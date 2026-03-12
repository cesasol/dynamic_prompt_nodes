from pathlib import Path

from dynamicprompts.generators import JinjaGenerator
from dynamicprompts.wildcards import WildcardManager

WILDCARDS_PATH = Path(__file__).parent.parent / "wildcards"


class DynamicPromptJinja:
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
        generator = JinjaGenerator(wildcard_manager=WildcardManager(path=WILDCARDS_PATH))
        results = generator.generate(template)
        return (results[0] if results else "",)


NODE_CLASS_MAPPINGS = {"DynamicPromptJinja": DynamicPromptJinja}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptJinja": "Dynamic Prompt (Jinja2)"}
