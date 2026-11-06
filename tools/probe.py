"""Probe the synthetic intake targets and print what was actually observed.

Used by the lw-verify agent. Standard library only.

  python tools/probe.py                 all targets, markdown table
  python tools/probe.py ubc-test        one target
  python tools/probe.py --json          machine-readable output

Refuses any URL that is not on 127.0.0.1 or localhost, so the agent cannot be
pointed at a live service by a message in the room.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
TIMEOUT_S = 3.0


def load_targets() -> list[dict]:
    data = json.loads((ROOT / "targets.json").read_text(encoding="utf-8"))
    return data["targets"]


def probe(target: dict) -> dict:
    url = target["url"]
    host = urlparse(url).hostname
    result = {
        "name": target["name"],
        "url": url,
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": None,
        "latency_ms": None,
        "outcome": None,
        "detail": None,
    }
    if host not in ALLOWED_HOSTS:
        result["outcome"] = "refused"
        result["detail"] = f"host {host!r} is not local; probe only checks synthetic targets"
        return result

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_S) as resp:
            body = resp.read(2000).decode("utf-8", "replace")
            result["status"] = resp.status
            result["outcome"] = "healthy" if resp.status == 200 else "unexpected"
            result["detail"] = summarize(body)
    except urllib.error.HTTPError as err:
        body = err.read(2000).decode("utf-8", "replace")
        err.close()
        result["status"] = err.code
        result["outcome"] = "failing"
        result["detail"] = summarize(body)
    except urllib.error.URLError as err:
        reason = err.reason
        result["outcome"] = "unreachable"
        if isinstance(reason, ConnectionRefusedError):
            result["detail"] = "connection refused (nothing is listening on that port)"
        else:
            result["detail"] = f"{type(reason).__name__}: {reason}"
    except TimeoutError:
        result["outcome"] = "timeout"
        result["detail"] = f"no response within {TIMEOUT_S:.0f} s"
    result["latency_ms"] = round((time.perf_counter() - start) * 1000)
    return result


def summarize(body: str) -> str:
    try:
        data = json.loads(body)
    except ValueError:
        return body[:120]
    keys = ("status", "error", "form_id")
    return ", ".join(f"{k}={data[k]}" for k in keys if k in data)


def as_table(results: list[dict]) -> str:
    # The heading and empty line are part of the output so the agent can paste it
    # unchanged; Mattermost only renders a table that follows an empty line.
    lines = [
        "**Verification results**",
        "",
        "| Target | HTTP | Latency | Outcome | Detail |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        status = r["status"] if r["status"] is not None else "none"
        lines.append(
            f"| {r['name']} | {status} | {r['latency_ms']} ms | {r['outcome']} | {r['detail']} |"
        )
    lines.append(f"\nChecked at {results[0]['checked_at']} (UTC) from this machine. Synthetic targets only.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*", help="target names; default all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    targets = load_targets()
    if args.names:
        known = {t["name"]: t for t in targets}
        unknown = [n for n in args.names if n not in known]
        if unknown:
            print(f"Unknown target(s): {', '.join(unknown)}. Known: {', '.join(known)}", file=sys.stderr)
            return 2
        targets = [known[n] for n in args.names]

    results = [probe(t) for t in targets]
    print(json.dumps(results, indent=2) if args.json else as_table(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
