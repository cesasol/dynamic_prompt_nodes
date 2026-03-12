from pathlib import Path

from dynamicprompts.wildcards import WildcardManager

BUNDLED_WILDCARDS_PATH = Path(__file__).parent.parent / "wildcards"


def get_wildcard_manager() -> WildcardManager:
    """Build a WildcardManager that searches bundled and ComfyUI model wildcards."""
    paths: list[Path] = [BUNDLED_WILDCARDS_PATH]
    try:
        import folder_paths  # type: ignore[import-not-found]

        for p in folder_paths.get_folder_paths("wildcards"):
            path = Path(p)
            if path not in paths:
                paths.append(path)
    except (ImportError, KeyError):
        pass
    existing = [p for p in paths if p.exists()]
    if not existing:
        return WildcardManager(path=BUNDLED_WILDCARDS_PATH)
    if len(existing) == 1:
        return WildcardManager(path=existing[0])
    return WildcardManager(root_map={"": existing})  # type: ignore[dict-item]
