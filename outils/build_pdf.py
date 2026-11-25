"""Produit un PDF (A5) à partir de l'EPUB généré par build_epub.py."""
import os
import re
import zipfile

from weasyprint import CSS, HTML

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPUB = os.path.join(RACINE, "gerer-et-rentabiliser-son-bar-resto.epub")
SORTIE = os.path.join(RACINE, "gerer-et-rentabiliser-son-bar-resto.pdf")
COUVERTURE = os.path.join(RACINE, "outils", "couverture.jpg")

CSS_IMPRESSION = """
@page {
  size: A5;
  margin: 18mm 15mm 20mm 15mm;
  @bottom-center { content: counter(page); font-size: 9pt; }
}
@page couverture { margin: 0; @bottom-center { content: none; } }
@page liminaire { @bottom-center { content: none; } }

body { font-family: "Liberation Serif", serif; font-size: 10.5pt; margin: 0; }
.page-couverture { page: couverture; }
.page-couverture img { width: 148mm; height: 210mm; display: block; }
.liminaire { page: liminaire; }
.fichier { break-before: page; }
h1 { break-before: avoid; }
.encadre, table, tr { break-inside: avoid; }
nav a { text-decoration: none; color: inherit; }
nav a::after { content: leader('.') target-counter(attr(href), page); }
nav[hidden] { display: none; }
a { color: inherit; text-decoration: none; }
"""


def main():
    with zipfile.ZipFile(EPUB) as z:
        opf = z.read("OEBPS/content.opf").decode("utf-8")
        css_epub = z.read("OEBPS/style.css").decode("utf-8")
        ids = re.findall(r'<itemref idref="([^"]+)"', opf)
        hrefs = dict(re.findall(r'<item id="([^"]+)" href="([^"]+)"', opf))
        morceaux = []
        for ident in ids:
            fichier = hrefs[ident]
            if fichier == "couverture.xhtml":
                morceaux.append(
                    f'<div class="page-couverture"><img src="file://{COUVERTURE}" '
                    'alt="Couverture"/></div>'
                )
                continue
            source = z.read(f"OEBPS/{fichier}").decode("utf-8")
            corps = re.search(r"<body[^>]*>(.*)</body>", source, re.S).group(1)
            # Liens internes : « fichier.xhtml#id » -> « #id », « fichier.xhtml » -> ancre.
            corps = re.sub(r'href="[a-z0-9-]+\.xhtml#', 'href="#', corps)
            corps = re.sub(
                r'href="([a-z0-9-]+)\.xhtml"', r'href="#fichier-\1"', corps
            )
            classe = "fichier"
            if fichier in ("titre.xhtml", "copyright.xhtml", "avertissement.xhtml"):
                classe += " liminaire"
            nom = fichier[:-6]
            morceaux.append(f'<div class="{classe}" id="fichier-{nom}">{corps}</div>')

    document = (
        '<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>'
        "<title>Gérer et rentabiliser son bar-resto</title></head><body>"
        + "\n".join(morceaux)
        + "</body></html>"
    )
    HTML(string=document, base_url=RACINE).write_pdf(
        SORTIE, stylesheets=[CSS(string=css_epub), CSS(string=CSS_IMPRESSION)]
    )
    print("PDF écrit :", SORTIE)


if __name__ == "__main__":
    main()
