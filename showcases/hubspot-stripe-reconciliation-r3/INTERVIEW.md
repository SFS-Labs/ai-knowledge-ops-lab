# Arbeitsprobe für B2B-KI-Implementierung

**CV-Text mit aktuell belegbaren Aussagen**

> HubSpot–Stripe-Abrechnungskontrolle umgesetzt und im Sandbox-Betrieb geprüft. Der Workflow ordnet Rechnungspflichten aus Closed-Won-Deals zu, meldet überlappende Abweichungen und bricht bei erkennbar unvollständigen Eingaben ab. Kontrollgüte gegen ein ausführbares Tabellenäquivalent auf identischen synthetischen Daten geprüft. Wirtschaftlichkeit nach Volumen und zusätzlichem Reviewaufwand modelliert.

Die Fallzahl für diese Aussage steht im Ergebnisbericht. Der Live-Test zu einem Deal und zwei Raten ist separat verlinkt. Vor einer Angabe zur eingesparten menschlichen Arbeitszeit müssten zwei vollständige Bedienpfade bei gleicher Ergebnisqualität gemessen werden. Erfasst würden aktive Aufbereitung, fachliches Review, Nacharbeit und Wartezeit getrennt. Der bisherige Vergleich liefert keine gemessene Personaleinsparung.

## Live im Gespräch vorführen

Aus dem Repository-Stamm:

```sh
cd showcases/hubspot-stripe-reconciliation
python3 reconcile.py evidence/derived/obligations.csv \
  --as-of 2026-11-12 \
  --invoice-fixture evidence/live-43177257680/invoices-during.json \
  --audit /tmp/sfs-interview-audit.json
python3 ../hubspot-stripe-reconciliation-r3/cycles.py
```

Der erste Befehl spielt den aufgezeichneten Stripe-Datenstand lokal ab. Rate 1 meldet eine fehlende ausgestellte Rechnung. Rate 2 meldet zusätzlich einen Betragsfehler. Der zweite Befehl demonstriert den Abbruch und die erneute Prüfung nach Fehlerbehebung.

## Aufgabe für das Gespräch

> Eine Rechnung wird storniert und am selben Stichtag ersetzt. Im selben Deal gibt es zwei Raten. Wie stellst du sicher, dass der Ersatz nur die richtige Rate erfüllt? Ändere den Testfall und zeige die Ausgabe. Was würdest du im Kontrollprotokoll festhalten, wenn die Zuordnungs-ID im CRM fehlt?

Die Aufgabe prüft Anforderungsklärung, fachliche Zuordnung und nachvollziehbare Verifikation. Eine weiterführende Variante lässt den Interviewer einen neuen Ausnahmefall vorgeben und zuerst den erwarteten Status und alle Alerts festlegen.
