from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


Node = "Text | Template | Variant | WeightedOption | Wildcard | Variable | PPPSet | PPPEcho | PPPIf | PPPSendToNegative | PPPExtraNetwork"


@dataclass
class Text:
    value: str


@dataclass
class Template:
    """A sequence of nodes forming a complete template or sub-expression."""

    parts: list[Text | Variant | Wildcard | Variable | PPPSet | PPPEcho | PPPIf | PPPSendToNegative | PPPExtraNetwork]


@dataclass
class PPPSet:
    """<ppp:set varname [modifiers]>content<ppp:/set>"""

    var_name: str
    modifiers: list[str]
    content: Template


@dataclass
class PPPEcho:
    """<ppp:echo varname/> or <ppp:echo varname>default<ppp:/echo>"""

    var_name: str
    default: Template | None


@dataclass
class PPPIf:
    """<ppp:if condition>content<ppp:elif condition>content<ppp:else>content<ppp:/if>"""

    branches: list[tuple[str, Template]]
    else_content: Template | None


@dataclass
class PPPSendToNegative:
    """<ppp:stn [position]>content<ppp:/stn> or <ppp:stn iN/>"""

    position: str | None
    content: Template | None
    is_insertion_point: bool


@dataclass
class PPPExtraNetwork:
    """<ppp:ext type name [weight] [if condition]>[triggers]<ppp:/ext>"""

    ext_type: str
    name: str
    weight: str | None
    condition: str | None
    triggers: Template | None
    is_mapping: bool


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
