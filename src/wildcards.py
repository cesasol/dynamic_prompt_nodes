from __future__ import annotations

import json
import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Iterator

BUNDLED_WILDCARDS_PATH = Path(__file__).parent.parent / "wildcards"


class WildcardManager:
    """Loads wildcard values from .txt, .yaml, and .json files in one or more directories.

    Wildcard names for .txt files are the file's path relative to the root, without extension
    (e.g. ``colours/dark.txt`` → ``colours/dark``).

    Wildcard names for .yaml/.json files are formed from the nested dict keys joined with ``/``,
    with any parent directory prefix prepended (the file name itself is not included).
    A top-level flat list uses the file stem as the name.

    Pattern matching in :meth:`get_all_values` uses ``fnmatch`` semantics (``*`` and ``?``).
    """

    def __init__(self, paths: list[Path] | None = None) -> None:
        self._index: dict[str, list[str]] = {}
        for path in paths or []:
            if path.is_dir():
                self._load_directory(path)

    def _load_directory(self, root: Path) -> None:
        for file_path in sorted(root.rglob("*")):
            if file_path.suffix == ".txt":
                rel = str(file_path.relative_to(root).with_suffix("")).replace(os.sep, "/")
                self._index.setdefault(rel, []).extend(self._read_txt(file_path))
            elif file_path.suffix in (".yaml", ".yml", ".json"):
                rel_parent = str(file_path.parent.relative_to(root)).replace(os.sep, "/")
                prefix = "" if rel_parent == "." else rel_parent + "/"
                for name, values in self._parse_structured(file_path):
                    self._index.setdefault(f"{prefix}{name}", []).extend(values)

    def _read_txt(self, path: Path) -> list[str]:
        return [
            line.strip()
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    def _parse_structured(self, path: Path) -> list[tuple[str, list[str]]]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix in (".yaml", ".yml"):
            import yaml

            data: Any = yaml.safe_load(text)
        else:
            data = json.loads(text)

        if not data:
            return []
        if isinstance(data, dict):
            return list(self._flatten_dict(data, prefix=()))
        if isinstance(data, list):
            values = [s for s in data if isinstance(s, str)]
            if values:
                return [(path.stem, values)]
        return []

    def _flatten_dict(self, data: dict[str, Any], prefix: tuple[str, ...]) -> Iterator[tuple[str, list[str]]]:
        for key, value in data.items():
            if not isinstance(key, str) or not value:
                continue
            full_key = (*prefix, key)
            name = "/".join(full_key)
            if isinstance(value, str):
                yield (name, [value])
            elif isinstance(value, list):
                values = [s for s in value if isinstance(s, str)]
                if values:
                    yield (name, values)
            elif isinstance(value, dict):
                yield from self._flatten_dict(value, prefix=full_key)

    def get_all_values(self, wildcard: str) -> list[str]:
        results: list[str] = []
        for name, values in self._index.items():
            if fnmatch(name, wildcard):
                results.extend(values)
        return results


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
    return WildcardManager(paths=[p for p in paths if p.exists()])
