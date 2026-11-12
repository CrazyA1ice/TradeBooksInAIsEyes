"""Adversarial checks for the isolated F01 policy-boundary intake prototype."""
import unittest
from dataclasses import replace

from intake.f01_policy_boundary_v477 import (
    BoundaryError, Candidate, Evidence, STRICT, OPERABLE, check_candidate
)


def records(policy=OPERABLE):
    return [
        Evidence("raw", policy, 1, 1, "RAW_OBSERVATION"),
        Evidence("exit", policy, 2, 3, "OPERABLE_EXIT_OBSERVATION",
                 ("raw",)),
    ]


class PolicyBoundaryTests(unittest.TestCase):
    def test_operable_proposal_is_never_completed(self):
        result = check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 3), records())
        self.assertEqual(result["status"], "OPERABLE_RESEARCH_CANDIDATE_ONLY")
        self.assertFalse(result["certified_finished"])
        self.assertFalse(result["market_authenticated"])

    def test_strict_tick_candidate_stays_open_even_with_exit_label(self):
        result = check_candidate(Candidate(STRICT, 0, "C0", "exit", 3),
                                 records(STRICT))
        self.assertEqual(result["status"], "ROOT_EXIT_OPEN")
        self.assertFalse(result["certified_finished"])

    def test_cross_policy_dependency_rejected(self):
        ev = records()
        ev[0] = replace(ev[0], policy_id=STRICT)
        with self.assertRaisesRegex(BoundaryError, "cross-policy"):
            check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 3), ev)

    def test_future_known_exit_cannot_backfill(self):
        with self.assertRaisesRegex(BoundaryError, "not knowable"):
            check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 2), records())

    def test_circular_dependency_rejected(self):
        ev = records()
        ev[0] = replace(ev[0], depends_on=("exit",))
        with self.assertRaisesRegex(BoundaryError, "cyclic"):
            check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 3), ev)

    def test_missing_dependency_rejected(self):
        ev = records()
        ev[1] = replace(ev[1], depends_on=("not-here",))
        with self.assertRaisesRegex(BoundaryError, "missing proof"):
            check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 3), ev)

    def test_strict_completed_flag_is_not_accepted(self):
        with self.assertRaisesRegex(BoundaryError, "status"):
            check_candidate(Candidate(STRICT, 0, "C0", "exit", 3, "PROVEN"),
                            records(STRICT))

    def test_exit_cannot_depend_on_finished_movement(self):
        ev = records()
        ev[0] = replace(ev[0], kind="FINISHED_MOVEMENT")
        with self.assertRaisesRegex(BoundaryError, "completion assertion"):
            check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 3), ev)

    def test_wrong_observation_kind_rejected(self):
        ev = records()
        ev[1] = replace(ev[1], kind="PAN_DIVERGENCE_ALERT")
        with self.assertRaisesRegex(BoundaryError, "typed observation"):
            check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 3), ev)

    def test_dependency_future_clock_rejected(self):
        ev = records()
        ev[0] = replace(ev[0], first_known_at=4)
        with self.assertRaisesRegex(BoundaryError, "future knowledge"):
            check_candidate(Candidate(OPERABLE, 0, "C0", "exit", 5), ev)


if __name__ == "__main__":
    unittest.main()
