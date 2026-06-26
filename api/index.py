"""Vercel serverless entrypoint — Juno's browser face, hosted.

A single Python function that serves the chat page (GET) and the chat endpoint (POST),
routed by HTTP method so it works behind a catch-all rewrite. It reuses the SAME agent
core as the terminal and the local web face — only the front door changes.

Serverless notes:
  - The filesystem is read-only except /tmp, so memory + audit are pointed there.
  - There is no background heartbeat here (serverless has no long-lived process); the
    heartbeat lives in the local/always-on runtime. This face is chat + tools + memory.
  - With ANTHROPIC_API_KEY set in the Vercel project, the real Claude brain answers;
    otherwise the built-in demo brain drives the real tool loop so the page still works.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler

# Make the repo root importable and force-bundle dynamically-imported modules so
# Vercel's import tracer ships them.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import juno.agent  # noqa: E402,F401
import juno.audit  # noqa: E402,F401
import juno.llm  # noqa: E402,F401
import juno.memory  # noqa: E402,F401
import juno.safety  # noqa: E402,F401
import juno.tools.calendar_tools  # noqa: E402,F401
import juno.tools.memory_tools  # noqa: E402,F401
import juno.tools.prospecting_tools  # noqa: E402,F401
import juno.tools.registry  # noqa: E402,F401
from juno.config import Config  # noqa: E402
from juno.main import _build_agent  # noqa: E402
from juno.web import PAGE, DemoProvider, handle_chat, synthesize  # noqa: E402

# Config built inline (no config.toml read at runtime), with state under /tmp.
CONFIG_DATA = {
    "agent": {
        "name": "Juno",
        "persona": "warm, plain-spoken, and brief",
        "purpose": (
            "a personal prospecting & outreach assistant — finds businesses in a niche "
            "I describe, drafts outreach emails for review, and helps manage my calendar"
        ),
    },
    "model": {
        "provider": "anthropic",
        "name": "claude-opus-4-8",
        "max_tokens": 2048,
        "temperature": 1.0,
        "max_retries": 4,
        "request_timeout_seconds": 60,
    },
    "memory": {"store_path": "/tmp/juno-memory.json", "max_facts_in_prompt": 100},
    "voice": {
        "elevenlabs_voice_id": "UgBBYS2sOqTuMpoF3BR0",
        "elevenlabs_model": "eleven_turbo_v2_5",
    },
    "safety": {
        "confirm_required_tools": [
            "send_email",
            "send_message",
            "enrich_businesses",
            "create_event",
            "delete_event",
            "delete_data",
            "change_setting",
        ],
        "audit_log_path": "/tmp/juno-audit.jsonl",
    },
    "pricing": {},
}

_config = Config(CONFIG_DATA)
_live = bool(os.environ.get("ANTHROPIC_API_KEY"))
_provider = None if _live else DemoProvider()
# Web confirmer denies consequential actions (a confirm UI is a follow-up); the bundled
# tools are read-only, so this never blocks the demo.
_agent, _audit = _build_agent(_config, confirmer=lambda n, i: False, provider=_provider)
_lock = threading.Lock()

_VOICE = _config.section("voice")
_ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY")
_VOICE_ID = _VOICE.get("elevenlabs_voice_id", "")
_ELEVEN_MODEL = _VOICE.get("elevenlabs_model", "eleven_turbo_v2_5")

NAME = "Juno"
MODE = "live brain (Claude)" if _live else "demo brain — set ANTHROPIC_API_KEY in Vercel for the real model"
GREETING = (
    f"Hi, I'm {NAME}. Ask me what's on your calendar, to find businesses in a niche, "
    "or to remember something about you."
)


class handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the function logs quiet
        pass

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        html = (
            PAGE.replace("__NAME__", NAME)
            .replace("__MODE__", MODE)
            .replace("__GREETING__", GREETING)
        ).encode("utf-8")
        self._send(200, html, "text/html; charset=utf-8")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send(400, b'{"error":"bad request"}', "application/json")
            return

        # One endpoint, action-routed: "speak" returns audio (or 503), else chat JSON.
        if payload.get("action") == "speak":
            audio = synthesize(
                str(payload.get("text", "")), _ELEVEN_KEY, _VOICE_ID, _ELEVEN_MODEL
            )
            if audio:
                self._send(200, audio, "audio/mpeg")
            else:
                self._send(503, b'{"fallback":true}', "application/json")
            return

        message = str(payload.get("message", "")).strip()
        with _lock:
            result = handle_chat(_agent, message)
        self._send(200, json.dumps(result).encode("utf-8"), "application/json")
