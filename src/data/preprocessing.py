"""Nettoyage du texte, partagé entre l'entraînement et l'API.

Le même code doit tourner aux deux endroits : un écart entre les deux fausserait
les prédictions en production sans déclencher d'erreur.
"""
import html
import re

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"[@#]\w+")
TIMESTAMP_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
TAG_RE = re.compile(r"<[^>]+>")
NON_ALPHA_RE = re.compile(r"[^a-z\s]")
SPACES_RE = re.compile(r"\s+")

# Le dataset Reddit ne contient pas d'emojis, alors que les commentaires YouTube en
# sont pleins. On les traduit donc en mots déjà connus du vocabulaire du modèle.
EMOJI_WORDS = {
    "😀": "happy", "😃": "happy", "😄": "happy", "😁": "happy", "😊": "happy",
    "🙂": "happy", "😂": "funny", "🤣": "funny", "😍": "love", "🥰": "love",
    "😘": "love", "❤": "love", "💕": "love", "💖": "love", "🔥": "great",
    "👍": "good", "👏": "great", "🎉": "great", "💯": "great", "🙏": "thanks",
    "😢": "sad", "😭": "sad", "😞": "sad", "😔": "sad", "💔": "sad",
    "😡": "angry", "😠": "angry", "🤬": "angry", "👎": "bad", "🤮": "disgusting",
    "💩": "bad", "😒": "bad",
}


def clean_text(text: object) -> str:
    """Retourne le texte en minuscules, sans URL, mention ni caractère spécial."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = TAG_RE.sub(" ", text)
    for symbol, word in EMOJI_WORDS.items():
        text = text.replace(symbol, f" {word} ")
    text = text.lower().replace("’", "'").replace("'", "")
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = TIMESTAMP_RE.sub(" ", text)
    text = NON_ALPHA_RE.sub(" ", text)
    return SPACES_RE.sub(" ", text).strip()
