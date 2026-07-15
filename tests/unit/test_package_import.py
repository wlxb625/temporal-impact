"""Smoke tests for the initialized package."""

import temporal_impact


def test_package_imports() -> None:
    """The package can be imported after installation."""
    assert temporal_impact.__version__ == "0.1.0a0"
