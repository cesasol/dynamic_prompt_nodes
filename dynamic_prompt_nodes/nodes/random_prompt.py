from pathlib import Path

from dynamicprompts.generators import RandomPromptGenerator
from dynamicprompts.wildcards import WildcardManager

WILDCARDS_PATH = Path(__file__).parent.parent / "wildcards"


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
            }
        }

    @classmethod
    def IS_CHANGED(cls, template: str, seed: int) -> int:
        return seed

    def generate(self, template: str, seed: int) -> tuple[str]:
        if not template.strip():
            return ("",)
        generator = RandomPromptGenerator(wildcard_manager=WildcardManager(path=WILDCARDS_PATH), seed=seed)
        results = generator.generate(template)
        return (results[0] if results else "",)


NODE_CLASS_MAPPINGS = {"DynamicPromptRandom": DynamicPromptRandom}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptRandom": "Dynamic Prompt (Random)"}
