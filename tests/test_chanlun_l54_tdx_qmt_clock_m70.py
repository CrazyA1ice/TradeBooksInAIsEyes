"""M70: fake native 32B TDX calendar clocks and fake QMT only; no paid files."""
import hashlib
import io
import json
import struct
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tools import probe_chanlun_l54_tdx_qmt_clock_m70 as m

def fake_record(d,minute):
    day=date.fromisoformat(d)
    packed=(day.year-2004)*2048+day.month*100+day.day
    return struct.pack("<HH",packed,minute)+b"\x00"*28

def fake_native(path,record_pairs):
    path=Path(path)
    path.write_bytes(b"".join(fake_record(d,mn) for d,mn in record_pairs))
    return path

def day_sample(d,profile):
    return [(d,minute) for minute in m.GRID[profile]]

class FakeQMT:
    def __init__(self):
        self.calls=[]
    def get_market_data_ex(self,**kwargs):
        self.calls.append(kwargs)
        rows=[
            ("2007-05-18 13:21:00",{
                "open":18.30,"high":18.59,"low":18.03,
                "close":18.40,"volume":5,"amount":100}),
            ("2007-05-18 13:22:00",{
                "open":18.40,"high":18.50,"low":18.10,
                "close":18.20,"volume":6,"amount":120})
        ]
        class Frame:
            def iterrows(self):
                return iter(rows)
        return {m.m69.CODE:Frame()}

class M70NativeClockTests(unittest.TestCase):
    def test_preflight_does_not_read_user_cache(self):
        s=m.preflight()
        self.assertFalse(s["user_local_files_inspected"])
        self.assertEqual(s["market_experiments"],"NOT_RUN")
        self.assertEqual(s["candidate_dates"],["2006-05-18","2007-05-18"])

    def test_packed_date_and_minute_from_native_header(self):
        self.assertEqual(m.decode_key(fake_record("2007-05-18",801)),
                         ("2007-05-18",801))
        self.assertEqual(m.decode_key(fake_record("2006-05-18",570)),
                         ("2006-05-18",570))

    def test_two_calendar_year_candidates_in_same_local_file(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600151.lc1",
              day_sample("2006-05-18","TDX_1MIN_END_240")+
              day_sample("2007-05-18","TDX_1MIN_START_240"))
            result,keys=m.scan_tdx(p)
            self.assertEqual(result["source_total_records"],480)
            self.assertEqual(result["dates"]["2006-05-18"]["rows"],240)
            self.assertEqual(result["dates"]["2007-05-18"]["rows"],240)
            self.assertEqual(result["dates"]["2007-05-18"]["profile"],"TDX_1MIN_START_240")
            self.assertEqual(len(keys["2007-05-18"]),240)
            self.assertEqual(result["source_sha256"],hashlib.sha256(p.read_bytes()).hexdigest())
            self.assertFalse(result["tdx_prices_or_volumes_decoded"])

    def test_date_absence_is_only_local_cache_absence(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600151.lc1",day_sample("2006-05-18","TDX_1MIN_END_240"))
            meta,keys=m.scan_tdx(p)
            self.assertEqual(meta["dates"]["2007-05-18"]["rows"],0)
            self.assertEqual(keys["2007-05-18"],[])
            self.assertEqual(meta["dates"]["2007-05-18"]["status"],"DATE_NOT_IN_LOCAL_FILE")
            self.assertFalse(meta["dates"]["2007-05-18"]["vendor_history_absence_proven"])

    def test_special_241_never_silently_becomes_240(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600151.lc1",
                          day_sample("2007-05-18","TDX_OPENING_PLUS_END_241"))
            meta,keys=m.scan_tdx(p)
            self.assertEqual(meta["dates"]["2007-05-18"]["rows"],241)
            self.assertEqual(meta["dates"]["2007-05-18"]["profile"],"TDX_OPENING_PLUS_END_241")
            self.assertNotEqual(len(keys["2007-05-18"]),240)

    def test_tdx_full_start_profile_same_qmt_intervals(self):
        tdx=list(m.GRID["TDX_1MIN_START_240"])
        out=m.compare(tdx,tdx,"bar_start","bar_start","TDX_1MIN_START_240")
        self.assertEqual(out["status"],"LOCAL_INTERVAL_KEYS_AGREE_ONLY")
        self.assertEqual(out["common_minutes"],240)
        self.assertFalse(out["price_equal_proven"])

    def test_normalize_cross_end_start_conventions(self):
        starts=list(m.GRID["TDX_1MIN_START_240"])
        ends=list(m.GRID["TDX_1MIN_END_240"])
        out=m.compare(ends,starts,"bar_end","bar_start","TDX_1MIN_START_240")
        self.assertEqual(out["status"],"LOCAL_INTERVAL_KEYS_AGREE_ONLY")
        self.assertEqual(out["common_minutes"],240)

    def test_explicit_wrong_tdx_label_is_conflict(self):
        ends=list(m.GRID["TDX_1MIN_END_240"])
        out=m.compare(ends,ends,"bar_end","bar_start","TDX_1MIN_END_240")
        self.assertEqual(out["status"],"TDX_DECLARED_CONVENTION_CONFLICTS_WITH_FULL_GRID")
        self.assertFalse(out["price_equal_proven"])

    def test_partial_tdx_day_differences_are_only_clock_differences(self):
        out=m.compare([801,802],[801],"bar_start","bar_start")
        self.assertEqual(out["status"],"LOCAL_TIME_KEYS_DIFFER")
        self.assertEqual(out["common_minutes"],1)
        self.assertEqual(out["qmt_only_minutes"],1)
        self.assertEqual(out["tdx_only_minutes"],0)

    def test_one_source_missing_is_not_provider_absence(self):
        result=m.compare(None,[801],"bar_start","bar_start")
        self.assertEqual(result["status"],"ONE_LOCAL_SOURCE_MISSING_NOT_COMPARABLE")
        self.assertFalse(result["provider_authenticated"])

    def test_both_missing_days_not_a_market_claim(self):
        result=m.compare([],[],"bar_start","bar_start")
        self.assertEqual(result["status"],"BOTH_LOCAL_SOURCES_MISSING_CANDIDATE_DAY")
        self.assertEqual(result["F01"],"OPEN")

    def test_duplicate_minute_keys_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600151.lc1",
                          [("2007-05-18",801),("2007-05-18",801)])
            with self.assertRaisesRegex(ValueError,"not increasing"):
                m.scan_tdx(p)

    def test_reversed_minute_keys_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600151.lc1",
                          [("2007-05-18",802),("2007-05-18",801)])
            with self.assertRaises(ValueError):
                m.scan_tdx(p)

    def test_invalid_calendar_encoding_refused(self):
        bad=struct.pack("<HH",0,801)+b"\x00"*28
        with self.assertRaisesRegex(ValueError,"invalid compressed"):
            m.decode_key(bad)

    def test_unaligned_or_empty_file_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"sh600151.lc1"
            p.write_bytes(b"X"*31)
            with self.assertRaisesRegex(ValueError,"aligned"):
                m.scan_tdx(p)
            p.write_bytes(b"")
            with self.assertRaisesRegex(ValueError,"aligned"):
                m.scan_tdx(p)

    def test_wrong_stock_file_name_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600519.lc1",[("2007-05-18",801)])
            with self.assertRaisesRegex(ValueError,"sh600151"):
                m.scan_tdx(p)

    def test_no_raw_time_keys_or_market_prices_in_tdx_report(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600151.lc1",[("2007-05-18",801)])
            meta,_=m.scan_tdx(p)
            dump=json.dumps(meta)
            self.assertNotIn("13:21",dump)
            self.assertNotIn('"open"',dump)
            self.assertNotIn('"high"',dump)
            self.assertFalse(meta["individual_minutes_exported"])

    def test_qmt_fake_snapshot_reuses_m69_one_frozen_query(self):
        fake=FakeQMT()
        package=types.ModuleType("xtquant")
        package.xtdata=fake
        with patch.dict(sys.modules,{"xtquant":package}):
            result,minute_keys=m.get_local_qmt("bar_start")
        self.assertEqual(len(fake.calls),1)
        self.assertEqual(fake.calls[0],m.m69.m57.ARGS)
        self.assertEqual(result["rows"],2)
        self.assertEqual(minute_keys,[801,802])
        self.assertNotIn("open",result)
        self.assertFalse(result["chart_identity_authenticated"])

    def test_missing_file_cli_reports_local_absence_only(self):
        with tempfile.TemporaryDirectory() as temp:
            out=io.StringIO()
            p=Path(temp)/"sh600151.lc1"
            with redirect_stdout(out):
                code=m.main(["--mode","tdx-local","--tdx-file",str(p),
                             "--tdx-convention","bar_start"])
            self.assertEqual(code,0)
            report=json.loads(out.getvalue())
            self.assertEqual(report["tdx"]["status"],
                             "TDX_LOCAL_FILE_MISSING_NOT_PROVIDER_ABSENCE")
            self.assertFalse(report["chart_year_authenticated"])

    def test_cli_dual_fake_sources_only_show_timestamps(self):
        with tempfile.TemporaryDirectory() as temp:
            p=fake_native(Path(temp)/"sh600151.lc1",
                          [("2007-05-18",801),("2007-05-18",802)])
            fake=FakeQMT()
            pkg=types.ModuleType("xtquant")
            pkg.xtdata=fake
            out=io.StringIO()
            with patch.dict(sys.modules,{"xtquant":pkg}),redirect_stdout(out):
                self.assertEqual(m.main(["--mode","dual-local","--tdx-file",str(p),
                          "--tdx-convention","bar_start",
                          "--qmt-convention","bar_start"]),0)
            meta=json.loads(out.getvalue())
            self.assertEqual(meta["comparison"]["status"],"LOCAL_INTERVAL_KEYS_AGREE_ONLY")
            self.assertEqual(meta["comparison"]["common_minutes"],2)
            self.assertFalse(meta["comparison"]["price_equal_proven"])
            self.assertFalse(meta["chart_year_authenticated"])
            self.assertNotIn("13:21",out.getvalue())
            self.assertNotIn("18.59",out.getvalue())

    def test_invalid_or_unknown_conventions_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"conventions"):
            m.compare([801],[801],"auto","bar_start")
        with self.assertRaisesRegex(ValueError,"conventions"):
            m.compare([801],[801],"bar_start","unknown")

if __name__=="__main__":
    unittest.main()
