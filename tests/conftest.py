import pytest
from pathlib import Path

import src.wildcards as wildcards_mod
from src.wildcards import WildcardManager


@pytest.fixture
def wildcards_path(tmp_path: Path) -> Path:
    (tmp_path / "animals.txt").write_text("cat\ndog\nbird\n")
    (tmp_path / "styles.yaml").write_text("painting:\n  - oil painting\n  - watercolor\n")
    return tmp_path


@pytest.fixture(autouse=True)
def patch_wildcards(wildcards_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wildcards_mod, "get_wildcard_manager", lambda: WildcardManager(paths=[wildcards_path]))
