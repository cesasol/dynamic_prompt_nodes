import random
import pytest
from pathlib import Path
from dynamicprompts.wildcards import WildcardManager

from src.evaluator.context import EvaluationContext
from src.evaluator.cyclical_eval import evaluate
from src.parser.parser import parse


@pytest.fixture
def make_ctx(wildcards_path: Path):  # type: ignore[no-untyped-def]
    counters: dict[str, int] = {}

    def _make() -> EvaluationContext:
        return EvaluationContext(
            rng=random.Random(0),
            wildcard_manager=WildcardManager(path=wildcards_path),
            cycle_counters=counters,  # shared across calls
        )

    return _make


def test_variant_cycles(make_ctx) -> None:  # type: ignore[no-untyped-def]
    t = parse("{a|b|c}")
    ctx = make_ctx()
    assert evaluate(t, ctx) == "a"
    assert evaluate(t, ctx) == "b"
    assert evaluate(t, ctx) == "c"
    assert evaluate(t, ctx) == "a"  # wraps


def test_plain_text_unchanged(make_ctx) -> None:  # type: ignore[no-untyped-def]
    t = parse("hello")
    ctx = make_ctx()
    assert evaluate(t, ctx) == "hello"
    assert evaluate(t, ctx) == "hello"


def test_wildcard_cycles(make_ctx) -> None:  # type: ignore[no-untyped-def]
    t = parse("__animals__")
    ctx = make_ctx()
    results = [evaluate(t, ctx) for _ in range(6)]
    # Should cycle through all 3 animals twice
    assert len(set(results)) == 3
    assert results[:3] == results[3:]


def test_two_variants_cycle_independently(make_ctx) -> None:  # type: ignore[no-untyped-def]
    t = parse("{a|b} {x|y|z}")
    ctx = make_ctx()
    r1 = evaluate(t, ctx)
    r2 = evaluate(t, ctx)
    r3 = evaluate(t, ctx)
    # First variant cycles: a, b, a; second: x, y, z
    assert r1 == "a x"
    assert r2 == "b y"
    assert r3 == "a z"
