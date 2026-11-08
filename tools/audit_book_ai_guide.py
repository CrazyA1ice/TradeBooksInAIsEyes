#!/usr/bin/env python3
"""Reusable, read-only structural acceptance for mandatory AI book deep-reading guides.

Checks reproducible structure, navigable links, source provenance, diagrams and
uncertainty markers. Cannot judge interpretation correctness or re-verify PDF images.
Never runs trades, backtests or OCR and never writes into the repository.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "README.md",
    "01_核心定理与规则白话解读.md",
    "02_全书行文脉络与思想地图.md",
    "03_关键概念图示讲解.md",
    "04_AI视角下的争议与启发.md",
]
LINK = re.compile(r"\]\(([^)\n]+)\)")
SOURCE_ROOTS = {
    "ChineseBooks", "EnglishBooks", "Reports", "analyses", "knowledge",
    "catalog", "reports",
}


def audit(slug: str, acceptance_dir: str | None = None, tutorials: tuple[str, ...] = (), source_cases: tuple[str, ...] = (), min_source_cases: int = 1) -> dict:
    target = Path(acceptance_dir) if acceptance_dir else Path("deliverables") / f"{slug}_acceptance"
    if target.is_absolute() or ".." in target.parts:
        return {"status": "FAIL", "errors": ["Unsafe acceptance directory"]}
    folder = (ROOT / target).resolve()
    if not folder.is_relative_to((ROOT / "deliverables").resolve()):
        return {"status": "FAIL", "errors": ["Acceptance folder must be under deliverables"]}
    base = folder / "04_AI_GUIDE"
    errors: list[str] = []
    docs: dict[str, str] = {}
    local_links = 0
    provenance_links = 0

    def fail(msg: str) -> None:
        errors.append(msg)

    if not re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
        return {"status": "FAIL", "errors": ["Unsafe book slug"]}
    if not base.is_dir() or base.is_symlink():
        return {"status": "FAIL", "errors": ["Required deep reading directory is absent"]}
    if list(base.rglob("*.pdf")) or list(base.rglob("*.PDF")):
        fail("Do not duplicate source PDFs inside the deep reading guide")

    if len(tutorials) != len(set(tutorials)):
        fail("Duplicate requested tutorial names")
    for name in tutorials:
        if Path(name).name != name or not name.endswith(".md") or not re.fullmatch(r"[0-9]{2}_[^/\\\\]+[.]md", name):
            fail(f"Invalid tutorial filename: {name}")
    if len(source_cases) != len(set(source_cases)):
        fail("Duplicate requested source-case file")
    for name in source_cases:
        if Path(name).name != name or not name.endswith(".md") or not re.fullmatch(r"[0-9]{2}_[^/\\\\]+[.]md", name):
            fail(f"Invalid source-case filename: {name}")
    if min_source_cases < 1:
        fail("Minimum source-case count must be >= 1")
    required_docs = FILES + [name for name in tutorials if Path(name).name == name] + [name for name in source_cases if Path(name).name == name]

    for name in required_docs:
        file = base / name
        if not file.is_file() or file.is_symlink():
            fail(f"Required AI deep guide file missing: {name}")
            continue
        content = file.read_text(encoding="utf-8")
        docs[name] = content
        if len(content.strip()) < (350 if name == "README.md" else 850):
            fail(f"Missing substantive educational explanation in {name}")
        for m in LINK.finditer(content):
            link = m.group(1).split("#", 1)[0].strip()
            if not link or link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            dest = (file.parent / unquote(link)).resolve()
            if not dest.is_relative_to(ROOT.resolve()):
                fail(f"Guide link escapes repository: {name}: {link}")
                continue
            if not dest.exists():
                fail(f"Guide link is broken: {name}: {link}")
                continue
            local_links += 1
            rel = dest.relative_to(ROOT.resolve())
            if rel.parts and rel.parts[0] in SOURCE_ROOTS:
                provenance_links += 1
                if name != "README.md":
                    docs.setdefault("__source__" + name, "yes")

    for name in required_docs[1:]:
        if name in docs and "__source__" + name not in docs:
            fail(f"Deep-reading chapter lacks links back to canonical evidence: {name}")

    for name in tutorials:
        tutorial = docs.get(name, "")
        if not tutorial:
            continue
        if len(tutorial.strip()) < 1800:
            fail(f"Worked tutorial lacks substantive steps: {name}")
        if tutorial.count("```mermaid") + tutorial.count("```text") < 1:
            fail(f"Worked tutorial needs a readable conditional or timeline diagram: {name}")
        if not all(term in tutorial for term in ("AI", "条件", "原", "未")) or not any(term in tutorial for term in ("自测", "自检", "理解检查")):
            fail(f"Worked tutorial misses source/condition/unknown/self-test boundaries: {name}")

    source_case_counts = {}
    for name in source_cases:
        case_text = docs.get(name, "")
        if not case_text:
            continue
        case_ids = re.findall(r"^## SRC-([0-9]{3})\\b", case_text, re.M)
        source_case_counts[name] = len(case_ids)
        if len(case_ids) < min_source_cases or len(case_ids) != len(set(case_ids)):
            fail(f"Source-case atlas has too few or duplicate SRC case IDs: {name}")
        if case_text.count("```mermaid") + case_text.count("```text") < 1:
            fail(f"Source-case atlas needs original AI teaching diagrams: {name}")
        if not all(term in case_text for term in ("SOURCE", "AI", "PDF", "VISUAL_LIMITED", "原图", "未", "NOT_RUN")):
            fail(f"Source-case atlas lacks explicit original-text/image/AI boundaries: {name}")

    explain = docs.get(FILES[1], "")
    argument = docs.get(FILES[2], "")
    visual = docs.get(FILES[3], "")
    critique = docs.get(FILES[4], "")
    mermaid_count = visual.count("```mermaid")
    ascii_count = visual.count("```text")
    diagram_titles = len(re.findall(r"^##\s+图\d+", visual, re.M))

    if not all(s in explain for s in ("AI", "条件", "原", "未")):
        fail("Core interpretation must separate original claims, conditions and AI caveats")
    if not all(s in argument for s in ("为什么", "作者", "AI")):
        fail("Argument map must explain why ideas evolve, not just copy chapter headings")
    if mermaid_count + ascii_count < 1 or diagram_titles < 1:
        fail("Visual explanation must contain at least one labelled meaningful diagram")
    if not all(s in critique for s in ("AI", "原书", "启发", "证")):
        fail("Critical interpretation must distinguish AI opinions from source evidence")
    workflow = ROOT / "docs" / "BOOK_RESEARCH_WORKFLOW.md"
    if not workflow.is_file() or "G3-D" not in workflow.read_text(encoding="utf-8"):
        fail("Reusable book workflow does not declare mandatory G3-D deep reading")
    return {
        "status": "PASS" if not errors else "FAIL",
        "book_slug": slug,
        "required_files_present": len(docs) - sum(k.startswith("__source__") for k in docs),
        "minimum_files": len(required_docs),
        "required_worked_tutorials": len(tutorials),
        "required_source_case_atlases": len(source_cases),
        "source_case_counts": source_case_counts,
        "diagram_sections": diagram_titles,
        "mermaid_diagrams": mermaid_count,
        "ascii_diagrams": ascii_count,
        "local_links_checked": local_links,
        "canonical_source_links_checked": provenance_links,
        "empirical_backtests_run": 0,
        "figure_pixels_independently_verified": False,
        "human_quality_review_replaced": False,
        "errors": errors,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--book-slug", required=True)
    p.add_argument("--acceptance-dir", help="Optional legacy deliverable folder, relative to repository root")
    p.add_argument("--require-tutorial", action="append", default=[], help="Required in-guide worked tutorial markdown basename; repeat per topic")
    p.add_argument("--require-source-case", action="append", default=[], help="Source-anchored case atlas Markdown basename; repeat if needed")
    p.add_argument("--min-source-cases", type=int, default=1, help="Minimum SRC-numbered examples per required atlas")
    args = p.parse_args()
    report = audit(args.book_slug, args.acceptance_dir, tuple(args.require_tutorial), tuple(args.require_source_case), args.min_source_cases)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
