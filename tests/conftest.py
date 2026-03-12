import pytest
from pathlib import Path


@pytest.fixture
def wildcards_path(tmp_path: Path) -> Path:
    (tmp_path / "animals.txt").write_text("cat\ndog\nbird\n")
    (tmp_path / "styles.yaml").write_text("painting:\n  - oil painting\n  - watercolor\n")
    return tmp_path
