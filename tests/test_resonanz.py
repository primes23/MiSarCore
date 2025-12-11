from pathlib import Path
import json

import pytest

from misarcore.resonanz import (
    add_eventualitaet,
    add_impuls,
    add_resonanz_event,
    build_kontext_snapshot,
    initialize_logs,
    update_werte_markierungen,
)


def test_initialize_and_marker_updates(tmp_path: Path) -> None:
    paths = initialize_logs(tmp_path)

    assert paths.resonanz.exists()
    assert paths.werte.exists()

    update_werte_markierungen({"offenheit": 1, "ruhe": -0.5}, base_path=tmp_path)
    payload = json.loads(paths.werte.read_text(encoding="utf-8"))

    assert payload["markers"]["offenheit"] == 1
    assert payload["markers"]["ruhe"] == -0.5
    assert len(payload["history"]) == 1


def test_append_events_and_snapshot(tmp_path: Path) -> None:
    initialize_logs(tmp_path)

    add_resonanz_event(
        event="test_resonanz",
        resonanz=7,
        emotion="klarheit",
        werte_delta={"sensibilitaet": 0.5},
        base_path=tmp_path,
    )
    add_impuls(
        impulsart="umlenkung",
        trigger="externer input",
        zeitpunkt="2025-01-01T00:00:00",
        base_path=tmp_path,
    )
    add_eventualitaet(
        ausgangslage="entscheidungspunkt",
        moegliche_wege={"1": "pause", "2": "weiter"},
        wahrscheinlichkeit=0.5,
        base_path=tmp_path,
    )

    snapshot = build_kontext_snapshot(limit_per_branch=2, base_path=tmp_path)

    assert snapshot["branches"]["resonanz"][0]["event"] == "test_resonanz"
    assert snapshot["branches"]["impuls"][0]["impulsart"] == "umlenkung"
    assert snapshot["branches"]["eventualitaeten"][0]["ausgangslage"] == "entscheidungspunkt"
    assert snapshot["branches"]["werte"]["sensibilitaet"] == pytest.approx(0.5)
