# 02 — Préprocessing et pipeline de bout en bout

> **Source de vérité.** Notebook `notebook_ML_IA_confiance_numerique.ipynb` et pipeline sérialisé `model.joblib`. Ce document décrit la chaîne exacte du **modèle retenu** (régression logistique améliorée) et les règles anti-fuite qui doivent l'accompagner. Données synthétiques et pédagogiques, sans validation sur de vraies campagnes.

---

## 1. Construction de `X` et `y`

```text
X = 9 variables numériques
    heure_envoi, longueur_message, nb_liens, urgence_score,
    domaine_age_jours, fautes_langue, expediteur_connu,
    piece_jointe, personnalisation_score

y = message_malveillant  (Non = 0 / Oui = 1 selon le codage du notebook)
```

- **Aucune variable catégorielle** : il n'y a donc aucun encodeur (`OneHotEncoder`, `OrdinalEncoder`, etc.) à ajuster. Le point d'attention « encodage » de la section 4 est ici **non applicable**, mais il doit être documenté comme tel.
- **`date` est exclue** : variable calendaire sans justification métier, réservée à l'exploration (voir `01`).
- **La cible n'est jamais dans `X`** : elle sert uniquement à `y` et au calcul des poids de classe.

---

## 2. Séparation train / test

```python
train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
```

| Jeu | Effectif total | `Non` | `Oui` |
|---|---:|---:|---:|
| Train (80 %) | 416 | 299 | 117 |
| Test (20 %) | 104 | 75 | 29 |
| **Total** | **520** | **374** | **146** |

### Pourquoi 80 / 20

Le partage 80/20 conserve l'essentiel des 520 observations pour l'apprentissage tout en réservant un jeu de test indépendant pour estimer la performance. Avec 520 lignes, un test plus petit rendrait les métriques très instables (petit nombre de positifs) ; un test plus large priverait inutilement le modèle de données d'entraînement. Le compromis 80/20 est donc adapté à l'échelle de ce jeu.

### Pourquoi `stratify=y`

La proportion de `Oui` est de 28,1 % sur l'ensemble. Un split aléatoire simple peut faire varier cette proportion dans chaque sous-jeu, en particulier sur les 104 lignes de test. La stratification force chaque partition à reproduire la répartition de la cible : 117/416 et 29/104. Cela réduit la variance de l'estimation et évite qu'un tirage défavorable donne un test pauvre en positifs.

### Pourquoi `random_state=42`

Fixer la graine rend le split **reproductible** : toute exécution ultérieure obtient exactement les mêmes 416 lignes d'entraînement et les mêmes 104 lignes de test. Sans graine, les résultats comparés entre modèles ou entre sessions ne seraient pas comparables.

---

## 3. Fuite de données : principe général

Une **fuite de données** (*data leakage*) se produit lorsqu'une information du jeu de test— même indirecte — est utilisée pendant l'apprentissage. La conséquence est systématique : les métriques calculées sur le test deviennent **optimistes** et ne reflètent pas la capacité de généralisation.

Règle opérationnelle : **toute opération qui apprend quelque chose des données doit être ajustée sur le train uniquement**, puis appliquée telle quelle au test.

| Étape | Apprend-elle quelque chose ? | Où doit-elle être ajustée ? |
|---|---|---|
| Suppression des doublons | Non ( règle fixe, avant split ) | Avant split, sur le jeu complet — le doublon est une propriété du fichier source |
| Split stratifié | Non ( tirage avec graine ) | Avant toute statistique apprise |
| Feature engineering `FeaturesPhishing` | **Non** : transformations déterministes | Aucun ajustement : `fit()` ne stocke aucune statistique |
| Imputation par la médiane | **Oui** : apprend une médiane par colonne reçue (8 après `FeaturesPhishing`) | Sur le train de chaque fold, **jamais sur le jeu complet** |
| Standardisation | **Oui** : apprend moyennes et écarts-types | Sur le train de chaque fold, après imputation |
| Encodage de catégories | Oui en général | **Non applicable ici** : aucune variable catégorielle |
| Réglage des hyperparamètres | Oui (sélection) | Sur le train / validation croisée, jamais sur le test final |
| Choix du seuil de décision | Oui (sélection) | Sur train / validation, idéalement par OOF ; voir ci-dessous |
| Entraînement du classifieur | **Oui** | Sur le train uniquement |
| Évaluation finale | Non | Sur le test, une seule fois après gel du modèle et du seuil |

---

## 4. Points d'attention détaillés

### 4.1 Imputation

10 valeurs sont manquantes dans `domaine_age_jours`, 0 ailleurs. L'imputation retenue est la **médiane**, intégrée comme étape du pipeline (`SimpleImputer(strategy="median")`). Deux exigences :

1. la médiane de la colonne `log_age` (issue de `domaine_age_jours` après `FeaturesPhishing`) est **calculée sur le train de chaque fold**, pas sur les 520 lignes ;
2. elle est ensuite **appliquée** aux lignes du test (ou du fold de validation) sans être recalculée.

Imputer sur le jeu complet avant le split transmettrait au train des informations sur la distribution du test : c'est une fuite, même si elle ne porte que sur 10 valeurs. Le pipeline scikit-learn garantit ce comportement quand `fit` est appelé sur le train et `transform` sur le test.

### 4.2 Standardisation

`StandardScaler` est appliqué **après** imputation et **après** feature engineering. Il centre et réduit chaque caractéristique en utilisant la moyenne et l'écart-type appris sur le train. Deux raisons :

- la régression logistique régularisée est sensible à l'échelle des variables ;
- les variables du projet ont des échelles très différentes (`domaine_age_jours` jusqu'à 5 874, indicatrices 0/1).

L'ordre importe : imputer d'abord évite de propager des `NaN` dans le scaler ; construire les features d'abord garantit que les colonnes transformées (`log_age`, produits) sont également standardisées avec les statistiques du train.

### 4.3 Feature engineering

La classe `FeaturesPhishing` est **intégrée au Pipeline** et produit exactement 8 caractéristiques :

| Caractéristique | Formule | Intention métier |
|---|---|---|
| `log_age` | `log1p(domaine_age_jours)` = `log(1 + domaine_age_jours)` | Compresser l'asymétrie de l'âge du domaine (moyenne 740,68 ; médiane 512,5 ; écart-type 764,34 ; max 5 874) |
| `urg_x_inconnu` | `urgence_score × (1 − expediteur_connu)` | L'urgence est plus suspecte quand l'expéditeur n'est pas connu |
| `liens_x_inconnu` | `nb_liens × (1 − expediteur_connu)` | Les liens sont plus suspects quand l'expéditeur n'est pas connu |
| `urgence_score` | valeur brute | Signal principal (corrélation train +0,285) |
| `nb_liens` | valeur brute | Signal principal (corrélation train +0,244) |
| `expediteur_connu` | valeur brute 0/1 | Signal principal (corrélation train −0,278) |
| `piece_jointe` | valeur brute 0/1 | Signal faible conservé (corrélation train +0,060) |
| `personnalisation_score` | valeur brute | Signal faible conservé (corrélation train +0,133) |

**Variables retirées du modèle amélioré** : `heure_envoi`, `longueur_message`, `fautes_langue` (bruit / faible signal : corrélations train respectives −0,027, −0,114 et −0,022). Elles restent présentes dans le CSV et dans l'EDA du document `01`.

`log1p` est bien défini ici : le minimum observé de `domaine_age_jours` est 1, donc `1 + x > 0`.

### 4.4 `fit()` de `FeaturesPhishing` et absence de fuite

Le `fit()` de `FeaturesPhishing` **n'apprend aucune statistique** : il ne calcule ni moyenne, ni médiane, ni paramètre. Les transformations sont déterministes et s'appliquent identiquement à chaque ligne, indépendamment des autres lignes. Par conséquent, appeler `fit` sur le train puis `transform` sur le test ne transmet aucune information du train au test au-delà des paramètres légitimes du modèle. Il n'y a donc **pas de fuite introduite par le feature engineering**.

À noter : les deux produits (`urg_x_inconnu`, `liens_x_inconnu`) sont des fonctions algébriques de leurs facteurs. Ils créent donc des dépendances avec `urgence_score`, `nb_liens` et `expediteur_connu` **par construction**, ce qui est distinct de la multicolinéarité observée entre variables brutes (|r| ≤ 0,07 sur le jeu complet, voir `01`). La régularisation de la régression logistique et la standardisation contribuent à stabiliser l'estimation.

### 4.5 Hyperparamètres du classifieur

```python
LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42)
```

- `max_iter=3000` : limite portée haut pour laisser l'optimiseur converger sur des caractéristiques standardisées et interactives.
- `random_state=42` : reproductibilité du solveur.
- `class_weight="balanced"` : pondération automatique des classes.

#### `class_weight="balanced"`

Avec 374 `Non` et 146 `Oui`, une perte non pondérée favoriserait la classe majoritaire. scikit-learn attribue à chaque classe un poids proportionnel à l'inverse de sa fréquence, selon la formule `n_samples / (n_classes × n_samples_de_la_classe)`. La classe minoritaire `Oui` reçoit donc un poids plus élevé que `Non`, ce qui pénalise davantage les faux négatifs (menaces manquées). **Les valeurs numériques exactes des poids appliqués ne sont pas disponibles dans les artefacts** ; seule la règle `balanced` est documentée.

Ce choix est cohérent avec le coût métier asymétrique : rater un message malveillant est plus coûteux qu'examiner une fausse alerte. Il explique aussi que le seuil optimal rapporté (0,21) soit bien inférieur à 0,50.

### 4.6 Seuil de décision à 0,21

Le modèle retenu est évalué à un **seuil de 0,21** : F1 macro 0,712. Ce seuil est plus bas que le seuil implicite de 0,50 des comparaisons historiques, ce qui augmente le rappel sur la classe `Oui` au prix de quelques fausses alertes.

**L'origine exacte du seuil 0,21 n'est pas disponible dans les artefacts.** Règle à respecter : un seuil doit être choisi sur le train ou par validation croisée (idéalement sur des prédictions OOF), puis figé avant l'évaluation sur le test. S'il a été sélectionné en regardant directement le jeu de test, le F1 macro de 0,712 devient une estimation **optimiste** et doit être lu comme tel. Ce point est signalé, non corrigé.

---

## 5. Pipeline exact sérialisé

Chaîne sauvegardée dans `model.joblib` (ordre strict) :

```text
1. FeaturesPhishing        → 8 caractéristiques déterministes (fit sans statistique)
2. SimpleImputer(median)   → impute domaine_age_jours (10 valeurs) sur la base du train
3. StandardScaler          → centrage / réduction appris sur le train
4. LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42)
```

Le jeu de données d'entrée du pipeline est `X` (9 colonnes numériques, sans `date` ni cible). La sortie est une probabilité puis une décision selon le seuil retenu.

### Ce qui est appris, et quand

| Étape | `fit` | `transform` / `predict` |
|---|---|---|
| `FeaturesPhishing` | Aucun paramètre | Calcul de `log_age`, `urg_x_inconnu`, `liens_x_inconnu`, sélection des 8 colonnes |
| `SimpleImputer` | Une médiane par colonne reçue du feature engineering (8 colonnes) ; celle de `log_age` dérive de `domaine_age_jours` | Remplacement des `NaN` |
| `StandardScaler` | Moyennes et écarts-types des 8 colonnes | Mise à l'échelle |
| `LogisticRegression` | Coefficients et intercept | Probabilité, puis classe selon le seuil |

---

## 6. Cohérence entraînement / prédiction

Le sérialisation de **tout le pipeline** dans `model.joblib` est une garantie essentielle : l'application de prédiction ne doit pas réimplémenter manuellement le feature engineering, l'imputation ou la standardisation.

En pratique :

1. charger `model.joblib` ;
2. construire une ligne d'entrée avec **exactement les 9 colonnes numériques** attendues, dans le même ordre et avec les mêmes types ;
3. appeler la méthode de prédiction du pipeline : celui-ci applique dans l'ordre `FeaturesPhishing` → imputation → standardisation → régression logistique ;
4. appliquer le seuil de décision documenté au résultat, si le pipeline ne l'intègre pas lui-même.

Une dérive entre le code d'entraînement et le code de service (par exemple un `log` naturel au lieu de `log1p`, ou une médiane recalculée sur les données en production) produirait des prédictions incohérentes sans erreur visible. Le pipeline sérialisé supprime cette classe de bugs. L'implémentation de service est désormais visible dans `app.py` : `details_probabilite()` applique les étapes du pipeline sauvegardé et vérifie que `sigmoïde(intercept + Σ coef × variable standardisée)` reconstitue `predict_proba()` (écart 0,00). Voir `docs/10_probability_and_learning.md`.

---

## 7. Points à retenir

- `X` contient 9 variables numériques ; `date` et la cible en sont absentes ; aucune catégorie à encoder.
- Split 80/20 stratifié, graine 42 : 416 / 104 lignes, avec 299/117 et 75/29 selon la classe.
- Toute statistique (médiane, moyenne, écart-type) est apprise sur le train de chaque fold, jamais sur le jeu complet.
- `FeaturesPhishing` est déterministe : son `fit()` n'apprend rien, donc aucune fuite de ce côté.
- `class_weight="balanced"` compense un déséquilibre modéré (374 vs 146) en pénalisant davantage les erreurs sur la classe minoritaire.
- Le seuil 0,21 est la médiane du plateau de coût OOF `5·FN + FP` = 0,20–0,22, choisie sur le train seul ; il donne F1 macro test 0,712 (voir `docs/05` et `docs/10`).
- En production, réutiliser le pipeline sérialisé plutôt que de reconstruire les étapes à la main.
