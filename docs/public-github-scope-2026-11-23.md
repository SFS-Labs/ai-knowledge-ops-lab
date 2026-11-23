# SFS Interactive — öffentlicher GitHub-Account: vollständiger Repository-Abgleich
**Abgleich:** 23. November 2026 über die verbundene GitHub-API, Konto `SFS-Labs` (GitHub-Owner-Typ `User`, nicht `Organization`). **Geltungsbereich:** ausschließlich öffentlich sichtbare Repositories und freigegebene öffentliche Fallstudien. Dies ist ein Snapshot, kein automatischer Discovery-Service.

## Primäre öffentliche Implementierungs- und Beleg-Repositories
| Repository | Einordnung für Besucher | Nachweisansatz |
|---|---|---|
| [SFS-Labs](https://github.com/SFS-Labs/SFS-Labs) | Profil/öffentliche Fallstudien, kein eigenständiges Produkt | Persönlicher Kompetenz- und Arbeitskontext; POINCARÉ, Education Funding |
| [ai-knowledge-ops-lab](https://github.com/SFS-Labs/ai-knowledge-ops-lab) | B2B AI-Integration und Evaluation; Website/Voice-Widget im **Draft-PR #58** | Workflow-, Routing-, SEC-/AI-Quellen und Tests |
| [tender-intelligence-case-study](https://github.com/SFS-Labs/tender-intelligence-case-study) | Technischer EU-TED-Prototyp / dokumentierte Stop-Entscheidung | A/B-Protokoll; keine gemessene Kundenwirkung |
| [sfs-genomics](https://github.com/SFS-Labs/sfs-genomics) | Datentechnik, Cloud D1, OAuth/MCP und Research-Evaluation | Engineering-Nachweis; keine klinischen Aussagen |
| [value-rail-mvp](https://github.com/SFS-Labs/value-rail-mvp) | Monitoring, deterministische Validierung, Signalsystem | Historische Offline-/CI-Läufe; kein Trading-ROI |
| [security-reviews](https://github.com/SFS-Labs/security-reviews) | Controlled MCP tool execution / REA, Sicherheitsreviews | Begrenzte Agenten-Tool-Abnahme und Prüfgrenzen |
| [ctf-skills](https://github.com/SFS-Labs/ctf-skills) | Konsolidierte CTF-/Pentesting-Skill-Integration mit Quellattribution | V8/V9-Tests, Laufzeitgrenzen; Upstream von Lukasz Jagiello |

## Weitere öffentlich sichtbare Repositories: richtige Zuschreibung
| Repository | Richtige Einordnung |
|---|---|
| [ctf-skill-factory](https://github.com/SFS-Labs/ctf-skill-factory) | **Archivierter historischer Quellstand**, weitgehend in `ctf-skills` konsolidiert; keine doppelte unabhängige Implementierung |
| [linkedin-preview-leadflow](https://github.com/SFS-Labs/linkedin-preview-leadflow) | **Öffentliches Design-/Review-Mockup** für einen LinkedIn-Beitrag, **kein veröffentlichter LinkedIn-Post**, kein Nachweis für Kampagnen- oder Umsatzerfolg |
| [agent-toolkit](https://github.com/SFS-Labs/agent-toolkit) | Atlan Agent Toolkit, Drittanbieter-/Upstream-Quellen; nicht als eigenständig gebautes SFS-Produkt ausgeben |
| [DamnVulnerableCryptoApp](https://github.com/SFS-Labs/DamnVulnerableCryptoApp) | Fremdes Übungs-/Trainingsprojekt; Herkunft kenntlich machen |
| [awesome-cryptocurrency-security](https://github.com/SFS-Labs/awesome-cryptocurrency-security) | Historische fremde Security-Quellensammlung; keine eigene Testabnahme oder originäre Entwicklung unterstellen |
| [skills-introduction-to-github](https://github.com/SFS-Labs/skills-introduction-to-github) | GitHub-Skills-Lernexercise; kein beruflicher Nachweis für Copilot-Proficiency oder Kunden-Delivery |

**Zählung:** 13 öffentlich sichtbare Repositories auf dem zugänglichen Konto; die übrigen zugänglichen Repositories sind nicht öffentlich. Keine privaten Repository-Namen, Dateiinhalte oder Projektvorhaben in den öffentlichen Agenten-Context übernehmen. Ein Repository ist nicht automatisch eine eigenständige Fallstudie; ein integriertes Upstream-Projekt ist nicht vollständig eigenständige Autorenschaft.

## Portfolio-Struktur und Projektbelege
**Zehn kuratierte technische Fallstudien** verteilen sich auf die sieben primären Repositories und auf veröffentlichte Fallstudien im Profil. Fachgebiete: (1) HubSpot–Stripe, (2) AI Knowledge Ops / service intake und SEC-Quellenarbeit, (3) Tender Intelligence, (4) SFS Genomics, (5) Education Funding, (6) Value Rail, (7) Camber × REA, (8) POINCARÉ, (9) CTF Engineering, (10) CyberChainBench × ReEVMBench. Die vollständigen Zahlen und Prüfgrenzen stehen in den getrennten projektspezifischen Wissensdokumenten.

**SFS Interactive als übergreifende demonstrierbare Integration:** Auf der öffentlich erreichbaren [Cloudflare-V2-Vorschau](https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/interactive.html) ist ein ElevenLabs-Voice-/Text-Agent per ausdrücklichem Klick eingebettet. Er nutzt dokumentbasiertes RAG, einen sicheren `open_project`-Client-Tool-Linkanzeiger, Quellzuordnung und Tests. Der GitHub-Draft [PR #58](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/58) dokumentiert Website, Quellen und Browser-Regressionen. ElevenLabs-Simulationen belegten fachliche Antworten und einen Toolaufruf; die Simulation ist kein unabhängiger Mikrofon-/Audiostream-Nachweis und kein Kunden-Deployment. AI-assisted Entwicklung ist nach Arbeitsanteil und Prüfnachweis zu attribuieren. Das Portfolio-Produkt selbst darf als Integrationsarbeitsprobe erläutert werden, nicht automatisch als elfte unabhängige Produktfallstudie.

**Faktenaktualität:** Ein öffentliches Repo kann sich ändern, ohne dass der Agent automatisch davon erfährt. `git push` ist weder erfolgreiche CI noch neue Produktfunktion. Bei Fragen nach „jetzt“, „gestern“ oder dem neusten Release nur aus tatsächlich abgefragener GitHub-API berichten. Die derzeit bestehende Website-Funktion fragt höchstens öffentliche Commit-Metadaten ab; der Sprachagent hat keinen GitHub-Live-Reader. GitHub-API-Ratenbegrenzung und fehlgeschlagene Abfragen nicht als Aktualitätsbestätigung ausgeben.

## Nutzerperspektive und berufliche Einordnung
Die Arbeit ist nicht bloß ein Katalog von Softwaretools: Von Anwenderproblemen über Anforderungen zu technisch ausführbaren Abläufen, Gegenproben, Entscheidung und erklärbarer Nutzung. Der öffentliche [Profil-README](https://github.com/SFS-Labs/SFS-Labs/blob/main/README.md) beschreibt Technical Onboarding Support, laufendes Finance-&-Capital-Markets-Studium und den Fokus auf AI-/Automation-Implementierung. Weder einen abgeschlossenen Bachelor noch Produktivkunden, eigenständige Codehandarbeit oder formale Security-Audit-Zertifizierungen erfinden. Für Recruiter relevante Reihenfolge: (1) Welche begrenzte Aufgabe könnte die Person tragen? (2) Welche Arbeit hat sie tatsächlich gezeigt? (3) Was ist dafür getestet und was muss in einem Fachgespräch noch überprüft werden?

**Interne Personal-/Projektinformationen** (beispielsweise vertrauliche Bewerbungslisten, psychologische Selbstberichte, medizinische Daten oder private Build-Assets) sind für den öffentlichen SFS-Interactive-Agenten kein Material. Nie aus Assistant-Memory ungefragt in eine öffentlich erreichbare Wissensbasis übertragen.
