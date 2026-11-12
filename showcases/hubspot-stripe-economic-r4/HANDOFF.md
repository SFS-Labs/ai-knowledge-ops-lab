# SFS | ASCEND — R4 Economic Impact: technisches und methodisches Übergabeprotokoll

**Stand:** 2026-11-12. **Ausgangspunkt:** R3-Head `b52bea2f9651334ffb2b3662f2e706ee180fbc45`, R2 `a092b896ea3544a0e67c1fbda52e116d1eb23206`. **Phase 1 ausgeschlossen.**

## Studienziel, Resultat und Freigabegeltung

R4 ergänzt R2/R3 um ein nachvollziehbares Kostenmodell mit externem deutschen Arbeitgeberkostenanker. Hier wird **keine empirisch gemessene Prozesszeit**, **keine realisierte Ersparnis**, **kein nachgewiesener ROI** und **kein echter Produktionsbetrieb** behauptet. KfW und APQC dienen der strukturellen Kontextualisierung, nicht als Soll-Ist-Aufwandsmessung.

**Vorläufige Entscheidung:** FREIGEGEBEN MIT KONKRETEN EINSCHRÄNKUNGEN **für die konditionale, synthetische wirtschaftliche Szenarienrechnung**; abschließende technische Freigabe der R4-CI erst nach erfolgreichem Lauf auf finalem Head. Eine **empirisch kalibrierte Tätigkeitszeit und Betriebskostenmessung** bleibt methodisch **BLOCKIERT**, da die erforderlichen Direktevidenzen fehlen.

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
- APQC AR Invoice/FTE: aktuell **34.000** (Median, 3.434 Unternehmen), AR-Prozess inkl. Verarbeitung von Kundenzahlungen, **kein** Nachweis dieser speziellen Soll-Ist-Kontrolle: https://www.apqc.org/what-we-do/benchmarking/open-standards-benchmarking/measures/number-invoices-processed-fte-performs
- KfW Mittelstandspanel 2026, 78,3 % Mittelständler in Dienstleistungsbereichen: Branchenkontext, keine Unternehmenskennzahl: https://www.kfw.de/%C3%9Cber-die-KfW/KfW-Research/Mittelstand.html
- Apollo-Free-Kandidat Personio als Technologieprofil entdeckt, **ohne** daraus Rechnungsvolumen, Umsatz oder Mitarbeiterzahl als Fakten abzuleiten.
- Elicit abgewiesen wegen Tarif `api_access_denied`; kein Upgrade, keine erneute bezahlte Abfrage.
- Exa-Fund mit Einzelzeitangaben zur peruanischen Forderungsbearbeitung und Vendor-OCR-Beispiele wegen **abweichender Tätigkeit**, Geografie und/oder Quelle nicht als Minutenbenchmark übernommen.
- Kein methodisch tragfähiger deutscher Direktparameter für manuelle Kontrollzeit je Verpflichtungsbestand, Fehlerrate, zusätzliche menschliche Alert-Triage oder realisierte Kosteneinsparung verfügbar. **Daher nur konditionale Ergebnisse.**

## Prüfumfang und Grenzen

TDD-Akzeptanztests prüfen R3-Quelle, Einheiten, symmetrischen gemeinsamen Review, Vorzeichenumkehr, Grenzwerte, fehlende Amortisation und bytegleiche Resultate. Secretfreie GitHub-Actions-CI `.github/workflows/reconciliation-r4.yml` prüft zusätzlich R2-Code-Blob, Repository-Regressionstests, R2-Fachtests und R4-Reproduktion.

**CI-Status:** wird mit den finalen GitHub-Run-Links und dem finalen Head nachverifiziert; kein ungeprüfter Erfolg wird behauptet.

**Keine wissenschaftliche Freigabe** für tatsächliche externe Wirtschaftlichkeit: Die zentrale unbekannte Grenzgröße von ~1,95 s manuellem Prüfumfang im Basisfall kann ohne echte Zeit-/Prozessmessung nicht entschieden werden. Insbesondere kann ein Tabellenfilter weniger Grenzarbeit erfordern; bei hoher Alertzahl und Wartung kann die Automation schlechter ausfallen. Der Kapazitätswert ist eine modellierte Opportunitätsbewertung, nicht Cashflow. Negative Modellstunden werden als voller Kostenaufwand bewertet. Implementierungskosten werden nur in der bedingten Amortisation, nicht noch einmal im periodischen Netto berechnet.

**Nächster empirisch notwendiger Beleg:** eine definierte, vollständige, vergleichbare Tätigkeitszeitmessung des Export-/Tabellenpfads inklusive Überwachungs- und Alarmreview, reale Betriebs-/Wartungsdaten und für Cash-Claims nachweisbare Verwendung freier Kapazität. Keine menschliche Gegenprobe als Voraussetzung für **diese** rein konditionale R4-Freigabe.

**Wiederaufnahme:** Aus diesem Verzeichnis: `python3 -m unittest discover -s . -p test_model.py -v`, `python3 model.py --json | diff - RESULTS.json -`, `python3 model.py --report | diff - RESULTS.md -`. Finaler PR wird gegen `study/hubspot-stripe-reconciliation-r3` erstellt. Nicht mergen.
