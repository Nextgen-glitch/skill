"""The tool registry — the thing we extend forever.

A tool is a named capability with a reader-friendly description and typed, named inputs.
Adding a capability means writing one self-contained function and registering it — never
editing the core agent loop.

Each tool declares whether it is `consequential` (sends, spends, deletes, or changes a
setting). Read-only tools run freely; consequential ones are stopped by the confirmation
gate in Tier 6. The registry runs tools defensively: bad input or a thrown exception
comes back as a plain-language string the model can reason over, never a crash.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Param:
    """One typed, named input to a tool."""

    type: str  # JSON-schema scalar: "string", "integer", "number", "boolean"
    description: str
    required: bool = True
    default: Any = None
    enum: list[Any] | None = None


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Param]
    consequential: bool
    func: Callable[..., str]

    @property
    def schema(self) -> dict[str, Any]:
        """The shape handed to the model so it knows when and how to call this tool."""
        properties: dict[str, Any] = {}
        required: list[str] = []
        for pname, p in self.parameters.items():
            prop: dict[str, Any] = {"type": p.type, "description": p.description}
            if p.enum:
                prop["enum"] = p.enum
            properties[pname] = prop
            if p.required:
                required.append(pname)
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }


class ToolInputError(ValueError):
    """Raised when the model's tool input doesn't match the declared parameters."""


@dataclass
class ToolRegistry:
    """Holds tools and runs them safely."""

    _tools: dict[str, Tool] = field(default_factory=dict)

    def add(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Param] | None = None,
        consequential: bool = False,
    ) -> Callable[[Callable[..., str]], Callable[..., str]]:
        """Decorator: register a function as a tool. The function is returned unchanged."""

        def decorate(fn: Callable[..., str]) -> Callable[..., str]:
            self.add(Tool(name, description, parameters or {}, consequential, fn))
            return fn

        return decorate

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def anthropic_schema(self) -> list[dict[str, Any]]:
        return [t.schema for t in self._tools.values()]

    def _validate(self, tool: Tool, raw: dict[str, Any]) -> dict[str, Any]:
        clean: dict[str, Any] = {}
        for pname, p in tool.parameters.items():
            if pname in raw and raw[pname] is not None:
                value = raw[pname]
                if p.enum and value not in p.enum:
                    raise ToolInputError(
                        f"'{pname}' must be one of {p.enum}, got {value!r}."
                    )
                clean[pname] = value
            elif p.required:
                raise ToolInputError(f"Missing required input '{pname}'.")
            elif p.default is not None:
                clean[pname] = p.default
        return clean

    def run(self, name: str, raw_input: dict[str, Any]) -> str:
        """Run a tool by name. Always returns a string — errors included."""
        tool = self.get(name)
        if tool is None:
            return f"(no such tool: {name})"
        try:
            kwargs = self._validate(tool, raw_input or {})
        except ToolInputError as err:
            return f"(invalid input for {name}: {err})"
        try:
            result = tool.func(**kwargs)
        except Exception as err:  # noqa: BLE001 - hand the failure to the model, don't crash
            return f"(the {name} tool failed: {err})"
        return result if isinstance(result, str) else str(result)


# A shared default registry. Tool modules register onto it via the `tool` decorator;
# `build_registry()` imports those modules and returns it. Tests build isolated
# ToolRegistry() instances instead of touching this global.
_DEFAULT = ToolRegistry()
tool = _DEFAULT.tool


def build_registry() -> ToolRegistry:
    """Import the bundled tool modules (registering them) and return the registry."""
    from juno.tools import calendar_tools, prospecting_tools  # noqa: F401

    return _DEFAULT
