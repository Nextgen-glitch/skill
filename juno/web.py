"""A browser face for Juno — a thin web adapter over the SAME agent core.

Run: `python -m juno.web` then open the printed URL. A typed turn from the browser flows
through the very same `Agent.run_turn` the terminal uses — the web layer only changes how
turns arrive and leave.

If ANTHROPIC_API_KEY is set, the real Claude brain answers. If not, a small built-in
*demo brain* drives the real tool loop and memory deterministically, so the UI is fully
clickable without any key (try: "what's on my calendar today?", "find bike shops in
Zurich", "remember that I prefer morning meetings").
"""

from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterator

from juno.config import Config
from juno.llm import TextDelta, ToolUse, TurnResult


# --- demo brain: exercises the real loop without an API key ----------------------

class DemoProvider:
    """A keyword-driven stand-in for the model, so the browser is testable offline.

    It speaks the Provider seam: on a fresh user turn it may emit a tool_use; after a
    tool result comes back it produces a short, warm reply. Not intelligence — just
    enough to drive the real tool + memory machinery end to end.
    """

    _id = 0

    def stream_turn(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Iterator[TextDelta | TurnResult]:
        tool_names = {t["name"] for t in (tools or [])}
        last = messages[-1] if messages else {"role": "user", "content": ""}

        # Step 2: a tool just ran — summarize its result in a friendly line.
        if last.get("role") == "user" and isinstance(last.get("content"), list):
            result_text = ""
            for block in last["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    result_text = str(block.get("content", ""))
                    break
            reply = f"Here you go:\n\n{result_text}" if result_text else "Done."
            yield from self._stream_text(reply)
            return

        # Step 1: a fresh typed turn.
        text = last.get("content", "") if isinstance(last.get("content"), str) else ""
        low = text.lower().strip()

        if any(w in low for w in ("calendar", "schedule", "today", "my day", "agenda")) and "list_calendar_events" in tool_names:
            day = "tomorrow" if "tomorrow" in low else "today"
            yield self._tool("list_calendar_events", {"day": day})
            return

        if any(w in low for w in ("find", "search", "prospect", "lead", "business", "shops", "shop")) and "search_businesses" in tool_names:
            yield self._tool("search_businesses", {"niche": text.strip() or "businesses"})
            return

        if low.startswith("remember") and "remember" in tool_names:
            fact = text.split(" ", 1)[1].strip() if " " in text else text
            yield self._tool("remember", {"fact": fact})
            return

        # Otherwise, a plain warm reply (demo brain has no real reasoning).
        reply = (
            "I'm running in demo mode (no ANTHROPIC_API_KEY set), so I can show the tools "
            "and memory working but not reason freely. Try: “what's on my calendar "
            "today?”, “find bike shops in Zurich”, or “remember that I "
            "prefer morning meetings”."
        )
        yield from self._stream_text(reply)

    def _tool(self, name: str, tool_input: dict[str, Any]) -> TurnResult:
        DemoProvider._id += 1
        return TurnResult(
            text="", tool_uses=[ToolUse(id=f"demo-{DemoProvider._id}", name=name, input=tool_input)]
        )

    def _stream_text(self, text: str) -> Iterator[TextDelta | TurnResult]:
        for word in text.split(" "):
            yield TextDelta(word + " ")
        yield TurnResult(text=text)


# --- the page --------------------------------------------------------------------

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>__NAME__</title>
<style>
  :root { --bg:#faf7f2; --card:#fff; --ink:#2b2622; --muted:#8a817a; --accent:#c2703d; --line:#ece5dc; }
  * { box-sizing:border-box; }
  body { margin:0; font:16px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         background:var(--bg); color:var(--ink); height:100vh; display:flex; flex-direction:column; }
  header { padding:18px 22px; border-bottom:1px solid var(--line); display:flex; align-items:center; gap:12px; }
  .dot { width:11px; height:11px; border-radius:50%; background:var(--accent); box-shadow:0 0 0 4px rgba(194,112,61,.15); }
  header h1 { font-size:17px; margin:0; font-weight:650; }
  header .sub { color:var(--muted); font-size:13px; margin-left:auto; }
  #log { flex:1; overflow-y:auto; padding:24px; display:flex; flex-direction:column; gap:14px; max-width:760px; width:100%; margin:0 auto; }
  .msg { max-width:78%; padding:11px 15px; border-radius:16px; white-space:pre-wrap; word-wrap:break-word; }
  .you { align-self:flex-end; background:var(--accent); color:#fff; border-bottom-right-radius:5px; }
  .juno { align-self:flex-start; background:var(--card); border:1px solid var(--line); border-bottom-left-radius:5px; }
  .tool { align-self:flex-start; font-size:12.5px; color:var(--muted); background:transparent;
          border:1px dashed var(--line); border-radius:10px; padding:6px 10px; font-family:ui-monospace,Menlo,monospace; }
  form { display:flex; gap:10px; padding:16px 22px; border-top:1px solid var(--line); max-width:760px; width:100%; margin:0 auto; }
  input { flex:1; padding:12px 15px; border:1px solid var(--line); border-radius:12px; font-size:15px; outline:none; background:#fff; }
  input:focus { border-color:var(--accent); }
  button { padding:12px 18px; border:0; border-radius:12px; background:var(--accent); color:#fff; font-weight:600; cursor:pointer; }
  button:disabled { opacity:.5; cursor:default; }
</style>
</head>
<body>
  <header>
    <span class="dot"></span>
    <h1>__NAME__</h1>
    <span class="sub">__MODE__</span>
  </header>
  <div id="log">
    <div class="msg juno">__GREETING__</div>
  </div>
  <form id="f">
    <input id="m" autocomplete="off" placeholder="Message __NAME__…" autofocus/>
    <button id="b" type="submit">Send</button>
  </form>
<script>
  const log = document.getElementById('log'), form = document.getElementById('f'),
        input = document.getElementById('m'), btn = document.getElementById('b');
  function add(cls, text) {
    const d = document.createElement('div');
    d.className = 'msg ' + cls; d.textContent = text;
    log.appendChild(d); log.scrollTop = log.scrollHeight; return d;
  }
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim(); if (!text) return;
    add('you', text); input.value = ''; btn.disabled = true;
    const thinking = add('juno', '…');
    try {
      const r = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'},
                                          body: JSON.stringify({message: text})});
      const data = await r.json();
      thinking.remove();
      (data.tools || []).forEach(t => add('tool', '· ' + t.name + '(' + JSON.stringify(t.input) + ')'));
      add('juno', data.reply || '(no reply)');
    } catch (err) {
      thinking.textContent = '(could not reach the server)';
    } finally { btn.disabled = false; input.focus(); }
  });
</script>
</body>
</html>"""


class _Handler(BaseHTTPRequestHandler):
    agent = None
    lock = threading.Lock()
    name = "Juno"
    mode = "demo brain"
    greeting = "Hi, I'm Juno."

    def log_message(self, *args):  # quiet the default per-request stderr noise
        pass

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            # Token replacement (not str.format) so literal { } in the CSS/JS survive.
            html = (
                PAGE.replace("__NAME__", self.name)
                .replace("__MODE__", self.mode)
                .replace("__GREETING__", self.greeting)
            ).encode("utf-8")
            self._send(200, html, "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/chat":
            self._send(404, b"not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            message = str(payload.get("message", "")).strip()
        except (ValueError, json.JSONDecodeError):
            self._send(400, b'{"error":"bad request"}', "application/json")
            return

        tools: list[dict[str, Any]] = []
        # One shared brain + history; serialize turns so they don't interleave.
        with self.lock:
            reply = self.agent.run_turn(
                message,
                on_tool=lambda n, i, r: tools.append({"name": n, "input": i, "result": r}),
            )
        body = json.dumps({"reply": reply, "tools": tools}).encode("utf-8")
        self._send(200, body, "application/json")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(prog="juno-web", description="Juno browser face")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    config = Config.load()
    name = config.get("agent", "name", "Juno")

    # Import here to reuse the shared agent builder without a circular import at module load.
    from juno.main import _build_agent

    live = bool(os.environ.get("ANTHROPIC_API_KEY"))
    provider = None if live else DemoProvider()
    # Web confirmer denies consequential actions for now (a confirm UI is a follow-up);
    # the bundled stub tools are all read-only, so this doesn't block the demo.
    agent, _audit = _build_agent(config, confirmer=lambda n, i: False, provider=provider)

    _Handler.agent = agent
    _Handler.name = name
    _Handler.mode = "live brain (Claude)" if live else "demo brain — set ANTHROPIC_API_KEY for the real model"
    _Handler.greeting = (
        f"Hi, I'm {name}. Ask me what's on your calendar, to find businesses in a niche, "
        "or to remember something about you."
    )

    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    shown_host = "localhost" if args.host in ("0.0.0.0", "127.0.0.1") else args.host
    print(f"{name} web face running at http://{shown_host}:{args.port}  ({_Handler.mode})")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
