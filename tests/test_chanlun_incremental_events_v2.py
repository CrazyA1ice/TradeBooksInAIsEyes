"""Incremental event chains and typed segment-feature necessary conditions: synthetic only."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import chanlun_incremental_events_v2 as lab
BASE=json.loads((ROOT/"experiments/fixtures/chanlun_prefix_synthetic_v1.json").read_text("utf8"))
PIN_OLD={"version_id":"pen_077_exposition","attested_known_at":"2007-09-19T09:00:00+08:00",
         "proof_ref":"synthetic-paper-availability","proof_kind":"synthetic_fixture"}
PIN_NEW={"version_id":"pen_081_later_dated_post","attested_known_at":"2007-09-19T09:00:00+08:00",
         "proof_ref":"synthetic-paper-availability","proof_kind":"synthetic_fixture"}
T="2007-09-20T02:00:00+00:00"

def history(bars=None,**opts):
    return lab.event_history(BASE["bars"] if bars is None else bars,
                             data_kind=opts.get("data_kind",BASE["kind"]),
                             direction=opts.get("direction","UP"),
                             rule_pin=opts.get("rule_pin",PIN_OLD),
                             stop_at=opts.get("stop_at"))

def feature(k,seq,role,i,low,high,time):
    return {"key":k,"sequence_id":seq,"role":role,"index":i,
            "low":str(low),"high":str(high),"completed_at":time}
MAIN_GAP=[
    feature("a1","segment-old","STRICT",1,0,1,"2007-09-20T01:30:00+00:00"),
    feature("a2","segment-old","STRICT",2,2,4,"2007-09-20T01:31:00+00:00"),
    feature("a3","segment-old","STRICT",3,1,3,"2007-09-20T01:32:00+00:00")]
OPPOSITE=[
    feature("b1","segment-new","STRICT",4,8,10,"2007-09-20T01:33:00+00:00"),
    feature("b2","segment-new","STRICT",5,6,8,"2007-09-20T01:34:00+00:00"),
    feature("b3","segment-new","STRICT",6,7,9,"2007-09-20T01:35:00+00:00")]

class ImmutableCausalEvents(unittest.TestCase):
    def test_fixture_builds_and_validates(self):
        z=history()
        self.assertTrue(lab.validate_ledger(z))
        self.assertEqual(len(z["prefixes"]),10)
        self.assertTrue(z["events"])
        self.assertFalse(z["orders_sent"])
        self.assertFalse(z["full_pen_parser"])
        self.assertFalse(z["full_segment_parser"])
    def test_no_real_market_contract(self):
        with self.assertRaisesRegex(ValueError,"synthetic"):
            history(data_kind="market")
    def test_source_key_gap_fails_closed(self):
        x=copy.deepcopy(BASE["bars"]);x.pop(4)
        with self.assertRaisesRegex(ValueError,"Gap"):
            history(x)
    def test_source_sha_change_fails_closed(self):
        x=copy.deepcopy(BASE["bars"]);x[3]["source_revision_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"Mixed"):
            history(x)
    def test_future_unfinished_suffix_is_ignored(self):
        a=history(BASE["bars"])
        b=history(BASE["bars"][:-1])
        self.assertEqual(a,b)
    def test_unseen_future_suffix_not_in_prior_prefix_history(self):
        x=BASE["bars"]
        past=history(x[:5])
        full=history(x,stop_at="2007-09-20T01:35:01+00:00")
        self.assertEqual(past["events"],full["events"])
        self.assertEqual(past["prefixes"],full["prefixes"])
        self.assertEqual(past["active_objects"],full["active_objects"])
    def test_future_stop_before_first_bar_has_no_history(self):
        z=history(stop_at="2007-09-20T01:30:00+00:00")
        self.assertEqual(z["events"],[])
        self.assertEqual(z["prefixes"],[])
    def test_first_fractal_emits_at_third_completion_not_at_center(self):
        z=history(BASE["bars"][:3],rule_pin=None)
        f=[e for e in z["events"] if e["object_kind"]=="FRACTAL_CANDIDATE"]
        self.assertEqual(len(f),1)
        self.assertEqual(f[0]["action"],"OPEN")
        self.assertEqual(f[0]["observed_at"],"2007-09-20T01:33:01+00:00")
        self.assertEqual(f[0]["payload"]["extremum_known_at"],"2007-09-20T01:32:01+00:00")
        self.assertLess(f[0]["payload"]["extremum_known_at"],f[0]["observed_at"])
    def test_merged_right_witness_emits_revision_and_keeps_history(self):
        x=copy.deepcopy(BASE["bars"][:4])
        x[3].update(low="4",high="6",open="5",close="5")
        z=history(x,rule_pin=None)
        f=[e for e in z["events"] if e["object_kind"]=="FRACTAL_CANDIDATE"]
        self.assertEqual([e["action"] for e in f],["OPEN","REVISE"])
        self.assertEqual(f[0]["object_id"],f[1]["object_id"])
        self.assertEqual(f[1]["revision"],2)
        self.assertEqual(f[1]["supersedes_event_id"],f[0]["event_id"])
        self.assertNotEqual(f[0]["payload"],f[1]["payload"])
        self.assertEqual(f[0]["payload"]["witness_raw_keys"][-1],[x[2]["key"]])
        self.assertEqual(f[1]["payload"]["witness_raw_keys"][-1],[x[2]["key"],x[3]["key"]])
    def test_a_new_high_retracts_but_does_not_rewrite_past(self):
        x=copy.deepcopy(BASE["bars"][:4])
        x[3].update(low="3",high="8",open="4",close="6")
        z=history(x,rule_pin=None)
        f=[e for e in z["events"] if e["object_kind"]=="FRACTAL_CANDIDATE"]
        self.assertEqual([e["action"] for e in f],["OPEN","RETRACT"])
        self.assertEqual(f[1]["reason"],"NO_LONGER_PRESENT_IN_OBSERVED_PREFIX")
        self.assertEqual(z["active_objects"],[])
        self.assertEqual(f[0]["payload"]["status"],"PREFIX_LOCAL_REVISABLE")
    def test_retracted_candidate_can_reopen_on_later_validated_prefix(self):
        # Unit-test the immutable version chain for a reappearance of the same
        # identity, without claiming any particular synthetic OHLC does so.
        events=[]; last={};asof=lab.dt("2007-09-20T01:40:00+00:00")
        payload={"object_kind":"FRACTAL_CANDIDATE","evidence_known_at":"2007-09-20T01:33:01+00:00"}
        for act in ("OPEN","RETRACT","REOPEN"):
            lab._append(events,last,"F-A",act,payload,asof,"a"*64)
        z={"events":events,"active_objects":[{"id":"F-A","payload":payload}]}
        self.assertTrue(lab.validate_ledger(z))
        self.assertEqual([x["revision"] for x in events],[1,2,3])
    def test_ledger_hash_tampering_rejected(self):
        z=history(BASE["bars"][:3],rule_pin=None)
        z["events"][0]["observed_at"]="2007-09-20T01:31:01+00:00"
        with self.assertRaisesRegex(ValueError,"digest"):
            lab.validate_ledger(z)
    def test_bad_supersedes_chain_rejected_even_if_rehashed(self):
        x=copy.deepcopy(BASE["bars"][:4]);x[3].update(low="4",high="6",open="5",close="5")
        z=history(x,rule_pin=None)
        target=z["events"][1]
        target["supersedes_event_id"]="EV-not-a-real-prior-event"
        target["event_id"]="EV-"+lab.digest({k:v for k,v in target.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"chain"):
            lab.validate_ledger(z)
    def test_append_only_event_no_non_substantive_revision(self):
        events=[];last={};t=lab.dt(T)
        payload={"object_kind":"FRACTAL_CANDIDATE","evidence_known_at":t.isoformat()}
        lab._append(events,last,"F-X","OPEN",payload,t,"a"*64)
        lab._append(events,last,"F-X","REVISE",payload,t,"a"*64)
        with self.assertRaisesRegex(ValueError,"Non-substantive"):
            lab.validate_ledger({"events":events,"active_objects":[{"id":"F-X","payload":payload}]})
    def test_old_and_new_pens_have_distinct_rule_identity(self):
        a=history(rule_pin=PIN_OLD)
        b=history(rule_pin=PIN_NEW)
        pen_a={e["object_id"] for e in a["events"] if e["object_kind"]=="PEN_NECESSARY_GATE"}
        pen_b={e["object_id"] for e in b["events"] if e["object_kind"]=="PEN_NECESSARY_GATE"}
        self.assertTrue(pen_a and pen_b)
        self.assertTrue(pen_a.isdisjoint(pen_b))
        self.assertEqual([p["visible_prefix_digest_sha256"] for p in a["prefixes"]],
                         [p["visible_prefix_digest_sha256"] for p in b["prefixes"]])
    def test_undated_rule_does_not_make_pen_events(self):
        pin=dict(PIN_OLD,version_id="pen_062_appended_candidate")
        z=history(rule_pin=pin)
        self.assertFalse(any(e["object_kind"]=="PEN_NECESSARY_GATE" for e in z["events"]))
    def test_no_pin_makes_fractal_events_but_not_pen_events(self):
        z=history(rule_pin=None)
        self.assertTrue(any(e["object_kind"]=="FRACTAL_CANDIDATE" for e in z["events"]))
        self.assertFalse(any(e["object_kind"]=="PEN_NECESSARY_GATE" for e in z["events"]))
    def test_negative_evidence_time_refused_by_validator(self):
        events=[];last={};clock=lab.dt("2007-09-20T01:40:00+00:00")
        payload={"object_kind":"FRACTAL_CANDIDATE","evidence_known_at":"2007-09-20T01:45:00+00:00"}
        lab._append(events,last,"F-1","OPEN",payload,clock,"a"*64)
        with self.assertRaisesRegex(ValueError,"future"):
            lab.validate_ledger({"events":events,"active_objects":[{"id":"F-1","payload":payload}]})

class StrictFeatureGate(unittest.TestCase):
    def gate(self,rows=None,**kw):
        return lab.feature_three_gate(MAIN_GAP if rows is None else rows,
                                      expected=kw.get("expected","TOP"),asof=kw.get("asof",T),
                                      opposite_three=kw.get("opposite",None))
    def test_requires_three_strict_complete_features(self):
        with self.assertRaisesRegex(ValueError,"three"):
            self.gate(MAIN_GAP[:2])
    def test_main_strict_sequence_not_auxiliary(self):
        x=copy.deepcopy(MAIN_GAP);x[2]["role"]="AUXILIARY"
        self.assertEqual(self.gate(x)["status"],"BLOCKED_NON_STRICT_MEMBERSHIP")
    def test_main_cross_sequence_rejected(self):
        x=copy.deepcopy(MAIN_GAP);x[1]["sequence_id"]="other"
        with self.assertRaisesRegex(ValueError,"Mixed"):
            self.gate(x)
    def test_main_incomplete_third_pending(self):
        self.assertEqual(self.gate(asof="2007-09-20T01:31:30+00:00")["status"],
                         "PENDING_THIRD_COMPLETED_FEATURE")
    def test_gap_without_opposite_remains_pending(self):
        z=self.gate()
        self.assertEqual(z["status"],"PENDING_OPPOSITE_THREE_FEATURES")
        self.assertIsNone(z["confirmed_at"])
        self.assertEqual(z["candidate_extremum_key"],"a2")
        self.assertFalse(z["orders_sent"])
    def test_valid_opposite_three_conditional_confirmation(self):
        z=self.gate(opposite=OPPOSITE)
        self.assertEqual(z["status"],"LOCAL_GAP_CONDITION_PASSED_NECESSARY_ONLY")
        self.assertEqual(z["confirmed_at"],"2007-09-20T01:35:00+00:00")
        self.assertEqual(z["candidate_extremum_completed_at"],"2007-09-20T01:31:00+00:00")
        self.assertNotEqual(z["confirmed_at"],z["candidate_extremum_completed_at"])
        self.assertFalse(z["full_segment_parser"])
    def test_future_opposite_proof_not_used(self):
        z=self.gate(asof="2007-09-20T01:34:30+00:00",opposite=OPPOSITE)
        self.assertEqual(z["status"],"PENDING_OPPOSITE_THREE_FEATURES")
    def test_wrong_opposite_fractal_does_not_confirm(self):
        bad=copy.deepcopy(OPPOSITE);bad[1].update(low="9",high="11")
        self.assertEqual(self.gate(opposite=bad)["status"],"PENDING_OPPOSITE_THREE_FEATURES")
    def test_same_sequence_is_not_valid_opposite(self):
        bad=copy.deepcopy(OPPOSITE)
        for x in bad:x["sequence_id"]="segment-old"
        with self.assertRaisesRegex(ValueError,"distinct"):
            self.gate(opposite=bad)
    def test_earlier_opposite_proof_is_not_valid(self):
        bad=copy.deepcopy(OPPOSITE)
        for i,x in enumerate(bad):x["completed_at"]=f"2007-09-20T01:2{6+i}:00+00:00"
        with self.assertRaisesRegex(ValueError,"later"):
            self.gate(opposite=bad)
    def test_opposite_auxiliary_not_allowed(self):
        bad=copy.deepcopy(OPPOSITE);bad[2]["role"]="AUXILIARY"
        with self.assertRaisesRegex(ValueError,"auxiliary"):
            self.gate(opposite=bad)
    def test_overlap_no_gap_passed_only_locally(self):
        m=copy.deepcopy(MAIN_GAP);m[0].update(high="3")
        z=self.gate(m)
        self.assertEqual(z["status"],"LOCAL_NO_GAP_CONDITION_PASSED_NECESSARY_ONLY")
        self.assertEqual(z["confirmed_at"],"2007-09-20T01:32:00+00:00")
        self.assertFalse(z["full_segment_parser"])
    def test_equal_extreme_is_not_fractal(self):
        m=copy.deepcopy(MAIN_GAP);m[2]["high"]="4"
        self.assertEqual(self.gate(m)["status"],"NOT_EXPECTED_STRICT_FRACTAL")
    def test_containment_requires_same_strict_sequence(self):
        a=feature("c1","s","STRICT",0,1,8,"2007-09-20T01:30:00+00:00")
        b=feature("c2","s","STRICT",1,2,7,"2007-09-20T01:31:00+00:00")
        self.assertEqual(lab.feature_containment(a,b),"LOCAL_CONTAINMENT_ELIGIBLE")
        b["role"]="UNDETERMINED"
        self.assertEqual(lab.feature_containment(a,b),"BLOCKED_NON_STRICT_MEMBERSHIP")
        b["role"]="STRICT";b["sequence_id"]="other"
        self.assertEqual(lab.feature_containment(a,b),"BLOCKED_CROSS_SEQUENCE")
    def test_float_price_or_naive_time_rejected(self):
        x=copy.deepcopy(MAIN_GAP);x[0]["low"]=0.0
        with self.assertRaisesRegex(ValueError,"float"):
            self.gate(x)
        x=copy.deepcopy(MAIN_GAP);x[0]["completed_at"]="2007-09-20T01:30:00"
        with self.assertRaisesRegex(ValueError,"Naive"):
            self.gate(x)
    def test_duplicate_key_or_bad_index_fails(self):
        x=copy.deepcopy(MAIN_GAP);x[1]["key"]=x[0]["key"]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            self.gate(x)
        x=copy.deepcopy(MAIN_GAP);x[2]["index"]=x[1]["index"]
        with self.assertRaisesRegex(ValueError,"order"):
            self.gate(x)

if __name__=="__main__":
    unittest.main()
