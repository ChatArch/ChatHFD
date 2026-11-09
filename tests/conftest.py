from pathlib import Path
import sys

import pytest


@pytest.fixture(autouse=True)
def isolate_download_configuration(monkeypatch, tmp_path):
    monkeypatch.setenv("CHATARCH_HOME", str(tmp_path / "chatarch-home"))
    monkeypatch.delenv("CHATHFD_DOWNLOAD_ROOT", raising=False)


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
