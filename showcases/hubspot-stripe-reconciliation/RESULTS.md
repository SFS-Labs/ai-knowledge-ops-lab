# Ergebnisse der HubSpot–Stripe-Studie

Revision 2 – reproduzierbare Implementierung, 12. November 2026.

36 gepaarte Läufe × 100 simulierte Geschäftstage; 2,207,277 Verpflichtungs-Tagesbewertungen je Methode.
Beide Methoden stimmen in Status **und vollständiger Alertmenge** exakt mit der Modellreferenz überein.
Keine übersehenen kritischen Meldungen, Fehlalarmepisoden oder Verzögerungen auf diesen Eingaben.
Wiederholte Snapshots sind abhängig. Diese Simulation belegt keine betriebliche Fehlerquote oder menschliche Zeitersparnis.

## Wirtschaftlichkeit

Illustrative Annahmen je 100 Geschäftstage: 5 Minuten Tabellenrefresh/Tag, 60 Minuten Aufsicht/Pflege,
1 zusätzliche Minute je eindeutigem Verpflichtungs-/Alerttyp-Paar, 40 EUR/Stunde, 20 EUR Betriebskosten.

| Profil | Verpflichtungs-Tagesbewertungen | Median Alertpaare | Kapazitätswert EUR | Nullschwelle min/Paar | 100-EUR-Schwelle min/Paar |
| --- | ---: | ---: | ---: | ---: | ---: |
| low | 242864 | 23.5 | 257.67 | 17.45 | 11.06 |
| default | 491062 | 268.0 | 94.67 | 1.53 | 0.97 |
| stress | 1473351 | 1167.0 | -504.67 | 0.35 | 0.22 |

Die Schwellen werden am medianen Alertpaar-Aufkommen berechnet; sie sind nicht der Median laufweiser Quotienten.
Implementierungskosten sind im Kapazitätswert nicht enthalten. Amortisation bei positivem Wert V und Investition I:
100 × I / V Geschäftstage, unter konstanten Annahmen und voller wirtschaftlicher Nutzung der freigesetzten Zeit.

## Streuung über vollständige Läufe

Min/Median/Max beschreiben die zwölf Läufe je Profil; dies sind keine Konfidenzintervalle.

| Profil | Alertpaare min / median / max | Kapazitätswert EUR min / median / max |
| --- | ---: | ---: |
| low | 11 / 23.5 / 38 | 248.00 / 257.67 / 266.00 |
| default | 252 / 268.0 / 294 | 77.33 / 94.67 / 105.33 |
| stress | 1132 / 1167.0 / 1231 | -547.33 / -504.67 / -481.33 |

## Ereignisse und Horizont

Identische Zahlen für Workflow und Tabellenäquivalent. Verzögerungen beziehen sich auf Geschäftstags-Prüfschritte.

| Profil | Alerttyp | Eingetreten | Erkannt | Übersehen | Fehlalarmepisoden | Am Horizont offen |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| low | amount_mismatch | 56 | 56 | 0 | 0 | 56 |
| low | currency_mismatch | 0 | 0 | 0 | 0 | 0 |
| low | missing_invoice | 115 | 115 | 0 | 0 | 47 |
| low | multiple_invoices | 19 | 19 | 0 | 0 | 19 |
| low | payment_overdue | 100 | 100 | 0 | 0 | 100 |
| default | amount_mismatch | 541 | 541 | 0 | 0 | 541 |
| default | currency_mismatch | 0 | 0 | 0 | 0 | 0 |
| default | missing_invoice | 1255 | 1255 | 0 | 0 | 572 |
| default | multiple_invoices | 288 | 288 | 0 | 0 | 288 |
| default | payment_overdue | 1163 | 1163 | 0 | 0 | 1163 |
| stress | amount_mismatch | 2359 | 2359 | 0 | 0 | 2359 |
| stress | currency_mismatch | 0 | 0 | 0 | 0 | 0 |
| stress | missing_invoice | 5533 | 5533 | 0 | 0 | 2425 |
| stress | multiple_invoices | 1187 | 1187 | 0 | 0 | 1187 |
| stress | payment_overdue | 4951 | 4951 | 0 | 0 | 4951 |

Währungsfehler haben im Massengenerator keine Exposition; sie werden im handbeschrifteten Referenzsatz geprüft.
Null Ereignisse sind keine erfolgreiche Prüfung dieser Fehlerklasse. Rohdaten enthalten jeden Lauf und offene Fristfenster.

## Sensitivität

Kapazitätswerte in EUR je 100 Geschäftstage; Spalten sind zusätzliche Reviewminuten je Alertpaar.

| Profil | Refresh min/Tag | 0 min/Paar | 1 min/Paar | 3 min/Paar |
| --- | ---: | ---: | ---: | ---: |
| low | 2 | 73.33 | 57.67 | 26.33 |
| low | 5 | 273.33 | 257.67 | 226.33 |
| low | 8 | 473.33 | 457.67 | 426.33 |
| default | 2 | 73.33 | -105.33 | -462.67 |
| default | 5 | 273.33 | 94.67 | -262.67 |
| default | 8 | 473.33 | 294.67 | -62.67 |
| stress | 2 | 73.33 | -704.67 | -2260.67 |
| stress | 5 | 273.33 | -504.67 | -2060.67 |
| stress | 8 | 473.33 | -304.67 | -1860.67 |

## Reproduktion und Evidenz

`python3 run_study.py` führt Tests und sämtliche Läufe aus, prüft Akzeptanzkriterien, Dateihashes und Ergebnistabellen.
Die Ausgabe wird gegen die versionierten Rohdaten geprüft; ausschließlich die lokale Kernruntime wird beim Gleichheitsvergleich ausgenommen.
[Protokoll](README.md) · [Rohdaten](study-results.jsonl) · [Evidenzmanifest](evidence-manifest.json) · [Sandbox und Review-Grenzen](EVIDENCE_NOTES.md)
