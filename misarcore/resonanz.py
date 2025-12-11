"""Resonanzstruktur und Log-Verwaltung für MiSarCore.

Dieses Modul stellt Hilfsfunktionen bereit, um die geforderten JSON-Logs
im Verzeichnis ``logs/`` zu initialisieren, zu erweitern und zu
kontextualisieren. Die Struktur bildet einen "Resonanzkern" mit
zusammenhängenden Branches für Resonanz, Impulse, Eventualitäten und
Werte-Markierungen, sodass ein LLM die Dateien direkt als
Langzeit-Kontext nutzen kann.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping
import json


ROOT_NAME = "Resonanzkern"


@dataclass(frozen=True)
class LogPaths:
    """Sammlung aller Log-Pfade für die Resonanzstruktur."""

    resonanz: Path
    impuls: Path
    eventualitaeten: Path
    werte: Path
    kontext: Path


def _default_markers() -> Dict[str, float]:
    return {
        "offenheit": 0.0,
        "sensibilitaet": 0.0,
        "konzentrationslevel": 0.0,
        "ruhe": 0.0,
        "unruhe": 0.0,
        "stabilitaet": 0.0,
    }


def _log_dir(base_path: Path | None = None) -> Path:
    root = base_path if base_path is not None else Path(__file__).resolve().parent.parent
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_or_init(path: Path, default_payload: Dict[str, Any]) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    _write_json(path, default_payload)
    return default_payload


def initialize_logs(base_path: Path | None = None) -> LogPaths:
    """Lege die benötigten JSON-Dateien mit Grundstruktur an.

    Die Funktion ist idempotent und überschreibt bestehende Dateien nicht.
    Sie stellt sicher, dass die Branch-Zuordnung und Meta-Informationen
    vorhanden sind, damit andere Komponenten direkt auf die Struktur
    zugreifen können.
    """

    logs_dir = _log_dir(base_path)
    paths = LogPaths(
        resonanz=logs_dir / "resonanz_log.json",
        impuls=logs_dir / "impuls_log.json",
        eventualitaeten=logs_dir / "eventualitaeten_log.json",
        werte=logs_dir / "werte_markierungen.json",
        kontext=logs_dir / "kontext_input.json",
    )

    _load_or_init(
        paths.resonanz,
        {
            "root": ROOT_NAME,
            "branch": "resonanz",
            "entries": [],
            "beschreibung": "Ereignisse mit starker innerer Resonanz.",
        },
    )

    _load_or_init(
        paths.impuls,
        {
            "root": ROOT_NAME,
            "branch": "impuls",
            "entries": [],
            "beschreibung": "Spontane Impulse und Richtungswechsel.",
        },
    )

    _load_or_init(
        paths.eventualitaeten,
        {
            "root": ROOT_NAME,
            "branch": "eventualitaeten",
            "entries": [],
            "beschreibung": "Mögliche Wege, Reaktionen und Szenarien.",
        },
    )

    _load_or_init(
        paths.werte,
        {
            "root": ROOT_NAME,
            "branch": "werte",
            "markers": _default_markers(),
            "history": [],
            "hinweis": "Werte werden inkrementell angepasst (positiv/negativ).",
        },
    )

    _load_or_init(
        paths.kontext,
        {
            "root": ROOT_NAME,
            "branch": "kontext",
            "meta": {"erstellt": datetime.utcnow().isoformat()},
            "letzte_snapshots": [],
        },
    )

    return paths


def _timestamp(ts: str | None = None) -> str:
    return ts if ts is not None else datetime.utcnow().replace(microsecond=0).isoformat()


def update_werte_markierungen(
    delta_markers: Mapping[str, float], base_path: Path | None = None
) -> Dict[str, Any]:
    """Passe die Markerwerte inkrementell an und protokolliere die Änderung."""

    logs = initialize_logs(base_path)
    payload = _load_or_init(
        logs.werte,
        {
            "root": ROOT_NAME,
            "branch": "werte",
            "markers": _default_markers(),
            "history": [],
        },
    )

    markers: MutableMapping[str, float] = payload.setdefault("markers", _default_markers())
    for name, delta in delta_markers.items():
        markers[name] = markers.get(name, 0.0) + float(delta)

    payload.setdefault("history", []).append(
        {"timestamp": _timestamp(), "delta": dict(delta_markers)}
    )
    _write_json(logs.werte, payload)
    return payload


def add_resonanz_event(
    event: str,
    resonanz: int,
    emotion: str,
    kommentar: str | None = None,
    werte_delta: Mapping[str, float] | None = None,
    timestamp: str | None = None,
    base_path: Path | None = None,
) -> Dict[str, Any]:
    """Füge dem Resonanz-Log ein Ereignis hinzu und aktualisiere Marker."""

    logs = initialize_logs(base_path)
    payload = _load_or_init(
        logs.resonanz,
        {"root": ROOT_NAME, "branch": "resonanz", "entries": []},
    )

    entry = {
        "timestamp": _timestamp(timestamp),
        "event": event,
        "resonanz": resonanz,
        "emotion": emotion,
    }
    if kommentar:
        entry["kommentar"] = kommentar
    if werte_delta:
        entry["werte"] = dict(werte_delta)
        update_werte_markierungen(werte_delta, base_path=base_path)

    payload.setdefault("entries", []).append(entry)
    _write_json(logs.resonanz, payload)
    return entry


def add_impuls(
    impulsart: str,
    trigger: str,
    uebertrag_in_werte: Mapping[str, float] | None = None,
    zeitpunkt: str | None = None,
    base_path: Path | None = None,
) -> Dict[str, Any]:
    """Halte einen spontanen Impuls fest und übertrage optional Markerwerte."""

    logs = initialize_logs(base_path)
    payload = _load_or_init(
        logs.impuls,
        {"root": ROOT_NAME, "branch": "impuls", "entries": []},
    )

    entry = {
        "timestamp": _timestamp(zeitpunkt),
        "impulsart": impulsart,
        "trigger": trigger,
    }
    if uebertrag_in_werte:
        entry["werte"] = dict(uebertrag_in_werte)
        update_werte_markierungen(uebertrag_in_werte, base_path=base_path)

    payload.setdefault("entries", []).append(entry)
    _write_json(logs.impuls, payload)
    return entry


def add_eventualitaet(
    ausgangslage: str,
    moegliche_wege: Mapping[str, str] | Mapping[str, Mapping[str, Any]],
    wahrscheinlichkeit: float,
    erwartete_resonanz: str | None = None,
    base_path: Path | None = None,
) -> Dict[str, Any]:
    """Speichere mögliche Wege oder Szenarien für spätere Entscheidungen."""

    logs = initialize_logs(base_path)
    payload = _load_or_init(
        logs.eventualitaeten,
        {"root": ROOT_NAME, "branch": "eventualitaeten", "entries": []},
    )

    entry = {
        "timestamp": _timestamp(),
        "ausgangslage": ausgangslage,
        "moegliche_wege": dict(moegliche_wege),
        "wahrscheinlichkeit": float(wahrscheinlichkeit),
    }
    if erwartete_resonanz:
        entry["erwartete_resonanz"] = erwartete_resonanz

    payload.setdefault("entries", []).append(entry)
    _write_json(logs.eventualitaeten, payload)
    return entry


def build_kontext_snapshot(limit_per_branch: int = 5, base_path: Path | None = None) -> Dict[str, Any]:
    """Erzeuge einen kompakten Kontext-Snapshot aus allen Branches."""

    logs = initialize_logs(base_path)

    resonanz = _load_or_init(logs.resonanz, {"entries": []})
    impuls = _load_or_init(logs.impuls, {"entries": []})
    eventualitaeten = _load_or_init(logs.eventualitaeten, {"entries": []})
    werte = _load_or_init(logs.werte, {"markers": _default_markers()})

    snapshot = {
        "root": ROOT_NAME,
        "generated_at": _timestamp(),
        "branches": {
            "resonanz": resonanz.get("entries", [])[-limit_per_branch:],
            "impuls": impuls.get("entries", [])[-limit_per_branch:],
            "eventualitaeten": eventualitaeten.get("entries", [])[-limit_per_branch:],
            "werte": werte.get("markers", {}),
        },
    }

    kontext_payload = _load_or_init(
        logs.kontext,
        {"root": ROOT_NAME, "branch": "kontext", "letzte_snapshots": []},
    )
    kontext_payload.setdefault("letzte_snapshots", []).append(snapshot)
    kontext_payload.setdefault("meta", {})["aktualisiert"] = snapshot["generated_at"]
    _write_json(logs.kontext, kontext_payload)
    return snapshot


__all__ = [
    "LogPaths",
    "add_eventualitaet",
    "add_impuls",
    "add_resonanz_event",
    "build_kontext_snapshot",
    "initialize_logs",
    "update_werte_markierungen",
]
