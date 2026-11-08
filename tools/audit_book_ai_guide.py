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


def audit(slug: str) -> dict:
    base = ROOT / "deliverables" / f"{slug}_acceptance" / "04_AI_GUIDE"
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

    for name in FILES:
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

    for name in FILES[1:]:
        if name in docs and "__source__" + name not in docs:
            fail(f"Deep-reading chapter lacks links back to canonical evidence: {name}")

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
        "minimum_files": len(FILES),
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
    args = p.parse_args()
    report = audit(args.book_slug)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
