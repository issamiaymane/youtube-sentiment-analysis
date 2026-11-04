const $ = (id) => document.getElementById(id);
const CLASSES = [
  { key: "positif", label: "Positif" },
  { key: "neutre", label: "Neutre" },
  { key: "negatif", label: "Négatif" },
];

const DISPLAY = Object.fromEntries(CLASSES.map(({ key, label }) => [key, label]));

async function checkHealth() {
  const dot = $("health-dot");
  try {
    const response = await fetch("/health");
    const body = await response.json();
    dot.className = `dot ${body.model_loaded ? "ok" : "down"}`;
    $("health").textContent = body.model_loaded ? `En ligne, modèle chargé, version ${body.version}` : "Modèle indisponible";
  } catch {
    dot.className = "dot down";
    $("health").textContent = "API injoignable";
  }
}

function showMessage(text) {
  $("message").textContent = text;
  $("message").hidden = !text;
}

function render({ predictions, statistics, processing_time_ms: elapsed }) {
  const stats = CLASSES.map(({ key, label }) => {
    const wrapper = document.createElement("div");
    const name = document.createElement("dt");
    name.textContent = label;
    const value = document.createElement("dd");
    value.className = key;
    value.textContent = `${String(statistics.percentages[key]).replace(".", ",")} %`;
    wrapper.append(name, value);
    return wrapper;
  });
  $("stats").replaceChildren(...stats);
  $("timing").textContent = `${statistics.total} commentaires traités en ${String(elapsed).replace(".", ",")} ms`;

  const rows = predictions.map((prediction) => {
    const row = document.createElement("li");
    const text = document.createElement("span");
    text.className = "text";
    text.textContent = prediction.text;
    const score = document.createElement("span");
    score.className = `score ${prediction.sentiment}`;
    score.textContent = `${DISPLAY[prediction.sentiment]} · ${Math.round(prediction.confidence * 100)} %`;
    row.append(text, score);
    return row;
  });
  $("predictions").replaceChildren(...rows);
  $("results").hidden = false;
}

async function analyze() {
  const comments = $("comments").value.split("\n").map((line) => line.trim()).filter(Boolean);
  showMessage("");
  if (!comments.length) {
    $("results").hidden = true;
    showMessage("Saisissez au moins un commentaire.");
    return;
  }
  const button = $("analyze");
  button.disabled = true;
  try {
    const response = await fetch("/predict_batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comments }),
    });
    if (!response.ok) throw new Error(`L'API a répondu avec une erreur ${response.status}.`);
    render(await response.json());
  } catch (error) {
    $("results").hidden = true;
    showMessage(error instanceof TypeError ? "API injoignable." : error.message);
  } finally {
    button.disabled = false;
  }
}

$("analyze").addEventListener("click", analyze);
checkHealth();
