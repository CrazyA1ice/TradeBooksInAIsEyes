# F01 policy-isolated exit intake (v4.77 prototype)

This is **research intake**, deliberately outside the book canonical source roots and exact-mirror manifest. It does not amend v4.76 or replace `check_graph`. The prototype prevents a later *operable* policy result from being silently repackaged as a strict tick-level conclusion.

- `STRICT_TICK_F1`: even a well-formed proposed exit returns `ROOT_EXIT_OPEN`, never `PROVEN`.
- `OPERABLE_SEGMENT_CUTOFF_F1`: a typed, time-consistent, non-cyclic observation may be registered as `OPERABLE_RESEARCH_CANDIDATE_ONLY`, never as a certified movement.
- Every dependency must be in the same frozen policy, present, acyclic, and known by the time it is used. The candidate cannot pretend an event is known before its `first_known_at` time.
- Author quotes, researcher assertions, and raw observations have distinct source roles. A role label does **not** authenticate the source.
- Dependency `FINISHED_MOVEMENT`, `PAN_EXIT` or `THIRD_POINT` cannot stand in for an independent exit prerequisite.

Local smoke checks, from repository root:

```sh
python -B -m unittest discover -s intake -p 'test_f01_policy_boundary_v477.py' -v
```

**Promotion gate (not yet passed):** audit actual author/source evidence, agree a precise non-strict `f1` initialization and independent exit predicate, integrate with the existing F01 graph checker, add dedicated CI, update workflow/status/work log, exact-mirror new canonical files and regenerate `ChanlunCollection/COLLECTION_MANIFEST.json`. Do not merge this prototype while the book-collection workflow gate rejects its incomplete lifecycle.

F01 ROOT_IDENTITY / ROOT_EXIT, OB38, OB99: **OPEN**. Real market data, backtests, trading and claims of author-wide proof: **NOT_RUN / NOT_CERTIFIED**.
