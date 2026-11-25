"""Applique la typographie française aux fichiers Markdown du livre."""
import re
import sys

NBSP = "\u00a0"


def typographie(texte: str) -> str:
    texte = texte.replace("'", "\u2019")
    # Espaces insécables dans les nombres (deux passes pour 1 000 000).
    for _ in range(2):
        texte = re.sub(r"(\d)[ \u202f](?=\d{3}\b)", r"\1" + NBSP, texte)
    texte = re.sub(r"(\d)[ \u202f](FCFA|%)", r"\1" + NBSP + r"\2", texte)
    texte = re.sub(r"[ \u00a0\u202f]*(?<=[ \u00a0\u202f])([:;!?])", NBSP + r"\1", texte)
    texte = re.sub(r"«[ \u00a0\u202f]*", "«" + NBSP, texte)
    texte = re.sub(r"[ \u00a0\u202f]*»", NBSP + "»", texte)
    texte = re.sub(r"n°[ \u202f]", "n°" + NBSP, texte)
    return texte


if __name__ == "__main__":
    for chemin in sys.argv[1:]:
        with open(chemin, encoding="utf-8") as f:
            contenu = f.read()
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(typographie(contenu))
        print("typographie :", chemin)
