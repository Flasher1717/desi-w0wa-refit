"""Shared pytest configuration.

Tests marked ``requires_data`` are external-anchor tests; they auto-skip
when the ``data/`` directory (populated only by scripts/download_data.py)
is absent, so the suite stays green on a fresh clone and in CI.
"""

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    del config
    if DATA_DIR.is_dir():
        return
    skip_marker = pytest.mark.skip(reason="data/ absent (run scripts/download_data.py)")
    for item in items:
        if "requires_data" in item.keywords:
            item.add_marker(skip_marker)
