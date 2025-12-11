"""Core module for MiSarCore.

This module defines the primary functionality exposed by the MiSarCore
package. Currently, it provides a simple greeting function. As the
project evolves, more complex logic and features can be added here.
"""
from __future__ import annotations


def greet(name: str) -> str:
    """Return a friendly greeting for the given name.

    Parameters
    ----------
    name: str
        The name of the person to greet.

    Returns
    -------
    str
        A greeting message personalized with the provided name.

    Examples
    --------
    >>> greet("Micha")
    'Hello, Micha! Welcome to MiSarCore.'
    """
    if not isinstance(name, str):
        raise TypeError(f"Expected name to be a string, got {type(name).__name__}")
    # Strip leading/trailing whitespace and capitalize the name for a tidy greeting.
    clean_name = name.strip().title()
    return f"Hello, {clean_name}! Welcome to MiSarCore."



def _main() -> None:
    """Entry point for command-line execution.

    This function demonstrates a simple interaction with the greet function.
    It can be extended to parse command-line arguments or provide a CLI.
    """
    import sys

    if len(sys.argv) > 1:
        name_arg = sys.argv[1]
    else:
        name_arg = "World"
    print(greet(name_arg))



if __name__ == "__main__":
    _main()
