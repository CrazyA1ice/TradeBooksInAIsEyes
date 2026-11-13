"""Fail-closed v4.88 historical-reply identity and analytic-axis contract."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"catalog/chanlun_early_author_reply_triage_v488.json"

def audit(data,root=ROOT):
    def require(ok,why):
        if not ok: raise ValueError("REPLY_TRIAGE_V488: "+why)
    require(data.get("schema_version")==1 and data.get("version")=="4.88.0", "schema/version")
    require(data.get("id")=="CHANLUN-KAIXIANG-A087-EARLY-ARCHIVED-REPLY-TRIAGE-V488" and data.get("person_claim")=="A087", "identity")
    require(data.get("person_post_url")=="https://www.zhihu.com/question/626662382/answer/3523681743", "person source")
    replies={x["id"]:x for x in data["archival_replies"]}
    require(set(replies)=={"FEB09_R29","FEB12_R52"} and len(data["archival_replies"])==2, "reply keys")
    expected={
      "FEB09_R29":("2007-02-09 16:20:18","2007-02-09 15:55:07","袖手旁观","LESSON29_COMMENT_ARCHIVE","https://eczsc.com/replies?lesson=29","https://blog.sina.com.cn/s/blog_9e33391b0101n3v9.html","https://blog.sina.com.cn/s/blog_486e105c010008la.html","BASE_INPUT_CHOICE_1MIN_THREE_BARS_VS_INDIVIDUAL_TRADE"),
      "FEB12_R52":("2007-02-12 16:07:02","2007-02-12 15:43:32","温柔的股客","CONFUCIUS52_COMMENT_ARCHIVE_NOT_LESSON29","https://chzhshch.blog/stocks/confucius52/","https://blog.sina.com.cn/s/blog_d6c202040102xc41.html",None,"ROOT_A0_TO_RECURSION_AN_PLUS_ONE")
    }
    for key,values in expected.items():
        obj=replies[key]
        actual=tuple(obj[k] for k in ("reply_at","question_at","questioner","parent_context","archive_url","corroboration_url","original_sina_parent_article","reading"))
        require(actual==values,"reply context or timestamp: "+key)
        require(obj["source_role"]=="ARCHIVED_ATTRIBUTED_AUTHOR_REPLY_NOT_ORIGINAL_SINA_COMMENT_BYTES", "reply source role")
        require(obj["question_at"]<obj["reply_at"] and obj["candidates"]==["B1a"] and obj["no_independent_center_formula"] is True, "no hidden formula")
    priors={x["id"]:x for x in data["prior_evidence"]}
    require(set(priors)=={"MAR08_TWO_VIEWS","MAY24_TWO_R","JUL20_TWO_A0"}, "previous source ids")
    expected_prior={
      "MAR08_TWO_VIEWS":("catalog/chanlun_two_methods_archives_laohu_v438.json","B2V_ANALYTICAL_VIEW_NOT_EQUIVALENT_TO_R","2007-03-08 16:38:56"),
      "MAY24_TWO_R":("catalog/chanlun_second_method_disambiguation_v439.json","B2R_LEGAL_PARTITION_POLICY_NOT_EQUIVALENT_TO_VIEW","2007-05-24"),
      "JUL20_TWO_A0":("catalog/chanlun_20070720_dual_a0_original_post_v441.json","B1a_TWO_INITIALIZATION_PATHS_NOT_A_REPLY","2007-07-20 08:26:20")
    }
    for key,(path,axis,date) in expected_prior.items():
        item=priors[key]
        require((item["prior_catalog"],item["axis"],item["date"])==(path,axis,date), "prior identity: "+key)
        prior=json.loads((root/path).read_text(encoding="utf-8"))
        require(isinstance(prior,dict) and prior.get("schema_version")==1, "prior catalog exists")
    require(next(x for x in priors.values() if x["id"]=="JUL20_TWO_A0")["locator"]=="https://blog.sina.com.cn/s/blog_486e105c01000bs4.html", "July provenance")
    old=json.loads((root/expected_prior["MAR08_TWO_VIEWS"][0]).read_text(encoding="utf-8"))
    require(any(x.get("at")=="2007-03-08 16:38:56" for x in old["author_replies_archive"]), "March reply was previously registered")
    types={x["id"]:x for x in data["candidate_taxonomy"]}
    require(set(types)=={"B1a","B2V","B2R","B3"} and len(types)==4, "candidate taxonomy")
    for name,variable,evidence in (
        ("B1a","LOWEST_BASE_A0_F1",["FEB09_R29","FEB12_R52"]),
        ("B2V","ANALYTICAL_VIEW_a_PLUS_B_PLUS_b_VS_CENTER_OSCILLATION",["MAR08_TWO_VIEWS"]),
        ("B2R","LEGAL_DECOMPOSITION_POLICY_R",["MAY24_TWO_R"]),
        ("B3","POSSIBLE_UNDISCOVERED_INDEPENDENT_CENTER_AXIOM",[]),
    ):
        item=types[name]
        require(item["changes"]==variable and item["reply_evidence"]==evidence, "variable or provenance confused: "+name)
        require(item["identification"]==("NO_SOURCE" if name=="B3" else "CANDIDATE_ONLY"), "improper identification: "+name)
    flags=data["provenance_limit"]
    require(set(flags)=={"archive_author_marker_not_historical_source_authentication","exact_historical_sina_comment_bytes_verified","kaixiang_explicitly_identified_one_of_these_replies","laohu_complete_edition_bytes_reviewed","source_replies_prove_second_independent_center_axiom","source_replies_certify_finished_movement","market_experiment_run"}, "provenance flags")
    require(flags["archive_author_marker_not_historical_source_authentication"] is True and all(v is False for k,v in flags.items() if k!="archive_author_marker_not_historical_source_authentication"),"false proof promotion")
    require(set(data["gates"])=={"A087_REFERENT_OPEN","A016_THIRD_LAYER_OPEN","F01_OPEN","OB38_OPEN","OB99_OPEN","E1_E4_NOT_RUN"}, "open gates")
    require(data["prior_art_v487"]=="catalog/chanlun_source_novelty_v487.json", "prior art review")
    require(json.loads((root/data["prior_art_v487"]).read_text(encoding="utf-8"))["first_discovered_in_v486"] is False, "v4.87 preserved")
    require(data["report_path"]=="other_views/chanlun/speaker-unknown-001/IDEA_2007_FEB_EARLY_REPLY_TRIANGULATION_V488.md", "report identity")
    report=(root/data["report_path"]).read_text(encoding="utf-8")
    require(all(v in report for v in ("FEB09_R29","FEB12_R52","B1a","B2V","B2R","B3","OPEN","NOT_RUN")), "research report coverage")
    return {"status":"ARCHIVED_EARLY_REPLY_TRIAGE_PASS","replies":2,"prior_references":3,"candidate_axes":4,"A087":"OPEN","market":"NOT_RUN"}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(SPEC.read_text(encoding="utf-8"))),sort_keys=True,ensure_ascii=False))
