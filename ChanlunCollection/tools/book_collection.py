#!/usr/bin/env python3
"""Per-book collection mirror builder and fail-closed auditor.

Canonical files remain at original relative paths for existing CI and citations.
A collection mirrors their bytes under <BookCollection>/<same relative path>,
so relative links inside the mirrored Markdown continue to work. A single
stable manifest lists exact Git blob SHA and sizes. No PDF OCR/market trading.
Future books register their own collection in BOOK_COLLECTIONS.json.

Usage:
  python -B tools/book_collection.py --book chanlun --sync
  python -B tools/book_collection.py --book chanlun --check
  python -B tools/book_collection.py --book chanlun --report

--sync is an explicit local repository change and must be committed along with
docs/BOOK_RESEARCH_WORKFLOW.md and the book's WORK_LOG.md (required by CI).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"BOOK_COLLECTIONS.json"
MANAGED={"README.md","WORKFLOW.md","WORK_LOG.md","RESEARCH_STATUS.md",
         "QUESTION_GUIDE.md","COLLECTION_MANIFEST.json"}
VERSION=1

def fail(ok,message):
    if not ok:
        raise ValueError(message)

def jload(path):
    return json.loads(path.read_text(encoding="utf-8"))

def blob_sha(path):
    """Git blob-id is identical for copied bytes, without Git commands."""
    size=path.stat().st_size
    h=hashlib.sha1()
    h.update(("blob "+str(size)+"\0").encode("ascii"))
    with path.open("rb") as src:
        for b in iter(lambda:src.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def collection(id_):
    r=jload(REGISTRY)
    fail(r.get("schema_version")==1 and
         r.get("policy")=="CANONICAL_SOURCES_PLUS_VERIFIED_PER_BOOK_MIRROR",
         "Collection registry version/policy changed")
    matches=[c for c in r["collections"] if c["id"]==id_]
    fail(len(matches)==1,"Book not registered exactly once: "+id_)
    c=matches[0]
    folder=c["folder"]
    fail(folder.endswith("Collection") and folder and
         "/" not in folder and "\\" not in folder and folder not in {".",".."},
         "Unsafe or inconsistent per-book folder name")
    fail(c["mirror_policy"]=="EXACT_GIT_BLOB_WITH_ORIGINAL_RELATIVE_PATH" and
         c["canonical_unchanged"] is True,"Mirroring must not change originals")
    fail(c["collection_work_log"]==folder+"/WORK_LOG.md" and
         c["workflow_version"]!="","Missing per-book workflow log/version")
    validate_mirror_overrides(c)
    return c

def validate_mirror_overrides(c):
    """Require secure subtree aliases; source bytes stay in canonical roots."""
    aliases=c.get("mirror_path_overrides",{})
    fail(isinstance(aliases,dict),"Mirror overrides must be an object")
    for source_prefix,mirror_prefix in aliases.items():
        fail(source_prefix in c["source_roots"] and
             isinstance(mirror_prefix,str) and mirror_prefix and
             not mirror_prefix.startswith("/") and
             "\\\\" not in mirror_prefix and
             all(part not in {"",".",".."} for part in mirror_prefix.split("/")),
             "Unsafe or unregistered mirror override")
    return aliases

def mirror_destination(c,rel):
    """Preserve default relpaths; allow validated per-book reader subfolders."""
    aliases=validate_mirror_overrides(c)
    matches=[(src,dst) for src,dst in aliases.items() if rel.startswith(src+"/")]
    fail(len(matches)<=1,"Ambiguous mirror override for "+rel)
    if matches:
        src,dst=matches[0]
        return c["folder"]+"/"+dst+"/"+rel[len(src)+1:]
    return c["folder"]+"/"+rel

def canonical_paths(c):
    found={}
    folder=c["folder"]+"/"
    for root in c["source_roots"]:
        fail(root and not root.startswith("/") and ".." not in root.split("/") and
             not root.startswith(folder),
             "Invalid source root: "+root)
        rootpath=ROOT/root
        fail(rootpath.exists() and rootpath.is_dir(),
             "Registered original source root does not exist: "+root)
        for path in rootpath.rglob("*"):
            if not path.is_file():continue
            rel=path.relative_to(ROOT).as_posix()
            if (rel.startswith(folder) or path.name in c["source_exclusions"] or
                    "__pycache__" in path.parts or path.suffix==".pyc"):
                continue
            fail(rel not in found,"Overlapping book collection root: "+rel)
            found[rel]=path
    fail(found,"Book collection has no canonical results")
    return dict(sorted(found.items()))

def snapshot(c):
    files=canonical_paths(c)
    entries=[]
    for rel,path in files.items():
        entries.append({"source_path":rel,"mirror_path":mirror_destination(c,rel),
                        "git_blob_sha":blob_sha(path),"size_bytes":path.stat().st_size})
    destinations=[e["mirror_path"] for e in entries]
    fail(len(destinations)==len(set(destinations)),
         "Canonical sources map to duplicate mirror destinations")
    fail(not any(p.split("/")[-1] in MANAGED and p.count("/")==1
                 for p in destinations),
         "Canonical source would overwrite curated book entry")
    manuscript=[e for e in entries if e["source_path"].startswith(
        "analyses/books/chanlun/chapters/lesson_") and
        e["source_path"].endswith(".md")]
    evidence=[e for e in entries if e["source_path"].startswith(
        "knowledge/evidence/chanlun_lesson") and
        e["source_path"].endswith(".json")]
    source=[e for e in entries if e["source_path"].startswith(
        "ChineseBooks/缠论/") and e["source_path"].endswith(".pdf")]
    # Requirements are only enforced for books with positive expected counts.
    for key,count in (("expected_lesson_research_files",len(manuscript)),
                      ("expected_evidence_cards",len(evidence)),
                      ("expected_original_volumes",len(source))):
        expected=c.get(key,0)
        if expected:
            fail(count==expected,
                "Canonical source coverage changed: "+key+
                " actual="+str(count)+" expected="+str(expected))
    return {"schema_version":VERSION,"book_id":c["id"],
            "collection_folder":c["folder"],"workflow_version":c["workflow_version"],
            "source_count":len(entries),"original_pdf_count":len(source),
            "chapter_research_count":len(manuscript),"evidence_card_count":len(evidence),
            "mode":"exact_git_blob_mirror_no_canonical_moves",
            "proof_status":c["proof_status"],"real_market_experiments":c["real_market_experiments"],
            "entries":entries}

def manifest_text(data):
    return json.dumps(data,ensure_ascii=False,indent=2)+"\n"

def check(c):
    folder=ROOT/c["folder"]
    fail(folder.is_dir(),"Missing book folder: "+c["folder"])
    for name in MANAGED:
        fail((folder/name).is_file(),"Missing curated book entry: "+name)
    expected=snapshot(c)
    actual_text=(folder/"COLLECTION_MANIFEST.json").read_text(encoding="utf-8")
    fail(actual_text==manifest_text(expected),
         "Book manifest out of date: explicitly run --sync and commit workflow revision")
    allowed={e["mirror_path"] for e in expected["entries"]}
    for e in expected["entries"]:
        original=ROOT/e["source_path"]; mirror=ROOT/e["mirror_path"]
        fail(mirror.is_file(),"Canonical research result missing in book folder: "+e["source_path"])
        fail(original.stat().st_size==mirror.stat().st_size and
             blob_sha(mirror)==e["git_blob_sha"],
             "Stale or altered mirrored research result: "+e["source_path"])
    unexpected=[]
    for p in folder.rglob("*"):
        if p.is_file():
            rel=p.relative_to(ROOT).as_posix()
            if rel not in allowed and p.relative_to(folder).as_posix() not in MANAGED:
                unexpected.append(rel)
    fail(not unexpected,"Unregistered extra or orphan files in collection: "+
         ", ".join(unexpected[:6]))
    # No software conclusion may silently upgrade source/author/theorem status.
    fail(c["proof_status"].startswith("OPEN_") and
         c["real_market_experiments"]=="NOT_RUN",
         "Unverified author source/theorem/empirical result was promoted")
    return {"status":"EXACT_PER_BOOK_COLLECTION_SOURCE_MIRROR_PASSED",
            "book":c["id"],"collection":c["folder"],
            "mirrored_files":len(expected["entries"]),
            "chapters":expected["chapter_research_count"],
            "source_cards":expected["evidence_card_count"],
            "original_pdfs":expected["original_pdf_count"],
            "workflow_version":c["workflow_version"],
            "unproved_theorems_preserved":True,"real_market":"NOT_RUN"}

def sync(c):
    folder=ROOT/c["folder"]
    fail(folder.is_dir(),"Create reader-facing collection entry first")
    for name in MANAGED-{"COLLECTION_MANIFEST.json"}:
        fail((folder/name).is_file(),"Create manual collection entry first: "+name)
    data=snapshot(c)
    expected=set()
    for e in data["entries"]:
        target=ROOT/e["mirror_path"]
        target.parent.mkdir(parents=True,exist_ok=True)
        expected.add(target.resolve())
        original=ROOT/e["source_path"]
        if (not target.is_file() or target.stat().st_size!=original.stat().st_size or
                blob_sha(target)!=e["git_blob_sha"]):
            shutil.copyfile(original,target)
    for p in folder.rglob("*"):
        if (p.is_file() and p.resolve() not in expected and
                p.relative_to(folder).as_posix() not in MANAGED):
            raise ValueError("Unexpected extra book file; investigate, never delete automatically: "+str(p))
    (folder/"COLLECTION_MANIFEST.json").write_text(manifest_text(data),encoding="utf-8")
    return check(c)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--book",required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--sync",action="store_true")
    group.add_argument("--check",action="store_true")
    group.add_argument("--report",action="store_true")
    opts=p.parse_args()
    book=collection(opts.book)
    result=sync(book) if opts.sync else check(book) if opts.check else snapshot(book)
    if opts.report:result={k:v for k,v in result.items() if k!="entries"}
    print("BOOK_COLLECTION_RESULT="+json.dumps(result,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
