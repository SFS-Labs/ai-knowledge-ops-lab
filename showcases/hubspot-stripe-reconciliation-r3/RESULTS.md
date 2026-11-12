# Revision 3 — Ergebnisse

108 gepaarte Läufe, 6,631,538 Verpflichtungs-Tagesbewertungen je Methode.
Alle neun Zellen erfüllen die vorab festgeschriebenen Modellkriterien.
Währungsfehler haben im Simulationsgenerator keine Exposition. Die 108 Replikationen sind die Auswertungseinheit.

| Deals/Tag | Inzidenz | Bewertungen je Methode | Alertpaare Min/Median/Max | Offene Ereignisse | Modellkriterien |
| ---: | ---: | ---: | ---: | ---: | --- |
| 3 | 5% | 243800 | 10 / 22.0 / 26 | 189 | bestanden |
| 3 | 28% | 244747 | 105 / 134.0 / 159 | 1272 | bestanden |
| 3 | 40% | 244822 | 166 / 196.0 / 220 | 1786 | bestanden |
| 6 | 5% | 490199 | 25 / 46.0 / 56 | 397 | bestanden |
| 6 | 28% | 491538 | 243 / 273.0 / 297 | 2581 | bestanden |
| 6 | 40% | 492341 | 378 / 397.0 / 440 | 3854 | bestanden |
| 18 | 5% | 1478274 | 117 / 150.0 / 158 | 1374 | bestanden |
| 18 | 28% | 1471175 | 772 / 812.0 / 857 | 7609 | bestanden |
| 18 | 40% | 1474642 | 1115 / 1179.5 / 1219 | 11055 | bestanden |

Bei festem Volumen steigt der Median der Alertpaare mit der Inzidenz. Bei fester Inzidenz steigt er mit dem Volumen. Die Unterschiede gelten für den Generator. Eine betriebliche Effektgröße oder Nichtunterlegenheitsgrenze wurde nicht geschätzt.

SHA-256 der deterministischen JSONL-Ausgabe: 38a813bcaec4323e0f8990cd7174ed8c9b5ce21a502f07cce05240bc52909ffa

Reproduktion aus diesem Verzeichnis:

```sh
python3 factorial.py > /tmp/factorial.jsonl
python3 render_results.py /tmp/factorial.jsonl | diff - RESULTS.md
python3 cycles.py | diff - cycles-results.json
```

Der lokale Fehlerreplay prüft zehn Zyklen mit aufgezeichneten Antworten. Die sieben normalen Zyklen und drei Wiederholungen nach Fehlerbehebung waren vollständig. Alle drei injizierten Fehler veröffentlichten null Entscheidungen. Der CRM-Fehler wird auf der abgeleiteten Verpflichtungs-CSV injiziert. Mehrtägiger Betrieb mit echten API-Aufrufen bleibt offen.

Der [direkte Stripe-Lauf mit nativem HubSpot-Export](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43180713631) bestand. Die Original-CSV aus Export-Audit 164215342 enthält drei synthetische Closed-Won-Deals. Deal-ID, Name, Stage und Betrag wurden gegen HubSpot geprüft. USD stammt aus der Kontokonfiguration ohne Zusatzwährungen. Der Job erhielt die aus der Originaldatei extrahierten fachlichen Spalten und transformierte die Beträge in Minor Units. Beide Stripe-Drafts und die fehlende Rechnung ergaben am Ausstellungsstichtag die erwarteten Meldungen. Audit und Ergebnisse stehen in native-export-evidence.json. Dieser Lauf prüft drei Einzelverpflichtungen. Der [separate Zwei-Raten-Live-Test](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43177257680) verwendete den HubSpot-MCP-Pfad. Der separate [Live-Abdeckungstest](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43181973570) prüft vier Alerttypen und zehn Zyklen mit echten Stripe-GETs und injizierten Fehlern. Der [separate Stripe-HTTP-Test](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43182639885) ergänzt payment_overdue an einer offenen synthetischen Rechnung mit explizit gesetzten Bewertungsdaten. Vor dem Kontrollstichtag erschien kein Alert, am Stichtag ausschließlich payment_overdue. Die Rechnung wurde danach als void zurückgelesen. Mehrtägiger Betrieb bleibt außerhalb des Nachweises.
