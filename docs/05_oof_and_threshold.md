# 05 — Validation croisée, probabilités OOF et choix du seuil

Ce document explique comment le seuil de décision **0,21** a été appris sans consulter le jeu de test. Il s'appuie sur le notebook `notebook_ML_IA_confiance_numerique.ipynb`, sur `model.joblib` et sur `model_meta.json`.

## 1. Protocole de validation croisée

Le jeu d'entraînement contient **416 observations** (299 `Non` / 117 `Oui`), issues d'un split stratifié 80/20 avec `random_state=42`. C'est **uniquement sur ces 416 lignes** que la validation croisée est effectuée.

Pour chacune des cinq graines `seed = 42, 43, 44, 45, 46` :

```python
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
p = cross_val_predict(modele, X_train, y_train, cv=cv, method="predict_proba")[:, 1]
```

- 5 plis stratifiés par répétition ;
- 5 répétitions avec des découpages différents ;
- **5 × 5 = 25 entraînements** au total ;
- `method="predict_proba"` fournit une probabilité `P(Oui)` par observation et par répétition ;
- la **moyenne des 5 vecteurs de probabilités** donne une probabilité OOF unique par observation du train.

La cible `message_malveillant` n'est jamais présente dans `X` (assertion dans le notebook).

## 2. Résultats de la validation croisée

| Indicateur | Valeur |
|---|---|
| AUC CV moyen | 0,9092 ± 0,0031 |
| AP CV moyen | 0,8119 ± 0,0034 |
| AUC sur probabilités OOF moyennées | 0,9112 |
| AP sur probabilités OOF moyennées | 0,8154 |

L'AUC et l'AP sont calculées sur des scores continus : elles ne dépendent pas d'un seuil de décision fixe. Les probabilités OOF servent, elles, à fixing le seuil sur le train.

## 3. Vocabulaire : Train, Validation, Test, CV, OOF

| Notion | Définition dans ce projet | Rôle |
|---|---|---|
| **Train** | 416 lignes, dont 299 `Non` et 117 `Oui` | Apprentissage, validation croisée, choix du modèle et du seuil |
| **Validation** | À chaque répétition, le pli mis de côté dans `StratifiedKFold` | Fournit une prédiction sur des données non vues par le modèle du pli |
| **Test** | 104 lignes, dont 75 `Non` et 29 `Oui` | Évaluation finale, **lue une seule fois**, après tous les choix |
| **CV** | *Cross-validation* : le protocole 5 plis × 5 répétitions | Estime la stabilité des performances sur le train |
| **OOF** | *Out-of-fold* : une méthode de production de prédictions, **pas une métrique** | Donne des probabilités « hors entraînement » pour optimiser le seuil sans toucher au test |

Confusion fréquente à éviter : dire « l'OOF est un score » est faux. L'OOF désigne la façon dont les prédictions sont générées ; l'AUC et l'AP sont des métriques calculées à partir de ces prédictions.

## 4. Optimisation du seuil par coût métier

Le balayage porte sur les probabilités OOF du train, avec :

```python
seuils = np.round(np.arange(0.02, 0.99, 0.01), 2)
cout(t) = 5 * FN(t) + FP(t)
```

Le rapport 5:1 traduit l'hypothèse métier suivante : **un phishing manqué (FN) coûte cinq fois plus cher qu'une fausse alerte (FP)**. Ce rapport doit être validé par un responsable sécurité ; la date de cette validation : **non disponible dans les artefacts**.

| Seuil | TN | FP | FN | TP | Coût `5·FN + FP` |
|---|---:|---:|---:|---:|---:|
| 0,20 | — | 118 | 2 | — | **128 (minimum)** |
| **0,21 (retenu)** | 182 | 117 | 3 | 114 | **132** |
| 0,22 | — | 114 | 4 | — | 134 |

À 0,21, la matrice OOF complète est **TN 182 · FP 117 · FN 3 · TP 114**, soit 416 observations. Le coût y est donc **132**, et non 128 : la valeur 128 correspond au seuil 0,20. Un correctif a déjà été appliqué sur ce point dans le notebook et le README (commit `f573fc9`).

Le plateau de coût minimal s'étend de **0,20 à 0,22**. Le seuil retenu est la **médiane du plateau, soit 0,21** : plutôt qu'un point arbitraire, on choisit le centre d'une zone stable où le coût varie peu.

### Sensibilité au rapport de coûts

| `c_FN` | Seuil optimal | Plateau |
|---:|---:|---|
| 3 | 0,47 | 0,39–0,57 |
| 5 | 0,21 | 0,20–0,22 |
| 10 | 0,20 | 0,20–0,20 |

Le choix du seuil est donc une **décision métier**, pas une propriété intrinsèque du modèle : changer le rapport de coûts change la décision. Le jeu de test n'intervient à aucun moment dans ce raisonnement.

## 5. Triage appris sur le train : une action, pas une classe

Le modèle reste **binaire** :

- `P(Oui) ≥ 0,21` → **Malveillant** ;
- `P(Oui) < 0,21` → **Non malveillant**.

Par-dessus ce verdict, un triage en trois zones, également appris sur le train, indique la priorité de vérification :

| Zone | Intervalle de `P(Oui)` | Action |
|---|---|---|
| 🟢 Normal | `< 0,20` | Surveillance courante |
| 🟠 Revue humaine | `0,20 – 0,88` | Vérification par un analyste |
| 🔴 Alerte | `≥ 0,88` | Vérification humaine prioritaire |

Ces trois zones ne constituent **pas une troisième classe** : elles ne modifient jamais le verdict binaire. Exemple : `P(Oui) = 0,28` donne **Malveillant** (0,28 ≥ 0,21) tout en étant en zone **VIGILANCE**.

## 6. Pourquoi ne pas annuler FN et FP simultanément avec un seul seuil

Avec un score continu et un seuil unique, les ensembles prédits `Oui` sont **emboîtés** : baisser le seuil ne peut qu'ajouter des positifs prédits. Par conséquent :

- `FN` ne peut que diminuer quand le seuil baisse ;
- `FP` ne peut qu'augmenter quand le seuil baisse.

Obtenir `FN = 0` **et** `FP = 0` exigerait une séparation parfaite : tous les messages malveillants auraient un `P(Oui)` strictement supérieur à tous les messages légitimes. Dans ce cas, l'AUC empirique vaudrait 1. Or l'AUC OOF est de **0,9112**, donc différente de 1 : il existe des inversions de classement. Pour toute position de seuil dans la zone de chevauchement, on doit accepter soit un `FN`, soit un `FP`.

Le choix du seuil est donc un **compromis**, pas une recherche du zéro absolu : à 0,20 on a 2 FN et 118 FP, à 0,22 on a 4 FN et 114 FP. Le seuil 0,21 conserve 3 FN et 117 FP, au coût métier 132 sur le train.
