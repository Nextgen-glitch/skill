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
- [ ] **Tier 3** — The ears & mouth (push-to-talk voice)
- [ ] **Tier 4** — The memory (survives restarts)
- [ ] **Tier 5** — The heartbeat (proactive, quiet by default)
- [ ] **Tier 6** — The rails (safety, confirmation, config, kill switch)

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

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The test suite exercises the agent loop against a fake provider, so it runs offline
without an API key.
