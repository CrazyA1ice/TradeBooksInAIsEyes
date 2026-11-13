#!/usr/bin/env python3
"""v4.93: A087 two-center-axioms hypothesis triage; no original author reply invented.

All operations read-only; only pinned third-party lesson/transcript and user export.
No remote downloads, private-material upload, or real market-data execution.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/chanlun_a087_two_center_claim_triage_v493.json"
UPSTREAM_REPO = "stockServ/chzhshch-108-plus"
UPSTREAM_COMMIT = "d2a87d5bd9c84baac2918edca668b9f82a20be52"
LESSONS = {
    20: ("108/0424-486e105c010007zw-020.md", "4083ee8458840d108cd9f7be323885feb34179c4",
         "FORMAL_CENTER_INTERSECTION_AND_TWO_FORMATION_DIRECTIONS"),
    35: ("108/0475-486e105c01000914-035.md", "54dae3ccf1f71e2cba73e4f5f81ac24b14d0bf4e",
         "TRADE_BY_TRADE_BASE_CASE_AND_RECURSIVE_CONSTRUCTION"),
    63: ("108/0569-486e105c01000bgd-063.md", "b75de72cb7aa187c09128b746726cf7b2f34bb13",
         "DISTINGUISH_MATHEMATICAL_EXISTENCE_AND_FINITE_CHART_PRACTICAL_WORKFLOW"),
    72: ("108/0648-486e105c01000cbj-072.md", "e6632b7eed66518126167ccabe089d676072c81c",
         "EXPLICIT_LAZY_MORPHOLOGY_ENTRY_ROUTE_VS_RECURSIVE_PROOFS")
}
EXPERT_EXPORT = "other_views/chanlun/speaker-unknown-001/answers-2026-11-11.md"
EXPERT_EXPORT_GIT_SHA = "3dda9aee3ecda29f48e86381315d21dd3d736aeb"
EXPECTED_SOURCE_MARKERS = {
    20: ["a1=b1", "b2=c2", "a2=b2", "b1=c1", "max（a2", "min（a1"],
    35: ["最严格去定义", "连续三笔相同价位", "严格的递归式定义"],
    63: ["存在性", "可操作性", "变通的方法", "不同级别显微镜"],
    72: ["从分型", "递归定义", "最小级别中枢", "逻辑上就容易乱"],
}
CANDIDATES = {
    "H01": ("TWO_ASCENDING_DESCENDING_CENTER_FORMATIONS", "ORIGINAL_LESSON20",
            "TWO_GEOMETRIC_FORMATION_DIRECTIONS_NOT_TWO_CENTER_AXIOMS"),
    "H02": ("TRANSACTION_LEVEL_RECURSION_VS_FINITE_KLINE_MORPHOLOGY_WORKFLOW",
            "ORIGINAL_LESSONS35_63_72",
            "TEXTUAL_THEORY_PRACTICE_DISTINCTION_PLAUSIBLE_BUT_NO_A087_CITATION"),
    "H03": ("THIRD_PARTY_FULL_MIDDLE_SEGMENT_IS_CENTER", "2019_THIRD_PARTY_ANALYSIS",
            "UNIVERSAL_FORMULA_FALSE_NOT_AUTHOR_REPLY"),
    "H04": ("AUTHOR_REPLIES_CONTAIN_DISTINCT_SECOND_CENTER_AXIOM",
            "A087_UNCITED_ASSERTION_ONLY", "NOT_LOCATED_NOT_CONFIRMED_NOR_DISPROVEN"),
}
FALSE_PROVENANCE = {
    "kaixiang_identity_platform_verified",
    "a087_quote_self_assigned_specific_historical_reply",
    "original_2007_sina_reply_bytes_verified",
    "laohu_edition_document_acquired",
    "laohu_vs_other_editions_comparison_run",
    "third_party_2019_interpretation_is_author_reply",
    "independent_B3_second_center_axiom_confirmed",
    "real_market_E1_E4_experiments_run",
}


def require(value, why):
    if not value:
        raise ValueError("A087_TRIAGE_V493: " + why)


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def price_interval(a, b):
    require(isinstance(a, (int, float)) and isinstance(b, (int, float)), "numeric endpoints")
    return [min(a, b), max(a, b)]


def overlap(*intervals):
    require(intervals and all(
        isinstance(x, (list, tuple)) and len(x) == 2 and x[0] <= x[1] for x in intervals
    ), "valid intervals required")
    lo = max(x[0] for x in intervals)
    hi = min(x[1] for x in intervals)
    return [lo, hi] if lo <= hi else None


def example_from_endpoints(points):
    require(isinstance(points, (list, tuple)) and len(points) == 4,
            "four chained pivots required")
    a, b, c, d = points
    up_down_up = a < b and b > c and c < d
    down_up_down = a > b and b < c and c > d
    require(up_down_up or down_up_down,
            "three price movements must alternate and be nonflat")
    return {
        "pattern": "UP_DOWN_UP" if up_down_up else "DOWN_UP_DOWN",
        "endpoints": list(points),
        "a": price_interval(a, b), "b": price_interval(b, c),
        "c": price_interval(c, d)
    }


def validate_math_case(case):
    derived = example_from_endpoints(case["endpoints"])
    require(all(case[key] == derived[key] for key in ("pattern", "endpoints", "a", "b", "c")),
            "case intervals not endpoint-consistent")
    intersection = overlap(derived["a"], derived["b"], derived["c"])
    require(intersection == case["triple_overlap"], "three segment center formula")
    require(overlap(derived["a"], derived["c"]) == intersection,
            "author lesson20 A,C simplification must hold in this formation")
    require(case["middle_interval"] == derived["b"], "comparison B interval differs")
    return intersection != derived["b"]


def check_original_a087_export(catalog, root=ROOT):
    info = catalog["expert_statement"]
    require(info["identity"] == "USER_SUPPLIED_ZHIHU_EXPORT_NOT_PLATFORM_VERIFIED"
            and info["export_path"] == EXPERT_EXPORT
            and info["export_git_blob"] == EXPERT_EXPORT_GIT_SHA,
            "expert export origin")
    raw = (root / EXPERT_EXPORT).read_bytes()
    require(git_blob_sha(raw) == EXPERT_EXPORT_GIT_SHA, "user export Git SHA changed")
    source = raw.decode("utf-8-sig")
    def answer_section(heading):
        require(source.count("## " + heading) == 1, "answer heading missing or duplicated: " + heading)
        begin = source.index("## " + heading)
        tail = source.find("\n---", begin)
        require(tail > begin, "answer boundary not found")
        return source[begin:tail]
    a087 = answer_section("谁能真正讲明白缠论的级别呢？")
    book = answer_section("想学缠论，应该看哪本书？")
    require(info["a087_url"] ==
            "https://www.zhihu.com/question/626662382/answer/3523681743"
            and info["a087_url"] in a087
            and info["a087_published_from_export"] == "2024-06-08 00:28",
            "A087 self statement URL/date")
    require(all(x in a087 for x in (
        "中枢的定义方法是有两种的",
        "第二种在原文中没细说",
        "回复中多次说了",
        "实战中远没得第二种好用",
        "老虎版"
    )), "A087 actual statement missing")
    require(info["other_exported_answer_title"] == "想学缠论，应该看哪本书？"
            and info["other_exported_answer_url"] ==
            "https://www.zhihu.com/question/386727740/answer/1943916084915860281"
            and info["other_exported_answer_url"] in book
            and info["other_answer_published_from_export"] == "2025-08-27 06:01"
            and "电子版只有老虎版最正宗" in book,
            "second expert answer incorrectly cited")
    return {"source":"USER_SUPPLIED_EXPORT_GIT_BLOB_CONFIRMED",
            "question_answer_refs":2, "exact_author_reply_citation_count":0}


def check_optional_sources(catalog, source_dir):
    base = Path(source_dir)
    checked = []
    for row in catalog["author_primary_text_mirrors"]:
        path = base / row["path"]
        require(path.is_file(), "source file absent " + row["path"])
        raw = path.read_bytes()
        require(git_blob_sha(raw) == row["git_blob_sha"],
                "source file blob changed " + row["path"])
        text = raw.decode("utf-8-sig")
        require(all(x in text for x in row["required_markers"]),
                "primary-text marker missing " + row["path"])
        checked.append(row["lesson"])
    return {"status":"FOUR_EXACT_GIT_BLOB_AND_MARKER_MATCHES",
            "lessons":checked,
            "original_2007_Sina_server_unauthenticated":True}


def audit(catalog, root=ROOT):
    require(catalog.get("schema_version") == 1 and catalog.get("version") == "4.93.0"
            and catalog.get("id") ==
            "A087-TWO-CENTER-DEFINITIONS-CLAIM-TREE-WITH-NUMERIC-COUNTEREXAMPLE-V493",
            "catalog version")
    info = catalog["expert_statement"]
    require(info["a087_assertions"] == [
        "pre_35_level_read_as_chart_clock_period", "post_35_recursion_of_center_level",
        "author_two_definitions_first_theoretical_second_practical",
        "second_only_vaguely_located_in_multiple_replies",
        "recommends_laohu_edition"
    ], "expert claim changed")
    require(info["other_answer_claim"] ==
            "laohu_reply_coverage_more_complete_than_other_editions_claim_only_not_measured",
            "unmeasured edition claim promoted to fact")
    texts = catalog["author_primary_text_mirrors"]
    require(len(texts) == len(LESSONS) == 4, "four pinned primary lessons required")
    for item, (lesson, expected) in zip(texts, LESSONS.items()):
        path, sha, source_role = expected
        require((item["lesson"], item["repo"], item["path"],
                 item["git_blob_sha"], item["source_commit"], item["source_role"]) ==
                (lesson, UPSTREAM_REPO, path, sha, UPSTREAM_COMMIT, source_role),
                "primary lesson identity or provenance")
        require(item["required_markers"] == EXPECTED_SOURCE_MARKERS[lesson],
                "primary lesson text markers altered")
    third = catalog["external_interpretation"]
    require((third["author"], third["title"], third["published_date"], third["url"]) ==
            ("段狼", "以缠论论证缠论真假“中枢”的逻辑推演及原文论证",
             "2019-10-31", "https://www.ttyfp.com/chzhshch/11104.html"),
            "external interpretation source")
    require(third["kind"] == "THIRD_PARTY_AUTHORED_ANALYSIS_NOT_ORIGINAL_CHAN_AUTHOR_REPLY"
            and third["claim_under_test"] ==
            "FOR_ANY_THREE_ALTERNATING_UP_DOWN_UP_MOVEMENTS_THE_COMMON_OVERLAP_IS_THE_ENTIRE_MIDDLE_MOVEMENT"
            and third["claim_status"] ==
            "REFUTED_AS_UNIVERSAL_GEOMETRIC_CLAIM_BY_VALID_COUNTEREXAMPLE"
            and third["identity_relation_to_kaixiang"] == "NOT_ESTABLISHED"
            and third["cannot_use_as_A087_reply_identification"] is True
            and third["source_content_git_blob"] is None, "outside author attribution/interpretation")
    formal = catalog["formal_formula"]
    require(formal["source_lesson"] == 20
            and formal["three_overlap"] ==
            ["max(a_low,b_low,c_low)", "min(a_high,b_high,c_high)"]
            and formal["two_edge_simplification"] ==
            ["max(a_low,c_low)", "min(a_high,c_high)"],
            "lesson20 formal expression")
    require(formal["assumption"] ==
            "A_high=B_high AND B_low=C_low for one formation orientation",
            "middle-boundary assumptions")
    counter = formal["counterexample"]
    require(counter["endpoints"] == [0, 10, 4, 8]
            and counter["author_formation_equalities_satisfied"] is True
            and counter["third_party_middle_equals_triple_overlap"] is False,
            "counterexample pinned")
    require(validate_math_case(counter), "counterexample is not a counterexample")
    control = formal["control_middle_equal_case"]
    require(control["endpoints"] == [0, 10, 4, 12]
            and not validate_math_case(control), "must include equal-middle special case")
    mirror = formal["mirror_counterexample"]
    require(mirror["endpoints"] == [10, 0, 6, 2]
            and validate_math_case(mirror), "must include reverse-direction counterexample")
    require(formal["inference_limit"] ==
            "COUNTEREXAMPLE_REFUTES_ALWAYS_EQUAL_MIDDLE_NOT_ALL_TWO_METHODS_HYPOTHESES",
            "overstated logical refutation")
    rows = catalog["candidate_triage"]
    require(len(rows) == len(CANDIDATES) and
            [x["id"] for x in rows] == list(CANDIDATES),
            "all four alternative hypotheses needed")
    for row in rows:
        require((row["claim"], row["support"], row["status"]) == CANDIDATES[row["id"]]
                and row["not_A087_verified"] is True,
                "candidate promoted or source changed: " + row["id"])
    prior = catalog["prior_evidence"]
    require(prior == {
        "v438":"catalog/chanlun_two_methods_archives_laohu_v438.json",
        "v490":"catalog/chanlun_108_author_uid_reply_baseline_v490.json",
        "v491":"catalog/chanlun_l70_comment_host_adjudication_v491.json",
        "v492":"catalog/chanlun_l70_editorial_time_roles_v492.json",
        "older_hypotheses_not_reidentified_as_new":True
    }, "prior-art chain")
    for key, expected_version in [("v438","4.38.0"),("v490","4.90.0"),
                                  ("v491","4.91.0"),("v492","4.92.0")]:
        data = json.loads((root/prior[key]).read_text(encoding="utf-8"))
        require(data["version"] == expected_version, "prior version " + key)
    flags = catalog["limits"]
    require(set(flags) == FALSE_PROVENANCE and all(v is False for v in flags.values()),
            "unproven identity/method/market claims")
    require(catalog["frontier"] == {
        "A087":"OPEN", "A016":"OPEN", "F01":"OPEN",
        "OB38":"OPEN", "OB99":"OPEN", "E1_E4":"NOT_RUN"
    }, "research frontier closed without evidence")
    require(catalog["report"] ==
            "other_views/chanlun/speaker-unknown-001/IDEA_A087_TWO_CENTER_DEFINITION_CANDIDATE_FALSIFICATION_V493.md",
            "report path")
    report = (root/catalog["report"]).read_text(encoding="utf-8")
    require(all(x in report for x in (
        "A087", "2019", "[4,8]", "[4,10]", "H01", "H02", "H03", "H04",
        "NOT_RUN", "老虎版"
    )), "report missing formula or unresolved status")
    check_original_a087_export(catalog, root=root)
    return {
        "status":"A087_ALTERNATIVE_INTERPRETATIONS_FENCED_NOT_IDENTIFIED",
        "pinned_author_lesson_sources":4, "external_competing_interpretations":1,
        "hypotheses":4, "middle_equals_overlap_universal":False,
        "A087":"OPEN", "Laohu_document":"NOT_OBTAINED", "real_market":"NOT_RUN"
    }


def main():
    parser = argparse.ArgumentParser(
        description="A087 ambiguity triage using archived metadata and a numerical counterexample")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-dir", type=Path)
    args = parser.parse_args()
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    output = {"catalog":audit(data)}
    if args.source_dir:
        output["source_verification"] = check_optional_sources(data, args.source_dir)
    print(json.dumps(output, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
