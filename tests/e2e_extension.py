"""Test de bout en bout : extension chargée dans Chromium -> vraie vidéo YouTube -> API.

Non lancé par pytest (nom sans préfixe test_) : il dépend du réseau et de la page YouTube.
    pip install playwright && playwright install chromium
    uvicorn app_api:app --port 7860   # dans un autre terminal
    python tests/e2e_extension.py [URL_API]
"""
import hashlib
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "chrome-extension"
SHOTS = ROOT / "docs" / "screenshots"
VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
API_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7860"

# Ouvert dans un onglet, le popup se verrait lui-même comme onglet actif : on lui désigne YouTube.
TARGET_YOUTUBE = """async () => {
  const [tab] = await chrome.tabs.query({ url: "https://www.youtube.com/*" });
  chrome.tabs.query = async () => [tab];
}"""


def unpacked_extension_id(path: Path) -> str:
    # Chrome dérive l'identifiant d'une extension non empaquetée du SHA-256 de son chemin.
    digest = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:32]
    return "".join(chr(ord("a") + int(c, 16)) for c in digest)


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'OK  ' if ok else 'FAIL'} {name} {detail}")
    if not ok:
        check.failed = True


check.failed = False


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p, tempfile.TemporaryDirectory() as profile:
        context = p.chromium.launch_persistent_context(
            profile,
            channel="chromium",
            headless=True,
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            args=[f"--disable-extensions-except={EXTENSION}", f"--load-extension={EXTENSION}"],
        )
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        extension_id = unpacked_extension_id(EXTENSION)
        check("identifiant de l'extension", bool(extension_id), extension_id)

        youtube = context.new_page()
        youtube.goto(VIDEO_URL, wait_until="domcontentloaded")
        # Écran de consentement éventuel : on refuse le non essentiel.
        reject = youtube.get_by_role("button", name="Reject all")
        try:
            reject.first.click(timeout=6000)
            youtube.wait_for_url("**/watch**", timeout=15000)
        except Exception:
            pass
        youtube.wait_for_selector("ytd-watch-metadata h1", timeout=30000)

        popup = context.new_page()
        popup.set_viewport_size({"width": 420, "height": 720})
        popup.goto(f"chrome-extension://{extension_id}/popup.html")
        popup.evaluate(TARGET_YOUTUBE)
        popup.click("#settings-toggle")
        popup.fill("#api-url", API_URL)
        popup.dispatch_event("#api-url", "change")
        popup.wait_for_function("document.getElementById('settings-status').textContent.includes('enregistr')")
        popup.click("#settings-toggle")
        popup.select_option("#limit", "50")

        popup.click("#analyze")
        popup.wait_for_selector("#results:not([hidden]), #status.error", timeout=120000)
        error = popup.locator("#status.error")
        if error.count():
            check("analyse", False, error.inner_text())
            youtube.screenshot(path=str(SHOTS / "debug_youtube.png"))
            return 1

        total = popup.locator("#comments li").count()
        check("commentaires extraits et classés", total > 0, f"{total} commentaires")
        print("    ", popup.locator("#meta").inner_text())
        print("    ", popup.locator("#legend").inner_text().replace("\n", " "))
        fonts = ('["1em Anton", "1em Outfit", "1em \'JetBrains Mono\'"]'
                 ".every(font => document.fonts.check(font))")
        check("polices locales chargées", popup.evaluate(fonts))
        check("thème clair par défaut", popup.evaluate("document.documentElement.dataset.theme") == "light")
        popup.screenshot(path=str(SHOTS / "popup_light.png"))

        popup.click("#theme")
        check("mode sombre", popup.evaluate("document.documentElement.dataset.theme") == "dark")
        popup.screenshot(path=str(SHOTS / "popup_dark.png"))
        popup.click("#theme")
        check("retour au thème clair", popup.evaluate("document.documentElement.dataset.theme") == "light")

        for name in ("positif", "neutre", "negatif"):
            popup.click(f'.chip[data-filter="{name}"]')
            classes = popup.locator("#comments li").evaluate_all("els => els.map(e => e.className)")
            check(f"filtre {name}", all(c in (name, "empty") for c in classes), f"{len(classes)} lignes")
        popup.click('.chip[data-filter="all"]')

        popup.click("#copy")
        copied = popup.evaluate("navigator.clipboard.readText()")
        check("copie", "%" in copied and len(copied.splitlines()) > 3, f"{len(copied)} caractères")

        with popup.expect_download() as download:
            popup.click("#csv")
        check("export CSV", download.value.suggested_filename.endswith(".csv"))

        popup.evaluate("""() => {
          window.fetch = () => Promise.reject(new TypeError('network'));
        }""")
        popup.click("#analyze")
        popup.wait_for_selector("#status.error", timeout=120000)
        check("erreur réseau affichée", "joindre l'API" in popup.locator("#status").inner_text())
        popup.screenshot(path=str(SHOTS / "popup_error.png"))

        context.close()
    return 1 if check.failed else 0


if __name__ == "__main__":
    sys.exit(main())
