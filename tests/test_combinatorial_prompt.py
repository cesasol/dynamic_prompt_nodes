import dynamic_prompt_nodes.src.nodes.combinatorial_prompt as combinatorial_module


def test_index_0() -> None:
    node = combinatorial_module.DynamicPromptCombinatorial()
    prompt, _, total = node.generate("{a|b}", index=0)
    assert prompt == "a"
    assert total == 2


def test_index_1() -> None:
    node = combinatorial_module.DynamicPromptCombinatorial()
    prompt, _, _ = node.generate("{a|b}", index=1)
    assert prompt == "b"


def test_all_prompts_length() -> None:
    node = combinatorial_module.DynamicPromptCombinatorial()
    _, all_prompts, total = node.generate("{a|b}", index=0)
    assert len(all_prompts) == 2
    assert total == 2


def test_index_wraps() -> None:
    node = combinatorial_module.DynamicPromptCombinatorial()
    prompt, _, _ = node.generate("{a|b}", index=2)
    assert prompt == "a"


def test_empty_template() -> None:
    node = combinatorial_module.DynamicPromptCombinatorial()
    result = node.generate("", index=0)
    assert result == ("", [], 0)
