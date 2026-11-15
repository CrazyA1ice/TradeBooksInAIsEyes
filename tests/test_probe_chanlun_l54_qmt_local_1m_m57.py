"""M57 fake QMT frames: never treat the fake rows as 2007 market evidence."""
import copy
import importlib.util
import json
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/"tools/probe_chanlun_l54_qmt_local_1m_m57.py"
spec=importlib.util.spec_from_file_location("m57_local",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
CONTRACT=json.loads(m.CONTRACT.read_text(encoding="utf-8"))
PRIOR=json.loads(m.PRIOR.read_text(encoding="utf-8"))
A={"open":18.30,"high":18.59,"low":18.20,"close":18.40,"volume":5,"amount":92}
B={"open":18.40,"high":18.50,"low":18.03,"close":18.20,"volume":6,"amount":108}

class FakeFrame:
    def __init__(self,rows):
        self.rows=rows
    def iterrows(self):
        return iter(self.rows)

class FakeNative:
    def __init__(self,rows,missing=False):
        self.rows=rows
        self.calls=[]
        self.missing=missing
    def get_market_data_ex(self,**kwargs):
        self.calls.append(kwargs)
        return {} if self.missing else {m.CODE:FakeFrame(self.rows)}

class M57QMTReadOnlyContractTests(unittest.TestCase):
    def sample(self,time="2007-05-18 13:21:00",bar=None):
        return [(time,dict(A if bar is None else bar))]
    def expect_failed(self,callback):
        with self.assertRaises(ValueError):
            callback()
    def modified_invalid(self,mutator):
        d=copy.deepcopy(CONTRACT)
        mutator(d)
        self.expect_failed(lambda:m.preflight(d,copy.deepcopy(PRIOR)))

    def test_preflight_never_reports_real_data(self):
        result=m.preflight(CONTRACT,PRIOR)
        self.assertEqual(result["status"],"LOCAL_QMT_NOT_PROBED")
        self.assertEqual(result["real_market_rows_observed"],0)

    def test_xtdata_native_has_no_subscribe_keyword(self):
        self.assertNotIn("subscribe",m.ARGS)
        self.assertEqual(m.ARGS["fill_data"],False)
        self.assertEqual(m.ARGS["dividend_type"],"none")

    def test_only_one_stock_day_requested(self):
        self.assertEqual(m.ARGS["stock_list"],["600151.SH"])
        self.assertEqual(m.ARGS["start_time"],"20070518093000")
        self.assertEqual(m.ARGS["end_time"],"20070518150000")

    def test_exactly_one_native_read_and_no_download(self):
        fake=FakeNative(self.sample())
        r=m.query_local_native(fake)
        self.assertEqual(len(fake.calls),1)
        self.assertEqual(fake.calls[0],m.ARGS)
        self.assertEqual(r["status"],"LOCAL_QMT_CANDIDATE_BARS_FOUND_UNAUTHENTICATED")

    def test_local_result_does_not_authenticate_chart(self):
        r=m.query_local_native(FakeNative(self.sample()))
        self.assertFalse(r["chart_date_authenticated"])
        self.assertFalse(r["provider_origin_authenticated"])
        self.assertFalse(r["market_movement_complete"])
        self.assertFalse(r["subminute_order_recovered"])
        self.assertFalse(r["phi20_proven"])

    def test_empty_local_cache_not_evidence_of_vendor_absence(self):
        r=m.query_local_native(FakeNative([]))
        self.assertEqual(r["status"],"QMT_LOCAL_DATA_ABSENT_NOT_PROVIDER_PROOF")
        self.assertFalse(r["provider_history_absence_proven"])

    def test_absent_symbol_local_cache(self):
        r=m.query_local_native(FakeNative(self.sample(),missing=True))
        self.assertEqual(r["status"],"QMT_LOCAL_DATA_ABSENT_NOT_PROVIDER_PROOF")

    def test_two_row_price_envelope(self):
        f=FakeNative([("2007-05-18 13:21:00",A),("2007-05-18 13:22:00",B)])
        r=m.query_local_native(f)
        self.assertEqual(r["min_max_price"],["18.03","18.59"])
        self.assertEqual(r["rows"],2)
        self.assertTrue(r["chart_18_59_within_full_day_range_necessary_not_sufficient"])

    def test_historical_14_digit_timestamp(self):
        self.assertEqual(m.parse_index(20070518132100).strftime("%Y-%m-%d %H:%M"),"2007-05-18 13:21")

    def test_epoch_millis_converts_beijing(self):
        millis=int(datetime(2007,5,18,13,21,tzinfo=timezone(timedelta(hours=8))).timestamp()*1000)
        self.assertEqual(m.parse_index(millis).strftime("%Y-%m-%d %H:%M"),"2007-05-18 13:21")

    def test_datetime_and_ISO_string(self):
        self.assertEqual(m.parse_index(datetime(2007,5,18,13,21)).hour,13)
        self.assertEqual(m.parse_index("2007-05-18T13:21:00").minute,21)

    def test_wrong_calendar_day_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample("2007-05-17 13:21:00"))))

    def test_duplicate_bar_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample()+self.sample())))

    def test_reverse_bar_order_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative([("2007-05-18 13:22:00",B),("2007-05-18 13:21:00",A)])))

    def test_lunch_period_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample("2007-05-18 12:05:00"))))

    def test_nonminute_second_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample("2007-05-18 13:21:02"))))

    def test_bad_OHLC_high_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample(bar=dict(A,open=19)))))

    def test_negative_volume_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample(bar=dict(A,volume=-1)))))

    def test_NaN_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample(bar=dict(A,high=float("nan"))))))

    def test_negative_amount_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample(bar=dict(A,amount=-4)))))

    def test_missing_fields_rejected(self):
        self.expect_failed(lambda:m.query_local_native(FakeNative(self.sample(bar={"open":18.3}))))

    def test_wrong_response_container_rejected(self):
        class Invalid:
            def get_market_data_ex(self,**kwargs):
                return ["not a dictionary"]
        self.expect_failed(lambda:m.query_local_native(Invalid()))

    def test_wrong_stock_claim_refused(self):
        self.modified_invalid(lambda d:d.__setitem__("instrument","000001.SZ"))

    def test_wrong_date_claim_refused(self):
        self.modified_invalid(lambda d:d.__setitem__("candidate_date","2006-05-18"))

    def test_fill_data_true_refused(self):
        self.modified_invalid(lambda d:d["xtdata_native_args"].__setitem__("fill_data",True))

    def test_unallowed_subscribe_parameter_refused(self):
        self.modified_invalid(lambda d:d["xtdata_native_args"].__setitem__("subscribe",False))

    def test_forged_QMT_coverage_refused(self):
        self.modified_invalid(lambda d:d["forbidden_outcome_claims"].__setitem__("day_data_acquired",True))

    def test_TDX_file_unverified(self):
        self.modified_invalid(lambda d:d["tdx_reuse"].__setitem__("contains_requested_day","YES"))

if __name__=="__main__":
    unittest.main()
