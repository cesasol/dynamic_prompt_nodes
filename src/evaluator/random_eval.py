from __future__ import annotations
import random

from src.evaluator.context import EvaluationContext
from src.parser.ast_nodes import Template, Text, Variant, Wildcard, Variable


def evaluate(template: Template, ctx: EvaluationContext) -> str:
    """Evaluate a template using random sampling."""
    return "".join(_eval_node(node, ctx) for node in template.parts)


def _eval_node(node: Text | Variant | Wildcard | Variable, ctx: EvaluationContext) -> str:
    if isinstance(node, Text):
        return node.value
    if isinstance(node, Variant):
        return _eval_variant(node, ctx)
    if isinstance(node, Wildcard):
        return _eval_wildcard(node, ctx)
    if isinstance(node, Variable):
        return _eval_variable(node, ctx)
    raise AssertionError(f"Unexpected node type: {type(node)}")


def _eval_variant(v: Variant, ctx: EvaluationContext) -> str:
    if v.sampler == "cyclical":
        key = str(id(v))
        idx = ctx.cycle_counters.get(key, 0)
        count = min(v.min_count, len(v.options))
        chosen = [v.options[(idx + i) % len(v.options)] for i in range(count)]
        ctx.cycle_counters[key] = (idx + count) % len(v.options)
    else:
        weights = [opt.weight for opt in v.options]
        total = sum(weights)
        normalized = [w / total for w in weights]
        count = ctx.rng.randint(v.min_count, min(v.max_count, len(v.options)))
        indices = _weighted_sample_no_replacement(normalized, count, ctx.rng)
        chosen = [v.options[i] for i in indices]

    values = [evaluate(opt.node, ctx) for opt in chosen]
    return v.separator.join(values)


def _weighted_sample_no_replacement(weights: list[float], k: int, rng: random.Random) -> list[int]:
    """Sample k indices without replacement using given weights."""
    remaining = list(range(len(weights)))
    remaining_weights = list(weights)
    chosen = []
    for _ in range(k):
        if not remaining:
            break
        total = sum(remaining_weights)
        r = rng.random() * total
        cumulative = 0.0
        for i, w in enumerate(remaining_weights):
            cumulative += w
            if r <= cumulative:
                chosen.append(remaining[i])
                remaining.pop(i)
                remaining_weights.pop(i)
                break
    return chosen


def _eval_wildcard(w: Wildcard, ctx: EvaluationContext) -> str:
    # Resolve any ${var} interpolations in the pattern
    pattern = _resolve_pattern(w.pattern, ctx)
    values = list(ctx.wildcard_manager.get_all_values(pattern))
    if not values:
        return f"__{pattern}__"
    if w.sampler == "cyclical":
        key = f"wc:{pattern}"
        idx = ctx.cycle_counters.get(key, 0)
        result = values[idx % len(values)]
        ctx.cycle_counters[key] = (idx + 1) % len(values)
    else:
        result = ctx.rng.choice(values)
    # Wildcard values can themselves be templates — parse and evaluate
    from src.parser.parser import parse as parse_template

    return evaluate(parse_template(result), ctx)


def _resolve_pattern(pattern: str, ctx: EvaluationContext) -> str:
    """Substitute ${var} references in a wildcard path pattern."""
    import re

    def replace(m: re.Match[str]) -> str:
        name = m.group(1)
        if name in ctx.resolved:
            return ctx.resolved[name]
        if name in ctx.variables:
            return evaluate(ctx.variables[name], ctx)
        return m.group(0)  # leave unresolved

    return re.sub(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}", replace, pattern)


def _eval_variable(v: Variable, ctx: EvaluationContext) -> str:
    if v.value is not None:
        # Assignment
        if v.immediate:
            value_str = evaluate(v.value, ctx)
            ctx.resolved[v.name] = value_str
        else:
            ctx.variables[v.name] = v.value
        return ""  # assignment produces no output
    # Reference
    return ctx.get_variable(v.name, v.default, evaluate)
