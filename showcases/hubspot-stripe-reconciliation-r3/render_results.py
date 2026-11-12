"""Render the fixed factorial run, including its reproducible raw-output hash."""
import hashlib
import json
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_bytes()
cells = [json.loads(line) for line in raw.splitlines()]
assert len(cells) == 9 and all(len(c["runs"]) == 12 for c in cells)
total = sum(c["evaluations_per_method"] for c in cells)
print("# Revision 3 — Ergebnisse\n")
print(f"108 gepaarte Läufe, {total:,} Verpflichtungs-Tagesbewertungen je Methode.")
print("Alle neun Zellen erfüllen die vorab festgeschriebenen Modellkriterien." if all(c["passed"] for c in cells) else "Mindestens eine Zelle verfehlt die Modellkriterien.")
print("Währungsfehler haben im Simulationsgenerator keine Exposition. Die 108 Replikationen sind die Auswertungseinheit.\n")
print("| Deals/Tag | Inzidenz | Bewertungen je Methode | Alertpaare Min/Median/Max | Offene Ereignisse | Modellkriterien |")
print("| ---: | ---: | ---: | ---: | ---: | --- |")
for c in cells:
    pairs = " / ".join(map(str, c["alert_pairs_min_median_max"]))
    print(f"| {c['daily_deals']} | {c['injected_incidence']:.0%} | {c['evaluations_per_method']} | {pairs} | {c['open_events']} | {'bestanden' if c['passed'] else 'verfehlt'} |")
print("\nBei festem Volumen steigt der Median der Alertpaare mit der Inzidenz. Bei fester Inzidenz steigt er mit dem Volumen. Die Unterschiede gelten für den Generator. Eine betriebliche Effektgröße oder Nichtunterlegenheitsgrenze wurde nicht geschätzt.")
print("\nSHA-256 der deterministischen JSONL-Ausgabe:", hashlib.sha256(raw).hexdigest())
print("\nReproduktion aus diesem Verzeichnis:\n\n```sh\npython3 factorial.py > /tmp/factorial.jsonl\npython3 render_results.py /tmp/factorial.jsonl | diff - RESULTS.md\npython3 cycles.py | diff - cycles-results.json\n```")
print("\nDer lokale Fehlerreplay prüft zehn Zyklen mit aufgezeichneten Antworten. Die sieben normalen Zyklen und drei Wiederholungen nach Fehlerbehebung waren vollständig. Alle drei injizierten Fehler veröffentlichten null Entscheidungen. Der CRM-Fehler wird auf der abgeleiteten Verpflichtungs-CSV injiziert. Mehrtägiger Betrieb mit echten API-Aufrufen bleibt offen.")
print("\nHubSpot hat einen nativen CSV-Export über drei synthetische Closed-Won-Deals erstellt (Export-Audit-ID 164215342). Die Downloadversuche aus Benachrichtigung und Export-Audit lieferten im Browser keine abrufbare Datei. Die native CSV ist deshalb noch nicht gegen die Quelle geprüft und nicht an Stripe übergeben. Der bestehende [Live-Test mit HubSpot-MCP-CSV](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43177257680) bleibt der belegte Integrationslauf.")
