# SFS | ASCEND — R4 Economic Impact: technisches und methodisches Übergabeprotokoll

**Stand:** 2026-11-12. **Ausgangspunkt:** R3-Head `b52bea2f9651334ffb2b3662f2e706ee180fbc45`, R2 `a092b896ea3544a0e67c1fbda52e116d1eb23206`. **Phase 1 ausgeschlossen.**

## Studienziel, Resultat und Freigabegeltung

R4 ergänzt R2/R3 um ein nachvollziehbares Kostenmodell mit externem deutschen Arbeitgeberkostenanker. Hier wird **keine empirisch gemessene Prozesszeit**, **keine realisierte Ersparnis**, **kein nachgewiesener ROI** und **kein echter Produktionsbetrieb** behauptet. KfW und APQC dienen der strukturellen Kontextualisierung, nicht als Soll-Ist-Aufwandsmessung.

**Freigabeentscheidung:** Technisches R4-Modell: **FREIGEGEBEN** nach isoliertem Ausführungstest und R4 Push-/PR-CI auf dem belegten Code-Commit. Konditionale methodische Szenariostudie: **FREIGEGEBEN MIT KONKRETEN EINSCHRÄNKUNGEN**. Ein **empirisch gemessener/konsistent extern kalibrierter Nettoeffizienzgewinn** bleibt **BLOCKIERT**, weil direkte Zeit-/Betriebsdatenevidenz fehlt. Gesamtentscheid R4: **FREIGEGEBEN MIT KONKRETEN EINSCHRÄNKUNGEN** ausschließlich als modellbasierte Studie.

## Provenienz und wissenschaftliche Fixierung

- `PROTOCOL.md` vor Ergebnisberechnung auf eigenem Branch commit `4c455a1beb20bb24bd1f8c9b7e5e93dcc058fcfc`. `PARAMETERS.json` ist die maschinenlesbare Quelle mit Einheiten, Bezugsjahr, Stichprobe, Herkunft, Qualität und Tätigkeitsgleichheit; anschließende dokumentierte Quellenkorrektur APQC.
- `PROFILES.md`: drei **synthetische** Unternehmen; Beschäftigte, Umsätze, Finance-FTE und jährliche Fallzahlen ausdrücklich Hypothesen.
- `model.py` liest den unveränderten R3-Ergebnisbericht und prüft dessen exakten Git-Blob `698c1ae6b899616aa3b68d2fd3313cb6e0b7b291`. R3-Head `b52bea2f9651334ffb2b3662f2e706ee180fbc45`.
- R3: 108 gepaarte Simulationsläufe, neun Zellen, 6.631.538 Verpflichtungs-Tagesbewertungen **pro Methode** über 108 Läufe. Die Durchschnitts-Tagesbewertungen **pro Lauf** und Median-Alertpaare stammen nicht notwendigerweise aus demselben Lauf. Die Darstellung ist modelliert, nicht ein Schätzer realer Unternehmenswerte.
- Währungsfehlerrate im R3 Massengenerator ohne Exposition. Wiederholte Tagesbewertungen, Rechnungen, neue Verpflichtungen, einzigartige Alertpaare und Bearbeitungsfälle sind unterschiedliche Denominatoren.
- R2/R3-Logik, Simulationsseeds und Daten wurden nicht geändert. Kein Branch nach `main` gemergt.

## Unabhängig geprüfter numerischer Referenzfall

6 Deals/Tag, 28 % **injizierte** Szenarioinzidenz, 100 Geschäftstage; R3: 491.538 Bewertungen über zwölf Läufe, also 40.961,5 je Lauf im Mittel; Median 273 Alertpaare pro Lauf.

Arbeitshypothesen: 3 min/Tag manueller Fixaufwand, 0,025 min pro Verpflichtungs-Tagesbewertung, 1,5 min/Tag Automationsaufsicht, 8 min gemeinsame Ausnahmebearbeitung pro Alertpaar, 4 min automatischer **Mehr**review, 120 min Wartung und 0 min Störungen pro 100 Tage. 45 EUR/Stunde ist Destatis-Durchschnitt 2025, nicht Personio-spezifisch. 100 EUR/100 Tage Betrieb, 50 h Implementierung und 50 % wirtschaftliche Nutzung sind ungemessene Annahmen.

- Manuell: `300 + 40.961,5 * 0,025 + 273 * 8 = 3.508,0375 min`.
- Automatisiert: `150 + 273*(8+4) + 120 = 3.546 min`.
- Differenz `−37,9625 min`, Kapazitätswert `−28,471875 EUR`, abzüglich Betrieb `−128,471875 EUR` pro 100 Tage.
- Wirtschaftlicher Schwellenwert manuelle Prüfdauer: `0,03243696316459765 min = 1,9462 Sekunden pro Verpflichtungs-Tagesbewertung`, bei angenommenen 1,5 Sekunden darunter.
- Wolfram Language wurde unabhängig für die drei Werte ausgeführt und lieferte `{-37.9625, -128.471875, 0.03243696316459765}`.

Weitere Zellresultate, Break-even-Schwellen, bedingte Amortisation, Kosten-/Reviewstress und Szenario-Kipppunkte stehen in `RESULTS.md` und maschinenlesbar in `RESULTS.json`.

## Quellenbewertung und Negativbefunde

- Destatis Arbeitskosten 2025: 45,00 EUR je geleisteter Stunde (amtliche Jahresschätzung, NACE B–S ohne O); sektorübergreifender Proxy: https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/04/PD26_148_624.html
- BA Entgeltatlas Buchhalter/in, bundesweiter Median 4.451 EUR brutto/Monat; kein Arbeitgebervollkostensatz, nicht zusätzlich zum Destatis-Kostensatz addiert: https://web.arbeitsagentur.de/entgeltatlas/beruf/7692
- APQC AR Invoice/FTE: **33.333** (Median, 3.496 Unternehmen; Primärquellenstand 12.11.2026, Measure 100797), AR-Prozess inkl. Verarbeitung von Kundenzahlungen; ausschließlich benachbarter Kontextindikator: https://www.apqc.org/resources/benchmarking/open-standards-benchmarking/measures/number-invoices-processed-fte-performs
- KfW Mittelstandspanel 2026, 78,3 % Mittelständler in Dienstleistungsbereichen: Branchenkontext, keine Unternehmenskennzahl: https://www.kfw.de/%C3%9Cber-die-KfW/KfW-Research/Mittelstand.html
- Apollo-Free-Kandidat Personio als Technologieprofil entdeckt, **ohne** daraus Rechnungsvolumen, Umsatz oder Mitarbeiterzahl als Fakten abzuleiten.
- Elicit abgewiesen wegen Tarif `api_access_denied`; kein Upgrade, keine erneute bezahlte Abfrage.
- Exa-Fund mit Einzelzeitangaben zur peruanischen Forderungsbearbeitung und Vendor-OCR-Beispiele wegen **abweichender Tätigkeit**, Geografie und/oder Quelle nicht als Minutenbenchmark übernommen.
- Kein methodisch tragfähiger deutscher Direktparameter für manuelle Kontrollzeit je Verpflichtungsbestand, Fehlerrate, zusätzliche menschliche Alert-Triage oder realisierte Kosteneinsparung verfügbar. **Daher nur konditionale Ergebnisse.**

## Prüfumfang und Grenzen

TDD-Akzeptanztests prüfen R3-Quelle, Einheiten, symmetrischen gemeinsamen Review, Vorzeichenumkehr, Grenzwerte, fehlende Amortisation und bytegleiche Resultate. Secretfreie GitHub-Actions-CI `.github/workflows/reconciliation-r4.yml` prüft zusätzlich R2-Code-Blob, Repository-Regressionstests, R2-Fachtests und R4-Reproduktion.

**CI-Nachweis für berechnete R4-Dateien, Head `4e5ce870749d89dc17719de04fe378ac3fe1056d`:** [Push-Run 43225985808](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43225985808) **SUCCESS**, [Draft-PR-Run 43226096758](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43226096758) **SUCCESS**. Auf isoliertem Sprite-Checkout desselben Heads zusätzlich **10/10 R4-, 19/19 R2- und 135/135 allgemeinen Tests PASS**, bytegleiche JSON-/Markdown-Reproduktion PASS (Python 3.13.17); CI nutzt Python 3.12. Dieser Handoff-Dokumentationscommit erfolgt danach: **sein eigener Head-Status ist gesondert zu prüfen**, nicht aus älteren Jobs abzuleiten. [Draft PR #49](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/49), Base `study/hubspot-stripe-reconciliation-r3`, keine Merges.

**Keine wissenschaftliche Freigabe** für tatsächliche externe Wirtschaftlichkeit: Die zentrale unbekannte Grenzgröße von ~1,95 s manuellem Prüfumfang im Basisfall kann ohne echte Zeit-/Prozessmessung nicht entschieden werden. Insbesondere kann ein Tabellenfilter weniger Grenzarbeit erfordern; bei hoher Alertzahl und Wartung kann die Automation schlechter ausfallen. Der Kapazitätswert ist eine modellierte Opportunitätsbewertung, nicht Cashflow. Negative Modellstunden werden als voller Kostenaufwand bewertet. Implementierungskosten werden nur in der bedingten Amortisation, nicht noch einmal im periodischen Netto berechnet.

**Nächster empirisch notwendiger Beleg:** eine definierte, vollständige, vergleichbare Tätigkeitszeitmessung des Export-/Tabellenpfads inklusive Überwachungs- und Alarmreview, reale Betriebs-/Wartungsdaten und für Cash-Claims nachweisbare Verwendung freier Kapazität. Keine menschliche Gegenprobe als Voraussetzung für **diese** rein konditionale R4-Freigabe.

## Quellenkorrektur und Interpretation der Kennzahlen

- Die APQC-Primärquelle zeigt beim aktuellen erneuten Abruf **33.333 Rechnungen/FTE, N=3.496**. Die zuvor notierte Fassung **34.000/N=3.434** wurde in `PARAMETERS.json` korrigiert. Die APQC-Kennzahl ist **kein Rechenparameter** des Modells; `RESULTS.json` und `RESULTS.md` bleiben numerisch unverändert.
- Das Modellfeld `verified_cash_savings_eur: 0` bedeutet **0 EUR nachgewiesene Einsparungen**, nicht die empirische Feststellung, dass ein Betrieb tatsächlich exakt 0 EUR spart. Die wirtschaftlichen Szenarien sind davon getrennt.

## Übergabeschnittstelle an Phase 1: positive, belegbare Positionierung

Phase 1 wurde in R4 **nicht** ausgeführt. Die folgende Schnittstelle dient der nachgelagerten recruiterorientierten Präsentation, ohne eine Änderung an R2/R3/R4 oder an deren Nachweislogik.

**Primärer Leistungsnachweis:** Konzeption und Implementierung einer read-only HubSpot–Stripe-Soll-Ist-Abrechnungskontrolle, regelbasierte Erkennung kritischer Rechnungsabweichungen, nachvollziehbare Prüf- und Testführung sowie reproduzierbares, sensitivitätsgeprüftes Kostenmodell.

**Sichtbare Fakten für Projektseite, Profil und CV:** 108 gepaarte R3-Simulationsläufe auf konsistenten synthetischen Szenarien; 6.631.538 Verpflichtungs-Tagesbewertungen pro Methode; R4-CI mit 135 allgemeinen Repository-, 19 R2-Fach- und 10 R4-Modelltests; bytegenaue Reproduktion der Ergebnisdateien. Genaue Zuordnung jedes Zahlenwerts und ein öffentlicher Beleglink gehören in die Case Study.

**Ein-Satz-Vorschlag für den Recruiter-Einstieg:** „HubSpot–Stripe: Read-only-Abrechnungskontrolle mit reproduzierbaren Tests, 108 gepaarten Simulationsläufen und transparenter Wirtschaftlichkeitssensitivität.“

**Darstellungsstandard:** Problem → eigene Entscheidung/Umsetzung → überprüfbares Ergebnis → beruflicher Nutzen. Aussagen über simulierte Testdaten klar als solche kennzeichnen. Keine unbelegten Aussagen über einen Kundeneinsatz oder gemessene Einsparungen einführen. In Karriereprofilen **keine ungefragten Negativkataloge**, keine „kein ROI / keine Produktionsdaten / keine menschliche Gegenprobe“-Litanei: Diese methodischen Details sind im technischen Anhang direkt verlinkt und bei Nachfrage vollständig verfügbar. Nicht aus Unbelegtheit einen persönlichen Kompetenzmangel insinuieren.

**Wiederaufnahme:** Aus diesem Verzeichnis: `python3 -m unittest discover -s . -p test_model.py -v`, `python3 model.py --json | diff - RESULTS.json -`, `python3 model.py --report | diff - RESULTS.md -`. Finaler PR wird gegen `study/hubspot-stripe-reconciliation-r3` erstellt. Nicht mergen.
