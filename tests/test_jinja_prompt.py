import dynamic_prompt_nodes.src.nodes.jinja_prompt as jinja_module


def test_jinja_expression() -> None:
    node = jinja_module.DynamicPromptJinja()
    (result,) = node.generate('{{ ["cat", "dog"] | random }}', seed=0)
    assert result in {"cat", "dog"}


def test_wildcard_resolution() -> None:
    node = jinja_module.DynamicPromptJinja()
    (result,) = node.generate('{{ wildcard("animals") | random }}', seed=0)
    assert result in {"cat", "dog", "bird"}


def test_empty_template() -> None:
    node = jinja_module.DynamicPromptJinja()
    (result,) = node.generate("", seed=0)
    assert result == ""
