"""Synthetic Looseword intake endpoints for the Ops Room demo.

Everything here is invented. No real forms, students, receipts or services are
touched. The simulator binds to 127.0.0.1 only.

Targets (defined in targets.json at the repo root):
  ubc-test     port 8701  failing  (HTTP 503 after a slow response)
  vanier-test  port 8702  healthy  (HTTP 200)
  orchard-test port 8703  nothing listens here, so it is unavailable

Scenario switch: `python sim/intake_sim.py --scenario recovered` makes
ubc-test return 200, so a re-check after the human decision shows a change.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"

FAILING_BODY = {
    "service": "synthetic-intake",
    "form_id": "SYN-UBC-TEST-01",
    "status": "unavailable",
    "error": "form_backend_timeout",
    "detail": "Synthetic upstream form provider did not answer within 1000 ms.",
    "synthetic": True,
}

HEALTHY_BODY = {
    "service": "synthetic-intake",
    "form_id": "SYN-VANIER-TEST-01",
    "status": "accepting",
    "synthetic": True,
}

RECOVERED_BODY = {
    "service": "synthetic-intake",
    "form_id": "SYN-UBC-TEST-01",
    "status": "accepting",
    "synthetic": True,
}


def make_handler(name: str, mode: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "SyntheticIntake/1.0"

        def do_GET(self):  # noqa: N802 (stdlib naming)
            if self.path not in ("/", "/intake", "/health"):
                self._send(404, {"error": "not_found", "synthetic": True})
                return
            if mode == "failing":
                time.sleep(1.2)  # slow, then fail, like a stalled upstream
                self._send(503, FAILING_BODY, {"Retry-After": "120"})
            elif mode == "recovered":
                self._send(200, RECOVERED_BODY)
            else:
                self._send(200, HEALTHY_BODY)

        def _send(self, code: int, body: dict, extra: dict | None = None):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Synthetic", "true")
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            print(f"[{name}] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")

    return Handler


class ExclusiveServer(ThreadingHTTPServer):
    # The stock server sets SO_REUSEADDR, which on Windows lets a second process bind
    # the same port and silently share traffic. Fail loudly instead.
    allow_reuse_address = False


def serve(scenario: str) -> list[ThreadingHTTPServer]:
    ubc_mode = "recovered" if scenario == "recovered" else "failing"
    plan = [("ubc-test", 8701, ubc_mode), ("vanier-test", 8702, "healthy")]
    servers = []
    for name, port, mode in plan:
        try:
            httpd = ExclusiveServer((HOST, port), make_handler(name, mode))
        except OSError as err:
            for running in servers:
                running.shutdown()
                running.server_close()
            raise SystemExit(
                f"Port {port} is already in use ({err}). Stop the other simulator first."
            ) from err
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        servers.append(httpd)
        print(f"{name:12} http://{HOST}:{port}/intake  mode={mode}")
    print("orchard-test http://127.0.0.1:8703/intake  mode=unavailable (nothing listens)")
    return servers


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", choices=["outage", "recovered"], default="outage")
    args = parser.parse_args()
    servers = serve(args.scenario)
    print(f"Scenario '{args.scenario}' running. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        for httpd in servers:
            httpd.shutdown()


if __name__ == "__main__":
    main()
