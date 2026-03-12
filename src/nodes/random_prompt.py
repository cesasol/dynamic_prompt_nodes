import random

from src import wildcards as _wildcards
from src.evaluator.context import EvaluationContext
from src.evaluator.random_eval import evaluate
from src.parser.parser import parse


class DynamicPromptRandom:
    CATEGORY = "Dynamic Prompts"
    DESCRIPTION = (
        "Evaluates a dynamic prompt template using random sampling. "
        "Variants like {cat|dog|bird} pick one option at random. "
        "Wildcards like __animals__ are resolved from wildcard files. "
        "The seed controls reproducibility — the same seed always produces the same output. "
        "Use the wildcard dropdown to insert a wildcard into the template."
    )
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, object]:
        return {
            "required": {
                "template": ("STRING", {"multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**31 - 1}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, template: str, seed: int) -> int:
        return seed

    def generate(self, template: str, seed: int) -> tuple[str]:
        if not template.strip():
            return ("",)
        ast = parse(template)
        ctx = EvaluationContext(
            rng=random.Random(seed),
            wildcard_manager=_wildcards.get_wildcard_manager(),
        )
        return (evaluate(ast, ctx),)


NODE_CLASS_MAPPINGS = {"DynamicPromptRandom": DynamicPromptRandom}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptRandom": "Dynamic Prompt (Random)"}
