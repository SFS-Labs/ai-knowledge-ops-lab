# R4 Forschungsprotokoll — vor Ergebnisberechnung fixiert

**Fixierung:** 2026-11-12. **Ausgangspunkt:** R3-Head `b52bea2f9651334ffb2b3662f2e706ee180fbc45`; R2-Head `a092b896ea3544a0e67c1fbda52e116d1eb23206`. Diese Revision ändert keine Fachregeln und keinen R3-Datengenerator.

## Frage und estimands

Wie ändern sich Ressourcenverbrauch und **modellierter**, nicht realisierter wirtschaftlicher Gegenwert zwischen (M) manuellem Export-/Tabellenfilter und (A) read-only automatisierter Kontrolle samt menschlicher Restarbeit? Horizont 100 Geschäftstage pro vollständiger R3-Replikation. Betrachtet werden Zeitdifferenz, Kapazitätswert, wirtschaftlich verwertbarer Modell-Nettoeffekt, Break-even-Kontrollzeit, Break-even-Zusatzreview, Grenz-Inzidenzen und bedingte Amortisation. Positive Zeitersparnis impliziert **weder** frei werdenden Cashflow **noch** Abbau von Stellen.

## Einheit und Vergleichbarkeit

R3-Zellen: 3/6/18 neue Deals/Geschäftstag × 5/28/40 % **injizierte Szenarioinzidenz**; 12 Seeds je Zelle, je 100 Tage. R3-RESULTS.md enthält **summierte Verpflichtung-Tagesbewertungen über zwölf Läufe**, aber Min/Median/Max **eindeutiger `(obligation, alert type)`-Paare pro Lauf**. Berechnung je Zelle verwendet den **Mittelwert** der Tagesbewertungen über zwölf Läufe und den **Median** der Alertpaare: ein synthetischer repräsentativer Mix, **kein beobachteter einzelner Lauf**. Damit keine laufweisen Konfidenzintervalle, keine Korrelation und keine gepaarten Wirtschaftlichkeitsverteilungen behaupten. Deal ≠ Verpflichtung ≠ Rechnung ≠ Alertpaar ≠ Tagesbewertung. Ein Alertpaar kann länger als einen Tag sichtbar sein. R3 berichtet keinen vollständigen manuellen Realbetrieb.

## Tätigkeitsabgrenzung

M: fester täglicher sicherer Export/Tabellenaufbau, zeitvariable Überprüfung der fortlaufenden Verpflichtung-Tagesbewertungen, menschliches Abarbeiten jedes eindeutigen Alertpaars. A: tägliche Überwachung einschließlich Extraktions- und Vollständigkeitskontrollaufwand, identisches menschliches Abarbeiten jedes Alertpaars **plus** zusätzlicher Triage-Aufwand, laufende Wartung/Störungen, Betriebsgebühren. Gemeinsame Ausnahmebearbeitung ist auf BEIDEN Seiten enthalten, ohne Differenz doppelt zu belasten. Korrekturbuchungen, Kundenkontakt, Inkasso und Settlement auf beiden Seiten ausgeschlossen. Kein kostenloser laufender Betrieb angenommen; keine überwachungsfreie Vollautomatisierung.

## Vorgegebene Kostenfunktion

Bezeichner: D=100 Tage, N=R3-Tagesbewertungen / 12, A=Median einzigartige Alertpaare.
- M_min = D*m_fixed_min_per_day + N*m_incremental_min_per_evaluation + A*common_exception_min_per_pair.
- W_min = D*a_supervision_min_per_day + A*(common_exception_min_per_pair + a_extra_review_min_per_pair) + maintenance_min_per_100_days + incident_min_per_100_days.
- Δ_min=M_min−W_min. Positive Δ=freigesetzte Kapazität; negative Δ=zusätzliche Kapazität.
- Kapazitätswert EUR=Δ_min/60*wage_eur_per_hour; nicht als Cashflow ausweisen.
- Betriebsnetto ohne Setup bei vollständig nutzbarer Arbeit = Kapazitätswert−operating_eur_per_100_days.
- **Nutzbarkeits-adjustierter Szenariowert** EUR=wenn Δ≥0 dann `Δ/60*wage*utilization_fraction`, andernfalls `Δ/60*wage`; davon Betriebskosten abziehen. Negative Zusatzstunden werden als voller Ressourcenverbrauch angesetzt. `utilization_fraction` ist KEINE gemessene Einsparquote und keine reale Cashwirkung.
- Einmalige Implementierung `setup_hours*wage` EUR. Nur wenn laufender nutzbarkeits-adjustierter Szenariowert positiv: amortisation_days=100*setup_cost/net_value; andernfalls keine Amortisation.
- **Cash-Einsparungen nachgewiesen:** immer 0 EUR, da kein Personal-/Vertrags-/Budgetabbau nachgewiesen.
- Arbeits-Break-even N>0: `m_incremental=(D*(a_supervision-m_fixed)+A*a_extra_review+maintenance+incident)/N`.
- Wirtschaftlicher Break-even bei `utilization_fraction>0`: zur rechten Seite zusätzlich `operating*60/(wage*utilization_fraction)` addieren, für die Triage-Grenze entsprechend umstellen. Keine Division durch Null; bei 0 Verwertung und positiven Gebühren kein positiver Cash-Schwellenwert.

## Vorab spezifizierte Parameter und Szenarien

Basis: 45 EUR/geleistete Arbeitsstunde (Destatis 2025, **breiter Branchenproxy**). Weitere Zeiten/Kosten sind **hypothetische Arbeitsannahmen**, keine aus APQC oder R3 gemessenen Tätigkeitszeiten. M-Extraktion 3 min/Tag, M marginale Tabellenprüfung 0,025 min/Tagesbewertung (=1,5 s), A Aufsicht 1,5 min/Tag, gemeinsamer Fachreview 8 min/Paar, A zusätzlicher Review 4 min/Paar, Wartung 120 min/100 Tage, Störung 0 min in Basis, sonst sensibel; Systemgebühren 100 EUR/100 Tage, Setup 50 h, Verwertungsgrad 0,5 (nicht real gemessen). Alle Kosten nominal, ohne Inflation und Discount, reine Vorsteuerbetrachtung.

Sensitivität vorab: Tagesbewertungszeit [0,005;0,025;0,06] min, A-Mehrreview [0;2;4;8] min/Paar, Verwertung [0;0,5;1], Betriebsgebühr [0;100;300] EUR/100 Tage, Wartung [0;120;480] min/100 Tage, Ausfall [0;240] min/100 Tage, Arbeitskosten [32;45;60] EUR/h, Implementation [10;50;150] h, neun R3-Volumen/Inzidenz-Zellen. Alle Kombinationen müssen deterministisch ausgewertet werden können; Bericht zeigt gezielte Grenzen und negative Gegenfälle.

## Qualitätskriterien

(1) Parametertypen, Einheiten und Quellen maschinenlesbar; (2) Daten aus R3-RESULTS.md maschinell per exakt benannten Tabellenfeldern und fixiertem R3-Hash übernommen, nicht durch Schätzung; (3) Test RED→GREEN; (4) Invarianzen: gemeinsame Bearbeitungszeit kürzt sich in Δ; doppelte Alt-Snapshots ändern nicht Alertpaar-Anzahl; Null-Wirtschaftlichkeitsgewinn kann nicht amortisieren; positive Mehrreview senkt den Vorteil; (5) Reproduktion per Stdlib ohne Secrets; (6) R2/R3-Logik und Rohdaten unverändert; (7) unabhängige Wolfram-Stichprobe; (8) finales GitHub-CI auf Head. Wenn (2), (5) oder (8) fehlen, keine technische Gesamtfreigabe.

## Zulässige Schlussfolgerungen

Zulässig: konditionale Wirtschaftlichkeit mit transparenten Annahmen und externem Arbeitskostenanker. Unzulässig: empirisch gemessene 1,5 s/Verpflichtung, verifizierter ROI, echte Kostenersparnis, Personaleinsparung, repräsentative Fehlerinzidenz, empirische AR-spezifische Betriebskosten, produktive E2E-Validierung oder statistische Nichtunterlegenheit. Die Gegenhypothese „A ist teurer“ ist **gleichrangig**.
