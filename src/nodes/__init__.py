from .combinatorial_prompt import NODE_CLASS_MAPPINGS as _combinatorial_classes
from .combinatorial_prompt import NODE_DISPLAY_NAME_MAPPINGS as _combinatorial_names
from .cyclical_prompt import NODE_CLASS_MAPPINGS as _cyclical_classes
from .cyclical_prompt import NODE_DISPLAY_NAME_MAPPINGS as _cyclical_names
from .prompt_with_wildcards import NODE_CLASS_MAPPINGS as _wildcard_classes
from .prompt_with_wildcards import NODE_DISPLAY_NAME_MAPPINGS as _wildcard_names
from .random_prompt import NODE_CLASS_MAPPINGS as _random_classes
from .random_prompt import NODE_DISPLAY_NAME_MAPPINGS as _random_names

NODE_CLASS_MAPPINGS = {**_random_classes, **_combinatorial_classes, **_cyclical_classes, **_wildcard_classes}
NODE_DISPLAY_NAME_MAPPINGS = {**_random_names, **_combinatorial_names, **_cyclical_names, **_wildcard_names}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
