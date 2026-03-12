import sys
from pathlib import Path

_here = Path(__file__).parent

try:
    from .src.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
except ImportError:
    # Fallback for environments where this file is loaded without a parent package
    # (e.g., pytest package-setup walker). Add the project root to sys.path so that
    # absolute imports of src.* work.
    if str(_here) not in sys.path:
        sys.path.insert(0, str(_here))
    from src.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS  # type: ignore[import-not-found]

WILDCARDS_PATH = _here / "wildcards"

try:
    import folder_paths  # type: ignore[import-not-found]

    _models_wildcards = Path(folder_paths.models_dir) / "wildcards"
    folder_paths.add_model_folder_path("wildcards", str(_models_wildcards))
except (ImportError, AttributeError):
    pass

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
