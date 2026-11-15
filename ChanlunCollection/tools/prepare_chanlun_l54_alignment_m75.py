#!/usr/bin/env python3
"""M75: project-contained local comparison of L54 source PDF vs verified M74 SVG.

No remote requests, no provider credentials, no market-data row writes.
All generated files stay in ignored <canonical-project>/work/chanlun/lesson054/.
A linked worktree may run the script from work/review-worktrees/M74-Review,
but its outputs always land in the canonical project's own work/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools import replay_chanlun_l54_real_minute_m74 as m74

PDF_REL = Path("ChineseBooks/缠论/缠论_卷3.pdf")
PDF_SHA = "fad3474e103353f6f67799aefec8c9fba28c9615c0c77a5c67fcbf2b6b4f8a7a"
SVG_REL = Path("work/chanlun/lesson054/figures/L54-M74-20070518-afternoon.svg")
ALIGN_REL = Path("work/chanlun/lesson054/alignment")
HTML_NAME = "L54-M75-original-vs-replay.html"
JSON_NAME = "L54-M75-marker-review-template.json"
SOURCE_PAGES = [170,171,172,173,174,175]


def need(ok, reason):
    if not ok:
        raise ValueError("M75_REJECTED: " + reason)


def project_root():
    return m74.canonical_project_root()


def private_root():
    return project_root() / "work"


def project_pdf_candidates(root):
    """Use an existing in-project PDF; do not copy or download the book.

    The main worktree may be sparse or locally incomplete while one of the
    project's registered worktrees or its verified book mirror has the PDF.
    Keep exact-source SHA verification independent of this path selection.
    """
    root = root.resolve()
    return (
        (root / PDF_REL).resolve(),
        (root / "ChanlunCollection" / PDF_REL).resolve(),
        (root / "work" / "review-worktrees" / "M74-Review" / PDF_REL).resolve(),
        (root / "work" / "review-worktrees" / "M73-Review" / PDF_REL).resolve(),
    )


def files(root=None):
    root = (root or project_root()).resolve()
    candidates = project_pdf_candidates(root)
    available = next((path for path in candidates
                      if root in path.parents and path.is_file()), None)
    return {
        "project": root,
        "pdf": available if available is not None else candidates[0],
        "svg": (root / SVG_REL).resolve(),
        "directory": (root / ALIGN_REL).resolve(),
    }


def sha256_file(path):
    hash_ = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda:file.read(1024*1024),b""):
            hash_.update(chunk)
    return hash_.hexdigest()


def verify_inputs(location, expected_pdf_sha=None):
    expected_pdf_sha = PDF_SHA if expected_pdf_sha is None else expected_pdf_sha
    root = location["project"].resolve()
    work = (root/"work").resolve()
    need(work in location["svg"].parents, "replay figure must remain in project work")
    need(work in location["directory"].parents, "alignment output must remain in project work")
    need(root in location["pdf"].resolve().parents, "source PDF must remain in project")
    need(location["pdf"].is_file(), "volume-3 PDF missing from all project-local candidates")
    need(location["svg"].is_file(), "M74 SVG missing; first migrate the existing figure")
    pdf_sha = sha256_file(location["pdf"])
    need(pdf_sha == expected_pdf_sha, "canonical PDF SHA256 differs from source evidence")
    need(location["svg"].stat().st_size <= 6*1024*1024, "SVG unexpectedly large")
    svg = location["svg"].read_text(encoding="utf-8")
    for needle in ("<svg ", "600151.SH / 2007-05-18", "13:07 / 18.59",
                   "15:00 / 18.03", "OpenFinMind pinned SHA256"):
        need(needle in svg, "required verified M74 SVG anchor missing")
    return {"pdf_sha256":pdf_sha,
            "pdf_project_relative":location["pdf"].relative_to(root).as_posix(),
            "svg_sha256":sha256_file(location["svg"]),
            "figure_rows_proved_by_m74_log":240}


def image_template(evidence):
    marks={}
    for prefix in ("g","d"):
        for i in range(1,8):
            marks[f"{prefix}{i}"]={
                "source_pixel_x":None,"source_pixel_y":None,
                "candidate_market_minute":None,"candidate_price":None,
                "candidate_basis":"NOT_REVIEWED",
                "market_bar_close_observable_at":None,
                "author_text_stage":f"{prefix}{i}",
                "subminute_segment_completed_at":None,
                "market_first_actionable_at":None,
                "independent_author_point_certified":False,
            }
    return {
        "schema_version":1,"lesson":54,
        "candidate_date":"2007-05-18","symbol":"600151.SH",
        "evidence_grade":"HISTORICAL_1M_FINGERPRINT_MATCHED_G_D_NOT_YET_MAPPED",
        "source_pdf_repo_relative":evidence.get("pdf_project_relative", PDF_REL.as_posix()),
        "source_pdf_sha256":evidence["pdf_sha256"],
        "replay_svg_repo_relative":SVG_REL.as_posix(),
        "replay_svg_sha256":evidence["svg_sha256"],
        "source_page_physical_candidates":SOURCE_PAGES,
        "source_compilation_reference":"https://xqdoc.imedao.com/15621999f6b25803feb29d4c.pdf#page=129",
        "observed_anchors":[{"time":"13:07","observed_high":"18.59",
                             "author_marker_identity":"NOT_ASSIGNED"},
                            {"time":"15:00","observed_low":"18.03",
                             "observed_close":"18.03",
                             "author_marker_identity":"AFTER_G7_FROM_TEXT_NOT_TICK_CERTIFIED"}],
        "author_alpha":{"center_at":"g5","g7_type":"THIRD_SELL_AUTHOR_TEXT_ONLY"},
        "author_beta":{"center_at":"g6","g7_type":"CENTER_OSCILLATION_AUTHOR_TEXT_ONLY"},
        "marks":marks,"F01":"OPEN","OB38":"OPEN","OB99":"OPEN","Phi20":"OPEN",
        "E1_E4":"NOT_RUN","chart_year_independently_authenticated":False,
        "price_adjustment_verified":False,
    }


def html_viewer(location, evidence):
    pdf_uri=location["pdf"].as_uri()
    svg_uri=location["svg"].as_uri()
    anchors="".join(
        '<a href="'+pdf_uri+'#page='+str(i)+'" target="source-pdf">第'+str(i)+'物理页</a>'
        for i in SOURCE_PAGES
    )
    marks="".join(
        '<tr><td>'+f"{p}{i}"+'</td><td>未登记</td><td>未登记</td><td>UNKNOWN</td></tr>'
        for p in ("g","d") for i in range(1,8)
    )
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>M75｜第54课：原图与真实1分钟复盘图对照</title>
<style>
body{font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif;color:#23303b;background:#f6f8fa;margin:0;padding:22px}
h1{font-size:22px;margin:0 0 8px} h2{font-size:17px;margin:20px 0 8px}
p{max-width:1300px} a{margin-right:14px;color:#1766a0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start}
.panel{background:white;border:1px solid #dce2e7;border-radius:10px;padding:12px;min-width:0}
iframe{width:100%;height:810px;border:1px solid #dce2e7}
img{width:100%;height:auto;border:1px solid #dce2e7}
table{border-collapse:collapse;width:100%;background:white}td,th{padding:7px 10px;border-bottom:1px solid #dce2e7;text-align:left}
small{color:#5c6c7b} code{word-break:break-all}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
</style></head><body>
<h1>第54课｜2007-05-18 实际1m行情与编纂PDF原图配准</h1>
<p><b>数据指纹：</b>13:07高点18.59；15:00低点/收盘18.03；240根唯一分钟；末成交量1917，均量MA5=1565.2、MA10=1498.4。
<b>注意：</b>图像日期虽获得极高一致性支持，但复权、原图年份、作者g/d完成级别和盘中首知尚未独立认证。</p>
<div class="grid">
<section class="panel"><h2>规范PDF原图候选页面</h2>
<p>卷三物理页170—175之间查找第54课图；页面位置依所选PDF版式而异。</p>
<div>"""+anchors+"""</div>
<iframe name="source-pdf" title="缠论卷三PDF" src='"""+pdf_uri+"""#page=170'></iframe>
<p><small>若浏览器阻止本地PDF嵌入，请点击上方页码链接独立打开。二次编纂参考：
<a href="https://xqdoc.imedao.com/15621999f6b25803feb29d4c.pdf#page=129" target="_blank">印刷第125页/PDF129页</a></small></p>
</section>
<section class="panel"><h2>从已验证文件生成的M74分钟图（下午）</h2>
<img src='"""+svg_uri+"""' alt="600151 2007-05-18一分K线复盘图">
<p><small>本图只标13:07、15:00的历史价位，未自动指派原图的g/d标签；
MACD为单日EMA初始化的教学曲线。</small></p></section>
</div>
<h2>14个作者标记的人工复核记录（尚未填写）</h2>
<p>逐个登记原图标注实际所指影线/实体、图面像素、候选分钟及价格；不得直接用局部极值自动配准，更不可把g7以后的15:00行情倒填到g7时刻。</p>
<table><thead><tr><th>标记</th><th>图面位置</th><th>市场分钟与价格</th><th>状态</th></tr></thead><tbody>"""+marks+"""</tbody></table>
<p><small>配套的JSON模板保存在同一alignment目录；一旦有可靠图像定位资料，再更新模板，不要改动原始行情。
规范PDF SHA256：<code>"""+evidence["pdf_sha256"]+"""</code><br>
M74 SVG SHA256：<code>"""+evidence["svg_sha256"]+"""</code></small></p>
</body></html>
"""


def prepare(location):
    evidence=verify_inputs(location)
    target=location["directory"]
    html=target/HTML_NAME
    meta=target/JSON_NAME
    need(not html.exists() and not meta.exists(), "existing M75 outputs must not be overwritten")
    target.mkdir(parents=True,exist_ok=True)
    html.write_text(html_viewer(location,evidence),encoding="utf-8",newline="\n")
    meta.write_text(json.dumps(image_template(evidence),ensure_ascii=False,indent=2)+"\n",
                    encoding="utf-8",newline="\n")
    return {
        "status":"M75_PROJECT_LOCAL_FIGURE_ALIGNMENT_PREPARED_G_D_NOT_CERTIFIED",
        "pdf_sha256_verified":True,
        "selected_pdf_inside_project":evidence["pdf_project_relative"],
        "svg_sha256":evidence["svg_sha256"],
        "html":str(html),"annotation_template":str(meta),
        "marker_count":14,"assigned_markers":0,
        "all_outputs_inside_canonical_project":True,
        "network_queries":0,"original_market_rows_rewritten":0,
        "F01":"OPEN","E1_E4":"NOT_RUN",
    }


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("preflight","prepare"),default="preflight")
    args=p.parse_args(argv)
    if args.mode=="preflight":
        print(json.dumps({"status":"M75_LOCAL_ALIGNMENT_PREFLIGHT",
             "project":str(project_root()),"work_root":str(private_root()),
             "svg_expected":str(project_root()/SVG_REL),
             "no_network":True,"outputs_created":0},ensure_ascii=False,indent=2))
        return 0
    print(json.dumps(prepare(files()),ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
