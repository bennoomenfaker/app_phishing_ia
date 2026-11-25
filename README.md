# Sécurité — Phishing IA — application Streamlit

Mini-projet 3 — ISCAE Master VIC. Prototype pédagogique d'aide à la décision.
Données synthétiques, aucune donnée personnelle. Décision humaine obligatoire.

## Fichier à utiliser (version finale)

- **Notebook de référence** : `notebook_ML_IA_confiance_numerique.ipynb` — il reste le notebook principal. Protocole conservé : split **80/20 stratifié**, entraînement et réglages sur le train, **validation croisée 5×5 répétée**, choix du modèle sur le train, puis évaluation **une seule fois** sur le test. Ajout : matrice de confusion **OOF** (train) en plus de la matrice test, avec explication OOF/FN/FP.
- **Application de référence** : `app.py` — verdict binaire clair **Malveillant / Non malveillant**. La probabilité et la zone de triage (0,20 / 0,88) sont des informations secondaires, jamais une troisième classe.
- **Dossier `work/` supprimé** : il ne contenait qu'une démo redondante (validation croisée imbriquée sur 520 lignes, sans test indépendant). L'essentiel — matrice OOF et explication FN/FP — est intégré au notebook principal et à `app.py`.

`OOF` = *out-of-fold* (« hors pli ») : chaque ligne est prédite par un modèle qui ne l'a pas vue à l'entraînement. Au seuil 0,21, la matrice OOF du train est **TN 182 · FP 117 · FN 3 · TP 114** ; la matrice test finale est **TN 47 · FP 28 · FN 1 · TP 28**. `FN = 0` et `FP = 0` simultanément demanderaient une séparation parfaite (AUC = 1), ce qui n'est pas le cas ici (AUC ≈ 0,91).

## Lancer l'application

⚠️ Le dossier du projet contient un `:` dans son chemin
(`Mini-projet 3: Veille stratégique…`). `python -m venv .venv` **échoue** dans ce cas
(`Refusing to create a venv … because it contains the PATH separator :`).
Créez l'environnement **en dehors** du dossier :

```bash
# 1. environnement isolé, hors du chemin avec ":"
uv venv ~/.venvs/vic-phishing --python 3.12
#    (sans uv : python3 -m venv ~/.venvs/vic-phishing)

# 2. dépendances
uv pip install --python ~/.venvs/vic-phishing/bin/python -r requirements.txt
#    (ou : ~/.venvs/vic-phishing/bin/pip install -r requirements.txt)

# 3. lancer depuis le dossier du projet
cd "app_phishing_ia"
~/.venvs/vic-phishing/bin/streamlit run app.py
```

L'application s'ouvre sur <http://localhost:8501>.

### Vérification hors-ligne (sans installer de dépendance)

```bash
python3 -m py_compile app.py
python3 - <<'PY'
import json
from pathlib import Path
for f in ["model_meta.json", "notebook_ML_IA_confiance_numerique.ipynb"]:
    json.loads(Path(f).read_text(encoding="utf-8"))
    print("JSON OK :", f)
PY
```

Ces contrôles valident la syntaxe de `app.py` et l'intégrité des artefacts JSON. Le rendu Streamlit
n'est pas testé ici : `streamlit` n'est pas installé dans l'environnement de vérification.

Si toutes les dépendances sont déjà installées pour l'utilisateur courant,
`python3 -m streamlit run app.py` suffit.

## Pages de l'application

Navigation en douze entrées : les cinq pages historiques sont conservées et sept vues nouvelles
couvrent l'intégralité du pipeline.

| Page | Contenu |
|---|---|
| 1. Accueil / Vue d'ensemble | contexte général, problématique, objectif de pré-dépistage, questions de recherche, erreur la plus coûteuse |
| 2. Exploration des données (EDA) | KPI de nettoyage, aperçu du CSV, distribution de la cible, histogrammes par classe, heatmap **identique au notebook** + corrélations train |
| 3. Analyse des corrélations | heatmap exacte de l'ipynb (cellule 31, train seul, 416 messages), classement train seul commenté, limites de Pearson et de la causalité |
| 4. Processus Machine Learning | schéma et 12 étapes du dataset au déploiement, détail des 5 plis × 5 répétitions |
| 5. Comparaison des modèles | tableau des scores réellement calculés, graphiques F1 / AUC / AP, justification du choix |
| 6. Évaluation et métriques | matrices OOF et test annotées, métriques du pipeline sauvegardé, courbe de coût selon le seuil |
| 7. Prédiction d'un message | 3 scénarios synchronisés, formulaire à 9 champs, verdict binaire, probabilité, décomposition réelle et zone de triage secondaire |
| 8. Explication des attributs | dictionnaire des variables, définition / échelle / rôle, moyennes et corrélations calculées à l'ouverture |
| 9. À propos / Limites | nature synthétique des données, périmètre d'aide à la décision, traçabilité des artefacts |
| 10. Guide de présentation | processus ML, AUC / AP / OOF, coût `5·FN + FP`, matrices, points clés de soutenance |
| 11. 🎓 Mode présentation académique | 14 étapes navigables, pensées pour une projection en soutenance |
| 12. 🎓 Comprendre le Machine Learning | apprentissage, vrais coefficients, sigmoïde et `P(Oui)`, seuil, OOF, test final et lien avec le formulaire |

Les matrices OOF et test sont présentées en **tableaux annotés** dans la page 6, avec le décompte
`TN / FP / FN / TP` et le coût métier. Les graphiques de la page 2 (cible, histogrammes, corrélation)
sont recalculés à l'ouverture depuis le CSV — aucune valeur n'est saisie à la main. Le mode
présentation (page 11) ne réentraîne rien : il lit les artefacts et le pipeline sauvegardé.
Le module pédagogique (page 12) affiche les coefficients réels de `model.joblib`, recalcule
`P(Oui)` étape par étape (`details_probabilite()`) et vérifie l'égalité avec `predict_proba()`.
Le détail est dans `docs/10_probability_and_learning.md`.

## Explication des variables

Chaque attribut est expliqué dans l'application (page 4, **Explication des attributs**),
dans le notebook (cellule **Dictionnaire détaillé des attributs**) et dans le tableau ci-dessous.

| Variable | Définition | Lecture phishing | Rôle dans le modèle |
|---|---|---|---|
| `domaine_age_jours` | Âge du domaine expéditeur en jours (1–5 874 ; 10 NA imputés par la médiane) | Un domaine récent est très suspect (339 j en moyenne pour `Oui` contre 897 j pour `Non`). | **Conservée**, en `log1p` : variable la plus discriminante. |
| `urgence_score` | Pression temporelle de 0 à 10 | L'urgence empêche la victime de vérifier (5,54 pour `Oui` contre 4,11 pour `Non`). | **Conservée** + interaction `urgence × inconnu`. |
| `nb_liens` | Nombre de liens (0–5) | Chaque lien est une redirection potentielle (1,86 contre 1,20). | **Conservée** + interaction `liens × inconnu`. |
| `expediteur_connu` | 0/1 : adresse déjà connue | Les malveillants viennent plus souvent d'un inconnu (25 % de `1` contre 51 %). | **Conservée**. |
| `piece_jointe` | 0/1 : pièce jointe présente | Vecteur d'infection classique, mais courant aussi en légitime (30 % contre 21 %). | **Conservée**, importance modérée. |
| `personnalisation_score` | Degré d'adaptation du message au destinataire (0–10) | Le *spear phishing* personnalise pour gagner la confiance (5,40 contre 4,82 ; r ≈ +0,10). | **Conservée** : un message personnalisé n'est pas forcément malveillant. |
| `longueur_message` | Nombre de caractères (60–896) | Les malveillants sont ici légèrement plus courts (≈ 395 contre ≈ 421). | **Retirée** (bruit). |
| `heure_envoi` | Heure d'envoi (0–23) | Un envoi nocturne peut trahir une automatisation, signal faible. | **Retirée** (importance quasi nulle). |
| `fautes_langue` | Nombre de fautes (0–6) | L'IA écrit sans faute : 1,95 (`Oui`) contre 2,05 (`Non`), aucune séparation. | **Retirée** (bruit). |
| `date` | Date de réception | Variable calendaire sans justification métier. | **Exclue**. |
| `message_malveillant` | Cible `Non` / `Oui` | 374 `Non`, 146 `Oui`. | **Jamais** utilisée comme variable explicative. |

**Exemple pour `personnalisation_score`**

> Générique (score faible) : « Cher client, votre compte nécessite une vérification. Cliquez ici. »

> Personnalisé (score plus élevé) : « Bonjour Faker, votre compte bancaire associé à votre adresse e-mail nécessite une vérification. »

Le score illustre la personnalisation, pas la malveillance : les banques personnalisent aussi.
Ce qui départage, c'est la combinaison avec l'âge du domaine, l'urgence et l'expéditeur inconnu.

| Score | Interprétation |
|---|---|
| 0–2 | Très peu personnalisé |
| 3–4 | Faiblement personnalisé |
| 5–7 | Moyennement personnalisé |
| 8–10 | Fortement personnalisé |

Bornes **illustratives** : l'échelle réelle du fichier a été vérifiée dans le code (minimum 0,
maximum 10, moyenne 4,98, médiane 5). Messages normaux : moyenne **4,82** ; messages malveillants :
moyenne **5,40** ; corrélation avec la cible **r ≈ +0,10**.

## Générer la présentation PowerPoint et le Markdown du notebook

Les deux commandes se lancent depuis le dossier du projet, sans réseau.

```bash
# 1. (Legacy) Présentation PowerPoint 20 diapositives, ancien générateur
python3 scripts/make_pptx.py
# → Presentation_Projet_Phishing_IA.pptx  (noms d'images issus d'anciennes cellules)

# 2. Plan de la présentation 15 diapositives (valeurs + images à insérer)
#    → docs/11_plan_pptx_15_diapos.md  (référence actuelle)

# 3. Notebook → Markdown (texte + images des sorties)
python3 -m nbconvert --to markdown notebook_ML_IA_confiance_numerique.ipynb
# → notebook_ML_IA_confiance_numerique.md
# → notebook_ML_IA_confiance_numerique_files/  (images extraites)
```

Dépendances : `python-pptx` et `pillow` pour le PPTX ; `nbconvert` pour le Markdown (voir
`requirements.txt`). Le script PPTX lit les images déjà extraites dans `artefacts/pptx/` :
si le notebook est réexécuté et que les figures changent, réextraire les images avant de relancer
le script. Pour réexécuter le notebook avant conversion :

```bash
python3 -m nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 notebook_ML_IA_confiance_numerique.ipynb
```

## Créer la présentation avec Copilot (GPT-5 Thinking, compte étudiant)

### Pourquoi passer par le Markdown

Copilot (Word / PowerPoint, compte étudiant) **ne lit pas les fichiers `.ipynb`**. Il lit très bien
le Markdown, le texte et le JSON. Le dossier fournit donc déjà la version texte du notebook :

| Fichier à joindre à Copilot | Ce qu'il contient | Indispensable ? |
|---|---|---|
| `notebook_ML_IA_confiance_numerique.md` | **tout le notebook en texte** : explications, code, sorties, tableaux | oui |
| `README.md` | consignes, pages de l'app, protocole, tableau FN/FP | oui |
| `model_meta.json` | seuils appris (0,21 / 0,20 / 0,88), métriques, triage | oui |
| `artefacts/seuil_phishing_ia.json` | protocole de choix du seuil (plateau 0,20–0,22) | recommandé |
| `artefacts/comparaison_modeles_phishing_ia.csv` | résultats chiffrés par modèle | recommandé |
| `docs/11_plan_pptx_15_diapos.md` | plan 15 diapositives : titre, messages, valeurs exactes, image à insérer, notes | oui |
| `Presentation_Projet_Phishing_IA.pptx` | ancienne version de référence 20 diapositives (si présente) | facultatif |

Si le `.md` est absent ou périmé, le régénérer (commande donnée plus haut) :

```bash
python3 -m nbconvert --to markdown notebook_ML_IA_confiance_numerique.ipynb
```

### Prompt à copier-coller dans Copilot

```text
Tu es assistant de soutenance pour un Master Veille et Intelligence Compétitive (ESEN–ISCAE).
À partir des fichiers joints (notebook en Markdown, README, model_meta.json), crée une
présentation PowerPoint de 15 diapositives, en français, pour un jury non technique.

Règles absolues :
- N'invente AUCUN chiffre. Utilise uniquement ceux des fichiers joints.
- Une idée par diapositive, 5 puces maximum, pas de paragraphe dense.
- Charte : fond blanc, titres bleu marine, cartes bleu clair / gris, accent ambre.
- Chaque diapositive a des notes oratoires de 3 phrases : « À dire », « Pourquoi », « Question jury ».
- Ne jamais écrire « slide » dans le texte affiché.

Plan imposé :
1. Page de garde (titre, Master VIC, ESEN–ISCAE, mention données synthétiques)
2. Contexte général (phishing, IA générative, confiance numérique)
3. Problématique et objectifs
4. Solutions existantes et limites (SPF/DKIM/DMARC, filtres ML, réputation d'URL, LLM, suites commerciales)
5. Approche retenue et valeur ajoutée
6. Architecture globale (CSV → nettoyage → EDA → split 80/20 → pipeline → CV → test → app)
7. Processus ML en 10 étapes (le test n'apparaît qu'à l'étape 8)
8. Jeu de données et variables (524 lignes brutes, 520 propres, 374 Non / 146 Oui)
9. Nettoyage et qualité (4 doublons, 10 NA imputées par la médiane du train)
10. Analyse exploratoire (âge du domaine, urgence, liens, expéditeur inconnu)
11. Matrice de corrélation AVEC la cible, calculée sur le TRAIN ( domaine_age_jours −0,322 ;
    urgence_score +0,285 ; expediteur_connu −0,278 ; nb_liens +0,244 )
12. Préparation et séparation des données (416 train / 104 test, seed 42)
13. Modèles comparés et protocole (LR, Random Forest, SVM RBF, LR améliorée ; CV 5-fold sur le train)
14. Résultats (LR améliorée : AUC 0,910 ; AP 0,810 ; Brier 0,123 ; F1 macro 0,712 au seuil 0,21 ;
    F1 macro OOF 5×5 = 0,8082 au seuil 0,50)
15. Matrice de confusion et coût métier (TN 47, FP 28, FN 1, TP 28 ; coût 5·FN + FP = 33)
16. Importance des variables et analyse des erreurs (permutation, F1 macro)
17. Triage 3 zones, limites et perspectives (61/104 automatisés, 1 FN, 1 FP, 43 en revue)
18. Conclusion et questions
19. Annexe A — personnalisation_score (0–10 ; exemples générique/personnalisé ;
    moyennes 4,82 vs 5,40 ; r ≈ +0,10 ; ne prouve rien seule)
20. Annexe B — vérifications et traçabilité (notebook unique réexécuté, 82 cellules, 0 erreur ;
    3 cas du formulaire ; FN/FP par seuil et triage zéro erreur 0,07/0,98 → 74/104 en revue)

Points à ne pas rater :
- FN = phishing manqué = erreur critique ; FP = fausse alerte = coût analyste.
- Le seuil 0,21 vient du train (plateau de coût 0,20–0,22), jamais du test.
- FN = 0 et FP = 0 avec un seuil unique est impossible ; le triage 0,07/0,98 donne 0 FN / 0 FP
  sur la partie automatisée mais envoie 74 messages sur 104 en revue humaine.
- R², MAE et MSE restent présents dans la présentation PowerPoint comme mesure de calibration,
  mais ne pilotent pas la décision ; l'app simplifiée affiche le Brier Score et les matrices.
```

### Contrôles après génération

1. Vérifier que chaque chiffre du PPTX se retrouve dans le `.md` ou `model_meta.json`.
2. Vérifier la diapositive 11 : la cible doit être **dans** la matrice (dernière ligne/colonne).
3. Vérifier la diapositive 20 : les deux tableaux (3 cas, FN/FP) doivent être présents.
4. Comparer avec `Presentation_Projet_Phishing_IA.pptx`, généré par `scripts/make_pptx.py` :
   c'est la référence chiffrée.

## Formulaire : trois cas distincts (page 7)

Les trois scénarios chargibles donnent trois verdicts différents, calculés sur
**P(Oui)** (et non sur la confiance globale), avec le modèle amélioré et les seuils appris :

| Scénario | P(Oui) | Classe binaire (seuil 0,21) | Zone / action |
|---|---:|---|---|
| 1. Message normal | 0,1 % | Non — légitime | 🟢 NORMAL — surveillance courante |
| 2. Phishing typé IA | 100,0 % | Oui — malveillant | 🔴 ALERTE — vérification humaine prioritaire |
| 3. À surveiller | 47,1 % | **Malveillant** | 🟠 VIGILANCE — revue humaine |

La **classe binaire** est toujours `Malveillant` ou `Non malveillant` ; la **zone de triage**
est une action (qui doit agir, à quelle priorité), pas une troisième classe. Dans l'app, le verdict
binaire est affiché en premier et la zone de triage en information complémentaire.

Règle affichée dans l'application :

- `P(Oui) < 0,20` → 🟢 NORMAL (rappel en validation croisée ≥ 98 %) ;
- `0,20 ≤ P(Oui) < 0,88` → 🟠 VIGILANCE / revue humaine (cas ambigus) ;
- `P(Oui) ≥ 0,88` → 🔴 ALERTE (précision en validation croisée ≥ 85 %).

La décision **binaire** utilise le seuil coût `0,21` (`5·FN + FP`, plateau de coût en validation croisée
0,20–0,22 en validation croisée répétée 5×5). Les seuils ne sont plus fixés à la main :
ils sont **appris sur le train seul**. Tout verdict reste une aide à la décision :
validation humaine obligatoire, aucune suppression automatique.

## Vérifier que l'app utilise le nouveau dataset

La page 2 affiche la source du CSV lu au lancement :
`dataset_phishing_ia - dataset_phishing_ia.csv`, soit **524 lignes brutes → 520 après
`drop_duplicates()`** (374 `Non` / 146 `Oui`). L'empreinte SHA-256 (`9383a1b70165a728…`)
reste vérifiée dans `app.py` (`EMPREINTE_CSV`) et fait partie de la clé de cache Streamlit :
si le CSV est remplacé, les données, les graphiques et la matrice de corrélation sont
recalculés automatiquement.

## Fichiers

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit : 12 pages (accueil, EDA, corrélations, processus, comparaison, évaluation, prédiction, attributs, limites, guide, mode présentation, comprendre le ML) |
| `docs/01_dataset_and_eda.md` … `docs/11_plan_pptx_15_diapos.md` | Documentation scientifique, rapport d'audit et plan de présentation (11 fichiers) |
| `model.joblib` | Pipeline scikit-learn entraîné (régression logistique améliorée) |
| `model_meta.json` | Seuils appris, bornes des champs, métriques, triage, citation |
| `dataset_phishing_ia - dataset_phishing_ia.csv` | Jeu de données synthétique (copie locale) |
| `notebook_ML_IA_confiance_numerique.ipynb` | Notebook de référence, source des décisions scientifiques |
| `docs/11_plan_pptx_15_diapos.md` | Plan de la présentation **15 diapositives** : titre, messages, valeurs exactes, image à insérer, notes orales |
| `scripts/make_pptx.py` | Ancien générateur 20 diapositives (noms d'images issus d'anciens numéros de cellules) — **le plan de référence est `docs/11`** |
| `notebook_ML_IA_confiance_numerique.md` | Version Markdown du notebook exécuté (texte des cellules et sorties ; les graphiques restent dans le `.ipynb`) |
| `artefacts/seuil_phishing_ia.json` | Protocole de choix du seuil sauvegardé par le notebook |
| `artefacts/pptx/` | Images extraites du notebook pour la présentation |
| `requirements.txt` | Dépendances |
| `.streamlit/config.toml` | Thème clair de l'application |

## Validation croisée — critère de sélection du modèle

La validation croisée est calculée **sur le train seul** (416 messages). Deux protocoles distincts
coexistent dans les artefacts et ne doivent pas être confondus :

**A. CV 5-fold simple, `StratifiedKFold(5, shuffle=True, random_state=42)` — sorties réelles du notebook :**

| Modèle | F1 macro (moyenne ± écart-type) | Accuracy CV |
|---|---:|---:|
| Random Forest | **0,791 ± 0,051** | 0,839 |
| Régression logistique | 0,785 ± 0,067 | 0,810 |
| SVM RBF | 0,784 ± 0,018 | 0,815 |

**B. CV 5×5 répétée (graines 42–46) du §17, probabilités OOF moyennées :**

| Modèle | F1 macro OOF au seuil 0,50 | F1 macro moyen des 25 plis |
|---|---:|---:|
| **Régression logistique améliorée (retenue)** | **0,8082** | 0,8073 ± 0,0466 |

Les valeurs **0,814** et **0,771** anciennement annoncées ne sont reproductibles depuis aucun
artefact : elles ont été remplacées par les sorties réelles du notebook, **0,8082** (F1 macro OOF
5×5 au seuil 0,50, probabilités moyennées) et **0,8073 ± 0,0466** (moyenne des 25 plis). Les
entrées historiques `KNN` et `Dummy` ont été **retirées de `model_meta.json`** : elles n'étaient
produites par aucune cellule du notebook. Les trois modèles de référence réellement comparés
(`Random_Forest`, `Regression_logistique`, `SVM_RBF`) sont les seuls exposés par l'application.

La LR améliorée est retenue pour sa meilleure AUC/AP (0,910 / 0,810), son coût métier minimal (33)
et son interprétabilité — **pas** en comparant un F1 OOF 5×5 à un F1 CV 5-fold d'un autre modèle.
Le test de 104 messages ne sert qu'au contrôle final. Ces valeurs sont récapitulées dans l'app
(pages 5, 6 et 10) et discutées dans la diapositive 14 du PPTX, dont les chiffres historiques sont
signalés dans le rapport d'audit.

## Protocole reproductible

- `drop_duplicates()`, suppression de `date` (variable calendaire sans justification métier),
  cible jamais incluse dans `X`.
- Split 80/20 stratifié, `random_state=42` ; validation croisée **StratifiedKFold 5×5
  répétée sur le train uniquement** : AUC en validation croisée `0,909 ± 0,003`, AP `0,812 ± 0,003`.
- **Modèle retenu, identique dans le notebook et dans l'app** :
  `log1p(domaine_age_jours)` + interactions `urgence × inconnu` et `liens × inconnu`,
  retrait de `heure_envoi`, `longueur_message` et `fautes_langue` (bruit), puis
  imputation médiane, `StandardScaler` et `LogisticRegression(class_weight="balanced")`.
- Le Random Forest (300 arbres, `min_samples_leaf=2`) reste affiché comme **référence
  historique** dans les tableaux comparatifs ; il ne sert plus à la décision.
- Seuil binaire : plateau de coût minimal `5·FN + FP` en validation croisée, entre **0,20 et 0,22**,
  médiane **0,21**. Sensibilité : `c_FN = 3` → 0,47 ; `c_FN = 10` → 0,20.
- Résultats sur le test de 104 messages (29 `Oui`) : **AUC 0,910**, **AP 0,810**,
  Brier `0,123` ; au seuil `0,21` : `TN = 47, FP = 28, FN = 1, TP = 28`,
  rappel `Oui` **96,6 %**, F1 macro **0,712**, coût `5·FN + FP = 33`.
  À 0,50 : `TN = 58, FP = 17, FN = 5, TP = 24` (F1 macro 0,763, coût 42).
- **Triage 3 zones** (seuils train 0,20 / 0,88) : **61/104 messages traités
  automatiquement**, avec seulement **1 FN** et **1 FP** sur cette partie ; les
  **43 cas ambigus** sont confiés à l'analyste. La zone orange n'est pas un « succès »
  du classifieur : c'est une délégation explicite à l'humain.
- **Incertitude (bootstrap 2 000 tirages sur le test)** : rappel IC95 %
  `[0,886 ; 1,000]`, précision `[0,368 ; 0,636]`, taux de fausses alertes
  `[0,262 ; 0,481]`. Ces intervalles larges rappellent la petite taille de l'échantillon.
- Dans le PPTX : R², MAE et MSE sont calculés entre la probabilité `P(Oui)` et la vérité encodée
  0/1 (MSE = score de Brier) puis interprétés ; ils mesurent la **calibration**, la décision se juge
  sur la matrice de confusion au seuil appris. L'app affiche le Brier Score (0,123) en page 6.

## Matrice de confusion de la validation croisée

La page 6 affiche aussi la matrice de confusion de la **validation croisée**, calculée sur
le train seul (chaque message est prédit par un modèle qui ne l'a pas vu), avec les probabilités
moyennées sur 5 répétitions, au seuil `0,21` :

| | Prédit `Non` | Prédit `Oui` |
|---|---:|---:|
| **Réel `Non`** | TN = 182 | FP = 117 |
| **Réel `Oui`** | FN = 3 | TP = 114 |

Rappel `Oui` ≈ 97,4 %, précision `Oui` ≈ 49,4 %. Le nombre de FP y est plus élevé
que sur le test (28) : la CV décrit un régime moyen, le test de 104 messages est une
seule réalisation. Les deux matrices doivent être lues ensemble.

### FN et FP peuvent-ils atteindre 0 ?

Les pages 6 et 10 expliquent l'arbitrage seuil / triage. Réponse honnête :

- **FN = 0** est atteignable en baissant le seuil à `0,07` : tous les malveillants sont
  détectés, mais les fausses alertes explosent (**48 FP**) ;
- **FP = 0** est atteignable en montant le seuil à `0,98` : plus aucune fausse alerte,
  mais **26 malveillants** sont manqués ;
- **à 0,89 ou 0,90**, on obtient bien 1 FP, mais **15 à 18 FN** : ce n'est pas le
  compromis « 1 FN / 2 FP ». Le triage actuel fait mieux sur la partie automatisée
  (1 FN / 1 FP) tout en envoyant les cas douteux en revue humaine ;
- **FN = 0 et FP = 0 avec un seuil unique est impossible** sur ce jeu : les distributions des
  deux classes se chevauchent. Le seuil `0,21` est le compromis de coût `5·FN + FP` retenu ;
  le triage `0,20 / 0,88` confine les erreurs restantes à une revue humaine (1 FN et 1 FP
  sur la partie automatisée, 61 messages sur 104) ;
- **zéro erreur automatisée est possible** avec un triage `0,07 / 0,98` : 0 FN et 0 FP sur la
  partie automatique, mais **74 messages sur 104 (71 %) partent en revue humaine** et le
  système n'automatise plus que 30 cas. C'est le vrai arbitrage : automatisation contre erreurs.

## Vérifications et traçabilité

Ces vérifications sont aussi résumées dans l'application (pages 6, 9 et 10) et dans le rapport
`docs/09_audit_findings.md`.

**Notebook : un seul exemplaire, réellement exécuté**

- Le notebook du projet est **identique octet pour octet** au notebook réexécuté de zéro
  (`cmp` → IDENTIQUE) : **82 cellules, 0 erreur**.
- `model.joblib` identique ; `model_meta.json` ne change que des libellés (mêmes seuils, mêmes
  métriques).
- Le terme **OOF** est conservé et explicité (notebook §17, application pages 5, 6 et 10) :
  il s'agit d'une méthode de production de prédictions hors pli, pas d'une métrique. Résultats
  inchangés : **AUC 0,9092 ± 0,0031**, seuil **0,21**, test **AUC 0,910 / AP 0,810 / Brier 0,123**.
- Cohérence arithmétique corrigée dans le notebook : au seuil 0,21, le coût OOF vaut
  `5×3 + 117 = 132` ; le coût minimal **128** correspond au seuil 0,20 (`5×2 + 118`).
- La matrice de corrélation **inclut la cible** (`cible (Oui = 1)`) : on y lit à la fois la
  redondance entre variables et l'association de chacune avec la malveillance. Elle est calculée
  **sur le train seul** (cellule 31 : 416 messages, split stratifié `random_state=42`), et
  l'application affiche cette **heatmap exacte** (image extraite byte-à-byte dans
  `artefacts/matrice_correlation_eda.png`, SHA-256 `5ddaa6e4c3bb234f4a6df3f2d83da4b09560308ccf684ec115c95212dd45196d`).
  Le tableau de corrélations de la page 3 et le classement chiffré portent sur **ces mêmes
  416 lignes** : un seul protocole, plus de mélange train / jeu complet.

**Formulaire de prédiction : trois scénarios vérifiés**

| Scénario | `P(Oui)` | Classe binaire | Zone |
|---|---:|---|---|
| 1. Message normal | 0,06 % | `Non` — légitime | 🟢 NORMAL |
| 2. Phishing typé IA | 100,00 % | `Oui` — malveillant | 🔴 ALERTE |
| 3. À surveiller | 47,09 % | `Oui` — malveillant | 🟠 VIGILANCE |

La classe ne vaut jamais « À vérifier » : elle est `Oui` / `Non`, le triage est une colonne
séparée. Les trois probabilités ci-dessus sont reproduites par `model.joblib` avec les saisies
définies dans `CFG["scenarios"]` de `app.py`.

**FN / FP = 0 sur le test : les chiffres, sans promesse**

| Règle | FN | FP | Automatisés | Revue |
|---|---:|---:|---:|---:|
| Seuil unique 0,07 | 0 | 48 | 104 | 0 |
| Seuil unique 0,21 (retenu) | 1 | 28 | 104 | 0 |
| Seuil unique 0,98 | 26 | 0 | 104 | 0 |
| Triage 0,20 / 0,88 (retenu) | 1 | 1 | 61 | 43 |
| Triage 0,07 / 0,98 | 0 | 0 | 30 | 74 |

**0 FN et 0 FP sur la partie automatisée est possible** (triage 0,07 / 0,98), mais **74 messages
sur 104 (71 %) partent en revue humaine** et le système n'automatise plus que 30 cas. À 0,89 / 0,90
on a 1 FP mais 15 à 18 FN. Le compromis retenu reste **0,21 + triage 0,20 / 0,88**.

## Limites

Données synthétiques, seulement 104 messages en test, probabilités non calibrées
(pas de Platt / isotonique), seuil sensible au découpage sur 416 lignes d'entraînement.
Réduire en même temps FN et FP demande un meilleur classement, pas seulement un autre seuil :
le triage 3 zones diminue les erreurs **sur la partie automatisée** en augmentant le travail humain.
Toute alerte reste soumise à validation humaine.
