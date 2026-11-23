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
| 3. Prédiction / Verdict | 3 scénarios, formulaire, comparaison des modèles, explication du verdict |
| 4. Notebook | notebook complet, téléchargeable et affiché |
| 5. Soutenance (12 points) | plan de présentation : solutions existantes, problème, schéma global, données, justification du modèle, corrélation, résultats, **R² / MAE / MSE**, triage 3 zones, test final, limites et perspectives |

Les matrices de confusion des pages 2 et 5 portent **TN, FP, FN et TP dans chaque case**
(et non seulement dans un texte en dessous).

## Formulaire : trois cas distincts (page 3)

Les trois scénarios chargibles donnent trois verdicts différents, calculés sur
**P(Oui)** (et non sur la confiance globale), avec le modèle amélioré et les seuils appris :

| Scénario | P(Oui) | Classe | Verdict affiché |
|---|---:|---|---|
| 1. Message normal | 0,1 % | Non | 🟢 NORMAL — surveillance courante |
| 2. Phishing typé IA | 100,0 % | Oui | 🔴 ALERTE — vérification humaine prioritaire |
| 3. À surveiller | 47,1 % | À vérifier | 🟠 VIGILANCE — revue humaine |

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
| `artefacts/seuil_phishing_ia.json` | Protocole de choix du seuil sauvegardé par le notebook |
| `requirements.txt` | Dépendances |
| `.streamlit/config.toml` | Thème clair de l'application |

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

## Limites

Données synthétiques, seulement 104 messages en test, probabilités non calibrées
(pas de Platt / isotonique), seuil sensible au découpage sur 416 lignes d'entraînement.
Réduire en même temps FN et FP demande un meilleur classement, pas seulement un autre seuil :
le triage 3 zones diminue les erreurs **sur la partie automatisée** en augmentant le travail humain.
Toute alerte reste soumise à validation humaine.
