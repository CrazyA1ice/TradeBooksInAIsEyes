"""M56: provenance boundary, chart-year uncertainty and minute order non-identifiability."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"tools/audit_chanlun_l54_2007_minute_candidate_m56.py"
spec=importlib.util.spec_from_file_location("m56",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
DOC=json.loads(m.CONTRACT.read_text(encoding="utf-8"))
CHART=json.loads(m.CHART.read_text(encoding="utf-8"))
M54=json.loads(m.M54.read_text(encoding="utf-8"))
M55=json.loads(m.M55.read_text(encoding="utf-8"))
HEADER="time,open,high,low,close,volume,amount\n"
GOOD=("2007-05-18 13:21:00,18.30,18.50,18.20,18.40,4,73.40\n"
      "2007-05-18 13:22:00,18.40,18.59,18.03,18.20,10,185.30\n"
      "2007-05-18 13:23:00,18.20,18.45,18.10,18.30,8,140.00\n")

class M56HistoricalEntryTest(unittest.TestCase):
    def audit_copy(self):
        return m.audit(copy.deepcopy(DOC),copy.deepcopy(CHART),copy.deepcopy(M54),copy.deepcopy(M55))
    def invalid_spec(self,change):
        d=copy.deepcopy(DOC)
        change(d)
        with self.assertRaises(ValueError):
            m.audit(d,copy.deepcopy(CHART),copy.deepcopy(M54),copy.deepcopy(M55))
    def csv(self,data=GOOD,date="2007-05-18",time_type="bar_end"):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"private_candidate.csv"
            path.write_text(HEADER+data,encoding="utf-8")
            return m.inspect_candidate_csv(path,date,time_type)

    def test_no_real_data_claim(self):
        self.assertEqual(self.audit_copy()["status"],"NOT_ACQUIRED_YEAR_UNCONFIRMED")
    def test_chart_year_not_on_picture(self):
        self.assertFalse(self.audit_copy()["chart_year_independently_confirmed"])
    def test_market_date_not_authenticated(self):
        self.assertFalse(self.audit_copy()["source_specific_2007_1m_coverage_confirmed"])
    def test_screenshot_levels_distinct(self):
        self.assertEqual(DOC["source_pdf"]["chart_peak_annotation"],"18.59")
        self.assertEqual(DOC["source_pdf"]["chart_right_annotation"],"18.03")
        self.assertEqual(DOC["source_pdf"]["author_prose_g0"],"18.50")
    def test_candidate_vendor_coverage_not_proven(self):
        self.assertTrue(all(not p["specific_2007_600151_coverage_confirmed"] for p in DOC["external_provider_candidates"]))
    def test_synthetic_ohlcva_equal(self):
        a=DOC["two_synthetic_tick_order_counterexamples"]
        self.assertEqual(m.aggregate(a["path_H_then_L"]),m.aggregate(a["path_L_then_H"]))
    def test_synthetic_HL_order_not_equal(self):
        a=DOC["two_synthetic_tick_order_counterexamples"]
        self.assertLess(a["path_H_then_L"].index("18.50"),a["path_H_then_L"].index("18.20"))
        self.assertGreater(a["path_L_then_H"].index("18.50"),a["path_L_then_H"].index("18.20"))
    def test_csv_valid_schema_never_certifies_real_market(self):
        r=self.csv()
        self.assertEqual(r["status"],"CANDIDATE_CSV_SCHEMA_ONLY_UNAUTHENTICATED")
        self.assertEqual(r["rows"],3)
        self.assertFalse(r["chart_identity_matched"])
        self.assertFalse(r["completed_market_movement_proved"])
    def test_csv_reports_range_only_not_chart_match(self):
        r=self.csv()
        self.assertTrue(r["chart_price_anchors_within_range_necessary_only"]["18.59"])
        self.assertEqual(r["chart_afternoon_bar_count"],3)
        self.assertFalse(r["chart_identity_matched"])
    def test_csv_sha_not_vendor_auth(self):
        self.assertFalse(self.csv()["file_hash_is_vendor_authentication"])
    def test_declared_bar_start_not_silently_changed(self):
        self.assertEqual(self.csv(time_type="bar_start")["timestamp_convention"],"bar_start")
    def test_wrong_date_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(date="2006-05-18")
    def test_invalid_date_candidate_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(date="2008-05-18")
    def test_duplicate_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data=GOOD+GOOD.splitlines(True)[0])
    def test_unsorted_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data="".join(reversed(GOOD.splitlines(True))))
    def test_nontrading_time_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data="2007-05-18 12:00:00,18,19,17,18,1,18\n")
    def test_negative_volume_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data="2007-05-18 13:21:00,18,19,17,18,-1,18\n")
    def test_bad_high_low_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data="2007-05-18 13:21:00,20,19,17,18,1,18\n")
    def test_nonfinite_price_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data="2007-05-18 13:21:00,NaN,19,17,18,1,18\n")
    def test_year_cannot_be_adopted_from_publication(self):
        self.invalid_spec(lambda d:d.__setitem__("date_proof_status","YEAR_PROVEN"))
    def test_supplier_coverage_cannot_be_asserted(self):
        self.invalid_spec(lambda d:d["external_provider_candidates"][0].__setitem__("specific_2007_600151_coverage_confirmed",True))
    def test_fake_download_rejected(self):
        self.invalid_spec(lambda d:d.__setitem__("real_600151_2007_1m_rows_ingested",240))
    def test_completion_from_ohlc_rejected(self):
        self.invalid_spec(lambda d:d["forbidden_upgrade_flags"].__setitem__("ohlcv_alone_treated_as_subminute_path",True))
    def test_chart_title_drift_rejected(self):
        self.invalid_spec(lambda d:d["source_pdf"].__setitem__("verified_image_chart_title","OTHER"))
    def test_fake_author_source_symbol_rejected(self):
        self.invalid_spec(lambda d:d["source_pdf"].__setitem__("author_prose_g0","18.59"))
    def test_foreign_stock_rejected(self):
        self.invalid_spec(lambda d:d["candidate_instrument"].__setitem__("code","000001.SZ"))
    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data="")
    def test_non_1m_seconds_rejected(self):
        with self.assertRaises(ValueError):
            self.csv(data="2007-05-18 13:21:12,18,19,17,18,1,18\n")
    def test_M54_source_drift_rejected(self):
        other=copy.deepcopy(M54)
        other["id"]="OTHER"
        with self.assertRaises(ValueError):
            m.audit(copy.deepcopy(DOC),copy.deepcopy(CHART),other,copy.deepcopy(M55))

if __name__=="__main__":
    unittest.main()
