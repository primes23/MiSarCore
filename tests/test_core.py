"""Tests for the `misarcore.core` module."""

import pytest

from misarcore import greet


def test_greet_returns_expected_message() -> None:
    """Greet should return a friendly greeting with the provided name."""
    assert greet("Micha") == "Hello, Micha! Welcome to MiSarCore."
    assert greet("  anna  ") == "Hello, Anna! Welcome to MiSarCore."


def test_greet_raises_type_error_for_non_string() -> None:
    """Greet should raise a TypeError when the argument is not a string."""
    with pytest.raises(TypeError):
        greet(42)  # type: ignore[arg-type]
