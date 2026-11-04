"""Génère reports/rapport_technique.pdf à partir de docs/RAPPORT.md.

    pip install markdown playwright && playwright install chromium
    python scripts/build_report.py
"""
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "RAPPORT.md"
OUTPUT = ROOT / "reports" / "rapport_technique.pdf"

CSS = """
@page { size: A4; margin: 22mm 20mm; }
body { font: 11pt/1.5 Georgia, 'Times New Roman', serif; color: #1b1b1b; }
.cover { height: 245mm; display: flex; flex-direction: column; justify-content: center; text-align: center; page-break-after: always; }
.cover h1 { font-size: 26pt; color: #1f3a68; border: 0; margin: 18mm 0 4mm; }
.cover .sub { font-size: 14pt; color: #1f3a68; margin-bottom: 30mm; }
h1, h2, h3 { font-family: Helvetica, Arial, sans-serif; color: #1f3a68; page-break-after: avoid; }
h2 { font-size: 15pt; margin-top: 9mm; border-bottom: 1px solid #c8d0e0; padding-bottom: 1mm; }
h3 { font-size: 12pt; }
table { width: 100%; border-collapse: collapse; margin: 4mm 0; font-size: 10pt; page-break-inside: avoid; }
th, td { border: 1px solid #c8d0e0; padding: 1.5mm 2.5mm; text-align: left; vertical-align: top; }
th { background: #eef1f8; }
img { display: block; max-width: 100%; max-height: 95mm; margin: 4mm auto; }
td img { max-height: 110mm; }
code { font: 9.5pt Menlo, Consolas, monospace; background: #f3f4f6; padding: 0 1mm; }
pre { background: #f3f4f6; padding: 3mm; font-size: 9pt; page-break-inside: avoid; white-space: pre-wrap; }
pre code { padding: 0; }
.todo { background: #fff3b0; }
"""


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    body = text.split("\n", 3)[3]  # Le titre et l'auteur passent en page de garde.
    html = markdown.markdown(body, extensions=["tables", "fenced_code"])
    html = html.replace("À COMPLÉTER", '<span class="todo">À COMPLÉTER</span>')
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
    <div class="cover">
      <div>Université Mohammed V de Rabat<br>École Nationale Supérieure d'Arts et Métiers</div>
      <h1>Analyse de sentiment des commentaires YouTube</h1>
      <div class="sub">Rapport technique : du développement au déploiement cloud</div>
      <div>Aymane ISSAMI<br>Filière INDIA, 2026/27<br>Encadrante : Prof. Maria Zemzami</div>
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
                footer_template='<div style="width:100%;text-align:center;font-size:9px"><span class="pageNumber"></span></div>',
                margin={"top": "22mm", "bottom": "22mm", "left": "20mm", "right": "20mm"},
            )
            browser.close()
    finally:
        temporary.unlink()
    print(OUTPUT)


if __name__ == "__main__":
    main()
