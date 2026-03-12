import random
import pytest
from pathlib import Path
from dynamicprompts.wildcards import WildcardManager

from src.evaluator.context import EvaluationContext
from src.evaluator.random_eval import evaluate
from src.parser.parser import parse


@pytest.fixture
def ctx(wildcards_path: Path) -> EvaluationContext:
    return EvaluationContext(
        rng=random.Random(42),
        wildcard_manager=WildcardManager(path=wildcards_path),
    )


def test_plain_text(ctx: EvaluationContext) -> None:
    result = evaluate(parse("hello world"), ctx)
    assert result == "hello world"


def test_variant_picks_one(ctx: EvaluationContext) -> None:
    result = evaluate(parse("{cat|dog}"), ctx)
    assert result in {"cat", "dog"}


def test_same_seed_reproducible() -> None:
    t = parse("{cat|dog|bird}")
    r1 = evaluate(t, EvaluationContext(rng=random.Random(42), wildcard_manager=WildcardManager()))
    r2 = evaluate(t, EvaluationContext(rng=random.Random(42), wildcard_manager=WildcardManager()))
    assert r1 == r2


def test_weighted_variant() -> None:
    # Weight 0 means never picked
    results = {
        evaluate(parse("{1000::always|0::never}"), EvaluationContext(rng=random.Random(i), wildcard_manager=WildcardManager()))
        for i in range(20)
    }
    assert "always" in results
    assert "never" not in results


def test_multi_pick(ctx: EvaluationContext) -> None:
    result = evaluate(parse("{2$$a|b|c}"), ctx)
    parts = result.split(", ")
    assert len(parts) == 2
    assert len(set(parts)) == 2  # no duplicates


def test_multi_pick_custom_separator(ctx: EvaluationContext) -> None:
    result = evaluate(parse("{2$$ and $$a|b|c}"), ctx)
    assert " and " in result


def test_wildcard_resolution(ctx: EvaluationContext) -> None:
    result = evaluate(parse("__animals__"), ctx)
    assert result in {"cat", "dog", "bird"}


def test_wildcard_in_template(ctx: EvaluationContext) -> None:
    result = evaluate(parse("A __animals__ running"), ctx)
    assert result.startswith("A ")
    assert result.endswith(" running")


def test_variable_immediate(ctx: EvaluationContext) -> None:
    result = evaluate(parse("${x=!{a|b}} ${x} ${x}"), ctx)
    words = [p for p in result.split() if p]
    assert len(words) == 2  # two uses, same value
    assert words[0] == words[1]


def test_variable_non_immediate() -> None:
    # Non-immediate: re-evaluated each use. With 2 options, uses might differ over many trials.
    seen = set()
    for i in range(50):
        result = evaluate(parse("${x={a|b}} ${x} ${x}"), EvaluationContext(rng=random.Random(i), wildcard_manager=WildcardManager()))
        words = [p for p in result.split() if p]
        seen.add(tuple(words))
    # Eventually we should see differing values
    assert any(w[0] != w[1] for w in seen)


def test_variable_default(ctx: EvaluationContext) -> None:
    result = evaluate(parse("${undefined:fallback}"), ctx)
    assert result == "fallback"


def test_nested_variant(ctx: EvaluationContext) -> None:
    result = evaluate(parse("{a|{b|c}}"), ctx)
    assert result in {"a", "b", "c"}


def test_cyclical_inline(ctx: EvaluationContext) -> None:
    # {@ } in random evaluator uses ctx.cycle_counters — cycles within one prompt
    r1 = evaluate(parse("{@x|y|z}"), ctx)
    assert r1 in {"x", "y", "z"}
