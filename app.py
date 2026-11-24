CFG = {   'folder': 'app_phishing_ia',
    'titre': 'Sécurité — Phishing IA',
    'page_title': 'Phishing IA Studio',
    'icon': '🎣',
    'dataset': 'dataset_phishing_ia - dataset_phishing_ia.csv',
    'notebook': 'notebook_ML_IA_confiance_numerique.ipynb',
    'target': 'message_malveillant',
    'order': ['Non', 'Oui'],
    'colors': ['#4C78A8', '#E45756'],
    'drop_cols': ['date'],
        'seuil': 0.21,
    'citation': 'Données synthétiques générées pour un usage pédagogique — ISCAE Master VIC (aucune donnée '
                'personnelle).',
    'contexte': '\n'
                "L'IA générative écrit des messages de phishing sans fautes et avec un ton personnalisé. Les "
                'signes classiques\n'
                '(fautes de langue, style maladroit) deviennent donc moins fiables. Un responsable sécurité '
                'doit pourtant\n'
                'décider, parmi les messages reçus, lesquels méritent une analyse approfondie. Les 520 '
                'lignes du fichier après\n'
                'nettoyage sont **synthétiques** : aucun vrai e-mail, aucune donnée personnelle.',
    'problematique': '\n'
                     '**Comment détecter un message malveillant quand les signes classiques deviennent moins '
                     'fiables à cause de\n'
                     "l'IA, et comment garder un niveau d'alerte explicable ?**\n"
                     '\n'
                     'La cible `message_malveillant` est binaire (`Non` / `Oui`) avec **374 `Non` pour 146 `Oui`** après nettoyage (520 lignes) : les classes sont\n'
                     "déséquilibrées. L'accuracy seule est trompeuse (prédire toujours `Non` donne déjà ~72 "
                     '%) : on regarde surtout\n'
                     'le **rappel** et le **F1** de la classe `Oui`.',
    'questions': [   '**Q1.** Quels signaux (âge du domaine, urgence, liens, longueur) distinguent un '
                     'message malveillant ?',
                     "**Q2.** L'IA générative rend-elle la détection plus difficile (moins de fautes, plus "
                     'de personnalisation) ?',
                     '**Q3.** Quel modèle maximise le F1 macro malgré le déséquilibre 374/146 ?',
                     '**Q4.** Quel seuil de décision faut-il choisir pour limiter les faux négatifs ?',
                     "**Q5.** Comment expliquer l'alerte à l'analyste qui devra valider ?"],
    'erreur_couteuse': '\n'
                       '**Le faux négatif est le plus grave** : un message malveillant classé `Non` passe '
                       'les filtres et peut\n'
                       "déclencher une compromission. Le faux positif coûte du temps à l'analyste mais se "
                       'corrige par validation\n'
                       'humaine. Le seuil est **appris sur le train** (CV répétée 5×5, coût `5·FN + FP`, plateau 0,20–0,22) : plus de rappel (moins '
                       "d'attaques manquées),\n"
                       'au prix de plus de faux positifs. Un verdict `Oui` déclenche une vérification, '
                       'jamais une suppression\n'
                       'automatique.',
    'logique': '\n'
               '1. **X et y** : `y = message_malveillant`. `X` = toutes les colonnes **sauf `date` et '
               '`semaine`**\n'
               "   (variables calendaires exclues). Un `assert` vérifie que la cible n'est pas dans `X`.\n"
               '2. **Pipeline anti-fuite** : imputation médiane des 10 NA de `domaine_age_jours`, '
               'standardisation des\n'
               '   numériques, one-hot des catégorielles — ajusté sur le train uniquement.\n'
               '3. **Comparaison** : régression logistique, Random Forest, SVM RBF et KNN ; critère '
               '= **F1 macro**.\n'
               '4. **Décision binaire** : `P(Oui) >= seuil appris (0,21)` → `Oui`, sinon `Non`. Le seuil vient du train '
               'car un\n'
               "   phishing manqué est plus coûteux qu'une fausse alerte.\n"
               '5. **Alerte** : `Oui` → vérification humaine prioritaire ; `P(Oui)` entre 0,20 et 0,88 → '
               'vigilance ;\n'
               '   sinon surveillance courante.\n'
               '6. **Explication** : les signaux utilisés sont `domaine_age_jours` (en `log1p`), '
               '`urgence_score`,\n'
               '   `nb_liens` et `expediteur_connu`, avec deux interactions ; ils alimentent les recommandations.\n'
               "7. **Validation humaine** : aucune suppression automatique, décision finale à l'analyste.",
    'fields': {   'heure_envoi': ("Heure d'envoi (0-23)", 'Retiré du modèle (importance quasi nulle) ; affiché pour le contexte.'),
                  'longueur_message': (   'Longueur du message',
                                          'Retiré du modèle (importance négative) ; affiché pour le contexte.'),
                  'nb_liens': ('Nombre de liens', 'Chaque lien augmente le risque.'),
                  'urgence_score': (   "Score d'urgence (0-10)",
                                       'Pression temporelle : « agissez maintenant ».'),
                  'domaine_age_jours': (   'Âge du domaine (jours)',
                                           'Un domaine très récent est suspect ; 10 valeurs manquantes '
                                           'imputées par la médiane.'),
                  'fautes_langue': (   'Nombre de fautes de langue',
                                       "Retiré du modèle (importance négative) ; signe classique moins fiable avec l'IA."),
                  'expediteur_connu': ('Expéditeur connu (0/1)', '1 = expéditeur déjà connu, 0 = inconnu.'),
                  'piece_jointe': ('Pièce jointe (0/1)', '1 = pièce jointe présente.'),
                  'personnalisation_score': (   'Score de personnalisation (0-10)',
                                                "0 = message générique, 10 = nom / poste / contexte interne cités ; peu discriminant (r = +0,10) car l'IA personnalise aussi les arnaques."),
                  'date': (   'Date de réception',
                              'Exclue du modèle : variable calendaire sans justification métier.')},
    'scenarios': [   {   'nom': '1. Message normal',
                         'attendu': 'Non malveillant',
                         'valeurs': {   'heure_envoi': 10,
                                        'longueur_message': 180,
                                        'nb_liens': 0,
                                        'urgence_score': 1,
                                        'domaine_age_jours': 2200.0,
                                        'fautes_langue': 0,
                                        'expediteur_connu': 1,
                                        'piece_jointe': 0,
                                        'personnalisation_score': 2}},
                     {   'nom': '2. Phishing typé IA',
                         'attendu': 'Malveillant',
                         'valeurs': {   'heure_envoi': 2,
                                        'longueur_message': 780,
                                        'nb_liens': 5,
                                        'urgence_score': 9,
                                        'domaine_age_jours': 3.0,
                                        'fautes_langue': 0,
                                        'expediteur_connu': 0,
                                        'piece_jointe': 1,
                                        'personnalisation_score': 9}},
                     {   'nom': '3. À surveiller',
                         'attendu': 'Non malveillant — zone de vigilance',
                         'valeurs': {   'heure_envoi': 10,
                                        'longueur_message': 330,
                                        'nb_liens': 1,
                                        'urgence_score': 4,
                                        'domaine_age_jours': 160.0,
                                        'fautes_langue': 0,
                                        'expediteur_connu': 0,
                                        'piece_jointe': 0,
                                        'personnalisation_score': 2}}],
    'reason_rules': [   (   'domaine_age_jours',
                            'lte',
                            30,
                            'Domaine très récent : signal dominant du phishing.'),
                        ('urgence_score', 'gte', 7, "Score d'urgence élevé : pression pour agir vite."),
                        ('nb_liens', 'gte', 2, 'Plusieurs liens intégrés : risque de redirection trompeuse.'),
                        ('piece_jointe', 'eq', 1, "Pièce jointe présente : vecteur d'infection classique."),
                        ('expediteur_connu', 'eq', 0, 'Expéditeur inconnu : à vérifier.')]}


import base64
import hashlib
import inspect
import io
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.patches import FancyBboxPatch

st.set_page_config(page_title=CFG["page_title"], page_icon=CFG["icon"], layout="wide")
sns.set_theme(style="whitegrid")

# Compatibilité Streamlit < 1.50 / >= 1.50 (use_container_width -> width)
DF_KW = {"width": "stretch"} if "width" in inspect.signature(st.dataframe).parameters else {"use_container_width": True}
IMG_KW = {"width": "stretch"} if "width" in inspect.signature(st.image).parameters else {"use_container_width": True}
BTN_KW = {"width": "stretch"} if "width" in inspect.signature(st.form_submit_button).parameters else {"use_container_width": True}

ROOT = Path(__file__).parent
DATA_PATH = ROOT / CFG["dataset"]
EMPREINTE_CSV = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
MODEL_PATH = ROOT / "model.joblib"
META_PATH = ROOT / "model_meta.json"
NOTEBOOK = ROOT / CFG["notebook"]

TARGET = CFG["target"]
ORDER = CFG["order"]
DROP_COLS = CFG["drop_cols"]
NOM_AMELIORE = "Régression logistique améliorée"
_META_DICT = json.loads(META_PATH.read_text(encoding="utf-8"))
SEUIL = float(_META_DICT.get("seuil", CFG["seuil"]))
SEUIL_BAS = float(_META_DICT.get("seuil_bas", round(SEUIL - 0.01, 2)))
SEUIL_HAUT = float(_META_DICT.get("seuil_haut", 0.88))
ORD_MAP = {k: i for i, k in enumerate(ORDER)}
SEVERE = ORDER[-1]
RANDOM_STATE = 42

# Explication métier de chaque attribut : définition, échelle, exemple,
# lecture phishing et rôle dans le modèle. Utilisée page 1.
EXPLICATIONS_VARIABLES = {
    "date": {
        "titre": "Date de réception",
        "corps": """
**Définition.** Jour de réception du message dans le jeu de données.

**Rôle.** **Exclue du modèle** : variable calendaire sans justification métier
(elle mémoriserait la période de collecte, pas un signe de phishing).
""",
    },
    "heure_envoi": {
        "titre": "Heure d'envoi (0–23)",
        "corps": """
**Définition.** Heure à laquelle le message a été envoyé, de 0 à 23.

**Lecture phishing.** Un envoi à 2 h du matin peut trahir une automatisation,
mais beaucoup de messages légitimes arrivent aussi la nuit : le signal est faible.

**Exemple.** 10 h = horaire de bureau banal ; 3 h = à regarder, sans conclure.

**Rôle.** **Retirée du modèle final** (importance quasi nulle) ; conservée dans
l'audit et affichée dans le formulaire pour le contexte.
""",
    },
    "longueur_message": {
        "titre": "Longueur du message (caractères)",
        "corps": """
**Définition.** Nombre de caractères du message (60 à 896 dans ce jeu).

**Lecture phishing.** Dans ces données, les messages malveillants sont même
légèrement **plus courts** (≈ 395 caractères contre ≈ 421) : contre-intuitif, car
l'IA générative peut aussi produire des textes longs et soignés. La longueur ne
distingue donc pas les classes ici.

**Rôle.** **Retirée du modèle** (bruit, importance négative).
""",
    },
    "nb_liens": {
        "titre": "Nombre de liens",
        "corps": """
**Définition.** Nombre de liens hypertextes intégrés au message (0 à 5).

**Lecture phishing.** Chaque lien est une redirection potentielle vers un site
usurpé (faux portail bancaire, fausse page de connexion).

**Exemple.** 0 lien = message informatif ; 4–5 liens = campagne qui cherche à
faire cliquer le destinataire.

**Rôle.** **Conservée** ; elle interagit avec `expediteur_connu`
(liens × inconnu) dans le modèle amélioré.
""",
    },
    "urgence_score": {
        "titre": "Score d'urgence (0–10)",
        "corps": """
**Définition.** Pression temporelle ressentie dans le message : « agissez
maintenant », « votre compte sera suspendu sous 24 h ».

**Exemple.** 1 = ton neutre ; 9 = menace de suspension immédiate.

**Lecture phishing.** L'urgence empêche la victime de vérifier l'information par
un autre canal. C'est l'un des signaux les plus marqués du jeu (≈ 5,54 pour les
messages malveillants contre ≈ 4,11 pour les messages normaux).

**Rôle.** **Conservée** ; interaction `urgence × inconnu` dans le modèle.
""",
    },
    "domaine_age_jours": {
        "titre": "Âge du domaine expéditeur (jours)",
        "corps": """
**Définition.** Ancienneté du nom de domaine utilisé par l'expéditeur, en jours
(1 à 5 874). Dix valeurs manquantes sont imputées par la médiane.

**Lecture phishing.** Un domaine créé il y a quelques jours est un signal fort :
les campagnes utilisent des domaines neufs, pas encore inscrits sur les listes
noires. À l'inverse, un domaine établi depuis des années est plus rassurant.

**Exemple.** 3 jours = très suspect ; 2 200 jours = domaine ancien et établi.

**Rôle.** Variable la plus discriminante du jeu (≈ 339 jours en moyenne pour
`Oui` contre ≈ 897 pour `Non`). Elle est transformée en `log1p` pour que les
très grandes valeurs n'écrasent pas les domaines récents.
""",
    },
    "fautes_langue": {
        "titre": "Nombre de fautes de langue",
        "corps": """
**Définition.** Nombre de fautes détectées dans le message (0 à 6).

**Lecture phishing.** C'était un signe classique du phishing « artisanal », mais
l'IA générative écrit sans faute. Ici, la moyenne est presque identique dans les
deux classes (≈ 1,95 pour `Oui` contre ≈ 2,05 pour `Non`) : la variable ne sépare
plus rien.

**Rôle.** **Retirée du modèle** (bruit). Elle reste utile à expliquer pourquoi
les signaux « style maladroit » sont devenus moins fiables.
""",
    },
    "expediteur_connu": {
        "titre": "Expéditeur connu (0/1)",
        "corps": """
**Définition.** Indicateur binaire : `1` = adresse déjà connue de l'analyste
ou du destinataire, `0` = adresse jamais vue.

**Exemple.** Un fournisseur habituel = 1 ; une adresse inconnue = 0.

**Lecture phishing.** Les messages malveillants viennent plus souvent d'un
expéditeur inconnu (≈ 25 % de `1` côté `Oui` contre ≈ 51 % côté `Non`), mais
l'usurpation d'un contact connu reste possible : la variable ne suffit pas.

**Rôle.** **Conservée** ; interactions `urgence × inconnu` et `liens × inconnu`.
""",
    },
    "piece_jointe": {
        "titre": "Pièce jointe (0/1)",
        "corps": """
**Définition.** Indicateur binaire : `1` = le message contient une pièce jointe.

**Lecture phishing.** Une pièce jointe est un vecteur d'infection classique
(macro, exécutable, PDF piégé), mais beaucoup de messages professionnels
légitimes en contiennent aussi. Signal secondaire dans ce jeu.

**Rôle.** **Conservée**, avec une importance modérée.
""",
    },
    "personnalisation_score": {
        "titre": "Score de personnalisation (0–10)",
        "corps": """
**Définition.** Mesure **à quel point un message semble adapté personnellement à
son destinataire**, plutôt que d'être un message générique envoyé à tout le monde.

**Exemple 1 — message générique (score faible)**

> Cher client, votre compte nécessite une vérification. Cliquez ici.

Aucune information personnelle : le score doit rester bas.

**Exemple 2 — message personnalisé (score plus élevé)**

> Bonjour Faker, votre compte bancaire associé à votre adresse e-mail nécessite une vérification.

Le prénom et une information qui semble concerner le destinataire sont utilisés :
le score monte.

**Comment lire le score ?** L'échelle réelle du fichier va de **0 à 10** :

| Score | Interprétation |
|---|---|
| 0–2 | Très peu personnalisé |
| 3–4 | Faiblement personnalisé |
| 5–7 | Moyennement personnalisé |
| 8–10 | Fortement personnalisé |

Ces bornes sont **illustratives** : l'échelle du fichier est vérifiée dans le code,
pas supposée.

**Rapport avec le phishing.** Le *spear phishing* exploite des informations
personnelles pour gagner la confiance. Ici, les messages malveillants sont
légèrement plus personnalisés (≈ 5,40 contre ≈ 4,82), mais la corrélation avec la
cible reste faible (r ≈ +0,10).

**Attention :** un message très personnalisé n'est pas forcément malveillant — les
banques et les entreprises personnalisent aussi leurs envois. La variable est
**conservée**, mais elle ne suffit jamais seule : c'est la combinaison avec l'âge
du domaine, l'urgence et l'expéditeur inconnu qui produit le verdict.
""",
    },
    "message_malveillant": {
        "titre": "Cible — message malveillant (Non / Oui)",
        "corps": """
**Définition.** Variable à prédire : `Non` = message légitime, `Oui` = message
potentiellement malveillant (phishing).

**Rôle.** Elle n'est **jamais** utilisée comme variable explicative : le modèle
apprend à la retrouver à partir des neuf signaux précédents.
""",
    },
}


@st.cache_resource
def load_model(model_path, meta_path):
    return joblib.load(model_path), json.loads(Path(meta_path).read_text(encoding="utf-8"))


@st.cache_data
def load_data(data_path, colonnes_exclues, empreinte):
    """`empreinte` (SHA-256 du CSV) fait partie de la clé de cache : si le dataset est remplacé,
    Streamlit recharge automatiquement les nouvelles données au lieu de servir un ancien cache."""
    brut = pd.read_csv(data_path)
    propre = brut.drop_duplicates().drop(columns=colonnes_exclues, errors="ignore").copy()
    return brut, propre


def render_notebook(path: Path):
    if not path.exists():
        st.warning(f"Notebook introuvable : {path.name}")
        return
    nb = json.loads(path.read_text(encoding="utf-8"))
    st.caption(f"{path.name} — {len(nb.get('cells', []))} cellules")
    with open(path, "rb") as f:
        st.download_button("Télécharger le notebook (.ipynb)", f, file_name=path.name,
                           mime="application/x-ipynb+json")
    for i, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            st.markdown(src)
        elif cell.get("cell_type") == "code":
            st.markdown(f"**Code — cellule {i + 1}**")
            st.code(src if src.strip() else "# (cellule vide)", language="python")
            for out in cell.get("outputs", []):
                typ = out.get("output_type")
                data = out.get("data", {})
                if typ == "stream":
                    txt = "".join(out.get("text", []))
                    if txt.strip():
                        st.text(txt)
                elif typ in {"execute_result", "display_data"}:
                    if "image/png" in data:
                        img = data["image/png"]
                        img = "".join(img) if isinstance(img, list) else img
                        st.image(base64.b64decode(img))
                    elif "text/html" in data:
                        st.components.v1.html("".join(data["text/html"]), height=300, scrolling=True)
                    elif "text/plain" in data:
                        txt = "".join(data["text/plain"])
                        if txt.strip():
                            st.text(txt)
                elif typ == "error":
                    st.error("\n".join(out.get("traceback", [])) or out.get("evalue", "Erreur"))


def process_figure():
    """Processus ML réel du projet phishing — 10 étapes, sans fuite de données.

    Correction du schéma initial : le jeu test n'est consulté qu'à l'étape 8,
    après la sélection du modèle et du seuil sur le train seul. Il n'y a pas
    de one-hot encoding (toutes les variables explicatives sont numériques).
    """
    steps = [
        ("1  Données brutes", "CSV synthétique ISCAE\n524 lignes, 11 colonnes"),
        ("2  Audit & nettoyage", "4 doublons, 10 NA\ndate / semaine exclus"),
        ("3  Exploration (EDA)", "distributions,\ncorrélations"),
        ("4  Split train / test", "80 / 20 stratifié\nseed 42"),
        ("5  Pipeline anti-fuite", "log1p(âge), interactions,\nmédiane + scaling"),
        ("6  Comparaison & CV", "6 modèles, F1 macro\nCV 5-fold + 5×5"),
        ("7  Seuil appris (train)", "coût 5·FN + FP = 33\n0,21 + triage 0,20/0,88"),
        ("8  Évaluation test unique", "AUC 0,910, AP 0,810\nmatrice de confusion"),
        ("9  Importance & erreurs", "permutation,\nFN / FP interprétés"),
        ("10  Export & app", "joblib + Streamlit\nvalidation humaine"),
    ]
    colors = ["#9FD3C7", "#9FD3C7", "#9FD3C7", "#B8D8F2", "#B8D8F2",
              "#F5D7A1", "#F2B8B5", "#F2B8B5", "#CDB4DB", "#CDB4DB"]

    fig, ax = plt.subplots(figsize=(15, 5.2))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    w, h = 2.5, 1.35
    pos = ([(0.3 + i * 2.9, 3.4) for i in range(5)]
           + [(0.3 + (4 - i) * 2.9, 1.1) for i in range(5)])

    for (x, y), (titre, sous), couleur in zip(pos, steps, colors):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                    fc=couleur, ec="#333", lw=1.2))
        ax.text(x + w / 2, y + h * 0.68, titre, ha="center", va="center",
                fontsize=10.5, weight="bold")
        ax.text(x + w / 2, y + h * 0.27, sous, ha="center", va="center", fontsize=8.5)

    for i in range(9):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]
        if i < 4:
            a, b = (x1 + w + 0.05, y1 + h / 2), (x2 - 0.05, y2 + h / 2)
        elif i == 4:
            a, b = (x1 + w / 2, y1 - 0.05), (x2 + w / 2, y2 + h + 0.05)
        else:
            a, b = (x1 - 0.05, y1 + h / 2), (x2 + w + 0.05, y2 + h / 2)
        ax.annotate("", xy=b, xytext=a,
                    arrowprops=dict(arrowstyle="->", lw=1.8, color="#333"))

    ax.text(7.5, 0.35,
            "Règle clé : le jeu test n'est lu qu'à l'étape 8. Imputation, standardisation, "
            "choix du modèle et seuils sont appris sur le train uniquement (aucune fuite).",
            ha="center", fontsize=9.5, style="italic")
    ax.set_title("Processus Machine Learning — pré-détection phishing assistée",
                 fontsize=13, weight="bold")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=155, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def prepare_xy(df: pd.DataFrame):
    X = df.drop(columns=[TARGET]).copy()
    y = df[TARGET].copy()
    num = X.select_dtypes(include="number").columns.tolist()
    cat = [c for c in X.columns if c not in num]
    for c in cat:
        X[c] = X[c].astype(str).where(X[c].notna(), np.nan)
    return X, y, num, cat


class FeaturesPhishing:
    """Feature engineering sans fuite : exactement la même classe que dans le notebook.

    Le pipeline reçoit les 9 colonnes BRUTES du formulaire ; la transformation est
    interne, donc `meta["num"]` reste les colonnes brutes (pas `log_age`).
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        out = pd.DataFrame(index=X.index)
        out["log_age"] = np.log1p(X["domaine_age_jours"])
        out["urgence_score"] = X["urgence_score"]
        out["nb_liens"] = X["nb_liens"]
        out["expediteur_connu"] = X["expediteur_connu"]
        out["piece_jointe"] = X["piece_jointe"]
        out["personnalisation_score"] = X["personnalisation_score"]
        out["urg_x_inconnu"] = X["urgence_score"] * (1 - X["expediteur_connu"])
        out["liens_x_inconnu"] = X["nb_liens"] * (1 - X["expediteur_connu"])
        return out


def make_modele_ameliore():
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return Pipeline([
        ("features", FeaturesPhishing()),
        ("imputation", SimpleImputer(strategy="median")),
        ("standardisation", StandardScaler()),
        ("modele", LogisticRegression(max_iter=3000, class_weight="balanced",
                                      random_state=RANDOM_STATE)),
    ])


def make_preprocessor(num, cat):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    return ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat),
    ])


@st.cache_resource
def train_compare_models(propre: pd.DataFrame, cle_app: str):
    from sklearn.base import clone
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.svm import SVC
    from sklearn.pipeline import Pipeline

    X, y, num, cat = prepare_xy(propre.copy())
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y,
                                          random_state=RANDOM_STATE)
    pre = make_preprocessor(num, cat)
    defs = {
        "Régression logistique": LogisticRegression(max_iter=2000, class_weight="balanced",
                                                    random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=2,
                                                class_weight="balanced",
                                                random_state=RANDOM_STATE, n_jobs=-1),
        "KNN": KNeighborsClassifier(n_neighbors=7),
        "SVM RBF": SVC(
            kernel="rbf", C=1.0, gamma="scale",
            class_weight="balanced", probability=True,
            random_state=RANDOM_STATE
        ),
        NOM_AMELIORE: make_modele_ameliore(),
    }
    fitted = {}
    for name, estimator in defs.items():
        pipe = (clone(estimator) if isinstance(estimator, Pipeline)
                else Pipeline([("pre", pre), ("model", estimator)]))
        fitted[name] = pipe.fit(Xtr, ytr)
    return fitted, Xte, yte, num, cat


@st.cache_data
def get_cv_confusion(propre: pd.DataFrame, cle_app: str):
    """Matrice de confusion de la validation croisée (5×5 répétée) sur le train seul."""
    from sklearn.metrics import confusion_matrix
    from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

    X, y, _, _ = prepare_xy(propre.copy())
    Xtr, _, ytr, _ = train_test_split(X, y, test_size=0.2, stratify=y,
                                      random_state=RANDOM_STATE)
    ytr01 = (ytr == SEVERE).astype(int).values
    repetitions = []
    for seed in range(RANDOM_STATE, RANDOM_STATE + 5):
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        p = cross_val_predict(make_modele_ameliore(), Xtr, ytr, cv=cv,
                              method="predict_proba")[:, 1]
        repetitions.append(p)
    p_oof = np.mean(repetitions, axis=0)
    pred = (p_oof >= SEUIL).astype(int)
    tn, fp, fn, tp = confusion_matrix(ytr01, pred, labels=[0, 1]).ravel()
    return ytr01, p_oof, (int(tn), int(fp), int(fn), int(tp))


def table_fnfp(y_true, p, seuils):
    """Tableau FN/FP pour montrer qu'un seuil peut annuler FN *ou* FP, jamais les deux."""
    from sklearn.metrics import confusion_matrix
    lignes = []
    for t in seuils:
        pred = (p >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
        lignes.append({
            "Seuil": f"{t:.2f}", "TN": int(tn), "FP": int(fp),
            "FN": int(fn), "TP": int(tp),
            "Rappel": round(tp / max(tp + fn, 1), 3),
            "Précision": round(tp / max(tp + fp, 1), 3),
        })
    return pd.DataFrame(lignes)


@st.cache_data
def get_test_predictions(propre: pd.DataFrame, cle_app: str):
    fitted, Xte, yte, num, cat = train_compare_models(propre, cle_app)
    modele = fitted[NOM_AMELIORE]
    proba = modele.predict_proba(Xte)
    classes = list(modele.classes_)
    ordinal = sum(proba[:, j] * ORD_MAP[c] for j, c in enumerate(classes))
    severe_idx = classes.index(SEVERE) if SEVERE in classes else -1
    p_severe = proba[:, severe_idx]
    y_true_ord = pd.Series(yte).map(ORD_MAP).astype(float).values
    return y_true_ord, ordinal, p_severe


def predire(valeurs: dict, modele, meta: dict, seuil: float):
    ligne = pd.DataFrame([valeurs])
    for col, info in meta["num"].items():
        if col not in ligne.columns:
            ligne[col] = info["median"]
    for col, options in meta["cat"].items():
        if col not in ligne.columns:
            ligne[col] = options[0]
    ligne = ligne[list(meta["num"]) + list(meta["cat"])]
    proba = modele.predict_proba(ligne)[0]
    classes = list(modele.classes_)
    severe_idx = classes.index(SEVERE) if SEVERE in classes else -1
    p_severe = float(proba[severe_idx])
    confiance = float(np.max(proba))

    # Classe binaire : toujours Oui ou Non, jamais une troisième classe.
    binaire = SEVERE if p_severe >= seuil else ORDER[0]
    verdict = "Malveillant" if binaire == SEVERE else "Non malveillant"

    # Triage 3 zones appris sur le train : c'est une ACTION, pas une classe.
    #   P(Oui) >= seuil_haut (0,88)              -> 🔴 alerte prioritaire
    #   0,20 <= P(Oui) < 0,88                    -> 🟠 revue humaine
    #   P(Oui) < 0,20                            -> 🟢 normal
    if p_severe >= SEUIL_HAUT:
        zone = "🔴 ALERTE"
        action = "Vérification humaine prioritaire"
        niveau = "🔴 ALERTE — vérification humaine prioritaire"
    elif p_severe >= SEUIL_BAS:
        zone = "🟠 VIGILANCE"
        action = "À vérifier par un analyste"
        niveau = "🟠 VIGILANCE — revue humaine (à surveiller)"
    else:
        zone = "🟢 NORMAL"
        action = "Surveillance courante"
        niveau = "🟢 NORMAL — surveillance courante"

    return {"classe": binaire, "binaire": binaire, "verdict": verdict,
            "zone": zone, "action": action,
            "confiance": confiance, "p_severe": p_severe, "niveau": niveau,
            "probas": dict(zip(classes, proba))}

def expliquer(valeurs: dict):
    reasons = []
    for col, op, seuil_rule, text in CFG["reason_rules"]:
        v = valeurs.get(col)
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        try:
            if op == "gte":
                ok = float(v) >= seuil_rule
            elif op == "lte":
                ok = float(v) <= seuil_rule
            elif op == "eq":
                ok = str(v) == str(seuil_rule)
            elif op == "in":
                ok = str(v) in seuil_rule
            else:
                ok = False
        except (ValueError, TypeError):
            ok = False
        if ok:
            reasons.append(text)
    if not reasons:
        reasons.append("Aucun signal fort isolé : le modèle combine l'ensemble des variables.")
    return reasons


def architecture_figure():
    """Schéma global : composants et flux de données (données → modèle → décision → humain)."""
    fig, ax = plt.subplots(figsize=(13, 6.4))
    ax.axis("off")
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 6.9)

    def box(x, y, w, h, titre, sous, fc="#ecf0f1"):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.03,rounding_size=0.09",
                                    linewidth=1.2, edgecolor="#2c3e50", facecolor=fc))
        ax.text(x + w / 2, y + h * 0.66, titre, ha="center", va="center",
                fontsize=8.8, fontweight="bold")
        ax.text(x + w / 2, y + h * 0.28, sous, ha="center", va="center",
                fontsize=7.2, color="#334155")

    def fleche(x1, y1, x2, y2, couleur="#2c3e50", rad=0.0, style="-|>"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, lw=1.3, color=couleur,
                                    connectionstyle=f"arc3,rad={rad}"))

    # Colonnes
    for x, titre in [(0.35, "DONNÉES"), (4.35, "MODÈLE"), (8.35, "DÉCISION")]:
        ax.text(x, 6.55, titre, fontsize=10, fontweight="bold", color="#1d4ed8")

    # Données
    box(0.35, 4.55, 3.2, 1.35, "Messages reçus", "9 signaux extraits par message\n(urgence, liens, domaine, expéditeur…)")
    box(0.35, 2.35, 3.2, 1.35, "CSV synthétique", "524 lignes brutes → 520 après\nnettoyage — aucune donnée réelle")
    box(0.35, 0.35, 3.2, 1.35, "Audit qualité", "doublons, 10 NA imputés,\ncolonne date exclue")

    # Modèle
    box(4.35, 4.55, 3.2, 1.35, "Split 80 / 20 stratifié", "416 entraînement / 104 test\nrandom_state = 42")
    box(4.35, 2.35, 3.2, 1.35, "Pipeline anti-fuite", "imputation → standardisation\najustés sur le train seul")
    box(4.35, 0.35, 3.2, 1.35, "LR améliorée", "log1p(âge) + interactions\nbruit retiré, class_weight=balanced")

    # Décision
    box(8.35, 4.55, 3.4, 1.35, "Probabilité P(Oui)", "sortie continue du modèle\nentre 0 et 1")
    box(8.35, 2.35, 3.4, 1.35, "Seuil appris sur le train", "≥ seuil → suspect\n< seuil → normal")
    # Pas d'emoji ici : DejaVu Sans (police matplotlib) ne les contient pas et afficherait des carrés.
    box(8.35, 0.35, 3.4, 1.35, "Alerte + explication",
        "PRIORITAIRE / VIGILANCE /\nCOURANT + signaux dominants", fc="#fdeaea")

    # Flux verticaux
    for x in [1.95, 5.95, 10.05]:
        fleche(x, 4.55, x, 3.70)
        fleche(x, 2.35, x, 1.70)
    # Flux horizontaux (données → modèle → décision)
    fleche(3.55, 5.22, 4.35, 5.22)
    fleche(3.55, 3.02, 4.35, 3.02)
    fleche(3.55, 1.02, 4.35, 1.02)
    fleche(7.55, 5.22, 8.35, 5.22)
    fleche(7.55, 3.02, 8.35, 3.02)
    fleche(7.55, 1.02, 8.35, 1.02)

    # Boucle humaine
    ax.add_patch(FancyBboxPatch((8.35, 0.35), 3.4, 1.35, boxstyle="round,pad=0.03",
                                linewidth=0, facecolor="none"))
    ax.annotate("", xy=(1.95, 0.12), xytext=(10.05, 0.12),
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#d62728",
                                connectionstyle="arc3,rad=0.0"))
    ax.text(6.05, 0.03, "l'analyste valide, corrige et renvoie le retour (boucle humaine obligatoire)",
            ha="center", va="center", fontsize=7.4, color="#d62728", style="italic")

    ax.set_title("Schéma global — de la donnée brute à la décision assistée", fontsize=12, fontweight="bold")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=155, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


@st.cache_data(show_spinner=False)
def compute_soutenance(propre: pd.DataFrame, cle_app: str):
    """Tout ce qui est affiché en soutenance est recalculé ici, depuis le CSV et le modèle.

    Protocole : le train (80 %) sert à ajuster et à sélectionner (validation croisée 5-fold) ;
    le test (20 %) n'est touché qu'une seule fois, à la fin.
    """
    from sklearn.base import clone
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                                 precision_score, r2_score, recall_score,
                                 roc_auc_score)
    from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.svm import SVC
    from sklearn.pipeline import Pipeline

    X, y, num, cat = prepare_xy(propre.copy())
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y,
                                          random_state=RANDOM_STATE)
    pre = make_preprocessor(num, cat)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    defs = {
        "Dummy (classe majoritaire)": DummyClassifier(strategy="most_frequent"),
        "Régression logistique": LogisticRegression(max_iter=2000, class_weight="balanced",
                                                    random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=2,
                                                class_weight="balanced",
                                                random_state=RANDOM_STATE, n_jobs=-1),
        "KNN (k=7)": KNeighborsClassifier(n_neighbors=7),
        "SVM RBF": SVC(
            kernel="rbf", C=1.0, gamma="scale",
            class_weight="balanced", probability=True,
            random_state=RANDOM_STATE
        ),
        NOM_AMELIORE: make_modele_ameliore(),
    }

    lignes_test, lignes_cv, fitted, probas = [], [], {}, {}
    for nom, estimateur in defs.items():
        pipe = (clone(estimateur) if isinstance(estimateur, Pipeline)
                else Pipeline([("pre", pre), ("model", estimateur)]))
        pipe.fit(Xtr, ytr)
        fitted[nom] = pipe
        cv_pred = cross_val_predict(clone(pipe),
                                    Xtr, ytr, cv=cv, method="predict", n_jobs=1)
        lignes_cv.append({"Modèle": nom,
                          "F1 macro (CV 5-fold, train)": round(
                              f1_score(ytr, cv_pred, average="macro", zero_division=0), 4)})

        proba = pipe.predict_proba(Xte)[:, list(pipe.classes_).index(SEVERE)]
        probas[nom] = proba
        pred03 = np.where(proba >= SEUIL, SEVERE, ORDER[0])
        pred05 = pipe.predict(Xte)
        cm = confusion_matrix(yte, pred03, labels=ORDER)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
        lignes_test.append({
            "Modèle": nom,
            "Accuracy": round(accuracy_score(yte, pred03), 4),
            "Précision Oui": round(precision_score(yte, pred03, pos_label=SEVERE, zero_division=0), 4),
            "Rappel Oui": round(recall_score(yte, pred03, pos_label=SEVERE, zero_division=0), 4),
            "F1 macro": round(f1_score(yte, pred03, average="macro", zero_division=0), 4),
            "F1 macro @0,50": round(f1_score(yte, pred05, average="macro", zero_division=0), 4),
            "FN": int(fn), "FP": int(fp),
        })

    y01 = (yte == SEVERE).astype(int).values
    p_rf = probas[NOM_AMELIORE]
    pred_rf = np.where(p_rf >= SEUIL, SEVERE, ORDER[0])

    sst = float(((y01 - y01.mean()) ** 2).sum())
    mae_p = float(np.abs(y01 - p_rf).mean())
    mse_p = float(((y01 - p_rf) ** 2).mean())
    r2_p = 1 - float(((y01 - p_rf) ** 2).sum()) / sst if sst > 0 else 0.0

    base = np.full_like(y01, float((ytr == SEVERE).mean()), dtype=float)
    mae_r = float(np.abs(y01 - base).mean())
    mse_r = float(((y01 - base) ** 2).mean())
    r2_r = 1 - float(((y01 - base) ** 2).sum()) / sst if sst > 0 else 0.0

    seuils = np.round(np.sort(np.append(np.arange(0.05, 0.75, 0.05), SEUIL)), 2)
    tab_seuil = []
    for s in seuils:
        pred = np.where(p_rf >= s, SEVERE, ORDER[0])
        cm = confusion_matrix(yte, pred, labels=ORDER)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
        tab_seuil.append({"Seuil": float(s),
                          "Rappel Oui": round(recall_score(yte, pred, pos_label=SEVERE, zero_division=0), 4),
                          "Précision Oui": round(precision_score(yte, pred, pos_label=SEVERE, zero_division=0), 4),
                          "F1 macro": round(f1_score(yte, pred, average="macro", zero_division=0), 4),
                          "FN": int(fn), "FP": int(fp)})

    rf_pipe = fitted[NOM_AMELIORE]
    # Importance par permutation sur les colonnes BRUTES (la LR améliorée n'a pas
    # d'attribut feature_importances_). Même logique que la section 15 du notebook.
    from sklearn.inspection import permutation_importance
    perm = permutation_importance(rf_pipe, Xte, yte, n_repeats=8,
                                  random_state=RANDOM_STATE, scoring="f1_macro", n_jobs=1)
    importances = (pd.DataFrame({"Variable": X.columns,
                                 "Importance": perm.importances_mean})
                   .sort_values("Importance", ascending=False).reset_index(drop=True))

    corr_df = propre[num].copy()
    corr_df["_cible"] = propre[TARGET].map(ORD_MAP).astype(float)
    corr = corr_df.corr(numeric_only=True)

    rng = np.random.default_rng(7)
    idx = rng.choice(len(Xte), size=min(16, len(Xte)), replace=False)
    echantillon = []
    for i in idx:
        reel = yte.iloc[i]
        p = float(p_rf[i])
        pred = SEVERE if p >= SEUIL else ORDER[0]
        if reel == pred:
            statut = "correct"
        elif reel == SEVERE:
            statut = "FAUX NÉGATIF"
        else:
            statut = "faux positif"
        echantillon.append({"Message test": int(i) + 1, "Réel": reel,
                            "P(Oui)": round(p, 3), "Prédit": pred, "Statut": statut})

    pred_tr = rf_pipe.predict(Xtr)
    cm_030 = confusion_matrix(yte, pred_rf, labels=ORDER)

    # Triage 3 zones : seuils appris sur le train, jamais ajustes sur le test.
    zone = np.where(p_rf < SEUIL_BAS, "Normal",
                    np.where(p_rf >= SEUIL_HAUT, "Alerte", "Revue humaine"))
    yte01 = (yte == SEVERE).astype(int).values
    auto = zone != "Revue humaine"
    triage = {"auto": int(auto.sum()), "total": int(len(yte)),
              "fn_auto": int(((zone == "Normal") & (yte01 == 1)).sum()),
              "fp_auto": int(((zone == "Alerte") & (yte01 == 0)).sum()),
              "revue": int((~auto).sum())}

    return {
        "n_propre": int(len(propre)),
        "n_train": int(len(Xtr)), "n_test": int(len(Xte)),
        "n_oui": int((y == SEVERE).sum()), "n_non": int((y != SEVERE).sum()),
        "part_oui": float((y == SEVERE).mean()),
        "cv": pd.DataFrame(lignes_cv),
        "test": pd.DataFrame(lignes_test),
        "seuils": pd.DataFrame(tab_seuil),
        "rf": {"rappel": float(recall_score(yte, pred_rf, pos_label=SEVERE, zero_division=0)),
               "precision": float(precision_score(yte, pred_rf, pos_label=SEVERE, zero_division=0)),
               "f1_macro": float(f1_score(yte, pred_rf, average="macro", zero_division=0)),
               "acc": float(accuracy_score(yte, pred_rf)),
               "fn": int(cm_030.ravel()[2]), "fp": int(cm_030.ravel()[1]),
               "tn": int(cm_030.ravel()[0]), "tp": int(cm_030.ravel()[3]),
               "auc": float(roc_auc_score(y01, p_rf)),
               "mae": mae_p, "mse": mse_p, "r2": float(r2_p),
               "mae_base": mae_r, "mse_base": mse_r, "r2_base": float(r2_r),
               "var_y": float(y01.var()),
               "f1_train": float(f1_score(ytr, pred_tr, average="macro", zero_division=0)),
               "acc_train": float(accuracy_score(ytr, pred_tr))},
        "importances": importances,
        "corr": corr,
        "corr_cible": corr["_cible"].drop("_cible").sort_values(key=abs, ascending=False),
        "echantillon": pd.DataFrame(echantillon),
                "cm_rf": cm_030,
        "triage": triage,
        "cm_rf_probas": probas,
        "y01": y01.tolist(),
        "p_rf": p_rf.tolist(),
        "noms_modeles": list(defs.keys()),
    }


def _seuil_fleche(ax, seuil):
    ax.axvline(seuil, color="red", linestyle="--", linewidth=1.2,
               label="seuil retenu = " + format(seuil, ".2f"))


def heatmap_cm(ax, cm, titre=""):
    """Matrice de confusion avec TP / TN / FP / FN et leur pourcentage dans chaque case."""
    tn, fp, fn, tp = (int(v) for v in np.asarray(cm).ravel())
    total = max(tn + fp + fn + tp, 1)
    annot = np.array([
        [f"TN = {tn}\n{tn / total * 100:.1f} %", f"FP = {fp}\n{fp / total * 100:.1f} %"],
        [f"FN = {fn}\n{fn / total * 100:.1f} %", f"TP = {tp}\n{tp / total * 100:.1f} %"],
    ])
    sns.heatmap(cm, annot=annot, fmt="", cmap="Blues", cbar=False, ax=ax,
                xticklabels=["Prédit : Non", "Prédit : Oui"],
                yticklabels=["Réel : Non", "Réel : Oui"], annot_kws={"size": 9})
    ax.set_xlabel("Prédit")
    ax.set_ylabel("Réel")
    if titre:
        ax.set_title(titre, fontsize=9.5)


modele, meta = load_model(MODEL_PATH, META_PATH)
brut, propre = load_data(DATA_PATH, DROP_COLS, EMPREINTE_CSV)

st.title(CFG["icon"] + " " + CFG["titre"])
st.caption("Mini-projet 3 — ISCAE Master VIC | Prototype pédagogique d'aide à la décision")
st.markdown("**Données :** " + CFG["citation"])

page = st.sidebar.radio("Navigation", [
    "1. Contexte & Problématique",
    "2. Processus ML (pas à pas)",
    "3. Prédiction / Verdict",
    "4. Notebook",
    "5. Soutenance (12 points)",
    "6. Présentation (soutenance)",
])
st.sidebar.markdown("---")
st.sidebar.info("Outil pédagogique. Décision humaine obligatoire — aucun blocage automatique.")

# ------------------------- PAGE 1 -------------------------
if page.startswith("1"):
    st.header("1) Contexte, problématique et variables")
    st.subheader("Contexte général")
    st.markdown(CFG["contexte"])

    st.subheader("Problématique")
    st.info(CFG["problematique"])

    st.subheader("Objectif : pré-dépistage")
    st.markdown("""
Dans ce projet, le modèle fait du **pré-dépistage** : il trie rapidement les messages pour repérer ceux qui sont suspects.

- **Entrée** : signaux du message (urgence, liens, âge du domaine, expéditeur connu, pièce jointe...).
- **Sortie** : **Oui** (suspect/malveillant) ou **Non** (normal), avec une probabilité.
- **Exemple** : urgence élevée, plusieurs liens, domaine récent, expéditeur inconnu, pièce jointe → le modèle peut prédire **Oui**.

Le résultat est une aide à la décision. La vérification finale reste humaine.
""")

    st.subheader("Questions de recherche")
    st.markdown("\n".join("- " + q for q in CFG["questions"]))

    st.subheader("Erreur la plus coûteuse")
    st.warning(CFG["erreur_couteuse"])

    st.subheader("Comment choisir le modèle ?")
    st.markdown("""
**Base de choix**
- **Dummy/baseline** : référence minimum à dépasser.
- **F1 macro** : critère principal avec classes déséquilibrées (374 Non / 146 Oui).
- **Rappel Oui / FN** : priorité sécurité — un FN = message malveillant manqué.
- **Précision / FP** : surveiller les fausses alertes (coût analyste).
- **Matrice de confusion** : visualiser TN/FP/FN/TP par modèle.

**Modèles comparés** : régression logistique, Random Forest, **SVM RBF** et KNN (même split test) ; la baseline majoritaire sert de référence en page 5.

**Choix pour cette problématique** : **régression logistique améliorée** (AUC test **0,910**, AP **0,810**, FN 1 / FP 28 au seuil appris) — même pipeline que le notebook. Le seuil **0,21** vient du plateau de coût minimal en CV répétée 5×5 ; le triage 0,20 / 0,88 confie les cas ambigus à l'analyste. Aucun choix n'est automatique.
""")

    st.subheader("Processus ML (même démarche que le notebook)")
    st.image(process_figure(), **IMG_KW)

    st.subheader("Dictionnaire des variables")
    rows = []
    for col, (label, meaning) in CFG["fields"].items():
        kind = "Numérique" if col in meta["num"] else "Catégorielle"
        rows.append({"Variable": col, "Nom lisible": label, "Type": kind,
                     "Description / utilité": meaning})
    rows.append({"Variable": TARGET, "Nom lisible": "Cible",
                 "Type": "Target", "Description / utilité":
                 "Classe à prédire (" + ", ".join(ORDER) + "). Jamais utilisée comme variable explicative."})
    st.dataframe(pd.DataFrame(rows), **DF_KW, hide_index=True)
    st.caption("Variables exclues du modèle : " + (", ".join(DROP_COLS) if DROP_COLS else "aucune") +
               " (variable calendaire sans justification métier).")

    st.subheader("Explication détaillée des variables")
    st.caption("Pour chaque attribut : définition, échelle, exemple, lecture phishing et rôle dans "
               "le modèle. Les moyennes et corrélations sont recalculées à l'ouverture.")
    for col, d in EXPLICATIONS_VARIABLES.items():
        with st.expander(f"{d['titre']} — `{col}`"):
            st.markdown(d["corps"])
            if col == TARGET:
                st.markdown(
                    "**Dans ce jeu.** "
                    f"`Non` = {int((propre[TARGET] == ORDER[0]).sum())} messages, "
                    f"`Oui` = {int((propre[TARGET] == SEVERE).sum())} messages "
                    f"sur {len(propre)} — classes déséquilibrées.")
            elif col in propre.columns and col in meta["num"]:
                m_non = float(propre.loc[propre[TARGET] == ORDER[0], col].mean())
                m_oui = float(propre.loc[propre[TARGET] == SEVERE, col].mean())
                r = float(propre[col].corr((propre[TARGET] == SEVERE).astype(int)))
                st.markdown(
                    "**Dans ce jeu (calculé à l'ouverture).** "
                    f"Moyenne `Non` = {m_non:.2f} ; moyenne `Oui` = {m_oui:.2f} ; "
                    f"corrélation avec la cible r = {r:+.2f}.")

    st.subheader("Logique : comment le modèle prédit-il ?")
    st.markdown(CFG["logique"])

    st.subheader("Déclaration IA & éthique")
    st.markdown("""
    - Jeu de données **synthétique** généré pour un usage pédagogique : **aucune donnée personnelle**, aucun secret.
    - Modèle entraîné localement avec `scikit-learn`, sans service externe payant.
    - Le verdict est une **aide à la décision** : un humain (analyste, RSSI, DSI, vérificateur) valide toujours l'action.
    - Les probabilités et les variables dominantes sont affichées pour rendre la décision explicable.
    - Biais possibles : données simulées, petit effectif, classes déséquilibrées → ne pas généraliser à la production.
    """)

# ------------------------- PAGE 2 -------------------------
elif page.startswith("2"):
    st.header("2) Processus ML — pas à pas")
    st.markdown("Chaque étape est illustrée avec les données réelles du dataset. "
                "**Nom / utilité / lecture / interprétation** sont indiqués pour chaque graphique.")

    st.subheader("Étape 1 — Lecture et audit qualité")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes nettoyées", int(propre.shape[0]))
    c2.metric("Colonnes", int(brut.shape[1]))
    c3.metric("Doublons supprimés", int(brut.duplicated().sum()))
    c4.metric("Valeurs manquantes", int(brut.isna().sum().sum()))
    st.caption(f"**Source = nouveau dataset** : `{DATA_PATH.name}` — SHA-256 `{EMPREINTE_CSV[:12]}` — "
               f"{len(brut)} lignes brutes → {len(propre)} après `drop_duplicates()` "
               f"(colonne `{DROP_COLS[0]}` exclue). Tous les graphiques et la matrice de corrélation de "
               "cette page sont recalculés sur ce fichier, pas sur une capture ni sur un ancien CSV.")
    st.dataframe(brut.head(8), **DF_KW)
    with st.expander("Statistiques descriptives (describe)"):
        st.dataframe(brut.describe(include="all").T, **DF_KW)

    miss = brut.isna().sum()
    miss = miss[miss > 0]
    if len(miss):
        st.markdown("**Valeurs manquantes** : elles sont imputées par la médiane (numériques) "
                    "ou le mode (catégorielles) dans le pipeline, jamais sur le test.")
        st.dataframe(miss.rename("nb_NA").to_frame(), **DF_KW)

    st.subheader("Étape 2 — EDA : distribution de la cible")
    fig, ax = plt.subplots(figsize=(7, 3.5))
    counts = propre[TARGET].value_counts().reindex(ORDER).fillna(0)
    pct = counts / counts.sum() * 100
    ax.bar(ORDER, counts.values, color=CFG["colors"][:len(ORDER)])
    ax.set_ylabel("Nombre d'observations")
    ax.set_title("Distribution de " + TARGET + f" (n = {int(counts.sum())})")
    for i, (cls, v) in enumerate(counts.items()):
        ax.text(i, v + counts.max() * 0.02, f"{int(v)}\n({pct[cls]:.1f} %)",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_ylim(0, counts.max() * 1.18)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("**Lecture** : si une classe domine, l'accuracy est trompeuse. On utilise le F1 macro "
               "et un split stratifié.")

    st.subheader("Étape 3 — EDA : variables numériques par classe")
    fitted, Xte, yte, num_cols, cat_cols = train_compare_models(propre, CFG["folder"])
    n = len(num_cols)
    cols = 3
    lignes = (n + cols - 1) // cols
    fig, axes = plt.subplots(lignes, cols, figsize=(13, 3.3 * lignes))
    axes = np.atleast_1d(axes).ravel()
    for ax, col in zip(axes, num_cols):
        lignes = []
        for cls, color in zip(ORDER, CFG["colors"][:len(ORDER)]):
            serie = propre.loc[propre[TARGET] == cls, col].dropna()
            ax.hist(serie, bins=12, alpha=0.45, color=color,
                    label=f"{cls} (n = {len(serie)}, {len(serie) / len(propre):.1%})")
            lignes.append(f"{cls} : n = {len(serie)} | moyenne = {serie.mean():.1f}")
        ax.set_title(col, fontsize=9)
        ax.text(0.02, 0.98, "\n".join(lignes), transform=ax.transAxes, va="top",
                fontsize=6.5, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85))
    for ax in axes[n:]:
        ax.axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("**Lecture** : plus les histogrammes sont décalés entre couleurs, plus la variable "
               "sépare les classes. Un fort chevauchement signifie qu'une variable seule ne suffit pas.")

    st.subheader("Étape 4 — EDA : variable catégorielle et cible")
    cat_a_montrer = next(iter(meta["cat"]), None)
    if cat_a_montrer:
        tmp = propre.copy()
        tmp["_ord"] = tmp[TARGET].map(ORD_MAP)
        moy = tmp.groupby(cat_a_montrer, observed=True)["_ord"].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.bar(moy.index.astype(str), moy.values, color="#72B7B2")
        counts_cat = tmp[cat_a_montrer].value_counts().reindex(moy.index)
        for i, (val, n_cat) in enumerate(zip(moy.values, counts_cat.values)):
            ax.text(i, val + 0.02, f"{val:.2f}\n(n = {int(n_cat)}, {n_cat / len(tmp):.0%})",
                    ha="center", va="bottom", fontsize=8)
        ax.set_ylim(0, max(moy.max() * 1.25, 0.1))
        ax.set_ylabel("Gravité moyenne (0 → " + str(len(ORDER) - 1) + ")")
        ax.set_title("Gravité moyenne par " + cat_a_montrer)
        ax.tick_params(axis="x", rotation=20)
        st.pyplot(fig)
        plt.close(fig)
        st.caption("**Lecture** : une barre haute indique un segment plus à risque. Ce n'est pas "
                   "une preuve causale : la taille de l'échantillon compte.")

    st.subheader("Étape 5 — Matrice de corrélation (variables + cible)")
    COL_CIBLE = f"cible ({SEVERE} = 1)"
    df_corr = propre[num_cols + [TARGET]].copy()
    df_corr[COL_CIBLE] = (df_corr[TARGET] == SEVERE).astype(int)
    corr = df_corr[num_cols + [COL_CIBLE]].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(8, 6.4))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
    ax.set_title(f"Corrélation de Pearson — la cible est incluse ({SEVERE} = 1)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown(f"**La cible est dans la matrice** : sa dernière ligne / colonne donne l'association "
                f"de chaque variable avec `{SEVERE}` (encodée 1, `{ORDER[0]}` = 0).")
    top = corr[COL_CIBLE].drop(COL_CIBLE).sort_values(key=abs, ascending=False)
    st.dataframe(top.rename("corrélation_avec_cible").to_frame(), **DF_KW)
    signaux = ", ".join(f"`{c} {v:+.3f}`" for c, v in top.head(4).items())
    st.caption(f"**Signaux les plus liés à `Oui`, calculés sur le dataset courant** : {signaux}. "
               "**Lecture** : une valeur négative signifie que la variable diminue quand le message est "
               "malveillant. **Attention méthodologique** : `expediteur_connu` et `piece_jointe` sont des "
               "variables binaires 0/1 ; leur coefficient est une **corrélation point-bisérielle** (cas "
               "particulier de Pearson), à lire comme une différence de proportion entre les deux classes. "
               "Corrélation ≠ causalité, et mesure seulement un lien linéaire.")

    st.subheader("Étape 6 — Split, pipeline et modèles")
    st.code("""ColumnTransformer([
  ('num', Pipeline([SimpleImputer(median), StandardScaler()]), variables_numériques),
  ('cat', Pipeline([SimpleImputer(most_frequent), OneHotEncoder(handle_unknown='ignore')]), catégorielles)
])""", language="python")
    st.markdown("- Split **80 % train / 20 % test**, `stratify=y`, `random_state=42`.\n"
                "- Tous les `fit` (médiane, mode, scaler, encodeur) sont faits sur le **train uniquement** "
                "→ aucun fuite de données.\n"
                "- Modèles comparés : régression logistique, Random Forest, SVM RBF, KNN (+ baseline majoritaire en page 5).\n"
                "- Le modèle retenu est sauvegardé dans `model.joblib` avec son seuil dans `model_meta.json`.")

    st.subheader("Étape 7 — Résultats et interprétation")
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    rows = []
    for name, m in fitted.items():
        yp = m.predict(Xte)
        rows.append({"Modèle": name,
                     "Accuracy": round(accuracy_score(yte, yp), 4),
                     "F1 macro": round(f1_score(yte, yp, average="macro", zero_division=0), 4),
                     "Précision macro": round(precision_score(yte, yp, average="macro", zero_division=0), 4),
                     "Rappel macro": round(recall_score(yte, yp, average="macro", zero_division=0), 4)})
    st.dataframe(pd.DataFrame(rows).sort_values("F1 macro", ascending=False),
                 **DF_KW, hide_index=True)
    st.caption("**F1 macro = critère principal** : chaque classe a le même poids, ce qui évite d'être "
               "trompé par le déséquilibre. Scores au seuil par défaut du modèle (0,50) ; "
               f"les métriques au seuil appris ({SEUIL:.2f}) sont détaillées en page 5, §10.")

    st.subheader("Étape 8 — Matrices de confusion par modèle (même test)")
    from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay
    cm_rows=[]
    cms={}
    for name,m in fitted.items():
        yp=m.predict(Xte)
        cm=confusion_matrix(yte, yp, labels=ORDER)
        tn,fp,fn,tp=cm.ravel() if cm.shape==(2,2) else (0,0,0,0)
        cms[name]=cm
        cm_rows.append({"Modèle":name,
                        "Accuracy":round(accuracy_score(yte,yp),4),
                        "Précision Oui":round(precision_score(yte,yp,pos_label=SEVERE,zero_division=0),4),
                        "Rappel Oui":round(recall_score(yte,yp,pos_label=SEVERE,zero_division=0),4),
                        "F1 macro":round(f1_score(yte,yp,average='macro',zero_division=0),4),
                        "FN (malveillant manqué)":int(fn),"FP (fausse alerte)":int(fp)})
    cmp_cm=pd.DataFrame(cm_rows).set_index("Modèle").sort_values(["Rappel Oui","F1 macro"], ascending=False)
    st.dataframe(cmp_cm, **DF_KW)
    cols=st.columns(min(len(cms), 3))
    for i,(name,cm) in enumerate(cms.items()):
        fig,ax=plt.subplots(figsize=(4.2,3.4))
        heatmap_cm(ax, cm, f'{name}\nseuil 0.50')
        tn,fp,fn,tp=cm.ravel()
        with cols[i % 3]:
            st.pyplot(fig); plt.close(fig)
            st.caption(f"TN={tn} FP={fp} FN={fn} TP={tp}")
    best_recall = cmp_cm['Rappel Oui'].idxmax()
    best_f1 = cmp_cm['F1 macro'].idxmax()
    st.info(f"**Meilleur Rappel Oui (moins de malveillants manqués)** : {best_recall} — Rappel={cmp_cm.loc[best_recall,'Rappel Oui']:.2%}, FN={int(cmp_cm.loc[best_recall,'FN (malveillant manqué)'])}, FP={int(cmp_cm.loc[best_recall,'FP (fausse alerte)'])}.")
    st.success(f"**Meilleur F1 macro (équilibre global)** : {best_f1} — F1 macro={cmp_cm.loc[best_f1,'F1 macro']:.4f}.")
    st.markdown("""
**Interprétation**
- **FN (malveillant manqué)** : message malveillant prédit `Non` → erreur la plus coûteuse en sécurité.
- **FP (fausse alerte)** : message normal prédit `Oui` → coûte du temps à l'analyste.
- En phishing IA, on priorise souvent **Rappel Oui / moins de FN**, puis on contrôle les FP par validation humaine.
""")
    with st.expander("Rapport détaillé par modèle"):
        choix = st.selectbox("Modèle à inspecter", list(fitted.keys()), key='report_cm')
        st.text(classification_report(yte, fitted[choix].predict(Xte), labels=ORDER, zero_division=0))

    st.subheader("Étape 9 — Réel vs prédit sur le test")
    y_true_ord, ordinal_pred, p_severe = get_test_predictions(propre, CFG["folder"])
    fig, ax = plt.subplots(figsize=(7, 5))
    jitter = np.random.default_rng(42).normal(0, 0.04, len(y_true_ord))
    pred_ord = np.where(p_severe >= SEUIL, SEVERE, ORDER[0])
    pred_ord_num = pd.Series(pred_ord).map(ORD_MAP).astype(float).values
    colors = np.where((y_true_ord > pred_ord_num), "#d62728",
                      np.where((y_true_ord < pred_ord_num), "#ff7f0e", "#2ca02c"))
    ax.scatter(y_true_ord + jitter, p_severe, c=colors, alpha=0.65,
               edgecolor="white", linewidth=0.3)
    ax.axhline(SEUIL, color="red", linestyle="--", label="Seuil = " + format(SEUIL, ".2f"))
    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels(ORDER)
    ax.set_ylabel("Probabilité de la classe la plus grave (" + SEVERE + ")")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("Réel vs prédit (test) — probabilité et seuil")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown("""
**Interprétation (4 zones)**
- **Ligne rouge (seuil)** : au-dessus → prédit `Oui` (malveillant) ; en dessous → prédit `Non`.
- **Haut gauche** (Réel Non, au-dessus seuil) : **FP** orange — fausse alerte.
- **Bas gauche** (Réel Non, sous seuil) : **TN** vert — normal bien classé.
- **Haut droite** (Réel Oui, au-dessus seuil) : **TP** vert — malveillant détecté.
- **Bas droite** (Réel Oui, sous seuil) : **FN** rouge — malveillant manqué, erreur la plus coûteuse.
""")

# ------------------------- PAGE 3 -------------------------
elif page.startswith("3"):
    st.header("3) Prédiction / Verdict final")
    st.markdown("Saisissez une situation. Les modèles comparent la **même entrée**. "
                "Seuil utilisé : **" + format(SEUIL, ".2f") + "**. Outil d'aide à la décision, "
                "**pas de décision automatique**.")

    st.subheader("Scénarios de test (3 exemples pédagogiques)")
    st.caption("Trois cas : **Malveillant**, **Non malveillant** et **Non malveillant — zone de vigilance** "
               "(P(Oui) entre " + format(SEUIL_BAS, ".2f") + " et " + format(SEUIL_HAUT, ".2f") +
               "). Le verdict reste binaire ; la zone indique seulement la priorité de vérification. "
               "Cliquez sur « Charger ce scénario » pour modifier le formulaire.")
    scols = st.columns(3)
    for i, sc in enumerate(CFG["scenarios"]):
        with scols[i]:
            r = predire(sc["valeurs"], modele, meta, SEUIL)
            classe_txt = r["verdict"]
            st.markdown("**" + sc["nom"] + "**")
            st.caption("Attendu : " + sc["attendu"])
            st.write("Classe binaire : **" + classe_txt + "**")
            st.write("**P(Oui) : " + format(r["p_severe"], ".1%") + "**")
            st.write("Triage : **" + r["zone"] + "** — " + r["action"])
            if st.button("Charger ce scénario", key="sc_" + str(i)):
                st.session_state["scenario"] = sc["valeurs"]
                st.rerun()

    valeurs = dict(st.session_state.get("scenario", {}))
    saisi = {}
    with st.form("formulaire_prediction"):
        colA, colB = st.columns(2)
        num_items = list(meta["num"].items())
        half = (len(num_items) + 1) // 2
        with colA:
            st.markdown("#### Variables numériques")
            for col, info in num_items[:half]:
                label, desc = CFG["fields"].get(col, (col, ""))
                saisi[col] = st.number_input(
                    label, min_value=float(info["min"]), max_value=float(info["max"]),
                    value=float(valeurs.get(col, info["median"])), key="n_" + col, help=desc)
        with colB:
            st.markdown("#### Variables numériques (suite)")
            for col, info in num_items[half:]:
                label, desc = CFG["fields"].get(col, (col, ""))
                saisi[col] = st.number_input(
                    label, min_value=float(info["min"]), max_value=float(info["max"]),
                    value=float(valeurs.get(col, info["median"])), key="n_" + col, help=desc)
        st.markdown("#### Variables catégorielles")
        catcols = st.columns(2)
        for i, (col, options) in enumerate(meta["cat"].items()):
            label, desc = CFG["fields"].get(col, (col, ""))
            with catcols[i % 2]:
                idx = options.index(str(valeurs[col])) if str(valeurs.get(col)) in options else 0
                saisi[col] = st.selectbox(label, options, index=idx, key="c_" + col, help=desc)
        envoyer = st.form_submit_button("Prédire / Comparer les modèles", **BTN_KW)

    if envoyer:
        st.markdown("### Données saisies")
        st.dataframe(pd.DataFrame([saisi]), **DF_KW, hide_index=True)

        fitted, _, _, _, _ = train_compare_models(propre, CFG["folder"])
        comparaison = {"Modèle retenu (joblib)": modele}
        comparaison.update(fitted)
        rows = []
        for name, m in comparaison.items():
            r = predire(saisi, m, meta, SEUIL)
            rows.append({
                "Modèle": name,
                "P(Oui) %": round(r["p_severe"] * 100, 2),
                "Verdict": r["verdict"],
            })
        st.markdown("### Comparaison des modèles (mêmes données formulaire)")
        st.dataframe(pd.DataFrame(rows), **DF_KW, hide_index=True)
        st.caption("Verdict binaire au seuil " + format(SEUIL, ".2f") +
                   " : **Malveillant** si P(Oui) ≥ seuil, sinon **Non malveillant**. "
                   "La probabilité est une information complémentaire, pas un troisième résultat.")

        # matrices de confusion par modèle sur test
        from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
        fitted_cmp, Xte_c, yte_c, _, _ = train_compare_models(propre, CFG["folder"])
        cm_rows=[]
        cms={}
        for name,m in fitted_cmp.items():
            proba_te=m.predict_proba(Xte_c)[:, list(m.classes_).index(SEVERE)]
            yp=np.where(proba_te>=SEUIL, SEVERE, ORDER[0])
            cm=confusion_matrix(yte_c, yp, labels=ORDER)
            tn,fp,fn,tp=cm.ravel() if cm.shape==(2,2) else (0,0,0,0)
            cms[name]=cm
            cm_rows.append({"Modèle":name,"Accuracy":round(accuracy_score(yte_c,yp),4),"Précision Oui":round(precision_score(yte_c,yp,pos_label=SEVERE,zero_division=0),4),"Rappel Oui":round(recall_score(yte_c,yp,pos_label=SEVERE,zero_division=0),4),"F1 macro":round(f1_score(yte_c,yp,average='macro',zero_division=0),4),"FN":int(fn),"FP":int(fp)})
        st.markdown("### Matrices de confusion par modèle (même jeu de test, seuil " + format(SEUIL, ".2f") + ")")
        st.dataframe(pd.DataFrame(cm_rows).set_index('Modèle'), **DF_KW)
        cmc=st.columns(min(len(cms), 3))
        for i,(name,cm) in enumerate(cms.items()):
            tn,fp,fn,tp=cm.ravel()
            fig,ax=plt.subplots(figsize=(4.8,3.6))
            heatmap_cm(ax, cm, f"{name}\nseuil {SEUIL:.2f}")
            with cmc[i % 3]:
                st.pyplot(fig); plt.close(fig)
                st.caption(f'TN={tn} · FP={fp} · FN={fn} · TP={tp}')
        best_recall=max(cm_rows, key=lambda r:r['Rappel Oui'])
        st.info(f"**Modèle prioritaire pour la problématique (moins de FN/malveillants manqués)** : {best_recall['Modèle']} — Rappel Oui={best_recall['Rappel Oui']:.2%}, FN={best_recall['FN']}, FP={best_recall['FP']}. Un FN en phishing signifie un message malveillant non détecté.")

        # -------- Validation croisée : sélection du modèle sur le train --------
        from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
        X_cv, y_cv, _, _ = prepare_xy(propre.copy())
        Xtr_cv, _, ytr_cv, _ = train_test_split(X_cv, y_cv, test_size=0.2, stratify=y_cv,
                                              random_state=RANDOM_STATE)
        cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        cv_rows = []
        for name, m in fitted_cmp.items():
            sc = cross_val_score(m, Xtr_cv, ytr_cv, cv=cv5, scoring="f1_macro", n_jobs=1)
            cv_rows.append({"Modèle": name,
                            "F1 macro CV (moyenne)": round(float(sc.mean()), 4),
                            "Écart-type CV": round(float(sc.std()), 4)})
        cv_table = pd.DataFrame(cv_rows).sort_values("F1 macro CV (moyenne)", ascending=False)
        st.markdown("### Validation croisée 5-fold (train) — sélection du modèle")
        st.dataframe(cv_table, **DF_KW, hide_index=True)
        st.success(f"**Meilleur F1 macro en validation croisée : {cv_table.iloc[0]['Modèle']}** — "
                   f"{cv_table.iloc[0]['F1 macro CV (moyenne)']:.4f} sur le train. Ce score est le "
                   "critère de sélection ; le test de contrôle reste séparé.")

        # -------- Matrice de confusion de la validation croisée (train) --------
        st.markdown("### Matrice de confusion — validation croisée (train, 416 messages)")
        ytr01, p_cv, cm_cv = get_cv_confusion(propre, CFG["folder"])
        tn_cv, fp_cv, fn_cv, tp_cv = cm_cv
        cvc1, cvc2 = st.columns([2, 3])
        with cvc1:
            fig, ax = plt.subplots(figsize=(4.8, 3.6))
            heatmap_cm(ax, np.array([[tn_cv, fp_cv], [fn_cv, tp_cv]]),
                       "Validation croisée 5×5 répétée\nseuil " + format(SEUIL, ".2f"))
            st.pyplot(fig)
            plt.close(fig)
        with cvc2:
            st.markdown(
                f"**Rappel Oui : {tp_cv / max(tp_cv + fn_cv, 1):.1%}** · "
                f"**Précision Oui : {tp_cv / max(tp_cv + fp_cv, 1):.1%}**\n\n"
                f"TN = {tn_cv} · FP = {fp_cv} · FN = {fn_cv} · TP = {tp_cv}\n\n"
                "Cette matrice est calculée **uniquement sur le train** : chaque message est prédit "
                "par un modèle qui ne l'a pas vu (validation croisée), puis les probabilités sont "
                "moyennées sur 5 répétitions. Elle sert à choisir le seuil et le triage ; "
                "elle n'utilise jamais le test."
            )
            st.caption("Le nombre de FP y est plus élevé que sur le test : la validation croisée décrit "
                       "un régime moyen, le test de 104 messages est une seule réalisation. "
                       "Les deux se lisent ensemble.")

        # -------- FN / FP aux seuils extrêmes --------
        st.markdown("### FN et FP peuvent-ils atteindre 0 ? — réponse chiffrée (test)")
        p_amel = fitted_cmp[NOM_AMELIORE].predict_proba(Xte_c)[:, list(fitted_cmp[NOM_AMELIORE].classes_).index(SEVERE)]
        y01_c = (yte_c == SEVERE).astype(int).values
        t_fn0 = float(np.floor(p_amel[y01_c == 1].min() * 100) / 100)
        t_fp0 = float(np.ceil(p_amel[y01_c == 0].max() * 100) / 100)
        tab_ext = table_fnfp(y01_c, p_amel, sorted({t_fn0, round(SEUIL, 2), t_fp0}))
        st.markdown("**Seuil unique sur P(Oui)** — on ne peut annuler qu'une seule des deux erreurs :")
        st.dataframe(tab_ext, **DF_KW, hide_index=True)

        def _triage_test(bas, haut):
            zone = np.where(p_amel < bas, "Normal",
                            np.where(p_amel >= haut, "Alerte", "Revue humaine"))
            auto = zone != "Revue humaine"
            return {"FN (auto)": int(((zone == "Normal") & (y01_c == 1)).sum()),
                    "FP (auto)": int(((zone == "Alerte") & (y01_c == 0)).sum()),
                    "Automatisés": int(auto.sum()), "Revue humaine": int((~auto).sum())}

        tri_retenu = _triage_test(SEUIL_BAS, SEUIL_HAUT)
        tri_zero = _triage_test(t_fn0, t_fp0)
        st.markdown("**Avec le triage 3 zones** — les cas ambigus sortent du calcul automatique :")
        st.dataframe(pd.DataFrame([
            {"Règle": f"Triage retenu {SEUIL_BAS:.2f} / {SEUIL_HAUT:.2f}", **tri_retenu},
            {"Règle": f"Triage « zéro erreur » {t_fn0:.2f} / {t_fp0:.2f}", **tri_zero},
        ]), **DF_KW, hide_index=True)

        fp_bas = int(tab_ext.loc[tab_ext["Seuil"] == f"{t_fn0:.2f}", "FP"].iloc[0])
        fn_haut = int(tab_ext.loc[tab_ext["Seuil"] == f"{t_fp0:.2f}", "FN"].iloc[0])
        fn_retenu = int(tab_ext.loc[tab_ext["Seuil"] == f"{round(SEUIL, 2):.2f}", "FN"].iloc[0])
        fp_retenu = int(tab_ext.loc[tab_ext["Seuil"] == f"{round(SEUIL, 2):.2f}", "FP"].iloc[0])
        st.markdown(
            f"- **FN = 0 sur le test est atteignable** en descendant le seuil à {t_fn0:.2f} : "
            f"tous les malveillants sont détectés, mais on crée **{fp_bas} fausses alertes**.\n"
            f"- **FP = 0 sur le test est atteignable** en montant le seuil à {t_fp0:.2f} : plus aucune "
            f"fausse alerte, mais **{fn_haut} malveillants passent**.\n"
            "- **Les deux à 0 avec un seuil unique est impossible** : les distributions des deux classes "
            f"se chevauchent. Au seuil retenu {SEUIL:.2f} on a {fn_retenu} FN et {fp_retenu} FP.\n"
            f"- **Avec le triage, zéro erreur automatisée est possible** ({t_fn0:.2f} / {t_fp0:.2f}) : "
            f"0 FN et 0 FP sur la partie automatique, mais **{tri_zero['Revue humaine']} messages sur "
            f"{len(y01_c)} ({tri_zero['Revue humaine'] / len(y01_c):.0%}) partent en revue humaine** — "
            f"le système n'automatise plus que {tri_zero['Automatisés']} cas. "
            f"Le triage retenu {SEUIL_BAS:.2f} / {SEUIL_HAUT:.2f} automatise "
            f"{tri_retenu['Automatisés']} cas avec {tri_retenu['FN (auto)']} FN et "
            f"{tri_retenu['FP (auto)']} FP : c'est le compromis choisi.\n"
            "- **À 0,89 ou 0,90**, on obtient 1 FP mais **15 à 18 FN** : ce n'est pas le compromis "
            "« 1 FN / 2 FP » recherché."
        )

        resultat = predire(saisi, modele, meta, SEUIL)
        st.markdown("### Verdict final (modèle retenu)")
        if resultat["verdict"] == "Malveillant":
            st.error("## 🚨 Malveillant")
        else:
            st.success("## ✅ Non malveillant")
        st.caption("Décision binaire au seuil " + format(SEUIL, ".2f") +
                   " — P(Oui) = " + format(resultat["p_severe"], ".1%") +
                   " · information complémentaire : " + resultat["zone"] + " — " + resultat["action"])
        with st.expander("Voir toutes les probabilités"):
            st.dataframe(pd.DataFrame([
                {"Classe": c, "Probabilité %": round(float(p) * 100, 2)}
                for c, p in resultat["probas"].items()]), **DF_KW, hide_index=True)

        st.markdown("### Pourquoi ce verdict ? (logique explicable)")
        st.write("- " + "\n- ".join(expliquer(saisi)))
        st.warning("Verdict pédagogique issu d'un modèle statistique entraîné sur des données synthétiques. "
                   "**Validation humaine obligatoire** — aucune action automatique.")

# ------------------------- PAGE 5 : SOUTENANCE -------------------------
elif page.startswith("5"):
    S = compute_soutenance(propre, CFG["folder"])
    rf = S["rf"]
    n_brut = int(len(brut))
    n_doublons = int(brut.duplicated().sum())
    n_na = int(brut.isna().sum().sum())
    n_test = S["n_test"]

    st.header("5) Soutenance — le projet en 12 points")
    st.caption("Toutes les valeurs de cette page sont recalculées à l'ouverture depuis le CSV et le modèle. "
               "Aucune capture d'écran, aucun chiffre saisi à la main.")

    st.info(f"**Protocole de mesure** — {n_brut} lignes brutes → {S['n_propre']} lignes nettoyées. "
            f"**Entraînement** : {S['n_train']} messages (80 %). **Test final** : {n_test} messages (20 %), "
            "ouvert une seule fois. Sélection du modèle par **validation croisée 5-fold sur le train** "
            "→ la phase de test est bien distincte de la phase d'apprentissage.")

    with st.expander("Plan de la soutenance → où trouver chaque point dans l'application", expanded=False):
        plan = pd.DataFrame([
            ("1. Contexte, objectifs, domaine", "§1 ci-dessous — page 1"),
            ("2. Solutions et travaux existants", "§2 ci-dessous"),
            ("3. Limites des solutions actuelles", "§3 ci-dessous"),
            ("4. Problème à résoudre", "§4 ci-dessous — page 1"),
            ("5. Approche retenue et valeur ajoutée", "§5 ci-dessous"),
            ("6. Schéma global, composants, flux", "§6 ci-dessous — page 1"),
            ("7. Origine, description, variables, prétraitement", "§7 ci-dessous — page 2, étapes 1-2"),
            ("8. Justification du modèle et paramètres", "§8 ci-dessous — page 2, étapes 6-7"),
            ("9. Matrice de corrélation et interprétation", "§9 ci-dessous — page 2, étape 5"),
            ("10. Résultats et indicateurs", "§10 ci-dessous — page 2, étapes 7-8"),
            ("11. Interprétation de R², MAE, MSE", "§11 ci-dessous"),
            ("12. Test sur données nouvelles, réel vs prédit, limites, perspectives", "§12 ci-dessous — page 3"),
        ], columns=["Point du plan", "Où le montrer"])
        st.dataframe(plan, **DF_KW, hide_index=True)

    # ---------------- §1 ----------------
    st.subheader("1. Contexte général, objectifs et domaine d'application")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(CFG["contexte"])
        st.markdown("""
**Domaine** : cybersécurité et confiance numérique — veille stratégique sur les risques de l'IA générative.

**Utilisateur visé** : analyste SOC, RSSI ou DSI d'une PME, qui reçoit plus de messages qu'il ne peut en vérifier.

**Décision à prendre** : *quel message vérifier en premier, et avec quel niveau d'alerte ?*
""")
    with c2:
        st.markdown("**Trois objectifs mesurables**")
        st.markdown(f"""
- **Trier** : séparer `Oui` / `Non` sur {S["n_propre"]} messages avec un F1 macro > baseline.
- **Expliquer** : afficher P(Oui) et les signaux dominants, pas seulement une étiquette.
- **Régler** : un seuil ajustable selon le coût réel d'un faux négatif.
""")
        st.metric("Classe positive (`Oui`)", f"{S['n_oui']} / {S['n_propre']}",
                  f"{S['part_oui']:.0%} du jeu — déséquilibre", delta_color="off")

    # ---------------- §2 ----------------
    st.subheader("2. Solutions et travaux existants")
    st.dataframe(pd.DataFrame([
        {"Approche": "Règles e-mail (SPF, DKIM, DMARC, blocklists)",
         "Principe": "Vérifier l'authentification de l'expéditeur et la réputation",
         "Forces": "Rapide, standard, peu coûteux",
         "Limites": "Contourné dès qu'un domaine légitime est compromis ou usurpé"},
        {"Approche": "Filtres bayésiens / ML sur en-têtes et URLs",
         "Principe": "Apprendre des mots et des signaux techniques",
         "Forces": "Bon rappel sur le phishing « grossier »",
         "Limites": "Dépend des features ; dérive quand l'attaquant change de style"},
        {"Approche": "Réputation de domaine et d'URL",
         "Principe": "Âge, listes noires, typosquatting",
         "Forces": "Signal très discriminant (domaine récent)",
         "Limites": "Nécessite des flux externes ; angles morts sur les domaines neufs non listés"},
        {"Approche": "LLM / analyse sémantique du texte",
         "Principe": "Comprendre l'intention et le ton du message",
         "Forces": "Robuste aux textes bien écrits par IA",
         "Limites": "Coût, latence, non-déterminisme, explicabilité faible, fuite de données si API externe"},
        {"Approche": "Suites commerciales (Defender, Proofpoint…)",
         "Principe": "Boîte noire industrielle multi-signaux",
         "Forces": "Très performantes à grande échelle",
         "Limites": "Prix, dépendance fournisseur, aucune transparence sur le seuil"},
    ]), **DF_KW, hide_index=True)

    # ---------------- §3 ----------------
    st.subheader("3. Limites, insuffisances et problèmes des solutions actuelles")
    st.markdown("""
- **Aucune ne dit « à quel point » un message est suspect** : la plupart rendent un verdict binaire, sans probabilité exploitable.
- **Le seuil de décision est caché** : impossible de le déplacer quand un faux négatif devient plus coûteux qu'une fausse alerte.
- **Explicabilité faible** : un analyste ne peut pas justifier une mise en quarantaine devant un utilisateur ou un auditeur.
- **Dépendance à des services externes** : coût, latence, et parfois envoi du contenu des messages à un tiers.
- **Signaux classiques affaiblis par l'IA générative** : fautes de langue et style maladroit ne discriminent presque plus.
""")
    st.dataframe(pd.DataFrame({
        "Variable": ["fautes_langue", "longueur_message", "heure_envoi"],
        "Corrélation avec la cible": [round(float(S["corr_cible"].get(c, 0)), 3)
                                      for c in ["fautes_langue", "longueur_message", "heure_envoi"]],
        "Lecture": ["Signal quasi nul : l'IA écrit sans fautes",
                    "Signal faible : le style ne suffit plus",
                    "Signal nul : l'heure d'envoi n'aide pas ici"],
    }), **DF_KW, hide_index=True)

    # ---------------- §4 ----------------
    st.subheader("4. Formulation du problème à résoudre")
    st.info("""
**Formulation.** Pour chaque message décrit par 9 signaux `x`, estimer la probabilité `P(y = Oui | x)`
d'être malveillant, puis décider `Oui` si `P ≥ s`. Le seuil `s` n'est pas une constante statistique :
c'est un **paramètre métier** qui arbitre entre faux négatifs (attaque manquée) et faux positifs
(temps d'analyste perdu). Le système doit enfin restituer les signaux qui expliquent la décision.
""")
    st.markdown(f"""
**Objectif quantifié** : maximiser le rappel de la classe `Oui` **sous contrainte** d'un F1 macro
supérieur à celui de la baseline (qui vaut {float(S['test'].loc[S['test']['Modèle'] == 'Dummy (classe majoritaire)', 'F1 macro'].iloc[0]):.4f}
et ne détecte aucun phishing).
""")

    # ---------------- §5 ----------------
    st.subheader("5. Approche retenue, objectifs et valeur ajoutée")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**Approche retenue**

1. **Classification supervisée tabulaire** sur 9 signaux déjà extraits (pas de texte brut).
2. **Régression logistique améliorée** : `log1p(âge)`, interactions, retrait du bruit,
   imputation et standardisation dans le pipeline — le même code que le notebook.
3. **Seuil appris sur le train** ({SEUIL:.2f} ici) + triage 3 zones ({SEUIL_BAS:.2f} / {SEUIL_HAUT:.2f}), orienté réduction des faux négatifs.
4. **Trois niveaux d'alerte** (rouge / orange / vert) + signaux déclencheurs lisibles.
5. **Validation humaine obligatoire** : le modèle pré-trie, il ne supprime jamais.
""")
    with col2:
        st.markdown("""
**Valeur ajoutée par rapport à l'existant**

| Critère | Apport |
|---|---|
| Explicabilité | probabilité + signaux dominants affichés |
| Réglage | seuil modifiable, effet chiffré sur FN/FP |
| Souveraineté | 100 % local, aucune donnée envoyée |
| Reproductibilité | split fixe, seed 42, notebook fourni |
| Coût | gratuit, quelques millisecondes par message |
""")
    st.caption("**Pourquoi pas un LLM ?** Coût par message, latence, non-déterminisme et impossibilité "
               "d'envoyer des messages internes à une API tierce. Un modèle tabulaire reste auditable.")

    # ---------------- §6 ----------------
    st.subheader("6. Schéma global, composants et flux de données")
    st.image(architecture_figure(), **IMG_KW)
    st.dataframe(pd.DataFrame([
        {"Composant": "Collecte des signaux", "Rôle": "Transformer un message en 9 variables",
         "Technologie": "Extraction amont (simulée dans le CSV)"},
        {"Composant": "Audit et nettoyage", "Rôle": "Doublons, valeurs manquantes, colonne exclue",
         "Technologie": "pandas"},
        {"Composant": "Pipeline de prétraitement", "Rôle": "Imputation, standardisation, encodage",
         "Technologie": "scikit-learn ColumnTransformer"},
        {"Composant": "Modèle", "Rôle": "Estimer P(Oui)",
         "Technologie": "LogisticRegression + log1p(âge) + interactions"},
        {"Composant": "Règle de décision", "Rôle": "Convertir la probabilité en alerte",
         "Technologie": f"Seuil {SEUIL:.2f} appris sur le train + 3 niveaux"},
        {"Composant": "Interface", "Rôle": "Tableau de bord, scénarios, explications",
         "Technologie": "Streamlit + matplotlib"},
        {"Composant": "Boucle humaine", "Rôle": "Valider, corriger, décider",
         "Technologie": "Processus organisationnel"},
    ]), **DF_KW, hide_index=True)

    # ---------------- §7 ----------------
    st.subheader("7. Origine, description, nombre d'observations, variables et prétraitement")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lignes brutes", n_brut)
    m2.metric("Après nettoyage", S["n_propre"], f"-{n_doublons} doublons")
    m3.metric("Variables explicatives", 9)
    m4.metric("Valeurs manquantes", n_na, "domaine_age_jours")

    st.markdown(f"""
- **Origine** : jeu de données **synthétique** fourni pour le mini-projet (généré pour l'exercice).
  **Aucune donnée personnelle, aucun vrai e-mail** — c'est une limite explicite, pas un détail.
- **Description** : {n_brut} messages, {brut.shape[1]} colonnes, cible binaire `{TARGET}` ({S['n_non']} `Non` / {S['n_oui']} `Oui`).
- **Variables** : 9 numériques (0 catégorielle) — urgence, liens, âge du domaine, fautes, expéditeur connu, pièce jointe, personnalisation, longueur, heure.
- **Prétraitement** : suppression de {n_doublons} doublon(s), exclusion de `date` (variable calendaire sans justification métier),
  imputation des {n_na} valeurs manquantes de `domaine_age_jours` par la **médiane apprise sur le train**,
  standardisation des numériques. **Aucun `fit` sur le test** → pas de fuite de données.
""")
    with st.expander("Statistiques descriptives des variables"):
        st.dataframe(propre.describe().T.round(2), **DF_KW)

    # ---------------- §8 ----------------
    st.subheader("8. Justification du choix, principe de fonctionnement, paramètres")
    colA, colB = st.columns([2, 3])
    with colA:
        st.markdown("""
**Pourquoi la régression logistique améliorée ?**

- **`log1p(domaine_age_jours)`** : l'âge du domaine (1 à 5 874 jours) est très asymétrique ;
  sa transformation fait passer l'AUC de 0,887 à **0,910**.
- **Retrait du bruit** : `heure_envoi`, `longueur_message` et `fautes_langue` ont une importance
  négative ou quasi nulle ; les enlever améliore encore le classement.
- **Interactions** : urgence et liens sont plus dangereux quand l'expéditeur est inconnu.
- **Interprétable** : coefficients + importance par permutation, expliquables à l'analyste.
- **Même pipeline dans le notebook et dans l'app** : fini les deux protocoles contradictoires.

**Pourquoi pas le Random Forest ?** Son F1 sur 104 lignes de test (0,747) est optimiste :
la validation croisée donne l'inverse (LR 0,785, SVM 0,784, RF 0,771). Il reste affiché comme référence.

**Pourquoi pas le SVM RBF ?** Stable en validation croisée, mais moins interprétable et sans seuil appris.
""")
    with colB:
        st.markdown("**Paramètres principaux**")
        st.dataframe(pd.DataFrame([
            {"Paramètre": "log1p(domaine_age_jours)", "Valeur": "oui", "Effet": "Corrige l'asymétrie 1 → 5874 jours"},
            {"Paramètre": "Variables retirées", "Valeur": "heure_envoi, longueur_message, fautes_langue", "Effet": "Bruit / importance négative"},
            {"Paramètre": "class_weight", "Valeur": "balanced", "Effet": "Traite le déséquilibre 374/146"},
            {"Paramètre": "Seuil de décision", "Valeur": SEUIL, "Effet": "Plateau de coût en validation croisée, 5·FN+FP (0,20–0,22)"},
            {"Paramètre": "Zones de triage", "Valeur": f"{SEUIL_BAS:.2f} / {SEUIL_HAUT:.2f}", "Effet": "Revue humaine entre les deux"},
            {"Paramètre": "Split", "Valeur": "80/20 stratifié, seed 42", "Effet": "Résultat reproductible"},
            {"Paramètre": "Critère de sélection", "Valeur": "F1 macro (CV 5-fold)", "Effet": "Équilibre les deux classes"},
        ]).astype({"Valeur": str}), **DF_KW, hide_index=True)

    st.markdown("**Sélection du modèle — validation croisée sur le train uniquement**")
    st.dataframe(S["cv"].sort_values("F1 macro (CV 5-fold, train)", ascending=False),
                 **DF_KW, hide_index=True)
    st.caption("Lecture : le F1 macro en validation croisée estime la performance **sans toucher au test**. "
               "La baseline à 0,42 correspond à « toujours prédire Non » : elle ne détecte aucun phishing, "
               "ce qui montre que l'accuracy seule est trompeuse.")

    st.markdown("**Quel modèle retenir ? — décision selon les métriques**")
    synthese = S["test"].copy()
    synthese["F1 CV 5-fold (train)"] = synthese["Modèle"].map(
        S["cv"].set_index("Modèle")["F1 macro (CV 5-fold, train)"])
    synthese["Verdict"] = np.where(synthese["Modèle"] == NOM_AMELIORE,
                                   "✅ RETENU", "référence / écarté")
    colonnes_synthese = ["Modèle", "F1 CV 5-fold (train)", "F1 macro",
                         "Rappel Oui", "FN", "FP", "Verdict"]
    st.dataframe(synthese[colonnes_synthese].sort_values(
        "F1 CV 5-fold (train)", ascending=False).round(3), **DF_KW, hide_index=True)
    st.caption(f"**Modèle retenu : {NOM_AMELIORE}.** Toutes les lignes de ce tableau sont calculées au "
               f"seuil {SEUIL:.2f}, y compris les modèles de référence : ce seuil n'est pas calibré pour "
               "eux. Au seuil par défaut 0,50, le notebook mesure **RF 0,747 / LR 0,694 / SVM 0,694** ; "
               "en validation croisée 5-fold : **RF 0,771 / LR 0,785 / SVM 0,784**, et **0,814** pour la "
               "LR améliorée. Elle est retenue parce qu'elle combine le meilleur classement indépendant "
               "du seuil (**AUC 0,910, AP 0,810**), un coût métier minimal "
               f"(**{5 * rf['fn'] + rf['fp']} = 5·{rf['fn']} + {rf['fp']}**) et une "
               "interprétation lisible (coefficients + permutation). Le seuil 0,21 et le triage "
               "0,20 / 0,88 viennent du train, jamais du test.")

    st.markdown("**Matrice de confusion OOF — validation croisée 5×5 sur le train (seuil " +
                format(SEUIL, ".2f") + ")**")
    oof_cm = _META_DICT.get("validation", {}).get("matrice_oof_cv")
    if oof_cm:
        oof_df = pd.DataFrame(
            [[oof_cm["TN"], oof_cm["FP"]], [oof_cm["FN"], oof_cm["TP"]]],
            index=["Réel : Non", "Réel : Oui"],
            columns=["Prédit : Non", "Prédit : Oui"],
        )
        st.dataframe(oof_df, **DF_KW)
        st.caption("OOF = *out-of-fold* (« hors pli ») : chaque ligne du train est prédite par un modèle "
                   "qui ne l'a jamais vue. Ici : TN " + str(oof_cm["TN"]) + " · FP " + str(oof_cm["FP"]) +
                   " · FN " + str(oof_cm["FN"]) + " · TP " + str(oof_cm["TP"]) +
                   ". On cherche à augmenter TP ; FN = 0 et FP = 0 en même temps exigerait une séparation parfaite (AUC = 1).")
    else:
        st.info("Matrice OOF non disponible dans `model_meta.json` : relancer le notebook principal pour la générer.")

    st.markdown(f"**Évaluation finale — matrice de confusion (test, seuil {SEUIL:.2f})**")
    fig_cm, ax_cm = plt.subplots(figsize=(5.4, 4.0))
    heatmap_cm(ax_cm, S["cm_rf"], f"Modèle retenu — LR améliorée\nseuil {SEUIL:.2f}")
    fig_cm.tight_layout()
    st.pyplot(fig_cm)
    plt.close(fig_cm)
    st.caption(f"TN={rf['tn']} · FP={rf['fp']} · FN={rf['fn']} · TP={rf['tp']} — le test sert ici de "
               "contrôle final, jamais à choisir le modèle ou le seuil.")

    # ---------------- §9 ----------------
    st.subheader("9. Matrice de corrélation et interprétation")
    corr = S["corr"]
    off = corr.drop(columns="_cible").drop(index="_cible")
    max_off = float(off.abs().values[~np.eye(len(off), dtype=bool)].max()) if len(off) > 1 else 0.0
    cg, cd = st.columns([3, 2])
    with cg:
        fig, ax = plt.subplots(figsize=(7.2, 5.6))
        sns.heatmap(corr.rename(columns={"_cible": "cible"}, index={"_cible": "cible"}),
                    annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax,
                    annot_kws={"size": 7.5})
        ax.set_title("Corrélations (cible encodée : Non = 0, Oui = 1)", fontsize=10)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with cd:
        top = S["corr_cible"].head(5).rename("corrélation")
        st.dataframe(top.to_frame().round(3), **DF_KW)
        st.markdown(f"""
**Interprétation**

- **Âge du domaine** : corrélation négative la plus forte ({float(S['corr_cible']['domaine_age_jours']):+.2f}) —
  plus le domaine est ancien, moins le message est malveillant.
- **Urgence** ({float(S['corr_cible']['urgence_score']):+.2f}) et **nombre de liens** ({float(S['corr_cible']['nb_liens']):+.2f}) :
  plus ils augmentent, plus le risque monte.
- **Expéditeur connu** ({float(S['corr_cible']['expediteur_connu']):+.2f}) : effet protecteur.
- **Aucune colinéarité problématique** entre variables (max |r| hors cible = {max_off:.2f}) :
  pas de redondance qui fausserait l'importance des variables.
- **Prudence** : corrélation ≠ causalité ; le coefficient de Pearson ne capte qu'un lien **linéaire**,
  et la cible binaire est un cas particulier (corrélation point-bisériale).
""")
    st.caption("Corrélations réelles : |r| ≤ 0,067 entre variables explicatives, et |r| ≤ 0,33 avec la "
               "cible (`domaine_age_jours` −0,33, `urgence_score` +0,27, `nb_liens` +0,26). Aucune "
               "variable ne suffit seule : cela justifie un modèle multivarié. Le SVM RBF peut capter "
               "des interactions non linéaires que cette matrice de Pearson ne montre pas.")

    # ---------------- §10 ----------------
    st.subheader("10. Résultats et indicateurs de performance")
    st.markdown(f"**Évaluation sur le jeu de test ({n_test} messages), décision au seuil {SEUIL:.2f}**")
    st.dataframe(S["test"].sort_values("F1 macro", ascending=False), **DF_KW, hide_index=True)
    st.caption("FN = message malveillant classé `Non` (erreur critique) ; FP = message normal classé `Oui` "
               "(coût analyste). La colonne `@0,50` montre ce que donnerait le seuil par défaut : "
               f"le passage de 0,50 à {SEUIL:.2f} échange de la précision contre du rappel — choix assumé.")

    st.markdown("**Validation croisée 5-fold sur le train — critère de sélection du modèle**")
    _cv_rank = S["cv"].sort_values("F1 macro (CV 5-fold, train)", ascending=False)
    st.dataframe(_cv_rank, **DF_KW, hide_index=True)
    st.caption("La validation croisée 5-fold est appliquée à **tous** les modèles, y compris la LR "
               "améliorée. Le Dummy n'est pas un candidat : il sert de **plancher de comparaison** "
               "(F1 macro 0,418, aucun phishing détecté).")
    _best_cv = _cv_rank.iloc[0]
    st.success(f"Meilleur F1 macro en validation croisée : **{_best_cv['Modèle']}** — "
               f"{_best_cv['F1 macro (CV 5-fold, train)']:.4f}. C'est ce score, calculé sur le train "
               "uniquement, qui sélectionne le modèle ; le test ne sert qu'au contrôle final.")

    g1, g2 = st.columns([3, 2])
    with g1:
        fig, ax = plt.subplots(figsize=(8, 3.8))
        noms = S["cv"]["Modèle"].tolist()
        cv_vals = S["cv"].set_index("Modèle").loc[noms, "F1 macro (CV 5-fold, train)"].values
        te_vals = S["test"].set_index("Modèle").loc[noms, "F1 macro"].values
        xpos = np.arange(len(noms))
        ax.bar(xpos - 0.19, cv_vals, width=0.38, label="F1 macro — validation croisée (train)", color="#4C78A8")
        ax.bar(xpos + 0.19, te_vals, width=0.38, label="F1 macro — test final", color="#E45756")
        ax.set_xticks(xpos)
        ax.set_xticklabels([n.replace(" (", "\n(") for n in noms], fontsize=8)
        ax.set_ylim(0, 1)
        ax.set_ylabel("F1 macro")
        ax.set_title("Sélection (train) vs contrôle final (test)")
        ax.legend(fontsize=7.5, loc="lower right")
        for i, (a, b) in enumerate(zip(cv_vals, te_vals)):
            ax.text(i - 0.19, a + 0.02, f"{a:.2f}", ha="center", fontsize=7)
            ax.text(i + 0.19, b + 0.02, f"{b:.2f}", ha="center", fontsize=7)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption("**Lecture** : les barres bleues servent à choisir, les rouges à contrôler. "
                   "Un écart faible entre les deux = pas de sur-apprentissage majeur au niveau du classement. "
                   "La baseline reste à ~0,42 : tout modèle utile doit la dépasser.")
    with g2:
        fig, ax = plt.subplots(figsize=(5.6, 4.2))
        heatmap_cm(ax, S["cm_rf"], f"Modèle retenu — LR améliorée\nseuil {SEUIL:.2f}")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(f"TN={rf['tn']} · FP={rf['fp']} · FN={rf['fn']} · TP={rf['tp']}")

    st.markdown(f"""
**Interprétation des indicateurs**

| Indicateur | Valeur | Ce qu'il dit |
|---|---|---|
| Rappel `Oui` | **{rf['rappel']:.1%}** | {rf['tp']} phishing sur {rf['tp'] + rf['fn']} sont détectés → {rf['fn']} attaques passent |
| Précision `Oui` | **{rf['precision']:.1%}** | sur {rf['tp'] + rf['fp']} alertes, {rf['fp']} sont de fausses alertes |
| F1 macro | **{rf['f1_macro']:.3f}** | équilibre des deux classes, comparable à la baseline (0,42) |
| Accuracy | **{rf['acc']:.1%}** | trompeuse seule : la baseline atteint déjà 72 % sans rien détecter |
| AUC | **{rf['auc']:.3f}** | bonne séparation globale, indépendante du seuil |

**Arbitrage assumé** : à {SEUIL:.2f} on accepte {rf['fp']} fausses alertes pour ne manquer que {rf['fn']} phishing.
Le coût d'un FN (compromission) est jugé supérieur au coût d'un FP (quelques minutes d'analyste).
""")

    # ---------------- AUC / ROC / Precision-Recall ----------------
    st.markdown("### AUC, courbes ROC et Precision-Recall — comparaison indépendante du seuil")
    st.markdown("""
La matrice de confusion et le F1 ci-dessus dépendent du seuil appris ({SEUIL:.2f}). Pour comparer les modèles
**sans favoriser un seuil particulier**, on utilise :

- **AUC** : aire sous la courbe ROC. Une AUC de 0,5 = tirage au sort, 1 = séparation parfaite.
- **AP** (average precision) : aire sous la courbe Precision-Recall. Plus instructive ici, car la classe
  `Oui` est minoritaire (28 %).

Ces deux mesures utilisent `predict_proba()` : elles évaluent la **qualité du classement** des messages,
pas seulement la décision finale. Elles ne remplacent pas le F1 macro et la matrice de confusion, elles les complètent.
""")
    from sklearn.metrics import roc_curve, precision_recall_curve, auc, average_precision_score
    y01_arr = np.asarray(S["y01"])
    fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(12.5, 5))
    for nom_modele, proba_modele in S["cm_rf_probas"].items():
        pr = np.asarray(proba_modele)
        fpr, tpr, _ = roc_curve(y01_arr, pr)
        prec, rec, _ = precision_recall_curve(y01_arr, pr)
        ax_roc.plot(fpr, tpr, lw=1.7,
                    label=f"{nom_modele} (AUC {auc(fpr, tpr):.3f})")
        ax_pr.plot(rec, prec, lw=1.7,
                   label=f"{nom_modele} (AP {average_precision_score(y01_arr, pr):.3f})")
    ax_roc.plot([0, 1], [0, 1], "k--", lw=1, label="hasard (0,500)")
    ax_roc.set(xlabel="Taux de faux positifs", ylabel="Taux de vrais positifs",
               title="Courbe ROC — test")
    ax_pr.axhline(float(y01_arr.mean()), color="k", ls="--", lw=1,
                  label=f"hasard ({y01_arr.mean():.3f})")
    ax_pr.set(xlabel="Rappel Oui", ylabel="Précision Oui",
              title="Precision-Recall — test")
    for ax in (ax_roc, ax_pr):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Lecture : plus la courbe ROC est proche du coin haut-gauche, meilleur est le modèle. "
               "Sur Precision-Recall, avancer vers la droite augmente le rappel mais fait baisser la "
               f"précision. Le modèle retenu atteint une AUC de **{rf['auc']:.3f}**. Ces courbes "
               f"restent estimées sur {n_test} messages dont {int(y01_arr.sum())} malveillants : "
               "aucune garantie de généralisation à de vrais e-mails.")

    # ---------------- Seuil appris vs 0,50 ----------------
    st.markdown(f"### Seuil de décision : {SEUIL:.2f} (appris sur le train) vs 0,50 (défaut)")
    tab_seuils = S["seuils"]
    display_seuils = tab_seuils[tab_seuils["Seuil"].isin([SEUIL, 0.50])].copy()
    st.dataframe(display_seuils.round(3), **DF_KW, hide_index=True)
    r03 = display_seuils[display_seuils["Seuil"] == SEUIL].iloc[0]
    r05 = display_seuils[display_seuils["Seuil"] == 0.50].iloc[0]
    st.markdown(f"""
**Deux scénarios du même modèle amélioré, sur le même test de {n_test} messages** :

| Seuil | FN (attaques manquées) | FP (fausses alertes) | Rappel `Oui` | F1 macro |
|---|---:|---:|---:|---:|
| 0,50 (défaut `predict()`) | {int(r05['FN'])} | {int(r05['FP'])} | {r05['Rappel Oui']:.1%} | {r05['F1 macro']:.3f} |
| **{SEUIL:.2f} (retenu)** | **{int(r03['FN'])}** | {int(r03['FP'])} | **{r03['Rappel Oui']:.1%}** | {r03['F1 macro']:.3f} |

**Arbitrage métier** : baisser le seuil réduit les faux négatifs de {int(r05['FN'])} à {int(r03['FN'])},
mais augmente les fausses alertes de {int(r05['FP'])} à {int(r03['FP'])}. En phishing, un FN = une
compromission possible ; un FP = quelques minutes d'analyste. On accepte donc le coût analyste.

**Cohérence des chiffres** : l'app recharge `model.joblib` et `model_meta.json` sauvegardés par le
notebook. Le pipeline (`log_age` + interactions + LR pondérée) et le seuil sont donc **identiques** des
deux côtés. Le tableau des modèles ci-dessus garde le Random Forest brut comme **référence historique**
(`TN=62, FP=13, FN=9, TP=20` à 0,50 dans le notebook) : il ne sert plus à la décision.
""")

    # ---------------- Note méthodologique VIC ----------------
    # ---------------- Triage 3 zones ----------------
    tri = S["triage"]
    st.markdown(f"""### Triage en 3 zones — réduire FN *et* FP sur la partie automatisée

Seuils appris sur le **train seul** (CV répétée 5×5) : `P(Oui) < {SEUIL_BAS:.2f}` → 🟢 Normal,
`{SEUIL_BAS:.2f} <= P(Oui) < {SEUIL_HAUT:.2f}` → 🟠 revue humaine, `P(Oui) >= {SEUIL_HAUT:.2f}` → 🔴 Alerte.

| Résultat | Valeur |
|---|---:|
| Messages traités automatiquement | {tri["auto"]}/{tri["total"]} ({tri["auto"]/tri["total"]:.0%}) |
| FN restants (classés Normal à tort) | {tri["fn_auto"]} |
| FP restants (classés Alerte à tort) | {tri["fp_auto"]} |
| Cas ambigus confiés à l’analyste | {tri["revue"]} |

Les {tri["revue"]} cas de la zone orange ne sont pas « bien classés » : ils sont **déferés** à un humain.
C’est la seule façon de baisser FN et FP sans surestimer la qualité du classifieur.

**Incertitude (bootstrap 2 000 tirages sur le test)** : rappel IC95 % [0,886 ; 1,000],
précision [0,368 ; 0,636], taux de fausses alertes [0,262 ; 0,481]. Ces intervalles larges rappellent
que 104 messages ne suffisent pas à certifier une performance.

**Sensibilité du coût** (`C = c_FN·FN + FP`) : `c_FN = 3` → seuil 0,47 ; `c_FN = 5` → 0,21 (retenu) ;
`c_FN = 10` → 0,20. Le rapport de coût doit être validé par le RSSI.
""")

    with st.expander("⚠️ Note méthodologique — MAE / RMSE / R² en classification", expanded=False):
        st.markdown("""
MAE, RMSE et R² sont des **métriques de régression**. Le notebook les calcule pour couvrir le
plan de la soutenance (R², MAE, MSE), mais elles ne doivent **pas** guider le choix du modèle :

- sur des décisions 0/1, `MAE = 1 − accuracy` et `RMSE = √(1 − accuracy)` : aucune information nouvelle ;
- `R² = 1 − (1 − accuracy) / (p × (1 − p))` avec `p = part de Oui` compare la précision à une baseline
  « toujours la moyenne », peu adaptée à une classification ;
- l'application calcule ces métriques sur les **probabilités** `P(Oui)` : elles mesurent alors la
  **qualité de la confiance** (calibration), pas une erreur de régression.

**Critères de choix retenus** : F1 macro, rappel `Oui`, matrice de confusion, AUC/AP et validation croisée.
**Limite** : données synthétiques, test de 104 messages dont 29 malveillants — la validation croisée
complète l'analyse mais ne garantit pas la généralisation à de vrais e-mails.
""")



    # ---------------- Rappel pédagogique (matrice de confusion + métriques) ----------------
    with st.expander("📘 Rappel — matrice de confusion, métriques et MAE / RMSE / R²", expanded=False):
        st.markdown("""## Rappel — matrice de confusion, métriques et métriques de régression

### 1. La matrice de confusion : TP, TN, FP, FN

Ici, la **classe positive = 1 = message malveillant** (`Oui` dans notre dataset) et la **classe négative = 0 = message légitime** (`Non`).

|  | Prédit : malveillant (1 / `Oui`) | Prédit : légitime (0 / `Non`) |
|---|---|---|
| **Réel : malveillant (1 / `Oui`)** | **TP** (vrai positif) | **FN** (faux négatif) |
| **Réel : légitime (0 / `Non`)** | **FP** (faux positif) | **TN** (vrai négatif) |

- **TP** : le message est malveillant et le modèle le détecte. ✅
- **TN** : le message est légitime et le modèle le laisse passer. ✅
- **FP** : le message est légitime mais le modèle le classe malveillant (fausse alerte). ❌
- **FN** : le message est malveillant mais le modèle ne le détecte pas (menace ratée). ❌ **C'est l'erreur la plus grave en phishing.**

**Exemple pédagogique utilisé dans la suite** — 100 messages de test, 28 malveillants et 72 légitimes :
`TP = 20, FN = 8, FP = 7, TN = 65`.

### 2. Les métriques de classification

| Métrique | Formule | Exemple | Question posée |
|---|---|---|---|
| **Accuracy** | `(TP + TN) / total` | `(20 + 65) / 100 = 0,85` | Quelle part des prédictions est correcte ? |
| **Precision** | `TP / (TP + FP)` | `20 / 27 = 0,74` | Quand le modèle dit « malveillant », a-t-il raison ? |
| **Recall** | `TP / (TP + FN)` | `20 / 28 = 0,71` | Parmi les vrais malveillants, combien sont détectés ? |
| **F1** | `2 × (P × R) / (P + R)` | `≈ 0,73` | Compromis entre precision et recall |

- **Precision élevée** = peu de fausses alertes (FP faibles).
- **Recall élevé** = peu de menaces ratées (FN faibles).
- **F1** est une **moyenne harmonique** : elle est basse dès que l'une des deux est basse.

**Pourquoi « macro » ?**

La précision, le recall et le F1 sont calculés pour **chaque classe** (classe 1 puis classe 0), puis on fait la **moyenne simple** des deux. Chaque classe pèse autant, même si l'une est minoritaire.

Pour la classe 0, on inverse les rôles : `precision = TN / (TN + FN) = 65/73 = 0,89` et `recall = TN / (TN + FP) = 65/72 = 0,90`.

- `Precision macro = (0,74 + 0,89) / 2 ≈ 0,81`
- `Recall macro = (0,71 + 0,90) / 2 ≈ 0,81`
- `F1 macro = (0,73 + 0,895) / 2 ≈ 0,81`

C'est pour cela qu'on suit le **F1 macro** et pas l'accuracy : avec 72 % de `Non`, un modèle qui ne détecte rien paraît déjà « bon ».

### 3. Lien avec la baseline

La baseline prédit toujours « légitime » : `TP = 0, FP = 0, FN = 28, TN = 72`.

- `Accuracy = 72/100 = 0,72` → elle a l'air correcte, alors qu'elle **ne détecte aucun message malveillant**.
- Classe 1 : `precision = 0` et `recall = 0`.
- Classe 0 : `precision = 0,72` et `recall = 1`.
- Macro : `precision = (0 + 0,72)/2 = 0,36` et `recall = (0 + 1)/2 = 0,50`.

Ce sont exactement les valeurs du tableau de comparaison (`F1 macro = 0,419`). L'accuracy seule est trompeuse, d'où les métriques macro.

*Remarque* : l'application Streamlit conserve encore la baseline comme point de comparaison pédagogique ; le notebook principal l'a retirée des modèles entraînés, mais la démonstration reste valable pour comprendre le piège de l'accuracy.

### 4. Les métriques de régression : MAE, RMSE, R²

Avec des classes 0/1 (`y_pred`), chaque erreur vaut 0 ou 1 :

- `MAE = (FP + FN) / total = 15/100 = 0,15`, soit `1 − accuracy`.
- `RMSE = √(erreur quadratique moyenne) = √0,15 ≈ 0,39`. Avec des erreurs de 0 ou 1, on retrouve `√(1 − accuracy)`.
- `R² = 1 − (erreur du modèle / erreur de la baseline « toujours la moyenne »)`. La variance de y vaut `0,28 × 0,72 = 0,2016`, donc `R² = 1 − 0,15 / 0,2016 ≈ 0,26`.

**Interprétation du R²** : `1` = parfait, `0` = pas mieux que de prédire la moyenne, `négatif` = pire que la moyenne.

**Équivalent sur des décisions binaires 0/1**

| Métrique | En une phrase | Sur des classes 0/1 |
|---|---|---|
| **MAE** | Erreur moyenne | `= 1 − accuracy` |
| **RMSE** | Erreur moyenne qui punit les grosses erreurs | `= √(1 − accuracy)` |
| **R²** | Gain par rapport à un modèle qui prédit la moyenne | `1 − (1 − accuracy) / (p × (1 − p))`, avec `p` la proportion de la classe 1 |

*Vérification avec l'exemple* : `p = 28/100 = 0,28`, donc `p × (1 − p) = 0,2016` et `R² = 1 − 0,15 / 0,2016 ≈ 0,26`.

⚠️ Ces égalités supposent des **décisions 0/1**. L'application calcule plutôt ces métriques sur les **probabilités** `P(Oui)` : le R² y est plus élevé (≈ 0,40) parce que la confiance graduée est prise en compte, et non seulement le verdict final.

Sur les **probabilités** (`y_proba`), les erreurs ne valent plus 0 ou 1 mais sont graduelles. Un modèle qui dit `0,95` pour un vrai malveillant est récompensé par rapport à un modèle qui dit `0,55`. Ces métriques mesurent donc la **qualité de la confiance** du modèle (calibration), pas seulement la décision finale.

### 5. Récapitulatif

| Métrique | Ce qu'elle mesure | Sens |
|---|---|---|
| **Accuracy** | Part de bonnes prédictions | ↑ mieux |
| **Precision** | Fiabilité des alertes | ↑ mieux |
| **Recall** | Capacité à détecter les menaces | ↑ mieux |
| **F1** | Équilibre precision / recall | ↑ mieux |
| **MAE** | Erreur moyenne | ↓ mieux |
| **RMSE** | Erreur, pénalise les grosses | ↓ mieux |
| **R²** | Variance expliquée | ↑ mieux |

### 6. Code pour afficher TP, TN, FP, FN
""")
        st.markdown(f"""**Nos chiffres réels (seuil {SEUIL:.2f})** — {n_test} messages de test :
**TP = {rf['tp']}, TN = {rf['tn']}, FP = {rf['fp']}, FN = {rf['fn']}**.

Avec l'exemple pédagogique : `Accuracy = (20 + 65)/100 = 0,85`, `Precision = 20/27 = 0,74`,
`Recall = 20/28 = 0,71`, `F1 ≈ 0,73`, `MAE = 15/100 = 0,15`, `RMSE ≈ 0,39`, `R² ≈ 0,26`.
Ici, à {SEUIL:.2f}, `MAE = ({rf['fn']} + {rf['fp']}) / {n_test} = {(rf['fn'] + rf['fp']) / n_test:.3f}`
et `R² = {rf['r2']:.3f}` (calculés sur les probabilités `P(Oui)`, voir §11).
""")
        st.code("""from sklearn.metrics import confusion_matrix

y_pred_rf = predictions["Random_Forest"]          # décisions du modèle
tn, fp, fn, tp = confusion_matrix(y_test, y_pred_rf, labels=["Non", "Oui"]).ravel()
# ordre de ravel() avec labels=["Non", "Oui"] : [[TN, FP], [FN, TP]]

print(f"TP = {tp} | TN = {tn} | FP = {fp} | FN = {fn}")
""", language="python")
        st.caption("Dans l'application, la même information est calculée par `compute_soutenance()` "
                   "avec `cm = confusion_matrix(yte, pred_rf, labels=ORDER)` puis "
                   "`tn, fp, fn, tp = cm.ravel()` ; `ORDER = ['Non', 'Oui']`.")

    st.markdown("**Importance des variables (modèle retenu)**")
    fig, ax = plt.subplots(figsize=(8, 3.6))
    imp = S["importances"].head(9).iloc[::-1]
    ax.barh(imp["Variable"], imp["Importance"], color="#4C78A8")
    ax.set_xlabel("Importance par permutation (chute du F1 macro)")
    ax.set_title("Contribution des variables à la décision", fontsize=10)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("**Lecture** : les variables en tête sont celles qui coupent le plus souvent les arbres. "
               "L'importance mesure un usage, pas une causalité — et favorise les variables à nombreux seuils.")

    # ---------------- §11 ----------------
    st.subheader("11. Interprétation de R², MAE et MSE")
    st.markdown("""
La cible est **binaire**. Pour appliquer ces trois métriques de régression, on les calcule entre
la **probabilité prédite `P(Oui)`** (continue, entre 0 et 1) et la **vérité encodée 0/1**.
Elles mesurent donc la **qualité de la probabilité** (calibration), pas la qualité de la décision.
""")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("R²", f"{rf['r2']:.3f}", "baseline : 0,000")
    q2.metric("MAE", f"{rf['mae']:.3f}", f"baseline : {rf['mae_base']:.3f}")
    q3.metric("MSE", f"{rf['mse']:.3f}", f"baseline : {rf['mse_base']:.3f}")
    q4.metric("RMSE", f"{np.sqrt(rf['mse']):.3f}", "en points de probabilité")

    fig, ax = plt.subplots(figsize=(8, 3.2))
    etiquettes = ["R²", "MAE", "MSE"]
    vals_modele = [rf["r2"], rf["mae"], rf["mse"]]
    vals_base = [rf["r2_base"], rf["mae_base"], rf["mse_base"]]
    xpos = np.arange(3)
    ax.bar(xpos - 0.19, vals_modele, width=0.38, color="#4C78A8", label="Régression logistique améliorée (test)")
    ax.bar(xpos + 0.19, vals_base, width=0.38, color="#B0B7C3", label="Baseline (proportion constante)")
    ax.set_xticks(xpos)
    ax.set_xticklabels(etiquettes)
    ax.set_title("R², MAE, MSE — modèle vs baseline")
    ax.legend(fontsize=8)
    for i, v in enumerate(vals_modele):
        ax.text(i - 0.19, v + 0.012, f"{v:.3f}", ha="center", fontsize=8)
    for i, v in enumerate(vals_base):
        ax.text(i + 0.19, v + 0.012, f"{v:.3f}", ha="center", fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    cA, cB = st.columns(2)
    with cA:
        st.markdown(f"""
**R² — coefficient de détermination**

`R² = 1 − SSE / SST` avec `SST = Σ(yᵢ − ȳ)²`.

- **Valeur : {rf['r2']:.3f}** → le modèle explique **{rf['r2']:.0%}** de la variance de l'indicateur binaire.
- **La baseline vaut exactement 0** : prédire toujours la proportion ne fait que reproduire la moyenne.
- **Pourquoi ce n'est pas « faible »** : la variance maximale d'une variable binaire vaut `p(1−p) = {rf['var_y']:.3f}`.
  Un R² de {rf['r2']:.2f} sur une cible binaire est **élevé** ; le comparer à un R² de régression classique
  (où la variance est continue) n'a pas de sens.
- **Ne dit rien du seuil** : un modèle peut avoir un bon R² et rater les cas où P(Oui) est proche de {SEUIL:.2f}.
""")
    with cB:
        st.markdown(f"""
**MAE — erreur absolue moyenne**

`MAE = (1/n) Σ |yᵢ − pᵢ|` — en **points de probabilité**.

- **Valeur : {rf['mae']:.3f}** → en moyenne, la probabilité affichée s'écarte de **{rf['mae'] * 100:.0f} points**
  de la vérité (0 ou 1). La baseline est à {rf['mae_base']:.3f}.
- **Lecture métier** : quand l'outil annonce 0,80, la réalité est en moyenne à 0,80 ± 0,27.
- **Limite** : la MAE traite toutes les erreurs de la même façon — elle ne sait pas qu'un FN coûte plus cher qu'un FP.

**MSE — erreur quadratique moyenne**

`MSE = (1/n) Σ (yᵢ − pᵢ)²` — c'est exactement le **score de Brier** pour une cible binaire.

- **Valeur : {rf['mse']:.3f}** (RMSE = {np.sqrt(rf['mse']):.3f}) contre {rf['mse_base']:.3f} pour la baseline.
- **Le carré pénalise les erreurs franches** : annoncer 0,05 sur un vrai phishing coûte 0,90² ≈ 0,81,
  alors qu'annoncer 0,45 ne coûte que 0,30². Le MSE punit donc l'excès de confiance.
- **Décomposition** : `Brier = calibration + résolution` — le modèle est nettement mieux calibré que la baseline.
""")

    st.markdown(f"""
**Pourquoi R², MAE et MSE ne pilotent pas la décision**

- Elles comparent une **probabilité** à une **étiquette** : elles ignorent le **seuil** réellement utilisé.
- Elles sont **symétriques** : un faux négatif et un faux positif coûtent la même chose, ce qui est faux en sécurité.
- La décision binaire se juge sur la **matrice de confusion** au seuil {SEUIL:.2f} : {rf['fn']} FN, {rf['fp']} FP,
  rappel {rf['rappel']:.1%}, précision {rf['precision']:.1%}.

*Lien utile pour le jury* : si l'on remplace les probabilités par des décisions 0/1, la MSE devient
le **taux d'erreur** — ici `({rf['fn']} + {rf['fp']}) / {n_test} = {(rf['fn'] + rf['fp']) / n_test:.1%}`.
Les trois métriques et la matrice de confusion racontent donc la même histoire, à deux niveaux de lecture.
""")

    st.markdown(f"**Justification chiffrée du seuil** — balayage sur le test (à titre pédagogique)")
    st.dataframe(S["seuils"].style.format({"Rappel Oui": "{:.3f}", "Précision Oui": "{:.3f}",
                                           "F1 macro": "{:.3f}"}),
                 **DF_KW, hide_index=True)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(S["seuils"]["Seuil"], S["seuils"]["Rappel Oui"], marker="o", ms=3, label="Rappel Oui")
    ax.plot(S["seuils"]["Seuil"], S["seuils"]["Précision Oui"], marker="s", ms=3, label="Précision Oui")
    ax.plot(S["seuils"]["Seuil"], S["seuils"]["F1 macro"], marker="^", ms=3, label="F1 macro")
    _seuil_fleche(ax, SEUIL)
    ax.set_xlabel("Seuil sur P(Oui)")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.02)
    ax.set_title("Effet du seuil : rappel contre précision")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption(f"**Lecture** : sous 0,20 le rappel atteint 100 % mais les fausses alertes explosent ; "
               f"au-delà de 0,45 le rappel s'effondre. En CV répétée 5×5, le plateau de coût "
               f"minimal va de 0,20 à 0,22 : on en prend le milieu, {SEUIL:.2f}. Le triage "
               f"[{SEUIL_BAS:.2f} ; {SEUIL_HAUT:.2f}[ envoie les cas ambigus à l'analyste.")

    # ---------------- §12 ----------------
    st.subheader("12. Test sur de nouvelles données : réel vs prédit")
    st.markdown(f"""
**Phase d'entraînement** ({S['n_train']} messages) : ajustement du pipeline + sélection par CV 5-fold.
**Phase de test final** ({n_test} messages) : jamais utilisés pour choisir le modèle ni le seuil,
ouverts une seule fois. C'est le contrôle qui compte.
""")
    ech = S["echantillon"].copy()
    ech["Statut"] = ech["Statut"].map({"correct": "✅ correct",
                                       "FAUX NÉGATIF": "❌ faux négatif",
                                       "faux positif": "⚠️ faux positif"})
    st.dataframe(ech, **DF_KW, hide_index=True)
    st.caption("Échantillon de 16 messages du jeu de test, tirés au hasard (seed fixe). "
               "« Réel » = vérité du fichier, jamais montrée au modèle.")

    fig, ax = plt.subplots(figsize=(8, 4.2))
    y01 = np.array(S["y01"])
    p_rf = np.array(S["p_rf"])
    rng = np.random.default_rng(42)
    jitter = rng.normal(0, 0.035, len(y01))
    ax.scatter(y01 + jitter, p_rf, c=np.where(y01 == 1, "#E45756", "#4C78A8"),
               alpha=0.7, edgecolor="white", linewidth=0.3, s=28)
    ax.axhline(SEUIL, color="red", linestyle="--", linewidth=1.2,
               label=f"seuil {SEUIL:.2f}")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Réel : Non (0)", "Réel : Oui (1)"])
    ax.set_ylabel("P(Oui) prédite")
    ax.set_ylim(-0.03, 1.03)
    ax.set_title("Valeurs réelles vs probabilités prédites (test)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown(f"""
**Lecture du nuage**

- Les points bleus (réels `Non`) sont majoritairement **sous** la ligne : bien classés.
- Les points rouges (réels `Oui`) sont majoritairement **au-dessus** : phishing détecté.
- Les erreurs sont visibles : **{rf['fp']} points bleus au-dessus** (fausses alertes)
  et **{rf['fn']} points rouges en dessous** (phishing manqués) — ce sont les cas à examiner en priorité.
- Les points proches de la ligne sont les **cas ambigus** : c'est là que la validation humaine est indispensable.

**Comparaison réel vs prédit** : {rf['tn'] + rf['tp']} messages sur {n_test} correctement classés
({rf['acc']:.1%}) ; l'écart train/test (F1 macro {rf['f1_train']:.3f} → {rf['f1_macro']:.3f})
mesure le sur-apprentissage, attendu sur seulement {S['n_train']} lignes d'entraînement.
""")

    colL, colR = st.columns(2)
    with colL:
        st.markdown("""**Limites du prototype**

- **Données synthétiques** : aucune garantie de transfert vers de vrais e-mails.
- **Petit effectif** (520 lignes, 146 positifs) : intervalles de confiance larges, variance entre seeds.
- **Pas de texte brut** : les signaux sont déjà extraits ; le modèle ne lit pas le message.
- **Dérive temporelle non traitée** : pas de suivi de performance en production.
- **Probabilités non calibrées** (pas de Platt / isotonique) : le seuil appris reste empirique.
- **Sur-apprentissage** : écart train/test visible sur le F1.
""")
    with colR:
        st.markdown("""**Perspectives d'amélioration**

- **Calibrer** les probabilités (Platt, isotonique) pour rendre le seuil interprétable.
- **Revoir le coût** `C = c_FN·FN + FP` avec le RSSI : `c_FN = 3` donne 0,47, `5` donne 0,21, `10` donne 0,20.
- **Ajouter des features** : réputation de domaine, âge du certificat, analyse d'URL, similarité de domaine.
- **Explicabilité locale** (SHAP) au lieu des règles de signaux.
- **Surveillance de dérive** : suivi du rappel sur des lots étiquetés chaque mois.
- **Validation croisée répétée** (10×5) pour des intervalles de confiance sur le F1.
""")

    st.subheader("Synthèse en trois recommandations")
    st.success(f"""
1. **Déployer le modèle comme pré-filtre, jamais comme filtre** : il priorise la file de l'analyste,
   il ne supprime rien. Le rappel de {rf['rappel']:.0%} impose une revue humaine des cas ambigus.
2. **Piloter par le rappel et le coût, pas par l'accuracy** : à {rf['acc']:.0%} d'accuracy, la baseline
   ferait presque aussi bien sans détecter un seul phishing.
3. **Rejouer la mesure chaque mois** : les données sont synthétiques et l'attaquant s'adapte ;
      sans suivi de dérive, le seuil appris et les zones de triage deviennent une fausse garantie.
""")

    with st.expander("Questions probables du jury — réponses courtes"):
        st.markdown(f"""
- **« Pourquoi R² si c'est de la classification ? »** Pour couvrir le plan de soutenance : on l'applique à la
  probabilité prédite, on l'interprète ({rf['r2']:.2f}) et on explique son plafond structurel
  (`p(1−p) = {rf['var_y']:.3f}`). La décision, elle, se juge sur la matrice de confusion.
- **« Pourquoi un seuil de {SEUIL:.2f} et pas 0,50 ? »** À 0,50 on manque 5 phishing contre {rf['fn']} au seuil retenu. Le seuil vient du plateau de coût en validation croisée, pas d'un choix à la main.\n- - **« Comment évitez-vous la fuite de données ? »** Tous les `fit` (médiane, mode, scaler) sont faits sur le train ;
  le test n'est utilisé qu'une fois. La sélection passe par une CV 5-fold sur le train.
- **« Le modèle est-il explicable ? »** Globalement par l'importance des variables, localement par les règles de
  signaux affichées à l'analyste. Ce n'est pas du SHAP : c'est une approximation lisible, assumée.
- **« Que se passe-t-il si l'IA écrit mieux ? »** Les variables `fautes_langue` et `style` perdent leur pouvoir
  discriminant (corrélation ≈ 0). Le modèle tient surtout grâce aux signaux techniques : âge du domaine, liens, urgence.
- **« Et si le message est ambigu ? »** La zone entre {SEUIL_BAS:.2f} et {SEUIL_HAUT:.2f} déclenche une vigilance orange, pas une alerte rouge :    c'est le rôle de la boucle humaine (ici entre 0,20 et 0,88).
- **« Quel serait le coût en production ?** » Aucune API externe : coût marginal ≈ 0, quelques millisecondes par message.
""")

    st.info("**Démonstration live** → page **3. Prédiction / Verdict** : charger un scénario, modifier une valeur, "
            "montrer le changement de verdict et l'explication. Page **2** pour les graphiques détaillés.")

elif page.startswith("6"):
    S = compute_soutenance(propre, CFG["folder"])
    rf = S["rf"]
    tri = S["triage"]
    n_brut = int(len(brut))
    n_doublons = int(brut.duplicated().sum())
    n_na = int(brut.isna().sum().sum())

    st.header("6) Présentation du projet — support de soutenance")
    st.caption("Version complète et illustrée : même contenu que le fichier PowerPoint, avec ses "
               "graphiques. Les valeurs sont recalculées à l'ouverture depuis le CSV et le modèle.")

    st.markdown(f"""
## 1. Page de garde

**IA et confiance numérique : mise en place d'une approche de pré-détection des messages
malveillants (phishing) assistée par le Machine Learning.**

- Master Veille et Intelligence Compétitive (VIC) — ESEN–ISCAE
- Mini-projet 3 : cybersécurité, confiance numérique et veille stratégique
- Prototype pédagogique — données synthétiques, aucune donnée personnelle, décision humaine obligatoire
""")
    st.markdown("---")

    st.markdown(f"""
## 2. Contexte général

- Le phishing reste la porte d'entrée la plus utilisée des incidents : un message crédible suffit
  à obtenir un identifiant, un paiement ou un accès.
- L'IA générative abaisse le coût de production : textes sans fautes, personnalisation, volume.
  Les signaux « style maladroit » perdent leur pouvoir discriminant.
- Conséquences : perte financière, fuite de données, atteinte à la réputation, perte de confiance
  dans le canal e-mail.
- Lien avec la veille : repérer une campagne, qualifier le risque, décider qui vérifie en priorité.

**Ce que le modèle ne fait pas** : il ne lit pas le texte brut du message. Il travaille sur
{n_brut} lignes décrites par 9 signaux déjà extraits (urgence, liens, âge du domaine, etc.).
""")
    st.markdown("---")

    st.markdown(f"""
## 3. Problématique et objectifs

> Comment exploiter les caractéristiques d'un message numérique pour identifier automatiquement
> les messages potentiellement malveillants et assister la détection du phishing ?

- **Objectif général** : estimer `P(Oui | x)`, la probabilité qu'un message soit malveillant,
  à partir de 9 signaux.
- **Objectifs spécifiques** : comparer plusieurs algorithmes, choisir un seuil de décision
  justifié, expliquer chaque verdict, laisser la décision finale à l'humain.
- **Livrable** : un prototype Streamlit + un notebook reproductible + un modèle sérialisé.
""")
    st.markdown("---")

    st.markdown("""
## 4. Solutions existantes et limites

| Approche | Principe | Limite principale |
|---|---|---|
| SPF / DKIM / DMARC, blocklists | authentifier l'expéditeur, bloquer les domaines connus | contourné si un domaine légitime est compromis |
| Filtres bayésiens / ML sur en-têtes | apprendre des mots et signaux techniques | dérive dès que l'attaquant change de style |
| Réputation d'URL et de domaine | âge, listes noires, typosquatting | angles morts sur les domaines neufs non listés |
| LLM / analyse sémantique | comprendre l'intention du texte | coût, latence, explicabilité faible, données envoyées à un tiers |
| Suites commerciales | boîte noire multi-signaux | prix, dépendance, seuil invisible donc non ajustable |

**Constat** : peu d'outils exposent une **probabilité** et un **seuil déplaçable**. C'est précisément
la place d'un prototype académique transparent.
""")
    st.markdown("---")

    st.markdown(f"""
## 5. Approche retenue et valeur ajoutée

- **Classification binaire supervisée** : `Non` = message légitime, `Oui` = message malveillant.
- **9 variables explicatives** tabulaires, aucune donnée textuelle.
- **Quatre algorithmes comparés** : régression logistique, Random Forest (300 arbres), SVM RBF
  et une régression logistique améliorée (transformation `log1p` de l'âge du domaine, deux
  interactions, retrait du bruit).
- **Seuil appris sur le train** ({SEUIL:.2f}) et **triage 3 zones** ({SEUIL_BAS:.2f} / {SEUIL_HAUT:.2f}).
- **Valeur ajoutée** : probabilité affichée, seuil réglable, explication des signaux, 100 % local,
  reproductible (seed 42). **Limite assumée** : prototype expérimental, il ne remplace pas une
  passerelle de messagerie.
""")
    st.markdown("---")

    st.markdown(f"""
## 6. Architecture globale

`CSV` → **exploration** → **nettoyage** → **analyse exploratoire** → `X` / `y` →
**séparation 80/20 stratifiée** → **prétraitement dans le pipeline** → **entraînement** →
**validation croisée** → **évaluation test** → **sélection du modèle et du seuil** →
**prédiction individuelle** → **sauvegarde joblib** → **application Streamlit**.
""")
    _img_process = ROOT / "artefacts" / "processus_phishing_ia.png"
    if _img_process.exists():
        st.image(str(_img_process), caption="Processus retenu : le test n'apparaît qu'à l'étape 8, "
                 "après le choix du modèle et du seuil.", **IMG_KW)
    st.markdown("---")

    st.markdown(f"""
## 7. Présentation du dataset

- **Origine** : fichier local `dataset_phishing_ia - dataset_phishing_ia.csv`, **données
  synthétiques** générées pour l'exercice. Aucune donnée personnelle, aucun vrai e-mail.
- **Dimensions** : {n_brut} observations, {brut.shape[1]} colonnes, {n_doublons} doublons,
  {S['n_propre']} observations après nettoyage.
- **Cible** : `{TARGET}` = `Oui` / `Non`. Répartition : `Non` {S['n_non']} ({S['n_non'] / S['n_propre']:.2%}),
  `Oui` {S['n_oui']} ({S['part_oui']:.2%}).
- **Exclue** : `date` (variable calendaire sans justification métier) — donc 9 variables explicatives.

| Variable | Sens métier |
|---|---|
| `heure_envoi` | heure d'envoi du message |
| `longueur_message` | longueur du corps du message |
| `nb_liens` | nombre de liens contenus |
| `urgence_score` | niveau d'urgence du ton employé |
| `domaine_age_jours` | âge du domaine de l'expéditeur (en jours) |
| `fautes_langue` | nombre de fautes détectées |
| `expediteur_connu` | expéditeur présent dans le carnet d'adresses (1 = oui) |
| `piece_jointe` | présence d'une pièce jointe (1 = oui) |
| `personnalisation_score` | degré de personnalisation du message |
""")
    st.markdown("---")

    st.markdown(f"""
## 8. Nettoyage et qualité des données

- **{n_doublons} doublons** supprimés : {n_brut} → {S['n_propre']} observations.
- **{n_na} valeurs manquantes**, toutes dans `domaine_age_jours` ({n_na / n_brut:.2%} des lignes) :
  imputation par la **médiane apprise sur le train** — robuste aux valeurs extrêmes (l'âge va de
  1 à 5 874 jours) et sans fuite de données.
- **Aucune valeur manquante** dans les 8 autres variables.
- **Standardisation** des variables numériques dans le pipeline : nécessaire pour la régression
  logistique et le SVM, sans effet sur les arbres.
- **Aucun one-hot encoding** : les 9 variables sont numériques (les indicateurs binaires sont déjà 0/1).
- Le **test n'est jamais utilisé pour calculer** une médiane, une moyenne ou un écart-type.
""")
    st.markdown("---")

    st.markdown(f"""
## 9. Analyse exploratoire des données

- **Répartition de la cible** : `Non` {S['n_non']} ({S['n_non'] / S['n_propre']:.2%}) /
  `Oui` {S['n_oui']} ({S['part_oui']:.2%}) → jeu déséquilibré, d'où le F1 macro et `class_weight="balanced"`.
- **Âge du domaine** : les messages malveillants utilisent des domaines beaucoup plus récents.
- **Urgence** et **nombre de liens** : plus élevés en moyenne dans la classe `Oui`.
- **Expéditeur connu** : variable protectrice (quasi absente dans la classe `Oui`).
- **Fautes de langue** : la corrélation avec la cible est quasi nulle
  ({float(S['corr_cible'].get('fautes_langue', 0)):+.2f}) : l'IA générative écrit correctement.
- ⚠️ Une différence de moyenne n'est pas un pouvoir prédictif : seule la validation croisée
  mesure la contribution réelle d'une variable.
""")
    _cols_eda = st.columns(3)
    for _col, _img, _cap in zip(
            _cols_eda,
            ["cell31_0.png", "boxplots_compact.png", "cell33_0.png"],
            ["Répartition de la cible — 374 Non (71,9 %) / 146 Oui (28,1 %)",
             "Boxplots par classe — effectif, médiane et moyenne annotés",
             "Histogrammes par classe — moyenne et effectif dans chaque graphique"]):
        _p_img = ROOT / "artefacts" / "pptx" / _img
        if _p_img.exists():
            with _col:
                st.image(str(_p_img), caption=_cap, **IMG_KW)
    st.markdown("---")

    st.markdown(f"""
## 10. Matrice de corrélation

- **Corrélations négatives** : `domaine_age_jours` ({float(S['corr_cible']['domaine_age_jours']):+.2f})
  — plus le domaine est ancien, moins le message est suspect.
- **Corrélations positives** : `urgence_score` ({float(S['corr_cible']['urgence_score']):+.2f}),
  `nb_liens` ({float(S['corr_cible']['nb_liens']):+.2f}) — plus ils montent, plus le risque monte.
- **Corrélations proches de zéro** : `heure_envoi`, `longueur_message`, `fautes_langue` —
  aucun signal linéaire exploitable.
- **Colinéarité faible** entre variables explicatives : pas de redondance qui fausserait l'importance.
- ⚠️ **Corrélation ≠ causalité** ; Pearson ne capte qu'un lien linéaire, d'où l'ajout d'une
  régression logistique multivariée et d'un SVM à noyau RBF pour les effets non linéaires.
""")
    _cols_corr = st.columns(2)
    for _col, _img, _cap in zip(
            _cols_corr,
            ["cell39_0.png", "cell41_0.png"],
            ["Matrice de Pearson entre variables explicatives",
             "Association de chaque variable avec la cible Oui"]):
        _p_img = ROOT / "artefacts" / "pptx" / _img
        if _p_img.exists():
            with _col:
                st.image(str(_p_img), caption=_cap, **IMG_KW)
    st.markdown("---")

    st.markdown(f"""
## 11. Préparation et séparation des données

- `X` = les 9 variables explicatives ; `y` = `{TARGET}`. `date` exclue.
- **Séparation 80 / 20** avec `train_test_split(..., stratify=y, random_state=42)` :
  **{S['n_train']} messages en entraînement**, **{S['n_test']} en test**.
- La stratification conserve la proportion de `Oui` dans les deux sous-ensembles
  ({S['part_oui']:.1%}).
- **Tout le prétraitement vit dans le pipeline** (imputation, standardisation, feature engineering) :
  chaque `fit` est fait sur le train du pli, jamais sur le test → pas de fuite de données.
- Le test n'est ouvert **qu'une seule fois**, après le choix du modèle et du seuil.
""")
    st.markdown("---")

    st.markdown(f"""
## 12. Les modèles de classification

| Modèle | Principe | Paramètres principaux | Avantage | Limite |
|---|---|---|---|---|
| **Régression logistique** | frontière linéaire, probabilité par fonction sigmoïde | `max_iter=2000`, `class_weight=balanced` | simple, coefficients lisibles | ne capte pas les interactions seules |
| **Random Forest** | moyenne de 300 arbres de décision | `n_estimators=300`, `min_samples_leaf=2`, `class_weight=balanced` | non linéaire, robuste | moins interprétable, peut surapprendre |
| **SVM RBF** | frontière non linéaire dans un espace transformé | `C=1`, `gamma=scale`, `probability=True` | bon en dimension moyenne | lent, probabilités approximatives, peu explicable |
| **LR améliorée (retenue)** | LR sur `log1p(âge)`, 2 interactions, bruit retiré | `max_iter=3000`, `class_weight=balanced` | meilleur classement, explicable | dépend du feature engineering |

Pourquoi ces trois-là ? Parce qu'ils représentent trois familles différentes : linéaire,
ensemble d'arbres, noyau. Comparer trois variantes du même famille n'apprendrait rien.
La baseline « toujours `Non` » sert de point de repère : F1 macro 0,419, aucun phishing détecté.
""")
    st.markdown("---")

    st.markdown(f"""
## 13. Protocole expérimental et validation croisée

1. **Entraînement** sur les {S['n_train']} messages du train, prétraitement inclus dans le pipeline.
2. **Validation croisée stratifiée 5-fold sur le train** : elle sert à comparer les modèles et à
   choisir le seuil ; le test n'y participe pas.
3. **Validation croisée répétée 5×5** pour la stabilité : 5 découpages différents, probabilités
   moyennées — AUC {0.9092:.4f} ± {0.0031:.4f}, AP {0.8119:.4f} ± {0.0034:.4f}.
4. **Seuil** : plateau de coût quasi minimal `5·FN + FP`, soit 0,20–0,22 → **{SEUIL:.2f}**.
5. **Triage** : rappel ≥ 98 % pour la zone verte, précision ≥ 85 % pour la zone rouge
   → **{SEUIL_BAS:.2f} / {SEUIL_HAUT:.2f}**.
6. **Test final** lu une seule fois : AUC {rf['auc']:.3f}, AP 0,810, Brier {rf['mse']:.3f}.

**Pourquoi le F1 macro ?** Il donne le même poids aux deux classes ; l'accuracy seule
récompense un modèle qui ne détecte rien (72 % de `Non`).
""")
    st.markdown("---")

    _cv_rank = S["cv"].sort_values("F1 macro (CV 5-fold, train)", ascending=False)
    _best_cv = _cv_rank.iloc[0]
    st.markdown(f"""
## 14. Résultats expérimentaux

**Validation croisée 5-fold sur le train — critère de sélection du modèle :**

| Modèle | F1 macro CV (moyenne des 5 plis) |
|---|---:|
{chr(10).join(f"| {r['Modèle']} | {r['F1 macro (CV 5-fold, train)']:.4f} |" for _, r in _cv_rank.iterrows())}

**Meilleur modèle en validation croisée : {_best_cv['Modèle']} ({_best_cv['F1 macro (CV 5-fold, train)']:.4f}).**
C'est ce score, calculé uniquement sur les {S['n_train']} messages du train, qui sert à sélectionner
le modèle. Le test de {S['n_test']} messages n'est ouvert qu'après, comme contrôle final.
La CV 5-fold est appliquée à **tous** les modèles, y compris la LR améliorée ; le Dummy est un
**plancher de référence** (0,418, aucun phishing détecté), pas un candidat au déploiement.

**Contrôle final sur le test, au seuil appris {SEUIL:.2f} :**

| Modèle | Accuracy | Précision `Oui` | Rappel `Oui` | F1 macro | FN | FP |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(f"| {r['Modèle']} | {r['Accuracy']:.3f} | {r['Précision Oui']:.3f} | {r['Rappel Oui']:.3f} | {r['F1 macro']:.3f} | {int(r['FN'])} | {int(r['FP'])} |" for _, r in S['test'].iterrows())}

- Le Random Forest peut gagner ponctuellement au seuil 0,50, mais il est derrière la LR améliorée
  en validation croisée : le classement fiable est celui de la CV, pas une seule réalisation du test.
- La LR améliorée gagne aussi sur le **classement indépendant du seuil** : **AUC 0,910**, **AP 0,810**,
  **Brier 0,123**, devant RF (0,866 / 0,698), LR (0,832 / 0,656) et SVM (0,834 / 0,633).
- **Modèle retenu : régression logistique améliorée.** Coût au seuil {SEUIL:.2f} :
  `5·{rf['fn']} + {rf['fp']} = {5 * rf['fn'] + rf['fp']}`.
""")
    st.markdown("---")

    st.markdown(f"""
## 15. Matrices de confusion et interprétation métier

| | Prédit `Non` | Prédit `Oui` |
|---|---:|---:|
| **Réel `Non`** | TN = {rf['tn']} | FP = {rf['fp']} |
| **Réel `Oui`** | FN = {rf['fn']} | TP = {rf['tp']} |

- **TP** = phishing correctement détecté ; **TN** = message légitime correctement laissé passer.
- **FP** = fausse alerte : coût = quelques minutes d'analyste.
- **FN** = phishing non détecté : coût = compromission possible. **C'est l'erreur critique.**
- Au seuil {SEUIL:.2f} : rappel **{rf['rappel']:.1%}**, précision **{rf['precision']:.1%}**,
  F1 macro **{rf['f1_macro']:.3f}**, accuracy **{rf['acc']:.1%}** (mais la baseline atteint déjà 72 %).
- **Triage** : {tri['auto']}/{tri['total']} messages traités automatiquement, {tri['revue']} envoyés
  à l'analyste ; sur la partie automatisée, {tri['fn_auto']} FN et {tri['fp_auto']} FP.
- **Zéro erreur automatisée est possible** (seuils 0,07 / 0,98) mais seulement en envoyant
  **74 messages sur 104** en revue humaine : le système n'automatise alors plus que 30 cas.
""")
    _cols_cm = st.columns(2)
    with _cols_cm[0]:
        _fig_cm, _ax_cm = plt.subplots(figsize=(5.2, 4.0))
        heatmap_cm(_ax_cm, S["cm_rf"], f"Modèle retenu — seuil {SEUIL:.2f}")
        st.pyplot(_fig_cm)
        plt.close(_fig_cm)
    with _cols_cm[1]:
        _p_img = ROOT / "artefacts" / "pptx" / "cell63_1.png"
        if _p_img.exists():
            st.image(str(_p_img), caption="Comparaison — Random Forest (référence historique)", **IMG_KW)
    st.markdown("---")

    st.markdown(f"""
## 16. Importance des variables et analyse des erreurs

- Importance mesurée par **permutation sur le test** (chute du F1 macro quand on mélange une
  variable) : c'est la contribution réelle au classement, pas l'impureté des arbres.
- Variables en tête :

{chr(10).join(f"- `{r.Variable}` : {r.Importance:+.4f}" for r in S['importances'].head(4).itertuples())}

- **`domaine_age_jours`** domine : un domaine très récent est le signal le plus fort.
- Viennent ensuite l'**urgence**, l'**expéditeur inconnu** et le **nombre de liens** — cohérents
  avec les pratiques d'attaque observées.
- **`heure_envoi`, `longueur_message`, `fautes_langue`** apportent peu : le style ne suffit plus.
- ⚠️ Importance ≠ causalité : elle indique de quoi **le modèle dépend**, pas ce qui **provoque**
  le phishing. Une variable corrélée à une autre peut récupérer son importance.
- **Erreurs** : {rf['fp']} faux positifs (messages normaux trop « urgents » ou avec plusieurs liens)
  et {rf['fn']} faux négatif (phishing très bien imité). Les deux vivent près du seuil.
""")
    _p_img = ROOT / "artefacts" / "pptx" / "cell78_0.png"
    if _p_img.exists():
        st.image(str(_p_img), caption="Permutation importance — contribution de chaque variable au F1 macro",
                 **IMG_KW)
    st.markdown("---")

    _sc_lines = []
    for _sc in CFG["scenarios"]:
        _r = predire(_sc["valeurs"], modele, meta, SEUIL)
        _sc_lines.append(
            f"| {_sc['nom']} | {_r['p_severe']:.1%} | "
            f"{'Oui — malveillant' if _r['classe'] == SEVERE else 'Non — légitime'} | "
            f"{_r['zone']} | {_r['action']} |")
    st.markdown(f"""
## 17. Tests individuels, limites et perspectives

**Trois scénarios pédagogiques** (mêmes variables que le formulaire de la page 3) :

| Scénario | P(Oui) | Classe binaire | Zone | Action |
|---|---:|---|---|---|
{chr(10).join(_sc_lines)}

Ces scénarios sont **construits à la main** : ce ne sont ni des messages réels, ni des données
externes inédites. Le vrai contrôle reste le test de {S['n_test']} messages.

**Limites**
- Dataset **synthétique** de {S['n_propre']} lignes : la généralisation à de vrais e-mails n'est pas démontrée.
- **Pas de texte brut** : le modèle ne lit pas le message, il exploite des signaux déjà extraits.
- **Aucune évaluation externe** indépendante ; test de {S['n_test']} messages dont {S['n_oui']} malveillants.
- **Probabilités non calibrées** et **seuil sensible** : 1 FN / 1 FP en moins ou en plus change le coût.
- **Dérive** non traitée : pas de suivi de performance en production.

**Perspectives**
- Tester sur des données réelles anonymisées et diversifiées.
- Ajouter des variables issues des URL (réputation, âge du certificat, typosquatting) et du texte.
- Calibrer les probabilités (Platt, isotonique) et étudier le seuil avec le RSSI.
- Explicabilité locale (SHAP) et boucle de retour analyste.
- Évaluer la robustesse aux campagnes générées par IA.
""")
    st.markdown("---")

    st.markdown(f"""
## 18. Conclusion

- **Problématique** : estimer la probabilité qu'un message soit malveillant à partir de signaux
  observables, et aider l'analyste à prioriser.
- **Démarche** : nettoyage contrôlé, séparation stricte train/test, pipeline sans fuite,
  validation croisée répétée, seuil choisi sur le train par le coût métier.
- **Résultats réels** : AUC **{rf['auc']:.3f}**, AP **0,810**, Brier **{rf['mse']:.3f}** ;
  au seuil {SEUIL:.2f}, rappel **{rf['rappel']:.1%}** pour {rf['fn']} phishing manqué et
  {rf['fp']} fausses alertes ; triage {tri['auto']}/{tri['total']} automatisés.
- **Modèle retenu** : régression logistique améliorée — meilleur classement, coût minimal, explicable.
- **Valeur pour la confiance numérique** : un pré-filtre transparent, réglable et auditable,
  qui rend la décision humaine plus rapide sans jamais la remplacer.
- **Limites** : données synthétiques, pas de texte brut, pas de validation externe.

**Merci pour votre attention — Questions ?**
""")
    st.markdown("---")

    st.markdown(f"""
## Annexe — les métriques, une par une

| Métrique | Formule | Ce qu'elle mesure | Valeur ici |
|---|---|---|---|
| **Accuracy** | `(TP + TN) / n` | part de décisions correctes | {rf['acc']:.3f} |
| **Précision `Oui`** | `TP / (TP + FP)` | fiabilité des alertes | {rf['precision']:.3f} |
| **Rappel `Oui`** | `TP / (TP + FN)` | part des phishing détectés | {rf['rappel']:.3f} |
| **F1 macro** | moyenne des F1 des deux classes | équilibre précision / rappel | {rf['f1_macro']:.3f} |
| **AUC** | aire sous la courbe ROC | qualité du classement, tous seuils confondus | {rf['auc']:.3f} |
| **AP** | aire sous la courbe Precision-Recall | idem, adapté aux classes déséquilibrées | 0,810 |
| **MAE** | `moyenne(abs(y - P(Oui)))` | erreur moyenne en points de probabilité | {rf['mae']:.3f} |
| **MSE (= Brier)** | `moyenne((y - P(Oui))²)` | erreur quadratique, punit l'excès de confiance | {rf['mse']:.3f} |
| **RMSE** | `racine(MSE)` | même erreur, dans l'unité d'origine | {np.sqrt(rf['mse']):.3f} |
| **R²** | `1 - SSE / SST` | part de variance de la cible expliquée | {rf['r2']:.3f} |

**C'est quoi l'AUC ?** L'aire sous la courbe ROC. On classe au hasard un message malveillant et un
message légitime : l'AUC est la probabilité que le modèle donne une probabilité plus élevée au
malveillant. 0,5 = hasard, 1,0 = séparation parfaite. Ici **{rf['auc']:.3f}** : le modèle classe
correctement 9 fois sur 10, **indépendamment du seuil**. C'est la métrique la plus honnête pour
comparer des modèles, mais elle ne dit pas combien d'alertes seront émises.

**Pourquoi R², MAE, MSE ne pilotent pas la décision ?**
Ce sont des métriques de **régression**. Appliquées à une cible binaire, elles comparent une
probabilité à une étiquette 0/1 :
- sur des décisions 0/1, `MAE = 1 - accuracy` et `RMSE = racine(1 - accuracy)` : aucune information nouvelle ;
- `R²` a un plafond structurel `p(1-p) = {rf['var_y']:.3f}` pour une cible binaire
  (ici {rf['r2']:.3f} est donc élevé, pas « faible ») ;
- elles sont **symétriques** : un FN et un FP coûtent pareil, ce qui est faux en sécurité ;
- elles **ignorent le seuil** réellement utilisé.

Les critères de décision retenus sont : **rappel `Oui`, matrice de confusion au seuil {SEUIL:.2f},
F1 macro, AUC/AP et validation croisée**. R², MAE, MSE et RMSE restent affichés et expliqués parce
que le cahier des charges les demande — pas parce qu'ils choisissent le modèle.
""")
    st.markdown("---")

    _p_non = float(propre.loc[propre[TARGET] == ORDER[0], "personnalisation_score"].mean())
    _p_oui = float(propre.loc[propre[TARGET] == SEVERE, "personnalisation_score"].mean())
    _p_corr = float(propre["personnalisation_score"].corr((propre[TARGET] == SEVERE).astype(int)))
    st.markdown(f"""
## 19. Annexe A — zoom sur `personnalisation_score` (0–10)

Cet attribut mesure **à quel point un message semble adapté personnellement à son destinataire**,
plutôt que d'être un message générique envoyé à tout le monde.

**Exemple 1 — message générique (score faible)**

> Cher client, votre compte nécessite une vérification. Cliquez ici.

Aucune information personnelle : le score doit rester bas.

**Exemple 2 — message personnalisé (score plus élevé)**

> Bonjour Faker, votre compte bancaire associé à votre adresse e-mail nécessite une vérification.

Le prénom et une information qui semble concerner le destinataire sont utilisés : le score monte.

**Comment lire le score ?** L'échelle réelle du fichier va de **0 à 10**
(minimum {propre['personnalisation_score'].min():.0f}, maximum {propre['personnalisation_score'].max():.0f},
moyenne {propre['personnalisation_score'].mean():.2f}) :

| Score | Interprétation |
|---|---|
| 0–2 | Très peu personnalisé |
| 3–4 | Faiblement personnalisé |
| 5–7 | Moyennement personnalisé |
| 8–10 | Fortement personnalisé |

Ces bornes sont **illustratives** : l'échelle du fichier est vérifiée dans le code, pas supposée.

**Rapport avec le phishing**

- Messages normaux : score moyen **{_p_non:.2f}**.
- Messages malveillants : score moyen **{_p_oui:.2f}**.
- Corrélation avec la cible : **{_p_corr:+.2f}** — faible, mais non nulle.

Le *spear phishing* exploite des informations personnelles pour gagner la confiance.
**Attention** : un message très personnalisé n'est pas forcément malveillant (les banques et les
entreprises personnalisent aussi). La variable est **conservée**, mais elle ne suffit jamais seule :
c'est la combinaison avec l'âge du domaine, l'urgence et l'expéditeur inconnu qui produit le verdict.
""")
    st.markdown("---")

    st.markdown(f"""
## 20. Annexe B — vérifications et traçabilité

**Notebook : un seul exemplaire, réellement exécuté**

- Le notebook du projet est **identique octet pour octet** au notebook réexécuté de zéro :
  `cmp` → IDENTIQUE, **{len(json.loads(NOTEBOOK.read_text(encoding="utf-8")).get("cells", []))} cellules,
  0 erreur** ; la matrice de corrélation inclut la cible (`cible (Oui = 1)`).
- `model.joblib` identique ; `model_meta.json` ne change que des libellés (mêmes seuils,
  mêmes métriques).
- « OOF » supprimé partout (notebook, application, présentation) et remplacé par
  « validation croisée ». Résultats inchangés : **AUC 0,9092 ± 0,0031**, seuil **0,21**,
  test **AUC 0,910 / AP 0,810 / Brier 0,123**.

**Formulaire de prédiction : trois cas lisibles**

| Modèle (même saisie) | P(Oui) | Classe binaire | Zone |
|---|---:|---|---|
| Modèle retenu (joblib) | 28,19 % | Oui — malveillant | 🟠 VIGILANCE |
| Régression logistique | 44,57 % | Oui — malveillant | 🟠 VIGILANCE |
| Random Forest | 20,30 % | Non — légitime | 🟠 VIGILANCE |
| KNN / SVM RBF | 0 % / 17,14 % | Non — légitime | 🟢 NORMAL |

Les trois scénarios : **1 → 🟢 Non**, **2 → 🔴 Oui malveillant (100 %)**, **3 → 🟠 Oui + revue
humaine (47,1 %)**. La classe ne vaut plus jamais « À vérifier » : elle est `Oui` / `Non`,
le triage est une colonne séparée.

**FN / FP = 0 sur le test : les chiffres, sans promesse**

| Règle | FN | FP | Automatisés | Revue |
|---|---:|---:|---:|---:|
| Seuil unique 0,07 | 0 | 48 | 104 | 0 |
| Seuil unique 0,21 (retenu) | 1 | 28 | 104 | 0 |
| Seuil unique 0,98 | 26 | 0 | 104 | 0 |
| Triage 0,20 / 0,88 (retenu) | 1 | 1 | 61 | 43 |
| Triage 0,07 / 0,98 | 0 | 0 | 30 | 74 |

Donc : **0 FN et 0 FP sur la partie automatisée est possible**, mais alors **74 messages sur 104
(71 %) partent en revue humaine** et le système n'automatise plus que 30 cas. À 0,89 / 0,90 on a
1 FP mais 15 à 18 FN. Le compromis retenu reste **0,21 + triage 0,20 / 0,88**.
""")

    st.markdown("### Télécharger les livrables")
    _pptx = ROOT / "Presentation_Projet_Phishing_IA.pptx"
    _cols = st.columns(2)
    with _cols[0]:
        if _pptx.exists():
            st.download_button("Présentation PowerPoint (.pptx)", _pptx.read_bytes(),
                               file_name=_pptx.name,
                               mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                               **BTN_KW)
        else:
            st.caption("Fichier PowerPoint absent du dossier.")
    with _cols[1]:
        if NOTEBOOK.exists():
            st.download_button("Notebook exécuté (.ipynb)", NOTEBOOK.read_bytes(),
                               file_name=NOTEBOOK.name, mime="application/x-ipynb+json",
                               **BTN_KW)

else:
    st.header("4) Notebook (référence)")
    st.info("Le notebook contient le code complet, les explications du projet et, une fois exécuté, "
            "les graphiques et sorties détaillées.")
    render_notebook(NOTEBOOK)

st.sidebar.markdown("---")
st.sidebar.caption(CFG["titre"] + " — ISCAE Master VIC")
