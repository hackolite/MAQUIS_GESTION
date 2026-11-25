"""Assemble les fichiers Markdown du livre en un EPUB 3 reflowable."""
import html
import os
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone

import markdown
from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "gerer-et-rentabiliser-son-bar-resto.epub")

TITRE = "Gérer et rentabiliser son bar-resto"
SOUS_TITRE = (
    "Le guide terrain pour gagner vraiment sa vie avec son bar-resto "
    "en Afrique de l’Ouest"
)
AUTEURS = ["Florence Tchantague", "Loïc Lauréote"]
AUTRICE = " et ".join(AUTEURS)
EDITEUR = "[À COMPLÉTER]"
ANNEE = "2026"
DESCRIPTION = (
    "Un guide pratique, chaleureux et sans jargon pour les femmes qui "
    "tiennent un bar-resto, une buvette ou un petit restaurant en Afrique "
    "de l’Ouest : séparer l’argent du bar et de la maison, tenir un cahier, "
    "compter le stock, fixer ses prix, gérer les employées, dire non au "
    "crédit et grandir pas à pas. Avec des exercices corrigés à chaque "
    "chapitre."
)
SUJETS = [
    "Restauration",
    "Gestion d’entreprise",
    "Entrepreneuriat féminin",
    "Afrique de l’Ouest",
    "Togo",
]
# Identifiant stable : le même livre garde le même identifiant à chaque build.
IDENTIFIANT = "urn:uuid:" + str(
    uuid.uuid5(uuid.NAMESPACE_URL, "gerer-et-rentabiliser-son-bar-resto")
)

SOURCES = [("introduction", "chapitre-00-introduction.md")]
SOURCES += [(f"chapitre-{n:02d}", f"chapitre-{n:02d}.md") for n in range(1, 12)]
SOURCES += [("annexes", "annexes.md")]

CLASSES_ENCADRES = [
    ("BOÎTE À OUTILS MATHS", "outils"),
    ("À RETENIR", "retenir"),
    ("ATTENTION", "attention"),
    ("RÉSUMÉ DU CHAPITRE", "resume"),
    ("EXERCICE", "exercice"),
    ("RÉPONSE", "reponse"),
]

CSS = """@charset "UTF-8";

/* Palette : orange (#D9661F) et bleu (#1F5FA8), assez soutenus pour
   rester lisibles sur fond blanc comme en mode nuit. Aucun fond imposé. */

body {
  margin: 0 0.5em;
  line-height: 1.5;
}

p {
  margin: 0 0 0.9em 0;
  text-indent: 0;
}

h1 {
  page-break-before: always;
  break-before: page;
  font-size: 1.6em;
  line-height: 1.25;
  margin: 0 0 1em 0;
  padding-bottom: 0.3em;
  border-bottom: 3px solid #D9661F;
  color: #1F5FA8;
}

h2.nouvelle-page {
  page-break-before: always;
  break-before: page;
}

h2 {
  font-size: 1.3em;
  line-height: 1.3;
  margin: 1.6em 0 0.6em 0;
  color: #D9661F;
  page-break-after: avoid;
  break-after: avoid;
}

h3 {
  font-size: 1.1em;
  line-height: 1.3;
  margin: 1.3em 0 0.5em 0;
  color: #1F5FA8;
  page-break-after: avoid;
  break-after: avoid;
}

ul, ol {
  margin: 0 0 0.9em 0;
  padding-left: 1.4em;
}

li {
  margin-bottom: 0.3em;
}

.encadre {
  margin: 1.2em 0;
  padding: 0.3em 0 0.3em 0.9em;
  border-left: 4px solid #1F5FA8;
}

.encadre > p:first-child {
  font-weight: bold;
  color: #1F5FA8;
}

.encadre.outils {
  border-left: 4px solid #1F5FA8;
}

.encadre.retenir,
.encadre.attention,
.encadre.resume {
  border-left: 4px solid #D9661F;
}

.encadre.retenir > p:first-child,
.encadre.attention > p:first-child,
.encadre.resume > p:first-child {
  color: #D9661F;
}

.encadre.exercice {
  border-left: 4px solid #D9661F;
}

.encadre.exercice > p:first-child {
  color: #D9661F;
}

.encadre.reponse {
  border-left: 4px dotted #1F5FA8;
  margin-left: 1.2em;
}

.essaie {
  font-style: italic;
  margin-left: 0.6em;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 1em 0;
  table-layout: fixed;
}

th, td {
  border: 1px solid #1F5FA8;
  padding: 0.3em;
  text-align: left;
  vertical-align: top;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

th {
  font-weight: bold;
  color: #1F5FA8;
  border-bottom: 2px solid #D9661F;
}

img {
  max-width: 100%;
  height: auto;
}

.couverture {
  margin: 0;
  padding: 0;
  text-align: center;
}

.page-titre {
  text-align: center;
  margin-top: 3em;
}

.page-titre .titre {
  font-size: 1.8em;
  font-weight: bold;
  line-height: 1.25;
  border-bottom: none;
}

.page-titre .sous-titre {
  font-size: 1.15em;
  font-style: italic;
  margin-top: 1em;
  color: #D9661F;
}

.page-titre .autrice {
  font-size: 1.2em;
  margin-top: 0.4em;
}

.page-titre .sous-titre + .autrice {
  margin-top: 3em;
}

nav ol {
  list-style-type: none;
  padding-left: 1em;
}

nav > ol {
  padding-left: 0;
}
"""


def xhtml(titre: str, corps: str, type_epub: str = "") -> str:
    attribut = f' epub:type="{type_epub}"' if type_epub else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="fr" lang="fr">\n'
        "<head>\n"
        '<meta charset="UTF-8"/>\n'
        f"<title>{html.escape(titre)}</title>\n"
        '<link rel="stylesheet" type="text/css" href="style.css"/>\n'
        "</head>\n"
        f"<body{attribut}>\n{corps}\n</body>\n</html>\n"
    )


def texte_brut(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def classe_encadre(contenu: str) -> str:
    premier = re.search(r"<strong>(.*?)</strong>", contenu, re.S)
    titre = texte_brut(premier.group(1)) if premier else ""
    for prefixe, classe in CLASSES_ENCADRES:
        if titre.upper().startswith(prefixe):
            return classe
    return "citation"


def convertir(md_texte: str, prefixe_id: str):
    """Convertit le Markdown en XHTML et renvoie (titre, corps, titres)."""
    def md(texte):
        return markdown.markdown(
            texte, extensions=["tables", "sane_lists"], output_format="xhtml"
        )

    # Encadrés : chaque bloc de lignes « > » (terminé par une ligne vide) est
    # converti à part. Sinon Python-Markdown fusionne deux encadrés voisins.
    lignes_sortie, encadres, bloc = [], [], []

    def fermer_bloc():
        if bloc:
            interieur = "\n".join(re.sub(r"^> ?", "", l) for l in bloc)
            contenu = md(interieur)
            encadres.append(
                f'<div class="encadre {classe_encadre(contenu)}">\n{contenu}\n</div>'
            )
            lignes_sortie.extend(["", f"ENCADRE{len(encadres) - 1}FIN", ""])
            bloc.clear()

    for ligne in md_texte.split("\n"):
        if ligne.startswith(">"):
            bloc.append(ligne)
        else:
            fermer_bloc()
            lignes_sortie.append(ligne)
    fermer_bloc()

    corps = md("\n".join(lignes_sortie))
    for i, html_encadre in enumerate(encadres):
        corps = corps.replace(f"<p>ENCADRE{i}FIN</p>", html_encadre, 1)
    if re.search(r"ENCADRE\d+FIN", corps):
        raise SystemExit(f"{prefixe_id} : encadré non remplacé")
    corps = corps.replace(
        "<p>Essaie d’abord seule, puis compare avec la réponse.</p>",
        '<p class="essaie">Essaie d’abord seule, puis compare avec la réponse.</p>',
    )

    titres = []
    compteur = {"n": 0}

    def remplacer_titre(m):
        niveau, contenu = m.group(1), m.group(2)
        compteur["n"] += 1
        ident = f"{prefixe_id}-t{compteur['n']}"
        texte = texte_brut(contenu)
        titres.append((int(niveau), ident, texte))
        classe = ""
        if niveau == "2" and (
            texte.startswith("À toi de jouer") or texte.startswith("Annexe ")
        ):
            classe = ' class="nouvelle-page"'
        return f'<h{niveau} id="{ident}"{classe}>{contenu}</h{niveau}>'

    corps = re.sub(r"<h([1-3])>(.*?)</h\1>", remplacer_titre, corps, flags=re.S)
    h1 = [t for t in titres if t[0] == 1]
    if len(h1) != 1:
        raise SystemExit(f"{prefixe_id} : {len(h1)} titres h1 (un seul attendu)")
    return h1[0][2], corps, titres


def creer_couverture(chemin: str) -> None:
    largeur, hauteur = 1600, 2560
    image = Image.new("RGB", (largeur, hauteur), (22, 58, 102))
    dessin = ImageDraw.Draw(image)
    dossier = "/usr/share/fonts/truetype/liberation/"
    gras = ImageFont.truetype(dossier + "LiberationSerif-Bold.ttf", 150)
    italique = ImageFont.truetype(dossier + "LiberationSerif-Italic.ttf", 70)
    normal = ImageFont.truetype(dossier + "LiberationSans-Regular.ttf", 80)
    creme = (250, 238, 214)
    ocre = (240, 140, 40)

    def centrer(lignes, police, y, couleur, interligne):
        for ligne in lignes:
            boite = dessin.textbbox((0, 0), ligne, font=police)
            x = (largeur - (boite[2] - boite[0])) // 2
            dessin.text((x, y), ligne, font=police, fill=couleur)
            y += interligne
        return y

    dessin.rectangle([80, 80, largeur - 80, hauteur - 80], outline=ocre, width=8)
    y = centrer(["Gérer et", "rentabiliser", "son bar-resto"], gras, 520, creme, 190)
    dessin.rectangle([largeur // 2 - 220, y + 60, largeur // 2 + 220, y + 72], fill=ocre)
    lignes_st = [
        "Le guide terrain pour gagner",
        "vraiment sa vie avec son",
        "bar-resto en Afrique de l’Ouest",
    ]
    centrer(lignes_st, italique, y + 180, creme, 100)
    centrer(AUTEURS, normal, hauteur - 500, ocre, 110)
    image.save(chemin, "JPEG", quality=90)


def page_copyright() -> str:
    corps = (
        '<section epub:type="copyright-page">\n'
        "<h1>Droits d’auteur</h1>\n"
        f"<p>{TITRE}</p>\n"
        f"<p>{SOUS_TITRE}</p>\n"
        f"<p>© {ANNEE} {AUTRICE}. Tous droits réservés.</p>\n"
        f"<p>Première édition, {ANNEE}.</p>\n"
        f"<p>Éditeur : {EDITEUR}</p>\n"
        "<p>[ISBN : facultatif]</p>\n"
        "</section>"
    )
    return xhtml("Droits d’auteur", corps)


def page_avertissement() -> str:
    corps = (
        "<section>\n"
        "<h1>Avertissement</h1>\n"
        "<p>Le personnage de Maman Akossiwa est fictif. Son bar-resto, "
        "ses employées et sa famille sont inventés pour rendre les conseils "
        "plus faciles à suivre.</p>\n"
        "<p>Les prix et les chiffres de ce livre sont des exemples. "
        "Adapte-les avec tes vrais prix.</p>\n"
        "<p>Ce livre ne remplace pas un conseil comptable, juridique ou "
        "fiscal.</p>\n"
        "<p>Les règles sur les autorisations, les impôts et l’hygiène "
        "changent selon les pays et les communes. Vérifie toujours auprès "
        "des autorités compétentes.</p>\n"
        "</section>"
    )
    return xhtml("Avertissement", corps)


def page_titre() -> str:
    corps = (
        '<section class="page-titre" epub:type="titlepage">\n'
        f'<h1 class="titre">{TITRE}</h1>\n'
        f'<p class="sous-titre">{SOUS_TITRE}</p>\n'
        + "".join(f'<p class="autrice">{a}</p>\n' for a in AUTEURS)
        + "</section>"
    )
    return xhtml(TITRE, corps)


def page_a_propos() -> str:
    corps = (
        "<section>\n"
        "<h1>À propos des auteurs</h1>\n"
        + "".join(
            f"<p><strong>{a}</strong></p>\n<p>[À COMPLÉTER]</p>\n" for a in AUTEURS
        )
        + "</section>"
    )
    return xhtml("À propos des auteurs", corps)


def page_couverture() -> str:
    corps = (
        '<section class="couverture" epub:type="cover">\n'
        f'<img src="images/couverture.jpg" alt="Couverture : {TITRE}"/>\n'
        "</section>"
    )
    return xhtml("Couverture", corps)


def construire_toc(entrees):
    """entrees : liste (fichier, titre, sous-entrées[(fichier#id, titre, enfants)])."""

    def li_nav(href, titre, enfants):
        sous = ""
        if enfants:
            sous = "<ol>" + "".join(li_nav(*e) for e in enfants) + "</ol>"
        return f'<li><a href="{href}">{html.escape(titre)}</a>{sous}</li>'

    liste = "".join(li_nav(*e) for e in entrees)
    nav = xhtml(
        "Table des matières",
        '<nav epub:type="toc" id="toc">\n<h1>Table des matières</h1>\n'
        f"<ol>{liste}</ol>\n</nav>\n"
        '<nav epub:type="landmarks" hidden="">\n<ol>'
        '<li><a epub:type="cover" href="couverture.xhtml">Couverture</a></li>'
        '<li><a epub:type="toc" href="nav.xhtml">Table des matières</a></li>'
        '<li><a epub:type="bodymatter" href="introduction.xhtml">Début</a></li>'
        "</ol>\n</nav>",
    )

    ordre = {"n": 0}

    def point_ncx(href, titre, enfants):
        ordre["n"] += 1
        n = ordre["n"]
        sous = "".join(point_ncx(*e) for e in enfants)
        return (
            f'<navPoint id="np{n}" playOrder="{n}"><navLabel><text>'
            f"{html.escape(titre)}</text></navLabel>"
            f'<content src="{href}"/>{sous}</navPoint>'
        )

    points = "".join(point_ncx(*e) for e in entrees)
    ncx = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" '
        'xml:lang="fr">\n<head>\n'
        f'<meta name="dtb:uid" content="{IDENTIFIANT}"/>\n'
        '<meta name="dtb:depth" content="3"/>\n'
        '<meta name="dtb:totalPageCount" content="0"/>\n'
        '<meta name="dtb:maxPageNumber" content="0"/>\n</head>\n'
        f"<docTitle><text>{html.escape(TITRE)}</text></docTitle>\n"
        f"<docAuthor><text>{html.escape(AUTRICE)}</text></docAuthor>\n"
        f"<navMap>{points}</navMap>\n</ncx>\n"
    )
    return nav, ncx


def entree_toc(fichier, titres):
    """Chapitre -> h1 ; « À toi de jouer » (h2) et ses h3 ; annexes (h2)."""
    h1 = next(t for t in titres if t[0] == 1)
    enfants = []
    jouer = None
    for niveau, ident, texte in titres:
        if niveau == 2:
            jouer = None
            if texte.startswith("À toi de jouer"):
                jouer = (f"{fichier}#{ident}", texte, [])
                enfants.append(jouer)
            elif fichier == "annexes.xhtml":
                enfants.append((f"{fichier}#{ident}", texte, []))
        elif niveau == 3 and jouer is not None:
            jouer[2].append((f"{fichier}#{ident}", texte, []))
    return (fichier, h1[2], enfants)


def main():
    fichiers = {}  # nom -> contenu
    spine = []
    entrees = []

    fichiers["couverture.xhtml"] = page_couverture()
    fichiers["titre.xhtml"] = page_titre()
    fichiers["copyright.xhtml"] = page_copyright()
    fichiers["avertissement.xhtml"] = page_avertissement()
    spine += ["couverture.xhtml", "titre.xhtml", "copyright.xhtml",
              "avertissement.xhtml", "nav.xhtml"]
    entrees += [
        ("titre.xhtml", "Page de titre", []),
        ("copyright.xhtml", "Droits d’auteur", []),
        ("avertissement.xhtml", "Avertissement", []),
    ]

    for nom, source in SOURCES:
        with open(os.path.join(RACINE, source), encoding="utf-8") as f:
            md_texte = f.read()
        titre, corps, titres = convertir(md_texte, nom)
        fichier = f"{nom}.xhtml"
        fichiers[fichier] = xhtml(titre, f"<section>\n{corps}\n</section>")
        spine.append(fichier)
        entrees.append(entree_toc(fichier, titres))

    fichiers["a-propos.xhtml"] = page_a_propos()
    spine.append("a-propos.xhtml")
    entrees.append(("a-propos.xhtml", "À propos des auteurs", []))

    nav, ncx = construire_toc(entrees)
    fichiers["nav.xhtml"] = nav
    fichiers["toc.ncx"] = ncx
    fichiers["style.css"] = CSS

    couverture = os.path.join(RACINE, "outils", "couverture.jpg")
    creer_couverture(couverture)

    modifie = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = ['<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
             '<item id="css" href="style.css" media-type="text/css"/>',
             '<item id="couverture-img" href="images/couverture.jpg" '
             'media-type="image/jpeg" properties="cover-image"/>']
    for nom in fichiers:
        if nom.endswith(".xhtml"):
            ident = "x-" + nom[:-6]
            props = ' properties="nav"' if nom == "nav.xhtml" else ""
            items.append(f'<item id="{ident}" href="{nom}" '
                         f'media-type="application/xhtml+xml"{props}/>')
    itemrefs = "".join(
        f'<itemref idref="x-{n[:-6]}"'
        + (' linear="yes"' if n != "couverture.xhtml" else "")
        + "/>"
        for n in spine
    )
    sujets = "".join(f"<dc:subject>{html.escape(s)}</dc:subject>\n" for s in SUJETS)
    opf = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="bookid" xml:lang="fr">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'<dc:identifier id="bookid">{IDENTIFIANT}</dc:identifier>\n'
        f'<dc:title id="titre">{html.escape(TITRE)}</dc:title>\n'
        '<meta refines="#titre" property="title-type">main</meta>\n'
        f'<dc:title id="soustitre">{html.escape(SOUS_TITRE)}</dc:title>\n'
        '<meta refines="#soustitre" property="title-type">subtitle</meta>\n'
        + "".join(
            f'<dc:creator id="auteur{i}">{html.escape(a)}</dc:creator>\n'
            f'<meta refines="#auteur{i}" property="role" scheme="marc:relators">aut</meta>\n'
            for i, a in enumerate(AUTEURS, 1)
        )
        + "<dc:language>fr</dc:language>\n"
        f"<dc:publisher>{html.escape(EDITEUR)}</dc:publisher>\n"
        f"<dc:date>{ANNEE}</dc:date>\n"
        f"<dc:description>{html.escape(DESCRIPTION)}</dc:description>\n"
        f"{sujets}"
        f"<dc:rights>© {ANNEE} {html.escape(AUTRICE)}. Tous droits réservés.</dc:rights>\n"
        f'<meta property="dcterms:modified">{modifie}</meta>\n'
        '<meta name="cover" content="couverture-img"/>\n'
        "</metadata>\n<manifest>\n" + "\n".join(items) + "\n</manifest>\n"
        f'<spine toc="ncx">{itemrefs}</spine>\n'
        '<guide><reference type="cover" title="Couverture" href="couverture.xhtml"/>'
        '<reference type="toc" title="Table des matières" href="nav.xhtml"/>'
        '<reference type="text" title="Début" href="introduction.xhtml"/></guide>\n'
        "</package>\n"
    )
    container = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/></rootfiles>\n</container>\n'
    )

    if os.path.exists(SORTIE):
        os.remove(SORTIE)
    with zipfile.ZipFile(SORTIE, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        for nom, contenu in fichiers.items():
            z.writestr(f"OEBPS/{nom}", contenu, zipfile.ZIP_DEFLATED)
        z.write(couverture, "OEBPS/images/couverture.jpg", zipfile.ZIP_STORED)
    print("EPUB écrit :", SORTIE)


if __name__ == "__main__":
    sys.exit(main())
