"""Reproduce all 36 paired runs and check committed evidence (offline, stdlib only)."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

from evaluate import CRITICAL

ROOT = Path(__file__).resolve().parent
PROFILES = {"low": (3, .05), "default": (6, .28), "stress": (18, .40)}


def deterministic(records):
    records = deepcopy(records)
    for record in records:
        for run in record["runs"]:
            run.pop("median_local_core_ms", None)
    return records


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(records):
    require([record["scenario"] for record in records] == list(PROFILES), "Wrong scenario set/order")
    for record in records:
        require((record["daily_deals"], record["injected_rate"]) == PROFILES[record["scenario"]],
                "Scenario parameters changed")
        require([run["seed"] for run in record["runs"]] == list(range(20261112, 20261124)),
                "Expected twelve pre-specified exploratory seeds per profile")
        for run in record["runs"]:
            require(run["metrics"]["workflow"] == run["metrics"]["table"], "Methods disagree")
            for method, metrics in run["metrics"].items():
                count = metrics["obligation_day_evaluations"]
                require(count > 0, "Empty evaluation")
                require(metrics["exact_status_matches"] == count, f"{method}: status mismatch")
                require(metrics["exact_alert_set_matches"] == count, f"{method}: alert mismatch")
                require(metrics["missed_critical_alert_snapshots"] == 0, f"{method}: missed alert")
                require(metrics["false_alert_snapshots"] == 0, f"{method}: false alert")
                require(set(metrics["by_alert"]) == CRITICAL, "Missing alert category")
                for counts in metrics["by_alert"].values():
                    require(counts["occurred_events"] == counts["detected_events"], "Missed event")
                    require(counts["missed_events"] == counts["false_alert_episodes"] == 0, "Event error")
                    require(counts["max_detection_delay_days"] == (0 if counts["detected_events"] else None),
                            "Detection delay or undefined denominator error")


def render(records):
    total = sum(run["metrics"]["workflow"]["obligation_day_evaluations"]
                for record in records for run in record["runs"])
    lines = ["# Ergebnisse der HubSpot–Stripe-Studie", "",
             "Revision 2 – reproduzierbare Implementierung, 12. November 2026.", "",
             f"36 gepaarte Läufe × 100 simulierte Geschäftstage; {total:,} Verpflichtungs-Tagesbewertungen je Methode.",
             "Beide Methoden stimmen in Status **und vollständiger Alertmenge** exakt mit der Modellreferenz überein.",
             "Keine übersehenen kritischen Meldungen, Fehlalarmepisoden oder Verzögerungen auf diesen Eingaben.",
             "Wiederholte Snapshots sind abhängig. Diese Simulation belegt keine betriebliche Fehlerquote oder menschliche Zeitersparnis.", "",
             "## Wirtschaftlichkeit", "",
             "Illustrative Annahmen je 100 Geschäftstage: 5 Minuten Tabellenrefresh/Tag, 60 Minuten Aufsicht/Pflege,",
             "1 zusätzliche Minute je eindeutigem Verpflichtungs-/Alerttyp-Paar, 40 EUR/Stunde, 20 EUR Betriebskosten.", "",
             "| Profil | Verpflichtungs-Tagesbewertungen | Median Alertpaare | Kapazitätswert EUR | Nullschwelle min/Paar | 100-EUR-Schwelle min/Paar |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for record in records:
        runs = record["runs"]
        economic = next(row for row in record["economics"] if row["manual_batch_minutes_per_day"] == 5
                        and row["extra_workflow_minutes_per_alert"] == 1)
        count = sum(run["metrics"]["workflow"]["obligation_day_evaluations"] for run in runs)
        pairs = median(run["metrics"]["workflow"]["unique_obligation_alert_pairs"] for run in runs)
        lines.append(f"| {record['scenario']} | {count} | {pairs:.1f} | {economic['net_capacity_eur']:.2f} | "
                     f"{economic['break_even_extra_minutes_per_alert']:.2f} | {economic['hurdle_100_eur_extra_minutes_per_alert']:.2f} |")
    lines += ["", "Die Schwellen werden am medianen Alertpaar-Aufkommen berechnet; sie sind nicht der Median laufweiser Quotienten.",
              "Implementierungskosten sind im Kapazitätswert nicht enthalten. Amortisation bei positivem Wert V und Investition I:",
              "100 × I / V Geschäftstage, unter konstanten Annahmen und voller wirtschaftlicher Nutzung der freigesetzten Zeit.", "",
              "## Streuung über vollständige Läufe", "",
              "Min/Median/Max beschreiben die zwölf Läufe je Profil; dies sind keine Konfidenzintervalle.", "",
              "| Profil | Alertpaare min / median / max | Kapazitätswert EUR min / median / max |",
              "| --- | ---: | ---: |"]
    for record in records:
        pairs = [run["metrics"]["workflow"]["unique_obligation_alert_pairs"] for run in record["runs"]]
        values = [(500 - 60 - count) / 60 * 40 - 20 for count in pairs]
        lines.append(f"| {record['scenario']} | {min(pairs)} / {median(pairs):.1f} / {max(pairs)} | "
                     f"{min(values):.2f} / {median(values):.2f} / {max(values):.2f} |")
    lines += ["", "## Ereignisse und Horizont", "",
              "Identische Zahlen für Workflow und Tabellenäquivalent. Verzögerungen beziehen sich auf Geschäftstags-Prüfschritte.", "",
              "| Profil | Alerttyp | Eingetreten | Erkannt | Übersehen | Fehlalarmepisoden | Am Horizont offen |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for record in records:
        for alert in sorted(CRITICAL):
            counts = [sum(run["metrics"]["workflow"]["by_alert"][alert][key] for run in record["runs"])
                      for key in ("occurred_events", "detected_events", "missed_events", "false_alert_episodes", "open_at_horizon")]
            lines.append("| " + " | ".join(map(str, [record["scenario"], alert, *counts])) + " |")
    lines += ["", "Währungsfehler haben im Massengenerator keine Exposition; sie werden im handbeschrifteten Referenzsatz geprüft.",
              "Null Ereignisse sind keine erfolgreiche Prüfung dieser Fehlerklasse. Rohdaten enthalten jeden Lauf und offene Fristfenster.", "",
              "## Sensitivität", "",
              "Kapazitätswerte in EUR je 100 Geschäftstage; Spalten sind zusätzliche Reviewminuten je Alertpaar.", "",
              "| Profil | Refresh min/Tag | 0 min/Paar | 1 min/Paar | 3 min/Paar |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for record in records:
        for refresh in (2, 5, 8):
            values = [row["net_capacity_eur"] for row in record["economics"]
                      if row["manual_batch_minutes_per_day"] == refresh]
            lines.append(f"| {record['scenario']} | {refresh} | " + " | ".join(f"{v:.2f}" for v in values) + " |")
    lines += ["", "## Reproduktion und Evidenz", "",
              "`python3 run_study.py` führt Tests und sämtliche Läufe aus, prüft Akzeptanzkriterien, Dateihashes und Ergebnistabellen.",
              "Die Ausgabe wird gegen die versionierten Rohdaten geprüft; ausschließlich die lokale Kernruntime wird beim Gleichheitsvergleich ausgenommen.",
              "[Protokoll](README.md) · [Rohdaten](study-results.jsonl) · [Evidenzmanifest](evidence-manifest.json) · [Sandbox und Review-Grenzen](EVIDENCE_NOTES.md)", ""]
    return "\n".join(lines)


def evidence_paths():
    return sorted(path for path in ROOT.rglob("*") if path.is_file()
                  and path.name != "evidence-manifest.json" and "__pycache__" not in path.parts
                  and path.suffix in {".py", ".md", ".csv", ".json", ".jsonl"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Explicitly replace results and checksum manifest after a reviewed change")
    args = parser.parse_args()
    if not args.write:
        manifest = json.loads((ROOT / "evidence-manifest.json").read_text())
        actual = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in evidence_paths()}
        require(actual == manifest["sha256"], "Evidence files changed; inspect differences before --write")
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT), "-v"], cwd=ROOT, check=True)
    process = subprocess.run([sys.executable, str(ROOT / "evaluate.py")], cwd=ROOT, text=True, capture_output=True, check=True)
    records = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    validate(records)
    rendered = render(records)
    if args.write:
        (ROOT / "study-results.jsonl").write_text(process.stdout, encoding="utf-8")
        (ROOT / "RESULTS.md").write_text(rendered, encoding="utf-8")
        manifest = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "command": "python3 run_study.py --write",
                    "comparison_excludes": ["median_local_core_ms"],
                    "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in evidence_paths()}}
        (ROOT / "evidence-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    else:
        recorded = [json.loads(line) for line in (ROOT / "study-results.jsonl").read_text().splitlines()]
        require(deterministic(records) == deterministic(recorded), "Simulation does not reproduce committed results")
        require(rendered == (ROOT / "RESULTS.md").read_text(), "Report differs from generated results")
    print("PASS: 36 paired runs; exact status and alert sets; zero missed/false alerts; evidence verified.")


if __name__ == "__main__":
    main()
