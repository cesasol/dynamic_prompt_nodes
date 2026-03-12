from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


Node = "Text | Template | Variant | WeightedOption | Wildcard | Variable"


@dataclass
class Text:
    value: str


@dataclass
class Template:
    """A sequence of nodes forming a complete template or sub-expression."""

    parts: list[Text | Variant | Wildcard | Variable]


@dataclass
class WeightedOption:
    weight: float
    node: Template


@dataclass
class Variant:
    min_count: int
    max_count: int
    separator: str
    sampler: Literal["random", "combinatorial", "cyclical"]
    options: list[WeightedOption]


@dataclass
class Wildcard:
    pattern: str
    sampler: Literal["random", "combinatorial", "cyclical"]
    params: dict[str, str] = field(default_factory=dict)


@dataclass
class Variable:
    name: str
    value: Template | None  # None = read-only reference
    immediate: bool  # True when ${name=!...}
    default: Template | None  # for ${name:default}
