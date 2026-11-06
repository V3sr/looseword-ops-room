# INC-001 (synthetic): UBC test intake form not loading

All targets are synthetic local endpoints. No live Looseword service, real student or real data was checked or affected.

## Issue
Operator reported: "The UBC test intake form looks down. Opening it spins, then errors."

## Observed evidence (from lw-verify, checked 2026-11-06T04:10:43Z UTC)
| Target | HTTP | Latency | Outcome | Detail |
|---|---|---|---|---|
| ubc-test | 503 | 1250 ms | failing | status=unavailable, error=form_backend_timeout, form_id=SYN-UBC-TEST-01 |
| vanier-test | 200 | 2 ms | healthy | status=accepting, form_id=SYN-VANIER-TEST-01 |
| orchard-test | none | 2042 ms | unreachable | connection refused (nothing is listening on that port) |

## Unknowns
- Root cause of the ubc-test backend timeout.
- Why orchard-test is not listening, and whether it is related to the UBC failure.
- When either failure started.
- Whether vanier-test shares the UBC backend (it could take on the same fault under fallback load).
- Whether real users would have been affected (none here, all synthetic).

## Decision
- **Option:** B
- **Operator's words:** "B. Send UBC test traffic to Vanier test for now and find out why orchard-test is not up."
- **Decided by:** user (operator, workspace owner)
- **Recorded at:** 2026-11-06T04:11:50Z (UTC)

## Tasks
- [ ] **operator:** Apply the simulated fallback that sends UBC test traffic to the Vanier test intake (no real change).
- [ ] **lw-verify:** Re-probe vanier-test after the fallback to confirm it stays healthy.
- [ ] **lw-verify:** Investigate why orchard-test is not listening and report findings.
- [ ] **lw-verify:** Re-probe ubc-test later to see if the backend timeout clears.
- [ ] **lw-triage:** Update this record with new evidence and the eventual resolution.
