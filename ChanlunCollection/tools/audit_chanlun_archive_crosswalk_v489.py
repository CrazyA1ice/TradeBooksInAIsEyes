"""v4.89 fail-closed archival HTML crosswalk and optional offline screenshot-free reply check."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"catalog/chanlun_archived_html_crosswalk_v489.json"
RAW_ROLE="ARCHIVED_SINA_STYLE_HTML_HOST_MARKER_NOT_AUTHENTICATED_HISTORICAL_ORIGINAL"

EXPECTED={
 "FEB09_R29":("2007-02-09 16:20:18","2007-02-09 15:55:07","袖手旁观","486e105c010008la","B1a","RAW_FEB09"),
 "FEB12_R52":("2007-02-12 16:07:02","2007-02-12 15:43:32","温柔的股客","486e105c010008n0","B1a","RAW_FEB12"),
 "MAR08_R55":("2007-03-08 16:38:56","2007-03-08 15:34:28","缠文观止","486e105c0100090r","B2V","RAW_MAR08")
}
SNAPSHOTS={
 "RAW_FEB09":("fangj/chan","raw/sina_blog/chan_fenlei/jiaonichaogupiao/460.html","cd2dddca6643236ef4091c21e86c0a64ebcccaab","feb09.html","FEB09_R29"),
 "RAW_FEB12":("fangj/chan","raw/sina_blog/chan_fenlei/wenshizhexue/458.html","2ed6e0db25b974530761b4cd02d0a308c7683a57","feb12.html","FEB12_R52"),
 "RAW_MAR08":("fangj/chan","raw/sina_blog/chan_fenlei/wenshizhexue/442.html","a3d7467d72402a5885309a00b595ff3d5fea196d","mar08.html","MAR08_R55"),
 "GAV_FEB09":("gavfu/chzhshch-blog-site","stocks/029/index.html","840003fc58509dd8c97a659044201a1214c3b345",None,"FEB09_R29"),
 "GAV_FEB12":("gavfu/chzhshch-blog-site","confucius/52/index.html","b078975de7f63608e2877558a1bfbb4a7394aac2",None,"FEB12_R52"),
 "GAV_MAR08":("gavfu/chzhshch-blog-site","confucius/55/index.html","6a589fe7ad4f8187aa0a20ae3153110610bf03ee",None,"MAR08_R55"),
 "STOCK_029":("stockServ/chzhshch-108-plus","108/0456-486e105c010008la-029.md","63d24f7d2665a284595266700b5e40024b070213",None,"FEB09_R29"),
 "ANAL_052":("figozhu/chzhshch_The_Analects","The Analects/0458-486e105c010008n0-(60).md","03730b436233de31d203e78a13d274882e9627e5",None,"FEB12_R52"),
 "ANAL_055":("figozhu/chzhshch_The_Analects","The Analects/0474-486e105c0100090r-(93).md","b41216c361d8329b5d81759f620b8108e2a6939d",None,"MAR08_R55")
}
MARKERS={
 "FEB09_R29":["如果你把1分钟当最低的","3根K线重合部分","每笔成交当最低的"],
 "FEB12_R52":["三根相连K线的重叠部分","中枢其实是一个典型的递归","An+1=F（An）"],
 "MAR08_R55":["你不能把两种不搭界的看法混在一起","a+B+b","前三段就是中枢"]
}

def require(test,why):
    if not test: raise ValueError("ARCHIVE_CROSSWALK_V489: "+why)

def audit(catalog,root=ROOT):
    require(catalog.get("schema_version")==1 and catalog.get("version")=="4.89.0" and catalog.get("id")=="CHANLUN-THREE-DATED-REPLY-MULTIMIRROR-CROSSWALK-V489","catalog identity")
    entries={x["id"]:x for x in catalog["case_replies"]}
    snaps={x["id"]:x for x in catalog["mirrored_snapshots"]}
    require(set(entries)==set(EXPECTED) and len(catalog["case_replies"])==3,"reply ids")
    require(set(snaps)==set(SNAPSHOTS) and len(catalog["mirrored_snapshots"])==9,"snapshot ids")
    for key,(reply_at,q_at,questioner,blog_id,axis,raw_id) in EXPECTED.items():
        e=entries[key]
        require(tuple(e[k] for k in ("author_reply_at","question_at","questioner","sina_blog_id","type_axis","raw_snapshot_id"))==(reply_at,q_at,questioner,blog_id,axis,raw_id),"reply identity "+key)
        require(e["primary_article_url"]=="https://blog.sina.com.cn/s/blog_"+blog_id+".html","original article id "+key)
        require(e["machine_observed_author_marker"]=="divReplyIsHostTrue" and e["exact_original_2007_comment_bytes"] is False,"historical comments overpromoted "+key)
        require(e["author_answer_markers"]==MARKERS[key],"answer fingerprint changed "+key)
        expected_refs={x for x in SNAPSHOTS if SNAPSHOTS[x][4]==key and x!=raw_id}
        require(set(e["reference_snapshot_ids"])==expected_refs and len(e["reference_snapshot_ids"])==2,"cross-reference missing "+key)
        require(q_at<reply_at,"reply chronology "+key)
    for sid,(repo,path,sha,filename,cid) in SNAPSHOTS.items():
        s=snaps[sid]
        require(tuple(s[k] for k in ("repo","path","git_blob_sha","local_filename","case_id"))==(repo,path,sha,filename,cid),"file/blob changed "+sid)
        require(re.fullmatch(r"[0-9a-f]{40}",s["git_blob_sha"]) is not None,"invalid blob identifier")
        if sid.startswith("RAW_"):
            require(s["snapshot_role"]==RAW_ROLE and s["can_parse_raw_reply"] is True,"raw role inflated "+sid)
        else:
            require(s["snapshot_role"].startswith("LATER_THIRD_PARTY_") and s["can_parse_raw_reply"] is False,"copied source promoted "+sid)
    old=json.loads((root/catalog["predecessor"]["v488"]).read_text(encoding="utf-8"))
    require(old["version"]=="4.88.0" and len(old["archival_replies"])==2,"v4.88 baseline")
    require(next(x for x in old["archival_replies"] if x["id"]=="FEB12_R52")["original_sina_parent_article"] is None,"unacknowledged v4.88 missing parent URL")
    prior=json.loads((root/catalog["predecessor"]["v438"]).read_text(encoding="utf-8"))
    require(prior["version"]=="4.38.0" and any(x["at"]=="2007-03-08 16:38:56" for x in prior["author_replies_archive"]),"March prior registration")
    novelty=json.loads((root/catalog["predecessor"]["v487"]).read_text(encoding="utf-8"))
    require(novelty["first_discovered_in_v486"] is False,"v4.87 novelty barrier")
    require(catalog["predecessor"]["v488_missing_feb12_original_sina_url_now_landed"] is True and catalog["predecessor"]["v438_march_reply_previously_known"] is True and catalog["predecessor"]["v438_stockserv_35_38_already_known"] is True,"prior art flags")
    require(catalog["predecessor"]["v489_new_source_role"]=="PINNED_RAW_STYLE_HTML_AND_CROSS_ARCHIVE_COMPARISON","misstated discovery")
    flags=catalog["provenance_limit"]
    require(set(flags)=={"archived_divReplyIsHostTrue_not_2007_sina_server_authentication","archived_replies_substantive_author_identity_authentication","archives_proven_independent_collection_lineage","kaixiang_identified_exact_reply","laohu_full_pdf_docx_bytes_collected","two_different_independent_center_axioms_discovered","market_backtest_performed"},"provenance flags changed")
    require(flags["archived_divReplyIsHostTrue_not_2007_sina_server_authentication"] is True and all(v is False for k,v in flags.items() if k!="archived_divReplyIsHostTrue_not_2007_sina_server_authentication"),"unsubstantiated source authentication")
    require(catalog["state"]=={"B1a":"ARCHIVED_REPLY_CROSSCHECKED_NOT_KAIXIANG_IDENTIFIED","B2V":"ARCHIVED_REPLY_CROSSCHECKED_NOT_KAIXIANG_IDENTIFIED","B2R":"PRIOR_LESSON_ONLY","B3":"NO_SOURCE","A087":"OPEN","A016":"OPEN","F01":"OPEN","OB38":"OPEN","OB99":"OPEN","E1_E4":"NOT_RUN"},"gates inflated")
    require(catalog["report"]=="other_views/chanlun/speaker-unknown-001/IDEA_RAW_ARCHIVE_REPLY_CROSSWALK_V489.md","report path")
    report=(root/catalog["report"]).read_text(encoding="utf-8")
    require(all(k in report for k in ("FEB09","FEB12","MAR08","fangj/chan","原Sina","老虎","NOT_RUN","F01")), "report not audited")
    return {"status":"CROSSWALK_CATALOG_PASS","cases":3,"pinned_snapshots":9,"historical_sina_original_comments":False,"A087":"OPEN"}

def normalized_html(s):
    return re.sub(r"\s+","",html.unescape(re.sub(r"<[^>]*>"," ",s)).replace("\u00a0",""))

def extract_host_reply(raw_html,reply_time,questioner,question_time,markers):
    # Parse only third-party HTML blocks explicitly marked divReplyIsHostTrue.
    # Guest's quotations outside a host block must never count as author evidence.
    blocks=re.findall(r'<div\s+class=["\']divReplyIsHostTrue["\'][^>]*>(.*?)</fieldset>',raw_html,re.DOTALL|re.IGNORECASE)
    matched=[]
    for block in blocks:
        author=re.search(r'<span\s+class=["\']author["\']\s*>\s*([^<]+)</span>',block,re.I)
        when=re.search(r'<span\s+class=["\']pubtime["\']\s*>\s*([^<]+)</span>',block,re.I)
        if not author or not when: continue
        if html.unescape(author.group(1)).strip()!="缠中说禅": continue
        parsed_date=html.unescape(when.group(1)).strip().replace("/","-")
        # Old archive times can omit zero-padding in month/day.
        parts=parsed_date.split(" ",1)
        if len(parts)!=2: continue
        ymd=parts[0].split("-")
        if len(ymd)!=3: continue
        parsed_date=f"{ymd[0]}-{int(ymd[1]):02d}-{int(ymd[2]):02d} {parts[1]}"
        if parsed_date!=reply_time:continue
        text=normalized_html(block)
        if all(normalized_html(x) in text for x in [questioner,question_time]+markers):
            matched.append(block)
    require(len(matched)==1,"missing or ambiguous exact author marked reply "+reply_time)
    return {"author_reply_at":reply_time,"matched_host_blocks":len(matched)}

def check_local_snapshots(catalog,root):
    entries={x["id"]:x for x in catalog["case_replies"]}
    snapshots={x["id"]:x for x in catalog["mirrored_snapshots"]}
    out={}
    for rid in EXPECTED:
        e=entries[rid]
        snap=snapshots[e["raw_snapshot_id"]]
        file=(Path(root)/snap["local_filename"])
        require(file.is_file(),"missing local archive snapshot "+snap["local_filename"])
        raw=file.read_text(encoding="utf-8")
        out[rid]=extract_host_reply(raw,e["author_reply_at"],e["questioner"],e["question_at"],e["author_answer_markers"])
    return out

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--snapshot-dir",type=Path,default=None)
    args=parser.parse_args()
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    result=audit(data)
    if args.snapshot_dir is not None:
        result["snapshots"]=check_local_snapshots(data,args.snapshot_dir)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
