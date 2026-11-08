"""V4 source-correction known-at and complete-pen proof-obligation audit."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import chanlun_revision_proof_gates_v4 as v4
import chanlun_incremental_events_v2 as v2

FIX=json.loads((ROOT/"experiments/fixtures/chanlun_pen_frontier_synthetic_v3.json").read_text("utf8"))
BARS=FIX["bars"]
T="2007-09-20T02:00:00+00:00"
BEFORE="2007-09-20T01:40:50+00:00"
AFTER="2007-09-20T01:41:01+00:00"
PIN={"version_id":"pen_077_exposition","attested_known_at":"2007-09-19T09:00:00+08:00",
     "proof_ref":"synthetic-paper-availability","proof_kind":"synthetic_fixture"}

def edit(row,**updates):
    price={k:row[k] for k in v4.BAR_PRICES}
    price.update(updates)
    return price

def make_one():
    return v4.make_synthetic_correction(1,BARS[5],"2007-09-20T01:41:00+00:00",
                                        edit(BARS[5],low="0.8",open="2.4",close="2.4"),
                                        proof_ref="synthetic-correction-5")

def make_second(first=None):
    e=first if first is not None else make_one()
    row=dict(BARS[5],**e["replacement_ohlcv"])
    return v4.make_synthetic_correction(2,row,"2007-09-20T01:42:00+00:00",
                                        edit(row,low="0.7",open="2.5",close="2.5"),
                                        proof_ref="synthetic-correction-5-again")

def view(events=None,asof=T,pin=PIN,rows=BARS):
    return v4.asof_restatement(rows,[] if events is None else events,
                               market_asof=asof,rule_pin=pin,direction="UP")

class SourceCorrectionInvariants(unittest.TestCase):
    def test_baseline_no_corrections(self):
        z=view()
        self.assertEqual(z["correction_count_applied"],0)
        self.assertTrue(z["active_provisional_pens"])
        self.assertFalse(z["full_pen_certified"])
        self.assertFalse(z["historic_replay_events_disclosed"])
        self.assertTrue(z["historic_replay_events_may_not_be_claimed_live"])
        self.assertFalse(z["real_market_data_used"])
    def test_before_correction_unchanged_even_with_future_record(self):
        a=view(asof=BEFORE)
        b=view([make_one()],asof=BEFORE)
        self.assertEqual(a,b)
    def test_after_correction_receives_new_version_and_snapshot(self):
        before=view([make_one()],asof=BEFORE)
        after=view([make_one()],asof=AFTER)
        self.assertEqual(before["correction_count_applied"],0)
        self.assertEqual(after["correction_count_applied"],1)
        self.assertNotEqual(before["effective_source_revision_sha256"],
                            after["effective_source_revision_sha256"])
        self.assertNotEqual(before["snapshot_sha256"],after["snapshot_sha256"])
        self.assertTrue(after["corrected_bar_original_known_at_unchanged_not_corrected_known_at"])
    def test_correction_after_bar_close_but_not_backdated(self):
        a=view([make_one()],asof="2007-09-20T01:40:59+00:00")
        b=view([make_one()],asof="2007-09-20T01:41:00+00:00")
        self.assertEqual(a["correction_count_applied"],0)
        self.assertEqual(b["correction_count_applied"],1)
        self.assertFalse(b["historic_replay_events_disclosed"])
    def test_immutable_first_event_when_second_appended(self):
        x=make_one();y=make_second(x)
        first=v4.validate_journal(BARS,[x])
        second=v4.validate_journal(BARS,[x,y])
        self.assertEqual(first,second[:1])
        self.assertEqual(view([x,y],asof="2007-09-20T01:41:30+00:00"),
                         view([x],asof="2007-09-20T01:41:30+00:00"))
        self.assertEqual(view([x,y])["correction_count_applied"],2)
    def test_same_event_replay_is_deterministic(self):
        x=make_one()
        self.assertEqual(view([x]),view([x]))
    def test_wrong_prior_hash_rejected(self):
        x=make_one()
        x["expected_old_digest"]="a"*64
        x["event_id"]="CORR4-"+v2.digest({k:v for k,v in x.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"prior"):
            view([x])
    def test_event_tamper_rejected_even_before_received_time(self):
        x=make_one();x["replacement_ohlcv"]["high"]="12"
        with self.assertRaisesRegex(ValueError,"digest"):
            view([x],asof=BEFORE)
    def test_duplicate_correction_event_rejected(self):
        e=make_one()
        with self.assertRaises(ValueError):
            view([e,e])
    def test_out_of_order_correction_events_rejected(self):
        e=make_one()
        later=make_second(e)
        events=[later,e]
        with self.assertRaisesRegex(ValueError,"ordinal"):
            view(events)
    def test_same_receive_time_rejected(self):
        a=make_one()
        b=make_second(a)
        b["received_at"]=a["received_at"]
        b["event_id"]="CORR4-"+v2.digest({k:v for k,v in b.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"strictly"):
            view([a,b])
    def test_before_original_bar_known_rejected(self):
        a=v4.make_synthetic_correction(1,BARS[5],"2007-09-20T01:35:30+00:00",
                                       edit(BARS[5],low="0.8",open="2.4",close="2.4"),
                                       proof_ref="synthetic")
        with self.assertRaisesRegex(ValueError,"predate"):
            view([a])
    def test_cannot_change_bar_times_or_keys(self):
        a=make_one()
        a["replacement_ohlcv"]["known_at"]="2007-09-20T02:00:00+00:00"
        a["event_id"]="CORR4-"+v2.digest({k:v for k,v in a.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"exactly five"):
            view([a])
    def test_cannot_mix_float_with_decimal_strings(self):
        a=make_one()
        a["replacement_ohlcv"]["low"]=0.8
        a["event_id"]="CORR4-"+v2.digest({k:v for k,v in a.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"decimal strings"):
            view([a])
    def test_invalid_replacement_ohlc_rejected(self):
        a=make_one()
        a["replacement_ohlcv"]["high"]="0.5"
        a["event_id"]="CORR4-"+v2.digest({k:v for k,v in a.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"OHLCV"):
            view([a])
    def test_repeated_unchanged_row_rejected(self):
        a=v4.make_synthetic_correction(1,BARS[5],"2007-09-20T01:41:00+00:00",
                                       edit(BARS[5]),proof_ref="synthetic")
        with self.assertRaisesRegex(ValueError,"No-op"):
            view([a])
    def test_unrecognized_source_proof_fails_closed(self):
        a=make_one()
        a["source_proof_kind"]="external_downloaded"
        a["event_id"]="CORR4-"+v2.digest({k:v for k,v in a.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"synthetic"):
            view([a])
    def test_unknown_bar_correction_rejected(self):
        a=make_one()
        a["bar_key"]="not-a-real-source"
        a["event_id"]="CORR4-"+v2.digest({k:v for k,v in a.items() if k!="event_id"})
        with self.assertRaisesRegex(ValueError,"unknown"):
            view([a])
    def test_bad_data_kind_disallowed(self):
        x=copy.deepcopy(BARS)
        x[2]["source_revision_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"Mixed"):
            view(rows=x)
    def test_future_correction_does_not_expose_future_id_or_count(self):
        future=make_one()
        a=view([future],asof=BEFORE)
        self.assertNotIn(future["event_id"],json.dumps(a))
        self.assertEqual(a["correction_count_applied"],0)
        self.assertEqual(a["applied_corrections"],[])
    def test_no_change_to_original_input(self):
        base=copy.deepcopy(BARS)
        a=make_one()
        view([a])
        self.assertEqual(BARS,base)
    def test_reject_naive_asof(self):
        with self.assertRaisesRegex(ValueError,"Naive"):
            view(asof="2007-09-20T02:00:00")
    def test_corrected_future_unfinished_bar_not_made_visible(self):
        a=make_one()
        z=view([a])
        self.assertEqual(z["visible_prefix_count"],10) # final synthetic bar remains unclosed
        self.assertTrue(z["active_provisional_pen_count"]>=0)

class PenProofContract(unittest.TestCase):
    def test_default_proof_gate_does_not_certify(self):
        z=view()
        item=z["active_provisional_pens"][0]
        p=v4.pen_proof_obligations(z,item["id"])
        self.assertEqual(p["status"],"BLOCKED_NOT_CERTIFIED")
        self.assertFalse(p["certifies_complete_pen"])
        self.assertEqual(p["segment_role"],"UNDETERMINED")
        self.assertIn("MISSING_UNIQUE_DECOMPOSITION",p["blockers"])
        self.assertIn("NO_INDEPENDENT_VERIFIER_REGISTERED",p["blockers"])
    def test_forged_all_proof_refs_cannot_certify(self):
        z=view()
        all_claimed={k:{"proof_ref":"self-asserted-verified","reviewed_at":T} for k in v4.OBLIGATIONS}
        p=v4.pen_proof_obligations(z,z["active_provisional_pens"][0]["id"],all_claimed)
        self.assertEqual(p["status"],"BLOCKED_NOT_CERTIFIED")
        self.assertEqual(p["proof_claims_count"],len(v4.OBLIGATIONS))
        self.assertTrue(all("UNVERIFIED_EXTERNAL_"+k.upper() in p["blockers"] for k in v4.OBLIGATIONS))
        self.assertFalse(p["certifies_complete_pen"])
    def test_future_proof_time_blocked(self):
        z=view()
        p=v4.pen_proof_obligations(z,z["active_provisional_pens"][0]["id"],
                                    {"original_chart":{"proof_ref":"madeup","reviewed_at":"2007-09-21T00:00:00+00:00"}})
        self.assertIn("FUTURE_PROOF_ORIGINAL_CHART",p["blockers"])
    def test_unknown_candidate_fails(self):
        z=view()
        p=v4.pen_proof_obligations(z,"P3-non-existent")
        self.assertIn("NOT_ACTIVE_IN_THIS_SNAPSHOT",p["blockers"])
    def test_old_candidate_from_pre_correction_is_not_active_post(self):
        before=view([make_one()],asof=BEFORE)
        after=view([make_one()],asof=AFTER)
        id_before=before["active_provisional_pens"][0]["id"]
        p=v4.pen_proof_obligations(after,id_before)
        self.assertEqual(p["status"],"BLOCKED_NOT_CERTIFIED")
        self.assertIn("NOT_ACTIVE_IN_THIS_SNAPSHOT",p["blockers"])
    def test_snapshot_provenance_bound_to_proof(self):
        z=view()
        ident=z["active_provisional_pens"][0]["id"]
        p=v4.pen_proof_obligations(z,ident)
        self.assertEqual(p["bound_source_snapshot_sha256"],z["snapshot_sha256"])
    def test_bad_claim_shape_rejected(self):
        z=view();ident=z["active_provisional_pens"][0]["id"]
        with self.assertRaisesRegex(ValueError,"Unknown"):
            v4.pen_proof_obligations(z,ident,{"trade_ready":True})
        with self.assertRaisesRegex(ValueError,"reference"):
            v4.pen_proof_obligations(z,ident,{"raw_extreme":{"proof_ref":""}})
    def test_naive_evidence_review_time_rejected(self):
        z=view();ident=z["active_provisional_pens"][0]["id"]
        with self.assertRaisesRegex(ValueError,"Naive"):
            v4.pen_proof_obligations(z,ident,{"raw_extreme":{"proof_ref":"any",
                                           "reviewed_at":"2007-09-20T02:00:00"}})
    def test_cannot_spoof_strict_role_in_payload(self):
        z=view()
        z["active_provisional_pens"][0]["payload"]["complete_pen"]=True
        with self.assertRaisesRegex(ValueError,"unsupported"):
            v4.pen_proof_obligations(z,z["active_provisional_pens"][0]["id"])
    def test_not_really_a_real_market_certifier(self):
        z=view()
        for x in z["active_provisional_pens"]:
            q=v4.pen_proof_obligations(z,x["id"])
            self.assertFalse(q["certifies_complete_pen"])
            self.assertFalse(q["orders_sent"])
        self.assertFalse(z["real_market_data_used"])

if __name__=="__main__":
    unittest.main()
