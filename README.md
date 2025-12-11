# MiSarCore

MiSarCore is a modular foundation for building scalable applications. The project
is currently in its early stages and serves as a template for organizing
Python code into a clean, testable structure. It includes a simple greeting
function as a starting point and illustrates how to set up a project with
package modules, tests, and licensing.

## Features

- **Package structure:** The core functionality lives in the `misarcore` package
  with a clear separation of concerns.
- **Unit tests:** The `tests` package contains unit tests using
  [`pytest`](https://docs.pytest.org/) to ensure code reliability.
- **MIT license:** The project is open-sourced under the permissive MIT
  license.

## Getting started

To experiment with the provided functionality, you can run the module directly
or import it into your own scripts.

```bash
git clone https://github.com/primes23/MiSarCore.git
cd MiSarCore
python -m misarcore.core Micha
```

Alternatively, import the `greet` function in your Python code:

```python
from misarcore import greet

print(greet("World"))  # Hello, World! Welcome to MiSarCore.
```

## Running tests

This project uses `pytest` for unit testing. To run the tests, install
pytest (e.g., `pip install pytest`) and execute:

```bash
pytest
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE)
file for details.
