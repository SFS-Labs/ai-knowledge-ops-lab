# SFS | ASCEND – Phase 0: Technisches Übergabeprotokoll

**Stand:** 12. November 2026 · **Projekt:** SFS | PLAYING FIELD · **Arbeitsprobe:** HubSpot–Stripe-Reconciliation · **Empfänger:** Phase 1 (Projektseite, Case-Study-PDF, Bewerbungsrollout)

## 1. Entscheidung und Freigabeumfang

**FREIGEGEBEN MIT KONKRETEN EINSCHRÄNKUNGEN.**

Freigegeben ist die Darstellung einer **reproduzierbaren, regelbasierten Abrechnungskontrolle** auf synthetischen Daten, einschließlich des nachgewiesenen begrenzten HubSpot–CSV/Stripe-Sandbox-HTTP-Pfads, fünf anhand getrennter Sandbox-Szenarien geprüfter Alerttypen und Fail-Closed-Tests. Die Ergebnisse entsprechen den festgelegten Modellregeln für die erprobten Konstellationen. Die Wirtschaftlichkeit ist **eine Sensitivitätsrechnung aus Annahmen**, keine gemessene Zeit- oder Geldersparnis.

**Nicht freigegeben:** Aussagen zu betrieblicher Gleichwertigkeit mit einem vollständigen menschlichen Export-und-Tabellenprozess, gemessener Arbeitsersparnis, nachgewiesener Langzeitverfügbarkeit, atomaren Stripe-Snapshots, universeller Vollständigkeit von CRM-Exporten, abgeschlossener Ausnahmebearbeitung oder Produktionsreife. Keine Produktionsdaten untersucht. Keine Stripe- oder HubSpot-Schreibzugriffe in diesem Phase-0-Review durchgeführt. Kein Studien-PR gemergt, kein Bewerbungsprofil geändert, Phase 1 nicht begonnen.

## 2. Git-Topologie und freizugebender Code

| Gegenstand | Final verifizierter Stand |
| --- | --- |
| Repository | https://github.com/SFS-Labs/ai-knowledge-ops-lab |
| PR #47 – Revision 2 | [PR #47](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/47); **open, non-draft, nicht gemergt**; Base `main` @ `bbdad1577f09a62424c0e335e635adbbe90b0fde`; Head `study/hubspot-stripe-reconciliation` @ `a092b896ea3544a0e67c1fbda52e116d1eb23206` |
| PR #48 – Revision 3 | [PR #48](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/48); **open, Draft, nicht gemergt**; Base `study/hubspot-stripe-reconciliation` @ `a092b896ea3544a0e67c1fbda52e116d1eb23206`; Head `study/hubspot-stripe-reconciliation-r3` @ `b52bea2f9651334ffb2b3662f2e706ee180fbc45` |
| R2 PR-Merge-Commit für CI | `72b3f2e8e00f03208f5c2e8a10f124bbd5c0cfde` (PR-Checkout, **nicht** R2-Head) |
| R3 PR-Merge-Commit für CI | `b8258ac6ec9273b50b8685904d7203a3f7422371` (PR-Checkout, **nicht** R3-Head) |
| R3 Push-Revision | `b52bea2f9651334ffb2b3662f2e706ee180fbc45` |
| Vorgelagertes R3-Protokoll | `68f9b0c66b9f5a549a9b3f74220aaa98b2eba227`, vor dem ersten R3-Faktoriellauf versioniert |
| Historischer R3-Anker | `e2c53eff077a898f9511ac9c9e8b1da91ea86a69`; durch finalen Head überholt |
| Separater Sandbox-Branch | `verify/stripe-sandbox-http` @ `060c922b9ecbce54ab1280a953b6afad24c34e5f`; kein Studien-PR-Head |
| `reconcile.py` Identität | Git-Blob `f8a3a62d6920037373f96341f67f9ff3891da9aa`; SHA-256 `ca49feead8a1101b7ccd9198f42a297a737b5b92990fe0e25d59b0348d57c7a8` |

**Code-Identität:** Derselbe `reconcile.py`-Blob wurde auf R2, R3 und den fünf nachstehenden Verifikationscommits festgestellt. Die Test-Runner und Datenherkunft sind **nicht** identisch. Das ist keine Behauptung eines identischen vollständigen E2E-Pfads. PR #48 hat die R2-Korrektur durch einen Merge **innerhalb der Studienbranches** übernommen. Kein Merge nach `main`. GitHub meldete beide PRs als mergeable.

## 3. Ausführung und Nachprüfung – strikt nach Evidenzart

### 3.1 Frischer isolierter Checkout / lokale Befehle

Frischer GitHub-Checkout im isolierten Testcontainer auf historischem R3-Head `23df4d341cd41677cfce54849b3511fd15a261ba`, anschließend separater R2-Fix-Checkout auf `e18cf2a24abd3a3b9f58cd8c7029e56458f5ba11`. Ausführungsumgebung Python 3.13.17; die verbindlichen vollständigen GitHub-CI-Läufe nutzten Python 3.12.

```sh
git clone https://github.com/SFS-Labs/ai-knowledge-ops-lab.git
git switch --detach 23df4d341cd41677cfce54849b3511fd15a261ba
# R2, im R2-Studienverzeichnis:
python3 -m unittest discover -s . -v
python3 reconcile.py fixtures/deals.csv --invoice-fixture fixtures/invoices.json --audit audit.json
python3 run_study.py
# R3, im R3-Verzeichnis:
python3 factorial.py > /tmp/r3-factorial.jsonl
sha256sum /tmp/r3-factorial.jsonl
python3 render_results.py /tmp/r3-factorial.jsonl | diff - RESULTS.md
python3 cycles.py | diff - cycles-results.json
```

**Tatsächlich ausgeführt:** Vor Fix 18/18 gezielte R2-Tests PASS; dokumentierter Fixture-CLI-Lauf mit `--audit` erfolgreich; danach R2-Reproduktion **gezielt fehlgeschlagen** (`Evidence files changed`, weil unversionierte `audit.json` erfasst wurde). Neuer gezielter Regressionstest zuerst **RED**, anschließend **GREEN**. Nach Fix 19/19 Studientests PASS; 30/30 registrierte Manifest-Hashes geprüft; selbstständig aus R2-Rohdaten Median-Alertpaare, Kapazitätswerte und Schwellen nachgerechnet. Die lokal angestoßene komplette 36+108-Läufe-Kette wurde wegen massiver Laufzeitabweichung der isolierten Python-Umgebung nicht abgeschlossen; **daraus wird kein lokaler Vollreproduktionsnachweis abgeleitet**. Der vollständig abgeschlossene Nachweis ist die folgende GitHub-CI auf dem **finalen** Code. Keine Daten/Seeds/Labels zur Erreichung grüner Tests geändert.

### 3.2 GitHub-CI, **nach** Korrektur

| Beweis | Exakt geprüfter Stand | Resultat |
| --- | --- | --- |
| [R2 PR-CI 43196803455](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196803455) | R2 PR-Merge `72b3f2e…` | **Success**; 135 allgemeine Repository-Tests, 19 Studien-Tests, 36 Replikationsläufe + Manifest/Report |
| [R3 Push-CI 43196867508](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196867508) | exakter R3-Push-Head `b52bea2f9651334ffb2b3662f2e706ee180fbc45` | **Success**; 135 + 19 Tests; R2-Reproduktion; R3-108-Läufe-Hash und Berichtsvergleich; 10 Offline-Zyklen |
| [R3 PR-CI 43196876051](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196876051) | R3 PR-Merge `b8258ac…` | **Success**; gleiche Testschritte einschließlich R3-Hash/Report/Replay |

Die R3-Ausgabe hat SHA-256 `38a813bcaec4323e0f8990cd7174ed8c9b5ce21a502f07cce05240bc52909ffa`. Der CI-Befehl `sha256sum --check` bestand. Die gesonderten älteren CI-Nachweise (R2 `43177551925`, R3 `43187631968`) beziehen sich **nicht** auf die finalen Head-Commits und sind nur Historie.

### 3.3 Fünf historische Sandbox-HTTP-Nachweise

| Workflow-Run | Verifikationscommit | Eingabequelle / Population | Prüfbehauptung und Ergebnis | Grenzen |
| --- | --- | --- | --- | --- |
| [43142463091](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43142463091) | `c444e73b477d4685dd9bbc723a7a57a24f60c46a` | Inline-CSV, zwei getrennte synthetische Deals; Stripe-GET | Beide Drafts `missing_invoice`, ein `amount_mismatch`; Pagination komplett | Kein HubSpot-Bezug, kein Zwei-Raten-Plan |
| [43177257680](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43177257680) | `b5b6c19aa7ab30d6e452286ef9300944bee10feb` | Erfasster HubSpot-MCP-Closed-Won-Deal, daraus 2 Sollraten; Stripe-GET und temporäre Metadata-Umordnung | Zwei Drafts, erwartete Alerts, `pagination_completed`, Audit vollständig; Metadaten zurückgesetzt und nochmals gelesen | Raten separat festgelegt; **kein** nativer HubSpot-UI-Export |
| [43180713631](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43180713631) | `752b7741a0ee61f185cb58d4cd3eddb37cb6dee0` | Reduzierte Projektion aus nativem HubSpot-CSV-Export mit **drei** synthetischen Closed-Won-Deals; Stripe-GET | Drei Einzelverpflichtungen, Draft- und Missing-Alerts; CSV-Zeilenanzahl, IDs, Stage, Betrag kontrolliert; USD aus Konto-Default | Original-CSV mit Owner-Feldern nicht veröffentlicht; kein Zwei-Raten-Test |
| [43181973570](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43181973570) | `fc1da456fe88764b7e789771cfa00de12b4e5b6c` | Synthetische Soll-CSV, echte Stripe-GETs (eine Rechnung je Seite), injizierte CRM-/Seiten-/Transportfehler | `missing_invoice`, `amount_mismatch`, `currency_mismatch`, `multiple_invoices`; sieben normale Zyklen + drei fehlerhafte ohne Entscheidungen mit drei erfolgreichen Wiederholungen; Metadata-Restore | Alles innerhalb **eines Jobs**; EUR-Soll gegen live gelesenen **USD-Entwurf**, keine reale EUR-Rechnung; Fehler künstlich injiziert |
| [43182639885](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43182639885) | `060c922b9ecbce54ab1280a953b6afad24c34e5f` | Separate synthetische offene USD-Sandbox-Rechnung, Stripe-GET; explizite Bewertungsdaten 13./14.11.2026 | Vor Kontrollstichtag keine Alerts; am 14.11. ausschließlich `payment_overdue`; `void` danach gelesen, null Zahlung / null Versuch | Bewertungsstichtage **hypothetisch vorgezogen**, kein mehrtägiges Warten; historische Test-Schreibfreigabe nicht erneuert |

Die Live-Läufe sind jeweils als GitHub Actions **success** dokumentiert. Ein vollständiger paginierter Abruf beweist die abgerufene Stripe-Invoice-Population zum Lesen, **nicht** atomare Konsistenz mehrerer Seiten oder Vollständigkeit einer vom Aufrufer bereitgestellten HubSpot-CSV. Rücksetzung/Storno wurden anhand versionierter Audit-Readbacks geprüft; ein erneutes Stripe-Lesen wurde hier nicht benötigt. Der ausgemusterte EUR-Entwurf ist ein interner Zustand und wird für keine öffentliche Behauptung verwendet.

## 4. Studiendesign, Rohdaten und selbstständig nachgerechnete Kernzahlen

**Revision 2:** 36 gepaarte Läufe (3 kombinierte Profile × 12 Seeds; je 100 Geschäftstage); 2.207.277 Verpflichtung-Tagesbewertungen **pro Methode**; Handreferenz mit 17 Szenarien. Bei sämtlichen exponierten Klassen stimmen Status und vollständige Alertmengen der zwei deterministischen Varianten mit der **Modellreferenz** überein; keine verpassten Ereignisse, Fehlalarmepisoden oder Verzögerungen in diesen Läufen. Wiederholte Tagesbewertungen sind abhängig und als Durchsatz, nicht unabhängige Stichprobe, zu behandeln. Der Massengenerator enthält **keine Währungsfehler-Exposition**; `currency_mismatch` wurde in Handfällen und getrennt in der Sandbox getestet. Am Horizont offene Ereignisse sind ausgewiesen, nicht als abgearbeitet gezählt.

**Revision 3:** Vorher versioniertes `PROTOCOL.md`; vollfaktorielles 3/6/18 Deals je Geschäftstag × 5/28/40 % injizierte Szenarien, zwölf unabhängige Seeds **je Zelle** = 108 gepaarte vollständige Modellreplikationen, 6.631.538 Verpflichtung-Tagesbewertungen **pro Methode**. Alle neun Zellen bestehen die vorab festgelegten **modellinternen** Kriterien. Die Median-Alertpaare (pro vollständigem Lauf, nach Volumen geordnet) sind:

| Deals/Tag | 5 % | 28 % | 40 % |
| ---: | ---: | ---: | ---: |
| 3 | 22 | 134 | 196 |
| 6 | 46 | 273 | 397 |
| 18 | 150 | 812 | 1179,5 |

**Ökonomische R2-Sensitivität, keine Zeitmessung:** Formel je 100 Geschäftstage: `[(100×Refreshminuten/Tag − 60 Minuten Aufsicht − Alertpaare×Zusatzreviewminuten − Störungsminuten) / 60] × 40 EUR − 20 EUR`. Angenommen: fünf manuelle Refreshminuten/Tag, eine Zusatzminute je eindeutigem Alertpaar, 40 EUR/Stunde, 20 EUR Betriebskosten, null Störungen, keine Implementierungskosten. Aus Rohdaten nachgerechnet:

| Profil | Median eindeutige Alertpaare | EUR/100 Tage | Nullschwelle min/Paar | 100-EUR-Schwelle min/Paar |
| --- | ---: | ---: | ---: | ---: |
| low | 23,5 | +257,67 | 17,45 | 11,06 |
| default | 268 | +94,67 | 1,53 | 0,97 |
| stress | 1167 | −504,67 | 0,35 | 0,22 |

27 Varianten aus drei Refreshannahmen, drei Zusatzreviewannahmen und drei Profilen werden im Bericht ausgewiesen. Für betriebliche ROI-/Amortisationsaussagen fehlen insbesondere gemessener menschlicher Refresh-/Reviewaufwand, tatsächliche Störungskosten, Implementierungskosten und realisierbarer Kapazitätsanteil. Nicht jedes positive Modellresultat ergibt Cashflow.

## 5. Befunde, Änderungen und verbleibende Grenzen

**B1 – behoben (Reproduzierbarkeit, P2, PR #47):** `showcases/hubspot-stripe-reconciliation/run_study.py:evidence_paths()` nahm neue Laufzeit-`audit.json` und weitere nicht versionierte JSONL-Dateien in die Evidenzliste auf. Der dokumentierte CLI-Lauf machte `run_study.py` danach fehlerhaft. Vorher-Nachher-Regressionstest: **RED**, danach **GREEN**. Korrektur im R2-Commit `a092b896ea3544a0e67c1fbda52e116d1eb23206`: Evidenzliste aus den expliziten Manifest-Keys, Pfadgrenzenprüfung, drei neue Dateihashes im Manifest, README-Hinweis und Test. 19/19 lokale Studientests und alle 30 registrierten Datei-Hashes grün; neue R2-/R3-CI grün. Der ursprüngliche [Codex-Review-Thread](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/47#discussion_r4547687680) wurde mit Belegen beantwortet und als erledigt markiert. Keine Geschäftsregeln, Seeds, Referenzlabels oder Ergebnis-Rohdaten geändert.

**B2 – eingeschränkter Geltungsbereich (Datenvollständigkeit):** `reconcile.py` prüft CSV-Schema, Datums-/Schlüsselvalidität, sichere Stripe-Pagination und gesamte Invoice-Antwort vor Entscheidung. Es erkennt aber **nicht selbst**, ob eine erwartete HubSpot-Deal-Zeile im fachlich vollständigen Export fehlt: `deal_population=caller_supplied_csv_unverified`. Die 3-Deal- und 10-Zyklen-Tests prüften die erwartete Population **außerhalb der CLI**. Externe Aussagen müssen diese Bedingung nennen. Für Produktion wäre die Population vor dem Abgleich durch einen separaten Import-/Kontrollnachweis abzusichern.

**B3 – fachliche Reichweite:** Testnorm: `deal_id + obligation_id`, Minor Units und Währung, Issue-/Pay-Stichtag, Draft als fehlende finale Invoice, Void ausgeschlossen, überlappende Alerts vollständig. `paid` umfasst Stripe-Zustand einschließlich manueller Markierung; Teilzahlungen, Gutschriften, Abstimmung gegen einen unabhängigen Finance-Sollprozess und tatsächliche Ausnahmebearbeitung fehlen. Währungsfehler des Massengenerators haben keinen Nenner. Perfekte Modelltreffer können gemeinsame Sollregel-Annahmen reproduzieren. Betriebswirksamkeit nicht behaupten.

**B4 – sicherer Sandbox-Betrieb / Restrestrisiko:** Offline-CI liest keine Stripe-Secrets; Live-Verifikationsjobs laufen branchgebunden auf `verify/stripe-sandbox-http` mit `stripe-sandbox`-Environment und `contents: read`. Actions sind über Commit-SHA fixiert; Checkout persistiert keine Credentials. Sandbox-GETs verwenden Testschlüssel, Metaänderungen sind auf Test-Rechnungen eingegrenzt. `try/finally` und Cleanup-Schritte schützen in normalen Fehlern, die Auditdaten dokumentieren Readback. **Nicht garantiert:** Cleanup nach jedem Prozessabbruch/Kill oder frühem Fehler vor `try`; Verifikationsrunner verwenden zum Teil `assert` (unter `python -O` deaktivierbar) und können vollständige synthetische Auditobjekte ins Log schreiben. Diese Runner sind **keine produktionssichere Freigabe**; für reale Einsätze Zugriffe technisch restriktiver, Cleanup und Logs härten. Kein weiterer Live-Schreibtest notwendig/autorisiert.

**B5 – Umgebungsabweichung:** Vollreproduktion auf der isolierten lokalen Python-3.13-Umgebung blieb wegen unverhältnismäßiger Laufzeit unvollständig, **nicht** wegen festgestelltem fachlichem Fehler. Zielgerichtete lokale Prüfungen bestanden. Abschließende **vollständige** Reproduktion wurde frisch im GitHub-Runner mit Python 3.12 am R2- und R3-Finalstand erfolgreich verifiziert. Das ist offen von den lokalen Ergebnissen getrennt.

**Methodische Gegenhypothese:** Modellbaseline und Regelabgleich können beide dasselbe unvollständige Fachmodell abbilden. Handlabels und getrennte Sandbox-Grenzfälle reduzieren, aber beseitigen dieses Risiko nicht. `bpm-peer-review` war in diesem Lauf als ausführbarer Skill nicht verfügbar; die Gegenprüfung erfolgte direkt anhand Protokoll, Implementierung, Tests, Rohdaten, historischen Audits und aktueller CI. Keine unabhängige externe wissenschaftliche Begutachtung behaupten.

## 6. Aussage–Beleg-Freigabematrix für Website, PDF und CV

| Freigegebene Formulierung | Öffentlicher Primärbeleg | Geltungsbereich / nicht hinzufügen |
| --- | --- | --- |
| „Reproduzierbare, regelbasierte HubSpot–Stripe-Abrechnungskontrolle mit definierten kritischen Ausnahmen implementiert.“ | [R2-README](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/README.md), [finale R2-CI](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196803455) | Regelbasierter, demonstrativer Kontrollprozess; kein fertiges Produktionsprodukt |
| „108 gepaarte synthetische Modellläufe in neun Volumen-/Inzidenzszenarien; alle vorab definierten Modellkriterien erfüllt.“ | [R3-Protokoll](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/PROTOCOL.md), [R3-Ergebnisse](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/RESULTS.md), [R3 Push-CI](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196867508) | Je Lauf 100 abhängige Tagesstände; keine reale Fehlerquote, keine statistische Nichtunterlegenheit |
| „Die fünf definierten Alerttypen sind durch Handtests und separate Sandbox-HTTP-Szenarien abgedeckt.“ | [R3-Abdeckung](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/live-coverage-evidence.json), [Overdue-Nachweis](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/overdue-live-evidence.json) | Nicht alle im gleichen HubSpot-Export; EUR-Gegenprobe synthetische Soll-Währung gegen USD-Entwurf |
| „Drei synthetische Closed-Won-Deals aus einem nativen HubSpot-CSV-Export wurden gegen Stripe-Sandbox-Rechnungen abgeglichen.“ | [Native Export-Evidenz](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/native-export-evidence.json), [Run 43180713631](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43180713631) | Nur 3 Einzelverpflichtungen; öffentliche Projektion statt Original-CSV |
| „Ein HubSpot-MCP-Deal wurde mit einem separaten Zwei-Raten-Sollplan über direkten Stripe-HTTP-Abgleich geprüft.“ | [Audit & Ratenquelle](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/EVIDENCE_NOTES.md), [Run 43177257680](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43177257680) | Kein nativer Export, Ratenplan außerhalb HubSpot |
| „Kontrollierte Fehler führen ohne veröffentlichte Entscheidungen zum Abbruch; erfolgreiche Wiederholung wurde erprobt.“ | [Offline-Replay](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/cycles-results.json), [Live Coverage Run 43181973570](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43181973570) | 10 Zyklen in einem Job und 10 Offline-Replays, keine Langzeitüberwachung |
| „Wirtschaftliche Tragfähigkeit wurde durch ein transparentes Sensitivitätsmodell untersucht; positive und negative Szenarien.“ | [R2-Rohdaten](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/study-results.jsonl), [R2-Bericht](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/RESULTS.md) | Keine real gemessene Einsparung, kein nachgewiesener ROI |

**CV-Kurzform (eine Aussage, ohne erfundene Impact-Zahl):** „Entwicklung und reproduzierbare Validierung einer regelbasierten HubSpot–Stripe-Abrechnungskontrolle mit fünf definierten Ausnahmeklassen, gepaarten synthetischen Tests und dokumentierter Sandbox-HTTP-Verifikation.“ Quellen: R2-/R3-Ergebnis- und Live-Nachweis oben.

## 7. Stabile Einstiegspunkte für Phase 1

- **R2 final:** [Commit a092b896ea3544a0e67c1fbda52e116d1eb23206](https://github.com/SFS-Labs/ai-knowledge-ops-lab/commit/a092b896ea3544a0e67c1fbda52e116d1eb23206), [README](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/README.md), [RESULTS](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/RESULTS.md), [EVIDENCE_NOTES](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/EVIDENCE_NOTES.md), [Manifest](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/a092b896ea3544a0e67c1fbda52e116d1eb23206/showcases/hubspot-stripe-reconciliation/evidence-manifest.json).
- **R3 final:** [Commit b52bea2f9651334ffb2b3662f2e706ee180fbc45](https://github.com/SFS-Labs/ai-knowledge-ops-lab/commit/b52bea2f9651334ffb2b3662f2e706ee180fbc45), [PROTOCOL](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/PROTOCOL.md), [RESULTS](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/RESULTS.md), [native Export-Evidenz](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/native-export-evidence.json), [Live-Abdeckung](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/live-coverage-evidence.json), [Overdue-Evidenz](https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/b52bea2f9651334ffb2b3662f2e706ee180fbc45/showcases/hubspot-stripe-reconciliation-r3/overdue-live-evidence.json).
- **Finale CI:** [R2 PR](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196803455) · [R3 Push](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196867508) · [R3 PR-Merge](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43196876051).
- **Offene PRs:** [#47](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/47) · [#48](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/48). Auch solange #48 Draft bleibt, funktionieren die obigen **commitgepinten** Dateilinks unabhängig vom Branchfortschritt.

**Öffentlicher Zugriff:** PR-, Commit-, CI-, Audit-, Ergebnis- und Evidenzseiten wurden ohne GitHub-Authentifizierung mit HTTP 200 und geprüftem erwarteten Seiteninhalt geöffnet. Die private Original-CSV mit Eigentümerdaten wird nicht veröffentlicht.

**Phasenübergang:** Phase 1 kann Projektseite, Case-Study-PDF und Bewerbungsunterlagen **unter den genannten Formulierungsgrenzen** erstellen. Neue Nutzenzahlen erfordern echte Zeitmessung; neue Produktions-/Datenzugriffe und öffentliche Profiländerungen benötigen ihre jeweils eigene Autorisierung. Dieser Review hat weder einen der Studien-PRs gemergt noch Phase 1 ausgelöst.
