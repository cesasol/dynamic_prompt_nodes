import random
import pytest

from src.evaluator.context import EvaluationContext
from src.evaluator.random_eval import evaluate
from src.evaluator.combinatorial_eval import evaluate_all
from src.evaluator.cyclical_eval import evaluate as cyclical_evaluate
from src.parser.parser import parse
from src.wildcards import WildcardManager


@pytest.fixture
def ctx() -> EvaluationContext:
    return EvaluationContext(
        rng=random.Random(42),
        wildcard_manager=WildcardManager(),
    )


def test_ppp_set_basic(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:set x>hello<ppp:/set><ppp:echo x/>"), ctx)
    assert result == "hello"


def test_ppp_set_evaluate(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:set x evaluate>{a|b}<ppp:/set><ppp:echo x/>"), ctx)
    assert result in {"a", "b"}


def test_ppp_set_evaluate_fixed_value(ctx: EvaluationContext) -> None:
    t = parse("<ppp:set x evaluate>{a|b}<ppp:/set><ppp:echo x/> <ppp:echo x/>")
    result = evaluate(t, ctx)
    words = result.split()
    assert len(words) == 2
    assert words[0] == words[1]


def test_ppp_set_add(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:set x>hello<ppp:/set><ppp:set x add>-world<ppp:/set><ppp:echo x/>"), ctx)
    assert result == "hello-world"


def test_ppp_set_ifundefined(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse("<ppp:set x>first<ppp:/set><ppp:set x ifundefined>second<ppp:/set><ppp:echo x/>"),
        ctx,
    )
    assert result == "first"


def test_ppp_set_ifundefined_undefined(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:set x ifundefined>second<ppp:/set><ppp:echo x/>"), ctx)
    assert result == "second"


def test_ppp_echo_self_closing(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:set x>hello<ppp:/set><ppp:echo x/>"), ctx)
    assert result == "hello"


def test_ppp_echo_with_default(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:echo x>fallback<ppp:/echo>"), ctx)
    assert result == "fallback"


def test_ppp_echo_undefined_no_default(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:echo x/>"), ctx)
    assert result == ""


def test_ppp_if_truthy(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse("<ppp:set x>yes<ppp:/set><ppp:if x>matched<ppp:/if>"),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_falsy(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:if x>matched<ppp:/if>"), ctx)
    assert result == ""


def test_ppp_if_else(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:if x>matched<ppp:else>fallback<ppp:/if>"), ctx)
    assert result == "fallback"


def test_ppp_if_elif(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>b<ppp:/set><ppp:if x eq "a">a<ppp:elif x eq "b">b<ppp:else>c<ppp:/if>'),
        ctx,
    )
    assert result == "b"


def test_ppp_if_eq_string(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello<ppp:/set><ppp:if x eq "hello">matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_ne(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello<ppp:/set><ppp:if x ne "world">matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_not_eq(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello<ppp:/set><ppp:if x not eq "world">matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_contains(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello world<ppp:/set><ppp:if x contains "world">matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_in_list(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>b<ppp:/set><ppp:if x in ("a","b","c")>matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_gt(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse("<ppp:set x>10<ppp:/set><ppp:if x gt 5>matched<ppp:/if>"),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_and(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello<ppp:/set><ppp:set y>world<ppp:/set><ppp:if x eq "hello" and y eq "world">matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_or(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello<ppp:/set><ppp:if x eq "hello" or x eq "world">matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_not(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello<ppp:/set><ppp:if not x eq "world">matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_parens(ctx: EvaluationContext) -> None:
    result = evaluate(
        parse('<ppp:set x>hello<ppp:/set><ppp:set y>world<ppp:/set><ppp:if (x eq "hello" and y eq "world") or false>matched<ppp:/if>'),
        ctx,
    )
    assert result == "matched"


def test_ppp_if_combinatorial() -> None:
    results = evaluate_all(parse("<ppp:if a eq 1>x<ppp:elif a eq 2>y<ppp:/if>"))
    assert results == [""]


def test_ppp_set_combinatorial() -> None:
    results = evaluate_all(parse("<ppp:set x evaluate>{a|b}<ppp:/set><ppp:echo x/>"))
    assert sorted(results) == ["a", "b"]


def test_ppp_set_cyclical(ctx: EvaluationContext) -> None:
    result = cyclical_evaluate(parse("<ppp:set x>hello<ppp:/set><ppp:echo x/>"), ctx)
    assert result == "hello"


def test_ppp_if_cyclical(ctx: EvaluationContext) -> None:
    result = cyclical_evaluate(
        parse("<ppp:set x>yes<ppp:/set><ppp:if x>matched<ppp:/if>"),
        ctx,
    )
    assert result == "matched"


def test_ppp_stn_collects_content(ctx: EvaluationContext) -> None:
    result = evaluate(parse("hello <ppp:stn>badword<ppp:/stn> world"), ctx)
    assert result == "hello  world"
    assert len(ctx.stn_contents) == 1
    assert ctx.stn_contents[0] == (None, "badword")


def test_ppp_stn_with_position(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:stn e>append<ppp:/stn>"), ctx)
    assert result == ""
    assert ctx.stn_contents[0] == ("e", "append")


def test_ppp_ext_basic(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:ext lora test_lora/>"), ctx)
    assert result == "<lora:test_lora:1>"


def test_ppp_ext_with_weight(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:ext lora test_lora 0.5/>"), ctx)
    assert result == "<lora:test_lora:0.5>"


def test_ppp_ext_with_triggers(ctx: EvaluationContext) -> None:
    result = evaluate(parse("<ppp:ext lora test_lora>trigger word<ppp:/ext>"), ctx)
    assert result == "<lora:test_lora:1>trigger word"


def test_ppp_ext_condition_false(ctx: EvaluationContext) -> None:
    result = evaluate(parse('<ppp:ext lora test_lora if _is_pony/>'), ctx)
    assert result == ""


def test_ppp_ext_condition_true(ctx: EvaluationContext) -> None:
    ctx.resolved["_is_pony"] = "yes"
    result = evaluate(parse('<ppp:ext lora test_lora if _is_pony/>'), ctx)
    assert result == "<lora:test_lora:1>"
