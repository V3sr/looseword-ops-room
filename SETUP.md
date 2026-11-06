# Room setup (one time, about 10 minutes)

Switch Console is a desktop app, so these steps are clicks. They match Switch Console 0.40.1
on Windows 11, as used for the recorded runs. Replace
`C:\Users\Andy\Projects\looseword-ops-room` with your own clone path.

## 0. Before you start
- Docker Desktop is installed and running.
- Claude Code is installed and signed in. The native installer puts it at
  `%USERPROFILE%\.local\bin\claude.exe`; check with `claude --version` (tested with 2.1.316).
- Switch Console is installed from the
  [Switch releases](https://github.com/sandbox-quantum/switch/releases/latest)
  (`switch-console-x64.exe`, signed by SandboxAQ).
- The simulator is running in its own terminal: `python sim\intake_sim.py`

## 1. Start a local server
1. Open **Switch Console**.
2. Choose **Set up a server on this computer** and start it. The first start pulls the
   Mattermost image, so give it a few minutes.
3. When it is ready, the top left shows **Local Switch server** and the top right **Running**.

## 2. Add lw-triage
1. Click **Your Agents**, then the **+** card.
2. **Name:** `lw-triage`
3. **Description:** `Triage agent for Looseword Ops Room (sim)`
4. **Agent instructions:**
   `You are lw-triage. Follow CLAUDE.md in your working directory exactly. All services here are synthetic. The human operator makes every decision.`
5. **Run location:** This computer. **Agent provider:** Claude Code (should say Ready).
6. Open **Settings** at the bottom of the form:
   - Leave **Auto mode** on and **Bypass permissions** off.
   - **Who can talk to your agent:** Me and my agents (default). This is what lets the two
     agents hand work to each other.
   - **Directory:** click **Choose...** and pick `...\looseword-ops-room\agents\lw-triage`.
     The field itself is read only.
7. Click **Add agent**.

## 3. Add lw-verify
Same as step 2, with:
- **Name:** `lw-verify`
- **Description:** `Verify agent for Looseword Ops Room (sim)`
- **Agent instructions:**
  `You are lw-verify. Follow CLAUDE.md in your working directory exactly. Only run tools/probe.py. Never invent results.`
- **Directory:** `...\looseword-ops-room\agents\lw-verify`

## 4. Create the room
1. Click **Your Rooms**, then **Create room**.
2. **Messaging app:** Mattermost. **Name:** `looseword-ops-room`.
   **Description:** `Synthetic intake incident drills. No real data.`
3. **Agents:** search and add `lw-triage`, then `lw-verify`.
4. Open **Instructions** and paste:
   `Synthetic incident drill. Flow: operator reports, lw-triage frames it and hands to lw-verify, lw-verify probes and hands back, operator decides. Only act when addressed.`
5. Click **Create room**. Console opens the room. Both bots post a short hello.

## 5. Check one agent answers
Type `@lw-triage say hello and your role in one line.` (pick the name from the
autocomplete). A reply within about 20 seconds means the setup works.

Then run the scenario in [DEMO.md](DEMO.md).

## Where things are
- The room is a Mattermost channel. Console shows it in its own window; Mattermost also
  serves it on a local port that Console picks (it was `127.0.0.1:54141` on the test machine).
- Each agent works in its folder under `agents/`. Switch keeps its own data under
  `%APPDATA%\switchdash`.
