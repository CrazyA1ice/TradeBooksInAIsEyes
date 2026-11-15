"""M69: 600151 one-shot native-local QMT -> M56 bytes -> 240-slot diagnosis.

ALL frames are explicit fake fixtures. These tests DO NOT access a real QMT
terminal, paid bars, user data directories, stock orders, or provider network.
"""
import csv
import io
import json
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from tools import admit_chanlun_l54_local_qmt_m69 as m
from tools import audit_chanlun_l54_2007_minute_candidate_m56 as m56
from tools import probe_chanlun_l54_qmt_local_1m_m57 as m57

PRICE={"open":18.30,"high":18.59,"low":18.03,"close":18.40,"volume":5,"amount":92}
GOOD="time,open,high,low,close,volume,amount\n2007-05-18 13:21:00,18.30,18.59,18.03,18.40,5,92\n"
class FakeFrame:
    def __init__(self,rows):
        self.rows=rows
    def iterrows(self):
        return iter(self.rows)
class FakeQMT:
    def __init__(self,rows,empty_symbol=False):
        self.rows=rows
        self.empty_symbol=empty_symbol
        self.calls=[]
    def get_market_data_ex(self,**kwargs):
        self.calls.append(kwargs)
        return {} if self.empty_symbol else {m.CODE:FakeFrame(self.rows)}

def raw_with_times(times):
    s=io.StringIO(newline="")
    writer=csv.writer(s,lineterminator="\n")
    writer.writerow(m.FIELDS)
    for t in times:
        writer.writerow([t.strftime("%Y-%m-%d %H:%M:%S"),"18.30","18.59","18.03","18.40","5","92"])
    return s.getvalue().encode("utf-8")

class M69LocalSourceTests(unittest.TestCase):
    def sample(self):
        return FakeQMT([("2007-05-18 13:21:00",dict(PRICE)),
                        ("2007-05-18 13:22:00",dict(PRICE))])

    def test_preflight_no_qmt_or_real_data_called(self):
        x=m.preflight()
        self.assertEqual(x["status"],"M69_LOCAL_SOURCE_READ_NOT_YET_RUN")
        self.assertFalse(x["user_local_cache_inspected"])
        self.assertEqual(x["market_experiments"],"NOT_RUN")

    def test_qmt_single_call_and_exact_no_download_args(self):
        xt=self.sample()
        raw=m.native_qmt_bytes(xt)
        self.assertEqual(xt.calls,[m57.ARGS])
        self.assertNotIn("subscribe",xt.calls[0])
        self.assertEqual(xt.calls[0]["fill_data"],False)
        self.assertEqual(xt.calls[0]["dividend_type"],"none")
        self.assertEqual(raw.count(b"\n"),3)

    def test_qmt_frame_validates_with_existing_m56_without_disk(self):
        raw=m.native_qmt_bytes(self.sample())
        a=m.inspect_blob(raw,m.DAY,"bar_start","QMT_NATIVE_LOCAL_CACHE_READ")
        self.assertEqual(a["schema"]["status"],"CANDIDATE_CSV_SCHEMA_ONLY_UNAUTHENTICATED")
        self.assertEqual(a["schema"]["rows"],2)
        self.assertEqual(a["minute_grid"]["missing_slot_count"],238)
        self.assertEqual(a["minute_grid"]["off_declared_grid_count"],0)
        self.assertEqual(a["minute_grid"]["grid_status"],"PARTIAL_1M_GRID_OR_VALID_NONTRADING")
        self.assertFalse(a["chart_identity_authenticated"])
        self.assertFalse(a["M68_L17_asof_bar_close_certified"])
        self.assertEqual(a["F01"],"OPEN")

    def test_csv_bytes_m56_equals_backward_compatible_file_mode(self):
        raw=GOOD.encode("utf-8")
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"cand.csv"
            path.write_bytes(raw)
            one=m56.inspect_candidate_csv(path,m.DAY,"bar_start")
            two=m56.inspect_candidate_csv_bytes(raw,m.DAY,"bar_start")
        self.assertEqual(one,two)
        self.assertEqual(two["rows"],1)

    def test_full_240_bar_start_grid_is_only_timegrid_success(self):
        raw=raw_with_times(m.expected_minutes(m.DAY,"bar_start"))
        x=m.inspect_blob(raw,m.DAY,"bar_start","USER_PROVIDED_CSV")
        self.assertEqual(x["minute_grid"]["grid_status"],"FULL_240_DECLARED_GRID_ONLY")
        self.assertEqual(x["minute_grid"]["missing_slot_count"],0)
        self.assertEqual(x["minute_grid"]["off_declared_grid_count"],0)
        self.assertFalse(x["minute_grid"]["provider_2007_coverage_verified"])
        self.assertEqual(x["historical_bar_close_first_known_at"],"UNKNOWN_NOT_DERIVABLE_FROM_CACHED_1M")

    def test_full_240_bar_end_grid(self):
        raw=raw_with_times(m.expected_minutes(m.DAY,"bar_end"))
        x=m.inspect_blob(raw,m.DAY,"bar_end","USER_PROVIDED_CSV")
        self.assertEqual(x["minute_grid"]["grid_status"],"FULL_240_DECLARED_GRID_ONLY")
        self.assertEqual(x["minute_grid"]["missing_slot_count"],0)

    def test_false_convention_reports_offgrid_not_chart_proof(self):
        raw=raw_with_times(m.expected_minutes(m.DAY,"bar_end"))
        x=m.inspect_blob(raw,m.DAY,"bar_start","USER_PROVIDED_CSV")
        self.assertEqual(x["minute_grid"]["grid_status"],"TIMESTAMP_CONVENTION_CONFLICT_OR_SPECIAL_PROVIDER_BAR")
        self.assertGreater(x["minute_grid"]["off_declared_grid_count"],0)
        self.assertFalse(x["minute_grid"]["grid_matches_under_declared_convention"])

    def test_one_missing_valid_bar_not_evidence_of_provider_absence(self):
        times=m.expected_minutes(m.DAY,"bar_end")
        x=m.inspect_blob(raw_with_times(times[:-1]),m.DAY,"bar_end","USER_PROVIDED_CSV")
        self.assertEqual(x["minute_grid"]["missing_slot_count"],1)
        self.assertEqual(x["minute_grid"]["grid_status"],"PARTIAL_1M_GRID_OR_VALID_NONTRADING")
        self.assertFalse(x["minute_grid"]["provider_2007_coverage_verified"])

    def test_empty_native_qmt_is_not_provider_absence(self):
        xt=FakeQMT([],empty_symbol=True)
        self.assertIsNone(m.native_qmt_bytes(xt))
        self.assertEqual(len(xt.calls),1)
        self.assertIsNone(m.native_qmt_bytes(FakeQMT([])))

    def test_native_wrong_date_rejected(self):
        with self.assertRaises(ValueError):
            m.native_qmt_bytes(FakeQMT([("2007-05-17 13:21:00",dict(PRICE))]))

    def test_native_out_of_order_rejected(self):
        with self.assertRaises(ValueError):
            m.native_qmt_bytes(FakeQMT([("2007-05-18 13:22:00",dict(PRICE)),
                                        ("2007-05-18 13:21:00",dict(PRICE))]))

    def test_native_invalid_ohlc_rejected(self):
        with self.assertRaises(ValueError):
            m.native_qmt_bytes(FakeQMT([("2007-05-18 13:21:00",dict(PRICE,high=17))]))

    def test_native_bad_container_rejected(self):
        class Wrong:
            def get_market_data_ex(self,**kwargs):
                return []
        with self.assertRaises(ValueError):
            m.native_qmt_bytes(Wrong())

    def test_wrong_convention_and_source_grade_rejected(self):
        raw=GOOD.encode("utf-8")
        with self.assertRaisesRegex(ValueError,"timestamp convention"):
            m.inspect_blob(raw,m.DAY,"auto","USER_PROVIDED_CSV")
        with self.assertRaisesRegex(ValueError,"source origin"):
            m.inspect_blob(raw,m.DAY,"bar_start","AUTHENTICATED_EXCHANGE")

    def test_private_save_is_opt_in_outside_git_and_no_clobber(self):
        raw=m.native_qmt_bytes(self.sample())
        report=m.inspect_blob(raw,m.DAY,"bar_start","QMT_NATIVE_LOCAL_CACHE_READ")
        with tempfile.TemporaryDirectory() as d:
            saved=m.save_private(raw,report,d)
            p=Path(saved["local_evidence_csv"])
            receipt=Path(saved["local_evidence_receipt"])
            self.assertEqual(p.read_bytes(),raw)
            self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["byte_sha256"],report["byte_sha256"])
            self.assertTrue(saved["private_files_only"])
            m.save_private(raw,report,d) # verified idempotence; no overwrite
            p.write_text("CORRUPTED",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"must not be overwritten"):
                m.save_private(raw,report,d)

    def test_inside_repo_private_save_rejected(self):
        raw=m.native_qmt_bytes(self.sample())
        report=m.inspect_blob(raw,m.DAY,"bar_start","QMT_NATIVE_LOCAL_CACHE_READ")
        with self.assertRaisesRegex(ValueError,"outside git"):
            m.save_private(raw,report,m.ROOT/"private-evidence")

    def test_csv_origin_cannot_be_saved_or_claim_market_first_known(self):
        raw=GOOD.encode("utf-8")
        report=m.inspect_blob(raw,m.DAY,"bar_start","USER_PROVIDED_CSV")
        self.assertEqual(report["instrument"],"600151.SH_CSV_SELF_DECLARED")
        self.assertFalse(report["byte_digest_is_provider_authentication"])
        self.assertEqual(report["real_market_experiments"],"NOT_RUN")
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"no source-copy"):
                m.save_private(raw,report,d)

    def test_csv_2006_year_alternative_is_not_2007_proof(self):
        raw=GOOD.replace("2007-05-18","2006-05-18").encode("utf-8")
        out=m.inspect_blob(raw,"2006-05-18","bar_start","USER_PROVIDED_CSV")
        self.assertEqual(out["candidate_date"],"2006-05-18")
        self.assertFalse(out["candidate_year_proved"])

    def test_cli_csv_read_only_and_explicit_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"source.csv";p.write_bytes(GOOD.encode("utf-8"))
            output=io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(m.main(["--mode","csv","--input-csv",str(p),
                                         "--timestamp-convention","bar_start"]),0)
            result=json.loads(output.getvalue())
            self.assertEqual(result["schema"]["rows"],1)
            self.assertEqual(sorted(x.name for x in Path(d).iterdir()),["source.csv"])

    def test_cli_qmt_fake_module_only_no_download_default_no_files(self):
        fake=self.sample()
        package=types.ModuleType("xtquant")
        package.xtdata=fake
        output=io.StringIO()
        with patch.dict(sys.modules,{"xtquant":package}),redirect_stdout(output):
            result=m.main(["--mode","qmt-local","--timestamp-convention","bar_start"])
        self.assertEqual(result,0)
        self.assertEqual(len(fake.calls),1)
        out=json.loads(output.getvalue())
        self.assertEqual(out["schema"]["rows"],2)
        self.assertNotIn("local_private_export",out)

    def test_source_contract_still_says_market_not_run(self):
        spec=json.loads(m.SPEC.read_text(encoding="utf-8"))
        self.assertEqual(spec["instrument"],m.CODE)
        self.assertFalse(spec["current_status"]["real_1m_bars_from_user"])
        self.assertFalse(spec["year_attested_by_chart"])
        self.assertEqual(spec["current_status"]["real_market_experiments"],"NOT_RUN")
        self.assertEqual(m.preflight()["status"],"M69_LOCAL_SOURCE_READ_NOT_YET_RUN")

if __name__=="__main__":
    unittest.main()
