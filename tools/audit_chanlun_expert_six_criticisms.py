"""Trace six previously paraphrased expert criticisms to the authored Chanlun lessons.

Purpose: provenance, domain/type distinctions, non-implication and research
limits.  It does NOT prove the author's entire theory, recover the expert's
literal post, replay an original chart, or predict prices.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_expert_six_criticisms_source_matrix_v1.json"
REPORT = ROOT / "deliverables/chanlun_108_acceptance/00_REVIEW/EXPERT_SIX_CRITICISMS_WHOLE_THEORY_THIRD_LAYER_SYNTHESIS.md"


def require(condition: bool, why: str) -> None:
    if not condition:
        raise ValueError("SIX_CRITICISMS_AUDIT_REJECTED: " + why)


def audit(spec: dict, report: str, root: Path = ROOT) -> dict:
    require(spec.get("id") == "CHANLUN-EXPERT-SIX-CRITICISMS-AND-THIRD-LAYER-SYNTHESIS-V435", "study identity")
    require(spec.get("schema_version") == 1, "schema")
    p = spec["provenance"]
    require(p["six_topic_paraphrases_from_prior_discussion_not_word_for_word"] is True, "must disclose paraphrase")
    require(p["critic_literal_original_quote_retrieved"] is False and
            p["critic_name_authenticated"] is False and
            p["critic_original_post_url_authenticated"] is False, "original expert words absent")
    require(p["original_author_lesson_compilation_available"] is True
            and p["later_editorial_notes_treated_separately"] is True, "author vs editor provenance")
    require(p["market_data_or_backtest_performed"] is False, "no market runs")

    objections = spec["six_objections"]
    by_id = {x["id"]: x for x in objections}
    require(len(objections) == len(by_id) == 6
            and set(by_id) == {"EX01","EX02","EX03","EX04","EX05","EX06"},
            "six independently described issues")
    needed = {
        "EX01": {15,17},
        "EX02": {17,18,89},
        "EX03": {17,33,35,72,83,84},
        "EX04": {27,35,38,44,102},
        "EX05": {27,35,53,83,84},
        "EX06": {54,69}
    }
    count = 0
    for key, obj in by_id.items():
        require(obj["paraphrase"].strip() and obj["interpretation"].strip(),
                "must explain meaning rather than only label issue")
        require(obj["assessment"].strip() and obj["hard_limit"].strip(),
                "must distinguish grounded status and limit")
        anchors = obj["author_claims"]
        require(len(anchors) >= 2, "evidence for each issue")
        require(needed[key].issubset({e["lesson"] for e in anchors}), "key lesson evidence missing " + key)
        require(len({(e["lesson"],e["id"]) for e in anchors}) == len(anchors),
                "duplicate source in issue " + key)
        for anchor in anchors:
            filepath = root / f"knowledge/evidence/chanlun_lesson{anchor['lesson']:03d}.json"
            require(filepath.exists(), "missing evidence card " + str(anchor["lesson"]))
            evidence = json.loads(filepath.read_text(encoding="utf-8"))
            matches = [c for c in evidence["claims"] if c["id"] == anchor["id"]]
            require(len(matches) == 1 and matches[0]["kind"] == "SOURCE",
                    "nonoriginal or absent claim: " + anchor["id"])
            require(set(anchor["pdf_pages"]).issubset(set(matches[0]["pdf_pages"])),
                    "physical page mismatch: " + anchor["id"])
            count += 1

    require(by_id["EX01"]["assessment"] == "AUTHOR_TEXT_SUPPORTS_DEFINITION_SHIFT_NOT_SAME_DOMAIN_CONTRADICTION_PROVED",
            "L15 vs L17 source-language shift not a global contradiction theorem")
    require(by_id["EX02"]["hard_limit"] == "CENTER_EXISTS_DOES_NOT_IMPLY_COMPLETED_PAN",
            "one center does not close its parent movement")
    require(by_id["EX03"]["hard_limit"] == "CHANGED_F1_NOT_A_COUNTEREXAMPLE_TO_FIXED_POLICY_UNIQUENESS",
            "do not confuse different f1 and one frozen policy")
    require(by_id["EX04"]["hard_limit"] == "L44_SMALL_TURN_NECESSARY_NOT_SUFFICIENT_FOR_LARGE_TURN",
            "author L44 explicitly necessary NOT sufficient")
    require(by_id["EX05"]["assessment"] ==
            "L83_AUTHOR_ACKNOWLEDGES_UNSTABLE_PEN_BASE_DESPITE_STRUCTURAL_ACROSS_LEVEL_ASSERTION",
            "L83 admission of instability is material")
    require(by_id["EX06"]["assessment"] ==
            "SOME_ORIGINAL_CHART_IMAGE_REFERENCES_EXIST_BUT_FULL_AUTHENTICATED_REALTIME_REPLAY_UNPROVEN",
            "cannot infer no charts or fully replayable market source")

    order = spec["author_date_order"]
    require(len(order) >= 15 and len({r["lesson"] for r in order}) == len(order), "dated author lesson order")
    dates = [date.fromisoformat(r["date"]) for r in order]
    require(dates == sorted(dates), "do not reorder author historical claims")
    require(order[0]["lesson"] == 15 and order[-1]["lesson"] == 102, "from early high-low to late strong uniqueness")
    require({i["lesson"] for i in order}.issuperset({15,17,18,27,33,35,38,44,54,69,72,83,84,89,99,102}),
            "chronology must include counter-source and mixed rule positions")

    image = spec["image_evidence"]
    require(image["lesson54_html"] == "https://eczsc.com/originals/54"
            and image["lesson69_html"] == "https://eczsc.com/originals/69", "must distinguish two preserved figures")
    require(image["lesson54_html_image_reference_observed"] is True
            and image["lesson69_html_image_reference_observed"] is True, "some pictures do exist")
    require(image["original_sina_image_bytes_independently_authenticated"] is False
            and image["complete_underlying_historical_market_replay_available"] is False,
            "no invented original bytes or replay")

    layers = {l["id"]: l for l in spec["strength_layers"]}
    require(set(layers) == {"L1","L2","L3","L4"}, "type grammar, eventual completion, unique recursion, online trade")
    require(layers["L3"]["name"] == "RECURSIVE_FIXED_POLICY_UNIQUENESS_COMPLETE_CLASSIFICATION",
            "exact strength of author late claim")
    require(layers["L4"]["name"] == "ONLINE_IDENTIFIABILITY_AND_REAL_WORLD_EXECUTION",
            "real-time action separate from completed parse")
    require(all(x["interpretive_not_formal_named_third_layer"] is True for x in layers.values()),
            "all our layer names are research framing")
    require(spec["author_called_our_L3_third_layer_in_original_lesson17"] is False,
            "invented original 'third layer' denomination")

    sep = set(spec["important_separations"])
    expected = {
        "VISUAL_DIRECTION_NOT_STRUCTURAL_TREND_CENTER_COUNT",
        "CENTER_EXISTS_NOT_MOVEMENT_FINISHED",
        "FINISHED_HISTORICAL_DECOMPOSITION_NOT_SAME_AS_ONLINE_PREFIX_LABEL",
        "FIXED_POLICY_UNIQUENESS_NOT_CROSS_POLICY_INVARIANCE",
        "STRICT_TRADE_LEVEL_NOT_CLOCK_BAR_TIMEFRAME",
        "LOWER_LEVEL_DIVERGENCE_NECESSARY_NOT_SUFFICIENT_FOR_HIGHER_TURN",
        "FORMAL_LEVEL_INVARIANCE_NOT_EQUAL_NOISE_STABILITY_OR_TRADABLE_PROFIT",
        "AN_ARCHIVED_CHART_NOT_AUTHENTICATED_RAW_SUBMINUTE_REPLAY",
        "EXPERT_PARAPHRASE_NOT_ORIGINAL_EXPERT_QUOTE"
    }
    require(expected.issubset(sep), "nine major semantic non-implications")
    lemma = spec["finite_prefix_lemma"]
    require(lemma["scope"] == "CONDITIONAL_PREFIX_INDISTINGUISHABILITY_NOT_GLOBAL_REFUTATION_OF_AUTHOR",
            "avoid false global no-algorithm theorem")
    require("same fixed policy" in lemma["premise"] and
            "identical P" in lemma["reasoning"] and
            "No future confirmation" in lemma["do_not_conclude"],
            "finite prefix proof assumptions/limits")
    status = spec["status"]
    require(status["six_argument_intent_explained"] == "CONCEPTUALLY_SYNTHESIZED_WITH_COURSE_SOURCE_ANCHORS", "status")
    require(status["expert_exact_quote"] == "UNAVAILABLE", "no literal claim")
    require(status["author_reconstructed_same_domain_uniqueness_theorem"] == "NOT_PROVEN", "strong theorem remains open")
    require(status["asof_complete_lower_movement"] == "OPEN_F01", "do not close F01")
    require(status["fixed_policy_global_unique_parse"] == "OPEN_OB38", "do not close OB38")
    require(status["yin_transition_compatible_proof"] == "OPEN_OB99", "do not close OB99")
    require(status["original_author_image_bytes_authenticated"] == "NO", "no original media byte claim")
    require(status["real_market_trades"] == "NOT_RUN"
            and status["market_backtest"] == "NOT_RUN", "no backtests")

    must_contain = ["①","②","③","④","⑤","⑥","第15课","第17课","第35课","第44课",
                    "第54课","第83课","第84课","第99课","第102课","六条","区间套",
                    "原话","级别","当下","OPEN","NOT_RUN","L1","L2","L3","L4"]
    require(all(q in report for q in must_contain), "reader-facing six-issue explanation incomplete")
    return {"status":"PASS_SOURCE_BOUND_CONCEPTUAL_SYNTHESIS_ONLY",
            "issues":6,"source_claim_anchors":count,
            "historical_lessons_in_order":len(order),
            "interpretive_strength_layers":4,"expert_original_quote":"NOT_FOUND",
            "finished_movement_proof":"OPEN","market_backtest":"NOT_RUN"}


def main() -> None:
    spec = json.loads(CATALOG.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    print(json.dumps(audit(spec, report), ensure_ascii=False))


if __name__ == "__main__":
    main()
