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


# --- shared request helpers (used by the local server AND the Vercel function) ----

def handle_chat(agent, message: str) -> dict[str, Any]:
    """Run one turn through the shared agent core, collecting any tool calls."""
    tools: list[dict[str, Any]] = []
    reply = agent.run_turn(
        message, on_tool=lambda n, i, r: tools.append({"name": n, "input": i, "result": r})
    )
    return {"reply": reply, "tools": tools}


def synthesize(text: str, api_key: str | None, voice_id: str | None, model: str) -> bytes | None:
    """ElevenLabs speech as MP3 bytes, or None to signal the page to use browser speech."""
    if not api_key or not voice_id or not text.strip():
        return None
    try:
        from juno.voice.tts import synthesize_bytes

        return synthesize_bytes(text, api_key=api_key, voice_id=voice_id, model=model)
    except Exception:  # noqa: BLE001 - any failure -> fall back to browser speech
        return None


def _decode_audio(b64: str) -> bytes:
    """Decode the page's base64 audio payload; empty/invalid -> empty bytes (a probe)."""
    import base64

    try:
        return base64.b64decode(b64) if b64 else b""
    except (ValueError, TypeError):
        return b""


def transcribe(audio: bytes, api_key: str | None, model: str, mimetype: str) -> str | None:
    """Deepgram transcript for recorded audio, or None if Deepgram isn't available.

    Empty audio with a key present returns "" (used by the page to probe availability).
    """
    if not api_key:
        return None
    if not audio:
        return ""
    try:
        from juno.voice.stt import transcribe_bytes

        return transcribe_bytes(audio, api_key=api_key, model=model, mimetype=mimetype)
    except Exception:  # noqa: BLE001 - any failure -> page falls back to browser speech
        return None


# --- the page --------------------------------------------------------------------

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>__NAME__</title>
<style>
  :root { --cyan:#2fd4ff; --ink:#cfe9f5; --muted:#5d7488; }
  * { box-sizing:border-box; }
  html,body { margin:0; height:100%; }
  body { font:16px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; color:var(--ink);
         background:radial-gradient(120% 120% at 50% 35%, #0a1626 0%, #060b14 55%, #03060b 100%);
         overflow:hidden; }
  #top { position:fixed; top:16px; left:20px; right:20px; display:flex; align-items:center; gap:10px; z-index:5; }
  #top .nm { font-weight:700; letter-spacing:.14em; text-transform:uppercase; font-size:14px; }
  #top .md { margin-left:auto; font-size:12px; color:var(--muted); }
  #stage { position:fixed; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; }
  canvas { display:block; }
  #state { letter-spacing:.32em; text-transform:uppercase; font-size:12px; color:var(--cyan);
           opacity:.85; height:16px; }
  #caps { width:min(680px,88vw); text-align:center; margin-top:10px; min-height:84px; }
  #you { color:var(--muted); font-size:15px; min-height:22px; }
  #juno { color:#eaf6ff; font-size:19px; font-weight:500; margin-top:6px; min-height:26px;
          text-shadow:0 0 18px rgba(47,212,255,.25); }
  #chips { display:flex; flex-wrap:wrap; gap:6px; justify-content:center; margin-top:10px; min-height:22px; }
  .chip { font:12px ui-monospace,Menlo,monospace; color:#8fd0e8; border:1px solid rgba(47,212,255,.25);
          border-radius:9px; padding:3px 8px; background:rgba(47,212,255,.05); }
  #bar { position:fixed; bottom:22px; left:0; right:0; display:flex; gap:10px; justify-content:center; align-items:center; z-index:5; }
  .pill { border:1px solid rgba(47,212,255,.3); background:rgba(47,212,255,.06); color:var(--ink);
          border-radius:999px; padding:10px 16px; cursor:pointer; font-size:14px; }
  .pill:hover { background:rgba(47,212,255,.14); }
  #textwrap { display:none; gap:8px; }
  #textwrap.show { display:flex; }
  #text { width:min(420px,70vw); padding:10px 14px; border-radius:999px; border:1px solid rgba(47,212,255,.3);
          background:#091420; color:var(--ink); outline:none; font-size:15px; }
  #overlay { position:fixed; inset:0; z-index:20; display:flex; flex-direction:column; align-items:center;
             justify-content:center; gap:18px; background:rgba(3,6,11,.78); backdrop-filter:blur(3px); }
  #overlay h2 { margin:0; font-weight:600; letter-spacing:.05em; }
  #overlay p { margin:0; color:var(--muted); max-width:420px; text-align:center; }
  #go { padding:14px 30px; font-size:16px; border-radius:999px; border:1px solid var(--cyan);
        background:rgba(47,212,255,.12); color:#eaf6ff; cursor:pointer; }
  #go:hover { background:rgba(47,212,255,.22); }
</style>
</head>
<body>
  <div id="top"><span class="nm">__NAME__</span><span class="md">__MODE__</span></div>
  <div id="stage">
    <canvas id="orb" width="320" height="320"></canvas>
    <div id="state">idle</div>
    <div id="caps">
      <div id="you"></div>
      <div id="juno">__GREETING__</div>
      <div id="chips"></div>
    </div>
  </div>
  <div id="bar">
    <button id="mic" class="pill">🎙 listening</button>
    <button id="kbd" class="pill">⌨</button>
    <div id="textwrap"><input id="text" placeholder="type instead…" autocomplete="off"/></div>
  </div>
  <div id="overlay">
    <h2>__NAME__</h2>
    <p>Tap to start, then just talk. __NAME__ listens, thinks, and speaks back. Tap the orb to interrupt.</p>
    <button id="go">Tap to start</button>
  </div>
<script>
(function(){
  const NAME = "__NAME__";
  const el = (id)=>document.getElementById(id);
  const youEl = el('you'), junoEl = el('juno'), chipsEl = el('chips'), stateEl = el('state');

  // ---- orb animation ----
  const cv = el('orb'), ctx = cv.getContext('2d');
  const DPR = Math.min(window.devicePixelRatio||1, 2);
  function size(){ const s=Math.min(340, Math.min(window.innerWidth,window.innerHeight)*0.6);
    cv.width=s*DPR; cv.height=s*DPR; cv.style.width=s+'px'; cv.style.height=s+'px'; }
  size(); window.addEventListener('resize', size);
  const STATE = { value:'idle' };
  const cfg = {
    idle:      {speed:0.4, glow:0.45, jitter:0.02},
    listening: {speed:0.8, glow:0.8,  jitter:0.10},
    thinking:  {speed:2.2, glow:0.7,  jitter:0.05},
    speaking:  {speed:1.4, glow:1.0,  jitter:0.22},
  };
  let t=0;
  function draw(){
    t += 0.016;
    const c = cfg[STATE.value] || cfg.idle;
    const w=cv.width, h=cv.height, cx=w/2, cy=h/2;
    const R = Math.min(w,h)*0.30;
    ctx.clearRect(0,0,w,h);
    // outer glow
    const pulse = 1 + Math.sin(t*c.speed)*0.05 + (STATE.value==='speaking'?Math.sin(t*9)*c.jitter*0.4:0);
    const g = ctx.createRadialGradient(cx,cy,R*0.2, cx,cy,R*1.9);
    g.addColorStop(0, 'rgba(47,212,255,'+(0.28*c.glow)+')');
    g.addColorStop(1, 'rgba(47,212,255,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,w,h);
    // particle rings
    ctx.save(); ctx.translate(cx,cy);
    for(let ring=0; ring<4; ring++){
      const rr = R*(0.6+ring*0.22)*pulse;
      const n = 26+ring*10;
      const dir = ring%2? -1:1;
      const rot = t*c.speed*0.5*dir + ring;
      for(let i=0;i<n;i++){
        const a = (i/n)*Math.PI*2 + rot;
        const jig = 1 + Math.sin(t*3 + i*1.7 + ring)*c.jitter;
        const x = Math.cos(a)*rr*jig, y = Math.sin(a)*rr*jig;
        const dotR = (ring===0?2.2:1.6)*DPR;
        ctx.beginPath(); ctx.arc(x,y,dotR,0,Math.PI*2);
        ctx.fillStyle='rgba('+(140+ring*20)+',225,255,'+(0.5*c.glow)+')';
        ctx.shadowBlur=10*DPR; ctx.shadowColor='rgba(47,212,255,'+c.glow+')';
        ctx.fill();
      }
    }
    // core
    ctx.shadowBlur=30*DPR; ctx.shadowColor='rgba(47,212,255,'+c.glow+')';
    ctx.beginPath(); ctx.arc(0,0,R*0.5*pulse,0,Math.PI*2);
    const cg = ctx.createRadialGradient(0,0,0, 0,0,R*0.5*pulse);
    cg.addColorStop(0,'rgba(190,240,255,'+(0.9*c.glow)+')');
    cg.addColorStop(1,'rgba(47,160,220,'+(0.15*c.glow)+')');
    ctx.fillStyle=cg; ctx.fill();
    ctx.restore();
    requestAnimationFrame(draw);
  }
  draw();
  function setState(s){ STATE.value=s; stateEl.textContent=s; }

  // ---- captions ----
  function showYou(text){ youEl.textContent = text ? 'you: '+text : ''; }
  function showJuno(text){ junoEl.textContent = text; }
  function showChips(tools){ chipsEl.innerHTML='';
    (tools||[]).forEach(tl=>{ const d=document.createElement('span'); d.className='chip';
      d.textContent='· '+tl.name; chipsEl.appendChild(d); }); }

  // ---- audio out (ElevenLabs endpoint, fallback to browser speech) ----
  let curAudio=null;
  function stopSpeaking(){ try{ if(curAudio){curAudio.pause(); curAudio=null;} }catch(e){}
    try{ window.speechSynthesis && speechSynthesis.cancel(); }catch(e){} }
  function browserSpeak(text){ return new Promise(res=>{
    if(!('speechSynthesis' in window)) return res();
    const u=new SpeechSynthesisUtterance(text); u.rate=1.02; u.onend=res; u.onerror=res;
    speechSynthesis.speak(u); }); }
  async function speak(text){
    if(!text) return;
    try{
      const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({action:'speak',text})});
      if(r.ok && (r.headers.get('Content-Type')||'').indexOf('audio')>=0){
        const blob=await r.blob(); const url=URL.createObjectURL(blob);
        await new Promise(res=>{ curAudio=new Audio(url); curAudio.onended=res; curAudio.onerror=res;
          curAudio.play().catch(res); });
        curAudio=null; URL.revokeObjectURL(url); return;
      }
    }catch(e){}
    await browserSpeak(text); // 503 / no key / error -> browser voice
  }

  // ---- shared state ----
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const app = { active:false, busy:false, muted:false, mode:'none', rec:null, recognizing:false,
                stream:null, recorder:null, chunks:[], recording:false, hadSpeech:false, silenceAt:0 };

  // A turn: think, speak, then resume listening. Assumes app.busy is already set true
  // and input has been paused (so Juno never transcribes its own voice).
  async function respond(text){
    stopSpeaking(); setState('thinking'); showYou(text); showJuno('…'); showChips([]);
    try{
      const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({action:'chat',message:text})});
      const data=await r.json();
      showChips(data.tools); showJuno(data.reply||'(no reply)');
      setState('speaking'); await speak(data.reply||'');
    }catch(e){ showJuno('(could not reach '+NAME+')'); }
    app.busy=false;
    if(!app.active || app.muted){ setState('idle'); return; }
    setState('listening');
    if(app.mode==='webspeech') startListening();   // deepgram VAD resumes on its own
  }
  function beginTurn(text){ if(app.busy || !text) return; app.busy=true;
    if(app.mode==='webspeech'){ try{ app.rec && app.rec.stop(); }catch(e){} } respond(text); }

  // ---- input mode A: Deepgram (MediaRecorder + voice-activity detection) ----
  const SILENCE_MS=900, SPEECH_RMS=0.018, MIN_BYTES=1600;
  function pickMime(){ for(const m of ['audio/webm;codecs=opus','audio/webm','audio/ogg']){
    if(window.MediaRecorder && MediaRecorder.isTypeSupported(m)) return m; } return ''; }
  function blobToB64(blob){ return new Promise(res=>{ const r=new FileReader();
    r.onloadend=()=>res(String(r.result).split(',')[1]||''); r.readAsDataURL(blob); }); }
  async function startDeepgram(){
    app.stream=await navigator.mediaDevices.getUserMedia({audio:true});
    const ac=new (window.AudioContext||window.webkitAudioContext)();
    const an=ac.createAnalyser(); an.fftSize=2048; ac.createMediaStreamSource(app.stream).connect(an);
    const buf=new Uint8Array(an.fftSize);
    (function vad(){ requestAnimationFrame(vad);
      if(!app.active || app.busy || app.muted) return;   // paused while thinking/speaking
      an.getByteTimeDomainData(buf);
      let s=0; for(let i=0;i<buf.length;i++){ const v=(buf[i]-128)/128; s+=v*v; }
      const rms=Math.sqrt(s/buf.length), now=performance.now();
      if(rms>SPEECH_RMS){ if(!app.recording) startRec(); app.hadSpeech=true; app.silenceAt=0; }
      else if(app.recording && app.hadSpeech){ if(!app.silenceAt) app.silenceAt=now;
        else if(now-app.silenceAt>SILENCE_MS) stopRec(); }
    })();
  }
  function startRec(){ app.chunks=[]; app.recording=true; app.hadSpeech=false; app.silenceAt=0;
    const mt=pickMime();
    app.recorder = mt ? new MediaRecorder(app.stream,{mimeType:mt}) : new MediaRecorder(app.stream);
    app.recorder.ondataavailable=e=>{ if(e.data && e.data.size) app.chunks.push(e.data); };
    app.recorder.onstop=onRecStop; app.recorder.start(); }
  function stopRec(){ if(app.recording){ app.busy=true; app.recording=false;
    try{ app.recorder.stop(); }catch(e){ app.busy=false; } } }
  async function onRecStop(){
    const blob=new Blob(app.chunks,{type:app.recorder.mimeType||'audio/webm'});
    if(blob.size<MIN_BYTES){ app.busy=false; if(!app.muted) setState('listening'); return; }
    setState('thinking');
    let text='';
    try{ const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({action:'transcribe',audio:await blobToB64(blob),
                             mimetype:app.recorder.mimeType||'audio/webm'})});
      if(r.ok){ const d=await r.json(); text=(d.text||'').trim(); } }catch(e){}
    if(!text){ app.busy=false; if(!app.muted) setState('listening'); return; }
    await respond(text);   // app.busy already true
  }

  // ---- input mode B: browser Web Speech (fallback) ----
  function buildRec(){ const rec=new SR(); rec.continuous=true; rec.interimResults=true; rec.lang='en-US';
    rec.onstart=()=>{ app.recognizing=true; };
    rec.onend=()=>{ app.recognizing=false; if(app.active&&!app.busy&&!app.muted){ try{ rec.start(); }catch(e){} } };
    rec.onresult=(e)=>{ if(app.busy||app.muted) return; let interim='',final='';
      for(let i=e.resultIndex;i<e.results.length;i++){ const r=e.results[i];
        if(r.isFinal) final+=r[0].transcript; else interim+=r[0].transcript; }
      if(interim) showYou(interim.trim());
      const text=final.trim(); if(text) beginTurn(text); };
    return rec; }
  function startListening(){ if(app.mode!=='webspeech'||!app.rec||app.recognizing) return;
    try{ app.rec.start(); }catch(e){} }

  // ---- choose the input mode after the start gesture ----
  async function deepgramAvailable(){
    try{ const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'transcribe',audio:''})}); return r.ok; }catch(e){ return false; } }
  async function startSession(){
    app.active=true;
    if(navigator.mediaDevices && window.MediaRecorder && await deepgramAvailable()){
      try{ await startDeepgram(); app.mode='deepgram'; setState('listening'); return; }catch(e){}
    }
    if(SR){ app.mode='webspeech'; app.rec=buildRec(); setState('listening'); startListening(); return; }
    app.mode='none'; app.muted=true; el('mic').textContent='🔇 no mic';
    showJuno('Voice needs Chrome or a mic. Use the ⌨ text box to chat with '+NAME+'.');
    el('textwrap').classList.add('show'); setState('idle');
  }

  // ---- controls ----
  el('orb').addEventListener('click', ()=>{ if(app.busy) stopSpeaking(); }); // tap orb to interrupt
  el('mic').addEventListener('click', ()=>{ app.muted=!app.muted;
    el('mic').textContent = app.muted ? '🔇 muted' : '🎙 listening';
    if(app.muted){ try{ app.rec && app.rec.stop(); }catch(e){} setState('idle'); }
    else if(app.active && !app.busy){ setState('listening'); startListening(); } });
  el('kbd').addEventListener('click', ()=> el('textwrap').classList.toggle('show'));
  el('text').addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ const v=e.target.value.trim();
    if(v){ e.target.value=''; beginTurn(v); } } });

  // ---- start gesture (unlocks mic + audio) ----
  el('go').addEventListener('click', ()=>{ el('overlay').style.display='none';
    try{ const u=new SpeechSynthesisUtterance(''); speechSynthesis.speak(u); }catch(e){}
    startSession();
  });
})();
</script>
</body>
</html>"""


class _Handler(BaseHTTPRequestHandler):
    agent = None
    lock = threading.Lock()
    name = "Juno"
    mode = "demo brain"
    greeting = "Hi, I'm Juno."
    eleven_key = None
    voice_id = ""
    eleven_model = "eleven_turbo_v2_5"
    deepgram_key = None
    deepgram_model = "nova-2"

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
        if self.path not in ("/api/chat", "/index"):
            self._send(404, b"not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send(400, b'{"error":"bad request"}', "application/json")
            return

        # One endpoint, action-routed.
        action = payload.get("action")
        if action == "speak":
            audio = synthesize(
                str(payload.get("text", "")), self.eleven_key, self.voice_id, self.eleven_model
            )
            if audio:
                self._send(200, audio, "audio/mpeg")
            else:
                self._send(503, b'{"fallback":true}', "application/json")
            return

        if action == "transcribe":
            text = transcribe(
                _decode_audio(payload.get("audio", "")),
                self.deepgram_key,
                self.deepgram_model,
                str(payload.get("mimetype", "audio/webm")),
            )
            if text is None:  # no Deepgram -> page falls back to browser speech
                self._send(503, b'{"fallback":true}', "application/json")
            else:
                self._send(200, json.dumps({"text": text}).encode("utf-8"), "application/json")
            return

        message = str(payload.get("message", "")).strip()
        with self.lock:  # one shared brain + history; serialize turns
            result = handle_chat(self.agent, message)
        self._send(200, json.dumps(result).encode("utf-8"), "application/json")


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

    voice = config.section("voice")
    _Handler.agent = agent
    _Handler.name = name
    _Handler.mode = "live brain (Claude)" if live else "demo brain — set ANTHROPIC_API_KEY for the real model"
    _Handler.greeting = f"Tap to start, then talk to {name}."
    _Handler.eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    _Handler.voice_id = voice.get("elevenlabs_voice_id", "")
    _Handler.eleven_model = voice.get("elevenlabs_model", "eleven_turbo_v2_5")
    _Handler.deepgram_key = os.environ.get("DEEPGRAM_API_KEY")
    _Handler.deepgram_model = voice.get("deepgram_model", "nova-2")

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
