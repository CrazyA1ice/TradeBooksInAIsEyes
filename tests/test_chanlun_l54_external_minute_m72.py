"""M72: only fake vendor samples; no network, paid data, tokens or writes."""
from __future__ import annotations
import copy
import io
import json
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from tools import probe_chanlun_l54_external_minute_m72 as m

ROW={"open":"18.30","high":"18.59","low":"18.03",
     "close":"18.40","volume":"5","total_turnover":"92"}
ARD={"code":"600151.XSHG","time":"2007-05-18T13:21:00",
     "open":18.30,"high":18.59,"low":18.03,"close":18.40,
     "volume":5,"money":92}
class FakeFrame:
    def __init__(self,rows):
        self.rows=rows
    def iterrows(self):
        return iter(self.rows)
class FakeRQ:
    def __init__(self,rows):
        self.rows=rows;self.calls=[]
    def get_price(self,*args,**kwargs):
        self.calls.append((args,kwargs))
        return FakeFrame(self.rows)
class FakeResponse:
    def __init__(self,payload,url):
        self.body=json.dumps(payload).encode("utf-8")
        self.url=url
    def __enter__(self):
        return self
    def __exit__(self,*_):
        return False
    def geturl(self):
        return self.url
    def read(self,size=None):
        return self.body if size is None else self.body[:size]

class FakeOpener:
    def __init__(self,price=None,wrong_url=False):
        self.calls=[]
        self.price=([ARD] if price is None else price)
        self.wrong_url=wrong_url
    def __call__(self,req,timeout):
        self.calls.append((req,timeout))
        if len(self.calls)==1:
            return FakeResponse({"token":"private-jwt"},m.API_HOST+"/auth/login")
        return FakeResponse(self.price,"https://elsewhere.bad/price" if self.wrong_url
                            else m.API_HOST+"/get_price")

class M72ExternalOneDayTests(unittest.TestCase):
    def fake_rq(self,day="2007-05-18"):
        return FakeRQ([(("600151.XSHG",day+" 13:21:00"),dict(ROW))])

    def test_offline_preflight_no_market(self):
        self.assertEqual(m.preflight()["status"],
                         "M72_EXTERNAL_ONE_DAY_SOURCE_GATE_READY_NOT_QUERIED")
        self.assertFalse(m.preflight()["provider_access_rights_verified"])

    def test_access_check_never_queries_provider(self):
        with patch.dict(os.environ,{"ARDATA_API_KEY":"secret-value"}):
            a=m.access_check()
        self.assertEqual(a["status"],"OFFLINE_PROVIDER_READINESS_CHECK")
        self.assertEqual(a["provider_network_queries"],0)
        self.assertTrue(a["ardata_key_environment_present"])
        self.assertNotIn("secret-value",json.dumps(a))

    def test_rq_exact_single_day_unadjusted_nonimputed_query(self):
        fake=self.fake_rq()
        raw=m.query_rq_once(fake,"2007-05-18")
        self.assertEqual(len(fake.calls),1)
        args,kw=fake.calls[0]
        self.assertEqual(args,("600151.XSHG",))
        self.assertEqual(kw["start_date"],kw["end_date"])
        self.assertEqual(kw["start_date"],"2007-05-18")
        self.assertEqual(kw["frequency"],"1m")
        self.assertEqual(kw["adjust_type"],"none")
        self.assertEqual(kw["skip_suspended"],True)
        self.assertEqual(raw.count(b"\n"),2)

    def test_rq_2006_alternative_day_allowed(self):
        raw=m.query_rq_once(self.fake_rq(day="2006-05-18"),"2006-05-18")
        res=m.admit(raw,"RQDATA","2006-05-18","bar_end")
        self.assertEqual(res["rows"],1)
        self.assertFalse(res["chart_year_authenticated"])

    def test_rq_wrong_stock_multiindex_rejected(self):
        f=FakeFrame([(("000001.XSHE","2007-05-18 13:21:00"),dict(ROW))])
        with self.assertRaisesRegex(ValueError,"symbol"):
            m.query_rq_once(FakeRQ(f.rows),"2007-05-18")

    def test_rq_wrong_day_rejected(self):
        with self.assertRaisesRegex(ValueError,"another year or day"):
            m.query_rq_once(self.fake_rq(day="2007-05-17"),"2007-05-18")

    def test_rq_bad_order_and_duplicate_rejected(self):
        base=(("600151.XSHG","2007-05-18 13:21:00"),dict(ROW))
        reverse=(("600151.XSHG","2007-05-18 13:20:00"),dict(ROW))
        with self.assertRaisesRegex(ValueError,"increase"):
            m.query_rq_once(FakeRQ([base,reverse]),"2007-05-18")
        with self.assertRaisesRegex(ValueError,"increase"):
            m.query_rq_once(FakeRQ([base,base]),"2007-05-18")

    def test_rq_missing_field_rejected(self):
        f=FakeRQ([(("600151.XSHG","2007-05-18 13:21:00"),{"open":18})])
        with self.assertRaisesRegex(ValueError,"missing RQData"):
            m.query_rq_once(f,"2007-05-18")

    def test_rq_empty_result_is_not_vendor_absence(self):
        raw=m.query_rq_once(FakeRQ([]),"2007-05-18")
        self.assertIsNone(raw)
        report=m.admit(raw,"RQDATA","2007-05-18","bar_end")
        self.assertFalse(report["vendor_historical_coverage_absent_proven"])

    def test_admit_normalized_sha_and_anchor_hits_without_raw_quotes(self):
        raw=m.query_rq_once(self.fake_rq(),"2007-05-18")
        rep=m.admit(raw,"RQDATA","2007-05-18","bar_end")
        self.assertEqual(rep["rows"],1)
        self.assertEqual(rep["anchors"]["bar_high_exact_18_59_hits_necessary_only"],1)
        self.assertEqual(rep["anchors"]["bar_low_exact_18_03_hits_necessary_only"],1)
        self.assertEqual(rep["grid"]["grid_status"],"PARTIAL_1M_GRID_OR_VALID_NONTRADING")
        self.assertFalse(rep["historical_first_known_available"])
        self.assertEqual(rep["F01"],"OPEN")
        self.assertNotIn('"open"',json.dumps(rep))

    def test_rq_m56_rejects_bad_high_price(self):
        f=FakeRQ([(("600151.XSHG","2007-05-18 13:21:00"),
                   dict(ROW,open=19.5))])
        raw=m.query_rq_once(f,"2007-05-18")
        with self.assertRaisesRegex(ValueError,"OHLCV"):
            m.admit(raw,"RQDATA","2007-05-18","bar_end")

    def test_rq_240_end_timegrid_admission_doesnt_certify_year(self):
        times=m.m69.expected_minutes("2007-05-18","bar_end")
        rows=[(("600151.XSHG",t),dict(ROW)) for t in times]
        raw=m.query_rq_once(FakeRQ(rows),"2007-05-18")
        rep=m.admit(raw,"RQDATA","2007-05-18","bar_end")
        self.assertEqual(rep["rows"],240)
        self.assertEqual(rep["grid"]["grid_status"],"FULL_240_DECLARED_GRID_ONLY")
        self.assertFalse(rep["author_chart_identity_authenticated"])

    def test_rq_241_local_special_not_silently_complete(self):
        times=m.m69.expected_minutes("2007-05-18","bar_end")
        times=[datetime(2007,5,18,9,30),*times]
        raw=m.query_rq_once(FakeRQ([(("600151.XSHG",t),dict(ROW)) for t in times]),
                            "2007-05-18")
        rep=m.admit(raw,"RQDATA","2007-05-18","bar_end")
        self.assertEqual(rep["rows"],241)
        self.assertEqual(rep["grid"]["off_declared_grid_count"],1)
        self.assertNotEqual(rep["grid"]["grid_status"],"FULL_240_DECLARED_GRID_ONLY")

    def test_rq_more_than_300_rows_refused(self):
        rows=[{"time":"2007-05-18 13:21:00",**ROW}]*301
        with self.assertRaisesRegex(ValueError,"one-day"):
            m.encode_rows(rows,"2007-05-18")

    def test_ardata_one_login_and_one_get_price_no_data_leak(self):
        op=FakeOpener()
        raw=m.call_ardata_once("MY-PRIVATE-KEY","2007-05-18",opener=op)
        self.assertEqual(len(op.calls),2)
        login,_=op.calls[0]
        get,_=op.calls[1]
        self.assertEqual(login.get_method(),"POST")
        self.assertEqual(json.loads(login.data)["api_key"],"MY-PRIVATE-KEY")
        self.assertEqual(get.get_method(),"GET")
        self.assertIn("frequency=1m",get.full_url)
        self.assertIn("2007-05-18",get.full_url)
        self.assertNotIn("fq=",get.full_url)
        self.assertIn("private-jwt",get.get_header("Authorization"))
        self.assertNotIn(b"MY-PRIVATE-KEY",raw)
        rep=m.admit(raw,"ARDATA","2007-05-18","bar_end")
        self.assertEqual(rep["rows"],1)
        self.assertNotIn("private-jwt",json.dumps(rep))

    def test_ardata_refuses_redirect_outside_provider(self):
        with self.assertRaisesRegex(ValueError,"redirect"):
            m.call_ardata_once("secret","2007-05-18",
                               opener=FakeOpener(wrong_url=True))

    def test_ardata_wrong_symbol_rejected(self):
        with self.assertRaisesRegex(ValueError,"symbol"):
            m.from_ardata_json([dict(ARD,code="000001.XSHE")],"2007-05-18")

    def test_ardata_wrong_date_rejected(self):
        with self.assertRaisesRegex(ValueError,"another year or day"):
            m.from_ardata_json([dict(ARD,time="2006-05-18T13:21:00")],
                               "2007-05-18")

    def test_ardata_zero_rows_not_service_history_proof(self):
        self.assertIsNone(m.call_ardata_once("secret","2007-05-18",
                                            opener=FakeOpener(price=[])))
        rep=m.admit(None,"ARDATA","2007-05-18","bar_end")
        self.assertEqual(rep["status"],"PROVIDER_RETURNED_ZERO_ROWS_NOT_COVERAGE_PROOF")

    def test_malformed_data_or_nan_refused(self):
        with self.assertRaises(ValueError):
            m.from_ardata_json([dict(ARD,close="NaN")],"2007-05-18")
        with self.assertRaises(ValueError):
            m.from_ardata_json({"rows":[ARD]},"2007-05-18")

    def test_wrong_candidate_year_rejected_before_network(self):
        with self.assertRaisesRegex(ValueError,"one of the two"):
            m.encode_rows([], "2008-05-18")
        with self.assertRaisesRegex(ValueError,"unapproved"):
            m.query_rq_once(FakeRQ([]),"2008-05-18")

    def test_cli_preflight_and_access_check_offline(self):
        out=io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(m.main(["--mode","preflight"]),0)
        self.assertEqual(json.loads(out.getvalue())["real_2007_minute_rows_received"],0)
        out=io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(m.main(["--mode","access-check"]),0)
        self.assertEqual(json.loads(out.getvalue())["provider_network_queries"],0)

    def test_cli_no_rqdatac_and_missing_ardata_key_do_not_send_network(self):
        pkg=types.ModuleType("rqdatac")
        # Simulate a missing module by causing an ImportError on import.
        with patch.dict(sys.modules,{"rqdatac":None}):
            out=io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(m.main(["--mode","rqdata-once",
                      "--timestamp-convention","bar_end"]),2)
            self.assertIn("NOT_INSTALLED",out.getvalue())
        with patch.dict(os.environ,{"ARDATA_API_KEY":""}):
            out=io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(m.main(["--mode","ardata-once",
                      "--timestamp-convention","bar_end"]),2)
            self.assertIn("ENVIRONMENT_MISSING",out.getvalue())

    def test_rq_init_and_query_exception_never_prints_secret(self):
        fake=types.ModuleType("rqdatac")
        def init():
            raise ValueError("secret-credential-should-not-leak")
        fake.init=init
        with patch.dict(sys.modules,{"rqdatac":fake}):
            out=io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(m.main(["--mode","rqdata-once",
                        "--timestamp-convention","bar_end"]),3)
            self.assertIn("RQDATA_INIT_OR_QUERY_FAILED",out.getvalue())
            self.assertNotIn("secret-credential",out.getvalue())

    def test_auth_failure_never_prints_key_or_api_response(self):
        with patch.dict(os.environ,{"ARDATA_API_KEY":"super-secret-account-key"}):
            with patch.object(m,"call_ardata_once",side_effect=RuntimeError("super-secret-account-key")):
                out=io.StringIO()
                with redirect_stdout(out):
                    self.assertEqual(m.main(["--mode","ardata-once",
                                             "--timestamp-convention","bar_end"]),3)
                self.assertNotIn("super-secret-account-key",out.getvalue())
                self.assertIn("details_redacted",out.getvalue())

    def test_contract_cannot_forge_acquisition_or_known_year(self):
        spec=json.loads(m.SPEC.read_text(encoding="utf-8"))
        self.assertEqual(spec["single_stock"],"600151.XSHG")
        self.assertFalse(spec["status"]["provider_day_source_acquired"])
        spec["status"]["provider_day_source_acquired"]=True
        with self.assertRaises(ValueError):
            m.preflight(spec)

if __name__=="__main__":
    unittest.main()
