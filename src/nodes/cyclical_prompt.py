import random

from src import wildcards as _wildcards
from src.evaluator.context import EvaluationContext
from src.evaluator.cyclical_eval import evaluate
from src.parser.ast_nodes import Template
from src.parser.parser import parse


class DynamicPromptCyclical:
    CATEGORY = "Dynamic Prompts"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate"

    def __init__(self) -> None:
        self._cycle_counters: dict[str, int] = {}
        self._last_template: str = ""
        self._ast: Template | None = None

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, object]:
        return {
            "required": {
                "template": ("STRING", {"multiline": True}),
                "wildcard_append": (_wildcards.wildcard_choices(),),
            }
        }

    @classmethod
    def IS_CHANGED(cls, template: str, wildcard_append: str) -> float:
        return float("nan")  # always re-execute

    def generate(self, template: str, wildcard_append: str = "-- none --") -> tuple[str]:
        if wildcard_append != "-- none --":
            template = template + " __" + wildcard_append + "__"
        if not template.strip():
            return ("",)
        # Re-parse only when template changes; reset counters so the cycle restarts
        if template != self._last_template:
            self._ast = parse(template)
            self._cycle_counters = {}
            self._last_template = template
        ctx = EvaluationContext(
            rng=random.Random(0),
            wildcard_manager=_wildcards.get_wildcard_manager(),
            cycle_counters=self._cycle_counters,
        )
        return (evaluate(self._ast, ctx),)  # type: ignore[arg-type]


NODE_CLASS_MAPPINGS = {"DynamicPromptCyclical": DynamicPromptCyclical}
NODE_DISPLAY_NAME_MAPPINGS = {"DynamicPromptCyclical": "Dynamic Prompt (Cyclical)"}
