from pathlib import Path

import pytest

from src.wildcards import WildcardManager, wildcard_choices


def test_list_names_returns_sorted(wildcards_path: Path) -> None:
    wm = WildcardManager(paths=[wildcards_path])
    assert wm.list_names() == ["animals", "painting"]


def test_list_names_empty() -> None:
    wm = WildcardManager(paths=[])
    assert wm.list_names() == []


def test_wildcard_choices_sentinel_first(wildcards_path: Path) -> None:
    choices = wildcard_choices()
    assert choices[0] == "-- none --"
    assert "animals" in choices
    assert "painting" in choices
