# MiSar Resonance – Stand (External Memory Sandbox)

## Ziel
Ein externer Test-Speicherraum, in dem MiSar **nur über Intents** schreiben/lesen/ändern/löschen darf, **ausschließlich** innerhalb `external_memory_test/`.

## Was implementiert ist (Repo-Stand)
- Sandbox-Ordnerstruktur: `external_memory_test/{reflections,impulses,decisions,raw_logs,meta}`.
- Go IO Tool: `misar_resonance/io/file_manager.go` → Binary `misar-file-manager` (JSON über STDIN, `--base` Sandbox, Pfad-Escape-Schutz, erlaubte Endungen `.txt/.json/.md/.log`).
- Rust Gate Tool: `misar_resonance/intent_gate/` → Binary `misar-intent-gate` (validiert Intents und gibt `{allowed,strength,memory_relevance}` zurück).
- Python Integration:
  - Intent-Erzeugung: `misar_resonance/external_memory/intent_engine.py` (heuristisch, triggert v.a. über Wörter wie `schreib/notier/speicher/halte fest`).
  - Controller (Gate + IO + Rückkopplung): `misar_resonance/external_memory/controller.py`.
  - Orchestrator ruft External-Memory nach der LLM-Antwort best-effort auf: `misar_resonance/core/orchestrator.py`.

## Rückkopplung (wenn IO erfolgreich)
- Schreibt ein `system`-Event in die SQLite-Events und legt eine Episode an.
- Marker aus gelesen/geschriebenem Inhalt werden als Trait gespeichert.

## Tests
- `python3 -m unittest -q` ist grün.
- `tests/test_external_memory.py` deckt Write/Read/Modify/Delete + Sandbox-Escape ab.

## Beobachtungen / Probleme aus dem Betrieb
1. **“MiSar behauptet gespeichert, aber es existiert keine Datei”**
   - Ursache sehr wahrscheinlich: **kein Intent entsteht** (Trigger-Wording passt nicht), oder Gate blockt.
   - Der LLM bekommt nicht zuverlässig IO-Erfolg zurück und kann „gespeichert“ halluzinieren.

2. **Repetitions-/Loop-Verhalten im Chat (“*Code schweigt kurz…*” vervielfältigt sich)**
   - Sehr wahrscheinlich **Memory-Echo**: Assistant-Ausgaben werden persistiert und in späteren Turns wieder in den Kontext geladen → Muster verstärkt sich über Turns.
   - Workaround: mit frischer Session testen (`--session <neu>`), Regieanweisungen mit wiederholbarer Struktur vermeiden.

3. **Debug-Logfile `external_memory_test/raw_logs/file_actions.jsonl`**
   - Soll bei jeder ausgeführten IO-Aktion (und bei Gate-Block) geschrieben werden.
   - Wenn es nicht existiert: typischerweise wurde **kein Intent ausgeführt** oder es ist vor der Logging-Stelle abgebrochen.

## Verifizierungs-Snippets (praktisch)
- Neue Session ohne Alt-Context:
  - `python3 -m misar_resonance --session clean1`
- IO direkt prüfen (Go-Tool spricht `path` + `filename` getrennt):
  - `printf '%s\n' '{"action":"write","path":"reflections","filename":"test.txt","content":"hello","overwrite":true}' | ./misar_resonance/bin/misar-file-manager --base "$(pwd)/external_memory_test"`

## Commit-Historie (relevant)
- `1c0de30` – Add external memory sandbox with intent gating
- `37075b2` – Fix external memory writes and add debug log

## Nächste sinnvolle Schritte (wenn weitergemacht wird)
- Intent-Trigger für “nach außen / festhalten / trage” verbessern oder explizites User-Command-Format einführen.
- LLM-Antwort erst nach IO-Result “bestätigen” (oder zumindest keine Behauptung ohne Bestätigung).
- Optional: Mechanismus gegen Repetition (z.B. Filter/TTL für wiederholte Phrasen) oder Context-Sanitizing.

---

## Update (2025-12-27) – Lexicon Memory (zweite SQLite DB)

Ziel: Kurze, mehrdeutige Token-Eingaben (z.B. `muh`, `hm`, `ok`) persistent als Cluster speichern und bei Unsicherheit **rückfragen**, statt zu raten.

### Was neu ist
- Persistente Lexikon-DB: `external_memory_test/meta/lexicon.sqlite` (wird nicht automatisch zurückgesetzt).
- Python-Modul: `misar_resonance/lexicon/`
  - `db.py`: Schema + Feedback-Logging (Gewicht/Usage steigen bei Auswahl)
  - `normalize.py`: Normalisierung (u.a. `muuuuh`→`muh`, `rückzug`→`rueckzug`)
  - `match.py`: Exact/Prefix/Fuzzy Matching (Levenshtein-basiert, ohne externe deps)
  - `resolver.py`: Entscheidung `clarify` vs. `hint` + Pending-Disambiguation pro Session
  - `generator.py`: deterministischer Erst-Seed (~2000 Konzepte) + Showcase `muh` inkl. Aliases `moh`/`mih`
- Integration in `misar_resonance/core/orchestrator.py` **vor** dem LLM:
  - Bei Mehrdeutigkeit: direkt eine Klärungsfrage (ohne LLM-Call), und Pending-State als Trait in der Haupt-Events-DB.
  - Bei Klarheit: kurzer System-Hinweis an das LLM (ohne den External-Memory-Controller zu verändern).

### Demo & Tests
- Demo: `python3 -m misar_resonance.lexicon.demo "moh"` (zeigt Kandidaten + ob Rückfrage gestellt wird).
- Reset nur explizit: `python3 -m misar_resonance.lexicon.demo --reset "moh"`.
- Tests ergänzt: `tests/test_lexicon.py`; `python3 -m unittest -q` bleibt grün.

---

## Update (2025-12-27) – Interaction Modes (Buddy/Help) + Anti-Echo

Ziel: MiSar ist standardmäßig **Buddy** (kumpelhaft, keine ungefragten Pläne/Coaching). **Help** passiert nur bei explizitem Trigger und fällt danach wieder auf Buddy zurück.

### Was neu ist
- Modus-Konzept + Trigger: `misar_resonance/core/interaction_mode.py` (Kommandos/Phrasen/Codewort + Priorität).
- Persona-Regeln pro Modus: `misar_resonance/core/persona.py` (BUDDY Default, HELP nur auf Kommando).
- Session-State: `interaction_mode:{session}` als Trait in der bestehenden SQLite-DB (`MemoryStore`).
- Integration in den Prompt-Bau: `misar_resonance/core/orchestrator.py` + `misar_resonance/core/prompt_composer.py`.

### Trigger (robust, simpel)
- HELP: `/help`, `/assist`, oder klare Bitten wie „hilf mir“, „erklär mir“, „mach mir“, „gib mir“, „bitte lös/schreib/plan“, oder Codewort `Helfermodus!`
- BUDDY: `/buddy`, `/chill`, oder Codewort `Chillmodus!`
- Auto-Return: HELP wird standardmäßig nur für den aktuellen Turn aktiviert und fällt danach wieder auf Buddy zurück (im Zweifel lieber Buddy).

### Anti-Echo / Anti-Regie
- Stage-Directions/Style-Marker wie `*schweigt kurz*` werden beim **Kontext-Reinladen** (Memory/Episodes) aus dem Prompt entfernt.
- Kurze identische Assistant-Zeilen werden innerhalb eines Context-Windows dedupliziert, um Wiederholungen nicht zu verstärken.

### Tests & Doku
- Tests ergänzt: `tests/test_interaction_mode.py` (Trigger, Priorität, Auto-Return, Anti-Echo).
- Doku ergänzt: `README.md` (Mode-Switch + `python3 -m unittest -q`).

### Commit-Historie (relevant)
- `112580f` – Add interaction mode primitives
- `ed12983` – Apply buddy/help mode to prompt
- `aba4f41` – Add tests for mode triggers
- `926676b` – Document buddy/help mode switching
