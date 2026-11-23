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
| 5. Soutenance (12 points) | plan de présentation complet : solutions existantes, problème, schéma global, données, justification du modèle, matrice de corrélation, résultats, **R² / MAE / MSE**, test final réel vs prédit, limites et perspectives |

## Formulaire : trois cas distincts (page 3)

Les trois scénarios chargibles donnent maintenant trois verdicts différents, calculés sur
**P(Oui)** (et non sur la confiance globale) :

| Scénario | P(Oui) | Classe | Verdict affiché |
|---|---:|---|---|
| 1. Message normal | 1,5 % | Non | 🟢 NORMAL — surveillance courante |
| 2. Phishing typé IA | 82,8 % | Oui | 🔴 ALERTE — vérification humaine prioritaire |
| 3. À surveiller | 21,1 % | Non | 🟠 VIGILANCE — à surveiller |

Règle affichée dans l'application : `P(Oui) ≥ 0,30` → alerte ; `0,15 ≤ P(Oui) < 0,30` → vigilance ;
`P(Oui) < 0,15` → normal. Un verdict reste toujours une aide à la décision : validation humaine obligatoire.

## Vérifier que l'app utilise le nouveau dataset

La page 2 affiche la source et l'empreinte SHA-256 du CSV lu au lancement :
`dataset_phishing_ia - dataset_phishing_ia.csv`, préfixe `9383a1b70165`,
**524 lignes brutes → 520 après `drop_duplicates()`** (374 `Non` / 146 `Oui`).
Le hash fait partie de la clé de cache Streamlit : si le CSV est remplacé, les données,
les graphiques et la matrice de corrélation sont recalculés automatiquement.

## Fichiers

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit : contexte, processus ML, prédiction, notebook |
| `model.joblib` | Pipeline scikit-learn entraîné (meilleur modèle : RandomForest) |
| `model_meta.json` | Seuil, bornes des champs, catégories, métriques, citation |
| `dataset_phishing_ia - dataset_phishing_ia.csv` | Jeu de données synthétique (copie locale) |
| `notebook_ML_IA_confiance_numerique.ipynb` | Notebook de référence, téléchargeable depuis l'app |
| `requirements.txt` | Dépendances |
| `.streamlit/config.toml` | Thème clair de l'application |

## Protocole reproductible

- `drop_duplicates()`, suppression de date.
- Split 80/20 stratifié, `random_state=42`.
- Pipeline : imputation médiane/mode, `StandardScaler`, `OneHotEncoder(handle_unknown='ignore')`
  ajustés sur le train uniquement.
- Critère de sélection : F1 macro. Meilleur modèle sur le test : **RandomForest** (F1 = 0.7792).
- Seuil de décision : **0.3**.
- Page 5 : R², MAE et MSE sont calculés entre la probabilité `P(Oui)` et la vérité encodée 0/1
  (MSE = score de Brier) puis interprétés ; ils mesurent la **calibration**, la décision se juge
  sur la matrice de confusion au seuil 0,30.
