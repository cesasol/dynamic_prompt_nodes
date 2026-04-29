import pytest

from src.evaluator.model_family import infer_model_family, build_system_variables
from src.nodes.prompt_with_wildcards import _merge_stn


class FakeSD1Model:
    class diffusion_model:
        in_channels = 4
        input_blocks = list(range(8))


class FakeSDXLModel:
    class diffusion_model:
        in_channels = 4
        input_blocks = list(range(9))


class FakeSD3Model:
    class diffusion_model:
        in_channels = 16


class FakeFluxModel:
    class diffusion_model:
        img_in = True


class FakeModelPatcher:
    def __init__(self, model: object) -> None:
        self.model = model


def test_infer_sd1():
    result = infer_model_family(FakeModelPatcher(FakeSD1Model))
    assert result == "sd1"


def test_infer_sdxl():
    result = infer_model_family(FakeModelPatcher(FakeSDXLModel))
    assert result == "sdxl"


def test_infer_sd3():
    result = infer_model_family(FakeModelPatcher(FakeSD3Model))
    assert result == "sd3"


def test_infer_flux():
    result = infer_model_family(FakeModelPatcher(FakeFluxModel))
    assert result == "flux"


def test_infer_unknown():
    result = infer_model_family(object())
    assert result == "unknown"


def test_build_system_variables_sdxl():
    vars = build_system_variables("sdxl", None)
    assert vars["_is_sdxl"] == "True"
    assert vars["_is_sd1"] == "False"
    assert vars["_is_pony"] == "False"
    assert vars["_is_illustrious"] == "False"


def test_build_system_variables_pony():
    vars = build_system_variables("sdxl", "pony")
    assert vars["_is_sdxl"] == "True"
    assert vars["_is_pony"] == "True"
    assert vars["_is_illustrious"] == "False"


def test_build_system_variables_sd1():
    vars = build_system_variables("sd1", None)
    assert vars["_is_sd"] == "True"
    assert vars["_is_sd1"] == "True"
    assert vars["_is_sdxl"] == "False"


def test_merge_stn_empty():
    assert _merge_stn("base", []) == "base"


def test_merge_stn_start():
    assert _merge_stn("base", [(None, "a"), ("s", "b")]) == "a, b, base"


def test_merge_stn_end():
    assert _merge_stn("base", [("e", "a")]) == "base, a"


def test_merge_stn_both():
    assert _merge_stn("base", [(None, "a"), ("e", "b")]) == "a, base, b"


def test_merge_stn_multiple():
    assert _merge_stn("base", [("e", "a"), ("e", "b")]) == "base, a, b"
