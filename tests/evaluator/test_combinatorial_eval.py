import pytest
from pathlib import Path
from dynamicprompts.wildcards import WildcardManager
import random

from src.evaluator.context import EvaluationContext
from src.evaluator.combinatorial_eval import evaluate_all
from src.parser.parser import parse


@pytest.fixture
def ctx(wildcards_path: Path) -> EvaluationContext:
    return EvaluationContext(
        rng=random.Random(0),
        wildcard_manager=WildcardManager(path=wildcards_path),
    )


def test_plain_text(ctx: EvaluationContext) -> None:
    results = evaluate_all(parse("hello"), ctx)
    assert results == ["hello"]


def test_single_variant(ctx: EvaluationContext) -> None:
    results = evaluate_all(parse("{a|b|c}"), ctx)
    assert sorted(results) == ["a", "b", "c"]


def test_cross_product(ctx: EvaluationContext) -> None:
    results = evaluate_all(parse("{a|b} {c|d}"), ctx)
    assert sorted(results) == ["a c", "a d", "b c", "b d"]


def test_cross_product_count(ctx: EvaluationContext) -> None:
    results = evaluate_all(parse("{a|b} {c|d}"))
    assert len(results) == 4


def test_nested_variant(ctx: EvaluationContext) -> None:
    results = evaluate_all(parse("{a|{b|c}}"), ctx)
    assert sorted(results) == ["a", "b", "c"]


def test_wildcard_combinatorial(ctx: EvaluationContext) -> None:
    results = evaluate_all(parse("__animals__"), ctx)
    assert sorted(results) == ["bird", "cat", "dog"]


def test_variable_evaluated_once_per_branch(ctx: EvaluationContext) -> None:
    # ${x=!{a|b}} creates branches; each branch fixes x for that branch
    results = evaluate_all(parse("${x=!{a|b}} ${x} ${x}"), ctx)
    # Each result should have the same word repeated
    for r in results:
        words = [w for w in r.split() if w]
        assert words[0] == words[1]


def test_empty_template(ctx: EvaluationContext) -> None:
    results = evaluate_all(parse(""), ctx)
    assert results == [""]
