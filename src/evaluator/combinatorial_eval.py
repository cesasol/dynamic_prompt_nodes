from __future__ import annotations
import random

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


def evaluate_all(template: Template, ctx: EvaluationContext | None = None) -> list[str]:
    """Enumerate all possible prompt strings from a template."""
    if ctx is None:
        from src.wildcards import get_wildcard_manager

        ctx = EvaluationContext(rng=random.Random(0), wildcard_manager=get_wildcard_manager())
    return [text for _, text in _expand(template, ctx)]


def _expand(template: Template, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    """Return all (context, string) pairs for this template.

    Contexts are threaded sequentially so that variable assignments in one node
    are visible to subsequent nodes in the same template.
    """
    if not template.parts:
        return [(ctx, "")]
    branches: list[tuple[EvaluationContext, str]] = [(ctx, "")]
    for node in template.parts:
        new_branches: list[tuple[EvaluationContext, str]] = []
        for branch_ctx, prefix in branches:
            for new_ctx, suffix in _expand_node(node, branch_ctx):
                new_branches.append((new_ctx, prefix + suffix))
        branches = new_branches
    return branches


def _expand_node(
    node: Text | Variant | Wildcard | Variable | PPPSet | PPPEcho | PPPIf | PPPSendToNegative | PPPExtraNetwork,
    ctx: EvaluationContext,
) -> list[tuple[EvaluationContext, str]]:
    if isinstance(node, Text):
        return [(ctx, node.value)]
    if isinstance(node, Variant):
        return _expand_variant(node, ctx)
    if isinstance(node, Wildcard):
        return _expand_wildcard(node, ctx)
    if isinstance(node, Variable):
        return _expand_variable(node, ctx)
    if isinstance(node, PPPSet):
        return _expand_ppp_set(node, ctx)
    if isinstance(node, PPPEcho):
        return _expand_ppp_echo(node, ctx)
    if isinstance(node, PPPIf):
        return _expand_ppp_if(node, ctx)
    if isinstance(node, PPPSendToNegative):
        return _expand_ppp_stn(node, ctx)
    if isinstance(node, PPPExtraNetwork):
        return _expand_ppp_ext(node, ctx)
    raise AssertionError(f"Unexpected node type: {type(node)}")


def _expand_variant(v: Variant, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    # Each option expands independently with the same incoming ctx.
    # Context mutations within an option do not propagate outward.
    results: list[tuple[EvaluationContext, str]] = []
    for opt in v.options:
        for _, text in _expand(opt.node, ctx):
            results.append((ctx, text))
    return results


def _expand_wildcard(w: Wildcard, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    from src.evaluator.random_eval import _resolve_pattern

    pattern = _resolve_pattern(w.pattern, ctx)
    values = list(ctx.wildcard_manager.get_all_values(pattern))
    if not values:
        return [(ctx, f"__{pattern}__")]
    results: list[tuple[EvaluationContext, str]] = []
    for val in values:
        sub = _parser_mod.parse(val)
        for _, text in _expand(sub, ctx):
            results.append((ctx, text))
    return results


def _expand_variable(v: Variable, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    if v.value is not None:
        if v.immediate:
            # Each branch of the value gets its own forked context with x fixed.
            result: list[tuple[EvaluationContext, str]] = []
            for _, branch_value in _expand(v.value, ctx):
                branch_ctx = EvaluationContext(
                    rng=ctx.rng,
                    wildcard_manager=ctx.wildcard_manager,
                    variables=dict(ctx.variables),
                    resolved={**ctx.resolved, v.name: branch_value},
                    cycle_counters=dict(ctx.cycle_counters),
                )
                result.append((branch_ctx, ""))
            return result
        else:
            # Non-immediate: store AST; subsequent references expand all branches.
            ctx.variables[v.name] = v.value
            return [(ctx, "")]
    # Reference
    if v.name in ctx.resolved:
        return [(ctx, ctx.resolved[v.name])]
    if v.name in ctx.variables:
        return [(ctx, text) for _, text in _expand(ctx.variables[v.name], ctx)]
    if v.default is not None:
        return [(ctx, text) for _, text in _expand(v.default, ctx)]
    raise KeyError(f"Variable '${{{v.name}}}' is not defined")


def _expand_ppp_set(node: PPPSet, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    has_evaluate = "evaluate" in node.modifiers
    has_add = "add" in node.modifiers
    has_ifundefined = "ifundefined" in node.modifiers

    if has_ifundefined and (node.var_name in ctx.resolved or node.var_name in ctx.variables):
        return [(ctx, "")]

    if has_evaluate:
        result: list[tuple[EvaluationContext, str]] = []
        for _, value_str in _expand(node.content, ctx):
            if has_add:
                existing = ctx.resolved.get(node.var_name, "")
                new_resolved = {**ctx.resolved, node.var_name: existing + value_str}
            else:
                new_resolved = {**ctx.resolved, node.var_name: value_str}
            branch_ctx = EvaluationContext(
                rng=ctx.rng,
                wildcard_manager=ctx.wildcard_manager,
                variables=dict(ctx.variables),
                resolved=new_resolved,
                cycle_counters=dict(ctx.cycle_counters),
            )
            result.append((branch_ctx, ""))
        return result

    if has_add:
        existing_ast = ctx.variables.get(node.var_name)
        if existing_ast is not None:
            combined = Template(parts=list(existing_ast.parts) + list(node.content.parts))
            ctx.variables[node.var_name] = combined
        else:
            existing_str = ctx.resolved.get(node.var_name, "")
            if existing_str:
                from src.parser.ast_nodes import Text
                wrapper = Template(parts=[Text(value=existing_str)] + list(node.content.parts))
                ctx.variables[node.var_name] = wrapper
            else:
                ctx.variables[node.var_name] = node.content
    else:
        ctx.variables[node.var_name] = node.content

    return [(ctx, "")]


def _expand_ppp_echo(node: PPPEcho, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    if node.var_name in ctx.resolved:
        return [(ctx, ctx.resolved[node.var_name])]
    if node.var_name in ctx.variables:
        return _expand(ctx.variables[node.var_name], ctx)
    if node.default is not None:
        return _expand(node.default, ctx)
    return [(ctx, "")]


def _expand_ppp_if(node: PPPIf, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    result: list[tuple[EvaluationContext, str]] = []
    for condition, content in node.branches:
        if evaluate_condition(condition, ctx, _dummy_evaluate):
            return _expand(content, ctx)
    if node.else_content is not None:
        return _expand(node.else_content, ctx)
    return [(ctx, "")]


def _expand_ppp_stn(node: PPPSendToNegative, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    if node.is_insertion_point:
        return [(ctx, "")]
    results: list[tuple[EvaluationContext, str]] = []
    for branch_ctx, text in _expand(node.content, ctx):
        branch_ctx.stn_contents.append((node.position, text))
        results.append((branch_ctx, ""))
    return results


def _expand_ppp_ext(node: PPPExtraNetwork, ctx: EvaluationContext) -> list[tuple[EvaluationContext, str]]:
    if node.condition is not None:
        if not evaluate_condition(node.condition, ctx, _dummy_evaluate):
            return [(ctx, "")]
    if node.is_mapping:
        return [(ctx, "")]
    weight = node.weight
    if weight is None and node.ext_type in ("lora", "hypernet"):
        weight = "1"
    prefix = f"<{node.ext_type}:{node.name}:{weight}>" if weight else f"<{node.ext_type}:{node.name}>"
    if node.triggers is None:
        return [(ctx, prefix)]
    results: list[tuple[EvaluationContext, str]] = []
    for branch_ctx, text in _expand(node.triggers, ctx):
        results.append((branch_ctx, prefix + text))
    return results


def _dummy_evaluate(template: Template, ctx: EvaluationContext) -> str:
    from src.evaluator.random_eval import evaluate as random_evaluate
    return random_evaluate(template, ctx)
