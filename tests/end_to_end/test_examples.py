"""The published examples all run through the same public SDK."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "relative_path",
    [
        "examples/novel_adapter/example.py",
        "examples/software_change/example.py",
        "examples/research_change/example.py",
    ],
)
def test_example_runs(relative_path: str) -> None:
    """Each example produces a serialized impact report without external services."""
    root = Path(__file__).parents[2]
    completed = subprocess.run(
        [sys.executable, str(root / relative_path)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "impacts" in completed.stdout
