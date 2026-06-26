"""Load configuration from config.toml and secrets from .env.

Configuration over hardcoded values: everything tunable lives in config.toml so a
change is a one-line edit, never a code change. Secrets live only in .env (git-ignored)
and are read from the environment — never stored in config.toml or source.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:  # tomllib is stdlib on 3.11+, tomli is the backport for 3.10
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised only on 3.10
    import tomli as tomllib  # type: ignore

# Project root = the directory that contains config.toml (one level up from this file).
ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.toml"


def _load_env() -> None:
    """Load .env into the process environment if python-dotenv is available.

    Kept soft so the harness still imports without the dependency; real keys are
    required only when a feature that needs them actually runs.
    """
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:  # pragma: no cover
        return
    load_dotenv(ROOT / ".env")


class Config:
    """Read-only view over config.toml with convenient dotted access.

    Example:
        cfg = Config.load()
        cfg.get("model", "name")
        cfg.section("voice")["push_to_talk_key"]
    """

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        _load_env()
        path = path or CONFIG_PATH
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(data)

    def section(self, name: str) -> dict[str, Any]:
        return dict(self._data.get(name, {}))

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self._data.get(section, {}).get(key, default)

    # --- secrets come from the environment, never from the toml file ---
    @staticmethod
    def secret(name: str) -> str | None:
        return os.environ.get(name)

    @staticmethod
    def require_secret(name: str) -> str:
        value = os.environ.get(name)
        if not value:
            raise MissingSecret(name)
        return value


class MissingSecret(RuntimeError):
    """Raised when a required secret (API key) is absent from the environment."""

    def __init__(self, name: str):
        super().__init__(
            f"Missing required secret: {name}. "
            f"Copy .env.example to .env and set {name}."
        )
        self.name = name
