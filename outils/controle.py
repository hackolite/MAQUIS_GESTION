"""Contrôle de cohérence des fichiers Markdown du livre."""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIERS = ["chapitre-00-introduction.md"]
FICHIERS += [f"chapitre-{n:02d}.md" for n in range(1, 12)]
FICHIERS += ["annexes.md"]

INTERDITS = [
    r"chiffre d.affaires", r"\bcharges?\b", r"d[ée]pens", r"b[ée]n[ée]fice",
    r"\bmarges?\b", r"tr[ée]sorerie", r"fonds? de roulement", r"fonds? de caisse",
    r"\bpertes?\b", r"d[ée]marque", r"pr[ée]visionnel", r"amortiss", r"\bBFR\b",
    r"seuil de rentabilit", r"\bflux\b", r"\bratios?\b", r"invest", r"\bWave\b",
]


def phrases(texte):
    texte = re.sub(r"^\s*(>|\||[-*]|#+)\s*", "", texte, flags=re.M)
    texte = re.sub(r"[*_]", "", texte)
    for bloc in texte.split("\n"):
        for phrase in re.split(r"(?<=[.!?…])\s+", bloc):
            yield phrase


def controler(nom):
    chemin = os.path.join(RACINE, nom)
    if not os.path.exists(chemin):
        return [f"FICHIER MANQUANT : {nom}"], 0
    texte = open(chemin, encoding="utf-8").read()
    alertes = []
    mots = len(re.sub(r"[#>|*\-]", " ", texte).split())
    for motif in INTERDITS:
        for m in re.finditer(motif, texte, flags=re.I):
            debut = texte.rfind("\n", 0, m.start()) + 1
            fin = texte.find("\n", m.end())
            alertes.append(f"mot interdit « {m.group(0)} » : {texte[debut:fin][:120]}")
    if texte.count("\n# ") + texte.startswith("# ") != 1:
        alertes.append("nombre de titres # différent de 1")
    if "'" in texte:
        alertes.append("apostrophe droite restante")
    for p in phrases(texte):
        n = len(p.split())
        if n > 25:
            alertes.append(f"phrase de {n} mots : {p[:100]}…")
    est_chapitre = re.match(r"chapitre-(0[1-9]|1[01])\.md", nom)
    if est_chapitre:
        attendus = {
            "## Ce qui a changé pour Maman Akossiwa": 1,
            "## À toi de jouer": 1,
            "### Résumé": 1,
            "### Situations à analyser": 1,
            "### Exercices de calcul": 1,
            "> **RÉSUMÉ DU CHAPITRE**": 1,
            "> **EXERCICE DE MISE EN SITUATION 1**": 1,
            "> **EXERCICE DE MISE EN SITUATION 2**": 1,
            "> **EXERCICE DE MISE EN SITUATION 3**": 1,
            "> **EXERCICE DE CALCUL 1**": 1,
            "> **EXERCICE DE CALCUL 2**": 1,
            "> **EXERCICE DE CALCUL 3**": 1,
            "> **RÉPONSE**": 6,
            "Essaie d’abord seule, puis compare avec la réponse.": 3,
        }
        for cle, n in attendus.items():
            trouve = texte.count(cle)
            if trouve != n:
                alertes.append(f"structure : « {cle} » trouvé {trouve} fois, attendu {n}")
        outils = texte.count("> **BOÎTE À OUTILS MATHS**")
        if outils < 2:
            alertes.append(f"structure : {outils} boîte(s) à outils maths, au moins 2 attendues")
        if not 2500 <= mots <= 3500:
            alertes.append(f"longueur : {mots} mots (attendu 2 500 à 3 500)")
        # Encadrés collés : une ligne « > » suivie directement d'un autre titre d'encadré.
        if re.search(r"^>.*\n> \*\*(EXERCICE|RÉPONSE|BOÎTE|À RETENIR|ATTENTION)", texte, re.M):
            alertes.append("encadrés collés (fusion probable)")
    verifs = len(re.findall(r"\[À VÉRIFIER[^\]]*\]", texte))
    return alertes, (mots, verifs)


if __name__ == "__main__":
    total = 0
    for nom in FICHIERS:
        alertes, info = controler(nom)
        if info:
            total += info[0]
            print(f"== {nom} : {info[0]} mots, {info[1]} mention(s) [À VÉRIFIER]")
        else:
            print(f"== {nom}")
        for a in alertes:
            print("   -", a)
    print("TOTAL mots :", total)
