# SFS Interactive — öffentliches SFS.Labs-Portfolio, organisationsübergreifend
Quellenabgleich: 23.11.2026 | Quelle: öffentliche SFS-Labs-Repositories und veröffentlichte Fallstudien.
Zweck: Beleggestützte Wissensbasis eines einzigen KI-Portfolio-Guides für Mathias Steinbach. Nicht auf eine Website oder Cybersecurity beschränkt.
Status: datierter Projekt-Snapshot. Ergänzend besitzt der Agent öffentliches GitHub-Katalog-/README-/Dokument-/Commit-Lesewerkzeug auf Abruf sowie täglich synchronisierte öffentliche Profil- und Portfolio-Quellen. Keine sekundengenaue Vollsynchronisierung. Private Projekte, persönliche Daten, Kundendaten, versteckte Benchmark-Referenzen und nicht veröffentlichte Implementierungsdetails sind ausgeschlossen.

## 1. Rolle und vollständige fachliche Landkarte

Mathias bearbeitet Probleme mit Analyse, Anforderungsdefinition, Architektur, API-/Workflow-Integration, Automatisierung, Datenqualität, technischen Tests und Evaluation. SFS.Labs ist die öffentliche Nachweisfläche dieser Arbeit, keine Behauptung eines etablierten kommerziellen Softwarebetriebs. Der technische Schwerpunkt umfasst B2B-AI-Implementierung, Workflow Automation, Solutions/Customer Engineering, Daten- und MCP-Integration, quantitative Evaluation, Agent Tooling und Cybersecurity. Welche Fallstudie relevant ist, richtet sich nach der Frage des Besuchers, nicht nach der Website, auf der das Gespräch beginnt.

**Fachgebiete und zehn unterscheidbare öffentliche Arbeitsproben:**
A. B2B Automation, Finance / Revenue Operations: (1) HubSpot × Stripe, (2) AI Knowledge Ops / B2B Service Intake, (3) Tender Intelligence.
B. Data Platforms und MCP: (4) SFS Genomics, (5) SFS Education Funding.
C. Monitoring und Agent Integration: (6) Value Rail, (7) Camber × REA MCP Execution.
D. Cybersecurity und unabhängige Evaluation: (8) POINCARÉ Solidity Code Review, (9) Penetration Testing / CTF Engineering, (10) CyberChainBench × ReEVMBench Adversarial Evaluation.

Diese zehn sind eine kuratierte Auswahl aus Mathias' öffentlichem GitHub-Portfolio. **Alle öffentlichen SFS-Labs-Repositories gehören zu seinem vorzeigbaren Portfolio** – eigene Implementierungen ebenso wie Integrationen, Übungen, Forks und kuratierte Quellen. Unterschiede in Upstream-Herkunft oder Entwicklungsstand betreffen den konkret erklärten Beitrag, nicht die Portfoliozugehörigkeit.

Öffentliche Einstiegspunkte:
- Öffentliches GitHub-Konto: https://github.com/SFS-Labs
- Persönliches öffentliches GitHub-Profil: https://github.com/SFS-Labs/SFS-Labs
- Vorhandene Recruiter-Seite: https://sfs-labs.github.io/ai-knowledge-ops-lab/recruiter.html
- Öffentlich erreichbare GitHub-Pages-Projektübersicht: https://sfs-labs.github.io/ai-knowledge-ops-lab/work.html
- Öffentlich erreichbarer Sprach-/Textagent auf GitHub Pages: https://sfs-labs.github.io/ai-knowledge-ops-lab/interactive.html
- Dazugehöriger Website-Entwurf: https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/58

Die V2-Unterseiten work.html, security-engineering.html, agent-systems.html und adversarial-evaluation.html wurden mit dem Merge von PR #58 in main veröffentlicht und anschließend unter den produktiven GitHub-Pages-URLs extern abgerufen.

## 2. HubSpot × Stripe — Finance / Revenue Operations / API reconciliation

Problem: Stimmt die in HubSpot vereinbarte Raten-/Zahlungsverpflichtung mit den in Stripe vorhandenen Rechnungen überein? Ein lesender Python-Workflow gleicht Daten ab und meldet fehlende oder doppelte Rechnungen, abweichende Beträge/Währungen und überfällige Fälle zur manuellen Prüfung. Trennung von Integrationslogik, Testdaten, wirtschaftlicher Modellannahme und tatsächlichem Geschäftsnutzen.

Der dokumentierte **simulierte** Fall mit sechs Deals täglich und 5 % Abweichungen modelliert 14 Stunden 27 Minuten weniger Prüfaufwand je 100 Geschäftstage gegenüber einer Tabellenprüfung; bedingter netto nutzbarer Zeitwert nach angenommenen Kosten 225,22 €. Bei 28 % simulierten Abweichungen kehrt sich der Zeitvorteil um. Diese Zahlen sind KEINE beobachteten Kundeneinsparungen, kein Live-Produktions-ROI und keine verallgemeinerte Erfolgsquote. Arbeitsprobe zeigt kontrollierte Integration, Fehlerklassifikation, Kosten- und Sensitivitätsanalyse.

Primärbeleg: https://sfs-labs.github.io/ai-knowledge-ops-lab/hubspot-stripe.html
Repository: https://github.com/SFS-Labs/ai-knowledge-ops-lab

## 3. AI Knowledge Ops — Service Intake, lokales LLM, n8n, Python, Evaluation

Echt implementierte Kette: lokales Qwen → n8n → Python-API → SQLite; Review/Approval getrennt von Modellklassifikation, Reject/Restart und Fail-closed. Historisch dokumentiert: 36 echte Modellinferenzen und 135 Python-Regressionstests (Recheck 10.11.2026). Das sind Ausführungsbelege, nicht 135 erfolgreiche Kundenfälle.

Retrospektiver **synthetischer** Service-Routing-Pilot mit 32 Anfragen: LLM-only 10/32 korrekte Kategorien/Dringlichkeiten, Rules-only 11/32, nachträglich gewählter Hybrid 22/32. Die Regeln übersehen 5 von 9 High-Urgency-Fällen; die vermeintlich bessere Gesamtgenauigkeit reicht deshalb nicht als Freigabe für kritische unbeaufsichtigte Fälle. Die Hybridwahl ist post-hoc, explorative Signifikanz nicht konfirmatorisch. Auf 96 realen NLBSE-Issues erreichte Qwen v2 im dokumentierten Wiederholungslauf 55/96 vs. 46/96 für Keyword-Regeln; gepaarte Unsicherheit lässt einen Nullvorteil zu. Ein getrennter Volvo-Prozessdatensatz liefert 7.554 Fälle/65.533 Ereignisse, keine Kundeneinsparung. Methodik: Vergleich mit Baseline, Gegenbeispiel, abhängige Fehlerkosten und Go/No-Go.

Es gibt im selben Repository auch **SEC Form 8-K Knowledge Operations** mit Quellenmanifest (15 Dokumente), regelbasierten und dokumentiert AI-assisted Verarbeitungswegen, Grundwahrheit mit Review-Grenzen. Diese Quelle nicht mit dem Service-Intake-Pilot gleichsetzen.

Primärquelle: https://github.com/SFS-Labs/ai-knowledge-ops-lab
Entscheidungsbeleg: https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/main/showcases/internal-service-intake/DECISION_EVIDENCE_BRIEF.md

## 4. Tender Intelligence — EU TED, Dokumentenänderungen, begrenzte Modellinferenz

Ein modularer Cloudflare-Workers-Prototyp mit offizieller EU-TED-API, nachvollziehbarer Quellenverarbeitung und regelbasiertem Entscheidungsbrief. Bei fünf Versionen einer polnischen Bekanntmachung wurden vier Verschiebungen einer Angebotsfrist identifiziert. Vergleich Baseline vs. erweitertem Prompt/Risikohinweisen bei **gleichem vorbereiteten Evidenzsatz**, vier Modellaufrufen insgesamt: je 32/32 vorbereitete Fakten korrekt; erwartete Quellenreferenzen 26/32 Baseline gegen 25/32 erweitert. Kein belegter Zusatznutzen des erweiterten Prompts. Kommerzielle Weiterentwicklung bewusst pausiert, nicht als Kunden-ROI oder produktiver Verkauf darstellen.

Primärquelle: https://github.com/SFS-Labs/tender-intelligence-case-study/blob/main/docs/DECISION-LOG.md
Repository: https://github.com/SFS-Labs/tender-intelligence-case-study

## 5. SFS Genomics — mobile data engineering, EU Cloudflare D1, OAuth MCP

Aus einem iPhone-seitig aufgenommenen SNP-Array-Export entstand eine persistente Forschungsinfrastruktur: 609.346 Rohzeilen, 607.051 akzeptierte Calls, 256 persistente EU-D1-Partitionen; Aggregatreconciliation. OAuth PKCE/DCR für begrenzte MCP-Tools, ChatGPT-authentifizierte Lookups; GWAS-Catalog-/Ensembl-Anfragen mit Studien-IDs und Referenzwerten. Fünf gepinnte Referenzloci mit Fehler- und Abstention-Gates; reale D1-Quota- und OAuth-Fehler untersucht. Technische Datenpipeline-/Auth-/MCP-Ergebnisse sind dokumentiert. **Keine** klinische Diagnose, keine orthogonale Bestätigung aller SNPs, keine validierten persönlichen Risikoprognosen. Niemals private Rohgenotypen oder medizinische Schlussfolgerungen offenlegen.

Primärquelle: https://github.com/SFS-Labs/sfs-genomics/blob/main/genomics/PORTFOLIO.md
Repository: https://github.com/SFS-Labs/sfs-genomics

## 6. SFS Education Funding — provenance, document pipelines, rule-based eligibility

Engineering eines dokument-/claim-basierten Förderquellen-Prototyps mit Cloudflare D1, Versionierung, SQL/FTS5, dreistufigen Prüfergebnissen (Pass/Fail/Unknown) und sieben begrenzten OAuth-MCP-Tools. Historischer Checkpoint 28.10.2026: 16.088 entdeckte/vorgemerkte URLs, 725 Dokumente, 729 Versionen, 353 Kandidaten, 2.025 dokumentierte Quellenaussagen, **null verifizierte Förderprogramme**. Interne Protokolle nennen 15 Tests; Rohlogs/Code sind nicht vollständig öffentlich reproduzierbar. Kein individueller Förderanspruch und keine vollständig bestätigte iOS-E2E-Abnahme.

Öffentliche Fallstudie: https://github.com/SFS-Labs/SFS-Labs/blob/main/case-studies/education-funding.md
Implementierungsrepository ist privat; dortige URLs nicht als öffentliche Nachweise verwenden.

## 7. Value Rail — monitoring, feed, inventory lifecycle, validation

Python-Monitor für CoinGate-Geschenkkarten-Clearance mit Quelldaten-Validierung, Rabattfiltern, Zuständen new/changed/returned, persistenten Signalen und GitHub-Actions-Scheduled-Feed. Optional SQLite/Alembic, Web UI und Outbox/Telegram/log Sinks. Historischer lokaler Test vom 24.10.2026: **326 bestandene Offline-Tests**; separates erfolgreicher Actions-Feed-Lauf dokumentiert. Ein beobachteter nominaler Preisnachlass ist weder ein ausführbarer Trade noch netto Ertrag, und eine erfolgreiche Workflow-Ausführung beweist keine aktuelle Marktverfügbarkeit oder erfolgreiche Telefon-Push-Zustellung.

Primärquelle: https://github.com/SFS-Labs/value-rail-mvp
Review: https://github.com/SFS-Labs/value-rail-mvp/blob/main/REVIEW.md

## 8. Camber × REA — agent tool selection, controlled MCP execution

Ein tatsächlich laufender Camber-Agent wählte für eine harmlose Android-Research-Readiness-Frage die read-only Werkzeuge binary_session({}), inspect_apktool_client({}), inspect_adb_client({}). Ein GitHub-Actions-Runner startete rea-agents@6.8.0, listete 229 damals vorhandene Tools und führte **genau drei** erlaubte MCP tools/call-Operationen aus; 33 Validierungschecks bestanden. Allowlist, leere Argumente, begrenzte Ausführung und provider gate wurden geprüft. Das ist ein E2E-Techniknachweis für kontrollierte Agenten-Werkzeugausführung, nicht für selbständig neu gestartete Camber-Inferenz, beliebige Toolrechte oder eine echte APK-Analyse.

Fallstudie in öffentlicher Vorschau: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/agent-systems.html
Primärquelle: https://github.com/SFS-Labs/security-reviews/blob/main/docs/CAMBER_MULTITOOL_ACCEPTANCE.md
Ausführung: https://github.com/SFS-Labs/security-reviews/actions/runs/40716523503

## 9. POINCARÉ — unabhängiger Solidity Security Code Review

Unabhängiger, ausdrücklich scope-begrenzter Review eines Uniswap-v4-Hooks: sieben Erstpartei-Solidity-Dateien (~1298 LOC) fixiert; ursprünglich 222/222 Foundry-Tests in isolierter Umgebung reproduziert, statische Tools triagiert, 2 Low-Findings und 8 Notes dokumentiert. Danach neun Entwickler-Remediation-Commits über 26 Dateien source-level geprüft. Maintainer meldete 240 Tests des neuen Stands, vom Reviewer nicht unabhängig wiederholt. Keine formale Audit-Zertifizierung, Mainnet-Garantie, vollständige Dependency- oder Frontendprüfung.

Primärquelle: https://github.com/SFS-Labs/SFS-Labs/blob/main/security-review/case-studies/poincare-2026.md

## 10. Cybersecurity · Penetration Testing · CTF Engineering — Skill Integration / Toolchain

CTF-Skill-Integration und Solidity-Security-Orchestrierung. Im öffentlichen kanonischen Repository sind **133 eigenständige Wissenskarten aus 134 Quelleneinträgen** enthalten (ein Alias); dies sind keine 133 installierten Pentesting-Scanner. Gemergter V8/V9-Stand: 170 bestandene CI-Tests, zwei Skips, 1616 Subtests (22.11.2026). Lokaler Toolchain-Lauf auf **absichtlich verwundbarem Test-Vault**: Surya-Map, zwölf Slither-Befunde, drei bestandene Forge-Tests und Negativkontrolle. Die Aktivierung durch eine frisch gestartete Agentensitzung und generalisierbare autonome Discovery sind nicht unabhängig bewiesen. Separater **Draft-PR #4**: historisch 184 Tests, zwei Skips, 1616 Subtests; Draft nicht als gemergtes Main darstellen.

Die ursprünglichen CTF-Agent-Skills stammen aus dem MIT-lizenzierten Open-Source-Projekt von Lukasz Jagiello; SFS.Labs integrierte Factory, Router, Orchestrierung und Tests. Interner Tool-/Produktname des lokalen Agenten ist nicht die öffentliche Projektüberschrift. Die Seite darf es als Cybersecurity/CTF/Pentesting präsentieren, ohne daraus bestätigte externe Pentest-Ergebnisse zu machen.

Fallstudie in Vorschau: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/security-engineering.html
Kanonischer Code: https://github.com/SFS-Labs/ctf-skills
Runtime-Abnahme: https://github.com/SFS-Labs/ctf-skills/blob/main/docs/FREEBUFF-V8-RUNTIME-ACCEPTANCE.md
Draft-PR #4: https://github.com/SFS-Labs/ctf-skills/pull/4

## 11. CyberChainBench × ReEVMBench — native adversarial evaluation / CTF benchmarks

Getrennt von der CTF-Toolchain: zwei native Smart-Contract-Security-Benchmark-Adapter, maskierte Detektionsbriefings, gefrorene Reports, getrenntes Referenzgrading und fixierte Upstream-Quellen. CyberChainBench nutzt Chain/Contract ohne Attack-Labels und vergleicht nach Berichtsfestschreibung type+function; ReEVMBench nutzt Source-Audit-Recipes/Historical Commit, bei fehlendem base_commit explizite HEAD-Snapshot-Provenienz. Originale Foundry-Submodul- und Judge-CLI-Kompatibilitätsprobleme wurden im historischen Factory-Repo behoben. Die dokumentierten Kalibrierungsläufe enthielten unter anderem HTTP-429 beim historischen RPC-Replay und Solver-Konstruktionsprobleme vor einem Fix. **Keine** verifizierte unabhängige Erfolgsquote eines autonomen Blindtest-Agenten; Testharness und richtige Antwort sind voneinander zu trennen. Archiviertes historisches Repo, nicht mit laufender Production-Toolchain verwechseln.

Fallstudie in Vorschau: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/adversarial-evaluation.html
Originale Benchmark-Spezifikation: https://github.com/SFS-Labs/ctf-skill-factory/blob/main/benchmarks/README.md
Fix-PR: https://github.com/SFS-Labs/ctf-skill-factory/pull/5

## 12. Gesprächsführung, Attribution und Geltungsbereich

Der Guide soll Fragen aus allen beschriebenen Bereichen beantworten können, auch fachübergreifende Fragen wie: Welches Projekt zeigt API-Integration? Welche Aufgaben sind B2B-relevant? Welche Ergebnisse sind CI-bestätigt? Welche Entscheidung fiel nach einem negativen Experiment? Wo wurde ein Modell gegen Regeln verglichen? Er soll sinnvolle Zusammenhänge zwischen Fallstudien herstellen, statt aus der Reihenfolge dieses Dokuments eine Rangliste zu machen.

Wenn eine konkrete Behauptung gefragt ist, nenne den dazugehörigen direkten Primärnachweis. Unterscheide selbst geschriebene Anforderungen/Evaluation von AI-assisted Coding und upstream übernommenen Komponenten. Keine Kundenwirkung, wirtschaftlichen ROI, produktiven Einsatz oder formelle Zertifizierung behaupten, wenn nur Tests, Modelle oder historische Eigenauskünfte vorliegen.

**GitHub-Aktualität:** Dieser Quellenstand ist datiert. Die verbundenen read-only Werkzeuge `github_public_catalog` und `github_public_lookup` ermöglichen den Abruf neu öffentlich sichtbarer Repositories, ihrer README-Dateien und ausgewählter öffentlicher Dokument-/Commit-Quellen. Die öffentliche Portfolio-Seite und das GitHub-Profil sind außerdem als täglich synchronisierte URL-Wissensquellen hinterlegt. Relevante CI-, PR- oder Produktivitätsbehauptungen benötigen die entsprechende separate Primärquelle.

**Werkzeug:** open_project ist ein browserseitiger Link-Anzeiger, kein GitHub-Abfragetool. Verfügbare Keys: security_engineering, benchmark_engineering, agent_execution, hubspot_stripe, knowledge_ops, tender_intelligence, sfs_genomics, value_rail, profile. Öffnet nicht automatisch neue Tabs, zeigt nur die erlaubte Quelle, soweit der Browser sie unterstützt. Bei fehlendem Tool direkte geprüfte URL als Text ausgeben. Bei Education Funding und POINCARÉ können die oben genannten öffentlichen Quellen direkt verlinkt werden, selbst wenn es keinen eigenen Toolkey gibt.

**Datenschutz:** Keine privaten Repositories, Rohgenotypen, sonstige persönlichen/medizinischen Informationen, Zugangsdaten, versteckte Evaluationsreferenzen oder Kundendaten öffentlich machen. Es gibt öffentlich nachvollziehbare Arbeitsproben und ggf. interne/partielle Nachweise; das ist ausdrücklich nicht das Gleiche.

**Einordnung:** Dies ist eine redaktionell kuratierte Quelle, kein automatischer GitHub-Index und keine Garantie auf Vollständigkeit aller öffentlichen Repositories. Bei unbekannten oder neueren Projekten Unsicherheit offen angeben, nicht Namen oder Fakten erfinden.
