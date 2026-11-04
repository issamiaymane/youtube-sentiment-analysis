// Extrait les commentaires de la page YouTube à la demande du popup.
// YouTube ne charge les commentaires qu'au défilement : on défile jusqu'à en avoir assez,
// puis on rend à l'utilisateur sa position de lecture.
(() => {
  if (window.__ytSentimentLoaded) return;
  window.__ytSentimentLoaded = true;

  const COMMENT_SELECTOR = "ytd-comments #content-text";
  const STEP_MS = 600;
  const MAX_IDLE_STEPS = 8; // Abandon après ~5 s sans nouveau commentaire.

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const countComments = () => document.querySelectorAll(COMMENT_SELECTOR).length;

  function readComments(limit) {
    const seen = new Set();
    const comments = [];
    for (const node of document.querySelectorAll(COMMENT_SELECTOR)) {
      const text = node.innerText.trim();
      if (!text) continue;
      const renderer = node.closest("ytd-comment-view-model, ytd-comment-renderer");
      const author = renderer?.querySelector("#author-text")?.innerText.trim() || "";
      const key = `${author}\n${text}`;
      if (seen.has(key)) continue;
      seen.add(key);
      // Les réponses visibles sont gardées, et marquées pour rester distinguables des fils.
      comments.push({ text, author, isReply: Boolean(node.closest("#replies")) });
      if (comments.length >= limit) break;
    }
    return comments;
  }

  async function loadComments(limit) {
    const startY = window.scrollY;
    let idleSteps = 0;
    let previous = countComments();
    while (previous < limit && idleSteps < MAX_IDLE_STEPS) {
      const section = document.querySelector("ytd-comments");
      if (previous === 0 && section) section.scrollIntoView();
      else window.scrollTo(0, document.documentElement.scrollHeight);
      await sleep(STEP_MS);
      const current = countComments();
      idleSteps = current > previous ? 0 : idleSteps + 1;
      previous = current;
    }
    window.scrollTo(0, startY);
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type !== "EXTRACT_COMMENTS") return false;
    loadComments(message.limit)
      .then(() => {
        sendResponse({
          comments: readComments(message.limit),
          title: document.querySelector("ytd-watch-metadata h1")?.innerText.trim() || document.title,
        });
      })
      .catch((error) => sendResponse({ error: error.message }));
    return true; // Réponse asynchrone.
  });
})();
