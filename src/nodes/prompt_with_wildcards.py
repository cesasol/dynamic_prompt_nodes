from __future__ import annotations
import random

from src import wildcards as _wildcards
from src.evaluator.context import EvaluationContext
from src.evaluator.model_family import infer_model_family, build_system_variables
from src.evaluator.random_eval import evaluate
from src.nodes.cleanup import cleanup_prompt
from src.parser.parser import parse


class PromptWithWildcards:
    CATEGORY = "Dynamic Prompts"
    DESCRIPTION = (
        "Processes positive and negative prompt templates with full PPP tag support. "
        "Infers model family for conditional tags like <ppp:if _is_pony>. "
        "Collects <ppp:stn> content from positive into negative. "
        "Generates <ppp:ext> as <lora:...> tags."
    )
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "process"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, object]:
        return {
            "required": {
                "model": ("MODEL",),
                "positive_template": ("STRING", {"multiline": True}),
                "negative_template": ("STRING", {"multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**31 - 1}),
                "ignore_repeats": ("BOOLEAN", {"default": False}),
                "cleanup_extra_spaces": ("BOOLEAN", {"default": False}),
                "cleanup_empty_constructs": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "model_variant": (
                    "STRING",
                    {"default": "", "multiline": False},
                ),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs: object) -> int:
        return kwargs.get("seed", 0)  # type: ignore[return-value]

    def process(
        self,
        model: object,
        positive_template: str,
        negative_template: str,
        seed: int,
        ignore_repeats: bool,
        cleanup_extra_spaces: bool,
        cleanup_empty_constructs: bool,
        model_variant: str = "",
    ) -> tuple[str, str]:
        base_family = infer_model_family(model)
        variant = model_variant.strip() or None
        sys_vars = build_system_variables(base_family, variant)

        rng = random.Random(seed)
        wm = _wildcards.get_wildcard_manager()

        ctx_pos = EvaluationContext(rng=rng, wildcard_manager=wm)
        ctx_pos.resolved.update(sys_vars)
        positive = (
            evaluate(parse(positive_template), ctx_pos)
            if positive_template.strip()
            else ""
        )

        ctx_neg = EvaluationContext(rng=rng, wildcard_manager=wm)
        ctx_neg.resolved.update(sys_vars)
        negative = (
            evaluate(parse(negative_template), ctx_neg)
            if negative_template.strip()
            else ""
        )

        negative = _merge_stn(negative, ctx_pos.stn_contents)

        positive = cleanup_prompt(
            positive,
            ignore_repeats=ignore_repeats,
            cleanup_extra_spaces=cleanup_extra_spaces,
            cleanup_empty_constructs=cleanup_empty_constructs,
        )
        negative = cleanup_prompt(
            negative,
            ignore_repeats=ignore_repeats,
            cleanup_extra_spaces=cleanup_extra_spaces,
            cleanup_empty_constructs=cleanup_empty_constructs,
        )

        return (positive, negative)


def _merge_stn(negative: str, stn_contents: list[tuple[str | None, str]]) -> str:
    if not stn_contents:
        return negative
    start_parts: list[str] = []
    end_parts: list[str] = []
    for position, content in stn_contents:
        if position == "e":
            end_parts.append(content)
        else:
            start_parts.append(content)
    parts: list[str] = []
    if start_parts:
        parts.extend(start_parts)
    if negative:
        parts.append(negative)
    if end_parts:
        parts.extend(end_parts)
    return ", ".join(parts)


NODE_CLASS_MAPPINGS = {"PromptWithWildcards": PromptWithWildcards}
NODE_DISPLAY_NAME_MAPPINGS = {"PromptWithWildcards": "Prompt with Wildcards"}
