from pathlib import Path
import pytest
import dynamic_prompt_nodes.nodes.jinja_prompt as jinja_module


@pytest.fixture(autouse=True)
def patch_wildcards(wildcards_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(jinja_module, "WILDCARDS_PATH", wildcards_path)


def test_jinja_expression():
    node = jinja_module.DynamicPromptJinja()
    (result,) = node.generate('{{ ["cat", "dog"] | random }}', seed=0)
    assert result in {"cat", "dog"}


def test_wildcard_resolution():
    node = jinja_module.DynamicPromptJinja()
    (result,) = node.generate('{{ wildcard("animals") | random }}', seed=0)
    assert result in {"cat", "dog", "bird"}


def test_empty_template():
    node = jinja_module.DynamicPromptJinja()
    (result,) = node.generate("", seed=0)
    assert result == ""
