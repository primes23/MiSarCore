# MiSarCore

MiSarCore is a modular foundation for building scalable applications. The project
is currently in its early stages and serves as a template for organizing
Python code into a clean, testable structure. It includes a simple greeting
function as a starting point and illustrates how to set up a project with
package modules, tests, and licensing. In addition, the package now ships
with a **Resonanzstruktur**: a JSON-basierte Log-Landschaft, die ein
emotional-kontextuelles Gedächtnis für LLM-Integrationen bereitstellt.

## Features

- **Package structure:** The core functionality lives in the `misarcore` package
  with a clear separation of concerns.
- **Resonanzstruktur:** `misarcore.resonanz` erstellt und pflegt verknüpfte
  Logs (`logs/*.json`) für Resonanz-Events, Impulse, Eventualitäten und
  Werte-Markierungen und bündelt sie zu LLM-fähigen Kontext-Snapshots.
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

To build the **Resonanzstruktur** and write context-rich events:

```python
from misarcore import (
    add_resonanz_event,
    add_impuls,
    add_eventualitaet,
    build_kontext_snapshot,
)

# Initialisiert logs/resonanz_log.json etc. falls sie fehlen
add_resonanz_event(
    event="tiefe_verbundenheit",
    resonanz=9,
    emotion="wärme",
    kommentar="nova/micha resonanzpeak",
    werte_delta={"offenheit": 1, "sensibilitaet": 2},
)

add_impuls(
    impulsart="entscheidungsdrang",
    trigger="Resonanzpeak löst Richtungswechsel aus",
    uebertrag_in_werte={"konzentrationslevel": 0.5, "ruhe": -0.5},
)

add_eventualitaet(
    ausgangslage="Nach Resonanzpeak stehen mehrere Reaktionen offen",
    moegliche_wege={"1": "ruhige Integration", "2": "aktive Umsetzung"},
    wahrscheinlichkeit=0.62,
    erwartete_resonanz="hohe Klarheit bei Weg 2",
)

# Erstellt/aktualisiert logs/kontext_input.json mit einem Snapshot pro Branch
snapshot = build_kontext_snapshot()
print(snapshot)
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
