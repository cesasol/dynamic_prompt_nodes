from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Iterable, Protocol

from src.parser.ast_nodes import Template


class WildcardProvider(Protocol):
    def get_all_values(self, wildcard: str) -> Iterable[str]: ...


class Evaluator(Protocol):
    def __call__(self, template: Template, ctx: "EvaluationContext") -> str: ...


@dataclass
class EvaluationContext:
    rng: random.Random
    wildcard_manager: WildcardProvider
    variables: dict[str, Template] = field(default_factory=dict)
    resolved: dict[str, str] = field(default_factory=dict)
    cycle_counters: dict[str, int] = field(default_factory=dict)
    stn_contents: list[tuple[str | None, str]] = field(default_factory=list)

    def get_variable(self, name: str, default: Template | None, evaluator: Evaluator) -> str:
        """Resolve a variable reference: resolved → variables → default → error."""
        if name in self.resolved:
            return self.resolved[name]
        if name in self.variables:
            return evaluator(self.variables[name], self)
        if default is not None:
            return evaluator(default, self)
        raise KeyError(f"Variable '${{{name}}}' is not defined")
