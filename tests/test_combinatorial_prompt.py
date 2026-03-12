from pathlib import Path
import pytest
import dynamic_prompt_nodes.nodes.combinatorial_prompt as combinatorial_module


@pytest.fixture(autouse=True)
def patch_wildcards(wildcards_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(combinatorial_module, "WILDCARDS_PATH", wildcards_path)


def test_index_0():
    node = combinatorial_module.DynamicPromptCombinatorial()
    prompt, _, total = node.generate("{a|b}", index=0)
    assert prompt == "a"
    assert total == 2


def test_index_1():
    node = combinatorial_module.DynamicPromptCombinatorial()
    prompt, _, _ = node.generate("{a|b}", index=1)
    assert prompt == "b"


def test_all_prompts_length():
    node = combinatorial_module.DynamicPromptCombinatorial()
    _, all_prompts, total = node.generate("{a|b}", index=0)
    assert len(all_prompts) == 2
    assert total == 2


def test_index_wraps():
    node = combinatorial_module.DynamicPromptCombinatorial()
    prompt, _, _ = node.generate("{a|b}", index=2)
    assert prompt == "a"


def test_empty_template():
    node = combinatorial_module.DynamicPromptCombinatorial()
    result = node.generate("", index=0)
    assert result == ("", [], 0)
