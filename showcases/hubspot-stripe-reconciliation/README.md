# HubSpot–Stripe Reconciliation Case Study

## Forschungsfrage und Evidenzgrenze

Wie zuverlässig setzen ein regelbasierter Abgleich und ein ausführbares
Tabellenäquivalent die definierten Rechnungsregeln auf identischen synthetischen
Datenständen um? Unter welchen Annahmen lohnt sich die laufende Automatisierung?

Die Untersuchung misst Klassifikation und Meldung. Der Abschluss von Ausnahmen
liegt außerhalb des gemessenen Prozesses. Die Tabellenbaseline ist eine
Python-Implementierung von Filtern, Gruppierung und Lookup. Ein vollständiger
Export-und-Tabellenprozess mit menschlicher Bedienung wurde nicht gemessen.
Gleiche Ergebnisse gelten für die getesteten Regeln und Datenstände.
Betriebliche Gleichwertigkeit und realisierte Zeitersparnis bleiben offen.

## Fachliche Festlegungen für Revision 2

* Die entscheidende Ausgabe ist die vollständige Menge `alerts` je Verpflichtung.
  `status` bleibt zur Kompatibilität als priorisierte Zusammenfassung erhalten.
  Die Auswertung verwendet sämtliche Alerts.
* Eine Verpflichtung wird mit `deal_id` und `obligation_id` zugeordnet. Zwei
  Raten eines Deals haben verschiedene Verpflichtungs-IDs.
* Ab dem geplanten Ausstellungsstichtag muss eine finalisierte, nicht stornierte
  Rechnung vorhanden sein. Ein reiner Entwurf erzeugt ab diesem Stichtag
  `missing_invoice`. Die fehlende Finalisierung ist damit ausdrücklich erfasst.
* Eine offene Rechnung erzeugt ab dem vereinbarten Zahlungskontrollstichtag
  `payment_overdue`. Dieser Stichtag muss im Input den ersten Kontrolltag nach
  dem vertraglich erlaubten Zahlungsfenster abbilden. Ein Ausstellungsdatum
  ersetzt diesen Zahlungskontrollstichtag nicht.
* Stornierte Rechnungen werden ausgeschlossen. Ein passender Ersatz erfüllt
  die Pflicht. Ohne Ersatz entsteht ab Ausstellungsstichtag eine Fehlmeldung.
* Jede Minor-Unit-Abweichung erzeugt `amount_mismatch`. Finanzielle
  Wesentlichkeit braucht eine zusätzliche fachliche Schwelle.
* Gleichzeitige Betrags-, Währungs- und Fristfehler werden gemeinsam gemeldet.
  Mehrere aktive Rechnungen derselben Verpflichtung ergeben zusätzlich
  `multiple_invoices`. In dieser Studie entspricht jede Rate einer Rechnung.
* `uncollectible` und `draft` bleiben sichtbare Rechnungszustände. Paid bezeichnet
  den Stripe-Zustand einschließlich manueller Markierung als bezahlt.

Diese Regeln sind Festlegungen für die Testumgebung. Eine fachliche Freigabe
durch einen betrieblichen Finance-Verantwortlichen wurde nicht erhoben.

## Reproduktion

Arbeitsverzeichnis ist dieses Verzeichnis.

```sh
python3 run_study.py  # Tests, 36 Läufe, Hash- und Ergebnisprüfung
python3 -m unittest -v
python3 reconcile.py fixtures/deals.csv --invoice-fixture fixtures/invoices.json --audit audit.json
python3 simulate.py --summary-only
python3 evaluate.py > /tmp/study-results.jsonl
```

Für einen direkten Stripe-Leseabruf `STRIPE_API_KEY` geschützt als Sandbox-Key
setzen und `--invoice-fixture` weglassen. CSV-Grundfelder sind
`deal_id,amount_minor,currency`. Für Raten und Stichtagskontrollen zusätzlich
`obligation_id,issue_due,pay_due` mit ISO-Daten verwenden und `--as-of YYYY-MM-DD`
angeben. Ein leerer Verpflichtungsschlüssel unterstützt den bisherigen
Einzelrechnungsfall. Beträge enthalten die modellierte Steuer.

Der direkte Adapter sammelt vor jeder Ausgabe alle Rechnungsseiten. Scheitert
eine Seite oder ist die Pagination ungültig, endet der Lauf ohne Entscheidungen.
Mit `--audit` werden Beginn, Ende, Code-Hash, Daten-Hashes, Umfang, Vollständigkeits-
status und Fehlerklasse gespeichert. Ein Neustart liest die Population erneut.

`pagination_completed` belegt die erfolgreich durchlaufene Pagination.
Die Vollständigkeit des bereitgestellten HubSpot-Exports und atomare
Snapshot-Isolation über mehrere API-Seiten sind damit nicht nachgewiesen.
CSV-Herkunft und Extraktionszeit müssen im betrieblichen Verfahren protokolliert
werden. Die `--as-of`-Option bewertet den bereitgestellten Snapshot und lädt
keinen historischen Stripe-Zustand.

## Referenzen, Ereignisse und Nenner

17 von Hand festgelegte fachliche Prüfsituationen decken die ursprünglichen zehn
Fälle und sieben zusätzliche Grenzsituationen ab. Dazu gehören Mehrfachfehler,
beide Seiten des Zahlungskontrollstichtags, Entwurf vor/am Ausstellungsstichtag,
Stornierung sowie Ersatz. Ein separater Test prüft wiederkehrende Ereignisse,
einen absichtlich übersehenen Fall, Fehlalarm und Erkennungsverzug.

Für die große Simulation kommt die Sollreferenz aus dem Generatormanifest.
Beide Abgleiche erhalten diese Labels nicht. Gemeinsame Modellannahmen können
trotz exakter Übereinstimmung fehlerhaft sein.

| Kennzahl | Definition |
| --- | --- |
| Exakte Übereinstimmung | identischer Status und identische Alertmenge je Verpflichtung und Prüftag |
| Ausnahmeereignis | zusammenhängende Folge positiver Prüftage je Verpflichtung und Alerttyp |
| Erkannt/übersehen | mindestens eine passende Meldung während des Ereignisfensters / keine |
| Erkennungsverzug | Geschäftstags-Prüfschritte ab erstem planmäßigem positiven Prüftermin bis erster passender Meldung |
| Fehlalarmepisode | zusammenhängende Folge von Meldungen ohne zeitgleiche Sollabweichung |
| Ausgegebene Episoden | zusammenhängende Folgen von Meldungen je Verpflichtung und Alerttyp |
| Reviewaufwand | einmal je eindeutigem Verpflichtungs-/Alerttyp-Paar im Kostenmodell |
| Offenes Fenster | Ausstellungs- oder Zahlungskontrollstichtag liegt nach Tag 100 |
| Am Horizont offen | eingetretenes Ausnahmeereignis besteht am letzten Prüftag fort |

Fehlalarmepisoden und ausgegebene Episoden werden als absolute Anzahlen
berichtet. Für Raten müssen Nenner und Episodenzuordnung explizit gewählt
werden. Nach einer Unterbrechung erneut auftretende Fehler zählen als neue
Ereignisse, während die Einmalprüfung im Kostenmodell weiterhin nur einmal
je Paar zählt. Zusätzliche Wiederholungsprüfungen sind ein eigener Kosteninput.
Nicht erkannte Ereignisse gehen in die Fehlzählung ein und erhalten keinen
künstlichen Verzögerungswert von null.

## Versuchsplanung

Drei kombinierte Belastungsprofile haben 3, 6 beziehungsweise 18 neue Deals
pro Geschäftstag und 5%, 28% beziehungsweise 40% injizierte Abweichungsszenarien je Verpflichtung.
Jedes Profil umfasst zwölf gepaarte Läufe über 100 Geschäftstage mit Seeds
20261112 bis 20261123. Die Profile schätzen keine getrennten Effekte von
Volumen und Fehlerquote. Jeder Lauf verwendet identische Snapshots für beide
Methoden. Wiederholte Tagesbewertungen sind abhängig.

Währungsfehler sind im handbeschrifteten Referenzsatz enthalten. Der bisherige
Massengenerator erzeugt ausschließlich USD und liefert deshalb keine
Währungsfehler-Ereignisse. Ein Nullwert in dieser Kategorie bezeichnet fehlende
Exposition. Die Simulationsstreuung wird auf Ebene vollständiger Läufe berichtet.
Eine Konfidenzaussage zur betrieblichen Fehlerquote wird daraus nicht abgeleitet.

## Wirtschaftlichkeit

Alle Arbeitszeit- und Kostenwerte sind illustrative Annahmen. Ein manueller
Tabellenrefresh benötigt im Modell 2, 5 oder 8 Minuten pro Tag. Für Aufsicht und
Pflege des Workflows werden 60 Minuten je 100 Tage angesetzt. Der Vollkostensatz
beträgt 40 EUR/Stunde, zusätzliche Betriebskosten 20 EUR je 100 Tage.
Zusätzlicher Reviewaufwand wird mit 0, 1 oder 3 Minuten je eindeutigem Alertpaar
variiert. Gleicher gemeinsamer Prüfaufwand hebt sich im Vergleich auf.

Kapazitätswert in EUR je 100 Geschäftstage = (100 × Refreshminuten pro Tag
− 60 Minuten Aufsicht/Pflege − Alertpaare × zusätzliche Reviewminuten pro Paar
− Störungsminuten) / 60 × 40 EUR/Stunde − 20 EUR.

Bei fünf Refreshminuten pro Tag stehen nach Aufsicht und Betriebskosten
410 Minuten für Zusatzreviews bis zur Nullschwelle zur Verfügung. Für
mindestens 100 EUR sind es 260 Minuten. Bei einer Zusatzminute je Paar
überschreitet Low beide Schwellenziele, Default bleibt positiv unter 100 EUR
und Stress ist negativ. Bei drei Zusatzminuten je Paar ist Default selbst
bei acht Refreshminuten pro Tag negativ. Die 27 Szenarien und beide
Schwellen wurden aus den Medianen der Rohdaten separat nachgerechnet.

Der aktuelle Rechenlauf setzt zusätzliche Störungsarbeit auf null. Jede
zusätzliche Stunde reduziert das ausgewiesene Ergebnis um 40 EUR.
Berichtet werden sowohl die Nullschwelle als auch die illustrative Schwelle
von 100 EUR je 100 Tage. Eine negative zulässige Prüfzeit bedeutet, dass die
gewünschte Schwelle bereits ohne Zusatzprüfung verfehlt wird.

Implementierungskosten gehören zur Amortisation. Bei konstantem positivem
Kapazitätswert V je 100 Tage und Investition I ist die modellierte
Amortisationsdauer 100 × I / V Geschäftstage. Bei V <= 0 ergibt sich im Modell
keine Amortisation. Nutzungshorizont, realisierbarer Kapazitätsanteil und
Implementierungskosten müssen für eine Investitionsentscheidung ergänzt
werden. Ein Kapazitätswert wird erst durch entsprechende Nutzung zahlungswirksam.

## Empirische Zeitmessung für weitergehende Aussagen

Vor einer betrieblichen Nutzenaussage werden beide vollständigen Bedienpfade
mit vergleichbaren Fällen und wechselnder Reihenfolge gemessen. Die Vorlage
`timing-template.csv` erfasst aktive Aktualisierung, Wartezeit, Aufsicht,
Störungsnacharbeit, Review, Wiederholungsprüfungen und Ergebnisqualität.
Ein gleicher Ausgangszustand wird je Vergleich wiederhergestellt.
Übungsfälle werden vorab ausgesondert. Abgebrochene Läufe werden erfasst.
Die Auswertung umfasst die gesamte Arbeitszeit bis zum gleichen Ergebnisstand.

Aktuelle Arbeitsprobe und Bericht beschränken sich auf das Sensitivitätsmodell.
Es liegen keine gemessenen menschlichen Zeiten vor. Lokale Kernruntime und
MCP-Aufrufdauer liefern keine menschliche Bedienzeit.

## Nutzung und Ergebnisstand

Python 3.12 oder neuer genügt; keine Drittanbieterpakete und für die lokale
Reproduktion keine Zugangsdaten erforderlich. [Ergebnisse](RESULTS.md) werden
aus [den Rohdaten](study-results.jsonl) erzeugt. `run_study.py` prüft exakte
Statusgleichheit und alle Alerts für beide Methoden, die 36 Läufe,
Fehlalarm-/Ausfallzähler sowie den Erkennungsverzug. Es beendet sich bei
Abweichungen mit Fehlerstatus. Ein ausschließlich lokal gemessener Runtime-Wert
ist ausdrücklich vom deterministischen Ergebnisvergleich ausgenommen.

Nach einer bewusst geprüften Änderung erzeugt `python3 run_study.py --write`
Rohdaten, Ergebnistabellen und Hashmanifest neu. Änderungen an Regeln, Eingaben
und Ergebnissen sind anschließend zusammen im Git-Diff zu prüfen. Das Manifest
ist ein Integritätsnachweis für die Dateien, keine unabhängige Beglaubigung.
Die Prüfung verwendet ausschließlich die im Manifest aufgelisteten Quellen.
Laufzeitdateien wie `audit.json` bleiben außerhalb der Belegbasis, sodass
CLI-Tests und erneute Reproduktion im selben Arbeitsverzeichnis möglich sind.
Neue bewusst versionierte Evidenzdateien müssen bei einer Überarbeitung explizit
ins Manifest aufgenommen werden.

Der Legacy-Status bleibt eine priorisierte Zusammenfassung. Insbesondere kann
`invoice_draft` gleichzeitig den Alert `missing_invoice` besitzen. Die
Akzeptanzprüfung prüft beide Ausgaben; für die Kontrollabdeckung und Kosten
sind die vollständigen Alertmengen maßgeblich.

Leere optionale Datumsfelder bedeuten den bisherigen Fall ohne Zeitplan.
Sobald ein Zeitplan verwendet wird, müssen beide Stichtage vorliegen und
`pay_due >= issue_due` gelten. Doppelte Schlüssel, beschädigte CSV-Zeilen,
ungültige Beträge und fehlerhafte Rechnungsantworten führen zum Abbruch ohne
Entscheidungen. Leere Populationen werden mit Anzahl null im Audit ausgewiesen;
ihre fachliche Vollständigkeit muss der Aufrufer bestätigen.

Die [Sandbox- und Review-Notizen](EVIDENCE_NOTES.md) dokumentieren den
historischen MCP-Ratentest, den lokalen Adapter-Replay, den direkten HTTP-Lauf
mit zwei separaten Deals und den HubSpot-abgeleiteten Sandbox-Ratentest.
