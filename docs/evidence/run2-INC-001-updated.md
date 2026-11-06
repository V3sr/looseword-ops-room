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

---

## Update 1: repeat report

### Issue
Operator reported: "New report: the UBC test form fails again tonight. Please check."
Treated as INC-001 continuing, because the error matches the first probe.

### Observed evidence (from lw-verify, checked 2026-11-06T04:13:44Z UTC)
| Target | HTTP | Latency | Outcome | Detail |
|---|---|---|---|---|
| ubc-test | 503 | 1249 ms | failing | status=unavailable, error=form_backend_timeout, form_id=SYN-UBC-TEST-01 |
| vanier-test | 200 | 2 ms | healthy | status=accepting, form_id=SYN-VANIER-TEST-01 |
| orchard-test | none | 2055 ms | unreachable | connection refused (nothing is listening on that port) |

### Unknowns
- Root cause of the ubc-test backend timeout, and when it started.
- Whether the simulated Vanier fallback (decision B above) was applied.
- Whether vanier-test shares the UBC backend.
- Why orchard-test is not listening.
- Whether real users would have been affected (none here, all synthetic).

### Decision
- **Option:** C
- **Operator's words:** "C. Hold, and get a fresh ubc-test probe."
- **Decided by:** user (operator, workspace owner)
- **Recorded at:** 2026-11-06T04:15:09Z (UTC)

### Tasks
- [ ] **operator:** Hold. Make no change until the fresh probe is in.
- [ ] **lw-verify:** Run one fresh probe of ubc-test and report the result.
- [ ] **lw-triage:** Add the fresh probe result to this record and bring the options back to the operator.
- [ ] **lw-verify:** Open item from decision B: find out why orchard-test is not listening.

### Fresh probe (from lw-verify, checked 2026-11-06T04:15:25Z UTC)
| Target | HTTP | Latency | Outcome | Detail |
|---|---|---|---|---|
| ubc-test | 200 | 54 ms | healthy | status=accepting, form_id=SYN-UBC-TEST-01 |

- ubc-test recovered between 04:13:44Z and 04:15:25Z. Cause of recovery unknown.
- lw-verify reports it cannot investigate orchard-test: its probe script only shows connection refused. The item needs someone with access to the simulator. Owner not yet reassigned.
- Task status: fresh ubc-test probe done. Options returned to the operator.
