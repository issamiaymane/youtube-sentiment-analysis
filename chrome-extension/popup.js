const BATCH_SIZE = 100;
// Un Space Hugging Face en veille peut mettre près d'une minute à se réveiller.
const REQUEST_TIMEOUT_MS = 60000;
const RENDER_LIMIT = 300;
const CLASSES = [
  { key: "positif", label: "Positif" },
  { key: "neutre", label: "Neutre" },
  { key: "negatif", label: "Négatif" },
];

const SENTIMENT_LABELS = Object.fromEntries(CLASSES.map(({ key, label }) => [key, label]));

const $ = (id) => document.getElementById(id);
const state = { items: [], stats: null, filter: "all", title: "", apiUrl: DEFAULT_API_URL };

class UserError extends Error {}

function showStatus(message, isError = false) {
  const status = $("status");
  status.textContent = message;
  status.className = isError ? "error" : "";
  status.hidden = !message;
}

// --- Réglages ---

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
}

async function loadPreferences() {
  const saved = await chrome.storage.local.get(["theme", "apiUrl"]);
  applyTheme(saved.theme || "light");
  state.apiUrl = saved.apiUrl || DEFAULT_API_URL;
  $("api-url").value = state.apiUrl;
}

function isAllowedApiUrl(value) {
  try {
    const url = new URL(value);
    return (
      (url.protocol === "https:" && url.hostname.endsWith(".hf.space")) ||
      (url.protocol === "http:" && ["localhost", "127.0.0.1"].includes(url.hostname) && url.port === "7860")
    );
  } catch {
    return false;
  }
}

async function saveApiUrl() {
  const value = $("api-url").value.trim().replace(/\/+$/, "");
  const hint = $("settings-status");
  if (!isAllowedApiUrl(value)) {
    hint.textContent = "URL refusée : utilisez https://*.hf.space ou http://localhost:7860.";
    return;
  }
  state.apiUrl = value;
  await chrome.storage.local.set({ apiUrl: value });
  hint.textContent = "URL enregistrée.";
}

// --- Extraction ---

async function getYouTubeTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url || !/^https:\/\/www\.youtube\.com\/(watch|shorts\/)/.test(tab.url)) {
    throw new UserError("Ouvrez une vidéo YouTube, puis relancez l'analyse.");
  }
  return tab;
}

async function extractComments(tab, limit) {
  const message = { type: "EXTRACT_COMMENTS", limit };
  let response;
  try {
    response = await chrome.tabs.sendMessage(tab.id, message);
  } catch {
    // Onglet ouvert avant l'installation de l'extension : le content script n'y est pas encore.
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content.js"] });
    response = await chrome.tabs.sendMessage(tab.id, message);
  }
  if (response?.error) throw new Error(response.error);
  if (!response?.comments?.length) {
    throw new UserError("Aucun commentaire trouvé. Ils sont peut-être désactivés sur cette vidéo.");
  }
  return response;
}

// --- API ---

async function postBatch(comments) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${state.apiUrl}/predict_batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comments }),
      signal: controller.signal,
    });
    if (!response.ok) throw new UserError(`L'API a répondu avec une erreur ${response.status}.`);
    return await response.json();
  } catch (error) {
    if (error instanceof UserError) throw error;
    if (error.name === "AbortError") {
      throw new UserError("L'API ne répond pas après 60 s. Si le Space était en veille, réessayez.");
    }
    throw new UserError(`Impossible de joindre l'API (${state.apiUrl}). Vérifiez qu'elle est démarrée.`);
  } finally {
    clearTimeout(timer);
  }
}

async function analyze(comments) {
  const predictions = [];
  const started = performance.now();
  let modelMs = 0;
  for (let i = 0; i < comments.length; i += BATCH_SIZE) {
    showStatus(`Analyse de ${Math.min(i + BATCH_SIZE, comments.length)} / ${comments.length} commentaires…`);
    const data = await postBatch(comments.slice(i, i + BATCH_SIZE).map((c) => c.text));
    predictions.push(...data.predictions);
    modelMs += data.processing_time_ms;
  }
  return { predictions, modelMs, totalMs: performance.now() - started };
}

// Recalculées ici : l'API ne connaît les statistiques que batch par batch.
function computeStats(items) {
  const counts = { positif: 0, neutre: 0, negatif: 0 };
  for (const item of items) counts[item.sentiment] += 1;
  return { total: items.length, counts };
}

// --- Affichage ---

function percent(count, total) {
  return total ? Math.round((1000 * count) / total) / 10 : 0;
}

function svgElement(name, attributes) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  return element;
}

function renderSummary() {
  const { counts, total } = state.stats;
  const donut = $("donut");
  const legend = $("legend");
  donut.replaceChildren();
  legend.replaceChildren();

  const styles = getComputedStyle(document.documentElement);
  // Circonférence 100 : la longueur d'un arc vaut directement son pourcentage.
  const radius = 100 / (2 * Math.PI);
  let offset = 0;
  for (const { key, label } of CLASSES) {
    const share = (100 * counts[key]) / total;
    donut.append(svgElement("circle", {
      cx: 21, cy: 21, r: radius, fill: "none",
      stroke: styles.getPropertyValue(`--${key}`).trim(),
      "stroke-width": 6,
      "stroke-dasharray": `${share} ${100 - share}`,
      "stroke-dashoffset": -offset,
    }));
    offset += share;

    const row = document.createElement("div");
    const dot = document.createElement("span");
    dot.className = "dot";
    dot.style.background = `var(--${key})`;
    const name = document.createElement("dt");
    name.textContent = label;
    const value = document.createElement("dd");
    value.textContent = `${String(percent(counts[key], total)).replace(".", ",")} % (${counts[key]})`;
    row.append(dot, name, value);
    legend.append(row);
  }
  const center = svgElement("text", { x: 21, y: 21 });
  center.textContent = total;
  donut.append(center);
}

function renderComments() {
  const list = $("comments");
  const visible = state.items.filter((item) => state.filter === "all" || item.sentiment === state.filter);
  // textContent uniquement : un commentaire est un contenu hostile potentiel.
  const nodes = visible.slice(0, RENDER_LIMIT).map((item) => {
    const li = document.createElement("li");
    li.className = item.sentiment;
    const row = document.createElement("div");
    row.className = "row";
    const author = document.createElement("span");
    author.className = "author";
    author.textContent = `${item.isReply ? "↳ " : ""}${item.author}`;
    const score = document.createElement("span");
    score.className = "score";
    score.textContent = `${SENTIMENT_LABELS[item.sentiment]} · ${Math.round(item.confidence * 100)} %`;
    row.append(author, score);
    const text = document.createElement("p");
    text.className = "text";
    text.textContent = item.text;
    li.append(row, text);
    return li;
  });
  if (!nodes.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Aucun commentaire pour ce filtre.";
    nodes.push(empty);
  }
  list.replaceChildren(...nodes);
  list.scrollTop = 0;
}

function renderResults(modelMs, totalMs) {
  $("video-title").textContent = state.title;
  $("meta").textContent =
    `Réponse de l'API en ${Math.round(totalMs)} ms, dont ${modelMs.toFixed(1)} ms pour le modèle.`;
  renderSummary();
  renderComments();
  $("results").hidden = false;
}

// --- Export ---

function visibleItems() {
  return state.items.filter((item) => state.filter === "all" || item.sentiment === state.filter);
}

async function copyResults() {
  const { counts, total } = state.stats;
  const summary = CLASSES.map(({ key, label }) => `${label} : ${percent(counts[key], total)} %`).join(" | ");
  const lines = visibleItems().map(
    (item) => `[${item.sentiment} ${Math.round(item.confidence * 100)} %] ${item.text.replace(/\s+/g, " ")}`
  );
  const button = $("copy");
  try {
    await navigator.clipboard.writeText(`${state.title}\n${summary}\n\n${lines.join("\n")}`);
    button.textContent = "Copié";
  } catch {
    button.textContent = "Échec de la copie";
  }
  setTimeout(() => { button.textContent = "Copier"; }, 1500);
}

function csvCell(value) {
  let text = String(value);
  // Empêche un tableur d'exécuter un commentaire commençant par =, +, - ou @.
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}

function exportCsv() {
  const rows = [["auteur", "reponse", "sentiment", "confiance", "commentaire"]];
  for (const item of visibleItems()) {
    rows.push([item.author, item.isReply ? "oui" : "non", item.sentiment, item.confidence, item.text]);
  }
  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\r\n");
  const url = URL.createObjectURL(new Blob(["﻿", csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "sentiments-youtube.csv";
  link.click();
  URL.revokeObjectURL(url);
}

// --- Événements ---

async function runAnalysis() {
  const button = $("analyze");
  button.disabled = true;
  $("results").hidden = true;
  try {
    const tab = await getYouTubeTab();
    showStatus("Chargement des commentaires de la page…");
    const { comments, title } = await extractComments(tab, Number($("limit").value));
    const { predictions, modelMs, totalMs } = await analyze(comments);
    state.items = comments.map((comment, i) => ({ ...comment, ...predictions[i] }));
    state.stats = computeStats(state.items);
    state.title = title;
    renderResults(modelMs, totalMs);
    showStatus("");
  } catch (error) {
    const known = error instanceof UserError;
    if (!known) console.error(error);
    showStatus(known ? error.message : "Erreur inattendue pendant l'analyse. Rechargez la page YouTube et réessayez.", true);
  } finally {
    button.disabled = false;
  }
}

$("analyze").addEventListener("click", runAnalysis);
$("copy").addEventListener("click", copyResults);
$("csv").addEventListener("click", exportCsv);
$("api-url").addEventListener("change", saveApiUrl);

$("theme").addEventListener("click", async () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
  await chrome.storage.local.set({ theme: next });
  if (state.stats) renderSummary();
});

$("settings-toggle").addEventListener("click", (event) => {
  const panel = $("settings");
  panel.hidden = !panel.hidden;
  event.currentTarget.setAttribute("aria-expanded", String(!panel.hidden));
});

for (const chip of document.querySelectorAll(".chip")) {
  chip.addEventListener("click", () => {
    state.filter = chip.dataset.filter;
    document.querySelectorAll(".chip").forEach((c) => c.classList.toggle("active", c === chip));
    renderComments();
  });
}

loadPreferences();
