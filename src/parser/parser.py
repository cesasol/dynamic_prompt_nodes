from __future__ import annotations
from pathlib import Path
from typing import Any, Literal, cast

from lark import Lark, Transformer

from src.parser.ast_nodes import (
    Template,
    Text,
    Variant,
    WeightedOption,
    Wildcard,
    Variable,
)

_GRAMMAR = (Path(__file__).parent / "grammar.lark").read_text()
_parser = Lark(_GRAMMAR, parser="earley", lexer="dynamic", ambiguity="resolve")


def parse(template_str: str) -> Template:
    """Parse a template string into an AST."""
    if not template_str:
        return Template(parts=[])
    tree = _parser.parse(template_str)
    result: Template = _Transformer().transform(tree)
    return result


class _Transformer(Transformer):  # type: ignore[type-arg]
    def start(self, items: list[Any]) -> Template:
        result: Template = items[0]
        return result

    def template(self, items: list[Any]) -> Template:
        parts: list[Text | Variant | Wildcard | Variable] = []
        for item in items:
            if item is None:
                continue
            if isinstance(item, Text) and parts and isinstance(parts[-1], Text):
                parts[-1] = Text(parts[-1].value + item.value)
            else:
                parts.append(item)
        # Strip leading/trailing whitespace from text at option boundaries
        if parts and isinstance(parts[0], Text):
            parts[0] = Text(parts[0].value.lstrip())
            if not parts[0].value:
                parts.pop(0)
        if parts and isinstance(parts[-1], Text):
            parts[-1] = Text(parts[-1].value.rstrip())
            if not parts[-1].value:
                parts.pop()
        return Template(parts=parts)

    def TEXT(self, token: Any) -> Text:
        return Text(value=str(token))

    def comment(self, items: list[Any]) -> None:
        return None  # stripped

    # --- Variants ---

    def variant(self, items: list[Any]) -> Variant:
        sampler: Literal["random", "combinatorial", "cyclical"] = "random"
        min_count = 1
        max_count = 1
        separator = ", "
        options: list[WeightedOption] = []

        for item in items:
            if isinstance(item, _SamplerMarker):
                sampler = cast(Literal["random", "combinatorial", "cyclical"], item.name)
            elif isinstance(item, _CountSpec):
                min_count = item.min_count
                max_count = item.max_count
                separator = item.separator
            elif isinstance(item, WeightedOption):
                options.append(item)

        return Variant(
            min_count=min_count,
            max_count=max_count,
            separator=separator,
            sampler=sampler,
            options=options,
        )

    def sampler_random(self, _: list[Any]) -> "_SamplerMarker":
        return _SamplerMarker("random")

    def sampler_cyclical(self, _: list[Any]) -> "_SamplerMarker":
        return _SamplerMarker("cyclical")

    def count_with_sep(self, items: list[Any]) -> "_CountSpec":
        count_range = items[0]
        sep = str(items[1])
        return _CountSpec(min_count=count_range[0], max_count=count_range[1], separator=sep)

    def count_only(self, items: list[Any]) -> "_CountSpec":
        count_range = items[0]
        return _CountSpec(min_count=count_range[0], max_count=count_range[1], separator=", ")

    def range_lo_hi(self, items: list[Any]) -> tuple[int, int]:
        return (int(items[0]), int(items[1]))

    def range_lo(self, items: list[Any]) -> tuple[int, int]:
        n = int(items[0])
        return (n, n)

    def range_hi(self, items: list[Any]) -> tuple[int, int]:
        return (1, int(items[0]))

    def range_single(self, items: list[Any]) -> tuple[int, int]:
        n = int(items[0])
        return (n, n)

    def weighted_option(self, items: list[Any]) -> WeightedOption:
        return WeightedOption(weight=float(items[0]), node=items[1])

    def plain_option(self, items: list[Any]) -> WeightedOption:
        return WeightedOption(weight=1.0, node=items[0])

    # --- Wildcards ---

    def wildcard(self, items: list[Any]) -> Wildcard:
        sampler: Literal["random", "combinatorial", "cyclical"] = "random"
        pattern = ""
        params: dict[str, str] = {}

        for item in items:
            if isinstance(item, _SamplerMarker):
                sampler = cast(Literal["random", "combinatorial", "cyclical"], item.name)
            elif isinstance(item, str):
                pattern = item
            elif isinstance(item, dict):
                params = item

        return Wildcard(pattern=pattern, sampler=sampler, params=params)

    def WILDCARD_PAT(self, token: Any) -> str:
        return str(token)

    def param_list(self, items: list[Any]) -> dict[str, str]:
        result: dict[str, str] = {}
        for item in items:
            if isinstance(item, dict):
                result.update(item)
        return result

    def param(self, items: list[Any]) -> dict[str, str]:
        return {str(items[0]): str(items[1]).strip()}

    def param_value(self, items: list[Any]) -> str:
        return str(items[0])

    # --- Variables ---

    def var_ref(self, items: list[Any]) -> Variable:
        return Variable(name=str(items[0]), value=None, immediate=False, default=None)

    def var_ref_default(self, items: list[Any]) -> Variable:
        return Variable(name=str(items[0]), value=None, immediate=False, default=items[1])

    def var_assign(self, items: list[Any]) -> Variable:
        return Variable(name=str(items[0]), value=items[1], immediate=False, default=None)

    def var_assign_imm(self, items: list[Any]) -> Variable:
        return Variable(name=str(items[0]), value=items[1], immediate=True, default=None)


class _SamplerMarker:
    def __init__(self, name: str) -> None:
        self.name = name


class _CountSpec:
    def __init__(self, min_count: int, max_count: int, separator: str) -> None:
        self.min_count = min_count
        self.max_count = max_count
        self.separator = separator
