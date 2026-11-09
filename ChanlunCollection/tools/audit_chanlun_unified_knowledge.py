#!/usr/bin/env python3
"""Read-only unified index over the 108 Chanlun lesson records and additive research graphs.

Source-printed dates are *not* live market knowability timestamps.
All original JSON sources stay immutable, including older evidence schemas.
"""
from __future__ import annotations
import argparse
import copy
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_FILES = (
    "knowledge/claims/chanlun_early_core_dependencies.json",
    "knowledge/claims/chanlun_lessons066_070_crossvolume_dependencies.json",
    "knowledge/claims/chanlun_lessons071_075_semantic_dependencies.json",
    "knowledge/claims/chanlun_lessons076_080_semantic_dependencies.json",
    "knowledge/claims/chanlun_lessons081_085_semantic_dependencies.json",
    "knowledge/claims/chanlun_lessons086_090_crossvolume_dependencies.json",
    "knowledge/claims/chanlun_lessons091_095_semantic_dependencies.json",
    "knowledge/claims/chanlun_lessons096_100_semantic_dependencies.json",
    "knowledge/claims/chanlun_lessons101_105_semantic_dependencies.json",
    "knowledge/claims/chanlun_lessons106_108_semantic_dependencies.json",
)
RULES = "catalog/chanlun_rule_history_v1.json"
INDEX_FILE = "knowledge/claims/chanlun_unified_index_v1.json"
ROLES = {"author_original", "author_separately_dated", "appendix_provenance_unresolved", "editor_later_undated"}
EDGE_CERTAINTY = {"ai_analysis", "documented_conceptual_relation"}

class AuditError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise AuditError(message)

def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def load_sources(root=ROOT):
    lesson_index = _read(root / "catalog/chanlun_lesson_index.json")
    graphs = [_read(root / f) for f in GRAPH_FILES]
    registry = _read(root / RULES)
    evidence = [_read(root / f"knowledge/evidence/chanlun_lesson{n:03d}.json") for n in range(1,109)]
    return lesson_index, graphs, registry, evidence

def _lesson_ranges(index):
    vols = index["volumes"]
    require(len(vols) == 5, "Exactly five indexed source PDF volumes required")
    ranges = {}
    volumes = {}
    for v in vols:
        num = v["volume"]
        require(num not in volumes, "Duplicate source volume")
        require(re.fullmatch("[0-9a-f]{64}", v["sha256"]) is not None, "Source fingerprint invalid")
        require(v["pdf_page_count"] > 0, "Source PDF has no pages")
        volumes[num] = v
        rows = v["lessons"]
        require(all(1 <= x["start_pdf_page"] <= v["pdf_page_count"] for x in rows), "Out-of-range lesson start")
        require([x["start_pdf_page"] for x in rows] == sorted({x["start_pdf_page"] for x in rows}), "Invalid lesson start order")
        for pos, x in enumerate(rows):
            n = x["lesson"]
            require(n not in ranges, "Duplicate lesson ID")
            end = rows[pos+1]["start_pdf_page"] - 1 if pos+1 < len(rows) else v["pdf_page_count"]
            start = x["start_pdf_page"]
            require(end >= start, "Invalid course PDF boundary")
            ranges[n] = {"lesson":n, "title":x["title"], "volume":num, "start_pdf_page":start, "end_pdf_page":end,
                         "pdf_sha256":v["sha256"], "evidence_file":f"knowledge/evidence/chanlun_lesson{n:03d}.json"}
    require(set(ranges) == set(range(1,109)), "Coverage must be exactly lessons 1–108")
    return ranges, volumes

def eligible_dated_source_versions(registry, family, displayed_asof):
    """Research-only date filter; NOT sufficient for historical trading as-of validation."""
    cut = datetime.fromisoformat(displayed_asof)
    return [v["id"] for v in registry["entries"]
            if v["family"] == family and v["role"] in ("author_original", "author_separately_dated")
            and v["source_displayed_at"] is not None and datetime.fromisoformat(v["source_displayed_at"]) <= cut]

def build_index(lesson_index, graphs, registry, evidence):
    ranges, volumes = _lesson_ranges(lesson_index)
    require(len(graphs) == len(GRAPH_FILES), "Graph source set changed")
    require(len(evidence) == 108, "Evidence set does not cover 108 lessons")
    for n, ev in enumerate(evidence, 1):
        source = ev.get("source", {})
        declared = ev.get("lesson", source.get("lesson_number"))
        require(declared == n, f"Lesson evidence number mismatch: {n}")
        target = ranges[n]
        require(source.get("path") == volumes[target["volume"]]["path"], f"Evidence source path mismatches: {n}")
        require(source.get("sha256") == target["pdf_sha256"], f"Evidence PDF SHA mismatches: {n}")
        if source.get("volume") is not None:
            require(source["volume"] == target["volume"], f"Evidence volume mismatches: {n}")
        pages = source.get("pdf_pages", [])
        require(bool(pages) and all(type(p) is int and target["start_pdf_page"] <= p <= target["end_pdf_page"] for p in pages),
                f"Evidence PDF physical page out of course: {n}")
        require(isinstance(ev.get("claims"), list) and len(ev["claims"]) > 0, f"Missing claims: {n}")
    node_table = {}
    nodes = []
    edges = []
    for path, graph in zip(GRAPH_FILES, graphs):
        require(graph.get("schema_version") == 1, "Unsupported graph schema: " + path)
        for k, expected in graph.get("source_pdf_sha256_by_volume", {}).items():
            require(int(k) in volumes and expected == volumes[int(k)]["sha256"], "Pinned source SHA mismatch: " + path)
        for ref in graph.get("references", []):
            require(ref in GRAPH_FILES, f"Graph dependency path missing: {ref}")
        for node in graph["nodes"]:
            ident = node["id"]
            require(ident not in node_table, "Duplicate node: " + ident)
            source = node["source"]
            v = source["volume"]
            pages = source["pdf_pages"]
            require(v in volumes and pages and all(type(p) is int and 1 <= p <= volumes[v]["pdf_page_count"] for p in pages),
                    "Invalid node source page: " + ident)
            require(bool(node.get("status")) and bool(node.get("claim")), "Missing node epistemic status/claim: " + ident)
            node_table[ident] = node
            nodes.append({"id":ident, "graph_file":path, "volume":v, "pdf_pages":pages,
                          "claim":node["claim"], "status":node["status"]})
        for edge in graph["edges"]:
            require(edge["certainty"] in EDGE_CERTAINTY, "Unknown relation certainty")
            require(edge["from"] != edge["to"], "Self-edge not permitted")
            edges.append({"from":edge["from"], "to":edge["to"], "type":edge["type"],
                          "certainty":edge["certainty"], "graph_file":path})
    for edge in edges:
        require(edge["from"] in node_table and edge["to"] in node_table, "Dangling graph edge: " + str(edge))
    require(registry.get("schema_version") == 1, "Unknown rule registry version")
    versions = registry["entries"]
    by_version = {}
    for v in versions:
        ident = v["id"]
        require(ident not in by_version, "Duplicate rule version ID: " + ident)
        by_version[ident] = v
        require(v["role"] in ROLES, "Invalid source attribution role: " + ident)
        require(v["source_node_id"] in node_table, "Rule source concept unknown: " + ident)
        node = node_table[v["source_node_id"]]
        require(node["source"]["volume"] == v["source"]["volume"], "Version and node volume differ: " + ident)
        require(set(v["source"]["pdf_pages"]).issubset(set(node["source"]["pdf_pages"])), "Version source pages do not support node: " + ident)
        require(v["lesson"] in ranges and ranges[v["lesson"]]["volume"] == v["source"]["volume"], "Rule lesson source mismatch: " + ident)
        require(all(ranges[v["lesson"]]["start_pdf_page"] <= p <= ranges[v["lesson"]]["end_pdf_page"]
                    for p in v["source"]["pdf_pages"]), "Rule page outside lesson range: " + ident)
        require(v["implementation_status"] == "research_only_not_market_tested", "Rule incorrectly marked validated: " + ident)
        stamped = v["source_displayed_at"]
        if v["role"] in ("editor_later_undated", "appendix_provenance_unresolved"):
            require(stamped is None and v["timestamp_basis"] == "unknown", "Unknown-date editorial/appendix was backdated: " + ident)
        else:
            require(isinstance(stamped,str) and v["timestamp_basis"] == "displayed_source_date", "Author original date missing: " + ident)
            require(datetime.fromisoformat(stamped).year in range(2000,2030), "Bad source date: " + ident)
    for v in versions:
        for edge in v["links"]:
            require(edge["target"] in by_version and edge["target"] != v["id"], "Bad rule version link")
            require(by_version[edge["target"]]["family"] == v["family"], "Cross-family version conflict not allowed")
    require(len(nodes) == 84 and len(edges) == 145, "New graph requires explicit baseline audit before count changes")
    return {"schema_version":1, "scope":"108 lessons, research provenance only; no proof of trading profitability",
            "graph_files":list(GRAPH_FILES), "rule_registry_file":RULES,
            "source_sha256_by_volume":{str(n):v["sha256"] for n,v in volumes.items()},
            "counts":{"lessons":len(ranges),"graph_nodes":len(nodes),"graph_edges":len(edges),
                      "rule_attributions":len(versions),"evidence_files":len(evidence)},
            "lessons":[ranges[n] for n in range(1,109)],
            "nodes":nodes, "edges":edges,
            "rule_version_refs":[{"id":v["id"],"family":v["family"],"role":v["role"],
                                  "source_node_id":v["source_node_id"],"source_displayed_at":v["source_displayed_at"]}
                                 for v in versions]}
def validate_snapshot(index):
    expected = _read(ROOT / INDEX_FILE)
    require(index == expected, "Unified index snapshot is stale; rebuild/review before updating")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--verify",action="store_true",help="Compare to committed versioned index")
    p.add_argument("--lesson",type=int,help="Show one lesson's source and graph nodes")
    p.add_argument("--node",help="Show a node and its outgoing research edges")
    p.add_argument("--family",help="Show alternative provenance versions in a rule family")
    args=p.parse_args()
    sources=load_sources()
    result=build_index(*sources)
    if args.verify:
        validate_snapshot(result)
    if args.lesson is not None:
        require(1 <= args.lesson <= 108,"Lesson out of bounds")
        result={"lesson":result["lessons"][args.lesson-1],
                "graph_nodes":[n for n in result["nodes"] if n["id"].startswith(f"L{args.lesson}-")]}
    elif args.node:
        result={"node":next((x for x in result["nodes"] if x["id"] == args.node), None),
                "related_edges":[e for e in result["edges"] if e["from"] == args.node or e["to"] == args.node]}
        require(result["node"] is not None, "Unknown node")
    elif args.family:
        result={"family":args.family, "versions":[x for x in sources[2]["entries"] if x["family"] == args.family]}
        require(bool(result["versions"]), "Unknown family")
    else:
        result={"status":"PASS",**result["counts"],"verified_snapshot":args.verify,
                "time_policy":"source-displayed dates, never historical live-signal eligibility"}
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
