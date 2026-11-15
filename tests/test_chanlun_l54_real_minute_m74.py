"""M74 minute figure replay: synthetic rows only; never make a real-data claim."""
from __future__ import annotations

import csv
import hashlib
import io
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

from tools import admit_chanlun_l54_local_qmt_m69 as m69
from tools import probe_chanlun_l54_external_minute_m72 as m72
from tools import replay_chanlun_l54_real_minute_m74 as m


def fake_full_day():
    # 240 real-session timestamps, but all synthetic prices and volumes.
    clocks = m69.expected_minutes(m.DAY, "bar_end")
    assert len(clocks) == 240
    rows = []
    for t in clocks:
        tm = t.strftime("%H:%M")
        lo = "18.04" if tm >= "13:21" else "18.00"
        rows.append({"time":t,"open":"18.20","high":"18.30",
                     "low":lo,"close":"18.20","volume":"1000",
                     "amount":"123456"})
    def row(tm):
        return next(x for x in rows if x["time"].strftime("%H:%M") == tm)
    row("10:05")["low"] = "17.61"
    row("13:07")["high"] = "18.59"
    row("13:30")["high"] = "18.45"
    row("15:00")["low"] = "18.03"
    last10 = ["18.05","18.05","18.05","18.06","18.06",
              "18.05","18.05","18.06","18.06","18.03"]
    volumes10 = [1432,1432,1432,1432,1430,
                 1477,1477,1477,1478,1917]
    for r, c, v in zip(rows[-10:],last10,volumes10):
        r["close"],r["volume"] = c,str(v)
    return rows


class ReplayTests(unittest.TestCase):
    def test_pinned_provenance_and_default_no_query(self):
        self.assertEqual(m.DAY,"2007-05-18")
        self.assertEqual(m.FILE_BYTES,2897499)
        self.assertEqual(len(m.FILE_SHA256),64)
        with mock.patch.object(m,"fetch_pinned",side_effect=AssertionError("network called")):
            self.assertEqual(m.main(["--mode","preflight"]),0)

    def test_verified_target_requires_exact_size_and_sha(self):
        with self.assertRaisesRegex(ValueError,"size"):
            m.exact_source(b"x")
        with mock.patch.object(m,"FILE_BYTES",4):
            with self.assertRaisesRegex(ValueError,"SHA256"):
                m.exact_source(b"test")

    def test_240_bar_admission_and_reference_fingerprint(self):
        rows=fake_full_day()
        report=m.summarize(rows)
        self.assertEqual(report["grid_status"],"FULL_240_DECLARED_GRID_ONLY")
        self.assertEqual(report["minute_rows"],240)
        self.assertEqual(report["unique_minutes"],240)
        self.assertTrue(report["all_reference_fields_match"])
        self.assertEqual(report["fingerprint"]["day_high_times"],["13:07"])
        self.assertEqual(report["fingerprint"]["volume_ma5"],"1565.2")
        self.assertEqual(report["fingerprint"]["volume_ma10"],"1498.4")
        self.assertEqual(report["fingerprint"]["close_ma10"],"18.052")
        self.assertFalse(report["original_file_bytes_verified"])
        self.assertTrue(all(x["market_minute"] is None for x in report["author_markers"].values()))
        self.assertEqual(len(report["author_markers"]),14)
        self.assertEqual(report["author_alpha"]["g7_structure"],"AUTHOR_THIRD_SELL")
        self.assertEqual(report["author_beta"]["g7_structure"],"AUTHOR_CENTER_OSCILLATION_NOT_THIRD_SELL")
        self.assertEqual(report["F01"],"OPEN")
        self.assertEqual(report["Phi20"],"OPEN")
        self.assertEqual(report["E1_E4"],"NOT_RUN")

    def test_one_price_mutation_breaks_reference_match_but_is_not_gd_proof(self):
        rows=fake_full_day()
        rows[-1]["close"]="18.04"
        report=m.summarize(rows)
        self.assertFalse(report["all_reference_fields_match"])
        self.assertFalse(report["reference_exact_match"]["last_close"])
        self.assertEqual(report["author_markers"]["g7"]["market_minute"],None)

    def test_reject_missing_or_duplicate_minutes_and_wrong_convention(self):
        rows=fake_full_day()
        with self.assertRaises(ValueError):
            m.summarize(rows[:-1])
        rows=fake_full_day()
        rows[1]["time"]=rows[0]["time"]
        with self.assertRaises(ValueError):
            m.summarize(rows)
        with self.assertRaisesRegex(ValueError,"bar_end"):
            m.summarize(fake_full_day(),"bar_start")

    def test_real_file_pipeline_can_be_exercised_with_synthetic_sha_override(self):
        rows=fake_full_day()
        # M73 receives the observed *original* Chinese vendor CSV, not the
        # later M72 canonical adapter CSV (whose "time" header has no date alias).
        sink=io.StringIO(newline="")
        writer=csv.writer(sink,lineterminator="\n")
        writer.writerow(("日期","时间","开盘","最高","最低","收盘","成交量","成交额"))
        for z in rows:
            writer.writerow((z["time"].strftime("%Y-%m-%d"),
                             z["time"].strftime("%H:%M"),
                             z["open"],z["high"],z["low"],z["close"],
                             z["volume"],z["amount"]))
        raw=sink.getvalue().encode("utf-8")
        with mock.patch.object(m,"FILE_BYTES",len(raw)), mock.patch.object(
                m,"FILE_SHA256",hashlib.sha256(raw).hexdigest()):
            parsed, report=m.from_verified_source(raw)
        self.assertEqual(len(parsed),240)
        self.assertTrue(report["original_file_bytes_verified"])
        self.assertEqual(report["annual_csv_rows"],240)
        self.assertEqual(report["fingerprint"]["day_high_times"],["13:07"])

    def test_svg_is_static_chart_with_three_panels_and_no_author_gd_points(self):
        rows=fake_full_day()
        report=m.summarize(rows)
        for window in ("afternoon","full"):
            svg=m.svg_figure(rows,report,window)
            self.assertIn("<svg ",svg)
            self.assertIn("2007-05-18",svg)
            self.assertIn("VOLUME",svg)
            self.assertIn("MACD",svg)
            self.assertIn("13:07 / 18.59",svg)
            self.assertIn("15:00 / 18.03",svg)
            self.assertNotIn('id="g7"',svg)

    def test_macd_is_session_seeded_and_not_assumed_vendor_identical(self):
        prices=[Decimal("18.20")]*30
        self.assertTrue(all(abs(z)<1e-12 for row in m.macd_session(prices) for z in row))
        self.assertEqual(m.summarize(fake_full_day())["macd_initialization"],
                         "SESSION_FIRST_CLOSE_ONLY_NOT_VENDOR_CROSS_DAY_MATCH")

    def test_opt_in_svg_destination_must_be_outside_repo_and_not_overwrite(self):
        with self.assertRaisesRegex(ValueError,"Git repository"):
            m.safe_svg_destination(str(m.ROOT/"output.svg"))
        with self.assertRaisesRegex(ValueError,".svg"):
            m.safe_svg_destination(str(m.ROOT.parent/"some-report.txt"))
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/"chart.svg"
            self.assertEqual(m.safe_svg_destination(str(output)),output.resolve())
            output.write_text("existing")
            with self.assertRaisesRegex(ValueError,"overwriting"):
                m.safe_svg_destination(str(output))

    def test_no_network_chart_request_is_invalid(self):
        with self.assertRaisesRegex(ValueError,"preflight"):
            m.main(["--mode","preflight","--svg-output",str(m.ROOT.parent/"chart.svg")])

    def test_http_redirect_cannot_leak_to_unknown_host(self):
        class FakeResponse:
            status=200
            def __init__(self, url):
                self.url=url
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def geturl(self): return self.url
            def read(self, _): return b"fake"
        with self.assertRaisesRegex(ValueError,"redirect"):
            m.fetch_pinned(opener=lambda req,timeout:FakeResponse("https://example.org/file"))
        self.assertEqual(m.fetch_pinned(opener=lambda req,timeout:FakeResponse(m.FILE_URL)),b"fake")


    def test_documented_hf_cdn_hosts_and_negative_domain_boundaries(self):
        # Hugging Face's published HTTPS download allowlist includes US/EU
        # LFS, nested CDN edges, and Xet (not only cas-bridge.xethub.hf.co).
        good = (
            "https://huggingface.co/datasets/owner/repo/resolve/main/file",
            "https://cdn-lfs-us-1.hf.co/obj",
            "https://cdn-lfs-eu-1.hf.co/obj",
            "https://us.aws.cdn.hf.co/obj",
            "https://us.gcp.cdn.hf.co/obj",
            "https://transfer.xethub-eu.hf.co/obj",
            "https://cas-server.xethub-eu.hf.co/obj",
            "https://cas-bridge.xethub.hf.co/obj",
        )
        for url in good:
            with self.subTest(url=url):
                self.assertTrue(m.trusted_hf_download_url(url))
        bad = (
            "http://cdn-lfs-us-1.hf.co/obj",
            "https://cdn-lfs-us-1.hf.co:444/obj",
            "https://cdn-lfs-us-1.hf.co.evil.example/obj",
            "https://evil.example/hf.co/obj",
            "https://evil-hf.co/obj",
            "https://user:secret@cdn-lfs-us-1.hf.co/obj",
            "https://cdn-lfs-us-1.hf.co:invalid/obj",
        )
        for url in bad:
            with self.subTest(url=url):
                self.assertFalse(m.trusted_hf_download_url(url))

    def test_cdn_response_read_does_not_skip_pinned_hash_or_length(self):
        class FakeResponse:
            status=200
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def geturl(self): return "https://cdn-lfs-us-1.hf.co/a"
            def read(self, n):
                self.read_cap=n
                return b"not-the-pinned-object"
        f=FakeResponse()
        raw=m.fetch_pinned(opener=lambda req,timeout:f)
        self.assertEqual(raw,b"not-the-pinned-object")
        self.assertEqual(f.read_cap,m.FILE_BYTES+1)
        with self.assertRaisesRegex(ValueError,"size"):
            m.exact_source(raw)


if __name__ == "__main__":
    unittest.main()
