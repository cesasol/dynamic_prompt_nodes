from pathlib import Path

from dynamicprompts.generators import CombinatorialPromptGenerator
from dynamicprompts.wildcards import WildcardManager

WILDCARDS_PATH = Path(__file__).parent.parent / "wildcards"


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
            }
        }

    def generate(self, template: str, index: int) -> tuple[str, list[str], int]:
        if not template.strip():
            return ("", [], 0)
        generator = CombinatorialPromptGenerator(wildcard_manager=WildcardManager(path=WILDCARDS_PATH))
        results = generator.generate(template)
        if not results:
            return ("", [], 0)
        prompt = results[index % len(results)]
        return (prompt, results, len(results))


NODE_CLASS_MAPPINGS = {"DynamicPromptCombinatorial": DynamicPromptCombinatorial}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptCombinatorial": "Dynamic Prompt (Combinatorial)"}
