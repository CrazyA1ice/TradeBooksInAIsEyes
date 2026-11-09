#!/usr/bin/env python3
"""Deterministic, synthetic-only multi-prefix old/new pen necessary-gate comparison."""
import json
from pathlib import Path
from chanlun_event_lab_v1 import replay

ROOT=Path(__file__).resolve().parents[1]
fixture=json.loads((ROOT/"experiments/fixtures/chanlun_prefix_synthetic_v1.json").read_text("utf8"))
assert fixture["kind"]=="synthetic_non_market_fixture"
rows=fixture["bars"]
cutoffs=["2007-09-20T01:32:01+00:00","2007-09-20T01:35:01+00:00",
         "2007-09-20T01:38:01+00:00","2007-09-20T02:00:00+00:00"]
pins={
    "old":{"version_id":"pen_077_exposition","attested_known_at":"2007-09-19T09:00:00+08:00",
           "proof_ref":"synthetic-publication-availability","proof_kind":"synthetic_fixture"},
    "revised":{"version_id":"pen_081_later_dated_post","attested_known_at":"2007-09-19T09:00:00+08:00",
               "proof_ref":"synthetic-publication-availability","proof_kind":"synthetic_fixture"}}
report=[]
for clock in cutoffs:
    runs={}
    for version,pin in pins.items():
        full=replay(rows,data_kind=fixture["kind"],market_asof=clock,direction="UP",rule_pin=pin)
        prefix_count=full["visible_closed_bars"]
        same=replay(rows[:prefix_count],data_kind=fixture["kind"],market_asof=clock,
                    direction="UP",rule_pin=pin)
        if full!=same:
            raise AssertionError("Future/unfinished suffix changed historical snapshot")
        if full["rule"]["state"]!="RESEARCH_RULE_PINNED":
            raise AssertionError("Synthetic rule pin unexpectedly unavailable")
        if full["orders_sent"] or full["complete_pen_parser"] or full["real_market_data_used"]:
            raise AssertionError("Experimental scope incorrectly elevated")
        runs[version]={"rule_id":full["rule"]["version_id"],
                       "visible_closed_bars":prefix_count,
                       "prefix_digest_sha256":full["visible_prefix_digest_sha256"],
                       "normalized_count":len(full["normalized_bars"]),
                       "fractal_candidates":[{"kind":f["kind"],"center":f["center_normalized_index"],
                                              "available_at":f["available_at"]} for f in full["fractal_candidates"]],
                       "pen_gate_statuses":[x["status"] for x in full["pen_necessary_gates"]],
                       "future_suffix_isolated":True}
    if runs["old"]["prefix_digest_sha256"]!=runs["revised"]["prefix_digest_sha256"]:
        raise AssertionError("Rule versions must not alter source market bars")
    report.append({"asof":clock,"old":runs["old"],"revised":runs["revised"],
                   "gate_disagreement":runs["old"]["pen_gate_statuses"]!=runs["revised"]["pen_gate_statuses"]})
result={"status":"PASS_SYNTHETIC_PREFIX_VERSION_COMPARISON",
        "dataset":"synthetic_non_market_fixture",
        "scope":"two necessary-condition versions, not complete Chanlun pens or backtesting",
        "prefixes":report,
        "no_market_orders":True,
        "real_market_backtest":"not_run"}
print(json.dumps(result,ensure_ascii=False,sort_keys=True))
