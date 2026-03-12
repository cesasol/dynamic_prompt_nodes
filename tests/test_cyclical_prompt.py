import src.nodes.cyclical_prompt as cyclical_module


def test_cycles_through_values() -> None:
    node = cyclical_module.DynamicPromptCyclical()
    (r1,) = node.generate("{a|b|c}")
    (r2,) = node.generate("{a|b|c}")
    (r3,) = node.generate("{a|b|c}")
    (r4,) = node.generate("{a|b|c}")
    assert r1 == "a"
    assert r2 == "b"
    assert r3 == "c"
    assert r4 == "a"


def test_empty_template() -> None:
    node = cyclical_module.DynamicPromptCyclical()
    (result,) = node.generate("")
    assert result == ""


def test_plain_text() -> None:
    node = cyclical_module.DynamicPromptCyclical()
    (r1,) = node.generate("hello")
    (r2,) = node.generate("hello")
    assert r1 == "hello"
    assert r2 == "hello"
