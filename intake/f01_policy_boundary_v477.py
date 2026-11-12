"""F01 v4.77 research intake: policy-isolated, evidence-aware exit proposals.

This is a *gate for user-supplied candidate records*, NOT an implementation
of Chanlun completion, an author-authenticated rule, or a market-data parser.
Keep outside the book's canonical/mirrored source roots until reviewed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

STRICT = "STRICT_TICK_F1"
OPERABLE = "OPERABLE_SEGMENT_CUTOFF_F1"
_ALLOWED = frozenset((STRICT, OPERABLE))


class BoundaryError(ValueError):
    """An asserted completion crossed a source, time, or policy boundary."""


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    policy_id: str
    observed_at: int
    first_known_at: int
    kind: str
    depends_on: tuple[str, ...] = ()
    source_role: str = "RESEARCHER_ASSERTION"


@dataclass(frozen=True)
class Candidate:
    policy_id: str
    level: int
    center_id: str
    exit_evidence_id: str
    proposed_at: int
    status: str = "CANDIDATE_ONLY"


def check_candidate(candidate: Candidate, evidence: Sequence[Evidence]) -> dict:
    """Fail closed. Return eligibility to STUDY a proposal, never a finish proof.

    A root STRICT_TICK_F1 candidate has no independently certified exit
    production rule in the current project; it always stays OPEN.
    The operable policy may produce a research candidate only when the
    required independent local evidence and time constraints are explicit.
    """
    if candidate.policy_id not in _ALLOWED:
        raise BoundaryError("unknown analysis policy")
    if candidate.level < 0 or not candidate.center_id:
        raise BoundaryError("missing level or center identity")
    if candidate.status != "CANDIDATE_ONLY":
        raise BoundaryError("completion status cannot be asserted by intake")
    if candidate.proposed_at < 0:
        raise BoundaryError("negative proposal clock")
    graph: dict[str, Evidence] = {}
    for e in evidence:
        if not e.evidence_id or e.evidence_id in graph:
            raise BoundaryError("empty or duplicate evidence id")
        if e.policy_id != candidate.policy_id:
            raise BoundaryError("cross-policy evidence cannot certify a candidate")
        if e.observed_at < 0 or e.first_known_at < e.observed_at:
            raise BoundaryError("lookahead or negative observation clock")
        if e.source_role not in ("RESEARCHER_ASSERTION", "SOURCE_QUOTE", "RAW_OBSERVATION"):
            raise BoundaryError("unrecognized evidence source role")
        graph[e.evidence_id] = e
    colors: dict[str, int] = {}

    def visit(key: str) -> None:
        if key not in graph:
            raise BoundaryError("missing proof dependency")
        if colors.get(key) == 1:
            raise BoundaryError("cyclic evidence dependency")
        if colors.get(key) == 2:
            return
        colors[key] = 1
        current = graph[key]
        for dep in current.depends_on:
            visit(dep)
            if graph[dep].first_known_at > current.first_known_at:
                raise BoundaryError("evidence depends on future knowledge")
        colors[key] = 2

    for key in graph:
        visit(key)
    if candidate.exit_evidence_id not in graph:
        raise BoundaryError("missing proposed exit evidence")
    exit_evidence = graph[candidate.exit_evidence_id]
    if exit_evidence.first_known_at > candidate.proposed_at:
        raise BoundaryError("exit was not knowable at proposal time")
    if candidate.policy_id == STRICT:
        return {
            "status": "ROOT_EXIT_OPEN",
            "certified_finished": False,
            "market_authenticated": False,
            "policy_id": STRICT,
            "reason": "NO_INDEPENDENT_STRICT_ROOT_PAN_EXIT_RULE",
        }
    if exit_evidence.kind != "OPERABLE_EXIT_OBSERVATION":
        raise BoundaryError("operable policy needs its own typed observation")
    if not exit_evidence.depends_on:
        raise BoundaryError("exit observation lacks independent prerequisites")
    if any(graph[dep].kind in ("FINISHED_MOVEMENT", "PAN_EXIT", "THIRD_POINT")
           for dep in exit_evidence.depends_on):
        raise BoundaryError("completion assertion cannot justify its own exit")
    return {
        "status": "OPERABLE_RESEARCH_CANDIDATE_ONLY",
        "certified_finished": False,
        "market_authenticated": False,
        "policy_id": OPERABLE,
        "reason": "CONDITIONAL_OBSERVATION_NOT_AUTHOR_COMPLETION",
    }
