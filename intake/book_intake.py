#!/usr/bin/env python3
"""G0 source inventory: offline, read-only by default, never republishes book bytes.

Only checks container signatures, UTF-8 decodability, hashes and local duplicates.
It does not extract text, run OCR, infer page numbers or authenticate provenance.
"""
from __future__ import annotations

import argparse
import codecs
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

SUPPORTED = {".pdf", ".epub", ".docx", ".md", ".txt"}
RIGHTS = {"UNKNOWN", "OWNED_OR_LICENSED", "PUBLIC_DOMAIN", "PERMISSION_REQUIRED"}
LANGUAGES = {"zh", "en", "other", "mixed", "unknown"}
MAX_FILE_COUNT = 10000


class IntakeError(ValueError):
    """An input cannot be safely accepted as a G0 candidate."""


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise IntakeError(msg)


def _verify_type(path: Path, suffix: str) -> str:
    with path.open("rb") as fp:
        prefix = fp.read(8)
    require(bool(prefix), f"Empty source file: {path.name}")
    if suffix == ".pdf":
        require(prefix.startswith(b"%PDF-"), f"PDF signature missing: {path.name}")
        return "PDF_HEADER_ONLY_NOT_FULLY_PARSED"
    if suffix in {".epub", ".docx"}:
        try:
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                require(len(names) == len(archive.namelist()), f"Duplicate ZIP members: {path.name}")
                if suffix == ".epub":
                    require("mimetype" in names, f"EPUB mimetype missing: {path.name}")
                    info = archive.getinfo("mimetype")
                    require(info.file_size <= 64, f"Oversized EPUB mimetype: {path.name}")
                    require(archive.read(info) == b"application/epub+zip",
                            f"Wrong EPUB mimetype: {path.name}")
                    require("META-INF/container.xml" in names,
                            f"EPUB container missing: {path.name}")
                    return "EPUB_CONTAINER_ONLY_NOT_FULLY_PARSED"
                require("[Content_Types].xml" in names and "word/document.xml" in names,
                        f"DOCX document parts missing: {path.name}")
                return "DOCX_CONTAINER_ONLY_NOT_FULLY_PARSED"
        except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
            raise IntakeError(f"Invalid ZIP container: {path.name}") from exc
    decoder = codecs.getincrementaldecoder("utf-8")("strict")
    try:
        with path.open("rb") as fp:
            for chunk in iter(lambda: fp.read(1024 * 1024), b""):
                decoder.decode(chunk)
            decoder.decode(b"", final=True)
    except UnicodeDecodeError as exc:
        raise IntakeError(f"Text must be UTF-8: {path.name}") from exc
    return "UTF8_TEXT_DECODED_NOT_SEMANTICALLY_REVIEWED"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(root: Path, *, book_id: str, title: str, language: str,
              rights_status: str, author: str = "", edition: str = "") -> dict:
    """Inventory one user's local folder; no persistence and no network calls."""
    require(re.fullmatch(r"[a-z][a-z0-9-]{0,39}", book_id) is not None,
            "book_id must be a lower-case ASCII slug")
    require(bool(title.strip()) and len(title) <= 300, "Nonempty title required")
    require(language in LANGUAGES, "Unsupported language marker")
    require(rights_status in RIGHTS, "Explicit rights status is required")
    require(root.is_dir() and not root.is_symlink(), "Input must be a real directory")
    root = root.resolve(strict=True)
    paths = sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix().casefold())
    require(len(paths) <= MAX_FILE_COUNT, "Too many input paths; split the intake")
    require(not any(p.is_symlink() for p in paths), "Symlinks forbidden in intake tree")
    used_names: set[str] = set()
    accepted = []
    ignored = []
    seen_digests: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        # Avoid ambiguous duplicates on case-insensitive Windows filesystems.
        fold = relative.casefold()
        require(fold not in used_names, f"Case-colliding relative paths: {relative}")
        used_names.add(fold)
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED:
            ignored.append(relative)
            continue
        kind = _verify_type(path, suffix)
        digest = _sha256(path)
        rec = {
            "relative_path": relative,
            "format": suffix[1:],
            "size_bytes": path.stat().st_size,
            "sha256": digest,
            "container_check": kind,
            "source_authentication": "USER_SUPPLIED_NOT_INDEPENDENTLY_AUTHENTICATED",
            "ocr_status": "NOT_RUN",
            "physical_page_count": None,
            "figure_verification": "NOT_RUN",
            "duplicate_of": seen_digests.get(digest),
        }
        seen_digests.setdefault(digest, relative)
        accepted.append(rec)
    require(bool(accepted), "No supported source files in input folder")
    warnings = []
    if rights_status != "OWNED_OR_LICENSED" and rights_status != "PUBLIC_DOMAIN":
        warnings.append("RIGHTS_REVIEW_REQUIRED_BEFORE_DISTRIBUTION")
    if ignored:
        warnings.append("UNSUPPORTED_INPUTS_NOT_PROCESSED")
    if any(e["duplicate_of"] for e in accepted):
        warnings.append("DUPLICATE_CONTENT_NEEDS_REVIEW")
    return {
        "schema_version": 1,
        "stage": "G0_SOURCE_INVENTORY_ONLY",
        "book_id": book_id,
        "title": title.strip(),
        "author_as_supplied": author.strip() or None,
        "edition_as_supplied": edition.strip() or None,
        "language": language,
        "rights_status_user_declared": rights_status,
        "status": "NEEDS_REVIEW" if warnings else "READY_FOR_MANUAL_G0_REVIEW",
        "source_count": len(accepted),
        "source_files": accepted,
        "ignored_files": ignored,
        "warnings": warnings,
        "next_step": "Review metadata/rights, identify edition and physical pages; register only after approval",
        "network_access": False,
        "source_files_modified_or_copied": False,
        "source_bytes_embedded": False,
        "market_data_accessed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--book-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--language", choices=sorted(LANGUAGES), default="unknown")
    parser.add_argument("--rights", choices=sorted(RIGHTS), default="UNKNOWN")
    parser.add_argument("--author", default="")
    parser.add_argument("--edition", default="")
    parser.add_argument("--output", type=Path, help="Optional metadata-only JSON receipt (no source bytes)")
    args = parser.parse_args(argv)
    try:
        result = inventory(args.input, book_id=args.book_id, title=args.title,
                           language=args.language, rights_status=args.rights,
                           author=args.author, edition=args.edition)
        serialized = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output:
            require(not args.output.is_symlink(), "Output cannot be a symlink")
            dest = args.output.resolve(strict=False)
            require(not dest.is_relative_to(args.input.resolve()),
                    "Do not write metadata inside original source directory")
            require(dest.parent.is_dir(), "Output parent directory must already exist")
            dest.write_text(serialized, encoding="utf-8")
        sys.stdout.write(serialized)
        return 0
    except (IntakeError, OSError) as exc:
        print(f"G0_INTAKE_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
