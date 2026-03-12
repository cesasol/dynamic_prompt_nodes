from pathlib import Path

from .src.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WILDCARDS_PATH = Path(__file__).parent / "wildcards"

try:
    import folder_paths  # type: ignore[import-not-found]

    _models_wildcards = Path(folder_paths.models_dir) / "wildcards"
    folder_paths.add_model_folder_path("wildcards", str(_models_wildcards))
except (ImportError, AttributeError):
    pass

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
