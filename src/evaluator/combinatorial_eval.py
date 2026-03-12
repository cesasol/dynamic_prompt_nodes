from __future__ import annotations
import random

from dynamicprompts.wildcards import WildcardManager

from src.evaluator.context import EvaluationContext
from src.parser.ast_nodes import Template, Text, Variant, Wildcard, Variable
from src.parser import parser as _parser_mod


def evaluate_all(template: Template, ctx: EvaluationContext | None = None) -> list[str]:
    """Enumerate all possible prompt strings from a template."""
    if ctx is None:
        ctx = EvaluationContext(rng=random.Random(0), wildcard_manager=WildcardManager())
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
    node: Text | Variant | Wildcard | Variable,
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
