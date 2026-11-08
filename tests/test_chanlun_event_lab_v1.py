import copy
import importlib.util
import json
import unittest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("chanlun_event_lab_v1",ROOT/"tools/chanlun_event_lab_v1.py")
lab=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=lab
spec.loader.exec_module(lab)
FIX=json.loads((ROOT/"experiments/fixtures/chanlun_prefix_synthetic_v1.json").read_text("utf8"))
REG=json.loads((ROOT/"catalog/chanlun_rule_history_v1.json").read_text("utf8"))
T="2007-09-20T02:00:00+00:00"
OLD={"version_id":"pen_077_exposition","attested_known_at":"2007-09-19T09:00:00+08:00",
     "proof_ref":"synthetic-paper-availability","proof_kind":"synthetic_fixture"}
NEW={"version_id":"pen_081_later_dated_post","attested_known_at":"2007-09-19T09:00:00+08:00",
     "proof_ref":"synthetic-paper-availability","proof_kind":"synthetic_fixture"}

def replay(bars=None,**kw):
    return lab.replay(FIX["bars"] if bars is None else bars,
                      market_asof=kw.get("market_asof",T),
                      direction=kw.get("direction","UP"),
                      rule_pin=kw.get("rule_pin",OLD),registry=kw.get("registry",REG))

def err_bar(field,value):
    x=copy.deepcopy(FIX["bars"]);x[0][field]=value
    with unittest.TestCase().assertRaises(ValueError):
        replay(x)

class MarketContract(unittest.TestCase):
    def test_fixture_only_marked_synthetic(self):
        self.assertEqual(FIX["kind"],"synthetic_non_market_fixture")
    def test_exact_decimals_and_no_floats(self):
        err_bar("high",7.0)
        err_bar("low","NaN")
        err_bar("volume","Infinity")
    def test_ohlcv_bounds(self):
        err_bar("high","1")
        err_bar("low","10")
        err_bar("volume","-1")
    def test_naive_time_rejected(self):
        err_bar("known_at","2007-09-20T01:31:01")
    def test_closed_before_bar_end_rejected(self):
        err_bar("known_at","2007-09-20T01:30:30+00:00")
    def test_duplicate_bar_keys_rejected(self):
        x=copy.deepcopy(FIX["bars"]);x[1]["key"]=x[0]["key"]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            replay(x)
    def test_gap_rejected(self):
        x=copy.deepcopy(FIX["bars"]);x.pop(3)
        with self.assertRaisesRegex(ValueError,"Gap"):
            replay(x)
    def test_different_source_revision_rejected(self):
        x=copy.deepcopy(FIX["bars"]);x[2]["source_revision_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"Mixed"):
            replay(x)
    def test_nonmonotone_known_at_rejected(self):
        x=copy.deepcopy(FIX["bars"]);x[2]["known_at"]=x[1]["known_at"]
        x[2]["known_at"]="2007-09-20T01:33:00+00:00"
        x[3]["known_at"]="2007-09-20T01:33:00+00:00"
        # Force valid completed timestamp but later record goes backwards.
        x[2]["known_at"]="2007-09-20T01:50:00+00:00"
        with self.assertRaisesRegex(ValueError,"availability"):
            replay(x)
    def test_invalid_direction_rejected(self):
        with self.assertRaisesRegex(ValueError,"Direction"):
            replay(direction="AUTO_FUTURE_BIAS")
    def test_future_suffix_does_not_change_prefix_snapshot(self):
        bars=FIX["bars"]
        known_asof="2007-09-20T01:35:01+00:00"
        a=replay(bars[:6],market_asof=known_asof)
        b=replay(bars,market_asof=known_asof)
        self.assertEqual(a,b)
        self.assertEqual(a["visible_closed_bars"],5)
    def test_known_late_bar_not_visible_early(self):
        x=copy.deepcopy(FIX["bars"])
        x[3]["known_at"]="2007-09-20T01:39:00+00:00"
        for i in range(4,len(x)):
            if x[i]["known_at"]<x[i-1]["known_at"]:
                x[i]["known_at"]="2007-09-20T01:39:00+00:00" if x[i]["is_closed"] else "2007-09-20T01:41:00+00:00"
        self.assertEqual(replay(x,market_asof="2007-09-20T01:38:00+00:00")["visible_closed_bars"],3)
    def test_incomplete_last_bar_never_consumed(self):
        a=replay()
        self.assertEqual(a["visible_closed_bars"],10)
        self.assertFalse(a["complete_pen_parser"])
        self.assertFalse(a["orders_sent"])
        self.assertEqual(a["scope"],lab.RESEARCH_ONLY)
    def test_same_prefix_reproducible_sha(self):
        a=replay();b=replay()
        self.assertEqual(a["visible_prefix_digest_sha256"],b["visible_prefix_digest_sha256"])
        self.assertEqual(len(a["visible_prefix_digest_sha256"]),64)

class NormalizationAndFractal(unittest.TestCase):
    def test_no_containment_exact_3bar_fractal(self):
        bars=[lab.ClosedBar.parse(x) for x in FIX["bars"][:3]]
        norm=lab.normalize(bars,"UP")
        self.assertEqual(len(norm),3)
        f=lab.fractals(norm)
        self.assertEqual(len(f),1)
        self.assertEqual(f[0].kind,"TOP")
        self.assertEqual(f[0].center,1)
        self.assertEqual(f[0].available_at,lab.dt(FIX["bars"][2]["known_at"]))
    def test_no_fractal_before_third_completed(self):
        self.assertEqual(replay(market_asof="2007-09-20T01:32:01+00:00")["fractal_candidates"],[])
    def test_direction_dependent_inclusion_preserves_sources(self):
        def b(lo,hi,seq):
            return lab.Merged(Decimal(str(lo)),Decimal(str(hi)),(str(seq),),(seq,),lab.dt(T))
        a,b1,c=b(0,6,0),b(0,10,1),b(4,10,2)
        self.assertTrue(lab.included(a,b1))
        self.assertTrue(lab.included(b1,c))
        self.assertFalse(lab.included(a,c))
        # Existing local containment function is intentionally nontransitive.
        for direction in ("UP","DOWN"):
            x=lab.normalize([lab.ClosedBar.parse(v) for v in FIX["bars"][:2]],direction)
            self.assertEqual(len(x),2)
        self.assertEqual(len(a.keys+b1.keys+c.keys),3)
    def test_equal_extrema_do_not_force_fractal(self):
        a=lab.Merged(Decimal(1),Decimal(3),("a",),(0,),lab.dt(T))
        b=lab.Merged(Decimal(2),Decimal(4),("b",),(1,),lab.dt(T))
        c=lab.Merged(Decimal(2),Decimal(4),("c",),(2,),lab.dt(T))
        self.assertEqual(lab.fractals([a,b,c]),())
    def test_last_bar_merge_can_revise_prior_local_candidate(self):
        x=copy.deepcopy(FIX["bars"][:3])
        first=lab.fractals(lab.normalize([lab.ClosedBar.parse(p) for p in x],"UP"))
        self.assertEqual(len(first),1)
        fourth=copy.deepcopy(FIX["bars"][3])
        fourth["low"]="3";fourth["high"]="8";fourth["open"]="4";fourth["close"]="6"
        after=lab.fractals(lab.normalize([lab.ClosedBar.parse(p) for p in x+[fourth]],"UP"))
        self.assertEqual(after,())
        self.assertTrue(all(f.kind in ("TOP","BOTTOM") for f in first))
    def test_merged_source_keys_not_lost(self):
        x=copy.deepcopy(FIX["bars"][:2])
        x[1]["low"]="3";x[1]["high"]="6";x[1]["open"]="4";x[1]["close"]="5"
        z=lab.normalize([lab.ClosedBar.parse(v) for v in x],"UP")
        self.assertEqual(len(z),1)
        self.assertEqual(z[0].keys,(x[0]["key"],x[1]["key"]))

class PenVersionGates(unittest.TestCase):
    def test_old_new_both_required_explicitly(self):
        a=replay(rule_pin=OLD)
        b=replay(rule_pin=NEW)
        self.assertEqual(a["rule"]["mode"],"old")
        self.assertEqual(b["rule"]["mode"],"revised")
        self.assertTrue(a["pen_necessary_gates"])
        self.assertFalse(any(x["trade_signal"] for x in a["pen_necessary_gates"]))
    def test_no_rule_no_pen_claim(self):
        a=replay(rule_pin=None)
        self.assertEqual(a["rule"]["state"],"NO_RULE_PIN")
        self.assertEqual(a["pen_necessary_gates"],[])
    def test_later_rule_not_assumed_known_early(self):
        a=replay(market_asof="2007-09-18T13:00:00+00:00",rule_pin=NEW)
        self.assertEqual(a["rule"]["state"],"PENDING_ATTESTED_AVAILABILITY")
        self.assertEqual(a["pen_necessary_gates"],[])
    def test_attestation_cannot_precede_displayed_date(self):
        p=dict(NEW,attested_known_at="2007-09-17T08:00:00+08:00")
        with self.assertRaisesRegex(ValueError,"predates"):
            replay(rule_pin=p)
    def test_undated_appendix_blocked(self):
        p=dict(OLD,version_id="pen_062_appended_candidate")
        a=replay(rule_pin=p)
        self.assertEqual(a["rule"]["state"],"BLOCKED_UNKNOWN_OR_EDITORIAL_PROVENANCE")
        self.assertEqual(a["pen_necessary_gates"],[])
    def test_unknown_rule_id_fails_closed(self):
        p=dict(OLD,version_id="not_in_registry")
        with self.assertRaisesRegex(ValueError,"not in immutable"):
            replay(rule_pin=p)
    def test_synthetic_proof_explicit(self):
        p=dict(OLD,proof_ref="")
        with self.assertRaisesRegex(ValueError,"Rule pin"):
            replay(rule_pin=p)
    def test_old_independent_bar_needed(self):
        a=replay(rule_pin=OLD)
        self.assertTrue(any(x["status"]=="REJECT_NO_INDEPENDENT_MERGED_BAR" for x in a["pen_necessary_gates"]))
    def test_revised_extrema_count_differs_from_merged_distance(self):
        m=[]
        t=lab.dt(T)
        for i,seqs in enumerate([(0,),(1,),(2,3,4),(5,6),(7,),(8,)]):
            m.append(lab.Merged(Decimal("1"),Decimal("9"),tuple("k"+str(x) for x in seqs),
                                tuple(seqs),t))
        # First and second strict 3-bar fractals do not share normalized bars.
        f=[lab.Fractal("TOP",1,Decimal("12"),t),lab.Fractal("BOTTOM",4,Decimal("0.5"),t)]
        self.assertEqual(lab.pair_gates(f,m,"old")[0]["status"],"REJECT_NO_INDEPENDENT_MERGED_BAR")
        self.assertEqual(lab.pair_gates(f,m,"revised")[0]["status"],"LOCAL_ELIGIBLE_NECESSARY_ONLY")
    def test_revised_merged_fractal_center_is_unknown(self):
        t=lab.dt(T)
        m=[lab.Merged(Decimal("1"),Decimal("9"),("k"+str(i),),(i,),t) for i in range(6)]
        m[1]=lab.Merged(Decimal(1),Decimal(9),("k1","k1b"),(1,2),t)
        f=[lab.Fractal("TOP",1,Decimal("12"),t),lab.Fractal("BOTTOM",4,Decimal("0.5"),t)]
        self.assertEqual(lab.pair_gates(f,m,"revised")[0]["status"],"UNKNOWN_RAW_EXTREMUM_PROVENANCE")
    def test_shared_kline_rejected(self):
        t=lab.dt(T)
        m=[lab.Merged(Decimal(1),Decimal(9),("k"+str(i),),(i,),t) for i in range(5)]
        f=[lab.Fractal("TOP",1,Decimal(12),t),lab.Fractal("BOTTOM",3,Decimal(0),t)]
        self.assertEqual(lab.pair_gates(f,m,"old")[0]["status"],"REJECT_SHARED_KLINE")
    def test_same_kind_extreme_tie_pending(self):
        t=lab.dt(T)
        f=[lab.Fractal("TOP",1,Decimal(12),t),lab.Fractal("TOP",4,Decimal(12),t)]
        m=[lab.Merged(Decimal(1),Decimal(9),("k"+str(i),),(i,),t) for i in range(6)]
        self.assertEqual(lab.pair_gates(f,m,"old")[0]["status"],"TIE_PENDING")

if __name__=="__main__":
    unittest.main()
