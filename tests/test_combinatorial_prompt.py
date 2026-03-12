import src.nodes.combinatorial_prompt as combinatorial_module


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


def test_wildcard_append_appends_syntax() -> None:
    node = combinatorial_module.DynamicPromptCombinatorial()
    prompt, all_prompts, total = node.generate("{a|b}", index=0, wildcard_append="animals")
    assert total == 6  # 2 variants × 3 animals
    assert all(p.split()[1] in {"cat", "dog", "bird"} for p in all_prompts)


def test_wildcard_append_none_sentinel() -> None:
    node = combinatorial_module.DynamicPromptCombinatorial()
    _, _, total = node.generate("{a|b}", index=0, wildcard_append="-- none --")
    assert total == 2
