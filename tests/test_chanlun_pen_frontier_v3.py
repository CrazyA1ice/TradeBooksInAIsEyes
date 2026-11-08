"""V3 conservative pen-frontier policy and provisional -> STRICT segment type fence."""
import copy
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import chanlun_pen_frontier_v3 as v3
import chanlun_incremental_events_v2 as v2
from chanlun_event_lab_v1 import Fractal, Merged, dt

FIX=json.loads((ROOT/"experiments/fixtures/chanlun_pen_frontier_synthetic_v3.json").read_text("utf8"))
OLD={"version_id":"pen_077_exposition","attested_known_at":"2007-09-19T09:00:00+08:00",
     "proof_ref":"synthetic-paper-availability","proof_kind":"synthetic_fixture"}
NEW={"version_id":"pen_081_later_dated_post","attested_known_at":"2007-09-19T09:00:00+08:00",
     "proof_ref":"synthetic-paper-availability","proof_kind":"synthetic_fixture"}
T="2007-09-20T02:00:00+00:00"
CONTEXT={"symbol":"SYNTH","timeframe":"1min","source_revision_sha256":"a"*64,"direction":"UP"}

def run(bars=None,**kwargs):
    return v3.replay_pen_frontier(FIX["bars"] if bars is None else bars,
        data_kind=kwargs.get("data_kind",FIX["kind"]),
        direction=kwargs.get("direction","UP"),
        rule_pin=kwargs.get("rule_pin",OLD),
        stop_at=kwargs.get("stop_at"))

def fake_inputs():
    now=dt(T)
    merged=[Merged(Decimal("1"),Decimal("10"),("k"+str(i),),(i,),now) for i in range(12)]
    return merged,now

def fr(kind,center,extreme,t):
    return Fractal(kind,center,Decimal(str(extreme)),t)

def select(fracs,merged,mode="old",version="pen_077_exposition"):
    return v3.pen_frontier(fracs,merged,mode=mode,rule_version=version,context=CONTEXT)

def pen_objects(x):
    return {k:v for k,v in x["objects"].items()
            if v["object_kind"]=="PROVISIONAL_PEN_FRONTIER"}

class IncrementalPenFrontier(unittest.TestCase):
    def test_baseline_causal_replay(self):
        z=run()
        self.assertTrue(v2.validate_ledger(z))
        self.assertEqual(len(z["prefixes"]),10)
        self.assertFalse(z["complete_pen_parser"])
        self.assertFalse(z["complete_segment_parser"])
        self.assertFalse(z["orders_sent"])
        self.assertEqual(z["scope"],v3.SCOPE)
    def test_original_v2_input_event_hash_referenced(self):
        z=run()
        old=v2.event_history(FIX["bars"],data_kind=FIX["kind"],direction="UP",rule_pin=OLD)
        self.assertEqual(z["source_v2_event_sha256"],v2.digest(old["events"]))
    def test_unfinished_last_bar_never_used(self):
        self.assertEqual(run(FIX["bars"]),run(FIX["bars"][:-1]))
    def test_future_suffix_not_replayed_into_earlier_asof(self):
        x=run(FIX["bars"],stop_at="2007-09-20T01:35:01+00:00")
        y=run(FIX["bars"][:5])
        self.assertEqual(x,y)
    def test_past_prefix_events_immutable_when_more_bars_arrive(self):
        full=run()["events"]
        past=run(FIX["bars"][:5])["events"]
        self.assertEqual(full[:len(past)],past)
    def test_no_pin_means_no_pen_frontier(self):
        x=run(rule_pin=None)
        self.assertEqual(x["events"],[])
        self.assertFalse(any(p["provisional_pen_count"] for p in x["prefixes"]))
    def test_forged_undated_pen_rule_blocked(self):
        pin=dict(OLD,version_id="pen_062_appended_candidate")
        self.assertEqual(run(rule_pin=pin)["events"],[])
    def test_later_attestation_never_preapplies(self):
        pin=dict(OLD,attested_known_at="2007-09-20T01:39:00+00:00")
        x=run(rule_pin=pin)
        self.assertEqual([p["provisional_pen_count"] for p in x["prefixes"][:8]],[0]*8)
    def test_new_version_distinct_from_old_identity(self):
        a=run(rule_pin=OLD)
        b=run(rule_pin=NEW)
        ids_a={e["object_id"] for e in a["events"] if e["object_kind"]=="PROVISIONAL_PEN_FRONTIER"}
        ids_b={e["object_id"] for e in b["events"] if e["object_kind"]=="PROVISIONAL_PEN_FRONTIER"}
        self.assertTrue(ids_a and ids_b)
        self.assertTrue(ids_a.isdisjoint(ids_b))
        self.assertEqual([p["visible_prefix_digest_sha256"] for p in a["prefixes"]],
                         [p["visible_prefix_digest_sha256"] for p in b["prefixes"]])
    def test_invalid_real_dataset_rejected(self):
        with self.assertRaisesRegex(ValueError,"synthetic"):
            run(data_kind="real_market")
    def test_mixed_source_rejected(self):
        b=copy.deepcopy(FIX["bars"]);b[2]["source_revision_sha256"]="b"*64
        with self.assertRaisesRegex(ValueError,"Mixed"):
            run(b)
    def test_gap_and_duplicate_key_fail_closed(self):
        b=copy.deepcopy(FIX["bars"]);b.pop(2)
        with self.assertRaisesRegex(ValueError,"Gap"):
            run(b)
        b=copy.deepcopy(FIX["bars"]);b[1]["key"]=b[0]["key"]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            run(b)
    def test_incomplete_first_prefix_empty(self):
        x=run(stop_at="2007-09-20T01:30:00+00:00")
        self.assertEqual(x["prefixes"],[])
        self.assertEqual(x["events"],[])
    def test_event_hash_tamper_detected(self):
        z=run()
        self.assertTrue(z["events"])
        z["events"][0]["action"]="RETRACT"
        with self.assertRaisesRegex(ValueError,"digest"):
            v2.validate_ledger(z)
    def test_zero_actual_complete_pen_claims(self):
        z=run()
        for item in z["active_objects"]:
            self.assertFalse(item["payload"].get("complete_pen",True))
        self.assertFalse(z["segment_inputs_certified"])

class SelectionPolicy(unittest.TestCase):
    def test_opposite_valid_pair_eligible_only(self):
        merged,t=fake_inputs()
        x=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged)
        p=pen_objects(x)
        self.assertEqual(len(p),1)
        q=next(iter(p.values()))
        self.assertEqual(q["status"],"LOCAL_READY_NECESSARY_ONLY")
        self.assertFalse(q["complete_pen"])
        self.assertEqual(q["feature_projection"]["role"],"UNDETERMINED")
    def test_adjacent_opposite_rejected_then_later_eligible(self):
        merged,t=fake_inputs()
        x=select([fr("TOP",1,12,t),fr("BOTTOM",3,5,t),fr("BOTTOM",6,4,t)],merged)
        self.assertEqual(len(pen_objects(x)),1)
        self.assertIn("OPPOSITE_LOCAL_GATE_NOT_PASSED",[d["decision"] for d in x["decisions"]])
    def test_stronger_same_kind_endpoint_retracts_prior_selection(self):
        merged,t=fake_inputs()
        prev=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged)
        later=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t),fr("BOTTOM",9,4,t)],merged)
        a=pen_objects(prev);b=pen_objects(later)
        self.assertEqual(len(a),1)
        self.assertEqual(len(b),1)
        self.assertTrue(set(a).isdisjoint(b))
        self.assertEqual(next(iter(b.values()))["right_extreme"],"4")
        self.assertIn("TERMINAL_EXTREME_REPLACED_RECHECKED",[d["decision"] for d in later["decisions"]])
    def test_less_extreme_same_kind_does_not_change_endpoint(self):
        merged,t=fake_inputs()
        initial=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged)
        x=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t),fr("BOTTOM",9,6,t)],merged)
        self.assertEqual(pen_objects(initial),pen_objects(x))
    def test_same_kind_tie_blocks_continuation(self):
        merged,t=fake_inputs()
        x=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t),fr("BOTTOM",9,5,t),
                  fr("TOP",11,13,t)],merged)
        self.assertTrue(x["blocked_tie"])
        self.assertEqual(sum(y["object_kind"]=="PEN_FRONTIER_CONFLICT"
                             for y in x["objects"].values()),1)
        self.assertEqual(len(pen_objects(x)),1)
    def test_same_kind_tie_at_start_never_forced(self):
        merged,t=fake_inputs()
        x=select([fr("TOP",1,12,t),fr("TOP",5,12,t)],merged)
        self.assertTrue(x["blocked_tie"])
        self.assertEqual(len(pen_objects(x)),0)
    def test_revised_requires_unambiguous_raw_center(self):
        merged,t=fake_inputs()
        merged[1]=Merged(Decimal("1"),Decimal("10"),("k1","k1b"),(1,2),t)
        x=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged,
                 mode="revised",version="pen_081_later_dated_post")
        self.assertEqual(pen_objects(x),{})
        self.assertIn("OPPOSITE_LOCAL_GATE_NOT_PASSED",[d["decision"] for d in x["decisions"]])
    def test_wrong_price_order_no_candidate(self):
        merged,t=fake_inputs()
        x=select([fr("TOP",1,5,t),fr("BOTTOM",5,6,t)],merged)
        self.assertEqual(len(pen_objects(x)),0)
    def test_explicit_version_required(self):
        merged,t=fake_inputs()
        with self.assertRaisesRegex(ValueError,"Version"):
            select([fr("TOP",1,12,t)],merged,version="")
    def test_raw_center_identity_is_stable_for_same_support(self):
        merged,t=fake_inputs()
        f=fr("TOP",1,12,t)
        ident=v3.fractal_identity(f,merged,CONTEXT)
        updated=list(merged)
        updated[2]=Merged(Decimal(1),Decimal(11),("k2","k2b"),(2,3),t)
        self.assertEqual(v3.fractal_identity(f,updated,CONTEXT),ident)

class StrictFeatureFence(unittest.TestCase):
    def test_provisional_to_strict_is_denied(self):
        merged,t=fake_inputs()
        x=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged)
        projected=v3.provisional_feature_audit(list(pen_objects(x).values()))
        self.assertEqual(projected["role"],"UNDETERMINED")
        self.assertFalse(projected["admitted_as_STRICT_segment_features"])
        self.assertEqual(projected["features"][0]["role"],"UNDETERMINED")
    def test_identity_not_sufficient_to_certify(self):
        merged,t=fake_inputs()
        x=next(iter(pen_objects(select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged)).values()))
        forged=copy.deepcopy(x)
        forged["feature_projection"]["role"]="STRICT"
        with self.assertRaisesRegex(ValueError,"unconfirmed"):
            v3.provisional_feature_audit([forged])
    def test_completed_pen_forgery_denied(self):
        merged,t=fake_inputs()
        x=next(iter(pen_objects(select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged)).values()))
        forged=copy.deepcopy(x)
        forged["complete_pen"]=True
        with self.assertRaisesRegex(ValueError,"unconfirmed"):
            v3.provisional_feature_audit([forged])
    def test_provisional_not_admitted_by_v2_strict_gate(self):
        merged,t=fake_inputs()
        x=select([fr("TOP",1,12,t),fr("BOTTOM",5,5,t)],merged)
        p=v3.provisional_feature_audit(list(pen_objects(x).values()))["features"][0]
        a={"key":"fx1","sequence_id":"left","role":p["role"],"index":1,
           "low":p["low"],"high":p["high"],"completed_at":p["evidence_known_at"]}
        b=dict(a,key="fx2",index=2)
        self.assertEqual(v2.feature_containment(a,b),"BLOCKED_NON_STRICT_MEMBERSHIP")
    def test_segment_projection_empty_without_provisional_pen(self):
        self.assertEqual(v3.provisional_feature_audit([])["count"],0)
    def test_cannot_derive_real_segment_from_v3_data(self):
        x=run()
        self.assertFalse(x["segment_inputs_certified"])
        self.assertFalse(x["complete_segment_parser"])

if __name__=="__main__":
    unittest.main()
