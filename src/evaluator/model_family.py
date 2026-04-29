from __future__ import annotations


KNOWN_VARIANTS = {
    "pony",
    "illustrious",
    "anima",
    "noobai",
    "sd1",
    "sd2",
    "sdxl",
    "sd3",
    "flux",
    "auraflow",
}


def infer_model_family(model_patcher: object) -> str:
    """Best-effort model family inference from a ComfyUI ModelPatcher object.

    Returns one of the known families or "unknown". Specific variants like
    "pony" or "illustrious" cannot be detected without checkpoint metadata,
    so this returns the base architecture (e.g. "sdxl") and the caller can
    override with a user-supplied variant.
    """
    try:
        model = getattr(model_patcher, "model", model_patcher)
        if hasattr(model, "diffusion_model"):
            dm = model.diffusion_model
            # SD3 has 16 input channels
            in_ch = getattr(dm, "in_channels", None)
            if in_ch == 16:
                return "sd3"
            # Flux typically has specific attributes
            if hasattr(dm, "guidance_in") or hasattr(dm, "img_in"):
                return "flux"
            # Count input blocks to distinguish SD1 vs SDXL
            input_blocks = getattr(dm, "input_blocks", None)
            if input_blocks is not None:
                num_blocks = len(input_blocks)
                if num_blocks >= 9:
                    return "sdxl"
                return "sd1"
        # Fallback: check model_config if available
        model_config = getattr(model_patcher, "model_config", None)
        if model_config is not None:
            name = getattr(model_config, "name", "")
            if "sdxl" in name.lower():
                return "sdxl"
            if "sd3" in name.lower():
                return "sd3"
            if "flux" in name.lower():
                return "flux"
    except Exception:
        pass
    return "unknown"


def build_system_variables(base_family: str, variant: str | None) -> dict[str, str]:
    """Build the _is_* system variables dict for the evaluation context."""
    family = (variant or base_family).lower()
    variables: dict[str, str] = {}

    variables["_model"] = family

    # Base kind variables
    variables["_is_sd"] = str(family in ("sd1", "sd2", "sdxl", "sd3") or family.startswith(("sd1", "sd2", "sdxl", "sd3")))
    variables["_is_sd1"] = str(family == "sd1")
    variables["_is_sd2"] = str(family == "sd2")
    variables["_is_sdxl"] = str(family in ("sdxl", "pony", "illustrious", "anima", "noobai"))
    variables["_is_sd3"] = str(family == "sd3")
    variables["_is_flux"] = str(family == "flux")
    variables["_is_auraflow"] = str(family == "auraflow")

    # Variant-specific variables
    variables["_is_pony"] = str(family == "pony")
    variables["_is_illustrious"] = str(family == "illustrious")
    variables["_is_anima"] = str(family == "anima")
    variables["_is_noobai"] = str(family == "noobai")

    # Pure vs variant helpers
    variables["_is_pure_sdxl"] = str(family == "sdxl")
    variables["_is_variant_sdxl"] = str(family in ("pony", "illustrious", "anima", "noobai"))

    return variables
