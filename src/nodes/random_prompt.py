import random

from src import wildcards as _wildcards
from src.evaluator.context import EvaluationContext
from src.evaluator.random_eval import evaluate
from src.parser.parser import parse


class DynamicPromptRandom:
    CATEGORY = "Dynamic Prompts"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, object]:
        return {
            "required": {
                "template": ("STRING", {"multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**31 - 1}),
                "wildcard_append": (_wildcards.wildcard_choices(),),
            }
        }

    @classmethod
    def IS_CHANGED(cls, template: str, seed: int, wildcard_append: str) -> int:
        return seed

    def generate(self, template: str, seed: int, wildcard_append: str = "-- none --") -> tuple[str]:
        if wildcard_append != "-- none --":
            template = template + " __" + wildcard_append + "__"
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
