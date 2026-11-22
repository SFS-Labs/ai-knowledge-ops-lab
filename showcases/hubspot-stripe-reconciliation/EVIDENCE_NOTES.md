# Sandbox und Review-Abdeckung

Übernommener Nachweisbericht aus Revision 2. Die historische Live-MCP-Sequenz wird als
Vorbefund dokumentiert; ihr lokaler Replay wird durch die Tests erneut geprüft.


HubSpot-Portal 149743226, synthetischer Closed-Won-Deal 539935357174, Betrag 2.000 USD. Stripe-Konto acct_1Uaj2tE19wsOrukR wurde als SFS sandbox mit livemode=false bestätigt. Zwei vorhandene synthetische Entwürfe wurden vorübergehend mit den Verpflichtungs-IDs 1 und 2 demselben Deal zugeordnet. Der dokumentierte Prüfplan teilt den Deal in zwei Sollraten zu je 1.000 USD. Die zweite Ist-Rechnung über 1.900 USD enthält absichtlich einen Betragsfehler.

Der Live-Abruf über Stripe MCP erfolgte mit limit=1. Nach einer ersten Seite mit has_more=true wurde ein absichtlich ungültiger Cursor verwendet. Stripe meldete INVALID_ARGUMENT und No such invoice. Der vollständige Neustart lieferte beide Seiten, abschließend has_more=false. Der gespeicherte Datenausschnitt in fixtures/sandbox-review.json wurde durch die Abgleichlogik und durch den paginierten HTTP-Adapter mit aufgezeichneten Antworten geprüft. Jede Rate erhält genau eine Rechnung. Am Ausstellungsstichtag erhalten beide Entwürfe missing_invoice und die zweite zusätzlich amount_mismatch.

Die temporären Metadaten wurden anschließend erfolgreich auf die ursprünglichen Deal-Zuordnungen zurückgesetzt. Es wurden keine Rechnungen finalisiert oder versendet. Der Ratenplan war eine explizite Testeingabe, kein aus HubSpot automatisch extrahierter Zahlungsplan.

Der HTTP-Adapter wurde lokal mit einem Abbruch auf Seite 2 getestet. Die CLI veröffentlichte keine Entscheidungen und schrieb incomplete in den Auditdatensatz. Der Wiederholungslauf schrieb complete. Der Live-MCP-Test und der lokale HTTP-Adaptertest sind getrennte Nachweise. Wiederholte betriebliche Zuverlässigkeitsmessungen liegen außerhalb dieser Arbeitsprobe.

## Review-Abdeckung

| Review-Punkt | Umsetzung und verbleibende Evidenzgrenze |
| --- | --- |
| Aussagekraft | Hauptaussage auf synthetische Snapshots und definierte Regeln begrenzt. Der native HubSpot-UI-Export und menschliche Bedienpfad liegen außerhalb des nachgewiesenen Pfads. |
| Mehrfachfehler und Stichtage | Vollständige Alertmengen, sieben zusätzliche unabhängig gelabelte Grenzsituationen. |
| Nenner | Ereignisse je Alerttyp, Fehlalarmepisoden, Verzögerung und offene Fenster in Rohdaten und Bericht. |
| Vollständigkeit | Pagination, Abbruch ohne Entscheidungen, Neustart und Auditstatus getestet. Die auf einen HubSpot-Deal begrenzte Auswahl ist geprüft. Atomare API-Snapshots bleiben unbestätigt. |
| Wirtschaftlichkeit | Null- und 100-EUR-Schwelle neu gerechnet, Investitionskosten und Horizont in Amortisationsformel berücksichtigt. |
| Arbeitszeit | Szenarioannahmen gekennzeichnet, Vorlage und gepaartes Messprotokoll vorbereitet. Menschliche Zeitmessung steht aus. |

Im Vorlauf bestanden sechs gezielte Testmethoden mit 17 fachlichen Prüfsituationen sowie Fehler-/Wiederholungstests. Bei der Umsetzung wurden zusätzliche Import- und Auswertungsprüfungen ergänzt. Die bestehenden 135 Repository-Tests wurden erneut erfolgreich ausgeführt.

Revision 2 ist eine explorative Überarbeitung nach Kenntnis früherer Ergebnisse. Eine prospektive Vorabregistrierung wird nicht beansprucht. Für eine unabhängige Bestätigung wären Regeln und Seeds vor einem weiteren zurückgehaltenen Prüfsatz festzuschreiben.

## Erneute Leseprüfung während der Umsetzung

Am 12. November 2026 wurde das explizit bezeichnete Konto `acct_1Uaj2tE19wsOrukR`
über Stripe MCP erneut als SFS sandbox (`livemode=false`) bestätigt.
`GetInvoices(limit=1)` lieferte die erste Rechnung mit `has_more=true`; die
Fortsetzung mit deren ID lieferte die zweite Rechnung mit `has_more=false`.
Beide Rechnungen waren Entwürfe, zu 100.000 bzw. 190.000 USD-Minor-Units.
Die erste war wieder Deal `539978132699`, die zweite Deal `539935357174`
zugeordnet; beide Metadaten enthielten keine `obligation_id`. Das bestätigt den
aktuellen Rücksetzungszustand. Es wurde bei dieser Prüfung ausschließlich gelesen.

## Direkter HTTP-Lauf mit zwei separaten Deals

Der [GitHub-Actions-Lauf 43142463091](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43142463091)
bestand auf Commit `c444e73b477d4685dd9bbc723a7a57a24f60c46a`. Der
Workflow schrieb zwei separate synthetische Dealzeilen inline in eine CSV und
führte `reconcile.py --audit` per Stripe-HTTP aus. Beide Drafts meldeten
`missing_invoice`, einer zusätzlich `amount_mismatch`. Die Invoice-Liste
wurde vollständig durchlaufen. Dieser Lauf enthielt weder einen HubSpot-Abruf
noch Raten oder einen expliziten Ausstellungsstichtag.

## HubSpot-abgeleiteter direkter HTTP-Ratentest

Die [aufgezeichnete Quelle](evidence/hubspot-source.json) stammt aus dem
HubSpot-MCP-Abruf `search_crm_objects` im Portal 149743226, gefiltert auf
`hs_object_id=539935357174` und `dealstage=closedwon`. Genau ein Treffer
wurde mit einem separaten Abruf nach ID und der Pipeline-Definition geprüft.
Der Betrag ist 2.000 USD. Weil `deal_currency_code` in beiden Antworten
fehlt, stammt USD aus den Kontoeinstellungen ohne weitere Währungen.
Der native UI-Export wurde nicht geprüft.

`prepare_sandbox_input.py` erzeugt die [Closed-Won-CSV](evidence/derived/hubspot-closed-won.csv)
und die [Verpflichtungs-CSV](evidence/derived/obligations.csv). Die
[Feldherkunft und Hashes](evidence/derived/transformation.json) dokumentieren
die Umrechnung in 200.000 Minor Units. Der [separate Testplan](evidence/installment-plan.json)
teilt diese in zwei Sollraten von je 100.000 USD-Minor-Units inklusive
modellierter Steuer von null. Er setzt beide Ausstellungsstichtage auf
2026-11-12 und beide Zahlungskontrollstichtage auf 2026-11-26.

Der [GitHub-Actions-Lauf 43177257680](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/43177257680)
bestand auf `b5b6c19aa7ab30d6e452286ef9300944bee10feb` im separaten
Verifikationsbranch. Der Job prüfte Konto und Drafts per HTTP, sicherte die
Originalmetadaten, setzte temporär die Ratenzuordnungen und rief das bytegleiche
`reconcile.py` mit der abgeleiteten CSV, `--as-of 2026-11-12` und `--audit`
auf. Der separate Job verwendet das vorhandene Environment `stripe-sandbox`.

| Rate | Stripe-Entwurf | Soll / Ist (USD-Minor-Units) | Vollständige Alerts |
| --- | --- | ---: | --- |
| 1 | `in_1UamitE19wsOrukR7goJaSyd` | 100.000 / 100.000 | `missing_invoice` |
| 2 | `in_1UamioE19wsOrukRDWKzG9Qn` | 100.000 / 190.000 | `amount_mismatch`, `missing_invoice` |

Der [Auditdatensatz](evidence/live-43177257680/audit.json) meldet `complete`
und `pagination_completed` für zwei Verpflichtungen und zwei gelesene
Rechnungen. Die [Ausgabe](evidence/live-43177257680/results.json) belegt die
eindeutigen Zuordnungen. Die Vollständigkeit der begrenzten HubSpot-Auswahl
wurde vor dem CLI-Aufruf separat geprüft. Der Audit beschreibt die
CSV wie vorgesehen als vom Aufrufer bereitgestellt. Die Rechnungsliste
endete vollständig, ohne Garantie atomarer Snapshot-Isolation oder
Aussage über Zuverlässigkeit im wiederholten Betrieb.

Die [Sicherung](evidence/live-43177257680/metadata-backup.json) stimmt mit dem
[erneut gelesenen Rücksetzungszustand](evidence/live-43177257680/restoration.json)
überein. Beide Rechnungen blieben Drafts mit deaktivierter automatischer
Weiterverarbeitung und ohne Zahlungsversuch. Es wurden ausschließlich
Metadaten geändert. Die Hashes im [Laufnachweis](evidence/live-43177257680/summary.json)
wurden gegen die versionierten Artefakte geprüft. Ein lokal injizierter
Fehler nach der zweiten Metadatenänderung prüft die Rücksetzung beider Drafts.

## Fachübergreifender Gegencheck der Revision 2

Der Gegencheck mit `bpm-peer-review` bewertet die Arbeitsprobe für die
definierten synthetischen Zustände und den begrenzten Integrationsnachweis
als tragfähig. Die stärkste alternative Erklärung für die perfekte
Übereinstimmung sind gemeinsame Regeln und Generatorannahmen. Die 17
Handfälle prüfen diese Regeln gegen separate Labels und decken auch den
im Massengenerator fehlenden Währungsfehler ab. Der Live-Test prüft eine
andere Fehlerquelle: Quelle, Ratenzuordnung, echter Transport und Rücksetzung
im selben Ablauf. Die Modellannahmen zur Reviewzeit können das wirtschaftliche
Urteil trotz gleicher Kontrollgüte umkehren. Die Nachrechnung der 27
Szenarien und beider Schwellen aus den Rohdaten bestätigt die Berichtswerte.
Die Befunde begrenzen die Aussage auf die Arbeitsprobe und begründen
keine Änderung an Regeln, Seeds oder Referenzlabels.

## Fachübergreifende Einordnung

| Perspektive | Nachweis / Grenze |
| --- | --- |
| Wirtschaftsinformatik / BPM | Read-only-Abgleich und Paarzuordnung implementiert; begrenzter HubSpot-MCP-Datenpfad mit CSV-Transformation geprüft. |
| Operations Management | Drei Belastungsprofile und offene Ereignisse; keine gemessene Bearbeitungskapazität. |
| Operations Research | Gepaarte Snapshots und Kosten-Sensitivität; Volumen und Inzidenz nicht separat identifiziert. |
| Empirisches Software Engineering | Handlabels, Mehrfachfehler, Adapterfehler, Wiederholung, Status- und Alertvergleich. |
| Statistik / Versuchsplanung | Zwölf Läufe je Profil, Streuung auf Laufebene; keine i.i.d.-Annahme für Tagesbewertungen. |
| Accounting Information Systems | Raten, Ausstellungs-/Zahlungskontrollstichtage, Draft/Void, Minor Units; Gutschriften und Teilzahlungen nicht modelliert. |
| Controlling | Laufender Kapazitätswert und Investitionsformel; realisierte Zahlungseffekte nicht gemessen. |
| Arbeitswissenschaft | Vorlage für gepaarte Zeitmessung; alle Zeitparameter bleiben Annahmen. |
| HCI | Kein gemessener Spreadsheet-/Dashboard-Bedienpfad. |
| Data Quality | Importvalidierung, Pagination, Hashes; begrenzte Population geprüft. Snapshot-Atomizität offen. |
| Interne Kontrolle / Revision | Reproduzierbare Kontrollregeln und Audit; keine betriebliche Wirksamkeitsprüfung. |
| Kausale Inferenz | Kein kausal identifizierter betrieblicher Nutzen; modellbedingte Ergebnisse. |
| Organisationspsychologie | Alarmmüdigkeit und Adoption nicht untersucht; zusätzliche Reviewzeit als Sensitivität. |
| Process Mining | Außerhalb des Designs: kein rekonstruierter Ist-Prozess aus Unternehmenslogs. |
| KI-/ML-Evaluation | Nicht anwendbar: beide Klassifikatoren sind deterministische Regeln ohne ML-Modell. |

Die stärkste Gegenhypothese bleibt: Beide Programme reproduzieren dieselben
Modellannahmen, die den betrieblichen Prozess möglicherweise unvollständig abbilden.
Die unabhängigen Handlabels prüfen Grenzfälle, ersetzen aber keine fachliche
Abnahme oder zurückgehaltene betriebliche Stichprobe.
