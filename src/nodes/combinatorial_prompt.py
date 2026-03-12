import random

from src import wildcards as _wildcards
from src.evaluator.context import EvaluationContext
from src.evaluator.combinatorial_eval import evaluate_all
from src.parser.parser import parse


class DynamicPromptCombinatorial:
    CATEGORY = "Dynamic Prompts"
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
                "wildcard_append": (_wildcards.wildcard_choices(),),
            }
        }

    def generate(self, template: str, index: int, wildcard_append: str = "-- none --") -> tuple[str, list[str], int]:
        if wildcard_append != "-- none --":
            template = template + " __" + wildcard_append + "__"
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
