"""M73 2007 public stock-minute archive: synthetic fixture only, no network."""
from __future__ import annotations

import copy
import hashlib
import io
import json
import unittest
from urllib import error as urlerror
from contextlib import redirect_stdout
from tools import probe_chanlun_l54_public_archive_m73 as m

DAY="2007-05-18"
PATH="A股分钟/2000-2024/2007/1分钟/sh600151.csv"
CSV_SAMPLE=("date,time,open,high,low,close,volume,amount\n"
            "2007-05-17,0931,15.30,15.40,15.20,15.31,70,1000\n"
            "2007-05-18,1321,18.50,18.59,18.03,18.40,7,1500\n"
            "2007-05-18,1322,18.40,18.50,18.30,18.50,6,1000\n"
            "2007-05-21,0931,15.20,15.20,15.00,15.10,20,300\n").encode()
ZZ_ROW={"ts_code":"600151.SH","trade_time":"200705181321",
        "open":18.5,"high":18.59,"low":18.03,
        "close":18.4,"vol":7,"amount":1500}

class M73PublicMinuteTests(unittest.TestCase):
    def test_preflight_is_no_network_receipt(self):
        r=m.preflight()
        self.assertEqual(r["provider_network_queries"],0)
        self.assertFalse(r["data_2007_observed"])
        self.assertEqual(r["F01"],"OPEN")

    def test_hf_filename_variants_only_stock_600151(self):
        for name in ("600151.csv","SH600151.csv","600151.SH.csv",
                     "600151.XSHG.csv","sh-600151.csv"):
            self.assertIn(m.normalize_name(name),m.ALLOWED_FILENAMES)
        self.assertNotIn(m.normalize_name("600152.csv"),m.ALLOWED_FILENAMES)
        self.assertNotIn(m.normalize_name("600151.txt"),m.ALLOWED_FILENAMES)

    def test_hf_directory_single_page_finds_target(self):
        seen=[]
        def fake(url):
            seen.append(url)
            return ([{"type":"file","path":"A股分钟/2000-2024/2007/1分钟/600152.csv","size":19},
                     {"type":"file","path":PATH,"size":len(CSV_SAMPLE)}],{})
        r=m.hf_directory_file(DAY,getter=fake)
        self.assertEqual(r["path"],PATH)
        self.assertEqual(len(seen),1)
        self.assertIn("2007",seen[0])
        self.assertNotIn("2006",seen[0])

    def test_hf_paginated_listing_can_find_second_page(self):
        seen=[]
        def fake(url):
            seen.append(url)
            if len(seen)==1:
                return ([{"type":"file","path":"A股分钟/2000-2024/2007/1分钟/600152.csv","size":19}],
                        {"Link":'<https://huggingface.co/api/datasets/OxFengyuan/stock_dataset/tree/main/A%E8%82%A1%E5%88%86%E9%92%9F/2000-2024/2007/1%E5%88%86%E9%92%9F?limit=1000&cursor=cursor123>; rel="next"'})
            return ([{"type":"file","path":PATH,"size":len(CSV_SAMPLE)}],{})
        r=m.hf_directory_file(DAY,getter=fake)
        self.assertEqual(len(seen),2)
        self.assertEqual(r["pages_scanned"],2)

    def test_hf_unlisted_file_not_vendor_absence(self):
        r=m.hf_directory_file(DAY,getter=lambda _:([{"type":"file","path":"A股分钟/2000-2024/2007/1分钟/600152.csv","size":9}],{}))
        self.assertFalse(r["dataset_absence_proven"])

    def test_hf_bigger_file_refused(self):
        def fake(_):
            return ([{"type":"file","path":PATH,"size":m.MAX_HF_FILE+1}],{})
        with self.assertRaisesRegex(ValueError,"30 MiB"):
            m.hf_directory_file(DAY,getter=fake)

    def test_hf_wrong_year_path_refused(self):
        def fake(_):
            return ([{"type":"file","path":PATH.replace("2007/","2006/"),"size":99}],{})
        r=m.hf_directory_file(DAY,getter=fake)
        self.assertEqual(r["status"],"HF_TARGET_NOT_FOUND_IN_LISTED_DIRECTORY")

    def test_hf_data_selects_only_target_date(self):
        p=m.csv_annual_day_rows(CSV_SAMPLE,DAY)
        self.assertEqual(p["annual_rows"],4)
        self.assertEqual(len(p["rows"]),2)
        self.assertEqual(p["rows"][0]["time"].strftime("%Y%m%d%H%M"),"200705181321")

    def test_hf_chinese_date_and_time_columns_are_distinct_minutes(self):
        # Matches the observed vendor layout, not the synthetic English fixture.
        raw=("日期,时间,开盘,最高,最低,收盘,成交量,成交额\n"
             "2007-05-18,09:31,18.50,18.59,18.03,18.40,7,1500\n"
             "2007-05-18,09:32,18.40,18.50,18.30,18.50,6,1000\n"
             "2007-05-18,15:00,18.50,18.50,18.50,18.50,9,4000\n").encode("utf-8")
        parsed=m.csv_annual_day_rows(raw,DAY)
        self.assertEqual(parsed["annual_rows"],3)
        self.assertEqual([x["time"].strftime("%H:%M") for x in parsed["rows"]],
                         ["09:31","09:32","15:00"])
        self.assertEqual(len({x["time"] for x in parsed["rows"]}),3)
        report=m.hf_once(DAY,"bar_end",
                         listing=lambda _:{"path":PATH,"size":len(raw)},
                         fetcher=lambda _,__:(raw,{}))
        self.assertEqual(report["admission"]["rows"],3)
        self.assertEqual(report["admission"]["grid"]["observed_rows"],3)
        self.assertEqual(report["admission"]["grid"]["off_declared_grid_count"],0)
        self.assertEqual(report["admission"]["F01"],"OPEN")

    def test_date_only_minute_is_not_silent_midnight(self):
        self.assertIsNone(m.parse_time_parts({"日期":DAY}))
        self.assertIsNone(m.parse_time_parts({"日期":DAY,"时间":""}))
        self.assertIsNone(m.parse_time_parts({"date":DAY}))
        self.assertEqual(m.parse_time_parts({"时间":"2007-05-18 09:31"}).strftime("%H:%M"),"09:31")

    def test_hf_single_file_is_admitted_via_m56(self):
        metadata={"path":PATH,"size":len(CSV_SAMPLE),
                  "lfs":{"oid":hashlib.sha256(CSV_SAMPLE).hexdigest()}}
        r=m.hf_once(DAY,"bar_end",listing=lambda _:metadata,
                    fetcher=lambda _,__: (CSV_SAMPLE,{}))
        self.assertEqual(r["status"],"HF_PUBLIC_ANNUAL_CSV_TARGET_DAY_ADMITTED_NOT_AUTHOR_AUTHENTICATED")
        self.assertEqual(r["admission"]["rows"],2)
        self.assertTrue(r["hf_repository_lfs_sha256_matches_download"])
        self.assertEqual(r["admission"]["anchors"]["bar_high_exact_18_59_hits_necessary_only"],1)
        self.assertEqual(r["admission"]["F01"],"OPEN")
        self.assertFalse(r["original_chart_year_authenticated"])
        self.assertNotIn('"open": "18.50"',json.dumps(r))

    def test_hf_anonymous_listing_401_falls_back_to_one_exact_stock_file(self):
        def metadata_blocked(day):
            self.assertEqual(day,DAY)
            raise urlerror.HTTPError("https://huggingface.co/",401,"Unauthorized",{},None)
        requested=[]
        def fake_fetch(url,cap):
            requested.append((url,cap))
            return CSV_SAMPLE,{}
        r=m.hf_once(DAY,"bar_end",listing=metadata_blocked,fetcher=fake_fetch)
        self.assertEqual(r["admission"]["rows"],2)
        self.assertTrue(r["direct_filename_guess_not_metadata_authenticated"])
        self.assertIn("sh600151.csv",requested[0][0])
        self.assertEqual(len(requested),1)
        self.assertEqual(requested[0][1],m.MAX_HF_FILE)
        self.assertEqual(r["admission"]["adjustment"],"UNVERIFIED_NOT_RQDATA_REQUEST")

    def test_zzshare_admission_never_claims_rqdata_adjustment(self):
        r=m.zzshare_once(DAY,"bar_end",getter=lambda _:
            ({"code":200,"data":[dict(ZZ_ROW)]},{}))
        self.assertEqual(r["admission"]["adjustment"],"UNVERIFIED_NOT_RQDATA_REQUEST")
        self.assertIsNone(r["admission"]["skip_suspended_rqdata"])

    def test_hf_lfs_blob_hash_mismatch_refused(self):
        metadata={"path":PATH,"size":len(CSV_SAMPLE),"lfs":{"oid":"0"*64}}
        with self.assertRaisesRegex(ValueError,"sha256 mismatch"):
            m.hf_once(DAY,"bar_end",listing=lambda _:metadata,
                      fetcher=lambda _,__: (CSV_SAMPLE,{}))

    def test_hf_annual_sha_sized_mismatch_refused(self):
        metadata={"path":PATH,"size":100}
        with self.assertRaisesRegex(ValueError,"size disagrees"):
            m.hf_once(DAY,"bar_end",listing=lambda _:metadata,
                      fetcher=lambda _,__: (CSV_SAMPLE,{}))

    def test_hf_2006_alternative_allowed_not_autoyear(self):
        p=m.csv_annual_day_rows(CSV_SAMPLE.replace(b"2007-05-18",b"2006-05-18"),
                                "2006-05-18")
        self.assertEqual(len(p["rows"]),2)

    def test_csv_nonfinite_rejected_by_old_gate(self):
        s=CSV_SAMPLE.replace(b"18.59",b"NaN")
        metadata={"path":PATH,"size":len(s)}
        with self.assertRaises(ValueError):
            m.hf_once(DAY,"bar_end",listing=lambda _:metadata,fetcher=lambda _,__: (s,{}))

    def test_csv_wrong_header_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"unexpected annual CSV columns"):
            m.csv_annual_day_rows(b"x,y,z\n1,2,3\n",DAY)

    def test_csv_no_target_day_is_zero_without_claiming_absence(self):
        raw=CSV_SAMPLE.replace(b"2007-05-18",b"2007-05-17")
        metadata={"path":PATH,"size":len(raw)}
        r=m.hf_once(DAY,"bar_end",listing=lambda _:metadata,fetcher=lambda _,__: (raw,{}))
        self.assertEqual(r["day_bars"],0)
        self.assertFalse(r["provider_coverage_proven"])

    def test_csv_over_300_same_day_rejected(self):
        head=b"date,time,open,high,low,close,volume\n"
        rows=[f"2007-05-18,{i:04d},18,18,18,18,1\n".encode() for i in range(301)]
        # Some invalid minutes are skipped, but count of >300 valid bars must fail.
        # Alternatively all same minute duplicates >300 are still bounded.
        rows=[b"2007-05-18,1321,18,18,18,18,1\n"]*301
        with self.assertRaisesRegex(ValueError,"maximum minute bars"):
            m.csv_annual_day_rows(head+b"".join(rows),DAY)

    def test_zzshare_one_success_query_correct_path(self):
        seen=[]
        def fake(url):
            seen.append(url)
            return ({"code":200,"data":[dict(ZZ_ROW)]},{})
        r=m.zzshare_once(DAY,"bar_end",getter=fake)
        self.assertEqual(r["admission"]["rows"],1)
        self.assertIn("freq=1min",seen[0])
        self.assertIn("20070518",seen[0])
        self.assertEqual(r["admission"]["F01"],"OPEN")
        self.assertEqual(r["provider"],"ZZSHARE")
        self.assertNotIn('"open": 18.5',json.dumps(r))

    def test_zzshare_empty_not_history_absence(self):
        r=m.zzshare_once(DAY,"bar_end",getter=lambda _:({"code":200,"data":[]},{}))
        self.assertEqual(r["status"],"ZZSHARE_ZERO_ROWS_NOT_HISTORICAL_COVERAGE_PROOF")
        self.assertFalse(r["provider_history_absence_proven"])

    def test_zzshare_auth_error_not_history_absence(self):
        r=m.zzshare_once(DAY,"bar_end",getter=lambda _:({"code":401,"msg":"secret"},{}))
        self.assertEqual(r["api_code"],401)
        self.assertNotIn("secret",json.dumps(r))

    def test_zzshare_wrong_stock_rejected(self):
        with self.assertRaisesRegex(ValueError,"another stock"):
            m.zzshare_once(DAY,"bar_end",getter=lambda _:
                ({"code":200,"data":[dict(ZZ_ROW,ts_code="000001.SZ")]},{}))

    def test_zzshare_wrong_day_rejected(self):
        with self.assertRaisesRegex(ValueError,"same day"):
            m.zzshare_once(DAY,"bar_end",getter=lambda _:
                ({"code":200,"data":[dict(ZZ_ROW,trade_time="200605181321")]},{}))

    def test_zzshare_bad_price_rejected_by_m56(self):
        with self.assertRaises(ValueError):
            m.zzshare_once(DAY,"bar_end",getter=lambda _:
                ({"code":200,"data":[dict(ZZ_ROW,high=0.1)]},{}))

    def test_cli_offline(self):
        sink=io.StringIO()
        with redirect_stdout(sink):
            rc=m.main(["--mode","preflight"])
        self.assertEqual(rc,0)
        self.assertEqual(json.loads(sink.getvalue())["provider_network_queries"],0)

    def test_cli_network_mode_must_have_time_convention(self):
        with self.assertRaisesRegex(ValueError,"explicit convention"):
            m.main(["--mode","hf-once"])
        with self.assertRaisesRegex(ValueError,"explicit convention"):
            m.main(["--mode","zzshare-once"])

    def test_cli_error_is_redacted(self):
        old=m.hf_once
        try:
            def boom(*args,**kwargs):
                raise RuntimeError("untrusted_url_with_credential")
            m.hf_once=boom
            sink=io.StringIO()
            with redirect_stdout(sink):
                rc=m.main(["--mode","hf-once","--timestamp-convention","bar_end"])
            self.assertEqual(rc,3)
            self.assertIn("error_detail_redacted",sink.getvalue())
            self.assertNotIn("credential",sink.getvalue())
        finally:
            m.hf_once=old

    def test_contract_cannot_invent_2007_market_acquisition(self):
        doc=json.loads(m.SPEC.read_text(encoding="utf-8"))
        doc["source_status"]["2007_1m_acquired"]=True
        with self.assertRaisesRegex(ValueError,"cannot fake"):
            m.preflight(doc)

    def test_http_request_is_pinned_to_two_hosts(self):
        with self.assertRaisesRegex(ValueError,"unexpected remote"):
            m.http_read("https://evil.example.com/api",100,opener=lambda *_:None)

    def test_no_untrusted_market_data_github_writes_by_default(self):
        spec=json.loads(m.SPEC.read_text(encoding="utf-8"))
        self.assertFalse(spec["raw_rows_to_stdout"])
        self.assertFalse(spec["write_market_data_to_git"])
        self.assertTrue(spec["default_no_network"])

if __name__=="__main__":
    unittest.main()
