from pathlib import Path

from src.wildcards import WildcardManager


def test_list_names_returns_sorted(wildcards_path: Path) -> None:
    wm = WildcardManager(paths=[wildcards_path])
    assert wm.list_names() == ["animals", "painting"]


def test_list_names_empty() -> None:
    wm = WildcardManager(paths=[])
    assert wm.list_names() == []
