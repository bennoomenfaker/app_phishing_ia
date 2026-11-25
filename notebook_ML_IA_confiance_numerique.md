# Détection de messages malveillants — classification binaire supervisée

## 0. Comprendre le phishing

### 0.1 C'est quoi ?
Le **phishing** (hameçonnage), c'est une **arnaque par message** (email, SMS, WhatsApp, etc.).  
L'attaquant se fait passer pour quelqu'un de confiance : banque, collègue, support IT, service de livraison, administration…

### 0.2 Quel est l'objectif de l'attaquant ?
L'objectif est de te faire faire une action qui lui profite, par exemple :
- **Voler tes identifiants** : mot de passe, code, compte.
- **Voler de l'argent** : faux paiement, faux virement.
- **Installer un malware** : via un lien ou une pièce jointe.
- **Entrer dans l'entreprise** : récupérer un accès pour aller plus loin.

### 0.3 Comment fonctionne la logique (étape par étape)
1. **Appât** : l'attaquant envoie un message crédible. Ex. : « Votre compte sera bloqué », « Facture urgente ».
2. **Pression** : il crée l'urgence ou la peur pour que tu agisses vite sans vérifier.
3. **Piège** : le message contient un lien, une pièce jointe, ou demande une information sensible.
4. **Action de la victime** : tu cliques, ouvres, réponds, ou donnes tes informations.
5. **Résultat** : l'attaquant récupère ce qu'il voulait (accès, argent, données).

### 0.4 Exemple concret
> « Votre compte sera désactivé dans 1 heure. Cliquez ici pour vérifier. »

- Tu cliques sur le lien.
- Tu arrives sur un faux site qui ressemble au vrai.
- Tu entres ton mot de passe.
- L'attaquant récupère ton mot de passe.

### 0.5 Pourquoi l'IA rend le phishing plus difficile à repérer
Avant : fautes, texte bizarre, message générique.  
Avec l'IA, un message peut être bien écrit, personnalisé, adapté au ton d'un collègue/service, donc plus crédible. Les anciens signes seuls ne suffisent plus.

### 0.6 Lien avec le projet (logique du modèle)
Le modèle ne « lit » pas comme un humain. Il regarde des **signaux/variables** et combine ces signaux pour estimer une probabilité : **malveillant (Oui)** ou **normal (Non)**.  
C'est une **aide à la décision** : un humain doit vérifier avant de bloquer/supprimer.


## 1. Données, objectif et cadre méthodologique

**Jeu de données synthétique** généré localement pour ce mini-projet (ISCAE Master VIC). Il ne contient **aucun vrai e-mail, aucune donnée personnelle et aucune source externe** à citer. Les performances mesurées ici ne doivent donc **pas** être présentées comme des résultats obtenus sur de vraies campagnes de phishing.

**Objectif — pré-dépistage.** Le modèle trie rapidement les messages pour repérer ceux qui sont suspects.

- **Entrée** : les signaux du message (urgence, liens, âge du domaine, expéditeur connu, etc.).
- **Sortie** : `Oui` (suspect/malveillant) ou `Non` (normal), avec une probabilité.
- **Exemple** : `urgence_score=9`, `nb_liens=5`, `domaine_age_jours=3`, `expediteur_connu=0`, `piece_jointe=1` → le modèle peut prédire **Oui**.

Le résultat est une **aide à la décision** : la vérification finale reste humaine. Aucun message n'est supprimé automatiquement.

**Règle méthodologique appliquée dans tout le notebook.** La séparation train / test est définie au §8, **avant toute statistique descriptive**. Les analyses qui peuvent orienter la modélisation (corrélations, associations, moyennes par classe) sont donc calculées sur le **train seul (416 messages)** ; le test (104 messages) n'est lu qu'au §16 et au §18, pour mesurer. Les contrôles de qualité (types, doublons, valeurs manquantes) portent en revanche sur le fichier brut complet : ils ne servent pas à choisir un modèle.


## 2. Comment choisir un modèle ?

### 2.1 Le contexte
On veut détecter les messages **malveillants (phishing IA)**. Les classes sont déséquilibrées : **374 `Non` / 146 `Oui`** après déduplication. L'erreur la plus grave est le **faux négatif** : un message malveillant prédit `Non`.

### 2.2 Les critères de choix
- **F1 macro** : critère principal, car il donne le même poids aux deux classes malgré le déséquilibre.
- **Rappel de la classe `Oui`** : mesure combien de malveillants sont réellement détectés.
- **Précision / faux positifs** : à surveiller pour éviter de saturer l'analyste.
- **AUC et AP** : qualité du classement, indépendante d'un seuil particulier.
- **Matrice de confusion** : montre les FN et FP en nombres concrets.
- **Simplicité / interprétabilité** : utile pour expliquer une décision à un humain.

### 2.3 Les modèles comparés
| Modèle | Intérêt | Limite |
|---|---|---|
| Régression logistique | Simple, interprétable | Peut rater des relations non linéaires |
| Random Forest | Bon sur les relations non linéaires, robuste | Moins simple à expliquer |
| SVM noyau RBF | Marge maximale, stable en validation croisée | Moins interprétable, plus lent |

### 2.4 La règle de décision (à retenir)
1. Le modèle est choisi **sur le train uniquement**, par validation croisée (§15).
2. Le modèle retenu est ensuite **spécialisé** (`log_age`, interactions) et son **seuil** est appris sur les probabilités hors pli du train (§17).
3. Le **test** n'est lu qu'ensuite, une seule fois, pour mesurer (§16 et §18). La comparaison des trois modèles de référence sur le test est donc **descriptive** : elle n'entre pas dans la sélection.


**Mini-projet 3 — Veille stratégique : IA et confiance numérique**

## 3. Contexte, problématique, dictionnaire des colonnes et feuille de route

### 3.1 Contexte
L'IA générative écrit des messages de phishing sans fautes et avec un ton personnalisé. Les signes classiques (fautes de langue, style maladroit) deviennent donc moins fiables. Un responsable sécurité (RSSI) doit pourtant décider, parmi les messages reçus, lesquels méritent une analyse approfondie. Les 524 lignes du fichier sont **synthétiques** : aucune donnée personnelle, aucun vrai e-mail.

### 3.2 Problématique
> **Comment détecter un message malveillant quand les signes classiques deviennent moins fiables à cause de l'IA, et comment garder un niveau d'alerte explicable ?**

La cible `message_malveillant` est binaire (`Non` / `Oui`), avec **374 `Non` pour 146 `Oui`** après suppression des doublons. L'accuracy seule est trompeuse (prédire toujours `Non` donne déjà ~72 %) : on regarde surtout le **rappel** et le **F1** de la classe `Oui`.

### 3.3 Quelle erreur coûte le plus cher ?
Le **faux négatif** : un message malveillant classé `Non` passe les filtres et peut déclencher une compromission. Le faux positif (message légitime signalé) coûte du temps à l'analyste mais se corrige par validation humaine. On peut donc **baisser le seuil de décision** pour gagner en rappel, en acceptant plus de faux positifs — ce compromis est étudié au §17.

### 3.4 Dictionnaire des colonnes

Un message avec un domaine récent peut mériter une vérification supplémentaire : un âge faible est un indice de risque potentiel, jamais une preuve. Le problème est formulé comme une classification binaire à partir d'indicateurs déjà extraits, pas comme une analyse du contenu, des liens ou de la réputation en temps réel.

| Colonne | Sens interprété | Utilisation |
|---|---|---|
| `date` | Date associée au message | EDA seulement ; exclue des prédicteurs pour éviter d'apprendre une tendance calendaire propre à ce petit échantillon. |
| `heure_envoi` | Heure d'envoi, de 0 à 23 | Prédicteur numérique ; relation potentiellement non linéaire avec le risque. |
| `longueur_message` | Longueur du message (unité non précisée) | Prédicteur ; ne révèle pas à elle seule le caractère malveillant. |
| `nb_liens` | Nombre de liens | Prédicteur ; ne renseigne pas sur la destination ni la sûreté du lien. |
| `urgence_score` | Score d'urgence, 0–10 | Prédicteur ; échelle supposée d'après les valeurs observées. |
| `domaine_age_jours` | Âge du domaine en jours | Prédicteur ; un âge faible peut être un signal, pas une preuve. 10 valeurs manquantes. |
| `fautes_langue` | Nombre d'erreurs linguistiques | Prédicteur ; peut refléter le bruit, la langue ou la qualité de saisie. |
| `expediteur_connu` | Indicateur 0/1 de familiarité | Prédicteur binaire ; définition métier à confirmer avec l'auteur des données. |
| `piece_jointe` | Indicateur 0/1 de présence | Prédicteur binaire ; ne distingue ni le type ni la sûreté du fichier. |
| `personnalisation_score` | Score de personnalisation, 0–10 | Prédicteur ; échelle supposée d'après les valeurs observées. |
| `message_malveillant` | Étiquette `Oui` / `Non` | Cible à prédire ; jamais utilisée comme variable d'entrée. |

Les valeurs des scores et indicateurs sont contrôlées au §6. Les colonnes binaires restent des entiers 0/1. La date est convertie et utilisée pour l'EDA, mais n'entre pas dans le modèle.

### 3.5 Zoom sur `personnalisation_score`

Cet attribut mesure **à quel point un message semble adapté à son destinataire**, au lieu d'être générique.

**Exemple 1 — message générique (score faible)**

> Cher client, votre compte nécessite une vérification. Cliquez ici.

**Exemple 2 — message personnalisé (score plus élevé)**

> Bonjour Faker, votre compte bancaire associé à votre adresse e-mail nécessite une vérification.

**Lecture du score.** Dans ce jeu de données, l'échelle va de **0 à 10** (médiane 5). Bornes illustratives :

| Score | Interprétation |
|---|---|
| 0–2 | Très peu personnalisé |
| 3–4 | Faiblement personnalisé |
| 5–7 | Moyennement personnalisé |
| 8–10 | Fortement personnalisé |

**Rapport avec le phishing (train seul).** Score moyen **4,81** pour `Non`, **5,58** pour `Oui` ; corrélation avec la cible **+0,13** : faible, mais non nulle. Le *spear phishing* exploite des informations personnelles pour gagner la confiance. Attention : **un message très personnalisé n'est pas forcément malveillant** (les banques personnalisent aussi). La variable est conservée, mais elle ne suffit jamais seule : c'est la combinaison avec l'âge du domaine, l'urgence et l'expéditeur inconnu qui produit le verdict.

### 3.6 Comment le modèle prédit-il ? (logique pas à pas)

1. **Séparation d'abord.** Le split 80/20 stratifié (seed 42) est défini au §8, avant toute statistique descriptive. `X` contient les 9 variables explicatives, `y` la cible. Un `assert` vérifie que la cible n'est pas dans `X`.
2. **EDA sur le train.** Corrélations et moyennes par classe sont calculées sur les 416 messages du train : le test ne guide ni le feature engineering ni le choix des variables.
3. **Prétraitement dans le pipeline.** Imputation médiane et standardisation sont ajustées **dans chaque pli d'entraînement**, jamais sur le test.
4. **Comparaison sur le train.** Régression logistique, Random Forest et SVM RBF sont comparés par validation croisée 5-fold sur le train (§15). La baseline majoritaire est écartée : elle prédit toujours `Non` et ne détecte aucune attaque.
5. **Modèle retenu et seuil.** La régression logistique améliorée (`log_age` + interactions) est spécialisée ; son seuil binaire est appris sur les probabilités hors pli du train (§17), pas sur le test.
6. **Explication.** L'importance par permutation est calculée **sur le train** (§19) : elle décrit ce que le modèle utilise, sans relire le test.
7. **Validation humaine.** Une prédiction `Oui` déclenche une vérification, jamais une suppression automatique.

### 3.7 Feuille de route

| Sections | Contenu |
|---|---|
| §4–§7 | Installation, chargement, diagnostic de qualité, nettoyage |
| §8–§9 | Séparation train/test, EDA et corrélations **sur le train seul** |
| §10–§13 | Construction de `X`/`y`, prétraitement, schéma du processus |
| §14–§15 | Modèles candidats, **sélection par validation croisée sur le train** |
| §16–§18 | Comparaison descriptive sur le test, modèle retenu, seuil, évaluation finale |
| §19–§23 | Importance des variables, scénarios, sauvegarde, conclusion, livrables |

Exécuter les cellules dans l'ordre, de haut en bas.


## 4. Installation et importation des bibliothèques

Installer une seule fois les bibliothèques si nécessaire.



```python
# Dans un terminal Jupyter si les bibliothèques ne sont pas installées :
# %pip install pandas numpy matplotlib seaborn scikit-learn joblib

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from IPython.display import display

from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, ConfusionMatrixDisplay
)
from sklearn.inspection import permutation_importance
from sklearn.base import clone
import joblib

RANDOM_STATE = 42
pd.set_option("display.max_columns", None)
sns.set_theme(style="whitegrid")
print("Bibliothèques chargées avec succès.")
```

    Bibliothèques chargées avec succès.


## 5. Chargement du fichier

Le CSV doit être dans le même dossier que ce notebook. Les constantes ci-dessous pointent directement sur le seul fichier utilisé.



```python
# Chargement du dataset
import pandas as pd

df_brut = pd.read_csv('dataset_phishing_ia - dataset_phishing_ia.csv')
TARGET = 'message_malveillant'
ORDER = ['Non', 'Oui']

print('Dimensions (lignes, colonnes) :', df_brut.shape)

```

    Dimensions (lignes, colonnes) : (524, 11)



```python
# Dernières lignes
df_brut.tail()

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>heure_envoi</th>
      <th>longueur_message</th>
      <th>nb_liens</th>
      <th>urgence_score</th>
      <th>domaine_age_jours</th>
      <th>fautes_langue</th>
      <th>expediteur_connu</th>
      <th>piece_jointe</th>
      <th>personnalisation_score</th>
      <th>message_malveillant</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>519</th>
      <td>2026-09-29</td>
      <td>5</td>
      <td>222</td>
      <td>1</td>
      <td>4</td>
      <td>5874.0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>6</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>520</th>
      <td>2026-09-30</td>
      <td>10</td>
      <td>475</td>
      <td>4</td>
      <td>10</td>
      <td>41.0</td>
      <td>4</td>
      <td>0</td>
      <td>0</td>
      <td>7</td>
      <td>Oui</td>
    </tr>
    <tr>
      <th>521</th>
      <td>2026-09-30</td>
      <td>6</td>
      <td>107</td>
      <td>0</td>
      <td>10</td>
      <td>661.0</td>
      <td>2</td>
      <td>1</td>
      <td>1</td>
      <td>6</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>522</th>
      <td>2026-09-30</td>
      <td>14</td>
      <td>509</td>
      <td>0</td>
      <td>4</td>
      <td>1227.0</td>
      <td>2</td>
      <td>1</td>
      <td>0</td>
      <td>5</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>523</th>
      <td>2026-09-30</td>
      <td>21</td>
      <td>507</td>
      <td>1</td>
      <td>4</td>
      <td>800.0</td>
      <td>3</td>
      <td>0</td>
      <td>1</td>
      <td>5</td>
      <td>Non</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Colonnes
df_brut.columns.tolist()

```




    ['date',
     'heure_envoi',
     'longueur_message',
     'nb_liens',
     'urgence_score',
     'domaine_age_jours',
     'fautes_langue',
     'expediteur_connu',
     'piece_jointe',
     'personnalisation_score',
     'message_malveillant']




```python
# Informations générales
df_brut.info()

```

    <class 'pandas.DataFrame'>
    RangeIndex: 524 entries, 0 to 523
    Data columns (total 11 columns):
     #   Column                  Non-Null Count  Dtype  
    ---  ------                  --------------  -----  
     0   date                    524 non-null    str    
     1   heure_envoi             524 non-null    int64  
     2   longueur_message        524 non-null    int64  
     3   nb_liens                524 non-null    int64  
     4   urgence_score           524 non-null    int64  
     5   domaine_age_jours       514 non-null    float64
     6   fautes_langue           524 non-null    int64  
     7   expediteur_connu        524 non-null    int64  
     8   piece_jointe            524 non-null    int64  
     9   personnalisation_score  524 non-null    int64  
     10  message_malveillant     524 non-null    str    
    dtypes: float64(1), int64(8), str(2)
    memory usage: 45.2 KB



```python
print("Statistiques descriptives des variables numériques :")
display(df_brut.describe().T)

print("Statistiques descriptives de toutes les variables :")
display(df_brut.describe(include="all").T)
```

    Statistiques descriptives des variables numériques :



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
      <th>mean</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>heure_envoi</th>
      <td>524.0</td>
      <td>12.238550</td>
      <td>6.889344</td>
      <td>0.0</td>
      <td>6.00</td>
      <td>13.0</td>
      <td>18.00</td>
      <td>23.0</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>524.0</td>
      <td>413.225191</td>
      <td>162.774765</td>
      <td>60.0</td>
      <td>301.50</td>
      <td>423.0</td>
      <td>523.25</td>
      <td>896.0</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>524.0</td>
      <td>1.387405</td>
      <td>1.165433</td>
      <td>0.0</td>
      <td>1.00</td>
      <td>1.0</td>
      <td>2.00</td>
      <td>5.0</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>524.0</td>
      <td>4.519084</td>
      <td>2.373696</td>
      <td>0.0</td>
      <td>3.00</td>
      <td>4.0</td>
      <td>6.00</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>514.0</td>
      <td>739.330739</td>
      <td>761.682914</td>
      <td>1.0</td>
      <td>217.25</td>
      <td>516.0</td>
      <td>951.25</td>
      <td>5874.0</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>524.0</td>
      <td>2.020992</td>
      <td>1.387440</td>
      <td>0.0</td>
      <td>1.00</td>
      <td>2.0</td>
      <td>3.00</td>
      <td>6.0</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>524.0</td>
      <td>0.440840</td>
      <td>0.496962</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>1.00</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>524.0</td>
      <td>0.232824</td>
      <td>0.423035</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>524.0</td>
      <td>4.977099</td>
      <td>2.554090</td>
      <td>0.0</td>
      <td>3.00</td>
      <td>5.0</td>
      <td>7.00</td>
      <td>10.0</td>
    </tr>
  </tbody>
</table>
</div>


    Statistiques descriptives de toutes les variables :



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
      <th>unique</th>
      <th>top</th>
      <th>freq</th>
      <th>mean</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>date</th>
      <td>524</td>
      <td>231</td>
      <td>2026-02-22</td>
      <td>7</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>heure_envoi</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>12.23855</td>
      <td>6.889344</td>
      <td>0.0</td>
      <td>6.0</td>
      <td>13.0</td>
      <td>18.0</td>
      <td>23.0</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>413.225191</td>
      <td>162.774765</td>
      <td>60.0</td>
      <td>301.5</td>
      <td>423.0</td>
      <td>523.25</td>
      <td>896.0</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1.387405</td>
      <td>1.165433</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>2.0</td>
      <td>5.0</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>4.519084</td>
      <td>2.373696</td>
      <td>0.0</td>
      <td>3.0</td>
      <td>4.0</td>
      <td>6.0</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>514.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>739.330739</td>
      <td>761.682914</td>
      <td>1.0</td>
      <td>217.25</td>
      <td>516.0</td>
      <td>951.25</td>
      <td>5874.0</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2.020992</td>
      <td>1.38744</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>2.0</td>
      <td>3.0</td>
      <td>6.0</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.44084</td>
      <td>0.496962</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.232824</td>
      <td>0.423035</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>524.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>4.977099</td>
      <td>2.55409</td>
      <td>0.0</td>
      <td>3.0</td>
      <td>5.0</td>
      <td>7.0</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>message_malveillant</th>
      <td>524</td>
      <td>2</td>
      <td>Non</td>
      <td>377</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



```python
print("Nombre de valeurs distinctes par colonne :")
display(df_brut.nunique().sort_values(ascending=False).to_frame("valeurs_uniques"))

print("Valeurs distinctes de la cible :")
print(df_brut[TARGET].value_counts(dropna=False))


```

    Nombre de valeurs distinctes par colonne :



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>valeurs_uniques</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>domaine_age_jours</th>
      <td>425</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>330</td>
    </tr>
    <tr>
      <th>date</th>
      <td>231</td>
    </tr>
    <tr>
      <th>heure_envoi</th>
      <td>24</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>11</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>11</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>7</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>6</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>2</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>2</td>
    </tr>
    <tr>
      <th>message_malveillant</th>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>


    Valeurs distinctes de la cible :
    message_malveillant
    Non    377
    Oui    147
    Name: count, dtype: int64


## 6. Diagnostic de qualité : valeurs manquantes et doublons

Ce diagnostic porte sur le **fichier brut complet** : il sert à nettoyer avant la séparation train/test, pas à choisir un modèle. Aucune statistique inferentielle (corrélation, moyenne par classe) n'est tirée de cette étape.



```python
tableau = pd.DataFrame({
    "manquants": df_brut.isna().sum(),
     "% manquants": (df_brut.isna().mean() * 100).round(2)
     })

display(tableau)

nb_doublons = df_brut.duplicated().sum()
print(f"Nombre de lignes dupliquées : {nb_doublons}")
print("Nombre de lignes avant nettoyage :", len(df_brut))
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>manquants</th>
      <th>% manquants</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>date</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>heure_envoi</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>10</td>
      <td>1.91</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>message_malveillant</th>
      <td>0</td>
      <td>0.00</td>
    </tr>
  </tbody>
</table>
</div>


    Nombre de lignes dupliquées : 4
    Nombre de lignes avant nettoyage : 524



```python
# Afficher les doublons pour les examiner avant suppression
display(df_brut[df_brut.duplicated(keep=False)].sort_values(by=list(df_brut.columns)).head(20))
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>heure_envoi</th>
      <th>longueur_message</th>
      <th>nb_liens</th>
      <th>urgence_score</th>
      <th>domaine_age_jours</th>
      <th>fautes_langue</th>
      <th>expediteur_connu</th>
      <th>piece_jointe</th>
      <th>personnalisation_score</th>
      <th>message_malveillant</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>71</th>
      <td>2026-02-02</td>
      <td>23</td>
      <td>283</td>
      <td>2</td>
      <td>8</td>
      <td>574.0</td>
      <td>3</td>
      <td>0</td>
      <td>0</td>
      <td>4</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>72</th>
      <td>2026-02-02</td>
      <td>23</td>
      <td>283</td>
      <td>2</td>
      <td>8</td>
      <td>574.0</td>
      <td>3</td>
      <td>0</td>
      <td>0</td>
      <td>4</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>224</th>
      <td>2026-04-26</td>
      <td>18</td>
      <td>528</td>
      <td>0</td>
      <td>5</td>
      <td>789.0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>9</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>225</th>
      <td>2026-04-26</td>
      <td>18</td>
      <td>528</td>
      <td>0</td>
      <td>5</td>
      <td>789.0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>9</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>330</th>
      <td>2026-06-15</td>
      <td>4</td>
      <td>397</td>
      <td>5</td>
      <td>7</td>
      <td>278.0</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>2</td>
      <td>Oui</td>
    </tr>
    <tr>
      <th>331</th>
      <td>2026-06-15</td>
      <td>4</td>
      <td>397</td>
      <td>5</td>
      <td>7</td>
      <td>278.0</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>2</td>
      <td>Oui</td>
    </tr>
    <tr>
      <th>458</th>
      <td>2026-08-30</td>
      <td>17</td>
      <td>377</td>
      <td>0</td>
      <td>3</td>
      <td>627.0</td>
      <td>3</td>
      <td>1</td>
      <td>0</td>
      <td>4</td>
      <td>Non</td>
    </tr>
    <tr>
      <th>459</th>
      <td>2026-08-30</td>
      <td>17</td>
      <td>377</td>
      <td>0</td>
      <td>3</td>
      <td>627.0</td>
      <td>3</td>
      <td>1</td>
      <td>0</td>
      <td>4</td>
      <td>Non</td>
    </tr>
  </tbody>
</table>
</div>


## 7. Nettoyage des données

Le cahier des charges indique que le fichier contient quelques doublons exacts et une colonne numérique avec des valeurs manquantes. On supprime les **4 doublons exacts** (524 → 520 lignes). L'imputation par médiane est faite **dans le pipeline**, donc calculée sur le train de chaque pli : elle ne transmet aucune information issue du test.



```python
# Copie de travail
df = df_brut.copy()
print('Lignes avant :', len(df))

```

    Lignes avant : 524



```python
# Suppression des doublons
nb_avant = len(df)
df = df.drop_duplicates().copy()
print('Doublons supprimés :', nb_avant - len(df))
print('Lignes après :', len(df))

```

    Doublons supprimés : 4
    Lignes après : 520



```python
# Valeurs manquantes
df.isna().sum().to_frame('manquants')

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>manquants</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>date</th>
      <td>0</td>
    </tr>
    <tr>
      <th>heure_envoi</th>
      <td>0</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>0</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>0</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>0</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>10</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>0</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>0</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>0</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>0</td>
    </tr>
    <tr>
      <th>message_malveillant</th>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Types de données
df.dtypes.to_frame('type')

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>date</th>
      <td>str</td>
    </tr>
    <tr>
      <th>heure_envoi</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>float64</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>int64</td>
    </tr>
    <tr>
      <th>message_malveillant</th>
      <td>str</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Vérification simple : la colonne à prédire existe
colonne_cible = 'message_malveillant'
if colonne_cible not in df.columns:
    raise ValueError('Colonne à prédire absente : ' + colonne_cible)
if df[colonne_cible].isna().any():
    print('Attention : valeurs manquantes dans la colonne à prédire.')
else:
    print('OK : la colonne à prédire est présente et complète.')

```

    OK : la colonne à prédire est présente et complète.



```python
# Répartition de la colonne à prédire
df[colonne_cible].value_counts().to_frame('effectif')

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>effectif</th>
    </tr>
    <tr>
      <th>message_malveillant</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Non</th>
      <td>374</td>
    </tr>
    <tr>
      <th>Oui</th>
      <td>146</td>
    </tr>
  </tbody>
</table>
</div>



## 8. Analyse exploratoire — distribution de la cible

Les graphiques servent à comprendre le phénomène avant de modéliser ; ils ne prouvent aucune causalité.

**Point clé anti-fuite.** La séparation train/test est définie **ici**, avant les graphiques, et réutilisée telle quelle au §11. Toutes les statistiques descriptives de l'EDA (répartition, distributions, corrélations, moyennes par classe) portent donc sur les **416 messages du train**. Le test (104 messages) reste vierge jusqu'au §16.



```python
# Séparation définie AVANT toute statistique descriptive (réutilisée au §11).
IDX_TRAIN, IDX_TEST = train_test_split(
    df.index,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=df[TARGET],
)
df_train_eda = df.loc[IDX_TRAIN]
print(f"Train = {len(IDX_TRAIN)} messages | Test réservé = {len(IDX_TEST)} messages (non analysé ici)")

# Graphique 1 : répartition de la variable cible dans le TRAIN (effectifs + pourcentages)
ordre = df_train_eda[TARGET].value_counts().index
counts = df_train_eda[TARGET].value_counts().reindex(ordre)
pct = counts / counts.sum() * 100

fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(data=df_train_eda, x=TARGET, order=ordre, palette=['#4C78A8', '#E45756'], ax=ax)
for i, cls in enumerate(ordre):
    n = int(counts[cls])
    ax.text(i, n + counts.max() * 0.02, f"{n}\n({pct[cls]:.1f} %)",
            ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_ylim(0, counts.max() * 1.18)
ax.set_title(f"Répartition de la cible : {TARGET} — train seul (n = {len(df_train_eda)})")
ax.set_xlabel("Classe")
ax.set_ylabel("Nombre d'observations")
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.show()

print("Effectifs et pourcentages (train) :")
display(pd.DataFrame({"effectif": counts, "pourcentage_%": pct.round(2)}))

```

    Train = 416 messages | Test réservé = 104 messages (non analysé ici)



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_24_1.png)
    


    Effectifs et pourcentages (train) :



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>effectif</th>
      <th>pourcentage_%</th>
    </tr>
    <tr>
      <th>message_malveillant</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Non</th>
      <td>299</td>
      <td>71.88</td>
    </tr>
    <tr>
      <th>Oui</th>
      <td>117</td>
      <td>28.12</td>
    </tr>
  </tbody>
</table>
</div>


### Interprétation — Histogrammes (variables numériques)

**Axes**
- **Abscisse (axe horizontal, X)** : les **valeurs** de la variable.  
  Exemple : pour `urgence_score`, l’axe X va de 0 à 10. Avec `bins=20`, les valeurs sont regroupées en 20 petites tranches.
- **Ordonnée (axe vertical, Y)** : le **nombre de messages** (effectif) dans chaque tranche.  
  Plus la barre est haute, plus il y a de messages avec cette valeur.

**Utilité** : voir la distribution d’une variable (où les valeurs sont concentrées, étalées, rares/extrêmes).

**Comment lire**
- Barre haute = beaucoup de messages dans cette plage.
- Barre basse = peu de messages.
- Pic = valeur/plage la plus fréquente.
- Valeurs isolées = rares/extrêmes.

**Exemples dataset** : `domaine_age_jours` faible peut signaler domaine récent ; `urgence_score` élevé = pression ; `fautes_langue` souvent faible avec IA.



```python
# Graphique 2 : distributions des variables numériques (train seul)
colonnes_num = df_train_eda.select_dtypes(include=np.number).columns.tolist()
if colonnes_num:
    df_train_eda[colonnes_num].hist(figsize=(14, 10), bins=20, edgecolor="black")
    plt.suptitle("Distribution des variables numériques — train seul (416 messages)", y=1.02)
    plt.tight_layout()
    plt.show()
else:
    print("Aucune variable numérique.")

```


    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_26_0.png)
    


### Médianes par classe — valeurs réelles sur le train

Le notebook affiche les **moyennes** puis les **médianes** par classe, calculées sur le train seul (416 messages). La médiane est plus robuste que la moyenne quand une variable est très asymétrique, comme `domaine_age_jours`.

| Variable | Médiane `Non` | Médiane `Oui` | Lecture |
|---|---:|---:|---|
| `domaine_age_jours` | 650,0 | 234,5 | Domaine bien plus jeune côté malveillant ; les quartiles `Non` vont de 325 à 1 175 jours, ceux de `Oui` de 72 à 504. |
| `urgence_score` | 4,0 | 6,0 | Pression temporelle plus forte côté malveillant. |
| `nb_liens` | 1,0 | 2,0 | Un lien de plus en médiane côté malveillant. |
| `longueur_message` | 432,0 | 397,0 | Écart faible, distributions très chevauchantes. |
| `heure_envoi` | 12,0 | 13,0 | Pratiquement identique. |
| `fautes_langue` | 2,0 | 2,0 | Aucune différence : l'IA écrit correctement. |
| `personnalisation_score` | 5,0 | 6,0 | Léger décalage seulement. |
| `expediteur_connu` | 1,0 | 0,0 | Expéditeur plus souvent inconnu côté malveillant. |

**Lecture détaillée**

- **Âge du domaine** : un domaine récent est typique du phishing, car les attaquants enregistrent des domaines jetables. C'est la variable qui sépare le mieux. Sa distribution est très asymétrique : les valeurs jusqu'à 5 874 jours chez les `Non` sont de vieux domaines légitimes, pas des erreurs. D'où `log1p(âge)` dans le modèle amélioré.
- **Urgence et liens** : les messages malveillants poussent à agir vite et contiennent plus de liens. Ces deux signaux sont cohérents avec le phishing, mais chacun se chevauche beaucoup avec les messages normaux.
- **Longueur et heure d'envoi** : le décalage est faible, donc ces variables aident peu seules.
- **Fautes de langue** : aucune différence. C'est le résultat le plus intéressant pour un projet « IA et confiance numérique » : les faux messages écrits par une IA sont souvent sans fautes, donc la faute d'orthographe ne permet plus de détecter le phishing. C'est une explication possible ; il faudrait la confirmer avec la façon dont le dataset a été construit.

**Conclusion** : aucune variable ne suffit seule, sauf peut-être l'âge du domaine. Classement : `domaine_age_jours > urgence_score > nb_liens > longueur_message > heure_envoi > fautes_langue`.


```python
# Colonnes à ignorer (calendrier) et cible — graphiques sur le TRAIN seul
IGNORER = [TARGET, "date", "semaine"]

# 1) Catégorielles (texte)
cols_cat = [c for c in df_train_eda.select_dtypes(include=["object", "category", "bool"]).columns
            if c not in IGNORER]

# 2) Numériques discrètes (ex. 0/1, scores 0-10, petits compteurs)
cols_discretes = [c for c in df_train_eda.select_dtypes(include="number").columns
                  if c not in IGNORER and df_train_eda[c].nunique(dropna=True) <= 15]

cols_a_tracer = [c for c in cols_cat + cols_discretes if df_train_eda[c].nunique(dropna=True) <= 15]
print("Variables tracées :", cols_a_tracer)

if not cols_a_tracer:
    print("Aucune variable catégorielle ou discrète à tracer.")

total = len(df_train_eda)
for col in cols_a_tracer:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.countplot(data=df_train_eda, x=col, hue=TARGET, ax=ax)
    for p in ax.patches:
        h = p.get_height()
        if h and not np.isnan(h):
            ax.annotate(f"{int(h)}\n({h/total*100:.1f} %)",
                        (p.get_x() + p.get_width() / 2, h),
                        ha="center", va="bottom", fontsize=7.5)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.18)
    ax.set_title(f"Répartition de {TARGET} selon {col} — train (n = {total})")
    ax.tick_params(axis="x", rotation=25)
    plt.tight_layout()
    plt.show()

```

    Variables tracées : ['nb_liens', 'urgence_score', 'fautes_langue', 'expediteur_connu', 'piece_jointe', 'personnalisation_score']



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_28_1.png)
    



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_28_2.png)
    



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_28_3.png)
    



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_28_4.png)
    



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_28_5.png)
    



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_28_6.png)
    


## 9. Corrélations sur le train seul (416 messages)

La corrélation de Pearson mesure une association **linéaire** entre variables numériques. Elle ne s'applique pas directement aux catégories nominales. On encode temporairement la cible pour visualiser une association exploratoire, mais le code numérique des classes n'est pas une distance naturelle. Une corrélation ne signifie jamais causalité.

**Pourquoi le train seul ?** Ces corrélations peuvent guider le feature engineering. Si elles étaient calculées sur les 520 lignes, les 104 messages du test influenceraient indirectement les choix de modélisation : c'est une fuite. Le graphique ci-dessous porte donc uniquement sur `df_train_eda` (416 lignes).


### Comment lire une matrice de corrélation

**1. La structure** : chaque case croise la variable de sa ligne avec celle de sa colonne. La matrice est symétrique (case A,B = case B,A), donc on lit surtout une moitié.

**2. La diagonale** : toujours 1,00 car une variable est parfaitement corrélée avec elle-même. On l'ignore.

**3. Le nombre (coefficient de Pearson r, entre -1 et +1)**
- `+1` : quand l'une augmente, l'autre augmente.
- `-1` : quand l'une augmente, l'autre diminue.
- `0` : aucun lien linéaire.
- Repères indicatifs : `|r| < 0,3` faible, `0,3 à 0,7` modéré, `> 0,7` fort.

**4. La couleur** : rouge = positif, bleu = négatif, gris clair = proche de 0.



```python
# Corrélations entre les variables explicatives ET la cible — TRAIN SEUL
# La cible est incluse (encodée Oui = 1) pour voir son association avec chaque variable.
# Les variables calendaires (date, semaine) restent exclues.

IGNORER = ["date", "semaine"]

num_features_eda = [
    c for c in df_train_eda.select_dtypes(include="number").columns
    if c not in IGNORER
]

# Encodage temporaire de la cible, uniquement pour la corrélation : Oui = 1, Non = 0
df_corr = df_train_eda[num_features_eda].copy()
df_corr["cible (Oui = 1)"] = (df_train_eda[TARGET] == "Oui").astype(int)

corr = df_corr.corr(method="pearson")

plt.figure(figsize=(12, 9))

sns.heatmap(
    corr,
    annot=True,
    cmap="vlag",
    center=0,
    vmin=-1,
    vmax=1,
    fmt=".2f",
    linewidths=0.5
)

plt.title(f"Corrélations de Pearson — TRAIN seul ({len(df_train_eda)} messages) — variables + cible")
plt.tight_layout()
plt.show()

display(corr.round(3))

# La dernière ligne / colonne donne l'association de chaque variable avec la cible.
display(corr["cible (Oui = 1)"].drop("cible (Oui = 1)").sort_values(key=abs, ascending=False).round(3).to_frame())
print("Nombre de lignes utilisées :", len(df_train_eda), "(test exclu)")

```


    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_31_0.png)
    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>heure_envoi</th>
      <th>longueur_message</th>
      <th>nb_liens</th>
      <th>urgence_score</th>
      <th>domaine_age_jours</th>
      <th>fautes_langue</th>
      <th>expediteur_connu</th>
      <th>piece_jointe</th>
      <th>personnalisation_score</th>
      <th>cible (Oui = 1)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>heure_envoi</th>
      <td>1.000</td>
      <td>-0.051</td>
      <td>0.001</td>
      <td>0.050</td>
      <td>0.002</td>
      <td>-0.001</td>
      <td>-0.016</td>
      <td>0.005</td>
      <td>-0.010</td>
      <td>-0.027</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>-0.051</td>
      <td>1.000</td>
      <td>0.006</td>
      <td>-0.054</td>
      <td>-0.000</td>
      <td>0.033</td>
      <td>0.010</td>
      <td>0.008</td>
      <td>-0.045</td>
      <td>-0.114</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>0.001</td>
      <td>0.006</td>
      <td>1.000</td>
      <td>0.006</td>
      <td>0.050</td>
      <td>-0.046</td>
      <td>0.025</td>
      <td>0.051</td>
      <td>-0.030</td>
      <td>0.244</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>0.050</td>
      <td>-0.054</td>
      <td>0.006</td>
      <td>1.000</td>
      <td>-0.009</td>
      <td>-0.008</td>
      <td>0.069</td>
      <td>-0.017</td>
      <td>-0.028</td>
      <td>0.285</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>0.002</td>
      <td>-0.000</td>
      <td>0.050</td>
      <td>-0.009</td>
      <td>1.000</td>
      <td>-0.001</td>
      <td>0.089</td>
      <td>-0.010</td>
      <td>0.028</td>
      <td>-0.322</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>-0.001</td>
      <td>0.033</td>
      <td>-0.046</td>
      <td>-0.008</td>
      <td>-0.001</td>
      <td>1.000</td>
      <td>-0.002</td>
      <td>-0.022</td>
      <td>0.024</td>
      <td>-0.022</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>-0.016</td>
      <td>0.010</td>
      <td>0.025</td>
      <td>0.069</td>
      <td>0.089</td>
      <td>-0.002</td>
      <td>1.000</td>
      <td>-0.067</td>
      <td>-0.051</td>
      <td>-0.278</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>0.005</td>
      <td>0.008</td>
      <td>0.051</td>
      <td>-0.017</td>
      <td>-0.010</td>
      <td>-0.022</td>
      <td>-0.067</td>
      <td>1.000</td>
      <td>0.033</td>
      <td>0.060</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>-0.010</td>
      <td>-0.045</td>
      <td>-0.030</td>
      <td>-0.028</td>
      <td>0.028</td>
      <td>0.024</td>
      <td>-0.051</td>
      <td>0.033</td>
      <td>1.000</td>
      <td>0.133</td>
    </tr>
    <tr>
      <th>cible (Oui = 1)</th>
      <td>-0.027</td>
      <td>-0.114</td>
      <td>0.244</td>
      <td>0.285</td>
      <td>-0.322</td>
      <td>-0.022</td>
      <td>-0.278</td>
      <td>0.060</td>
      <td>0.133</td>
      <td>1.000</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cible (Oui = 1)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>domaine_age_jours</th>
      <td>-0.322</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>0.285</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>-0.278</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>0.244</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>0.133</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>-0.114</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>0.060</td>
    </tr>
    <tr>
      <th>heure_envoi</th>
      <td>-0.027</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>-0.022</td>
    </tr>
  </tbody>
</table>
</div>


    Nombre de lignes utilisées : 416 (test exclu)


### Lecture de la matrice — valeurs réelles sur le train

- **Entre variables explicatives** : toutes les corrélations sont très faibles, avec `|r| ≤ 0,09`. Les plus fortes sont `expediteur_connu` / `domaine_age_jours` (**+0,089**), `urgence_score` / `expediteur_connu` (**+0,069**) et `piece_jointe` / `expediteur_connu` (**−0,067**). Aucune redondance, aucune multicolinéarité problématique : les 9 variables peuvent être conservées.
- **Avec la cible** (dernière ligne / colonne) : `domaine_age_jours` **−0,322**, `urgence_score` **+0,285**, `expediteur_connu` **−0,278**, `nb_liens` **+0,244**, `personnalisation_score` **+0,133**, `longueur_message` **−0,114**. Les autres sont quasi nulles (`piece_jointe` +0,060, `heure_envoi` −0,027, `fautes_langue` −0,022).
- **Lecture des signes** : un domaine jeune, un expéditeur inconnu, une urgence élevée et beaucoup de liens vont de pair avec la malveillance.
- ⚠️ La cible est binaire : le coefficient est une **corrélation point-bisérielle** (cas particulier de Pearson). Il se lit comme un lien linéaire, jamais comme une causalité ; encoder `Oui = 1` sert seulement à visualiser, le modèle ne voit jamais la cible dans `X`.
- Cette matrice ne mesure que le linéaire : le **SVM RBF** peut capter des interactions qu'elle ne montre pas.
- Ces valeurs sont calculées **sur le train** : elles ne dépendent pas des 104 messages du test.



```python
# Association de chaque variable avec la cible (Oui = 1) — TRAIN SEUL
# Pearson avec une variable binaire = corrélation point-bisérielle.
y_train_eda = (df_train_eda[TARGET] == "Oui").astype(int)

association = (
    df_train_eda[num_features_eda]
    .corrwith(y_train_eda, method="pearson")
    .rename("corrélation_avec_Oui")
    .sort_values(key=abs, ascending=False)
    .to_frame()
)
display(association.round(3))

fig, ax = plt.subplots(figsize=(8, 4.5))
vals = association["corrélation_avec_Oui"][::-1]
colors = ["#d62728" if v > 0 else "#1f77b4" for v in vals]
ax.barh(vals.index, vals.values, color=colors)
for i, v in enumerate(vals.values):
    ax.text(v + (0.006 if v >= 0 else -0.006), i, f"{v:+.3f}",
            va="center", ha="left" if v >= 0 else "right", fontsize=8)
ax.axvline(0, color="k", lw=0.8)
ax.set_xlim(-0.42, 0.42)
ax.set_title(f"Association avec la cible (Oui = 1) — train seul ({len(df_train_eda)} messages)")
ax.set_xlabel("coefficient r")
plt.tight_layout()
plt.show()

```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>corrélation_avec_Oui</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>domaine_age_jours</th>
      <td>-0.322</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>0.285</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>-0.278</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>0.244</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>0.133</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>-0.114</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>0.060</td>
    </tr>
    <tr>
      <th>heure_envoi</th>
      <td>-0.027</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>-0.022</td>
    </tr>
  </tbody>
</table>
</div>



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_33_1.png)
    


**🔎 À retenir pour la modélisation** : les quatre signaux les plus associés à la malveillance sont l'**âge du domaine**, l'**urgence**, l'**expéditeur inconnu** et le **nombre de liens**. `personnalisation_score` (+0,133) et `longueur_message` (−0,114) restent faibles ; `piece_jointe`, `heure_envoi` et `fautes_langue` sont pratiquement nuls.

C'est cohérent avec l'effet de l'IA générative : un message bien écrit, personnalisé et sans faute peut parfaitement être malveillant. Aucune variable ne décide seule ; le modèle les combine. Corrélation ≠ causalité, et rien ici ne prouve qu'une variable *cause* le phishing.


### Comment lire le tableau des moyennes par classe

Ce tableau compare la moyenne des variables pour les messages `Non` (normaux) et `Oui` (malveillants), **sur le train seul**. Les **médianes** sont affichées juste en dessous, puis commentées au §9.1.

| Variable | Lecture sur ton résultat |
|---|---|
| `heure_envoi` | 12,31 vs 11,89 : presque identique, peu discriminant. |
| `longueur_message` | 424,32 (Non) vs 382,06 (Oui) : messages un peu plus courts côté malveillant, différence modérée. |
| `nb_liens` | 1,20 vs 1,83 : les malveillants contiennent en moyenne plus de liens. |
| `urgence_score` | 4,15 vs 5,63 : les malveillants sont plus urgents. |
| `domaine_age_jours` | 886,66 vs 340,72 : les malveillants viennent de domaines beaucoup plus récents. |
| `fautes_langue` | 2,04 vs 1,97 : quasi identique (l'IA écrit correctement). |
| `expediteur_connu` | 0,54 vs 0,23 : les malveillants viennent plus souvent d'expéditeurs inconnus. |
| `piece_jointe` | 0,22 vs 0,27 : un peu plus de pièces jointes côté malveillant. |
| `personnalisation_score` | 4,81 vs 5,58 : légèrement plus personnalisés côté malveillant. |

**À retenir** : `domaine_age_jours`, `urgence_score`, `expediteur_connu` et `nb_liens` sont les signaux les plus marqués. Une moyenne ne suffit jamais à décider seule.



```python
# Comparaison exploratoire des variables numériques par classe — TRAIN SEUL
if num_features_eda:
    moyennes_par_classe = df_train_eda.groupby(TARGET, observed=False)[num_features_eda].mean().T
    print("Moyennes par classe (train) :")
    display(moyennes_par_classe.round(2))

    medianes_par_classe = df_train_eda.groupby(TARGET, observed=False)[num_features_eda].median().T
    print("Médianes par classe (train) :")
    display(medianes_par_classe.round(1))

```

    Moyennes par classe (train) :



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>message_malveillant</th>
      <th>Non</th>
      <th>Oui</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>heure_envoi</th>
      <td>12.31</td>
      <td>11.89</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>424.32</td>
      <td>382.06</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>1.20</td>
      <td>1.83</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>4.15</td>
      <td>5.63</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>886.66</td>
      <td>340.72</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>2.04</td>
      <td>1.97</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>0.54</td>
      <td>0.23</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>0.22</td>
      <td>0.27</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>4.81</td>
      <td>5.58</td>
    </tr>
  </tbody>
</table>
</div>


    Médianes par classe (train) :



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>message_malveillant</th>
      <th>Non</th>
      <th>Oui</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>heure_envoi</th>
      <td>12.0</td>
      <td>13.0</td>
    </tr>
    <tr>
      <th>longueur_message</th>
      <td>432.0</td>
      <td>397.0</td>
    </tr>
    <tr>
      <th>nb_liens</th>
      <td>1.0</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>urgence_score</th>
      <td>4.0</td>
      <td>6.0</td>
    </tr>
    <tr>
      <th>domaine_age_jours</th>
      <td>650.0</td>
      <td>234.5</td>
    </tr>
    <tr>
      <th>fautes_langue</th>
      <td>2.0</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>expediteur_connu</th>
      <td>1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>piece_jointe</th>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>personnalisation_score</th>
      <td>5.0</td>
      <td>6.0</td>
    </tr>
  </tbody>
</table>
</div>


## 10. Construction de `X` et `y`

- `y` contient uniquement la variable cible.
- `X` contient les variables explicatives.
- Les colonnes de date et de semaine sont exclues : sans justification métier, elles feraient apprendre le calendrier plutôt que le phénomène.
- La cible est explicitement retirée de `X` pour éviter la fuite de données.



```python
# Retirer la colonne à prédire et la date
colonnes_a_retirer = ['message_malveillant', 'date']
X = df.drop(columns=[c for c in colonnes_a_retirer if c in df.columns]).copy()
y = df['message_malveillant'].copy()

print('Colonnes utilisées (X) :', X.columns.tolist())
print('Colonne à prédire (y) : message_malveillant')

```

    Colonnes utilisées (X) : ['heure_envoi', 'longueur_message', 'nb_liens', 'urgence_score', 'domaine_age_jours', 'fautes_langue', 'expediteur_connu', 'piece_jointe', 'personnalisation_score']
    Colonne à prédire (y) : message_malveillant



```python
# Colonnes numériques et catégorielles
features_num = X.select_dtypes(include='number').columns.tolist()
features_cat = X.select_dtypes(exclude='number').columns.tolist()

print('Numériques :', features_num)
print('Catégorielles :', features_cat)

```

    Numériques : ['heure_envoi', 'longueur_message', 'nb_liens', 'urgence_score', 'domaine_age_jours', 'fautes_langue', 'expediteur_connu', 'piece_jointe', 'personnalisation_score']
    Catégorielles : []


## 11. Séparation train / test

La séparation a déjà été définie au §8 pour permettre une EDA sans fuite. On la matérialise ici en `X_train` / `X_test` : **les mêmes indices** sont réutilisés, ce qu'un `assert` vérifie. `stratify=y` conserve la proportion de chaque classe.

Le test ne sera pas utilisé pour ajuster les transformations, choisir un modèle ni régler le seuil.



```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y
)

# Preuve que l'EDA du §8 a bien porté sur exactement ce train.
assert list(X_train.index) == list(IDX_TRAIN), "Split incohérent avec celui défini au §8"
assert list(X_test.index) == list(IDX_TEST), "Split incohérent avec celui défini au §8"

print("Train :", X_train.shape, y_train.shape)
print("Test  :", X_test.shape, y_test.shape)
print("\nRépartition des classes — train (%)")
display((y_train.value_counts(normalize=True) * 100).round(2))
print("\nRépartition des classes — test (%)")
display((y_test.value_counts(normalize=True) * 100).round(2))

```

    Train : (416, 9) (416,)
    Test  : (104, 9) (104,)
    
    Répartition des classes — train (%)



    message_malveillant
    Non    71.88
    Oui    28.12
    Name: proportion, dtype: float64


    
    Répartition des classes — test (%)



    message_malveillant
    Non    72.12
    Oui    27.88
    Name: proportion, dtype: float64


## 12. Prétraitement avec `ColumnTransformer`

- Variables numériques : imputation par la médiane puis standardisation.
- Variables catégorielles : imputation par la modalité la plus fréquente puis one-hot encoding.
- `handle_unknown="ignore"` traite une catégorie inconnue rencontrée plus tard.

Les transformations sont intégrées aux pipelines : elles sont ajustées **uniquement sur l'entraînement de chaque pli**, jamais sur le test.



```python
transformations = []

if features_num:
    pipeline_num = Pipeline(steps=[
        ("imputation", SimpleImputer(strategy="median")),
        ("standardisation", StandardScaler())
    ])
    transformations.append(("numerique", pipeline_num, features_num))



preprocesseur = ColumnTransformer(transformers=transformations, remainder="drop")
print("Préprocesseur prêt.")
display(preprocesseur)
```

    Préprocesseur prêt.



<style>#sk-container-id-1 {
  /* Definition of color scheme common for light and dark mode */
  --sklearn-color-text: #000;
  --sklearn-color-text-muted: #666;
  --sklearn-color-line: gray;
  /* Definition of color scheme for unfitted estimators */
  --sklearn-color-unfitted-level-0: #fff5e6;
  --sklearn-color-unfitted-level-1: #f6e4d2;
  --sklearn-color-unfitted-level-2: #ffe0b3;
  --sklearn-color-unfitted-level-3: chocolate;
  /* Definition of color scheme for fitted estimators */
  --sklearn-color-fitted-level-0: #f0f8ff;
  --sklearn-color-fitted-level-1: #d4ebff;
  --sklearn-color-fitted-level-2: #b3dbfd;
  --sklearn-color-fitted-level-3: cornflowerblue;
}

#sk-container-id-1.light {
  /* Specific color for light theme */
  --sklearn-color-text-on-default-background: black;
  --sklearn-color-background: white;
  --sklearn-color-border-box: black;
  --sklearn-color-icon: #696969;
}

#sk-container-id-1.dark {
  --sklearn-color-text-on-default-background: white;
  --sklearn-color-background: #111;
  --sklearn-color-border-box: white;
  --sklearn-color-icon: #878787;
}

#sk-container-id-1 {
  color: var(--sklearn-color-text);
}

#sk-container-id-1 pre {
  padding: 0;
}

#sk-container-id-1 input.sk-hidden--visually {
  border: 0;
  clip: rect(1px 1px 1px 1px);
  clip: rect(1px, 1px, 1px, 1px);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
}

#sk-container-id-1 div.sk-dashed-wrapped {
  border: 1px dashed var(--sklearn-color-line);
  margin: 0 0.4em 0.5em 0.4em;
  box-sizing: border-box;
  padding-bottom: 0.4em;
  background-color: var(--sklearn-color-background);
}

#sk-container-id-1 div.sk-container {
  /* jupyter's `normalize.less` sets `[hidden] { display: none; }`
     but bootstrap.min.css set `[hidden] { display: none !important; }`
     so we also need the `!important` here to be able to override the
     default hidden behavior on the sphinx rendered scikit-learn.org.
     See: https://github.com/scikit-learn/scikit-learn/issues/21755 */
  display: inline-block !important;
  position: relative;
}

#sk-container-id-1 div.sk-text-repr-fallback {
  display: none;
}

div.sk-parallel-item,
div.sk-serial,
div.sk-item {
  /* draw centered vertical line to link estimators */
  background-image: linear-gradient(var(--sklearn-color-text-on-default-background), var(--sklearn-color-text-on-default-background));
  background-size: 2px 100%;
  background-repeat: no-repeat;
  background-position: center center;
}

/* Parallel-specific style estimator block */

#sk-container-id-1 div.sk-parallel-item::after {
  content: "";
  width: 100%;
  border-bottom: 2px solid var(--sklearn-color-text-on-default-background);
  flex-grow: 1;
}

#sk-container-id-1 div.sk-parallel {
  display: flex;
  align-items: stretch;
  justify-content: center;
  background-color: var(--sklearn-color-background);
  position: relative;
}

#sk-container-id-1 div.sk-parallel-item {
  display: flex;
  flex-direction: column;
}

#sk-container-id-1 div.sk-parallel-item:first-child::after {
  align-self: flex-end;
  width: 50%;
}

#sk-container-id-1 div.sk-parallel-item:last-child::after {
  align-self: flex-start;
  width: 50%;
}

#sk-container-id-1 div.sk-parallel-item:only-child::after {
  width: 0;
}

/* Serial-specific style estimator block */

#sk-container-id-1 div.sk-serial {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: var(--sklearn-color-background);
  padding-right: 1em;
  padding-left: 1em;
}


/* Toggleable style: style used for estimator/Pipeline/ColumnTransformer box that is
clickable and can be expanded/collapsed.
- Pipeline and ColumnTransformer use this feature and define the default style
- Estimators will overwrite some part of the style using the `sk-estimator` class
*/

/* Pipeline and ColumnTransformer style (default) */

#sk-container-id-1 div.sk-toggleable {
  /* Default theme specific background. It is overwritten whether we have a
  specific estimator or a Pipeline/ColumnTransformer */
  background-color: var(--sklearn-color-background);
}

/* Toggleable label */
#sk-container-id-1 label.sk-toggleable__label {
  cursor: pointer;
  display: flex;
  width: 100%;
  margin-bottom: 0;
  padding: 0.5em;
  box-sizing: border-box;
  text-align: center;
  align-items: center;
  justify-content: center;
  gap: 0.5em;
}

#sk-container-id-1 label.sk-toggleable__label .caption {
  font-size: 0.6rem;
  font-weight: lighter;
  color: var(--sklearn-color-text-muted);
}

#sk-container-id-1 label.sk-toggleable__label-arrow:before {
  /* Arrow on the left of the label */
  content: "▸";
  float: left;
  margin-right: 0.25em;
  color: var(--sklearn-color-icon);
}

#sk-container-id-1 label.sk-toggleable__label-arrow:hover:before {
  color: var(--sklearn-color-text);
}

/* Toggleable content - dropdown */

#sk-container-id-1 div.sk-toggleable__content {
  display: none;
  text-align: left;
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-1 div.sk-toggleable__content.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

#sk-container-id-1 div.sk-toggleable__content pre {
  margin: 0.2em;
  border-radius: 0.25em;
  color: var(--sklearn-color-text);
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-1 div.sk-toggleable__content.fitted pre {
  /* unfitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

#sk-container-id-1 input.sk-toggleable__control:checked~div.sk-toggleable__content {
  /* Expand drop-down */
  display: block;
  width: 100%;
  overflow: visible;
}

#sk-container-id-1 input.sk-toggleable__control:checked~label.sk-toggleable__label-arrow:before {
  content: "▾";
}

/* Pipeline/ColumnTransformer-specific style */

#sk-container-id-1 div.sk-label input.sk-toggleable__control:checked~label.sk-toggleable__label {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-1 div.sk-label.fitted input.sk-toggleable__control:checked~label.sk-toggleable__label {
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Estimator-specific style */

/* Colorize estimator box */
#sk-container-id-1 div.sk-estimator input.sk-toggleable__control:checked~label.sk-toggleable__label {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-1 div.sk-estimator.fitted input.sk-toggleable__control:checked~label.sk-toggleable__label {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-2);
}

#sk-container-id-1 div.sk-label label.sk-toggleable__label,
#sk-container-id-1 div.sk-label label {
  /* The background is the default theme color */
  color: var(--sklearn-color-text-on-default-background);
}

/* On hover, darken the color of the background */
#sk-container-id-1 div.sk-label:hover label.sk-toggleable__label {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-unfitted-level-2);
}

/* Label box, darken color on hover, fitted */
#sk-container-id-1 div.sk-label.fitted:hover label.sk-toggleable__label.fitted {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Estimator label */

#sk-container-id-1 div.sk-label label {
  font-family: monospace;
  font-weight: bold;
  line-height: 1.2em;
}

#sk-container-id-1 div.sk-label-container {
  text-align: center;
}

/* Estimator-specific */
#sk-container-id-1 div.sk-estimator {
  font-family: monospace;
  border: 1px dotted var(--sklearn-color-border-box);
  border-radius: 0.25em;
  box-sizing: border-box;
  margin-bottom: 0.5em;
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-1 div.sk-estimator.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

/* on hover */
#sk-container-id-1 div.sk-estimator:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-1 div.sk-estimator.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Specification for estimator info (e.g. "i" and "?") */

/* Common style for "i" and "?" */

.sk-estimator-doc-link,
a:link.sk-estimator-doc-link,
a:visited.sk-estimator-doc-link {
  float: right;
  font-size: smaller;
  line-height: 1em;
  font-family: monospace;
  background-color: var(--sklearn-color-unfitted-level-0);
  border-radius: 1em;
  height: 1em;
  width: 1em;
  text-decoration: none !important;
  margin-left: 0.5em;
  text-align: center;
  /* unfitted */
  border: var(--sklearn-color-unfitted-level-3) 1pt solid;
  color: var(--sklearn-color-unfitted-level-3);
}

.sk-estimator-doc-link.fitted,
a:link.sk-estimator-doc-link.fitted,
a:visited.sk-estimator-doc-link.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
  border: var(--sklearn-color-fitted-level-3) 1pt solid;
  color: var(--sklearn-color-fitted-level-3);
}

/* On hover */
div.sk-estimator:hover .sk-estimator-doc-link:hover,
.sk-estimator-doc-link:hover,
div.sk-label-container:hover .sk-estimator-doc-link:hover,
.sk-estimator-doc-link:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-3);
  border: var(--sklearn-color-fitted-level-0) 1pt solid;
  color: var(--sklearn-color-unfitted-level-0);
  text-decoration: none;
}

div.sk-estimator.fitted:hover .sk-estimator-doc-link.fitted:hover,
.sk-estimator-doc-link.fitted:hover,
div.sk-label-container:hover .sk-estimator-doc-link.fitted:hover,
.sk-estimator-doc-link.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-3);
  border: var(--sklearn-color-fitted-level-0) 1pt solid;
  color: var(--sklearn-color-fitted-level-0);
  text-decoration: none;
}

/* Span, style for the box shown on hovering the info icon */
.sk-estimator-doc-link span {
  display: none;
  z-index: 9999;
  position: relative;
  font-weight: normal;
  right: .2ex;
  padding: .5ex;
  margin: .5ex;
  width: min-content;
  min-width: 20ex;
  max-width: 50ex;
  color: var(--sklearn-color-text);
  box-shadow: 2pt 2pt 4pt #999;
  /* unfitted */
  background: var(--sklearn-color-unfitted-level-0);
  border: .5pt solid var(--sklearn-color-unfitted-level-3);
}

.sk-estimator-doc-link.fitted span {
  /* fitted */
  background: var(--sklearn-color-fitted-level-0);
  border: var(--sklearn-color-fitted-level-3);
}

.sk-estimator-doc-link:hover span {
  display: block;
}

/* "?"-specific style due to the `<a>` HTML tag */

#sk-container-id-1 a.estimator_doc_link {
  float: right;
  font-size: 1rem;
  line-height: 1em;
  font-family: monospace;
  background-color: var(--sklearn-color-unfitted-level-0);
  border-radius: 1rem;
  height: 1rem;
  width: 1rem;
  text-decoration: none;
  /* unfitted */
  color: var(--sklearn-color-unfitted-level-1);
  border: var(--sklearn-color-unfitted-level-1) 1pt solid;
}

#sk-container-id-1 a.estimator_doc_link.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
  border: var(--sklearn-color-fitted-level-1) 1pt solid;
  color: var(--sklearn-color-fitted-level-1);
}

/* On hover */
#sk-container-id-1 a.estimator_doc_link:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-3);
  color: var(--sklearn-color-background);
  text-decoration: none;
}

#sk-container-id-1 a.estimator_doc_link.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-3);
}

.estimator-table {
    font-family: monospace;
}

.estimator-table summary {
    padding: .5rem;
    cursor: pointer;
}

.estimator-table summary::marker {
    font-size: 0.7rem;
}

.estimator-table details[open] {
    padding-left: 0.1rem;
    padding-right: 0.1rem;
    padding-bottom: 0.3rem;
}

.estimator-table .parameters-table {
    margin-left: auto !important;
    margin-right: auto !important;
    margin-top: 0;
}

.estimator-table .parameters-table tr:nth-child(odd) {
    background-color: #fff;
}

.estimator-table .parameters-table tr:nth-child(even) {
    background-color: #f6f6f6;
}

.estimator-table .parameters-table tr:hover {
    background-color: #e0e0e0;
}

.estimator-table table td {
    border: 1px solid rgba(106, 105, 104, 0.232);
}

/*
    `table td`is set in notebook with right text-align.
    We need to overwrite it.
*/
.estimator-table table td.param {
    text-align: left;
    position: relative;
    padding: 0;
}

.user-set td {
    color:rgb(255, 94, 0);
    text-align: left !important;
}

.user-set td.value {
    color:rgb(255, 94, 0);
    background-color: transparent;
}

.default td {
    color: black;
    text-align: left !important;
}

.user-set td i,
.default td i {
    color: black;
}

/*
    Styles for parameter documentation links
    We need styling for visited so jupyter doesn't overwrite it
*/
a.param-doc-link,
a.param-doc-link:link,
a.param-doc-link:visited {
    text-decoration: underline dashed;
    text-underline-offset: .3em;
    color: inherit;
    display: block;
    padding: .5em;
}

/* "hack" to make the entire area of the cell containing the link clickable */
a.param-doc-link::before {
    position: absolute;
    content: "";
    inset: 0;
}

.param-doc-description {
    display: none;
    position: absolute;
    z-index: 9999;
    left: 0;
    padding: .5ex;
    margin-left: 1.5em;
    color: var(--sklearn-color-text);
    box-shadow: .3em .3em .4em #999;
    width: max-content;
    text-align: left;
    max-height: 10em;
    overflow-y: auto;

    /* unfitted */
    background: var(--sklearn-color-unfitted-level-0);
    border: thin solid var(--sklearn-color-unfitted-level-3);
}

/* Fitted state for parameter tooltips */
.fitted .param-doc-description {
    /* fitted */
    background: var(--sklearn-color-fitted-level-0);
    border: thin solid var(--sklearn-color-fitted-level-3);
}

.param-doc-link:hover .param-doc-description {
    display: block;
}

.copy-paste-icon {
    background-image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIj48IS0tIUZvbnQgQXdlc29tZSBGcmVlIDYuNy4yIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjUgRm9udGljb25zLCBJbmMuLS0+PHBhdGggZD0iTTIwOCAwTDMzMi4xIDBjMTIuNyAwIDI0LjkgNS4xIDMzLjkgMTQuMWw2Ny45IDY3LjljOSA5IDE0LjEgMjEuMiAxNC4xIDMzLjlMNDQ4IDMzNmMwIDI2LjUtMjEuNSA0OC00OCA0OGwtMTkyIDBjLTI2LjUgMC00OC0yMS41LTQ4LTQ4bDAtMjg4YzAtMjYuNSAyMS41LTQ4IDQ4LTQ4ek00OCAxMjhsODAgMCAwIDY0LTY0IDAgMCAyNTYgMTkyIDAgMC0zMiA2NCAwIDAgNDhjMCAyNi41LTIxLjUgNDgtNDggNDhMNDggNTEyYy0yNi41IDAtNDgtMjEuNS00OC00OEwwIDE3NmMwLTI2LjUgMjEuNS00OCA0OC00OHoiLz48L3N2Zz4=);
    background-repeat: no-repeat;
    background-size: 14px 14px;
    background-position: 0;
    display: inline-block;
    width: 14px;
    height: 14px;
    cursor: pointer;
}
</style><body><div id="sk-container-id-1" class="sk-top-container"><div class="sk-text-repr-fallback"><pre>ColumnTransformer(transformers=[(&#x27;numerique&#x27;,
                                 Pipeline(steps=[(&#x27;imputation&#x27;,
                                                  SimpleImputer(strategy=&#x27;median&#x27;)),
                                                 (&#x27;standardisation&#x27;,
                                                  StandardScaler())]),
                                 [&#x27;heure_envoi&#x27;, &#x27;longueur_message&#x27;, &#x27;nb_liens&#x27;,
                                  &#x27;urgence_score&#x27;, &#x27;domaine_age_jours&#x27;,
                                  &#x27;fautes_langue&#x27;, &#x27;expediteur_connu&#x27;,
                                  &#x27;piece_jointe&#x27;, &#x27;personnalisation_score&#x27;])])</pre><b>In a Jupyter environment, please rerun this cell to show the HTML representation or trust the notebook. <br />On GitHub, the HTML representation is unable to render, please try loading this page with nbviewer.org.</b></div><div class="sk-container" hidden><div class="sk-item sk-dashed-wrapped"><div class="sk-label-container"><div class="sk-label  sk-toggleable"><input class="sk-toggleable__control sk-hidden--visually" id="sk-estimator-id-1" type="checkbox" ><label for="sk-estimator-id-1" class="sk-toggleable__label  sk-toggleable__label-arrow"><div><div>ColumnTransformer</div></div><div><a class="sk-estimator-doc-link " rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html">?<span>Documentation for ColumnTransformer</span></a><span class="sk-estimator-doc-link ">i<span>Not fitted</span></span></div></label><div class="sk-toggleable__content " data-param-prefix="">
        <div class="estimator-table">
            <details>
                <summary>Parameters</summary>
                <table class="parameters-table">
                  <tbody>

        <tr class="user-set">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('transformers',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=transformers,-list%20of%20tuples">
            transformers
            <span class="param-doc-description">transformers: list of tuples<br><br>List of (name, transformer, columns) tuples specifying the<br>transformer objects to be applied to subsets of the data.<br><br>name : str<br>    Like in Pipeline and FeatureUnion, this allows the transformer and<br>    its parameters to be set using ``set_params`` and searched in grid<br>    search.<br>transformer : {'drop', 'passthrough'} or estimator<br>    Estimator must support :term:`fit` and :term:`transform`.<br>    Special-cased strings 'drop' and 'passthrough' are accepted as<br>    well, to indicate to drop the columns or to pass them through<br>    untransformed, respectively.<br>columns :  str, array-like of str, int, array-like of int,                 array-like of bool, slice or callable<br>    Indexes the data on its second axis. Integers are interpreted as<br>    positional columns, while strings can reference DataFrame columns<br>    by name.  A scalar string or int should be used where<br>    ``transformer`` expects X to be a 1d array-like (vector),<br>    otherwise a 2d array will be passed to the transformer.<br>    A callable is passed the input data `X` and can return any of the<br>    above. To select multiple columns by name or dtype, you can use<br>    :obj:`make_column_selector`.</span>
        </a>
    </td>
            <td class="value">[(&#x27;numerique&#x27;, ...)]</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('remainder',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=remainder,-%7B%27drop%27%2C%20%27passthrough%27%7D%20or%20estimator%2C%20default%3D%27drop%27">
            remainder
            <span class="param-doc-description">remainder: {'drop', 'passthrough'} or estimator, default='drop'<br><br>By default, only the specified columns in `transformers` are<br>transformed and combined in the output, and the non-specified<br>columns are dropped. (default of ``'drop'``).<br>By specifying ``remainder='passthrough'``, all remaining columns that<br>were not specified in `transformers`, but present in the data passed<br>to `fit` will be automatically passed through. This subset of columns<br>is concatenated with the output of the transformers. For dataframes,<br>extra columns not seen during `fit` will be excluded from the output<br>of `transform`.<br>By setting ``remainder`` to be an estimator, the remaining<br>non-specified columns will use the ``remainder`` estimator. The<br>estimator must support :term:`fit` and :term:`transform`.<br>Note that using this feature requires that the DataFrame columns<br>input at :term:`fit` and :term:`transform` have identical order.</span>
        </a>
    </td>
            <td class="value">&#x27;drop&#x27;</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('sparse_threshold',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=sparse_threshold,-float%2C%20default%3D0.3">
            sparse_threshold
            <span class="param-doc-description">sparse_threshold: float, default=0.3<br><br>If the output of the different transformers contains sparse matrices,<br>these will be stacked as a sparse matrix if the overall density is<br>lower than this value. Use ``sparse_threshold=0`` to always return<br>dense.  When the transformed output consists of all dense data, the<br>stacked result will be dense, and this keyword will be ignored.</span>
        </a>
    </td>
            <td class="value">0.3</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('n_jobs',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=n_jobs,-int%2C%20default%3DNone">
            n_jobs
            <span class="param-doc-description">n_jobs: int, default=None<br><br>Number of jobs to run in parallel.<br>``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.<br>``-1`` means using all processors. See :term:`Glossary <n_jobs>`<br>for more details.</span>
        </a>
    </td>
            <td class="value">None</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('transformer_weights',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=transformer_weights,-dict%2C%20default%3DNone">
            transformer_weights
            <span class="param-doc-description">transformer_weights: dict, default=None<br><br>Multiplicative weights for features per transformer. The output of the<br>transformer is multiplied by these weights. Keys are transformer names,<br>values the weights.</span>
        </a>
    </td>
            <td class="value">None</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('verbose',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=verbose,-bool%2C%20default%3DFalse">
            verbose
            <span class="param-doc-description">verbose: bool, default=False<br><br>If True, the time elapsed while fitting each transformer will be<br>printed as it is completed.</span>
        </a>
    </td>
            <td class="value">False</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('verbose_feature_names_out',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=verbose_feature_names_out,-bool%2C%20str%20or%20Callable%5B%5Bstr%2C%20str%5D%2C%20str%5D%2C%20default%3DTrue">
            verbose_feature_names_out
            <span class="param-doc-description">verbose_feature_names_out: bool, str or Callable[[str, str], str], default=True<br><br>- If True, :meth:`ColumnTransformer.get_feature_names_out` will prefix<br>  all feature names with the name of the transformer that generated that<br>  feature. It is equivalent to setting<br>  `verbose_feature_names_out="{transformer_name}__{feature_name}"`.<br>- If False, :meth:`ColumnTransformer.get_feature_names_out` will not<br>  prefix any feature names and will error if feature names are not<br>  unique.<br>- If ``Callable[[str, str], str]``,<br>  :meth:`ColumnTransformer.get_feature_names_out` will rename all the features<br>  using the name of the transformer. The first argument of the callable is the<br>  transformer name and the second argument is the feature name. The returned<br>  string will be the new feature name.<br>- If ``str``, it must be a string ready for formatting. The given string will<br>  be formatted using two field names: ``transformer_name`` and ``feature_name``.<br>  e.g. ``"{feature_name}__{transformer_name}"``. See :meth:`str.format` method<br>  from the standard library for more info.<br><br>.. versionadded:: 1.0<br><br>.. versionchanged:: 1.6<br>    `verbose_feature_names_out` can be a callable or a string to be formatted.</span>
        </a>
    </td>
            <td class="value">True</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('force_int_remainder_cols',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.compose.ColumnTransformer.html#:~:text=force_int_remainder_cols,-bool%2C%20default%3DFalse">
            force_int_remainder_cols
            <span class="param-doc-description">force_int_remainder_cols: bool, default=False<br><br>This parameter has no effect.<br><br>.. note::<br>    If you do not access the list of columns for the remainder columns<br>    in the `transformers_` fitted attribute, you do not need to set<br>    this parameter.<br><br>.. versionadded:: 1.5<br><br>.. versionchanged:: 1.7<br>   The default value for `force_int_remainder_cols` will change from<br>   `True` to `False` in version 1.7.<br><br>.. deprecated:: 1.7<br>   `force_int_remainder_cols` is deprecated and will be removed in 1.9.</span>
        </a>
    </td>
            <td class="value">&#x27;deprecated&#x27;</td>
        </tr>

                  </tbody>
                </table>
            </details>
        </div>
    </div></div></div><div class="sk-parallel"><div class="sk-parallel-item"><div class="sk-item"><div class="sk-label-container"><div class="sk-label  sk-toggleable"><input class="sk-toggleable__control sk-hidden--visually" id="sk-estimator-id-2" type="checkbox" ><label for="sk-estimator-id-2" class="sk-toggleable__label  sk-toggleable__label-arrow"><div><div>numerique</div></div></label><div class="sk-toggleable__content " data-param-prefix="numerique__"><pre>[&#x27;heure_envoi&#x27;, &#x27;longueur_message&#x27;, &#x27;nb_liens&#x27;, &#x27;urgence_score&#x27;, &#x27;domaine_age_jours&#x27;, &#x27;fautes_langue&#x27;, &#x27;expediteur_connu&#x27;, &#x27;piece_jointe&#x27;, &#x27;personnalisation_score&#x27;]</pre></div></div></div><div class="sk-serial"><div class="sk-item"><div class="sk-serial"><div class="sk-item"><div class="sk-estimator  sk-toggleable"><input class="sk-toggleable__control sk-hidden--visually" id="sk-estimator-id-3" type="checkbox" ><label for="sk-estimator-id-3" class="sk-toggleable__label  sk-toggleable__label-arrow"><div><div>SimpleImputer</div></div><div><a class="sk-estimator-doc-link " rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.impute.SimpleImputer.html">?<span>Documentation for SimpleImputer</span></a></div></label><div class="sk-toggleable__content " data-param-prefix="numerique__imputation__">
        <div class="estimator-table">
            <details>
                <summary>Parameters</summary>
                <table class="parameters-table">
                  <tbody>

        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('missing_values',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.impute.SimpleImputer.html#:~:text=missing_values,-int%2C%20float%2C%20str%2C%20np.nan%2C%20None%20or%20pandas.NA%2C%20default%3Dnp.nan">
            missing_values
            <span class="param-doc-description">missing_values: int, float, str, np.nan, None or pandas.NA, default=np.nan<br><br>The placeholder for the missing values. All occurrences of<br>`missing_values` will be imputed. For pandas' dataframes with<br>nullable integer dtypes with missing values, `missing_values`<br>can be set to either `np.nan` or `pd.NA`.</span>
        </a>
    </td>
            <td class="value">nan</td>
        </tr>


        <tr class="user-set">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('strategy',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.impute.SimpleImputer.html#:~:text=strategy,-str%20or%20Callable%2C%20default%3D%27mean%27">
            strategy
            <span class="param-doc-description">strategy: str or Callable, default='mean'<br><br>The imputation strategy.<br><br>- If "mean", then replace missing values using the mean along<br>  each column. Can only be used with numeric data.<br>- If "median", then replace missing values using the median along<br>  each column. Can only be used with numeric data.<br>- If "most_frequent", then replace missing using the most frequent<br>  value along each column. Can be used with strings or numeric data.<br>  If there is more than one such value, only the smallest is returned.<br>- If "constant", then replace missing values with fill_value. Can be<br>  used with strings or numeric data.<br>- If an instance of Callable, then replace missing values using the<br>  scalar statistic returned by running the callable over a dense 1d<br>  array containing non-missing values of each column.<br><br>.. versionadded:: 0.20<br>   strategy="constant" for fixed value imputation.<br><br>.. versionadded:: 1.5<br>   strategy=callable for custom value imputation.</span>
        </a>
    </td>
            <td class="value">&#x27;median&#x27;</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('fill_value',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.impute.SimpleImputer.html#:~:text=fill_value,-str%20or%20numerical%20value%2C%20default%3DNone">
            fill_value
            <span class="param-doc-description">fill_value: str or numerical value, default=None<br><br>When strategy == "constant", `fill_value` is used to replace all<br>occurrences of missing_values. For string or object data types,<br>`fill_value` must be a string.<br>If `None`, `fill_value` will be 0 when imputing numerical<br>data and "missing_value" for strings or object data types.</span>
        </a>
    </td>
            <td class="value">None</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('copy',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.impute.SimpleImputer.html#:~:text=copy,-bool%2C%20default%3DTrue">
            copy
            <span class="param-doc-description">copy: bool, default=True<br><br>If True, a copy of X will be created. If False, imputation will<br>be done in-place whenever possible. Note that, in the following cases,<br>a new copy will always be made, even if `copy=False`:<br><br>- If `X` is not an array of floating values;<br>- If `X` is encoded as a CSR matrix;<br>- If `add_indicator=True`.</span>
        </a>
    </td>
            <td class="value">True</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('add_indicator',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.impute.SimpleImputer.html#:~:text=add_indicator,-bool%2C%20default%3DFalse">
            add_indicator
            <span class="param-doc-description">add_indicator: bool, default=False<br><br>If True, a :class:`MissingIndicator` transform will stack onto output<br>of the imputer's transform. This allows a predictive estimator<br>to account for missingness despite imputation. If a feature has no<br>missing values at fit/train time, the feature won't appear on<br>the missing indicator even if there are missing values at<br>transform/test time.</span>
        </a>
    </td>
            <td class="value">False</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('keep_empty_features',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.impute.SimpleImputer.html#:~:text=keep_empty_features,-bool%2C%20default%3DFalse">
            keep_empty_features
            <span class="param-doc-description">keep_empty_features: bool, default=False<br><br>If True, features that consist exclusively of missing values when<br>`fit` is called are returned in results when `transform` is called.<br>The imputed value is always `0` except when `strategy="constant"`<br>in which case `fill_value` will be used instead.<br><br>.. versionadded:: 1.2</span>
        </a>
    </td>
            <td class="value">False</td>
        </tr>

                  </tbody>
                </table>
            </details>
        </div>
    </div></div></div><div class="sk-item"><div class="sk-estimator  sk-toggleable"><input class="sk-toggleable__control sk-hidden--visually" id="sk-estimator-id-4" type="checkbox" ><label for="sk-estimator-id-4" class="sk-toggleable__label  sk-toggleable__label-arrow"><div><div>StandardScaler</div></div><div><a class="sk-estimator-doc-link " rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.preprocessing.StandardScaler.html">?<span>Documentation for StandardScaler</span></a></div></label><div class="sk-toggleable__content " data-param-prefix="numerique__standardisation__">
        <div class="estimator-table">
            <details>
                <summary>Parameters</summary>
                <table class="parameters-table">
                  <tbody>

        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('copy',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.preprocessing.StandardScaler.html#:~:text=copy,-bool%2C%20default%3DTrue">
            copy
            <span class="param-doc-description">copy: bool, default=True<br><br>If False, try to avoid a copy and do inplace scaling instead.<br>This is not guaranteed to always work inplace; e.g. if the data is<br>not a NumPy array or scipy.sparse CSR matrix, a copy may still be<br>returned.</span>
        </a>
    </td>
            <td class="value">True</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('with_mean',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.preprocessing.StandardScaler.html#:~:text=with_mean,-bool%2C%20default%3DTrue">
            with_mean
            <span class="param-doc-description">with_mean: bool, default=True<br><br>If True, center the data before scaling.<br>This does not work (and will raise an exception) when attempted on<br>sparse matrices, because centering them entails building a dense<br>matrix which in common use cases is likely to be too large to fit in<br>memory.</span>
        </a>
    </td>
            <td class="value">True</td>
        </tr>


        <tr class="default">
            <td><i class="copy-paste-icon"
                 onclick="copyToClipboard('with_std',
                          this.parentElement.nextElementSibling)"
            ></i></td>
            <td class="param">
        <a class="param-doc-link"
            rel="noreferrer" target="_blank" href="https://scikit-learn.org/1.8/modules/generated/sklearn.preprocessing.StandardScaler.html#:~:text=with_std,-bool%2C%20default%3DTrue">
            with_std
            <span class="param-doc-description">with_std: bool, default=True<br><br>If True, scale the data to unit variance (or equivalently,<br>unit standard deviation).</span>
        </a>
    </td>
            <td class="value">True</td>
        </tr>

                  </tbody>
                </table>
            </details>
        </div>
    </div></div></div></div></div></div></div></div></div></div></div></div><script>function copyToClipboard(text, element) {
    // Get the parameter prefix from the closest toggleable content
    const toggleableContent = element.closest('.sk-toggleable__content');
    const paramPrefix = toggleableContent ? toggleableContent.dataset.paramPrefix : '';
    const fullParamName = paramPrefix ? `${paramPrefix}${text}` : text;

    const originalStyle = element.style;
    const computedStyle = window.getComputedStyle(element);
    const originalWidth = computedStyle.width;
    const originalHTML = element.innerHTML.replace('Copied!', '');

    navigator.clipboard.writeText(fullParamName)
        .then(() => {
            element.style.width = originalWidth;
            element.style.color = 'green';
            element.innerHTML = "Copied!";

            setTimeout(() => {
                element.innerHTML = originalHTML;
                element.style = originalStyle;
            }, 2000);
        })
        .catch(err => {
            console.error('Failed to copy:', err);
            element.style.color = 'red';
            element.innerHTML = "Failed!";
            setTimeout(() => {
                element.innerHTML = originalHTML;
                element.style = originalStyle;
            }, 2000);
        });
    return false;
}

document.querySelectorAll('.copy-paste-icon').forEach(function(element) {
    const toggleableContent = element.closest('.sk-toggleable__content');
    const paramPrefix = toggleableContent ? toggleableContent.dataset.paramPrefix : '';
    const paramName = element.parentElement.nextElementSibling
        .textContent.trim().split(' ')[0];
    const fullParamName = paramPrefix ? `${paramPrefix}${paramName}` : paramName;

    element.setAttribute('title', fullParamName);
});


/**
 * Adapted from Skrub
 * https://github.com/skrub-data/skrub/blob/403466d1d5d4dc76a7ef569b3f8228db59a31dc3/skrub/_reporting/_data/templates/report.js#L789
 * @returns "light" or "dark"
 */
function detectTheme(element) {
    const body = document.querySelector('body');

    // Check VSCode theme
    const themeKindAttr = body.getAttribute('data-vscode-theme-kind');
    const themeNameAttr = body.getAttribute('data-vscode-theme-name');

    if (themeKindAttr && themeNameAttr) {
        const themeKind = themeKindAttr.toLowerCase();
        const themeName = themeNameAttr.toLowerCase();

        if (themeKind.includes("dark") || themeName.includes("dark")) {
            return "dark";
        }
        if (themeKind.includes("light") || themeName.includes("light")) {
            return "light";
        }
    }

    // Check Jupyter theme
    if (body.getAttribute('data-jp-theme-light') === 'false') {
        return 'dark';
    } else if (body.getAttribute('data-jp-theme-light') === 'true') {
        return 'light';
    }

    // Guess based on a parent element's color
    const color = window.getComputedStyle(element.parentNode, null).getPropertyValue('color');
    const match = color.match(/^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*$/i);
    if (match) {
        const [r, g, b] = [
            parseFloat(match[1]),
            parseFloat(match[2]),
            parseFloat(match[3])
        ];

        // https://en.wikipedia.org/wiki/HSL_and_HSV#Lightness
        const luma = 0.299 * r + 0.587 * g + 0.114 * b;

        if (luma > 180) {
            // If the text is very bright we have a dark theme
            return 'dark';
        }
        if (luma < 75) {
            // If the text is very dark we have a light theme
            return 'light';
        }
        // Otherwise fall back to the next heuristic.
    }

    // Fallback to system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}


function forceTheme(elementId) {
    const estimatorElement = document.querySelector(`#${elementId}`);
    if (estimatorElement === null) {
        console.error(`Element with id ${elementId} not found.`);
    } else {
        const theme = detectTheme(estimatorElement);
        estimatorElement.classList.add(theme);
    }
}

forceTheme('sk-container-id-1');</script></body>


## 13. Processus Machine Learning du projet

Schéma identique à celui de l'application Streamlit. Le jeu de test n'est consulté qu'à l'étape 8, après la sélection du modèle et du seuil sur le train : aucune fuite de données, pas de one-hot encoding (les 9 variables explicatives sont numériques).



```python
from IPython.display import Image as IPyImage, display
display(IPyImage(filename="artefacts/processus_phishing_ia.png"))
print("Règle clé : imputation, standardisation, modèle et seuils appris sur le train seul.")
```


    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_45_0.png)
    


    Règle clé : imputation, standardisation, modèle et seuils appris sur le train seul.


## 14. Modèles candidats

On écarte la baseline majoritaire : elle prédit toujours `Non`, affiche ~72 % d'accuracy mais **ne détecte aucun phishing**. Elle sert seulement de repère pédagogique au §18.1.

Trois hypothèses complémentaires sont comparées :
1. **Régression logistique** : frontière linéaire, simple et interprétable.
2. **Random Forest** : ensemble d'arbres, capte les interactions non linéaires.
3. **SVM noyau RBF** : séparation à marge maximale, efficace sur un petit jeu numérique propre et stable en validation croisée ; `probability=True` fournit les probabilités.

Les modèles et prétraitements sont réunis dans des pipelines identiques.



```python
modeles = {
    "Regression_logistique": LogisticRegression(max_iter=2000, class_weight="balanced"),
    "Random_Forest": RandomForestClassifier(
        n_estimators=300,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        min_samples_leaf=2
    ),
    "SVM_RBF": SVC(
        kernel="rbf",
        C=1.0,
        gamma="scale",
        class_weight="balanced",
        probability=True,
        random_state=RANDOM_STATE
    )
}

pipelines = {
    nom: Pipeline(steps=[
        ("pretraitement", clone(preprocesseur)),
        ("modele", modele)
    ])
    for nom, modele in modeles.items()
}

print("Modèles préparés :", list(pipelines.keys()))
```

    Modèles préparés : ['Regression_logistique', 'Random_Forest', 'SVM_RBF']


## 15. Sélection du modèle sur le train — validation croisée 5-fold

C'est **ici** que se joue la sélection, avant toute lecture du test. Chaque pipeline est évalué par `StratifiedKFold(5)` sur les 416 messages du train : moyennes et écarts-types portent sur 5 scores de pli.

**Protocole exact** : 5 plis stratifiés, `shuffle=True`, `random_state=42`, soit **5 entraînements par modèle**. Il ne faut pas le confondre avec la CV **5×5 répétée** du §17 (25 entraînements, seeds 42–46), qui sert à apprendre le seuil et à mesurer la stabilité : les deux jeux de valeurs ne sont pas comparables.



```python
min_classe_train = y_train.value_counts().min()
n_splits = min(5, int(min_classe_train))

if n_splits >= 2:
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "accuracy": "accuracy",
        "precision_macro": "precision_macro",
        "recall_macro": "recall_macro",
        "f1_macro": "f1_macro"
    }
    cv_rows = []
    for nom, pipeline in pipelines.items():
        cv_scores = cross_validate(
            pipeline, X_train, y_train,
            cv=cv, scoring=scoring, n_jobs=-1
        )
        cv_rows.append({
            "Modele": nom,
            "Accuracy_CV_moyenne": cv_scores["test_accuracy"].mean(),
            "F1_macro_CV_moyenne": cv_scores["test_f1_macro"].mean(),
            "F1_macro_CV_ecart_type": cv_scores["test_f1_macro"].std()
        })
    cv_resultats = pd.DataFrame(cv_rows).sort_values("F1_macro_CV_moyenne", ascending=False)
    print("Protocole : CV 5-fold simple (5 entraînements par modèle, seed 42) — train seul")
    print("À ne pas confondre avec la CV 5x5 répétée du §17 (25 entraînements) : valeurs non comparables.")
    display(cv_resultats.round(3))
else:
    print("Validation croisée stratifiée impossible : effectif insuffisant dans une classe.")
```

    Protocole : CV 5-fold simple (5 entraînements par modèle, seed 42) — train seul
    À ne pas confondre avec la CV 5x5 répétée du §17 (25 entraînements) : valeurs non comparables.



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Modele</th>
      <th>Accuracy_CV_moyenne</th>
      <th>F1_macro_CV_moyenne</th>
      <th>F1_macro_CV_ecart_type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Random_Forest</td>
      <td>0.839</td>
      <td>0.791</td>
      <td>0.051</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Regression_logistique</td>
      <td>0.810</td>
      <td>0.785</td>
      <td>0.067</td>
    </tr>
    <tr>
      <th>2</th>
      <td>SVM_RBF</td>
      <td>0.815</td>
      <td>0.784</td>
      <td>0.018</td>
    </tr>
  </tbody>
</table>
</div>


## 16. Comparaison descriptive des trois modèles de référence sur le test (a posteriori)

⚠️ **Lis cette section comme un constat, pas comme une sélection.** Le modèle et le seuil ont été choisis **avant**, sur le train seul : validation croisée au §15, puis protocole du §17. Les trois modèles ci-dessous sont entraînés sur le train et évalués une fois sur le test, pour **documenter** leur comportement au seuil par défaut 0,50. Aucun choix du notebook ne repose sur ce tableau.

Cette lecture unique du test est assumée : elle ne sert qu'à la comparaison descriptive et à l'illustration pédagogique ; le chiffre de performance du modèle déployé est produit au §17–§18, avec le seuil appris sur le train.



```python
import numpy as np
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, mean_absolute_error,
                             roc_auc_score, average_precision_score,
                             mean_squared_error, r2_score)

resultats = []
probabilites = {}
predictions = {}

# Conversion Oui/Non -> 1/0
y_test_num = (y_test == "Oui").astype(int)

for nom, pipeline in pipelines.items():
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    predictions[nom] = y_pred

    y_pred_num = (pd.Series(y_pred) == "Oui").astype(int).values

    # Probabilité de la classe "Oui"
    idx_oui = list(pipeline.classes_).index("Oui")
    y_proba = pipeline.predict_proba(X_test)[:, idx_oui]
    probabilites[nom] = y_proba

    resultats.append({
        "Modele": nom,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision_macro": precision_score(y_test, y_pred, average="macro", zero_division=0),
        "Recall_macro": recall_score(y_test, y_pred, average="macro", zero_division=0),
        "F1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "AUC": roc_auc_score(y_test_num, y_proba),
        "Average_precision": average_precision_score(y_test_num, y_proba),
        # Sur les classes prédites
        "MAE": mean_absolute_error(y_test_num, y_pred_num),
        "RMSE": np.sqrt(mean_squared_error(y_test_num, y_pred_num)),
        "R2": r2_score(y_test_num, y_pred_num),
        # Sur les probabilités
        "MAE_proba": mean_absolute_error(y_test_num, y_proba),
        "RMSE_proba": np.sqrt(mean_squared_error(y_test_num, y_proba)),
        "R2_proba": r2_score(y_test_num, y_proba),
    })

    print(f"Entraînement terminé : {nom}")

resultats_df = pd.DataFrame(resultats).sort_values("F1_macro", ascending=False)
display(resultats_df.round(3))
```

    Entraînement terminé : Regression_logistique


    Entraînement terminé : Random_Forest


    Entraînement terminé : SVM_RBF



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Modele</th>
      <th>Accuracy</th>
      <th>Precision_macro</th>
      <th>Recall_macro</th>
      <th>F1_macro</th>
      <th>AUC</th>
      <th>Average_precision</th>
      <th>MAE</th>
      <th>RMSE</th>
      <th>R2</th>
      <th>MAE_proba</th>
      <th>RMSE_proba</th>
      <th>R2_proba</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Random_Forest</td>
      <td>0.798</td>
      <td>0.752</td>
      <td>0.723</td>
      <td>0.734</td>
      <td>0.866</td>
      <td>0.698</td>
      <td>0.202</td>
      <td>0.449</td>
      <td>-0.004</td>
      <td>0.288</td>
      <td>0.365</td>
      <td>0.337</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Regression_logistique</td>
      <td>0.721</td>
      <td>0.692</td>
      <td>0.733</td>
      <td>0.694</td>
      <td>0.832</td>
      <td>0.656</td>
      <td>0.279</td>
      <td>0.528</td>
      <td>-0.387</td>
      <td>0.298</td>
      <td>0.417</td>
      <td>0.134</td>
    </tr>
    <tr>
      <th>2</th>
      <td>SVM_RBF</td>
      <td>0.721</td>
      <td>0.692</td>
      <td>0.733</td>
      <td>0.694</td>
      <td>0.834</td>
      <td>0.633</td>
      <td>0.279</td>
      <td>0.528</td>
      <td>-0.387</td>
      <td>0.286</td>
      <td>0.386</td>
      <td>0.259</td>
    </tr>
  </tbody>
</table>
</div>


## 17. Modèle retenu : `log_age`, interactions et seuil appris sur le train

Les limitations mesurées sur le modèle de référence sont corrigées ici :

1. **`domaine_age_jours` est transformé** : la variable va de 1 à 5 874 jours et sa distribution est très asymétrique. On utilise `log1p(domaine_age_jours)` **à l'intérieur du pipeline**, donc sans fuite.
2. **Les variables de bruit sont retirées** : `heure_envoi`, `longueur_message` et `fautes_langue` ont une importance par permutation faible sur le train (≤ 0,05, contre 0,24 pour `domaine_age_jours`).
3. **Deux interactions métier** sont ajoutées : `urgence × expéditeur inconnu` et `nb_liens × expéditeur inconnu`.
4. **Modèle** : régression logistique pondérée (`class_weight="balanced"`), plus interprétable que le RF.
5. **Seuil appris sur le train seul**, par validation croisée **StratifiedKFold 5×5 répétée** (25 entraînements) :
   - coût `C = c_FN·FN + c_FP·FP` avec `c_FN = 5`, `c_FP = 1` → plateau quasi minimal **0,20–0,22**, médiane **0,21** = seuil binaire retenu ;
   - sensibilité publiée : `c_FN = 3` → 0,47 ; `c_FN = 10` → 0,20 ; le rapport de coût doit être validé par le RSSI ;
   - **triage 3 zones** : `P(Oui) < 0,20` → 🟢 Normal, `0,20 ≤ P(Oui) < 0,88` → 🟠 revue humaine, `P(Oui) ≥ 0,88` → 🔴 Alerte. Les cas ambigus ne sont pas « classés » : ils sont confiés à l'analyste ;
   - **incertitude** : IC95 % bootstrap (2 000 tirages sur le test) pour le rappel, la précision et le taux de fausses alertes.

Le pipeline reçoit les **colonnes brutes** de `X` (celles du formulaire Streamlit) et fait la transformation en interne : l'application et le notebook utilisent exactement le même code. Le test n'est utilisé qu'**une seule fois**, à la fin, pour mesurer — jamais pour choisir modèle ou seuil.


### 17.1 OOF, matrice de validation croisée et protocoles

**OOF** = *Out-Of-Fold* (« hors pli »). Avec `StratifiedKFold(5)` répété 5 fois, on entraîne 25 modèles ; chaque modèle prédit uniquement les lignes qu'il n'a jamais vues. On moyenne ces probabilités pour obtenir **une probabilité OOF par ligne du train**. La matrice de confusion qui en découle porte donc sur les **416 lignes du train**, pas sur les 104 du test.

**Deux protocoles différents coexistent dans ce notebook — ils ne sont pas comparables :**

| Protocole | Où | Usage | Ce qu'il produit |
|---|---|---|---|
| **CV 5-fold simple**, seed 42, 5 entraînements | §15 | Choisir le modèle de référence | F1 macro moyen par fold : RF 0,791 ± 0,051 ; LR 0,785 ± 0,067 ; SVM 0,784 ± 0,018 |
| **CV 5×5 répétée**, seeds 42–46, 25 entraînements | §17 | Apprendre le seuil et mesurer la stabilité | AUC 0,909 ± 0,003 ; AP 0,812 ± 0,003 ; F1 macro OOF au seuil 0,50 = **0,808** |

Le premier découpe une seule fois ; le second moyenne 5 découpages différents et agrège les probabilités. Un F1 de 0,791 (5-fold) et un F1 de 0,808 (OOF 5×5) ne mesurent donc pas la même chose : on ne les classe pas l'un contre l'autre.

Ici, les hyperparamètres sont fixés a priori (pas de recherche en grille) : la CV sert à la stabilité et au seuil, pas à une sélection d'hyperparamètres. Elle n'est donc pas imbriquée, et cette estimation reste légèrement optimiste — c'est une limite à connaître.

Au seuil retenu **0,21**, la matrice OOF du train est : **TN = 182 · FP = 117 · FN = 3 · TP = 114**. Le coût correspondant est `5·3 + 117 = 132` ; le coût minimal de 128 est atteint à 0,20 (`5·2 + 118 = 128`), d'où le plateau 0,20–0,22 et la médiane 0,21. On ne peut pas obtenir `FN = 0` et `FP = 0` simultanément : l'AUC de validation croisée vaut **0,909** (0,911 sur les probabilités moyennées), pas 1. Baisser le seuil réduit les FN mais augmente fortement les FP (à 0,20 : FN = 2, FP = 118). La matrice du test, au §18.4, est l'évaluation finale indépendante.



```python
# =====================================================================
# AMÉLIORATION PHISHING — version simplifiée
# Pipeline sans fuite, CV 5x5 répétée, seuil par coût, triage 3 zones,
# bootstrap. Le test n'est lu qu'à la fin.
# =====================================================================
import json, joblib
from pathlib import Path
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate
from sklearn.metrics import (roc_auc_score, average_precision_score, f1_score,
                             confusion_matrix, brier_score_loss)


class FeaturesPhishing(BaseEstimator, TransformerMixin):
    """Feature engineering sans fuite : `fit` n'apprend aucune statistique."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        out = pd.DataFrame(index=X.index)
        out["log_age"] = np.log1p(X["domaine_age_jours"])
        for c in ["urgence_score", "nb_liens", "expediteur_connu",
                  "piece_jointe", "personnalisation_score"]:
            out[c] = X[c]
        out["urg_x_inconnu"] = X["urgence_score"] * (1 - X["expediteur_connu"])
        out["liens_x_inconnu"] = X["nb_liens"] * (1 - X["expediteur_connu"])
        return out


def construire_modele():
    return Pipeline([
        ("features", FeaturesPhishing()),
        ("imputation", SimpleImputer(strategy="median")),
        ("standardisation", StandardScaler()),
        ("modele", LogisticRegression(max_iter=3000, class_weight="balanced",
                                      random_state=RANDOM_STATE)),
    ])


modele_ameliore = construire_modele()
COUT_FN, COUT_FP = 5, 1
SEUILS = np.round(np.arange(0.02, 0.99, 0.01), 2)
y_tr01 = (y_train == "Oui").astype(int).values
y_te01 = (y_test == "Oui").astype(int).values


def matrice(y_true, p, seuil):
    """TN, FP, FN, TP pour un seuil donné."""
    tn, fp, fn, tp = confusion_matrix(y_true, (p >= seuil).astype(int),
                                      labels=[0, 1]).ravel()
    return {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)}


def cout(y_true, p, seuil, c_fn=COUT_FN):
    m = matrice(y_true, p, seuil)
    return c_fn * m["FN"] + COUT_FP * m["FP"]


def probas_validation(modele, X, y, n_repetitions=5):
    """Probabilités de validation croisée, moyennées sur n répétitions (CV 5-fold)."""
    idx_oui = sorted(y.unique().tolist()).index("Oui")
    repetitions, aucs, aps = [], [], []
    for seed in range(RANDOM_STATE, RANDOM_STATE + n_repetitions):
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        p = cross_val_predict(modele, X, y, cv=cv,
                              method="predict_proba")[:, idx_oui]
        repetitions.append(p)
        aucs.append(roc_auc_score((y == "Oui").astype(int), p))
        aps.append(average_precision_score((y == "Oui").astype(int), p))
    return np.mean(repetitions, axis=0), np.array(aucs), np.array(aps)


def seuil_par_cout(y_true, p, c_fn=COUT_FN):
    """Médiane du plateau de coût quasi minimal (tolérance 5 %)."""
    couts = np.array([cout(y_true, p, t, c_fn) for t in SEUILS])
    best = float(couts.min())
    plateau = SEUILS[couts <= best * 1.05 + 1e-9]
    return float(np.median(plateau)), plateau, best, couts


def seuils_triage(y_true, p, seuil_opt):
    """Deux seuils appris sur le train : rappel en validation croisée >= 98 %, précision en validation croisée >= 85 %."""
    m = [matrice(y_true, p, t) for t in SEUILS]
    rappels = np.array([x["TP"] / max(x["TP"] + x["FN"], 1) for x in m])
    precisions = np.array([x["TP"] / max(x["TP"] + x["FP"], 1) for x in m])
    bas = SEUILS[rappels >= 0.98]
    haut = SEUILS[precisions >= 0.85]
    bas = float(max(bas[bas <= seuil_opt])) if (bas <= seuil_opt).any() else seuil_opt
    haut = float(min(haut[haut >= seuil_opt])) if (haut >= seuil_opt).any() else seuil_opt
    return (bas, haut) if bas <= haut else (seuil_opt, seuil_opt)


# --- 1. Stabilité du modèle : CV 5×5 répétée sur le train -------------------
p_cv, auc_cv, ap_cv = probas_validation(modele_ameliore, X_train, y_train)
print(f"CV 5x5 répétée — AUC en validation croisée {np.mean(auc_cv):.4f} ± {np.std(auc_cv):.4f} | "
      f"AP {np.mean(ap_cv):.4f} ± {np.std(ap_cv):.4f}")
print(f"Validation croisée (probabilités moyennées) — AUC {roc_auc_score(y_tr01, p_cv):.4f} | "
      f"AP {average_precision_score(y_tr01, p_cv):.4f}")

# --- 1 bis. Même protocole 5-fold que le §15, pour comparer le modèle retenu ---
cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv5_f1 = cross_validate(modele_ameliore, X_train, y_train, cv=cv5,
                        scoring="f1_macro", n_jobs=-1)["test_score"]
print(f"CV 5-fold simple (même protocole que §15) — F1 macro {cv5_f1.mean():.4f} ± {cv5_f1.std():.4f}")

# Deux lectures souvent citées dans les markdowns : OOF 5×5 au seuil 0,50 et moyenne des 25 plis.
f1_oof_50 = f1_score(y_tr01, (p_cv >= 0.50).astype(int), average="macro")
f1_25_plis = []
for seed in range(RANDOM_STATE, RANDOM_STATE + 5):
    cv_s = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    f1_25_plis += list(cross_validate(modele_ameliore, X_train, y_train, cv=cv_s,
                                      scoring="f1_macro", n_jobs=-1)["test_score"])
f1_25_plis = np.array(f1_25_plis)
print(f"OOF 5×5 (probabilités moyennées) — F1 macro au seuil 0,50 {f1_oof_50:.4f}")
print(f"25 plis CV 5×5 — F1 macro moyen {f1_25_plis.mean():.4f} ± {f1_25_plis.std():.4f}")

# --- 2. Seuil binaire : plateau de coût minimal -----------------------------
SEUIL_OPT, plateau, cout_min, couts_cv = seuil_par_cout(y_tr01, p_cv)
print(f"Coût minimal en validation croisée {cout_min:.0f} à {SEUILS[int(np.argmin(couts_cv))]:.2f} ; "
      f"plateau {plateau.min():.2f}–{plateau.max():.2f} ; seuil retenu = {SEUIL_OPT:.2f}")
print("Sensibilité du coût :", end=" ")
for c_fn in (3, 5, 10):
    s, pl, _, _ = seuil_par_cout(y_tr01, p_cv, c_fn)
    print(f"c_FN={c_fn} → {s:.2f} ({pl.min():.2f}–{pl.max():.2f})", end=" ; ")
print()

# --- 2 bis. MATRICE DE CONFUSION OOF — validation croisée 5x5, train seul ----
m_cv = matrice(y_tr01, p_cv, SEUIL_OPT)
matrice_oof_cv = pd.DataFrame(
    [[m_cv["TN"], m_cv["FP"]], [m_cv["FN"], m_cv["TP"]]],
    index=["Réel : Non", "Réel : Oui"],
    columns=["Prédit : Non", "Prédit : Oui"],
)
print("Matrice de confusion OOF (validation croisée 5×5 sur le train) :")
display(matrice_oof_cv)
print(f"OOF — TN={m_cv['TN']} · FP={m_cv['FP']} · FN={m_cv['FN']} · TP={m_cv['TP']} "
      f"| n={len(y_tr01)} | coût 5·FN+FP={COUT_FN * m_cv['FN'] + COUT_FP * m_cv['FP']}")
print("À 0,20 : FN=2 / FP=118 ; à 0,22 : FN=4 / FP=114 — zéro FN et zéro FP simultanés est impossible ici (AUC OOF ≈ 0,911).")

# --- 3. Triage 3 zones (appris sur le train, jamais sur le test) ------------
SEUIL_BAS, SEUIL_HAUT = seuils_triage(y_tr01, p_cv, SEUIL_OPT)
print(f"Triage : Normal < {SEUIL_BAS:.2f} | revue humaine {SEUIL_BAS:.2f}–{SEUIL_HAUT:.2f} "
      f"| Alerte ≥ {SEUIL_HAUT:.2f}")

# --- 4. Évaluation finale : le test est lu UNE SEULE fois -------------------
modele_ameliore.fit(X_train, y_train)
idx_oui = list(modele_ameliore.classes_).index("Oui")
p_test = modele_ameliore.predict_proba(X_test)[:, idx_oui]
auc_ameliore = roc_auc_score(y_te01, p_test)
ap_ameliore = average_precision_score(y_te01, p_test)
brier_ameliore = brier_score_loss(y_te01, p_test)

lignes_seuils = []
for nom, t in [("Seuil 0,50", 0.50), (f"Seuil optimal {SEUIL_OPT:.2f}", SEUIL_OPT)]:
    m = matrice(y_te01, p_test, t)
    lignes_seuils.append({
        "Config": nom, **m,
        "Rappel Oui": m["TP"] / max(m["TP"] + m["FN"], 1),
        "Precision Oui": m["TP"] / max(m["TP"] + m["FP"], 1),
        "F1 macro": f1_score(y_te01, (p_test >= t).astype(int),
                             average="macro", zero_division=0),
        "Coût 5·FN+FP": COUT_FN * m["FN"] + COUT_FP * m["FP"],
    })
tab_ameliore = pd.DataFrame(lignes_seuils)
f1_opt = float(tab_ameliore.iloc[-1]["F1 macro"])
print(f"AUC test = {auc_ameliore:.3f} | AP test = {ap_ameliore:.3f} | Brier = {brier_ameliore:.3f}")
print(tab_ameliore.round(3).to_string(index=False))

# --- 5. Triage sur le test : erreurs sur la PARTIE AUTOMATISÉE seulement ---
zone = np.where(p_test < SEUIL_BAS, "Normal",
                np.where(p_test >= SEUIL_HAUT, "Alerte", "Revue humaine"))
auto = zone != "Revue humaine"
triage = {
    "auto": int(auto.sum()), "total": int(len(y_te01)),
    "fn_auto": int(((zone == "Normal") & (y_te01 == 1)).sum()),
    "fp_auto": int(((zone == "Alerte") & (y_te01 == 0)).sum()),
    "revue": int((~auto).sum()),
}
print(f"Triage test : {triage['auto']}/{triage['total']} automatisés | "
      f"FN auto {triage['fn_auto']} | FP auto {triage['fp_auto']} | "
      f"revue humaine {triage['revue']}")
display(pd.crosstab(pd.Series(zone, name="Zone"),
                    pd.Series(y_te01, name="Réel").map({0: "Non", 1: "Oui"})))

# --- 6. IC95 % bootstrap (test) --------------------------------------------
rng = np.random.default_rng(RANDOM_STATE)
rec, pre, far = [], [], []
for _ in range(2000):
    idx = rng.integers(0, len(y_te01), len(y_te01))
    m = matrice(y_te01[idx], p_test[idx], SEUIL_OPT)
    rec.append(m["TP"] / max(m["TP"] + m["FN"], 1))
    pre.append(m["TP"] / max(m["TP"] + m["FP"], 1) if (m["TP"] + m["FP"]) else np.nan)
    far.append(m["FP"] / max(m["FP"] + m["TN"], 1))
ic = lambda z: np.nanpercentile(z, [2.5, 97.5]).round(3)
IC_RAPPEL, IC_PRECISION, IC_FAR = ic(rec), ic(pre), ic(far)
print("IC95 bootstrap — rappel", IC_RAPPEL, "| précision", IC_PRECISION,
      "| fausse alerte", IC_FAR)

# --- 7. Métadonnées partagées avec Streamlit -------------------------------
meta_app = {
    "dataset": "dataset_phishing_ia - dataset_phishing_ia.csv",
    "target": TARGET,
    "classes": sorted(y.unique().tolist()),
    "seuil": SEUIL_OPT,
    "seuil_bas": SEUIL_BAS,
    "seuil_haut": SEUIL_HAUT,
    "meilleur_modele": "LogisticRegression_amelioree",
    "f1_macro_test": f1_opt,
    "auc_test": float(auc_ameliore),
    "average_precision_test": float(ap_ameliore),
    "scores_f1_macro": {
        "LogisticRegression": float(resultats_df.loc[resultats_df["Modele"] == "Regression_logistique", "F1_macro"].iloc[0]),
        "RandomForest": float(resultats_df.loc[resultats_df["Modele"] == "Random_Forest", "F1_macro"].iloc[0]),
        "SVM_RBF": float(resultats_df.loc[resultats_df["Modele"] == "SVM_RBF", "F1_macro"].iloc[0]),
        "LogisticRegression_amelioree": f1_opt,
    },
    "couts": {"FN": COUT_FN, "FP": COUT_FP,
              "cout_test": int(COUT_FN * int(tab_ameliore.iloc[-1]["FN"]) + COUT_FP * int(tab_ameliore.iloc[-1]["FP"]))},
    "triage_test": {"automatise": triage["auto"], "total": triage["total"],
                    "fn_auto": triage["fn_auto"], "fp_auto": triage["fp_auto"],
                    "revue_humaine": triage["revue"]},
    "validation": {
        "cv": "StratifiedKFold 5x5 répété sur le train",
        "f1_macro_cv_5fold_modele_retenu": float(cv5_f1.mean()),
        "f1_macro_cv_5fold_ecart_type": float(cv5_f1.std()),
        "auc_cv_moyen": float(np.mean(auc_cv)), "ap_cv_moyen": float(np.mean(ap_cv)),
        "plateau_cout_cv": f"{plateau.min():.2f}-{plateau.max():.2f}",
        "matrice_oof_cv": {k: int(v) for k, v in m_cv.items()},
        "matrice_oof_cv_info": "OOF = out-of-fold : 5 plis x 5 répétitions sur le train, une prédiction par ligne jamais vue à l'entraînement",
        "bootstrap_ic95_rappel": IC_RAPPEL.tolist(),
        "bootstrap_ic95_precision": IC_PRECISION.tolist(),
        "bootstrap_ic95_fausse_alerte": IC_FAR.tolist(),
    },
    "colonnes_exclues": ["date"],
    "citation": "Données synthétiques générées pour un usage pédagogique — ISCAE Master VIC (aucune donnée personnelle).",
    "num": {c: {"min": float(X[c].min()), "max": float(X[c].max()),
                "median": float(X[c].median())} for c in X.select_dtypes(include="number").columns},
    "cat": {},
    "protocole": {
        "feature_engineering": "log1p(domaine_age_jours) + 2 interactions, bruit retiré",
        "seuil": f"plateau de coût en validation croisée 5·FN + FP en CV répétée 5×5 ({plateau.min():.2f}-{plateau.max():.2f}), médiane {SEUIL_OPT:.2f}",
        "triage": f"Normal < {SEUIL_BAS:.2f} ; revue humaine {SEUIL_BAS:.2f}-{SEUIL_HAUT:.2f} ; Alerte >= {SEUIL_HAUT:.2f}",
        "test": "évalué une seule fois, jamais utilisé pour choisir modèle ou seuil",
    },
}

```

    CV 5x5 répétée — AUC en validation croisée 0.9092 ± 0.0031 | AP 0.8119 ± 0.0034
    Validation croisée (probabilités moyennées) — AUC 0.9112 | AP 0.8154


    CV 5-fold simple (même protocole que §15) — F1 macro 0.8152 ± 0.0660


    OOF 5×5 (probabilités moyennées) — F1 macro au seuil 0,50 0.8082
    25 plis CV 5×5 — F1 macro moyen 0.8073 ± 0.0466


    Coût minimal en validation croisée 128 à 0.20 ; plateau 0.20–0.22 ; seuil retenu = 0.21
    Sensibilité du coût : 

    c_FN=3 → 0.47 (0.39–0.57) ; 

    c_FN=5 → 0.21 (0.20–0.22) ; 

    c_FN=10 → 0.20 (0.20–0.20) ; 
    Matrice de confusion OOF (validation croisée 5×5 sur le train) :



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Prédit : Non</th>
      <th>Prédit : Oui</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Réel : Non</th>
      <td>182</td>
      <td>117</td>
    </tr>
    <tr>
      <th>Réel : Oui</th>
      <td>3</td>
      <td>114</td>
    </tr>
  </tbody>
</table>
</div>


    OOF — TN=182 · FP=117 · FN=3 · TP=114 | n=416 | coût 5·FN+FP=132
    À 0,20 : FN=2 / FP=118 ; à 0,22 : FN=4 / FP=114 — zéro FN et zéro FP simultanés est impossible ici (AUC OOF ≈ 0,911).


    Triage : Normal < 0.20 | revue humaine 0.20–0.88 | Alerte ≥ 0.88
    AUC test = 0.910 | AP test = 0.810 | Brier = 0.123
                Config  TN  FP  FN  TP  Rappel Oui  Precision Oui  F1 macro  Coût 5·FN+FP
            Seuil 0,50  58  17   5  24       0.828          0.585     0.763            42
    Seuil optimal 0.21  47  28   1  28       0.966          0.500     0.712            33
    Triage test : 61/104 automatisés | FN auto 1 | FP auto 1 | revue humaine 43



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Réel</th>
      <th>Non</th>
      <th>Oui</th>
    </tr>
    <tr>
      <th>Zone</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Alerte</th>
      <td>1</td>
      <td>14</td>
    </tr>
    <tr>
      <th>Normal</th>
      <td>45</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Revue humaine</th>
      <td>29</td>
      <td>14</td>
    </tr>
  </tbody>
</table>
</div>


    IC95 bootstrap — rappel [0.886 1.   ] | précision [0.368 0.636] | fausse alerte [0.262 0.481]


### 17.2 Comment la probabilité `P(Oui)` est calculée — et pourquoi le seuil vaut 0,21

Le pipeline déployé (`model.joblib`) est une **régression logistique binaire**. Après `FeaturesPhishing`, imputation médiane et standardisation, elle calcule :

```
z = intercept + Σ(coef_i × variable_standardisée_i)
P(Oui) = 1 / (1 + exp(-z))        (sigmoïde)
```

Les coefficients appris, lus dans le modèle sauvegardé, sont :

| Variable transformée | Coefficient |
|---|---:|
| intercept | -0,764195 |
| log_age | -1,695200 |
| urgence_score | +0,966415 |
| nb_liens | +0,755597 |
| expediteur_connu | -0,328518 |
| piece_jointe | +0,184134 |
| personnalisation_score | +0,694086 |
| urg_x_inconnu | +0,475546 |
| liens_x_inconnu | +0,540464 |

Un coefficient positif augmente `z` donc `P(Oui)` ; un coefficient négatif le diminue. Les variables étant standardisées, les coefficients sont comparables entre eux. L'indice de la classe `Oui` est déduit de `model.classes_` (ici `['Non', 'Oui']` → indice 1) : le code ne suppose jamais que `Oui` est en position 1. Dans l'application, `details_probabilite()` vérifie que `intercept + contributions` reconstitue `predict_proba()` à `1e-12` près.

**Du score au verdict.** Le modèle renvoie une probabilité continue ; le **seuil** décide : `P(Oui) ≥ 0,21` → `Oui` (malveillant), sinon `Non`. Ce seuil n'est **pas appris par la régression logistique** : il est choisi après coup sur les probabilités OOF du **train seul** (416 lignes). On minimise le coût métier `5 × FN + FP` :

- coût minimal **128** au seuil **0,20** (`FN = 2`, `FP = 118`) ;
- plateau quasi minimal **0,20 – 0,22** ; médiane retenue **0,21** ;
- au seuil 0,21 : `FN = 3`, `FP = 117`, coût **132** ;
- au seuil 0,22 : `FN = 4`, `FP = 114`, coût **134**.

Le jeu de test (104 lignes) n'intervient **jamais** dans ce choix : il est lu une seule fois, au §18, pour mesurer. Les zones `Normal < 0,20`, `revue humaine 0,20–0,88` et `Alerte ≥ 0,88` sont une **action de triage secondaire**, pas une troisième classe : par exemple `P(Oui) = 28 %` donne bien `Oui` (malveillant) avec la zone VIGILANCE.


## 18. Évaluation détaillée des modèles

L'accuracy mesure la proportion de prédictions correctes. La précision indique, pour une classe prédite, quelle part est correcte. Le rappel mesure la part des observations réelles d'une classe retrouvées. Le F1 combine précision et rappel ; le F1 macro donne le même poids à chaque classe, ce qui est nécessaire avec 374 `Non` pour 146 `Oui`.

### 18.1 Les trois modèles de référence sur le test (descriptif)

| Modèle | Accuracy | Precision macro | Recall macro | F1 macro | F1 macro CV 5-fold (train) |
|---|---:|---:|---:|---:|---:|
| **Random_Forest** | **0,798** | **0,752** | 0,723 | **0,734** | **0,791** (± 0,051) |
| Regression_logistique | 0,721 | 0,692 | **0,733** | 0,694 | 0,785 (± 0,067) |
| SVM_RBF | 0,721 | 0,692 | **0,733** | 0,694 | 0,784 (± 0,018) |

Les chiffres du test sont ceux de la sortie ci-dessus ; ceux de la CV viennent du §15. Le RF de référence gagne sur ce prétraitement brut, mais il n'est pas le modèle retenu : la régression logistique améliorée (§17), évaluée avec le **même protocole 5-fold**, obtient **F1 macro = 0,815 ± 0,066**, une meilleure AUC et le coût métier le plus faible.

### 18.2 Résultats du modèle retenu (même test de 104 messages)

| Configuration | AUC | AP | FN | FP | Rappel `Oui` | F1 macro | Coût `5·FN+FP` |
|---|---:|---:|---:|---:|---:|---:|---:|
| RF de référence, seuil 0,30 | 0,866 | 0,698 | 3 | 23 | 0,897 | 0,733 | 38 |
| LR améliorée, seuil 0,50 | **0,910** | **0,810** | 5 | 17 | 0,828 | **0,763** | 42 |
| **LR améliorée, seuil 0,21 (retenu)** | **0,910** | **0,810** | **1** | 28 | **0,966** | 0,712 | **33** |

Le `log_age` et le retrait des variables de bruit font passer l'AUC de **0,866** (RF de référence) à **0,910**. Le seuil binaire vient du plateau de coût en CV 5×5 répétée. Le **triage 3 zones** (0,20 / 0,88) traite **61 messages sur 104 automatiquement** avec seulement **1 FN et 1 FP** sur cette partie ; les **43 cas ambigus** sont déferés à l'analyste. On ne surestime pas la qualité du classifieur : on déplace explicitement l'incertitude vers la revue humaine.

**Pourquoi ce modèle est retenu — `LogisticRegression_amelioree`.**

- Meilleur **F1 macro en validation croisée 5-fold** que les trois références (0,815 ± 0,066 contre 0,791 pour le RF).
- Meilleur classement indépendant du seuil sur le test : **AUC 0,910**, **AP 0,810**, Brier **0,123**.
- Coût métier le plus faible au seuil retenu : **33 = 5×1 + 28**.
- Explication lisible : coefficients et importance par permutation sur le train.

C'est ce modèle qui est exporté dans `model.joblib` et utilisé par l'application. Le Random Forest reste une **référence comparative**, pas le modèle déployé.



```python
classes = pipelines["Random_Forest"].named_steps["modele"].classes_

for nom, y_pred in predictions.items():
    print("\n" + "=" * 70)
    print("MODÈLE :", nom)
    print(classification_report(y_test, y_pred, zero_division=0))
```

    
    ======================================================================
    MODÈLE : Regression_logistique
                  precision    recall  f1-score   support
    
             Non       0.88      0.71      0.79        75
             Oui       0.50      0.76      0.60        29
    
        accuracy                           0.72       104
       macro avg       0.69      0.73      0.69       104
    weighted avg       0.78      0.72      0.73       104
    
    
    ======================================================================
    MODÈLE : Random_Forest
                  precision    recall  f1-score   support
    
             Non       0.84      0.89      0.86        75
             Oui       0.67      0.55      0.60        29
    
        accuracy                           0.80       104
       macro avg       0.75      0.72      0.73       104
    weighted avg       0.79      0.80      0.79       104
    
    
    ======================================================================
    MODÈLE : SVM_RBF
                  precision    recall  f1-score   support
    
             Non       0.88      0.71      0.79        75
             Oui       0.50      0.76      0.60        29
    
        accuracy                           0.72       104
       macro avg       0.69      0.73      0.69       104
    weighted avg       0.78      0.72      0.73       104
    



```python
# Matrices de confusion : une par modèle (effectifs + pourcentages)
labels = sorted(y.unique().tolist())

for nom, y_pred in predictions.items():
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    total_cm = int(cm.sum())
    annot = np.array([[f"{int(v)}\n{v / total_cm * 100:.1f} %" for v in row] for row in cm])
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=annot, fmt="", cmap="Blues", cbar=False, ax=ax,
                xticklabels=labels, yticklabels=labels,
                annot_kws={"size": 11})
    ax.set_xlabel("Prédit")
    ax.set_ylabel("Réel")
    ax.set_title(f"Matrice de confusion — {nom} (n = {total_cm})")
    plt.tight_layout()
    plt.show()
```


    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_58_0.png)
    



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_58_1.png)
    



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_58_2.png)
    


### 18.3 Rappel — matrice de confusion et métriques

#### 1. La matrice de confusion : TP, TN, FP, FN

Ici, la **classe positive = 1 = message malveillant** (`Oui`) et la **classe négative = 0 = message légitime** (`Non`).

|  | Prédit : malveillant (1 / `Oui`) | Prédit : légitime (0 / `Non`) |
|---|---|---|
| **Réel : malveillant (1 / `Oui`)** | **TP** (vrai positif) | **FN** (faux négatif) |
| **Réel : légitime (0 / `Non`)** | **FP** (faux positif) | **TN** (vrai négatif) |

- **TP** : le message est malveillant et le modèle le détecte. ✅
- **TN** : le message est légitime et le modèle le laisse passer. ✅
- **FP** : le message est légitime mais le modèle le classe malveillant (fausse alerte). ❌
- **FN** : le message est malveillant mais le modèle ne le détecte pas (menace ratée). ❌ **C'est l'erreur la plus grave en phishing.**

**Exemple pédagogique** — 100 messages, 28 malveillants et 72 légitimes : `TP = 20, FN = 8, FP = 7, TN = 65`.

#### 2. Les métriques de classification

| Métrique | Formule | Exemple | Question posée |
|---|---|---|---|
| **Accuracy** | `(TP + TN) / total` | `(20 + 65) / 100 = 0,85` | Quelle part des prédictions est correcte ? |
| **Precision** | `TP / (TP + FP)` | `20 / 27 = 0,74` | Quand le modèle dit « malveillant », a-t-il raison ? |
| **Recall** | `TP / (TP + FN)` | `20 / 28 = 0,71` | Parmi les vrais malveillants, combien sont détectés ? |
| **F1** | `2 × (P × R) / (P + R)` | `≈ 0,73` | Compromis entre précision et rappel |

- **Precision élevée** = peu de fausses alertes.
- **Recall élevé** = peu de menaces ratées.
- **F1** est une moyenne harmonique : elle s'effondre dès qu'un des deux termes est faible.

**Pourquoi « macro » ?** La précision, le rappel et le F1 sont calculés pour chaque classe, puis moyennés simplement : chaque classe pèse autant, même la minoritaire. Pour la classe 0, `precision = TN/(TN+FN) = 65/73 = 0,89` et `recall = TN/(TN+FP) = 65/72 = 0,90`, d'où `F1 macro ≈ 0,81`. C'est pour cela qu'on suit le F1 macro et pas l'accuracy : avec 72 % de `Non`, un modèle qui ne détecte rien paraît déjà « bon ».

#### 3. La baseline majoritaire, repère pédagogique

La baseline prédit toujours « légitime » : `TP = 0, FP = 0, FN = 28, TN = 72`.

- `Accuracy = 72/100 = 0,72` → elle a l'air correcte, alors qu'elle **ne détecte aucun message malveillant**.
- Macro : `precision = (0 + 0,72)/2 = 0,36`, `recall = (0 + 1)/2 = 0,50`, donc `F1 macro = 0,419`.

Cette valeur **0,419** est un repère arithmétique, pas un résultat du protocole de sélection : la baseline n'est pas un modèle candidat. C'est l'illustration du piège de l'accuracy.

#### 4. Les métriques de régression : MAE, RMSE, R²

Avec des classes 0/1 :

- `MAE = (FP + FN) / total = 15/100 = 0,15`, soit `1 − accuracy`.
- `RMSE = √0,15 ≈ 0,39`, soit `√(1 − accuracy)`.
- `R² = 1 − (erreur du modèle / erreur de la baseline « toujours la moyenne »)`. La variance de `y` vaut `0,28 × 0,72 = 0,2016`, donc `R² = 1 − 0,15/0,2016 ≈ 0,26`.

**Interprétation du R²** : `1` = parfait, `0` = pas mieux que prédire la moyenne, `négatif` = pire.

| Métrique | En une phrase | Sur des classes 0/1 |
|---|---|---|
| **MAE** | Erreur moyenne | `= 1 − accuracy` |
| **RMSE** | Erreur qui punit les grosses erreurs | `= √(1 − accuracy)` |
| **R²** | Gain par rapport à la moyenne | `1 − (1 − accuracy)/(p(1 − p))`, avec `p` la proportion de classe 1 |

⚠️ Ces égalités supposent des **décisions 0/1**. L'application calcule aussi ces métriques sur les **probabilités** `P(Oui)` : le R² y est plus élevé (**0,386** sur le test) car la confiance graduée est prise en compte.

**Note pour le jury** : MAE, RMSE et R² ne sont **pas** les métriques habituelles d'une classification. Sur des décisions binaires, `MAE = 1 − accuracy` et `RMSE = √(1 − accuracy)` n'apportent aucune information nouvelle. Le R² sur les classes prédites est mentionné pour satisfaire la consigne, **pas** pour choisir le modèle. Le choix repose sur le **F1 macro**, le **rappel `Oui`**, la **matrice de confusion**, l'**AUC** et l'**AP**.

#### 5. Récapitulatif

| Métrique | Ce qu'elle mesure | Sens |
|---|---|---|
| **Accuracy** | Part de bonnes prédictions | ↑ mieux |
| **Precision** | Fiabilité des alertes | ↑ mieux |
| **Recall** | Capacité à détecter les menaces | ↑ mieux |
| **F1** | Équilibre précision / rappel | ↑ mieux |
| **MAE** | Erreur moyenne | ↓ mieux |
| **RMSE** | Erreur, pénalise les grosses | ↓ mieux |
| **R²** | Variance expliquée | ↑ mieux |


**Chiffres réels du Random Forest de référence** : le bloc ci-dessus est un exemple pédagogique. Sur notre test (104 messages), le RF **entraîné dans ce notebook**, au seuil 0,50, donne `TN = 67, FP = 8, FN = 13, TP = 16` (accuracy 0,798, rappel `Oui` 0,552). Au seuil 0,30, le même modèle donne `TN = 52, FP = 23, FN = 3, TP = 26`. Ces valeurs sont reproduites dans le tableau du §18.4. Le modèle **retenu** est la régression logistique améliorée, dont la matrice est donnée au §18.5.


### 18.4 Comparer deux seuils sur le modèle de référence

**Tâche** : comparer deux seuils sur le même modèle et le même test, pour voir le compromis FN / FP.
**Pourquoi** : le seuil 0,30 était posé à la main dans l'ancien protocole. Le seuil du modèle retenu, lui, est appris sur le train (plateau de coût `5·FN + FP` en CV 5×5 répétée : 0,20–0,22, médiane 0,21). Les deux lignes ci-dessous utilisent le RF de référence et le test de 104 messages : seul le seuil change.



```python
# Deux seuils, un seul modèle, un seul jeu de test
y01 = (y_test == "Oui").astype(int).values
p_rf = probabilites["Random_Forest"]

def metrics_au_seuil(proba, seuil):
    pred = (np.asarray(proba) >= seuil).astype(int)
    cm = confusion_matrix(y01, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    return {
        "Seuil": seuil,
        "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp),
        "Accuracy": accuracy_score(y01, pred),
        "Rappel Oui": recall_score(y01, pred, pos_label=1, zero_division=0),
        "Precision Oui": precision_score(y01, pred, pos_label=1, zero_division=0),
        "F1 macro": f1_score(y01, pred, average="macro", zero_division=0),
    }

comparaison_seuils = pd.DataFrame([
    metrics_au_seuil(p_rf, 0.50),
    metrics_au_seuil(p_rf, 0.30),
])
display(comparaison_seuils.round(3))
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Seuil</th>
      <th>TN</th>
      <th>FP</th>
      <th>FN</th>
      <th>TP</th>
      <th>Accuracy</th>
      <th>Rappel Oui</th>
      <th>Precision Oui</th>
      <th>F1 macro</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.5</td>
      <td>67</td>
      <td>8</td>
      <td>13</td>
      <td>16</td>
      <td>0.798</td>
      <td>0.552</td>
      <td>0.667</td>
      <td>0.734</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.3</td>
      <td>52</td>
      <td>23</td>
      <td>3</td>
      <td>26</td>
      <td>0.750</td>
      <td>0.897</td>
      <td>0.531</td>
      <td>0.733</td>
    </tr>
  </tbody>
</table>
</div>


**🔎 Interprétation** : à 0,50, le Random Forest de référence manque **13** phishing (`FN = 13`) pour **8** fausses alertes ; à 0,30, il n'en manque plus que **3**, mais génère **23** fausses alertes au lieu de 8. Le coût métier `5·FN + FP` passe de **73** (à 0,50) à **38** (à 0,30). Ce seuil 0,30 était toutefois posé à la main, sans apprentissage sur le train.

**Ce que change le protocole retenu** : la LR améliorée, avec un seuil appris à **0,21** sur les probabilités OOF du train, donne sur le test `TN = 47, FP = 28, FN = 1, TP = 28`, soit un coût **33**. Le choix n'est donc plus manuel : il résulte du plateau **0,20–0,22** issu de la CV 5×5 répétée. Le rapport de coût reste une décision métier : `c_FN = 3` déplacerait le seuil vers 0,47, `c_FN = 10` vers 0,20.


### 18.5 Évaluation finale — matrice de confusion du modèle retenu (test, seuil 0,21)

Ne pas confondre les deux matrices : la **matrice OOF** (§17.1) est calculée sur les 416 lignes du train et sert à apprendre le seuil ; **celle-ci** est l'évaluation finale sur les 104 lignes du test, lues une seule fois : **TN = 47 · FP = 28 · FN = 1 · TP = 28**. Modèle et seuil ont été choisis sur le train uniquement.



```python
# Matrice de confusion du MODÈLE RETENU (régression logistique améliorée)
# au seuil appris sur le train — le test n'est utilisé qu'ici, une seule fois.
y_pred_ameliore = (p_test >= SEUIL_OPT).astype(int)
cm = confusion_matrix(y_te01, y_pred_ameliore, labels=[0, 1])
tn, fp, fn, tp = cm.ravel()
total_cm = int(cm.sum())

annot = np.array([
    [f"TN = {tn}\n{tn / total_cm * 100:.1f} %", f"FP = {fp}\n{fp / total_cm * 100:.1f} %"],
    [f"FN = {fn}\n{fn / total_cm * 100:.1f} %", f"TP = {tp}\n{tp / total_cm * 100:.1f} %"],
])
fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(cm, annot=annot, fmt="", cmap="Blues", cbar=False, ax=ax,
            xticklabels=["Prédit : Non", "Prédit : Oui"],
            yticklabels=["Réel : Non", "Réel : Oui"],
            annot_kws={"size": 12, "fontweight": "bold"})
ax.set_xlabel("Prédiction du modèle")
ax.set_ylabel("Vérité terrain")
ax.set_title(f"Matrice de confusion — modèle retenu (seuil {SEUIL_OPT:.2f})\n"
             f"Rappel Oui = {tp / (tp + fn):.1%} | Précision Oui = {tp / (tp + fp):.1%} | "
             f"Accuracy = {(tp + tn) / total_cm:.1%}")
plt.tight_layout()
plt.show()

print(f"Seuil choisi sur le train = {SEUIL_OPT:.2f}")
print(f"TP = {tp} | TN = {tn} | FP = {fp} | FN = {fn} | total = {total_cm}")
print(f"Part des messages correctement classés = {(tp + tn) / total_cm:.1%}")
```


    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_65_0.png)
    


    Seuil choisi sur le train = 0.21
    TP = 28 | TN = 47 | FP = 28 | FN = 1 | total = 104
    Part des messages correctement classés = 72.1%


### 18.6 Balayage de seuils sur le test — chiffres de l'annexe

Ce tableau ne sert pas à choisir : le seuil retenu reste **0,21**, appris sur le train. Il montre, sur les 104 messages du test, le compromis entre faux négatifs (menaces ratées) et faux positifs (fausses alertes). Les deux dernières lignes appliquent le **triage 3 zones** : un message n'est automatisé que s'il est très sûr (`P(Oui) < seuil bas` ou `P(Oui) >= seuil haut`), sinon il part en revue humaine.


```python
# Balayage de seuils sur le TEST — lecture descriptive pour l'annexe.
# Les décisions, elles, sont prises sur le train (seuil 0,21 + triage 0,20/0,88).
lignes_balayage = []
for s in [0.07, 0.21, 0.98]:
    tn, fp, fn, tp = confusion_matrix(y_te01, (p_test >= s).astype(int), labels=[0, 1]).ravel()
    lignes_balayage.append({"Règle": f"Seuil unique {s:.2f}", "FN": int(fn), "FP": int(fp),
                            "Automatisés": len(y_te01), "Revue": 0})

bas, haut = SEUIL_BAS, SEUIL_HAUT
normal, alerte = p_test < bas, p_test >= haut
revue = ~(normal | alerte)
lignes_balayage.append({"Règle": f"Triage {bas:.2f} / {haut:.2f}", "FN": int((normal & (y_te01 == 1)).sum()),
                        "FP": int((alerte & (y_te01 == 0)).sum()),
                        "Automatisés": int(normal.sum() + alerte.sum()), "Revue": int(revue.sum())})

bas2, haut2 = 0.07, 0.98
normal2, alerte2 = p_test < bas2, p_test >= haut2
revue2 = ~(normal2 | alerte2)
lignes_balayage.append({"Règle": f"Triage {bas2:.2f} / {haut2:.2f}", "FN": int((normal2 & (y_te01 == 1)).sum()),
                        "FP": int((alerte2 & (y_te01 == 0)).sum()),
                        "Automatisés": int(normal2.sum() + alerte2.sum()), "Revue": int(revue2.sum())})

display(pd.DataFrame(lignes_balayage))
print(f"Rappel du seuil retenu (0,21) : {recall_score(y_te01, (p_test >= SEUIL_OPT).astype(int)):.3f}")
print("Lecture : 0 FN et 0 FP sur la partie automatisée est possible, mais la revue humaine augmente fortement.")

```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Règle</th>
      <th>FN</th>
      <th>FP</th>
      <th>Automatisés</th>
      <th>Revue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Seuil unique 0.07</td>
      <td>0</td>
      <td>48</td>
      <td>104</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Seuil unique 0.21</td>
      <td>1</td>
      <td>28</td>
      <td>104</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Seuil unique 0.98</td>
      <td>26</td>
      <td>0</td>
      <td>104</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Triage 0.20 / 0.88</td>
      <td>1</td>
      <td>1</td>
      <td>61</td>
      <td>43</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Triage 0.07 / 0.98</td>
      <td>0</td>
      <td>0</td>
      <td>30</td>
      <td>74</td>
    </tr>
  </tbody>
</table>
</div>


    Rappel du seuil retenu (0,21) : 0.966
    Lecture : 0 FN et 0 FP sur la partie automatisée est possible, mais la revue humaine augmente fortement.



```python
# Comparaison visuelle des scores
scores_long = resultats_df.melt(
    id_vars="Modele",
    value_vars=["Accuracy", "Precision_macro", "Recall_macro", "F1_macro"],
    var_name="Metrique",
    value_name="Score"
)
plt.figure(figsize=(11, 5))
sns.barplot(data=scores_long, x="Modele", y="Score", hue="Metrique")
plt.ylim(0, 1)
plt.title("Comparaison des modèles sur le jeu de test")
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()
```


    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_68_0.png)
    


**Tâche** : calculer l'AUC et tracer les courbes ROC et Precision-Recall pour les trois modèles de référence.
**Pourquoi** : l'accuracy, la précision et le rappel dépendent d'un seuil unique. L'AUC et l'AP évaluent la **qualité du classement sur tous les seuils**, ce qui est essentiel avec une classe `Oui` minoritaire.



```python
from sklearn.metrics import roc_curve, precision_recall_curve, auc

y01 = (y_test == "Oui").astype(int)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
for nom, pipeline in pipelines.items():
    idx_oui = list(pipeline.classes_).index("Oui")
    p = pipeline.predict_proba(X_test)[:, idx_oui]
    fpr, tpr, _ = roc_curve(y01, p)
    ax1.plot(fpr, tpr, lw=1.8, label=f"{nom} (AUC = {auc(fpr, tpr):.3f})")
    prec, rec, _ = precision_recall_curve(y01, p)
    ax2.plot(rec, prec, lw=1.8, label=f"{nom} (AP = {average_precision_score(y01, p):.3f})")

ax1.plot([0, 1], [0, 1], "k--", lw=1, label="hasard (AUC = 0,500)")
ax1.set_xlabel("Taux de faux positifs")
ax1.set_ylabel("Taux de vrais positifs")
ax1.set_title("Courbe ROC — jeu de test")
ax2.axhline(y01.mean(), color="k", ls="--", lw=1,
            label=f"hasard (AP = {y01.mean():.3f})")
ax2.set_xlabel("Rappel `Oui`")
ax2.set_ylabel("Précision `Oui`")
ax2.set_title("Courbe Precision-Recall — jeu de test")
for ax in (ax1, ax2):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, loc="lower right")
plt.tight_layout()
plt.show()

auc_df = resultats_df[["Modele", "AUC", "Average_precision"]].copy()
display(auc_df.round(3))
```


    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_70_0.png)
    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Modele</th>
      <th>AUC</th>
      <th>Average_precision</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Random_Forest</td>
      <td>0.866</td>
      <td>0.698</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Regression_logistique</td>
      <td>0.832</td>
      <td>0.656</td>
    </tr>
    <tr>
      <th>2</th>
      <td>SVM_RBF</td>
      <td>0.834</td>
      <td>0.633</td>
    </tr>
  </tbody>
</table>
</div>


**🔎 Interprétation** : l'AUC est la probabilité qu'un message malveillant reçoive un score `P(Oui)` plus élevé qu'un message légitime. 0,5 = tirage au sort, 1 = séparation parfaite. L'AP résume la courbe Precision-Recall et est plus informative que l'AUC quand la classe positive est minoritaire (ici 28 %).

**Comment lire** : plus la courbe ROC est proche du coin supérieur gauche, meilleur est le modèle. Sur la courbe Precision-Recall, avancer vers la droite augmente le rappel mais fait baisser la précision.

**Utilité** : confirmer que les modèles classent mieux que le hasard **indépendamment du seuil**, puis justifier le seuil **0,21** par le coût métier (§17.2 et §18.4) plutôt que par une métrique unique.

⚠️ Ces courbes sont calculées sur les **104 messages du test, dont 29 malveillants** : elles donnent une indication, pas une garantie de généralisation à de vrais e-mails.


## 19. Importance des variables sur le train

La permutation importance mesure la baisse de performance lorsqu'on mélange les valeurs d'une variable. Elle est calculée **sur le train (416 messages)**, avec le Random Forest de référence, sans réentraîner le modèle et **sans relire le test**. Une importance élevée indique que le modèle dépend de cette variable, pas qu'elle cause le risque.



```python
meilleur_nom = resultats_df.iloc[0]["Modele"]
meilleur_pipeline = pipelines[meilleur_nom]

# Importance calculée sur le TRAIN uniquement : le test n'est plus lu après son évaluation finale.
perm = permutation_importance(
    meilleur_pipeline, X_train, y_train,
    n_repeats=15,
    random_state=RANDOM_STATE,
    scoring="f1_macro"
)
importance = pd.DataFrame({
    "Variable": X.columns,
    "Importance_moyenne": perm.importances_mean,
    "Ecart_type": perm.importances_std
}).sort_values("Importance_moyenne", ascending=False)

display(importance)
plt.figure(figsize=(9, 5))
ax = sns.barplot(data=importance.head(12), x="Importance_moyenne", y="Variable")
for container in ax.containers:
    ax.bar_label(container, fmt="%.3f", padding=2, fontsize=7)
plt.title(f"Permutation importance — {meilleur_nom} — train seul (n = {len(X_train)})")
plt.tight_layout()
plt.show()

```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Variable</th>
      <th>Importance_moyenne</th>
      <th>Ecart_type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>domaine_age_jours</td>
      <td>0.242940</td>
      <td>0.017595</td>
    </tr>
    <tr>
      <th>3</th>
      <td>urgence_score</td>
      <td>0.155835</td>
      <td>0.019130</td>
    </tr>
    <tr>
      <th>6</th>
      <td>expediteur_connu</td>
      <td>0.146920</td>
      <td>0.012907</td>
    </tr>
    <tr>
      <th>2</th>
      <td>nb_liens</td>
      <td>0.101181</td>
      <td>0.009922</td>
    </tr>
    <tr>
      <th>1</th>
      <td>longueur_message</td>
      <td>0.049192</td>
      <td>0.008509</td>
    </tr>
    <tr>
      <th>8</th>
      <td>personnalisation_score</td>
      <td>0.043761</td>
      <td>0.005820</td>
    </tr>
    <tr>
      <th>0</th>
      <td>heure_envoi</td>
      <td>0.039412</td>
      <td>0.008131</td>
    </tr>
    <tr>
      <th>5</th>
      <td>fautes_langue</td>
      <td>0.020201</td>
      <td>0.005820</td>
    </tr>
    <tr>
      <th>7</th>
      <td>piece_jointe</td>
      <td>0.011470</td>
      <td>0.002606</td>
    </tr>
  </tbody>
</table>
</div>



    
![png](notebook_ML_IA_confiance_numerique_files/notebook_ML_IA_confiance_numerique_73_1.png)
    


## 20. Tester un scénario individuel

La fonction ci-dessous reçoit un dictionnaire des variables explicatives. Elle renvoie la classe prédite et les probabilités par classe.

Pour un vrai formulaire Streamlit, reprendre les colonnes de `X.columns` et contrôler les valeurs saisies. Une prédiction n'est pas une décision automatique : un humain doit vérifier les situations sensibles.



```python
# Modèle retenu = régression logistique améliorée (§17).
# Le F1 du test n'a PAS servi à choisir le modèle ni les seuils.
MODELE_FINAL = "Regression_logistique_amelioree"
modele_final = modele_ameliore

def predire_scenario(valeurs):
    """Prédit le verdict d'un scénario à partir des colonnes BRUTES de X."""
    scenario = pd.DataFrame([valeurs]).reindex(columns=X.columns)
    proba = modele_final.predict_proba(scenario)[0]
    p_oui = float(proba[list(modele_final.classes_).index("Oui")])
    classe = "Oui" if p_oui >= SEUIL_OPT else "Non"
    if p_oui >= SEUIL_HAUT:
        zone, action = "🔴 ALERTE", "vérification humaine prioritaire"
    elif p_oui >= SEUIL_BAS:
        zone, action = "🟠 VIGILANCE", "revue humaine — à vérifier par un analyste"
    else:
        zone, action = "🟢 NORMAL", "surveillance courante"
    return {"classe_predite": classe, "binaire": classe, "zone": zone, "action": action,
            "P_Oui": p_oui, "verdict": zone + " — " + action,
            "probabilites": dict(zip(modele_final.classes_, proba))}

print("Modèle retenu pour les scénarios :", MODELE_FINAL)
print("Seuil binaire :", round(SEUIL_OPT, 2),
      "| triage :", round(SEUIL_BAS, 2), "/", round(SEUIL_HAUT, 2))
print("Variables attendues (brutes) :", X.columns.tolist())

```

    Modèle retenu pour les scénarios : Regression_logistique_amelioree
    Seuil binaire : 0.21 | triage : 0.2 / 0.88
    Variables attendues (brutes) : ['heure_envoi', 'longueur_message', 'nb_liens', 'urgence_score', 'domaine_age_jours', 'fautes_langue', 'expediteur_connu', 'piece_jointe', 'personnalisation_score']



```python
# Exemple neutre construit automatiquement à partir des médianes/modes du TRAIN.
# Modifier les valeurs pour créer vos propres scénarios métier.
scenario_exemple = {}
for col in X.columns:
    if col in features_num:
        scenario_exemple[col] = X_train[col].median()
    else:
        scenario_exemple[col] = X_train[col].mode(dropna=True).iloc[0]

display(pd.DataFrame([scenario_exemple]))
print(predire_scenario(scenario_exemple))
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>heure_envoi</th>
      <th>longueur_message</th>
      <th>nb_liens</th>
      <th>urgence_score</th>
      <th>domaine_age_jours</th>
      <th>fautes_langue</th>
      <th>expediteur_connu</th>
      <th>piece_jointe</th>
      <th>personnalisation_score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>12.0</td>
      <td>423.0</td>
      <td>1.0</td>
      <td>4.5</td>
      <td>531.0</td>
      <td>2.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5.0</td>
    </tr>
  </tbody>
</table>
</div>


    {'classe_predite': 'Oui', 'binaire': 'Oui', 'zone': '🟠 VIGILANCE', 'action': 'revue humaine — à vérifier par un analyste', 'P_Oui': 0.3329905876378498, 'verdict': '🟠 VIGILANCE — revue humaine — à vérifier par un analyste', 'probabilites': {'Non': 0.6670094123621502, 'Oui': 0.3329905876378498}}


## 21. Sauvegarde du modèle et des artefacts

Le pipeline sauvegardé contient le prétraitement et le modèle : Streamlit le charge sans le réentraîner. On conserve aussi la liste des colonnes, la cible, les seuils et les métriques réellement calculées.

Les valeurs `Dummy` et `KNN` de l'ancien `model_meta.json` ne sont **pas** réexportées : elles ne correspondent à aucun code de ce protocole et n'étaient pas reproductibles.



```python
DOSSIER_SORTIE = Path("artefacts")
DOSSIER_SORTIE.mkdir(exist_ok=True)

joblib.dump(modele_ameliore, DOSSIER_SORTIE / "modele_phishing_ia.joblib")
joblib.dump(
    {"features": X.columns.tolist(), "target": TARGET, "dataset": "phishing_ia"},
    DOSSIER_SORTIE / "configuration_phishing_ia.joblib"
)

resultats_df.to_csv(DOSSIER_SORTIE / "comparaison_modeles_phishing_ia.csv", index=False)

print("Modèle et résultats sauvegardés dans :", DOSSIER_SORTIE.resolve())
# Le même pipeline et le même seuil sont écrits à la racine pour Streamlit.
joblib.dump(modele_ameliore, "model.joblib")
meta_app["seuil"] = SEUIL_OPT
meta_app["meilleur_modele"] = "LogisticRegression_amelioree"
meta_app["f1_macro_test"] = float(f1_opt)
with open("model_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta_app, f, ensure_ascii=False, indent=2)
with open(DOSSIER_SORTIE / "seuil_phishing_ia.json", "w", encoding="utf-8") as f:
    json.dump({"seuil": SEUIL_OPT, "seuil_bas": SEUIL_BAS, "seuil_haut": SEUIL_HAUT,
               "modele": "LogisticRegression + log1p(age) + interactions, seuils appris sur le train (CV 5x5 repetee)",
               "protocole": "cout FN=5 / FP=1, plateau de coût 0.20-0.22, triage 0.20/0.88 ; test lu une seule fois",
               "validation": "AUC en validation croisée 0.909 +/- 0.003 ; AUC test 0.910 ; AP test 0.810",
               "triage_test": "61/104 automatises, FN 1, FP 1, 43 revues humaines"},
              f, ensure_ascii=False, indent=2)
print("model.joblib / model_meta.json synchronisés avec le notebook.")

```

    Modèle et résultats sauvegardés dans : /home/himawari/Desktop/learn_python/iscae/Mini-projet 3: Veille stratégique – IA et confiance numérique/app_phishing_ia/artefacts
    model.joblib / model_meta.json synchronisés avec le notebook.


## 22. Conclusion métier — résultats observés

Réponses appuyées sur les sorties réelles (modèle amélioré, CV 5×5 répétée) :

- **Q1 — Besoin** : prioriser la file de l'analyste face à des messages de phishing générés par IA, sans supprimer automatiquement. Signaux les plus discriminants **sur le train** : `domaine_age_jours` (r = −0,322), `urgence_score` (+0,285), `expediteur_connu` (−0,278), `nb_liens` (+0,244).
- **Q2 — Classes** : 374 `Non` / 146 `Oui` sur 520 lignes propres, soit un déséquilibre modéré ; d'où `class_weight="balanced"` et le pilotage par le rappel `Oui`, pas par l'accuracy.
- **Q3 — Données** : 4 doublons supprimés (524 → 520), `date` et `semaine` écartés, valeurs manquantes imputées par la médiane **dans le pipeline**. La cible n'est jamais dans `X`.
- **Q4 — Modèle** : le RF de référence a le meilleur F1 macro brut sur le test (0,734) mais la LR améliorée, évaluée avec le même protocole 5-fold, obtient **F1 macro CV = 0,815 ± 0,066**. Le modèle retenu est la **LR améliorée** : AUC test **0,910**, AP **0,810**, Brier **0,123** ; CV 5×5 répétée AUC **0,909 ± 0,003**, AP **0,812 ± 0,003**.
- **Q5 — Seuil et triage** : plateau de coût en validation croisée `5·FN + FP` **0,20–0,22**, médiane **0,21**. Sur le test : **TN = 47, FP = 28, FN = 1, TP = 28**, rappel `Oui` **96,6 %**, F1 macro **0,712**, coût **33**. Le triage 0,20 / 0,88 traite **61/104** messages automatiquement (**1 FN, 1 FP** sur cette partie) et confie **43 cas ambigus** à l'analyste. L'incertitude reste large : IC95 % bootstrap rappel `[0,886 ; 1,000]`, précision `[0,368 ; 0,636]`, fausses alertes `[0,262 ; 0,481]`.
- **Q6 — Erreurs** : le faux négatif est le plus coûteux ; c'est pourquoi le seuil binaire est bas. Mais baisser seulement le seuil augmente les faux positifs : le triage 3 zones réduit les deux sur la partie automatisée **en échange de 43 revues humaines**.
- **Q7 — Limites** : données synthétiques, 104 messages en test (29 `Oui`), probabilités non calibrées, dérive temporelle non traitée, corrélation ≠ causalité, CV non imbriquée (hyperparamètres fixés a priori).
- **Q8 — Gouvernance** : validation humaine obligatoire, aucune suppression automatique, journal des décisions, réentraînement et recalibrage du seuil à chaque lot étiqueté, données personnelles réelles exclues du prototype.

### Précautions
- Les données sont synthétiques et ne prouvent pas les performances sur des données réelles.
- Ne jamais présenter une prédiction comme une certitude.
- Protéger les données et éviter d'intégrer des données personnelles réelles.
- Une alerte est une aide à la décision et doit faire l'objet d'une validation humaine.


## 23. Rappel des livrables du cahier des charges

- Notebook Jupyter propre et exécutable de haut en bas.
- Rapport PDF de 5 à 8 pages.
- Application Streamlit et fichiers Python nécessaires.
- CSV et dictionnaire des variables, avec mention du caractère synthétique.
- Modèle sauvegardé et `requirements.txt`.
- `README.md` avec installation et lancement.
- Au moins trois scénarios : normal, à risque et cas limite.


## Annexe — vérifications de cohérence (à montrer au jury)

**Un seul notebook, réellement exécuté**

- Le notebook a été réexécuté de zéro après correction : **82 cellules, 0 erreur**.
- Toutes les statistiques descriptives (corrélations, moyennes et médianes par classe) portent sur le **train seul (416 messages)** ; le test (104 messages) n'est utilisé qu'au §16 et au §18.
- Toutes les valeurs affichées dans les markdowns sont celles des sorties réelles : plus de chiffres « historiques » recopiés.
- `model_meta.json` ne contient plus `Dummy` ni `KNN`, valeurs non reproductibles depuis le protocole actuel.

**Scénario neutre produit par le notebook**

Le notebook construit un scénario à partir des **médianes du train** (`heure_envoi = 12`, `longueur_message = 423`, `nb_liens = 1`, `urgence_score = 4,5`, `domaine_age_jours = 531`, `fautes_langue = 2`, `expediteur_connu = 0`, `piece_jointe = 0`, `personnalisation_score = 5`) :

| Scénario | P(Oui) | Classe binaire | Zone |
|---|---:|---|---|
| Médianes du train | 33,30 % | `Oui` — malveillant | 🟠 VIGILANCE |

L'application Streamlit complète ce cas par trois scénarios métier (normal, à risque, limite) qui donnent respectivement 🟢 `Non`, 🔴 `Oui` à 100 % et 🟠 `Oui` à 47,1 % avec revue humaine. La classe ne vaut jamais « À vérifier » : elle est `Oui` / `Non`, le triage est une colonne séparée.

**FN / FP = 0 sur le test : les chiffres, sans promesse**

Sortie du §18.6 (balayage descriptif sur le test) :

| Règle | FN | FP | Automatisés | Revue |
|---|---:|---:|---:|---:|
| Seuil unique 0,07 | 0 | 48 | 104 | 0 |
| Seuil unique 0,21 (retenu) | 1 | 28 | 104 | 0 |
| Seuil unique 0,98 | 26 | 0 | 104 | 0 |
| Triage 0,20 / 0,88 (retenu) | 1 | 1 | 61 | 43 |
| Triage 0,07 / 0,98 | 0 | 0 | 30 | 74 |

Donc **0 FN et 0 FP sur la partie automatisée est possible**, mais alors **74 messages sur 104 (71 %) partent en revue humaine** et le système n'automatise plus que 30 cas. À 0,89 / 0,90, on a 1 FP mais 15 à 18 FN. Le compromis retenu reste **0,21 + triage 0,20 / 0,88**.
