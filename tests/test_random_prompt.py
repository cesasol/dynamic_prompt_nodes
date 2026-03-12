from pathlib import Path
import pytest
import dynamic_prompt_nodes.nodes.random_prompt as random_module


@pytest.fixture(autouse=True)
def patch_wildcards(wildcards_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(random_module, "WILDCARDS_PATH", wildcards_path)


def test_variant_produces_valid_result():
    node = random_module.DynamicPromptRandom()
    (result,) = node.generate("{cat|dog}", seed=0)
    assert result in {"cat", "dog"}


def test_same_seed_reproducible():
    node = random_module.DynamicPromptRandom()
    (r1,) = node.generate("{cat|dog}", seed=42)
    (r2,) = node.generate("{cat|dog}", seed=42)
    assert r1 == r2


def test_wildcard_resolution():
    node = random_module.DynamicPromptRandom()
    (result,) = node.generate("__animals__", seed=0)
    assert result in {"cat", "dog", "bird"}


def test_empty_template():
    node = random_module.DynamicPromptRandom()
    (result,) = node.generate("", seed=0)
    assert result == ""
