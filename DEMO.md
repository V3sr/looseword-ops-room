# Demo script (about 3 minutes)

Use this for the submission video. Everything on screen is synthetic.

## Before you record
1. Start the simulator in its own terminal and leave it running:
   ```
   python sim\intake_sim.py
   ```
2. Clear old records so this take starts at INC-001:
   ```
   Remove-Item agents\lw-triage\records\* -ErrorAction SilentlyContinue
   ```
3. For a clean take, create a fresh room in Switch Console (**Your Rooms**, **Create room**),
   for example `ops-room-take-2`, with both agents and the same room instructions as in
   [SETUP.md](SETUP.md). Agents keep one session per room, so a new room means no memory of
   earlier takes.
4. Close other windows. Make the Console window full screen. Only the local operator
   account, the two bots and synthetic data should be visible.

## Beats

| Time | You type in the room | What to point out |
|---|---|---|
| 0:00 | (nothing) | "Looseword is a campus confession site. When an intake form breaks, one operator has to figure out what is real, fast. This room gives that operator two agents." Show the member list: you, lw-triage, lw-verify |
| 0:15 | `@lw-triage The UBC test intake form looks down. Opening it spins, then errors. Can you check?` | The report goes to one agent by name |
| 0:30 | (wait) | lw-triage posts a triage card and hands the checks to **@lw-verify**. It does not run checks itself |
| 0:50 | (wait) | lw-verify runs the probe and posts a real table: 503 after about 1.2 s, 200, connection refused. Then hands back to **@lw-triage** |
| 1:15 | (wait) | The assessment keeps **Observed** apart from **Unknown**, labels severity as a guess, and offers A, B, C |
| 1:40 | `@lw-triage B. Send UBC test traffic to Vanier test for now and find out why orchard-test is not up.` | The decision is yours, in your words |
| 1:55 | (wait) | "Decision recorded" with tasks and owners. Open `agents\lw-triage\records\INC-001.md` to show the written record |
| 2:15 | Optional: in the simulator terminal press Ctrl+C, run `python sim\intake_sim.py --scenario recovered`, then type `@lw-triage C. Hold, and get a fresh ubc-test probe.` | A second handoff: lw-verify re-probes and sees 200. Nobody claims to know why it recovered |
| 2:45 | (nothing) | Close: "Switch is the room, the routing between agents, and the record of who decided what. Synthetic data only; a prototype, not live monitoring." |

## If something goes wrong
- **An agent does not answer:** check the message starts with `@lw-triage` (pick it from the
  autocomplete) and that the agent shows "Running" under **Your Agents**.
- **The table shows raw `|` characters:** the agent's session predates the probe fix. Use a
  fresh room.
- **Probe shows 200 for ubc-test when you expected 503:** the simulator is in `recovered`
  mode. Restart it without `--scenario`.
- **"Port 8701 is already in use":** another simulator is running. Close that terminal first.
