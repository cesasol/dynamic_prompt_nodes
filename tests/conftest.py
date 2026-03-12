import pytest
from pathlib import Path
from dynamicprompts.wildcards import WildcardManager

import src.wildcards as wildcards_mod


@pytest.fixture
def wildcards_path(tmp_path: Path) -> Path:
    (tmp_path / "animals.txt").write_text("cat\ndog\nbird\n")
    (tmp_path / "styles.yaml").write_text("painting:\n  - oil painting\n  - watercolor\n")
    return tmp_path


@pytest.fixture(autouse=True)
def patch_wildcards(wildcards_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wildcards_mod, "get_wildcard_manager", lambda: WildcardManager(path=wildcards_path))
