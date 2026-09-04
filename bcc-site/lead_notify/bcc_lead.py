"""
bcc_lead -- push every buffaloclawmachines.com form submission to Ken's phone.

Why: Formspree emails land in Gmail's Updates tab and the phone never buzzes.
A lead that waits a day is a lead that booked someone else.

Runs on the droplet as a systemd unit, loopback only (127.0.0.1:8580); nginx
proxies POST /api/lead to it from the site's vhost. The site JS posts the same
JSON it sends to Formspree. Also accepts Formspree's webhook shape
({"submission": {...}}) if that ever gets turned on.

Config: /etc/bcc_lead.env  ->  NTFY_TOPIC=... (never in the repo or page source)
Log:    /home/bccsite/logs/lead.log

Stdlib only. Test-form submissions (email ending @example.com) are logged but
not pushed, so verify_site.py stays quiet.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = int(os.environ.get("LEAD_PORT", "8580"))
TOPIC = os.environ.get("NTFY_TOPIC", "")
LOG = os.environ.get("LEAD_LOG", "/home/bccsite/logs/lead.log")
MAX_BODY = 16_000
RATE_WINDOW = 3600          # seconds
RATE_MAX = 20               # pushes per window, global (one operator, one phone)
_recent: deque[float] = deque()

FIELDS = ("name", "business_or_event", "email", "phone",
          "preferred_contact", "preferred_time", "details")


def log(line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{stamp} {line}\n")
    except OSError:
        print(f"{stamp} {line}", file=sys.stderr)


def clean(v) -> str:
    s = str(v or "").strip()
    return s[:1000]


def normalize(payload: dict) -> dict:
    src = payload.get("submission") if isinstance(payload.get("submission"), dict) else payload
    return {k: clean(src.get(k)) for k in FIELDS}


def ascii_only(s: str) -> str:
    return "".join(c if 32 <= ord(c) < 127 else "?" for c in s)


def rate_ok() -> bool:
    now = time.time()
    while _recent and now - _recent[0] > RATE_WINDOW:
        _recent.popleft()
    if len(_recent) >= RATE_MAX:
        return False
    _recent.append(now)
    return True


def push(lead: dict) -> int:
    if not TOPIC:
        log("NO_TOPIC configured; not pushing")
        return 0
    who = lead["name"] or "Website visitor"
    what = lead["business_or_event"] or "inquiry"
    title = ascii_only(f"New lead: {who} ({what})")
    lines = []
    if lead["phone"]:
        lines.append(f"Phone: {lead['phone']}")
    if lead["email"]:
        lines.append(f"Email: {lead['email']}")
    pref = " / ".join(p for p in (lead["preferred_contact"], lead["preferred_time"]) if p)
    if pref:
        lines.append(f"Prefers: {pref}")
    if lead["details"]:
        lines.append("")
        lines.append(lead["details"][:600])
    body = "\n".join(lines) or "No contact details given."

    headers = {"Title": title, "Tags": "joystick", "Priority": "high"}
    actions = []
    phone = "".join(ch for ch in lead["phone"] if ch.isdigit() or ch == "+")
    if phone:
        actions.append(f"view, Call, tel:{phone}")
    if lead["email"]:
        actions.append(f"view, Email, mailto:{lead['email']}")
    if actions:
        headers["Actions"] = ascii_only("; ".join(actions))
        headers["Click"] = ascii_only((f"tel:{phone}" if phone else f"mailto:{lead['email']}"))

    req = urllib.request.Request(f"https://ntfy.sh/{TOPIC}", data=body.encode("utf-8"),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status


class Handler(BaseHTTPRequestHandler):
    server_version = "bcc_lead/1"

    def log_message(self, *a):  # quiet; we keep our own log
        pass

    def _reply(self, code: int, obj: dict) -> None:
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.rstrip("/") in ("/api/lead", "/health"):
            return self._reply(200, {"ok": True, "topic_set": bool(TOPIC)})
        self._reply(404, {"ok": False})

    def do_POST(self):
        if self.path.rstrip("/") != "/api/lead":
            return self._reply(404, {"ok": False})
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_BODY:
            return self._reply(413, {"ok": False, "error": "body size"})
        raw = self.rfile.read(n)
        try:
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            return self._reply(400, {"ok": False, "error": "json"})
        lead = normalize(payload)
        ip = self.headers.get("X-Real-IP") or self.client_address[0]
        if not (lead["email"] or lead["phone"] or lead["name"]):
            log(f"EMPTY from {ip}")
            return self._reply(400, {"ok": False, "error": "empty"})
        if lead["email"].lower().endswith("@example.com"):
            log(f"TEST  from {ip}: {json.dumps(lead)}")
            return self._reply(200, {"ok": True, "pushed": False, "test": True})
        if not rate_ok():
            log(f"RATE  from {ip}: dropped {json.dumps(lead)}")
            return self._reply(429, {"ok": False, "error": "rate"})
        try:
            status = push(lead)
            log(f"LEAD  from {ip} ntfy={status}: {json.dumps(lead)}")
            self._reply(200, {"ok": True, "pushed": status == 200})
        except Exception as e:  # noqa: BLE001 -- never lose the lead record
            log(f"FAIL  from {ip} {e!r}: {json.dumps(lead)}")
            self._reply(502, {"ok": False, "error": "ntfy"})


def main() -> None:
    log(f"start {HOST}:{PORT} topic_set={bool(TOPIC)}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
