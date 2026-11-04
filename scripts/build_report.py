"""Génère reports/rapport_technique.pdf à partir de docs/RAPPORT.md.

    pip install markdown playwright && playwright install chromium
    python scripts/build_report.py
"""
import re
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "RAPPORT.md"
OUTPUT = ROOT / "reports" / "rapport_technique.pdf"

FONTS = "../src/api/static/fonts"
BG = "#FFFFFF"
CSS = f"""
@font-face {{ font-family: Anton; src: url({FONTS}/anton-latin-400-normal.woff2); }}
@font-face {{ font-family: Outfit; font-weight: 400; src: url({FONTS}/outfit-latin-400-normal.woff2); }}
@font-face {{ font-family: Outfit; font-weight: 600; src: url({FONTS}/outfit-latin-600-normal.woff2); }}
@font-face {{ font-family: "JetBrains Mono"; font-weight: 400; src: url({FONTS}/jetbrains-mono-latin-400-normal.woff2); }}
@font-face {{ font-family: "JetBrains Mono"; font-weight: 600; src: url({FONTS}/jetbrains-mono-latin-600-normal.woff2); }}
@page {{ size: A4; margin: 20mm 20mm 18mm; }}
html, body {{ background: {BG}; }}
body {{ margin: 0; color: #120D02; font: 400 10.5pt/1.5 Outfit, sans-serif; }}
strong {{ font-weight: 600; }}
.cover {{ height: 250mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always; }}
.cover .label {{ color: #8A6508; font: 400 10pt "JetBrains Mono", monospace; letter-spacing: .14em; text-transform: uppercase; }}
.cover h1 {{ margin: 4mm 0; font: 400 46pt/1.12 Anton, sans-serif; letter-spacing: .02em; text-transform: uppercase; color: #120D02; }}
.cover .sub {{ color: #8A6508; font-size: 14pt; margin-bottom: 18mm; }}
.cover .meta {{ padding-top: 5mm; border-top: 1px solid #D6C9BF; color: #5C5048; line-height: 1.7; }}
.cover .meta b {{ color: #120D02; font-weight: 600; }}
h2, h3 {{ font-family: Anton, sans-serif; font-weight: 400; letter-spacing: .02em; text-transform: uppercase; color: #120D02; page-break-after: avoid; }}
h2 {{ font-size: 20pt; margin: 9mm 0 3mm; padding-top: 5mm; border-top: 1px solid #E8E2DC; }}
h3 {{ font-size: 13pt; margin: 6mm 0 2mm; }}
p {{ margin: 0 0 2.5mm; }}
ul, ol {{ margin: 0 0 3mm; padding-left: 6mm; }}
li {{ margin-bottom: 1mm; }}
li::marker {{ color: #8A6508; }}
table {{ width: 100%; border-collapse: collapse; margin: 3mm 0 5mm; font-size: 9.5pt; page-break-inside: avoid; }}
th, td {{ border-bottom: 1px solid #E8E2DC; padding: 1.7mm 3mm 1.7mm 0; text-align: left; vertical-align: top; }}
th {{ border-color: #D6C9BF; color: #5C5048; font: 400 8pt "JetBrains Mono", monospace; letter-spacing: .08em; text-transform: uppercase; }}
img, svg {{ display: block; max-width: 100%; max-height: 82mm; margin: 3mm auto; }}
td img {{ max-height: 100mm; margin: 0 auto; }}
code {{ font: 8.8pt "JetBrains Mono", monospace; color: #6B4F06; }}
pre {{ background: #F7F5F2; border: 1px solid #E8E2DC; padding: 3mm; page-break-inside: avoid; white-space: pre-wrap; }}
pre code {{ color: #120D02; }}
.todo {{ background: #F7C340; color: #120D02; font-weight: 600; padding: 0 1mm; }}
"""


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    body = text.split("\n", 3)[3]  # Le titre et l'auteur passent en page de garde.
    html = markdown.markdown(body, extensions=["tables", "fenced_code"])
    html = html.replace("À COMPLÉTER", '<span class="todo">À COMPLÉTER</span>')
    # SVG intégré dans la page : il hérite ainsi des polices du rapport.
    svg = (SOURCE.parent / "architecture.svg").read_text(encoding="utf-8")
    html = re.sub(r'<img[^>]*src="architecture\.svg"[^>]*/?>', lambda _: svg, html)
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
    <div class="cover">
      <div class="label">TP3 // Cloud Computing</div>
      <h1>Analyse de sentiment YouTube</h1>
      <div class="sub">Rapport technique : du modèle à l'extension Chrome</div>
      <div class="meta"><b>Aymane ISSAMI</b><br>Filière INDIA, année 2026/27<br>Encadrante : Prof. Maria Zemzami<br>
      École Nationale Supérieure d'Arts et Métiers, Université Mohammed V de Rabat</div>
    </div>{html}</body></html>"""
    temporary = SOURCE.with_name(".rapport.html")
    temporary.write_text(page, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            tab = browser.new_page()
            tab.goto(temporary.as_uri(), wait_until="networkidle")
            OUTPUT.parent.mkdir(exist_ok=True)
            tab.pdf(
                path=str(OUTPUT), format="A4", print_background=True, display_header_footer=True,
                header_template="<span></span>",
                footer_template='<div style="width:100%;padding:0 20mm;text-align:right;font:8px monospace;color:#5C5048"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                prefer_css_page_size=True,
            )
            browser.close()
    finally:
        temporary.unlink()
    print(OUTPUT)


if __name__ == "__main__":
    main()
