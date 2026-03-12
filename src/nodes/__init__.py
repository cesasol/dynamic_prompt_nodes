from .combinatorial_prompt import NODE_CLASS_MAPPINGS as _combinatorial_classes
from .combinatorial_prompt import NODE_DISPLAY_NAME_MAPPINGS as _combinatorial_names
from .jinja_prompt import NODE_CLASS_MAPPINGS as _jinja_classes
from .jinja_prompt import NODE_DISPLAY_NAME_MAPPINGS as _jinja_names
from .random_prompt import NODE_CLASS_MAPPINGS as _random_classes
from .random_prompt import NODE_DISPLAY_NAME_MAPPINGS as _random_names

NODE_CLASS_MAPPINGS = {**_random_classes, **_combinatorial_classes, **_jinja_classes}
NODE_DISPLAY_NAME_MAPPINGS = {**_random_names, **_combinatorial_names, **_jinja_names}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
