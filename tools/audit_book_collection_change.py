#!/usr/bin/env python3
"""Enforce per-step workflow learning for every registered book collection.

For any PR changing a registered original source or its mirrored book folder,
require that same PR to revise the common process, book-specific process,
book work log, research status and mirror manifest. GitHub Actions runs this
with full git history and the original PR base/head, not guessed filenames.
"""
import argparse
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def altered(base,head):
    r=subprocess.run(["git","diff","--name-only","-z",base,head],
                     cwd=ROOT,check=True,capture_output=True)
    return {p.decode("utf-8") for p in r.stdout.split(b"\0") if p}

def validate(changed,registry):
    required_by_book={}
    if registry.get("schema_version")!=1:
        raise ValueError("Unsupported collection registry")
    for book in registry["collections"]:
        root=book["folder"]
        src=book["source_roots"]
        relevant=any(p.startswith(root+"/") or
             any(p.startswith(pre+"/") for pre in src) or
             p=="BOOK_COLLECTIONS.json"
             for p in changed)
        if not relevant:
            continue
        required={"docs/BOOK_RESEARCH_WORKFLOW.md",
                  root+"/WORKFLOW.md",
                  root+"/WORK_LOG.md",
                  root+"/RESEARCH_STATUS.md",
                  root+"/COLLECTION_MANIFEST.json"}
        absent=required-changed
        if absent:
            raise ValueError("Every book research step must update workflow, log, status, manifest for "+
                             book["id"]+": "+", ".join(sorted(absent)))
        required_by_book[book["id"]]=sorted(required)
    return {"status":"PER_BOOK_EACH_STEP_WORKFLOW_CHANGE_GATE_PASS",
            "books_affected":sorted(required_by_book),
            "total_changed_paths":len(changed),
            "required_changes":required_by_book}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",required=True)
    ap.add_argument("--head",required=True)
    args=ap.parse_args()
    r=validate(altered(args.base,args.head),
               json.loads((ROOT/"BOOK_COLLECTIONS.json").read_text(encoding="utf-8")))
    print(json.dumps(r,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
