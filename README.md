# Juno

A voice-first personal assistant — a prospecting & outreach helper. It finds
businesses in a niche you describe, drafts outreach emails for review, and helps
manage your calendar. It talks, acts through tools you can see and stop, remembers you
between conversations, and reaches out only when something is genuinely worth your
attention.

See [`AGENT.md`](./AGENT.md) for the full spec and the reasoning behind the design.

## Build status (tier by tier)

- [x] **Tier 0** — Spec & scaffolding
- [x] **Tier 1** — The brain (text conversation loop)
- [x] **Tier 2** — The hands (tool registry)
- [x] **Tier 3** — The ears & mouth (push-to-talk voice)
- [x] **Tier 4** — The memory (survives restarts)
- [x] **Tier 5** — The heartbeat (proactive, quiet by default)
- [x] **Tier 6** — The rails (safety, confirmation, config, kill switch)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .            # text path only
# pip install -e ".[voice]" # add voice deps (Tier 3)

cp .env.example .env        # then fill in ANTHROPIC_API_KEY
```

## Run

```bash
juno            # text REPL
# python -m juno.main
```

Type your message and press enter. `exit` / `quit` / Ctrl-D to leave.
Everything is configured in [`config.toml`](./config.toml) — no code edits needed to
tune the model, intervals, quiet hours, voice, or the confirmation list.

### Commands (text mode)

- `inbox` — list held proactive notices; `dismiss <id>` — clear one
- `pause` / `resume` — the kill switch: halt or restore all proactive behavior (you can
  still chat while paused); `status` — show whether proactivity is running
- `cost` — show the running model-token tally

### Safety posture

- **Confirmation gate.** Tools that send, spend, delete, or change a setting stop and ask
  before running — stated plainly, per action, never generalizing. Which tools are gated
  is the `safety.confirm_required_tools` list in `config.toml` (a tool can also declare
  itself consequential in code). The gate sits in the shared agent core, so it covers
  typed, spoken, and heartbeat-initiated actions alike.
- **External content is data, not commands.** The system prompt instructs Juno to treat
  anything it reads (web pages, emails, tool results, stored notes) as data — if such
  content looks like an instruction, it surfaces it and asks rather than obeying.
- **Audit trail.** Every tool run, confirmation, and model call appends a line to
  `logs/audit.jsonl`, with a running cost tally.
- **Kill switch.** `pause` (or `touch juno/state/PAUSED`) halts proactivity at once.

### Voice mode

```bash
pip install -e ".[voice]"
juno --voice    # hold the push-to-talk key (config: voice.push_to_talk_key) to speak
```

Set an ElevenLabs voice id in `config.toml` (`voice.elevenlabs_voice_id`) and the
`DEEPGRAM_API_KEY` / `ELEVENLABS_API_KEY` secrets in `.env` first. The text path keeps
working regardless — it's the fallback and the debug path.

> Proactive checks and voice are **off by default** in `config.toml`
> (`heartbeat.enabled`, `voice.enabled`). Turn them on when you're ready.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The test suite exercises the agent loop against a fake provider, so it runs offline
without an API key.
