# Sandbox und Review-Abdeckung

Übernommener Nachweisbericht aus Revision 2. Die historische Live-MCP-Sequenz wird als
Vorbefund dokumentiert; ihr lokaler Replay wird durch die Tests erneut geprüft.


HubSpot-Portal 149743226, synthetischer Closed-Won-Deal 539935357174, Betrag 2.000 USD. Stripe-Konto acct_1Uaj2tE19wsOrukR wurde als SFS sandbox mit livemode=false bestätigt. Zwei vorhandene synthetische Entwürfe wurden vorübergehend mit den Verpflichtungs-IDs 1 und 2 demselben Deal zugeordnet. Der dokumentierte Prüfplan teilt den Deal in zwei Sollraten zu je 1.000 USD. Die zweite Ist-Rechnung über 1.900 USD enthält absichtlich einen Betragsfehler.

Der Live-Abruf über Stripe MCP erfolgte mit limit=1. Nach einer ersten Seite mit has_more=true wurde ein absichtlich ungültiger Cursor verwendet. Stripe meldete INVALID_ARGUMENT und No such invoice. Der vollständige Neustart lieferte beide Seiten, abschließend has_more=false. Der gespeicherte Datenausschnitt in fixtures/sandbox-review.json wurde durch die Abgleichlogik und durch den paginierten HTTP-Adapter mit aufgezeichneten Antworten geprüft. Jede Rate erhält genau eine Rechnung. Am Ausstellungsstichtag erhalten beide Entwürfe missing_invoice und die zweite zusätzlich amount_mismatch.

Die temporären Metadaten wurden anschließend erfolgreich auf die ursprünglichen Deal-Zuordnungen zurückgesetzt. Es wurden keine Rechnungen finalisiert oder versendet. Der Ratenplan war eine explizite Testeingabe, kein aus HubSpot automatisch extrahierter Zahlungsplan.

Der HTTP-Adapter wurde lokal mit einem Abbruch auf Seite 2 getestet. Die CLI veröffentlichte keine Entscheidungen und schrieb incomplete in den Auditdatensatz. Der Wiederholungslauf schrieb complete. Der Live-MCP-Test und der lokale HTTP-Adaptertest sind getrennte Nachweise. Ein direkter Live-HTTP-Lauf des Skripts sowie wiederholte betriebliche Zuverlässigkeitsmessungen stehen aus.

## Review-Abdeckung

| Review-Punkt | Umsetzung und verbleibende Evidenzgrenze |
| --- | --- |
| Aussagekraft | Hauptaussage auf synthetische Snapshots und definierte Regeln begrenzt. Vollständiger Export-/Bedienpfad bleibt ungeprüft. |
| Mehrfachfehler und Stichtage | Vollständige Alertmengen, sieben zusätzliche unabhängig gelabelte Grenzsituationen. |
| Nenner | Ereignisse je Alerttyp, Fehlalarmepisoden, Verzögerung und offene Fenster in Rohdaten und Bericht. |
| Vollständigkeit | Pagination, Abbruch ohne Entscheidungen, Neustart und Auditstatus getestet. HubSpot-CSV-Vollständigkeit und atomare API-Snapshots bleiben unbestätigt. |
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

Ein direkter Live-HTTP-Test von `reconcile.py` wurde nicht ausgeführt, da in der
Ausführungsumgebung kein Sandbox-API-Schlüssel verfügbar war. Der MCP-Zugriff
stellt dem Python-Prozess keinen Schlüssel zur Verfügung. Das bleibt ein offener
Integrationsnachweis; der lokale Adapter-Replay ersetzt ihn nicht.

## Fachübergreifende Einordnung

| Perspektive | Nachweis / Grenze |
| --- | --- |
| Wirtschaftsinformatik / BPM | Read-only-Abgleich und Paarzuordnung implementiert; vollständiger HubSpot-Exportpfad offen. |
| Operations Management | Drei Belastungsprofile und offene Ereignisse; keine gemessene Bearbeitungskapazität. |
| Operations Research | Gepaarte Snapshots und Kosten-Sensitivität; Volumen und Inzidenz nicht separat identifiziert. |
| Empirisches Software Engineering | Handlabels, Mehrfachfehler, Adapterfehler, Wiederholung, Status- und Alertvergleich. |
| Statistik / Versuchsplanung | Zwölf Läufe je Profil, Streuung auf Laufebene; keine i.i.d.-Annahme für Tagesbewertungen. |
| Accounting Information Systems | Raten, Ausstellungs-/Zahlungskontrollstichtage, Draft/Void, Minor Units; Gutschriften und Teilzahlungen nicht modelliert. |
| Controlling | Laufender Kapazitätswert und Investitionsformel; realisierte Zahlungseffekte nicht gemessen. |
| Arbeitswissenschaft | Vorlage für gepaarte Zeitmessung; alle Zeitparameter bleiben Annahmen. |
| HCI | Kein gemessener Spreadsheet-/Dashboard-Bedienpfad. |
| Data Quality | Importvalidierung, Pagination, Hashes; Population und Snapshot-Atomizität offen. |
| Interne Kontrolle / Revision | Reproduzierbare Kontrollregeln und Audit; keine betriebliche Wirksamkeitsprüfung. |
| Kausale Inferenz | Kein kausal identifizierter betrieblicher Nutzen; modellbedingte Ergebnisse. |
| Organisationspsychologie | Alarmmüdigkeit und Adoption nicht untersucht; zusätzliche Reviewzeit als Sensitivität. |
| Process Mining | Außerhalb des Designs: kein rekonstruierter Ist-Prozess aus Unternehmenslogs. |
| KI-/ML-Evaluation | Nicht anwendbar: beide Klassifikatoren sind deterministische Regeln ohne ML-Modell. |

Die stärkste Gegenhypothese bleibt: Beide Programme reproduzieren dieselben
Modellannahmen, die den betrieblichen Prozess möglicherweise unvollständig abbilden.
Die unabhängigen Handlabels prüfen Grenzfälle, ersetzen aber keine fachliche
Abnahme oder zurückgehaltene betriebliche Stichprobe.
