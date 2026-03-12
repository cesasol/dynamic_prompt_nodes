from __future__ import annotations

from src.evaluator.context import EvaluationContext
from src.parser.ast_nodes import Template, Text, Variant, Wildcard, Variable
from src.parser import parser as _parser_mod


def evaluate(template: Template, ctx: EvaluationContext) -> str:
    """Evaluate a template using cyclical sampling.

    ctx.cycle_counters must be shared across calls to maintain cycle state.
    """
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
    # Use object id as stable key — the same parsed Template is reused across calls
    key = str(id(v))
    idx = ctx.cycle_counters.get(key, 0)
    count = min(v.min_count, len(v.options))
    chosen = [v.options[(idx + i) % len(v.options)] for i in range(count)]
    ctx.cycle_counters[key] = (idx + count) % len(v.options)
    values = [evaluate(opt.node, ctx) for opt in chosen]
    return v.separator.join(values)


def _eval_wildcard(w: Wildcard, ctx: EvaluationContext) -> str:
    from src.evaluator.random_eval import _resolve_pattern

    pattern = _resolve_pattern(w.pattern, ctx)
    values = sorted(ctx.wildcard_manager.get_all_values(pattern))
    if not values:
        return f"__{pattern}__"
    key = f"wc:{pattern}"
    idx = ctx.cycle_counters.get(key, 0)
    result = values[idx % len(values)]
    ctx.cycle_counters[key] = (idx + 1) % len(values)
    return evaluate(_parser_mod.parse(result), ctx)


def _eval_variable(v: Variable, ctx: EvaluationContext) -> str:
    from src.evaluator.random_eval import evaluate as random_evaluate

    if v.value is not None:
        if v.immediate:
            value_str = random_evaluate(v.value, ctx)
            ctx.resolved[v.name] = value_str
        else:
            ctx.variables[v.name] = v.value
        return ""
    return ctx.get_variable(v.name, v.default, evaluate)
