# Recorded runs

All runs were on November 5, 2026 (local time, Pacific), in `#looseword-ops-room` on a local
Switch server (Switch Console 0.40.1, switch-core 0.31.0, Mattermost 11.9.0). Times in the
probe tables are UTC from the probe itself. The operator account is the local Mattermost
user named `user`. Every target is synthetic on 127.0.0.1.

## Run 0: one agent answers (9:09 PM)
- Operator: `@lw-triage say hello and your role in one line.`
- lw-triage: "Hi, I'm lw-triage. I frame each reported issue, hand the checks to lw-verify,
  then lay out options and record the decision you make."
- Shows: the agent is reachable in the room and has read its brief.

## Run 1: full workflow, decision B (9:10 to 9:12 PM)
Simulator: `outage`.

| Step | Who | What appeared in the room |
|---|---|---|
| 1 | Operator | "@lw-triage The UBC test intake form looks down. Opening it spins, then errors. Can you check?" |
| 2 | lw-triage | Triage card (Reported, Known facts, Not yet known, Checks needed), mentions @lw-verify |
| 3 | lw-verify | Probe table at 04:10:43Z: ubc-test 503 in 1250 ms `form_backend_timeout`; vanier-test 200 in 2 ms; orchard-test connection refused after 2042 ms. Mentions @lw-triage |
| 4 | lw-triage | Assessment INC-001: Observed (quoted from lw-verify), Unknown, severity guess "Medium", options A, B, C |
| 5 | Operator | "@lw-triage B. Send UBC test traffic to Vanier test for now and find out why orchard-test is not up." |
| 6 | lw-triage | "Decision recorded: INC-001", five tasks with owners, record path |

Record written by lw-triage: [run1-INC-001.md](run1-INC-001.md).
Screens: [run1-01](run1-01-report-triage-verify.jpg), [run1-02](run1-02-assessment-decision.jpg).

Found:
- Mattermost showed the probe table as raw text, because no empty line came before it.
  Fixed in `tools/probe.py`, which now prints the heading and the empty line itself
  (confirmed in run 3).
- The triage card's Known facts said "One person saw it", which the report did not state.
  The brief now says not to add facts like this. Not yet re-run with a fresh session.

## Run 2: repeat report, decision C, recovery (9:13 to 9:15 PM)
Simulator: `outage` for the report, switched to `recovered` before the decision.

| Step | Who | What appeared in the room |
|---|---|---|
| 1 | Operator | "@lw-triage New report: the UBC test form fails again tonight. Please check." |
| 2 | lw-triage | Triage card, mentions @lw-verify. Treated as INC-001 continuing |
| 3 | lw-verify | 04:13:44Z: ubc-test 503 in 1249 ms; vanier-test 200 in 2 ms; orchard-test refused after 2055 ms |
| 4 | lw-triage | Assessment with options |
| 5 | Operator | "@lw-triage C. Hold, and get a fresh ubc-test probe." |
| 6 | lw-triage | Decision recorded (Update 1), mentions @lw-verify for one re-probe |
| 7 | lw-verify | 04:15:25Z: ubc-test 200 in 54 ms. Said its probe cannot explain why orchard-test is down and that someone with simulator access is needed |
| 8 | lw-triage | New assessment: ubc-test recovered, cause unknown; severity "Low for UBC right now"; asks the operator to name an owner for Orchard |

Record after the run: [run2-INC-001-updated.md](run2-INC-001-updated.md).
Screens: [run2-01](run2-01-repeat-report.jpg), [run2-02](run2-02-decision-c-handoff.jpg),
[run2-03](run2-03-recovered-reprobe.jpg).

## Run 3: table fix and a separate report (9:17 to 9:18 PM)
Simulator: back to `outage`.

- Operator: "@lw-triage Separate report: the Orchard test form will not open at all."
- lw-verify's table now renders as a table (04:17:59Z: 503 in 1262 ms, 200 in 25 ms,
  refused after 2051 ms). Screen: [run3-01](run3-01-table-renders.jpg).
- lw-verify noticed ubc-test had gone from 200 back to 503 and said it could not tell why.
  That matches what happened: the simulator was restarted in `outage` mode between runs.
- Deviation: lw-triage kept the report under INC-001 and asked whether to track Orchard
  separately, instead of opening INC-002. Each agent keeps one session per room, so earlier
  context weighed in. The brief now says "new" or "separate" always opens a new number, and
  [DEMO.md](../../DEMO.md) starts each take in a fresh room. This fix has not been re-run yet.

## Checks run outside the room
- `python -m unittest discover -s tests -v`: 5 tests, OK (failing 503, healthy 200,
  unreachable, recovered 200, non-local URL refused).
- Running a second simulator while one is up now fails with "Port 8701 is already in use"
  instead of silently sharing the port (found during testing on Windows).
