import pytest
from src.parser.parser import parse
from src.parser.ast_nodes import Template, Text, Variant, WeightedOption, Wildcard, Variable


def test_plain_text():
    result = parse("hello world")
    assert isinstance(result, Template)
    assert len(result.parts) == 1
    assert isinstance(result.parts[0], Text)
    assert result.parts[0].value == "hello world"


def test_simple_variant():
    result = parse("{a|b|c}")
    assert len(result.parts) == 1
    v = result.parts[0]
    assert isinstance(v, Variant)
    assert v.min_count == 1
    assert v.max_count == 1
    assert v.sampler == "random"
    assert len(v.options) == 3
    assert v.options[0].node.parts[0].value == "a"
    assert v.options[1].node.parts[0].value == "b"
    assert v.options[2].node.parts[0].value == "c"


def test_text_with_variant():
    result = parse("A {big|small} dog")
    assert len(result.parts) == 3
    assert isinstance(result.parts[0], Text)
    assert isinstance(result.parts[1], Variant)
    assert isinstance(result.parts[2], Text)


def test_variant_default_weight():
    result = parse("{a|b}")
    v = result.parts[0]
    assert all(opt.weight == 1.0 for opt in v.options)


def test_empty_template():
    result = parse("")
    assert isinstance(result, Template)
    assert result.parts == []
