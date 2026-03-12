import dynamic_prompt_nodes.src.nodes.random_prompt as random_module


def test_variant_produces_valid_result() -> None:
    node = random_module.DynamicPromptRandom()
    (result,) = node.generate("{cat|dog}", seed=0)
    assert result in {"cat", "dog"}


def test_same_seed_reproducible() -> None:
    node = random_module.DynamicPromptRandom()
    (r1,) = node.generate("{cat|dog}", seed=42)
    (r2,) = node.generate("{cat|dog}", seed=42)
    assert r1 == r2


def test_wildcard_resolution() -> None:
    node = random_module.DynamicPromptRandom()
    (result,) = node.generate("__animals__", seed=0)
    assert result in {"cat", "dog", "bird"}


def test_empty_template() -> None:
    node = random_module.DynamicPromptRandom()
    (result,) = node.generate("", seed=0)
    assert result == ""
