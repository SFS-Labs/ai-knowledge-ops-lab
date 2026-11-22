// Live browser-only Qwen inference. No SFS API, secrets, storage or replay responses.
"use strict";
const select = document.getElementById("model");
const issue = document.getElementById("issue");
const load = document.getElementById("load");
const classify = document.getElementById("classify");
const status = document.getElementById("status");
const progress = document.getElementById("progress");
const result = document.getElementById("result");
const output = document.getElementById("output");

const LABELS = new Set(["bug", "feature", "question", "documentation"]);
const SYSTEM_PROMPT = "Du wirst ein diverses Set von GitHub Software-Anfragen vorgelegt bekommen. Das musst du strukturiert klassifizieren anhand der vier Domains beziehungsweise Kategorien Bug, Feature, Question, Documentation. Das heißt, du musst den Text analysieren und identifizieren, zu welcher der vier Kategorien der Kontext letztlich die Aussage der Anfrage beziehungsweise des Tickets am besten passt. Und dementsprechend wirst du das Ganze kategorisieren. Und als Output schreibst du dann einfach nur, das ist ein Bug, das ist ein Feature, das ist eine Question, das ist eine Documentation. Und das Ganze müssen wir in die bestehende Infrastruktur einsetzen. Du musst dabei beachten, dass das wenig natürliche Sprache enthält, sondern die Verfasser der Tickets selbst Developer sind und das Ganze ziemlich, ja, aus der IT-lastig ist vom Sprecher, dass du weißt, in welchen Dimensionen du dich da befindest\n\nBezüglich Ausgabe kannst du, ja, wir können sowohl das als JSON-Ausgabe machen als auch ja wir können auch einfache Sätze als Ausgabe machen. Aber JSON ist wahrscheinlich strukturierter";
const PROMPT_VERSION = "sfs-operator-de-verbatim-v1";
let engine = null;
let busy = false;
let predictions = 0;
const LIMIT = 12;
if (/iPhone|Android|Mobile/i.test(navigator.userAgent)) {
  select.value = "Qwen2.5-0.5B-Instruct-q4f16_1-MLC";
}
function setStatus(text) { status.textContent = text; }
function isValidInput(text) {
  return text.trim().length >= 10 && text.length <= 1200 &&
    !/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/.test(text);
}
async function loadModel() {
  if (busy || engine) return;
  busy = true;
  load.disabled = true;
  result.hidden = true;
  try {
    if (!window.isSecureContext || !("gpu" in navigator)) {
      throw new Error("WebGPU nicht verfügbar. Bitte einen kompatiblen Browser mit HTTPS nutzen.");
    }
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) throw new Error("Kein WebGPU-Adapter vorhanden.");
    progress.hidden = false;
    setStatus("Lade WebLLM und Modellgewichte. Die erste Initialisierung kann dauern.");
    const { CreateMLCEngine, prebuiltAppConfig } =
      await import("https://esm.run/@mlc-ai/web-llm@0.2.87");
    if (!prebuiltAppConfig.model_list.some(item => item.model_id === select.value)) {
      throw new Error("Diese Modellvariante wird von der installierten Runtime nicht angeboten.");
    }
    const modelId = select.value;
    const loaded = await CreateMLCEngine(modelId, {
      initProgressCallback: (event) => {
        if (Number.isFinite(event.progress))
          progress.value = Math.max(0, Math.min(1, event.progress));
        // Library progress messages can contain arbitrary strings: render as plain text.
        if (typeof event.text === "string")
          setStatus(event.text.slice(0, 260));
      }
    });
    engine = loaded;
    select.disabled = true;
    classify.disabled = false;
    progress.hidden = true;
    setStatus("Modell einsatzbereit: " + modelId + ". Die Inferenz erfolgt auf diesem Gerät.");
  } catch (err) {
    progress.hidden = true;
    load.disabled = false;
    setStatus("Modell nicht verfügbar: " + (err instanceof Error ? err.message : "unbekannter Fehler") +
              ". Keine Ersatzantwort erzeugt.");
  } finally {
    busy = false;
  }
}
async function classifyIssue() {
  if (busy || !engine || predictions >= LIMIT) return;
  const text = issue.value;
  if (!isValidInput(text)) {
    setStatus("Bitte 10 bis 1.200 gültige Zeichen eingeben.");
    return;
  }
  busy = true;
  classify.disabled = true;
  result.hidden = true;
  output.textContent = "";
  setStatus("Echte Modellinferenz läuft lokal im Browser …");
  try {
    const response = await engine.chat.completions.create({
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: "Issue title and body: " + text }
      ],
      temperature: 0,
      max_tokens: 56,
      response_format: { type: "json_object" },
      stream: false
    });
    const raw = response?.choices?.[0]?.message?.content;
    if (typeof raw !== "string" || raw.length > 1024) {
      throw new Error("Modellantwort fehlt oder überschreitet das Limit.");
    }
    let parsed;
    try { parsed = JSON.parse(raw); }
    catch { throw new Error("Das Modell lieferte kein valides JSON."); }
    if (!parsed || typeof parsed !== "object" || Object.keys(parsed).length !== 1 ||
        !LABELS.has(parsed.label)) {
      throw new Error("Die Modellantwort erfüllt das Klassifikationsschema nicht.");
    }
    output.textContent = parsed.label;
    result.hidden = false;
    predictions++;
    setStatus("Lokale Modellinferenz abgeschlossen. Antwort validiert.");
  } catch (err) {
    setStatus("Keine gültige Klassifikation: " +
      (err instanceof Error ? err.message : "unbekannter Fehler") +
      ". Kein fingiertes Ergebnis.");
  } finally {
    busy = false;
    classify.disabled = predictions >= LIMIT;
    if (predictions >= LIMIT) setStatus("Sitzungslimit von 12 Modellaufrufen erreicht. Zum Fortsetzen Seite neu laden.");
  }
}
load.addEventListener("click", loadModel);
classify.addEventListener("click", classifyIssue);
