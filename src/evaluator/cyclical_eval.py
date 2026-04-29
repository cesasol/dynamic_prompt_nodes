from __future__ import annotations

from src.evaluator.context import EvaluationContext
from src.evaluator.conditions import evaluate_condition
from src.parser.ast_nodes import (
    Template,
    Text,
    Variant,
    Wildcard,
    Variable,
    PPPSet,
    PPPEcho,
    PPPIf,
    PPPSendToNegative,
    PPPExtraNetwork,
)
from src.parser import parser as _parser_mod


def evaluate(template: Template, ctx: EvaluationContext) -> str:
    """Evaluate a template using cyclical sampling.

    ctx.cycle_counters must be shared across calls to maintain cycle state.
    """
    return "".join(_eval_node(node, ctx) for node in template.parts)


def _eval_node(
    node: Text | Variant | Wildcard | Variable | PPPSet | PPPEcho | PPPIf | PPPSendToNegative | PPPExtraNetwork,
    ctx: EvaluationContext,
) -> str:
    if isinstance(node, Text):
        return node.value
    if isinstance(node, Variant):
        return _eval_variant(node, ctx)
    if isinstance(node, Wildcard):
        return _eval_wildcard(node, ctx)
    if isinstance(node, Variable):
        return _eval_variable(node, ctx)
    if isinstance(node, PPPSet):
        return _eval_ppp_set(node, ctx)
    if isinstance(node, PPPEcho):
        return _eval_ppp_echo(node, ctx)
    if isinstance(node, PPPIf):
        return _eval_ppp_if(node, ctx)
    if isinstance(node, PPPSendToNegative):
        return _eval_ppp_stn(node, ctx)
    if isinstance(node, PPPExtraNetwork):
        return _eval_ppp_ext(node, ctx)
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


def _eval_ppp_set(node: PPPSet, ctx: EvaluationContext) -> str:
    from src.evaluator.random_eval import evaluate as random_evaluate

    has_evaluate = "evaluate" in node.modifiers
    has_add = "add" in node.modifiers
    has_ifundefined = "ifundefined" in node.modifiers

    if has_ifundefined and (node.var_name in ctx.resolved or node.var_name in ctx.variables):
        return ""

    if has_evaluate:
        value_str = random_evaluate(node.content, ctx)
        if has_add:
            existing = ctx.resolved.get(node.var_name, "")
            ctx.resolved[node.var_name] = existing + value_str
        else:
            ctx.resolved[node.var_name] = value_str
    else:
        if has_add:
            existing_ast = ctx.variables.get(node.var_name)
            if existing_ast is not None:
                combined = Template(parts=list(existing_ast.parts) + list(node.content.parts))
                ctx.variables[node.var_name] = combined
            else:
                existing_str = ctx.resolved.get(node.var_name, "")
                if existing_str:
                    wrapper = Template(parts=[Text(value=existing_str)] + list(node.content.parts))
                    ctx.variables[node.var_name] = wrapper
                else:
                    ctx.variables[node.var_name] = node.content
        else:
            ctx.variables[node.var_name] = node.content

    return ""


def _eval_ppp_echo(node: PPPEcho, ctx: EvaluationContext) -> str:
    try:
        return ctx.get_variable(node.var_name, node.default, evaluate)
    except KeyError:
        return ""


def _eval_ppp_if(node: PPPIf, ctx: EvaluationContext) -> str:
    for condition, content in node.branches:
        if evaluate_condition(condition, ctx, evaluate):
            return evaluate(content, ctx)
    if node.else_content is not None:
        return evaluate(node.else_content, ctx)
    return ""


def _eval_ppp_stn(node: PPPSendToNegative, ctx: EvaluationContext) -> str:
    if node.is_insertion_point:
        return ""
    content_str = evaluate(node.content, ctx) if node.content else ""
    ctx.stn_contents.append((node.position, content_str))
    return ""


def _eval_ppp_ext(node: PPPExtraNetwork, ctx: EvaluationContext) -> str:
    if node.condition is not None:
        if not evaluate_condition(node.condition, ctx, evaluate):
            return ""
    if node.is_mapping:
        return ""
    weight = node.weight
    if weight is None and node.ext_type in ("lora", "hypernet"):
        weight = "1"
    tag = f"<{node.ext_type}:{node.name}:{weight}>" if weight else f"<{node.ext_type}:{node.name}>"
    if node.triggers is not None:
        tag += evaluate(node.triggers, ctx)
    return tag
