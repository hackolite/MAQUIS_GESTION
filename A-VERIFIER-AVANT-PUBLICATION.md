# Points à vérifier avant la publication

## À compléter
- [x] **Noms des auteurs** : Florence Tchantague et Loïc Lauréote (liste `AUTEURS` dans `outils/build_epub.py`). Ils apparaissent sur la couverture, la page de titre, le copyright et dans les métadonnées.
- [ ] **À propos des auteurs** : remplacer les deux `[À COMPLÉTER]` (fonction `page_a_propos` dans `outils/build_epub.py`). Vérifier aussi que « je » dans l’introduction et le mot « autrice » du cahier des charges conviennent à deux auteurs.
- [ ] **Éditeur** : `[À COMPLÉTER]`, et ISBN (facultatif).
- [ ] **Couverture** : la couverture actuelle est **provisoire** (typographique, bleu et orange, 1600 × 2560, JPEG). Il faut la remplacer par une version professionnelle.

## Passages [À VÉRIFIER] (17 mentions)
- Introduction : 2 mentions. Elles expliquent seulement le principe de la mention, rien à vérifier.
- Chapitre 3 : 1 mention.
- Chapitre 6 : 3 mentions (règles d’hygiène).
- Chapitre 7 : 1 mention (frais d’argent mobile).
- Chapitre 8 : 1 mention (salaire minimum, déclaration des employées).
- Chapitre 9 : 1 mention (frais d’argent mobile).
- Chapitre 10 : 7 mentions (autorisations, impôts, taxes, microfinance).
- Chapitre 11 : 1 mention (autorisations pour un nouveau local).

## Chiffres à valider (aucun ne contredit le fil rouge)
- Les prix sont-ils réalistes aujourd’hui à Lomé ? Grande bière 650 / 1 000 FCFA, casier 7 800 FCFA, poulet 4 000 FCFA, congélateur 240 000 FCFA.
- Ch. 8 : paie d’Ama (15 000 FCFA par semaine) et de Séna (13 000 FCFA par semaine). Il faut les comparer au salaire minimum légal en vigueur.
- Ch. 9 : détail des crédits ajouté à la rédaction (Kodjo 18 000, Koffi 9 000, Abla 5 000, Edem 4 000, Mensah 6 000 = 42 000 FCFA).
- Ch. 11 : chiffres ajoutés à la rédaction. L’argent qui sort chaque semaine est fixé à 460 000 FCFA (500 000 − 460 000 = 40 000). Le congélateur ferait vendre 2 casiers de plus par semaine, et il serait remboursé en environ 30 semaines.
- Le prénom « Koffi » désigne un client qui doit de l’argent (ch. 9) et le voisin (ch. 11). C’est peut-être la même personne, à harmoniser si besoin.

## Relecture humaine
- [ ] Relire les 33 exercices de calcul et leurs réponses. Ils ont été recalculés automatiquement, avec 294 opérations contrôlées, mais une relecture humaine reste nécessaire.
- [ ] Relire le ton et le vocabulaire local avec une gérante togolaise.
- [ ] **Déclaration d’usage d’IA** sur la plateforme de vente (KDP, Google Play Livres, etc.).

## Longueur
- Le livre compte **32 249 mots**, texte seul. Les chapitres 2 (2 457 mots) et 8 (2 407 mots) sont un peu sous la cible de 2 500. Les autres chapitres sont entre 2 560 et 2 998 mots.

## PDF
- `gerer-et-rentabiliser-son-bar-resto.pdf` (A5, 209 pages) est généré depuis l’EPUB avec `python3 outils/build_pdf.py`. Il faut le relancer après chaque nouvel EPUB. Chaque partie (introduction, chapitres, annexes, à propos) commence en haut d’une page de droite. Des pages blanches sont donc ajoutées. « À toi de jouer » et chaque annexe commencent sur une nouvelle page.

## Couleurs
- Palette : titres et bordures en bleu (#1F5FA8) et orange (#D9661F). Dans l’EPUB, aucun fond n’est imposé et le mode nuit reste lisible. À tester sur une vraie liseuse en mode nuit. Dans le PDF, les encadrés ont un fond très clair.
