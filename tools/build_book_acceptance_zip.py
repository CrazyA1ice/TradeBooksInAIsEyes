#!/usr/bin/env python3
"""Temporarily assemble a self-contained book-review ZIP from canonical files.

No source files are copied into the git working tree or checked into the repo.
Only standard library; supports reusable manifest for the next book.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile


def reject(message):
    raise ValueError(message)


def gather(repo, spec):
    if spec.get("schema_version") != 1:
        reject("Unsupported package spec version")
    patterns = spec.get("patterns")
    if not isinstance(patterns, list) or not patterns:
        reject("Nonempty canonical source patterns required")
    banned = set(spec.get("skip_directory_names", []))
    suffix = tuple(spec.get("exclude_suffix", []))
    found = {}
    for pattern in patterns:
        if not isinstance(pattern, str) or not pattern or pattern.startswith("/"):
            reject("Invalid source pattern")
        if ".." in Path(pattern).parts or "\\" in pattern:
            reject("Disallowed path traversal in source pattern")
        matched = list(repo.glob(pattern))
        if not matched:
            reject("Source pattern did not match: " + pattern)
        members = []
        for match in matched:
            if match.is_symlink():
                reject("Symlinks not allowed: " + str(match))
            if match.is_file():
                members.append(match)
            elif match.is_dir():
                members.extend(x for x in match.rglob("*") if x.is_file())
        for file in members:
            if file.is_symlink():
                reject("Symlink inside source directory: " + str(file))
            rel = file.relative_to(repo)
            if any(p in banned for p in rel.parts):
                continue
            if file.name.endswith(suffix):
                continue
            found[rel.as_posix()] = file
    if not found:
        reject("No source files selected")
    must_contain = ("ChineseBooks/缠论/", "deliverables/chanlun_108_acceptance/")
    if spec.get("book_slug") == "chanlun":
        for required in must_contain:
            if not any(k.startswith(required) for k in found):
                reject("Required book source missing: " + required)
        pdfs = [x for x in found if x.startswith("ChineseBooks/缠论/") and x.endswith(".pdf")]
        if len(pdfs) != 5:
            reject("Five original PDF volumes must be present")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    specpath = args.spec.resolve()
    if repo not in specpath.parents:
        reject("Package spec must be part of repository")
    spec = json.loads(specpath.read_text(encoding="utf-8"))
    paths = gather(repo, spec)
    output = args.out.resolve()
    if repo == output.parent or repo in output.parents:
        reject("Never write temporary ZIP inside source repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        reject("Refusing to overwrite an existing ZIP")
    root_name = spec.get("archive_root", "BookResearch")
    if not isinstance(root_name, str) or not root_name or "/" in root_name or "\\" in root_name or root_name in (".", ".."):
        reject("Invalid archive_root")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=2, allowZip64=True) as archive:
        for relative, path in sorted(paths.items()):
            archive.write(path, arcname=root_name + "/" + relative)
    with zipfile.ZipFile(output, "r") as archive:
        invalid = archive.testzip()
        if invalid:
            reject("Archive CRC failed for " + invalid)
        if len(archive.namelist()) != len(paths):
            reject("Archive file count mismatch")
    sha = hashlib.sha256()
    with output.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    print(json.dumps({"status":"PASS_CANONICAL_ONLY_OFFLINE_REVIEW_ZIP",
                      "files":len(paths),"pdf_volumes":sum(name.endswith(".pdf") for name in paths),
                      "bytes":output.stat().st_size,"sha256":sha.hexdigest(),
                      "book_slug":spec.get("book_slug"),"contains_duplicate_git_source_tree":False},
                     sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    main()
