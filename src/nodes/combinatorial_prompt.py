import random

from src import wildcards as _wildcards
from src.evaluator.context import EvaluationContext
from src.evaluator.combinatorial_eval import evaluate_all
from src.parser.parser import parse


class DynamicPromptCombinatorial:
    CATEGORY = "Dynamic Prompts"
    DESCRIPTION = (
        "Generates every possible combination from a dynamic prompt template. "
        "Variants like {a|b} are expanded exhaustively — {a|b} {x|y} produces a x, a y, b x, b y. "
        "Wildcards like __colours__ insert every value from the wildcard file. "
        "Outputs the full list of prompts, the total count, and the single prompt at the given index "
        "(wraps around if index exceeds total)."
    )
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("prompt", "all_prompts", "total_count")
    OUTPUT_IS_LIST = (False, True, False)
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, object]:
        return {
            "required": {
                "template": ("STRING", {"multiline": True}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2**31 - 1}),
            }
        }

    def generate(self, template: str, index: int) -> tuple[str, list[str], int]:
        if not template.strip():
            return ("", [], 0)
        ast = parse(template)
        ctx = EvaluationContext(
            rng=random.Random(0),
            wildcard_manager=_wildcards.get_wildcard_manager(),
        )
        results = evaluate_all(ast, ctx)
        if not results:
            return ("", [], 0)
        prompt = results[index % len(results)]
        return (prompt, results, len(results))


NODE_CLASS_MAPPINGS = {"DynamicPromptCombinatorial": DynamicPromptCombinatorial}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptCombinatorial": "Dynamic Prompt (Combinatorial)"}
