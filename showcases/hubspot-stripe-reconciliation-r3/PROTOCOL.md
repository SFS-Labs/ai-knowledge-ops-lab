# Revision 3 — Protokoll vor Ergebnissichtung

Ziel ist ein überprüfbarer erster Implementierungsauftrag: CRM-Daten beziehen, Zahlungspflichten abgleichen, Ausnahmen übergeben und bei erkennbar unvollständigem Eingang abbrechen. Revision 2 bleibt die Ausgangsbasis.

## Gepaarte Simulation

Das bestehende Modell und seine Regeln bleiben eingefroren. Vollfaktoriell: 3/6/18 Deals je Geschäftstag × 5/28/40 % injizierte Abweichungen je Verpflichtung. Je Zelle zwölf Replikationen über 100 Geschäftstage. Nullbasierte Zellnummer in dieser Reihenfolge, Seeds 20261201 + 12 × Zellnummer + Replikationsindex. Beide Verfahren erhalten je Replikation dieselben Snapshots. Zwölf Replikationen dienen einer deskriptiven Vergleichbarkeit, ohne behauptete Power oder Nichtunterlegenheitsgrenze.

Vorab definierte Annahmeprüfung: pro Methode exakter Status und vollständige Alertmengen gegen die Modellreferenz; null verpasste kritische Ereignisse, null Fehlalarmepisoden, null Geschäftstage Verzögerung bei exponierten Alerttypen. Null Exposition separat ausweisen. Auswertung je Zelle mit Fallzahlen, offenen Ereignissen und Verteilung der eindeutigen Alertpaare über die zwölf Läufe. Bedingte Unterschiede des Alertaufkommens bei konstantem zweitem Faktor deskriptiv berichten. Tagesbewertungen messen Durchsatz. Unabhängig erzeugte Replikationen sind die Analyseeinheit. Neue Seeds prüfen weitere Realisierungen desselben Modells. Eine separate vorab gelabelte Live-Population prüft den Integrationspfad.

## Sandbox- und Aufwandsnachweis

Für den Live-Nachweis native Closed-Won-CSV mit synthetischen Deals und unabhängiger Kontrolle von IDs, Zeilenzahl, Stage, Betrag und Währung. Sollraten und erwartete Zuordnungen, vollständige Alertmengen und Zustände vor Ausführung festschreiben. Separate Fälle für alle fünf kritischen Alerttypen, einen regulären Treffer, kombinierte Fehler sowie Void/Ersatz. Auch ein realistischer manueller Review- und Nacharbeitsweg muss vor einer Zeitmessung beschrieben sein. Kein Versand und keine Zahlung.

Während der Extraktion bleibt die Testpopulation unverändert. Beide Verfahren verwenden dieselben eingefrorenen Dateien. Der vorhandene Adapter muss bei erkennbar unvollständiger Pagination ohne Entscheidungen abbrechen. Eine absichtlich fehlende erwartete CRM-Zeile muss ebenfalls vor der Klassifikation erkannt werden. Kein Ausbau zu einem atomaren Datenpfad für diese Arbeitsprobe.

Laufende Zuverlässigkeit separat prüfen: zehn geplante Prüfzyklen, davon sieben normal und drei mit je einem injizierten Fehler (unvollständige CRM-Auswahl, fehlende Stripe-Folgeseite, temporärer Transportfehler). Alle sieben normalen Läufe vollständig, alle drei Fehler ohne publizierte Entscheidungen, erfolgreiche Wiederholung nach Fehlerbehebung im selben Zyklus. Ausfälle und Wiederholungen getrennt zählen. Sandbox-Ergebnisse gelten für die geprüften Bedingungen.

Für Recruiting sind gemessene Rechenzeit, modellierte Kapazität und menschliche Arbeitszeit verschiedene Größen. Eine menschliche Gegenprobe gehört weiterhin nicht zum Auftrag. Die ökonomische Sensitivität enthält Review und Nacharbeit als explizite Annahmen. Der CV darf einen gemessenen Zeitgewinn erst nach einem entsprechenden tatsächlichen Vergleich nennen.
