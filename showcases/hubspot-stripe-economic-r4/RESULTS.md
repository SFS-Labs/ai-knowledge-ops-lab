# R4 — Kostenmodell: Ergebnisse (bedingte Szenarien)

**Kein gemessener menschlicher Zeitgewinn, kein gemessener ROI und keine realisierten Einsparungen.**
Die Ergebnisse hängen substanziell von NICHT empirisch gemessenen Minuten je Kontrolle/Alert,
Wartung, Nutzungsgrad und dem als Proxy eingesetzten deutschen Arbeitskosten-Mittel ab.

Extern kalibrierter Kostensatz: 45 EUR/Stunde (Destatis 2025, sektorübergreifend).
Unbeobachtete Hypothesen: 1.5 Sekunden je wiederholter Tabellenbewertung, 3.0 min manuelle Vorbereitung/Tag, 1.5 min A-Aufsicht/Tag, 4.0 min Zusatztriage/Alertpaar, 120 min Wartung/100 Tage, 100 EUR Betrieb/100 Tage, 50 h Setup, 50% nutzbare positive Kapazität.

## Modellierte Kosten je 100 Geschäftstage

| Deals/Tag | Injizierte Szenarioinzidenz | Prüfbewertungen je Lauf (Mittel) | Alertpaare je Lauf (Median) | Nettozeit h | Kapazitätswert EUR | Bedingter Nettoeffekt EUR | Amortisation Arbeitstage |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5% | 20,316.7 | 22.0 | 7.50 | 337.44 | 68.72 | 3,274 |
| 3 | 28% | 20,395.6 | 134.0 | 0.06 | 2.92 | -98.54 | n/a |
| 3 | 40% | 20,401.8 | 196.0 | -4.07 | -182.97 | -282.97 | n/a |
| 6 | 5% | 40,849.9 | 46.0 | 14.45 | 650.44 | 225.22 | 999 |
| 6 | 28% | 40,961.5 | 273.0 | -0.63 | -28.47 | -128.47 | n/a |
| 6 | 40% | 41,028.4 | 397.0 | -8.87 | -399.22 | -499.22 | n/a |
| 18 | 5% | 123,189.5 | 150.0 | 41.83 | 1,882.30 | 841.15 | 267 |
| 18 | 28% | 122,597.9 | 812.0 | -2.55 | -114.79 | -214.79 | n/a |
| 18 | 40% | 122,886.8 | 1,179.5 | -26.93 | -1,211.87 | -1,311.87 | n/a |

Die **Kapazitätsstunden** sind brutto differenzierte Modellstunden. Der **bedingte Nettoeffekt**
bewertet positive Differenzen nur mit 50% wirtschaftlicher Nutzbarkeit, negative vollständig,
abzüglich illustrativer Betriebsgebühren. Er ist **kein** Geldzufluss. Setup ist nicht im
periodischen Netto enthalten, sondern ausschließlich in bedingter Amortisation.

## Wirtschaftliche Kippschwellen

| Deals/Tag | Inzidenz | erforderliche manuelle min je Bewertung für Netto=0 | maximaler A-Zusatzreview min/Alertpaar für Netto=0 |
| ---: | ---: | ---: | ---: |
| 3 | 5% | 0.0160 | 12.33 |
| 3 | 28% | 0.0379 | 2.04 |
| 3 | 40% | 0.0500 | 1.39 |
| 6 | 5% | 0.0103 | 17.06 |
| 6 | 28% | 0.0324 | 2.88 |
| 6 | 40% | 0.0445 | 1.99 |
| 18 | 5% | 0.0068 | 18.95 |
| 18 | 28% | 0.0284 | 3.48 |
| 18 | 40% | 0.0403 | 2.40 |

Negative Zusatzreview-Grenzen bedeuten: Selbst bei **null** Zusatzreview wäre
der Nettoeffekt unter den übrigen Annahmen nicht positiv. Bei höherem Aufwand je
Bewertung als der angegebenen Untergrenze kann ein positiver Nettoeffekt entstehen.

Interpolierte (nicht empirische) Null-Durchgänge der injizierten Generator-Inzidenz:
- 3 Deals/Tag: 14.4%.
- 6 Deals/Tag: 19.6%.
- 18 Deals/Tag: 23.3%.
Zwischen den drei diskreten Inzidenzfaktoren wird linear interpoliert; dies ist keine
geschätzte reale Fehlerquote, kein Konfidenzintervall und keine Extrapolation.

## Adversarial Sensitivität — Referenzprofil 6 Deals/Tag, 28%

| Variante | Modifikation gegenüber Basis | Nettozeit h | Bedingter Nettoeffekt EUR/100 Tage |
| --- | --- | ---: | ---: |
| manual_batch_fast | m_per_eval=0.005 | -14.29 | -742.89 |
| manual_batch_slow | m_per_eval=0.06 | 23.26 | 423.38 |
| workflow_extra_review_zero | extra_review=0 | 17.57 | 295.26 |
| workflow_extra_review_eight | extra_review=8 | -18.83 | -947.47 |
| capacity_unusable | utilization=0 | -0.63 | -128.47 |
| maintenance_incident_fees_stress | maintenance=480, incident=240, operating=300 | -10.63 | -778.47 |

Menschlicher gemeinsamer Ausnahmeaufwand ist auf beiden Seiten symmetrisch erfasst.
Mehrfachmeldungen eines Verpflichtungs-/Alerttyps an verschiedenen Tagen werden nicht als
neue Alertpaare gezählt. R3-eigene Simulations-Fehlerinzidenzen sind nicht repräsentativ
für deutsche Dienstleistungsunternehmen. Tagesbewertungen sind abhängige Bestandssnapshots,
nicht neue Rechnungen oder unabhängige Beobachtungen. Der Mittelwert der Bewertungen und
der Median der Alertpaare stammen nicht notwendig aus demselben R3-Lauf.

**Freigegebene Interpretation:** Parametrisches bedingtes Kostenmodell mit amtlichem
Arbeitskostenanker; kein Beleg für tatsächliche oder branchenrepräsentative
Zeitersparnis, Cash-Einsparungen, produktive E2E-Gleichwertigkeit oder ROI.

Reproduktion: `python3 model.py --json | diff - RESULTS.json -` und
`python3 model.py --report | diff - RESULTS.md -` aus diesem Verzeichnis.
Tests: `python3 -m unittest discover -s . -p 'test_model.py' -v`.
