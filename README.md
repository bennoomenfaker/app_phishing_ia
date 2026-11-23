# Sécurité — Phishing IA — application Streamlit

Mini-projet 3 — ISCAE Master VIC. Prototype pédagogique d'aide à la décision.
Données synthétiques, aucune donnée personnelle. Décision humaine obligatoire.

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

Si toutes les dépendances sont déjà installées pour l'utilisateur courant,
`python3 -m streamlit run app.py` suffit.

## Pages de l'application

| Page | Contenu |
|---|---|
| 1. Contexte & Problématique | contexte, questions de recherche, dictionnaire des variables |
| 2. Processus ML (pas à pas) | audit, EDA, corrélations, comparaison des modèles, matrices de confusion |
| 3. Prédiction / Verdict | 3 scénarios, formulaire, comparaison des modèles, matrice de confusion CV, FN/FP par seuil, explication du verdict |
| 4. Notebook | notebook complet, téléchargeable et affiché |
| 5. Soutenance (12 points) | plan de présentation : solutions existantes, problème, schéma global, données, justification du modèle, corrélation, résultats, **R² / MAE / MSE**, triage 3 zones, test final, limites et perspectives |
| 6. Présentation (soutenance) | la présentation complète en **Markdown** (18 parties + glossaire des métriques), **illustrée avec les graphiques du PPTX**, téléchargement du `.pptx` et du notebook |

Toutes les matrices de confusion (pages 2, 3 et 5) sont des **graphiques annotés** : chaque case
affiche **TN / FP / FN / TP**, son **effectif** et son **pourcentage**. Aucune matrice n'est affichée
uniquement sous forme de tableau. Les graphiques de distribution (cible, histogrammes, boxplots,
variables catégorielles) portent aussi les **valeurs et pourcentages** directement sur le graphique.

## Explication des variables

Chaque attribut est expliqué dans l'application (page 1, section **Explication détaillée des variables**),
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

## Générer la présentation PowerPoint et le Markdown du notebook

Les deux commandes se lancent depuis le dossier du projet, sans réseau.

```bash
# 1. Présentation PowerPoint (18 diapositives, images de artefacts/pptx/)
python3 scripts/make_pptx.py
# → Presentation_Projet_Phishing_IA.pptx

# 2. Notebook → Markdown (texte + images des sorties)
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

## Formulaire : trois cas distincts (page 3)

Les trois scénarios chargibles donnent trois verdicts différents, calculés sur
**P(Oui)** (et non sur la confiance globale), avec le modèle amélioré et les seuils appris :

| Scénario | P(Oui) | Classe binaire (seuil 0,21) | Zone / action |
|---|---:|---|---|
| 1. Message normal | 0,1 % | Non — légitime | 🟢 NORMAL — surveillance courante |
| 2. Phishing typé IA | 100,0 % | Oui — malveillant | 🔴 ALERTE — vérification humaine prioritaire |
| 3. À surveiller | 47,1 % | **Oui — malveillant probable** | 🟠 VIGILANCE — revue humaine |

La **classe binaire** est toujours `Oui` ou `Non` ; la **zone de triage** est une
action (qui doit agir, à quelle priorité), pas une troisième classe. Le tableau de
comparaison des modèles affiche les deux séparément : `P(Oui) %`, `Classe (seuil 0,21)`,
`Zone de triage`, `Action`.

Règle affichée dans l'application :

- `P(Oui) < 0,20` → 🟢 NORMAL (rappel OOF ≥ 98 %) ;
- `0,20 ≤ P(Oui) < 0,88` → 🟠 VIGILANCE / revue humaine (cas ambigus) ;
- `P(Oui) ≥ 0,88` → 🔴 ALERTE (précision OOF ≥ 85 %).

La décision **binaire** utilise le seuil coût `0,21` (`5·FN + FP`, plateau OOF
0,20–0,22 en validation croisée répétée 5×5). Les seuils ne sont plus fixés à la main :
ils sont **appris sur le train seul**. Tout verdict reste une aide à la décision :
validation humaine obligatoire, aucune suppression automatique.

## Vérifier que l'app utilise le nouveau dataset

La page 2 affiche la source et l'empreinte SHA-256 du CSV lu au lancement :
`dataset_phishing_ia - dataset_phishing_ia.csv`, préfixe `9383a1b70165a728`,
**524 lignes brutes → 520 après `drop_duplicates()`** (374 `Non` / 146 `Oui`).
Le hash fait partie de la clé de cache Streamlit : si le CSV est remplacé, les données,
les graphiques et la matrice de corrélation sont recalculés automatiquement.

## Fichiers

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit : contexte, processus ML, prédiction, notebook, soutenance |
| `model.joblib` | Pipeline scikit-learn entraîné (régression logistique améliorée) |
| `model_meta.json` | Seuils appris, bornes des champs, métriques, triage, citation |
| `dataset_phishing_ia - dataset_phishing_ia.csv` | Jeu de données synthétique (copie locale) |
| `notebook_ML_IA_confiance_numerique.ipynb` | Notebook de référence, téléchargeable depuis l'app |
| `Presentation_Projet_Phishing_IA.pptx` | Présentation 18 diapositives, notes orales, images issues du notebook exécuté |
| `scripts/make_pptx.py` | Régénère le PPTX depuis les images de `artefacts/pptx/` |
| `notebook_ML_IA_confiance_numerique.md` | Version Markdown du notebook exécuté (avec ses images) |
| `1.ipynb` | Copie de travail du notebook, identique à la version de référence |
| `artefacts/seuil_phishing_ia.json` | Protocole de choix du seuil sauvegardé par le notebook |
| `artefacts/pptx/` | Images extraites du notebook pour la présentation |
| `requirements.txt` | Dépendances |
| `.streamlit/config.toml` | Thème clair de l'application |

## Validation croisée — critère de sélection du modèle

La validation croisée est calculée **sur le train seul** (416 messages, `StratifiedKFold` 5 plis,
`random_state=42`). C'est elle qui désigne le modèle, pas le test :

| Modèle | F1 macro CV (moyenne des 5 plis) |
|---|---:|
| **Régression logistique améliorée** | **0,814** |
| Random Forest | 0,791 |
| Régression logistique | 0,785 |
| SVM RBF | 0,784 |
| KNN (k=7) | 0,727 |
| Dummy (classe majoritaire) | 0,418 |

La CV 5-fold est appliquée à **tous** les modèles, y compris la LR améliorée. Le Dummy n'est pas un
candidat : c'est le **plancher de référence** (0,418, aucun phishing détecté).

La LR améliorée est donc **le meilleur modèle en validation croisée**, et aussi le meilleur en
AUC/AP (0,910 / 0,810) avec le coût métier minimal (33). Le test de 104 messages ne sert qu'au
contrôle final. Ces valeurs sont affichées dans l'app (page 3, page 5 §10, page 6 §14) et dans la
diapositive 14 du PPTX.

## Protocole reproductible

- `drop_duplicates()`, suppression de `date` et `semaine` (aucune justification métier),
  cible jamais incluse dans `X`.
- Split 80/20 stratifié, `random_state=42` ; validation croisée **StratifiedKFold 5×5
  répétée sur le train uniquement** : AUC OOF `0,909 ± 0,003`, AP OOF `0,812 ± 0,003`.
- **Modèle retenu, identique dans le notebook et dans l'app** :
  `log1p(domaine_age_jours)` + interactions `urgence × inconnu` et `liens × inconnu`,
  retrait de `heure_envoi`, `longueur_message` et `fautes_langue` (bruit), puis
  imputation médiane, `StandardScaler` et `LogisticRegression(class_weight="balanced")`.
- Le Random Forest (300 arbres, `min_samples_leaf=2`) reste affiché comme **référence
  historique** dans les tableaux comparatifs ; il ne sert plus à la décision.
- Seuil binaire : plateau de coût OOF minimal `5·FN + FP` entre **0,20 et 0,22**,
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
- Page 5 : R², MAE et MSE sont calculés entre la probabilité `P(Oui)` et la vérité encodée 0/1
  (MSE = score de Brier) puis interprétés ; ils mesurent la **calibration**, la décision se juge
  sur la matrice de confusion au seuil appris.

## Matrice de confusion de la validation croisée

La page 3 affiche aussi la matrice de confusion de la **validation croisée**, calculée sur
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

La page 3 affiche un tableau de seuils sur le test. Réponse honnête :

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

## Limites

Données synthétiques, seulement 104 messages en test, probabilités non calibrées
(pas de Platt / isotonique), seuil sensible au découpage sur 416 lignes d'entraînement.
Réduire en même temps FN et FP demande un meilleur classement, pas seulement un autre seuil :
le triage 3 zones diminue les erreurs **sur la partie automatisée** en augmentant le travail humain.
Toute alerte reste soumise à validation humaine.
