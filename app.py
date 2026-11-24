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
    "2. EDA des données",
    "3. Prédiction / Verdict",
    "4. Explication des attributs",
    "5. Guide de présentation",
])
st.sidebar.markdown("---")
st.sidebar.info("Outil pédagogique. Décision humaine obligatoire — aucun blocage automatique.")

N_BRUT = int(len(brut))
N_PROPRE = int(len(propre))
N_DOUBLONS = int(brut.duplicated().sum())
N_NON = int((propre[TARGET] == ORDER[0]).sum())
N_OUI = int((propre[TARGET] == SEVERE).sum())

# ------------------------- PAGE 1 : CONTEXTE -------------------------
if page.startswith("1"):
    st.header("1) Contexte général et problématique")

    st.subheader("Contexte général")
    st.markdown(CFG["contexte"])

    st.subheader("Problématique")
    st.info(CFG["problematique"])

    st.subheader("Objectif : pré-dépistage")
    st.markdown("""
    Le modèle fait du **pré-dépistage** : il trie rapidement les messages pour repérer ceux qui méritent
    une analyse humaine.

    - **Entrée** : signaux structurés du message (urgence, liens, âge du domaine, expéditeur connu, pièce jointe…).
    - **Sortie** : **Malveillant** ou **Non malveillant**, avec une probabilité P(Oui).
    - **Exemple** : urgence élevée + plusieurs liens + domaine récent + expéditeur inconnu → le modèle peut
      prédire **Malveillant**.
    - Le résultat est une **aide à la décision** : la vérification finale reste humaine.
    """)

    st.subheader("Questions de recherche")
    st.markdown("\n".join("- " + q for q in CFG["questions"]))

    st.subheader("Erreur la plus coûteuse")
    st.warning(CFG["erreur_couteuse"])

    st.caption("Les détails du jeu de données sont en page 2, le formulaire en page 3, le rôle de chaque "
               "attribut en page 4 et le guide de présentation (AUC / AP / OOF) en page 5.")

# ------------------------- PAGE 2 : EDA -------------------------
elif page.startswith("2"):
    st.header("2) EDA des données")
    st.caption("Tous les graphiques sont recalculés à l'ouverture depuis "
               + "`" + DATA_PATH.name + "` — aucun chiffre saisi à la main.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes brutes", N_BRUT)
    c2.metric("Doublons supprimés", N_DOUBLONS)
    c3.metric("Lignes uniques", N_PROPRE)
    c4.metric("Valeurs manquantes", int(brut.isna().sum().sum()))

    with st.expander("Aperçu du jeu de données"):
        st.dataframe(brut.head(8), **DF_KW)
        st.dataframe(brut.describe(include="all").T, **DF_KW)

    st.subheader("Distribution de la cible")
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
    st.caption(f"**Lecture** : {N_NON} messages légitimes ({N_NON / N_PROPRE:.1%}) contre "
               f"{N_OUI} malveillants ({N_OUI / N_PROPRE:.1%}). Un modèle qui prédirait toujours `Non` "
               f"aurait {N_NON / N_PROPRE:.1%} d'accuracy sans détecter aucun phishing : l'accuracy seule "
               "est trompeuse, on utilise le F1 macro.")

    st.subheader("Variables numériques par classe")
    num_cols = list(meta["num"])
    n = len(num_cols)
    cols = 3
    lignes = (n + cols - 1) // cols
    fig, axes = plt.subplots(lignes, cols, figsize=(13, 3.3 * lignes))
    axes = np.atleast_1d(axes).ravel()
    for ax, col in zip(axes, num_cols):
        ann = []
        for cls, color in zip(ORDER, CFG["colors"][:len(ORDER)]):
            serie = propre.loc[propre[TARGET] == cls, col].dropna()
            ax.hist(serie, bins=12, alpha=0.45, color=color,
                    label=f"{cls} (n = {len(serie)})")
            ann.append(f"{cls} : moyenne = {serie.mean():.1f}")
        ax.set_title(col, fontsize=9)
        ax.text(0.02, 0.98, "\n".join(ann), transform=ax.transAxes, va="top",
                fontsize=6.5, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85))
    for ax in axes[n:]:
        ax.axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("**Lecture** : plus les distributions sont décalées entre les deux couleurs, plus la "
               "variable sépare les classes. Un fort chevauchement signifie qu'aucune variable seule ne "
               "suffit — d'où la combinaison par le modèle.")

    st.subheader("Matrice de corrélation (variables + cible)")
    COL_CIBLE = "cible (" + SEVERE + " = 1)"
    df_corr = propre[num_cols + [TARGET]].copy()
    df_corr[COL_CIBLE] = (df_corr[TARGET] == SEVERE).astype(int)
    corr = df_corr[num_cols + [COL_CIBLE]].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(8, 6.4))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
    ax.set_title("Corrélation de Pearson — la cible est incluse (" + SEVERE + " = 1)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    top = corr[COL_CIBLE].drop(COL_CIBLE).sort_values(key=abs, ascending=False)
    st.dataframe(top.rename("corrélation_avec_cible").to_frame(), **DF_KW)
    signaux = ", ".join(f"`{c} {v:+.3f}`" for c, v in top.head(4).items())
    st.caption(f"**Signaux les plus liés à `Oui`** : {signaux}. Une valeur négative signifie que la "
               "variable diminue quand le message est malveillant. **Corrélation ≠ causalité** : la "
               "matrice mesure seulement un lien linéaire.")

# ------------------------- PAGE 3 : PREDICTION -------------------------
elif page.startswith("3"):
    st.header("3) Prédiction / Verdict final")
    st.markdown("Saisissez une situation. Le modèle utilise exactement le pipeline du notebook. "
                "Seuil décisionnel : **" + format(SEUIL, ".2f") + "**. Outil d'aide à la décision, "
                "**pas de décision automatique**.")

    st.subheader("Scénarios pédagogiques")
    st.caption("Trois cas : **Malveillant**, **Non malveillant** et **Non malveillant — zone de vigilance**. "
               "La zone de triage (0,20 / 0,88) ne crée pas une troisième classe : elle indique seulement "
               "la priorité de vérification.")
    scols = st.columns(len(CFG["scenarios"]))
    for i, sc in enumerate(CFG["scenarios"]):
        with scols[i]:
            r = predire(sc["valeurs"], modele, meta, SEUIL)
            st.markdown("**" + sc["nom"] + "**")
            st.caption("Attendu : " + sc["attendu"])
            st.write("Verdict : **" + r["verdict"] + "**")
            st.write("**P(Oui) : " + format(r["p_severe"], ".1%") + "**")
            st.caption("Triage : " + r["zone"])
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
            for col, options in meta["cat"].items():
                label, desc = CFG["fields"].get(col, (col, ""))
                idx = options.index(str(valeurs[col])) if str(valeurs.get(col)) in options else 0
                saisi[col] = st.selectbox(label, options, index=idx, key="c_" + col, help=desc)
        envoyer = st.form_submit_button("Prédire", **BTN_KW)

    if envoyer:
        st.markdown("### Données saisies")
        st.dataframe(pd.DataFrame([saisi]), **DF_KW, hide_index=True)

        resultat = predire(saisi, modele, meta, SEUIL)
        st.markdown("### Verdict final")
        if resultat["verdict"] == "Malveillant":
            st.error("## 🚨 Malveillant")
        else:
            st.success("## ✅ Non malveillant")
        st.caption("Décision binaire au seuil " + format(SEUIL, ".2f")
                   + " — P(Oui) = " + format(resultat["p_severe"], ".1%")
                   + " · information complémentaire : " + resultat["zone"] + " — " + resultat["action"])

        with st.expander("Voir les probabilités détaillées"):
            st.dataframe(pd.DataFrame([
                {"Classe": c, "Probabilité %": round(float(p) * 100, 2)}
                for c, p in resultat["probas"].items()]), **DF_KW, hide_index=True)

        st.markdown("### Pourquoi ce verdict ?")
        st.write("- " + "\n- ".join(expliquer(saisi)))
        st.warning("Verdict pédagogique issu d'un modèle statistique entraîné sur des données synthétiques. "
                   "**Validation humaine obligatoire** — aucune action automatique.")

# ------------------------- PAGE 4 : ATTRIBUTS -------------------------
elif page.startswith("4"):
    st.header("4) Explication des attributs")
    st.caption("Définition, échelle, exemple, lecture phishing et rôle de chaque variable. "
               "Les moyennes et corrélations sont recalculées à l'ouverture.")

    rows = []
    for col, (label, meaning) in CFG["fields"].items():
        kind = "Numérique" if col in meta["num"] else "Catégorielle"
        rows.append({"Variable": col, "Nom lisible": label, "Type": kind,
                     "Description / utilité": meaning})
    rows.append({"Variable": TARGET, "Nom lisible": "Cible", "Type": "Target",
                 "Description / utilité": "Classe à prédire (" + ", ".join(ORDER) + "). "
                                          "Jamais utilisée comme variable explicative."})
    st.subheader("Dictionnaire des variables")
    st.dataframe(pd.DataFrame(rows), **DF_KW, hide_index=True)
    st.caption("Variables exclues du modèle : " + (", ".join(DROP_COLS) if DROP_COLS else "aucune")
               + " (variable calendaire sans justification métier).")

    st.subheader("Détail par attribut")
    for col, d in EXPLICATIONS_VARIABLES.items():
        with st.expander(f"{d['titre']} — `{col}`"):
            st.markdown(d["corps"])
            if col == TARGET:
                st.markdown("**Dans ce jeu.** "
                            f"`{ORDER[0]}` = {N_NON} messages, `{SEVERE}` = {N_OUI} messages "
                            f"sur {N_PROPRE} — classes déséquilibrées.")
            elif col in propre.columns and col in meta["num"]:
                m_non = float(propre.loc[propre[TARGET] == ORDER[0], col].mean())
                m_oui = float(propre.loc[propre[TARGET] == SEVERE, col].mean())
                r = float(propre[col].corr((propre[TARGET] == SEVERE).astype(int)))
                st.markdown("**Dans ce jeu (calculé à l'ouverture).** "
                            f"Moyenne `{ORDER[0]}` = {m_non:.2f} ; moyenne `{SEVERE}` = {m_oui:.2f} ; "
                            f"corrélation avec la cible r = {r:+.2f}.")

# ------------------------- PAGE 5 : GUIDE DE PRESENTATION -------------------------
else:
    st.header("5) Guide de présentation — comprendre AUC, AP et OOF")
    st.caption("Ce guide relie chaque indicateur à la logique réelle du notebook et de `app.py`. "
               "Il sert à expliquer le projet à l'oral, pas seulement à afficher des chiffres.")

    st.subheader("1. Vue globale du processus Machine Learning")
    st.markdown(f"""
    ```
    DATASET BRUT — {N_BRUT} lignes (données synthétiques)
        |
        |  nettoyage : {N_DOUBLONS} doublons supprimés
        v
    {N_PROPRE} LIGNES UNIQUES
        |
        |  séparation X / y : X = {len(meta['num']) + len(meta['cat'])} variables explicatives,
        |                     y = message_malveillant (Oui / Non)
        v
    TRAIN — {int(round(N_PROPRE * 0.8))} lignes (80 %)      TEST — {N_PROPRE - int(round(N_PROPRE * 0.8))} lignes (20 %)
    apprentissage, CV, OOF,                                évaluation finale,
    sélection du modèle et du seuil                         lue une seule fois
        |
        v
    PIPELINE : FeaturesPhishing (log1p + interactions + sélection)
               -> imputation médiane -> StandardScaler
               -> régression logistique pondérée
        |
        v
    VALIDATION CROISÉE 5-fold répétée 5 fois -> AUC, AP, OOF
        |
        v
    SEUIL OPTIMISÉ : {SEUIL:.2f}   (coût métier : 5 × FN + FP)
        |
        v
    ÉVALUATION FINALE SUR LE TEST : matrice de confusion, F1, AUC, AP, Brier
        |
        v
    DÉPLOIEMENT : model.joblib + model_meta.json + app.py
    ```
    """)

    st.subheader("2. Comprendre chaque étape")

    st.markdown(f"""
    **Étape 1 — Les données et le nettoyage.** On part de {N_BRUT} observations. Après suppression de
    {N_DOUBLONS} doublons : **{N_PROPRE} messages uniques** — {N_NON} légitimes (`Non`, {N_NON / N_PROPRE:.1%})
    et {N_OUI} malveillants (`Oui`, {N_OUI / N_PROPRE:.1%}).

    *Pourquoi parler de déséquilibre ?* Les messages légitimes sont plus nombreux. Un modèle qui prédit
    toujours `Non` obtient déjà environ {N_NON / N_PROPRE:.1%} d'accuracy, mais il ne détecte aucun phishing.
    L'accuracy seule ne suffit pas : on utilise le **F1 macro**.
    """)

    st.markdown(f"""
    **Étape 2 — Train/Test Split : éviter la fuite de données.**

    | Ensemble | Lignes | Utilisation |
    |---|---|---|
    | Train | {int(round(N_PROPRE * 0.8))} | Apprentissage et optimisation |
    | Test | {N_PROPRE - int(round(N_PROPRE * 0.8))} | Évaluation finale, une seule fois |

    Code : `train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)`.

    - `stratify=y` conserve approximativement la même proportion de `Oui` et `Non` dans les deux ensembles.
    - Le test n'est jamais utilisé pendant l'apprentissage : sinon il y aurait **fuite de données**
      (data leakage) et les résultats seraient trop optimistes.
    """)

    st.markdown("""
    **Étape 3 — Pipeline : préparation des données.**

    ```
    Variables d'entrée
      -> FeaturesPhishing : log1p(âge) + 2 interactions + sélection des variables
      -> Imputation médiane : remplacement des valeurs manquantes
      -> StandardScaler : mise à l'échelle comparable
      -> Régression logistique : class_weight="balanced"
      -> Probabilité P(Oui)
    ```

    *Pourquoi un Pipeline ?* Les transformations sont apprises uniquement sur les données
    d'entraînement de chaque fold. Les informations du fold de validation ne peuvent donc pas
    influencer la préparation : c'est une protection contre la fuite de données.
    """)

    st.markdown("""
    **Étape 4 — Comparaison des modèles.** Six modèles sont comparés :

    1. Dummy Classifier (référence)
    2. KNN
    3. Régression logistique
    4. SVM RBF
    5. Random Forest
    6. Régression logistique améliorée (retenue)

    *Pourquoi comparer plusieurs modèles ?* Pour identifier le meilleur compromis entre performance,
    interprétabilité et coût métier. Le Random Forest a un F1 supérieur au seuil étudié ; la
    **régression logistique améliorée** a la meilleure AUC/AP et la meilleure performance en CV au
    seuil neutre 0,50. Elle est retenue pour sa stabilité et son interprétabilité.
    """)

    st.markdown("""
    | Résultat du modèle retenu | Valeur | Lecture |
    |---|---|---|
    | ROC-AUC | 0,910 | capacité de discrimination |
    | AP | 0,810 | qualité de la courbe Precision-Recall |
    | F1 en CV (seuil neutre 0,50) | 0,814 | stabilité sur le train |
    | F1 Random Forest (seuil 0,50) | 0,771 | comparaison |

    **Attention** : AUC et AP ne déterminent pas directement le coût métier. Elles mesurent d'autres
    aspects de la performance.
    """)

    st.subheader("3. AUC, AP et OOF : leur véritable rôle")

    st.markdown("""
    **A. AUC — capacité à distinguer les deux classes.** AUC = *Area Under the ROC Curve*. Elle mesure
    la capacité du modèle à placer un message malveillant au-dessus d'un message légitime en probabilité.

    Exemple : message A `P(Oui) = 0,90`, message B `P(Oui) = 0,15` → le modèle classe A avant B.
    Une AUC de 0,91 indique une bonne discrimination globale.

    | AUC | Signification |
    |---|---|
    | 0,50 | hasard |
    | 0,60 | faible |
    | 0,70 | acceptable |
    | 0,80 | bon |
    | 0,90 | excellent |

    **Point essentiel** : l'AUC ne dépend pas d'un seuil de décision fixe. Elle évalue le classement
    pour différents seuils.
    """)

    st.markdown("""
    **B. AP — qualité de détection de la classe positive.** AP = *Average Precision*. Elle résume la
    courbe Precision-Recall et répond à : *le modèle retrouve-t-il les messages malveillants sans générer
    trop de fausses alertes ?*

    - **Precision** : parmi les messages déclarés malveillants, combien le sont réellement ?
    - **Recall** : parmi les vrais malveillants, combien sont détectés ?

    L'AP prend en compte le compromis entre les deux sur différents seuils. Ici, la classe positive est
    `Oui` et **AP = 0,810** sur le test.

    **Attention** : AP = 0,81 ne signifie **pas** que 81 % des phishings sont détectés. Ce n'est pas le Recall.
    """)

    st.markdown(f"""
    **C. OOF — obtenir des prédictions hors entraînement.** OOF = *Out-Of-Fold*. On utilise
    `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`, répété 5 fois :

    - {int(round(N_PROPRE * 0.8))} lignes du **train uniquement**, réparties en 5 folds d'environ 83 messages ;
    - **5 répétitions × 5 folds = 25 entraînements** ;
    - chaque ligne reçoit une prédiction quand elle appartient au fold de validation ;
    - les probabilités sont moyennées pour obtenir **une prédiction OOF par ligne**.

    *Pourquoi l'OOF ici ?* Parce qu'on a besoin de probabilités produites par des modèles qui n'ont pas
    appris sur les observations concernées. Ces probabilités servent à choisir le seuil **sans toucher au test**.

    **Attention** : OOF n'est pas une métrique comme AUC ou AP. C'est une **méthode de production de
    prédictions hors fold**.
    """)

    st.subheader("4. Pourquoi choisir le seuil 0,21 au lieu de 0,50")

    st.markdown("""
    Normalement, en classification binaire, on utilise 0,50 : `P(Oui) ≥ 0,50` → Malveillant. Ici, rater
    une attaque coûte **cinq fois plus cher** qu'une fausse alerte. On définit donc :

    **C = 5 × FN + FP**

    avec `FN` = phishing non détecté et `FP` = message légitime déclaré malveillant. On teste différents
    seuils sur les probabilités **OOF du train** :

    | Seuil | FN | FP | Coût |
    |---|---|---|---|
    | 0,20 | 2 | 118 | 128 |
    | **0,21** | 3 | 117 | 132 |
    | 0,22 | 4 | 114 | 134 |

    Le plateau de coût minimal se situe entre 0,20 et 0,22 ; on retient **0,21**, sa médiane. On accepte
    davantage de fausses alertes pour éviter de manquer des attaques. Ce rapport de coûts est une
    **hypothèse métier** à valider par le RSSI.
    """)

    st.subheader("5. Évaluation finale : matrices de confusion")

    st.markdown("""
    **Matrice OOF — train (416 lignes, seuil 0,21)**

    |  | Prédit Non | Prédit Oui |
    |---|---|---|
    | Réel Non | 182 TN | 117 FP |
    | Réel Oui | 3 FN | 114 TP |

    Coût correspondant : `5 × 3 + 117 = 132`.

    **Matrice de confusion — test (104 lignes, seuil 0,21)**

    |  | Prédit Non | Prédit Oui |
    |---|---|---|
    | Réel Non | 47 TN | 28 FP |
    | Réel Oui | 1 FN | 28 TP |

    - **TN** : messages légitimes correctement classés.
    - **FP** : fausses alertes.
    - **FN** : phishing raté.
    - **TP** : phishing correctement détecté.

    | Métrique (test) | Valeur |
    |---|---|
    | F1 macro | 0,712 |
    | ROC-AUC | 0,910 |
    | AP | 0,810 |
    | Brier Score | 0,123 |

    Le **Brier Score** mesure la qualité des probabilités prédites : plus il est proche de 0, mieux c'est.
    """)

    st.subheader("6. Passage vers l'application Streamlit")
    st.markdown("""
    ```
    Utilisateur remplit le formulaire
      -> création de la ligne de données
      -> valeurs manquantes complétées par les médianes du meta
      -> pipeline sauvegardé : features + imputation + standardisation + LR
      -> predict_proba() : calcul de P(Non) et P(Oui)
      -> comparaison avec le seuil 0,21
           P(Oui) >= 0,21 ?  oui -> Malveillant
                             non -> Non malveillant
      -> zone de triage secondaire : NORMAL / VIGILANCE / ALERTE
    ```

    Les trois zones de triage ne sont **pas** trois classes : le modèle reste binaire. Par exemple,
    `P(Oui) = 0,28` donne **Malveillant** (0,28 ≥ 0,21) et la zone **VIGILANCE** (0,28 entre 0,20 et 0,88).
    """)

    st.subheader("7. Points à expliquer correctement en soutenance")
    st.markdown("""
    1. **Cohérence du coût OOF.** Avec TN 182, FP 117, FN 3, TP 114, la somme fait bien 416. Mais le coût
       à 0,21 est `5 × 3 + 117 = 132`. La valeur **128 correspond au seuil 0,20** (`5 × 2 + 118`).
    2. **Interprétation de l'AUC.** Elle est indépendante du seuil, mais une AUC élevée ne garantit **pas**
       un faible nombre de FN : le compromis dépend du seuil choisi.
    3. **CV vs Test.** Le F1 de 0,814 en CV au seuil 0,50 n'est pas directement comparable au F1 macro
       de 0,712 sur le test au seuil 0,21 : seuils et conditions de calcul diffèrent.
    """)

    st.subheader("8. Résumé à mémoriser")
    st.markdown("""
    | Terme | Rôle dans le projet |
    |---|---|
    | Train/Test Split | Séparer apprentissage et évaluation finale |
    | Pipeline | Automatiser la préparation et l'apprentissage |
    | Cross-Validation | Tester la stabilité sur plusieurs découpages |
    | OOF | Produire des prédictions hors entraînement |
    | AUC | Mesurer la capacité de discrimination |
    | AP | Mesurer la qualité de la courbe Precision-Recall |
    | Seuil 0,21 | Décision selon le coût métier |
    | Matrice de confusion | Compter TN, FP, FN et TP |
    | Brier Score | Évaluer la qualité des probabilités |
    | predict_proba() | Obtenir les probabilités dans Streamlit |
    """)

    st.markdown("""
    **La logique fondamentale :**

    1. Je prépare et nettoie mes données.
    2. Je sépare Train et Test pour éviter la fuite.
    3. Je construis un Pipeline pour apprendre les transformations correctement.
    4. Je compare plusieurs modèles avec la validation croisée.
    5. J'utilise AUC et AP pour étudier leur capacité de discrimination.
    6. Je génère des prédictions OOF pour choisir le seuil selon le coût métier.
    7. J'évalue le résultat final sur le Test.
    8. Je déploie le modèle dans Streamlit pour aider un analyste à prioriser les messages suspects.

    C'est cette logique qui donne une cohérence scientifique et métier au projet, au-delà de la simple
    utilisation d'un algorithme de classification.
    """)

st.sidebar.markdown("---")
st.sidebar.caption(CFG["titre"] + " — ISCAE Master VIC")
