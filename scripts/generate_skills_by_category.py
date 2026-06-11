#!/usr/bin/env python3
"""Group all installed skills into functional categories.

There is no category field in SKILL.md frontmatter, so categories are derived
from each skill's name + description using an ordered keyword rule set
(first match wins; specific rules are listed before generic ones). Anything
unmatched lands in "Other / Miscellaneous" so nothing is silently mis-filed.
"""
from __future__ import annotations

import re
import datetime
from pathlib import Path

SKILLS_DIR = Path(".claude/skills")
OUT = Path("INSTALLED_SKILLS_BY_CATEGORY.md")
MAX_LEN = 170

# Ordered list of (category, [keywords]). Matched against "name + description",
# lowercased. First category with any keyword hit wins, so put narrow/specific
# categories before broad ones.
RULES: list[tuple[str, list[str]]] = [
    ("AI Agents, LLM & Prompting", [
        "agent", "llm", "prompt", "rag", "langchain", "langgraph", "crewai",
        "mcp", "multi-agent", "subagent", "embedding", "vector-database",
        "vector-index", "voice-agent", "voice-ai", "pydantic-ai", "copilot",
        "computer-use", "autonomous", "ai-engineer", "ai-agent", "ai-ml",
        "ai-native", "ai-wrapper", "evaluation", "eval", "context-", "memory",
        "transformers", "hugging-face", "gemini-api", "claude-api", "ai-studio",
        "ai-analyzer", "anti-sycophancy", "reasoning", "tool-use", "tool-design",
    ]),
    ("Security & Pentesting", [
        "security", "pentest", "penetration", "vuln", "exploit", "owasp",
        "threat", "malware", "forensic", "red-team", "red team", "blue team",
        "burp", "metasploit", "sqlmap", "ffuf", "shodan", "reverse-engineer",
        "reversing", "privilege-escalation", "xss", "injection", "csrf", "idor",
        "fuzzing", "hardening", "secrets-management", "auth", "broken-auth",
        "semgrep", "sast", "compliance", "gdpr", "pci", "zeroize", "constant-time",
        "cred-", "ethical-hacking", "active-directory", "ssh-pen", "smtp-pen",
        "wireshark", "scanning", "attack", "stride", "mtls", "memory-safety",
        "binary-analysis", "firmware", "anti-reversing", "path-traversal",
    ]),
    ("Cloud SDKs (Azure / AWS / GCP)", [
        "azure-", "aws-", "gcp-", "azd-", "cloudformation", "terraform",
        "cloud-run", "serverless", "lambda-", "cdk-", "azure ", "amazon-alexa",
    ]),
    ("DevOps, Infra & Observability", [
        "devops", "kubernetes", "k8s", "docker", "helm", "terraform",
        "infrastructure", "cicd", "ci/cd", "ci-cd", "gitops", "deployment",
        "deploy", "incident", "observability", "monitoring", "prometheus",
        "grafana", "datadog", "sentry-auto", "pagerduty", "istio", "linkerd",
        "service-mesh", "sre", "on-call", "runbook", "slo", "tracing", "logging",
        "cloud-architect", "cloud-devops", "network-engineer", "network-101",
        "hybrid-cloud", "bazel", "turborepo", "nx-workspace", "monorepo",
        "mise-", "devcontainer", "github-actions", "gitlab-ci", "circleci",
        "cost-optim", "cost-clean", "finops", "render-auto", "appdeploy",
    ]),
    ("Databases & Data Stores", [
        "postgres", "postgresql", "mysql", "sql-", "sql ", "nosql", "mongodb",
        "database", "drizzle", "prisma", "neon", "supabase", "snowflake",
        "clickhouse", "redis", "cosmos", "sqlite", "convex", "firebase",
        "event-store", "event-sourcing", "cqrs", "migration", "orm",
    ]),
    ("Data Engineering, ML & Science", [
        "data-engineer", "data-pipeline", "data-quality", "airflow", "dbt",
        "spark", "polars", "pandas", "numpy", "scipy", "scikit", "matplotlib",
        "seaborn", "plotly", "statsmodels", "scanpy", "biopython", "astropy",
        "networkx", "sympy", "qiskit", "cirq", "ml-engineer", "ml-pipeline",
        "mlops", "machine-learning", "ml-ops", "data-scientist", "recsys",
        "backtesting", "quant", "monte-carlo", "analytics", "amplitude",
        "mixpanel", "segment", "data-driven", "data-storytelling", "data-struct",
        "uniprot", "pubmed", "scientific", "latex-paper", "citation",
        "computer-vision", "news-sentiment", "stock-research", "equity",
    ]),
    ("Web Frontend & UI Frameworks", [
        "react", "next", "nextjs", "vue", "svelte", "sveltekit", "angular",
        "astro", "remotion", "tailwind", "shadcn", "radix", "frontend",
        "three", "threejs", "webgl", "spline", "makepad", "robius", "animejs",
        "magic-ui", "magic-animator", "css", "html", "progressive-web",
        "browser-extension", "chrome-extension", "web-artifacts", "satori",
        "favicon", "scroll-experience", "view-transition", "tanstack",
        "zustand", "state-management", "component", "ui-pattern", "react-flow",
        "javascript-mastery", "modern-javascript", "vercel-ai-sdk",
    ]),
    ("Design & UX", [
        "ui-ux", "ux-", "design", "figma", "canva", "photopea", "vizcom",
        "stitch", "brand-guideline", "brand-perception", "typography",
        "color-palette", "iconsax", "minimalist-ui", "industrial-brutalist",
        "high-end-visual", "visual-emotion", "mobile-design", "product-design",
        "frontend-design", "baseline-ui", "accessibility", "a11y", "wcag",
        "screen-reader", "accesslint", "theme-factory", "canvas-design",
        "uxui", "interactive-portfolio", "emotional-arc",
    ]),
    ("Mobile Development", [
        "ios", "android", "swift", "swiftui", "flutter", "react-native",
        "expo", "jetpack-compose", "mobile-developer", "mobile-security",
        "kotlin", "hig-", "building-native-ui", "native-data-fetching",
        "macos", "telegram-mini-app", "avalonia",
    ]),
    ("Backend & APIs", [
        "backend", "fastapi", "django", "flask", "express", "nestjs", "hono",
        "node", "nodejs", "graphql", "grpc", "trpc", "rest", "api-", "api ",
        "openapi", "webhook", "microservice", "saga", "bullmq", "inngest",
        "trigger-dev", "temporal", "dbos", "upstash", "laravel", "rails",
        "ruby", "php-", "dotnet", "csharp", "java-pro", "golang", "go-",
        "rust-", "elixir", "scala", "haskell", "julia", "c-pro", "cpp-",
        "payment", "stripe-integration", "paypal", "plaid", "billing",
        "auth-implementation", "clerk-auth", "x402", "event-staffing",
        "typescript", "zod", "fp-", "async-python", "python-pro",
        "python-development", "python-fastapi", "python-performance",
    ]),
    ("Testing & QA", [
        "test", "testing", "tdd", "bdd", "qa", "playwright", "cypress",
        "e2e", "k6-load", "load-testing", "bats", "webapp-testing", "fuzz",
        "find-bugs", "bug-hunter", "mock-hunter", "debug", "debugger",
        "debugging", "lint", "shellcheck", "validate", "verification",
        "acceptance", "lambdatest", "ui-visual-validator",
    ]),
    ("SEO, Marketing & Growth", [
        "seo", "aeo", "geo-fundamental", "marketing", "growth", "ads",
        "ad-creative", "campaign", "cold-email", "email-sequence", "copywriting",
        "copy-editing", "headline", "landing-page", "lead-magnet", "lead-gen",
        "cro", "conversion", "funnel", "churn", "referral", "paywall", "pricing",
        "price-psychology", "social-proof", "scarcity", "objection", "persuasion",
        "psychograph", "competitive", "competitor", "market-sizing", "launch-strategy",
        "app-store-optim", "schema-markup", "programmatic-seo", "content-market",
        "content-strateg", "content-creator", "social-content", "social-post",
        "social-orchestrator", "social-metadata", "subject-line", "sequence-psych",
        "awareness-stage", "monetization", "free-tool-strategy", "revops",
        "sales-", "klaviyo", "mailchimp", "convertkit", "brevo", "activecampaign",
        "sendgrid", "postmark", "paid-ads", "x-article", "wechat-official",
        "xiaohongshu", "instagram", "tiktok", "linkedin-content", "linkedin-profile",
    ]),
    ("Content, Writing & Docs", [
        "writing", "write", "prose", "proofread", "blog", "article", "wiki",
        "documentation", "doc-", "docs-", "readme", "changelog", "tutorial",
        "reference-builder", "technical-change", "internal-comms", "ux-copy",
        "humanize", "avoid-ai-writing", "unslop", "beautiful-prose", "explain-like",
        "podcast", "notebooklm", "obsidian", "markdown", "latex", "doc2math",
        "scientific-writing", "postmortem-writing", "translation", "i18n",
        "localization", "json-canvas", "diary", "presentation", "slides", "ppt",
        "pptx", "docx", "xlsx", "pdf", "2slides", "nanobanana",
    ]),
    ("Productivity, SaaS & Integrations", [
        "automation", "zapier", "make-auto", "n8n", "notion", "slack", "discord",
        "telegram", "whatsapp", "jira", "asana", "trello", "monday", "clickup",
        "linear", "basecamp", "airtable", "google-sheet", "googlesheets",
        "google-doc", "google-drive", "google-slide", "google-calendar",
        "google-analytics", "gmail", "outlook", "one-drive", "dropbox", "box-auto",
        "salesforce", "hubspot", "pipedrive", "close-auto", "zoho", "zendesk",
        "freshdesk", "freshservice", "intercom", "helpdesk", "helium", "twilio",
        "calendly", "cal-com", "docusign", "confluence", "bitbucket", "gitlab-auto",
        "bamboohr", "wrike", "todoist", "coda", "miro", "webflow", "zoom-auto",
        "microsoft-teams", "posthog", "segment-auto", "stripe-auto", "square-auto",
        "shopify-auto", "vercel-auto", "render-automation", "youtube-auto",
        "reddit-auto", "twitter-auto", "instagram-auto", "tiktok-auto",
        "facebook", "file-organizer", "tmux", "obsidian-cli", "jq", "office-product",
        "odoo", "scraper", "scraping", "firecrawl", "exa-search", "tavily",
        "hasdata", "not-human-search", "linkedin-cli", "salesforce-dev",
    ]),
    ("Shell, OS & CLI", [
        "powershell", "bash-", "bash ", "busybox", "windows-shell", "posix-shell",
        "os-scripting", "linux-shell", "linux-troubleshoot", "linux-privilege",
        "windows-privilege", "shellcheck", "tmux", "server-management",
        "vscode-extension", "ai-native-cli", "runapi-cli",
    ]),
    ("Blockchain, Web3 & Crypto", [
        "blockchain", "web3", "crypto", "solidity", "defi", "nft", "lightning",
        "wallet", "smart-contract", "emblemai", "aomi", "longbridge", "x402",
        "options-flow", "yield-intelligence",
    ]),
    ("Finance, Business & Strategy", [
        "finance", "financial", "startup", "business-analyst", "business-case",
        "pricing-strategy", "product-manager", "product-marketing", "pitch",
        "investor", "risk-manager", "risk-metrics", "alpha-vantage", "billing",
        "revenue", "saas-mvp", "saas-multi", "micro-saas", "jobs-to-be-done",
        "osterwalder", "kotler", "business-model", "go-to-market", "okr",
        "kpi", "metrics-framework", "startup-metrics", "team-composition",
        "hr-pro", "it-manager", "legal-advisor", "employment-contract",
        "customs-trade", "energy-procurement", "inventory", "logistics",
        "carrier-relationship", "production-scheduling", "supply-chain",
        "returns-reverse", "quality-nonconformance", "interview-coach",
        "cv-generator", "jobgpt", "warren-buffett", "bill-gates", "sam-altman",
        "elon-musk", "steve-jobs", "decision-navigator", "goal-analyzer",
        "leiloeiro", "leilao", "junta-leilo", "advogado", "juridico", "pericia",
        "criminal", "contract-template",
    ]),
    ("Game & 3D / Creative Media", [
        "game", "unity", "unreal", "godot", "bevy", "shader", "glsl",
        "algorithmic-art", "fal-", "imagen", "stability-ai", "image-studio",
        "comfyui", "video", "podcast-generation", "remotion", "seek-and-analyze",
        "ingest-youtube", "youtube-summarizer", "youtube-full", "videodb",
        "transcriber", "audio", "amazon-alexa", "spline-3d", "minecraft",
        "vr-ar", "vr/ar",
    ]),
    ("Health & Lifestyle", [
        "health", "fitness", "nutrition", "weightloss", "sleep", "mental-health",
        "oral-health", "skin-health", "sexual-health", "occupational-health",
        "travel-health", "rehabilitation", "tcm-constitution", "family-health",
        "food-database", "puzzle-activity", "examprep",
    ]),
    ("Project, Git & Code Workflow", [
        "git", "github", "pull-request", "pr-", "pr ", "code-review", "review",
        "commit", "branch", "worktree", "merge", "refactor", "clean-code",
        "code-simplifier", "legacy-modernizer", "architect", "architecture",
        "ddd", "domain-driven", "c4-", "design-pattern", "composition-pattern",
        "planning", "plan-writing", "plan", "standup", "onboard", "issue",
        "code-documentation", "code-explain", "tech-debt", "production-audit",
        "production-code", "codebase", "dependency", "deps-", "uv-package",
        "python-packaging", "performance-engineer", "performance-optim",
        "performance-profil", "web-performance", "complexity", "simplify",
    ]),
    ("Skill & Agent Tooling (meta)", [
        "skill-", "skill ", "-skill", "mcp-builder", "mcp-tool", "agent-tool",
        "agent-manager", "agent-orchestrat", "orchestrat", "manage-skills",
        "manifest", "personal-tool-builder", "tool-builder", "claude-code",
        "claude-monitor", "claude-settings", "claude-ally", "permission-manager",
        "antigravity", "superpowers", "evolution", "kaizen", "blueprint",
    ]),
]

DEFAULT = "Other / Miscellaneous"


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data, key, buf = {}, None, []
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_]+):\s?(.*)$", line)
        if m:
            if key is not None:
                data[key] = " ".join(buf).strip()
            key, buf = m.group(1), [m.group(2)]
        elif key is not None and line.strip():
            buf.append(line.strip())
    if key is not None:
        data[key] = " ".join(buf).strip()
    return data


def clean(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
        val = val[1:-1]
    return val.strip()


def shorten(desc: str) -> str:
    desc = re.sub(r"\s+", " ", clean(desc))
    if not desc:
        return "_(no description)_"
    first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0]
    if 0 < len(first) <= MAX_LEN:
        return first.rstrip()
    return desc if len(desc) <= MAX_LEN else desc[: MAX_LEN - 1].rstrip() + "…"


def categorize(name: str, desc: str) -> str:
    hay_name = name.lower()
    hay_all = (name + " " + desc).lower()
    # pass 1: match against the name (stronger signal)
    for cat, kws in RULES:
        if any(k in hay_name for k in kws):
            return cat
    # pass 2: match against name + description
    for cat, kws in RULES:
        if any(k in hay_all for k in kws):
            return cat
    return DEFAULT


def md_escape(s: str) -> str:
    return s.replace("|", "\\|")


def main():
    rows = []
    for path in sorted(SKILLS_DIR.glob("**/SKILL.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        name = clean(fm.get("name", "")) or path.parent.name
        rows.append((name, shorten(fm.get("description", ""))))
    seen, uniq = set(), []
    for r in rows:
        if r[0].lower() in seen:
            continue
        seen.add(r[0].lower())
        uniq.append(r)

    cats: dict[str, list[tuple[str, str]]] = {}
    for name, desc in uniq:
        cats.setdefault(categorize(name, desc), []).append((name, desc))
    for c in cats:
        cats[c].sort(key=lambda r: r[0].lower())

    # category display order: defined order first, Other last
    order = [c for c, _ in RULES if c in cats]
    if DEFAULT in cats:
        order.append(DEFAULT)

    today = datetime.date.today().isoformat()
    L: list[str] = []
    L.append("# Installed Skills — by Category")
    L.append("")
    L.append(
        "All installed skills grouped by what they do. Categories are derived "
        "from each skill's name and description; a skill appears in exactly one "
        "category (its strongest match)."
    )
    L.append("")
    L.append(f"**Total skills:** {len(uniq)} · **Categories:** {len(order)} · **Generated:** {today}")
    L.append("")
    L.append("> Companion to `INSTALLED_SKILLS.md` (full alphabetical listing) and `INSTALLED_SKILLS.pdf`.")
    L.append("")

    # overview table
    L.append("## Overview")
    L.append("")
    L.append("| Category | Skills |")
    L.append("|---|---:|")
    for c in order:
        anchor = re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")
        L.append(f"| [{c}](#{anchor}) | {len(cats[c])} |")
    L.append(f"| **Total** | **{len(uniq)}** |")
    L.append("")

    for c in order:
        L.append(f"## {c}")
        L.append("")
        L.append(f"_{len(cats[c])} skills_")
        L.append("")
        L.append("| Skill | Description |")
        L.append("|---|---|")
        for name, desc in cats[c]:
            L.append(f"| `{md_escape(name)}` | {md_escape(desc)} |")
        L.append("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    # report distribution to stdout
    print(f"Wrote {OUT} — {len(uniq)} skills in {len(order)} categories:")
    for c in order:
        print(f"  {len(cats[c]):4d}  {c}")


if __name__ == "__main__":
    main()
