# 04 — Glossaire raisonné des métriques

> **Source de vérité.** Résultats du notebook `notebook_ML_IA_confiance_numerique.ipynb` et de `model_meta.json`. Les exemples numériques marqués « illustratif » sont **fictifs** et servent uniquement à rendre les formules tangibles : ils ne proviennent **pas** des artefacts et ne sont pas des résultats du projet. Données synthétiques et pédagogiques, sans validation sur de vraies campagnes.

---

## 0. Convention et notations

Dans tout ce document, la **classe positive** est `Oui` = message malveillant, et la classe négative est `Non` = message légitime.

| Symbole | Signification | Exemple concret |
|---|---|---|
| **TP** | *True Positive* — vrai positif | Un phishing est correctement détecté et bloqué |
| **TN** | *True Negative* — vrai négatif | Un message légitime est correctement laissé passer |
| **FP** | *False Positive* — faux positif (fausse alerte) | Un message du collègue est classé malveillant : l'analyste perd du temps |
| **FN** | *False Negative* — faux négatif (menace manquée) | Un phishing est classé légitime et atteint la boîte mail |

On note `N = TP + TN + FP + FN` l'effectif total, `p_i` la probabilité prédite pour l'observation `i`, et `y_i` sa vraie étiquette (1 pour `Oui`, 0 pour `Non`).

**Exemple illustratif fictif (non issu des artefacts)** : sur 100 messages dont 20 malveillants, le modèle en signale 18, dont 15 à juste titre. Alors `TP = 15`, `FP = 3`, `FN = 5`, `TN = 77`. Ces nombres servent uniquement aux calculs ci-dessous.

---

## 1. Matrice de confusion

### Définition

Tableau 2 × 2 qui croise la **classe réelle** et la **classe prédite**. C'est la brique de base : accuracy, précision, rappel, F1 et les métriques par classe en sont dérivées.

### Formule / structure

|  | Prédit `Oui` | Prédit `Non` |
|---|---:|---:|
| **Réel `Oui`** | TP | FN |
| **Réel `Non`** | FP | TN |

Avec l'exemple illustratif :

|  | Prédit `Oui` | Prédit `Non` |
|---|---:|---:|
| **Réel `Oui`** | 15 | 5 |
| **Réel `Non`** | 3 | 77 |

### Interprétation faible / élevé

Il n'existe pas de « bonne » matrice abstraite : ce qui compte, c'est la répartition des erreurs. Beaucoup de **FN** = beaucoup de menaces manquées (risque élevé). Beaucoup de **FP** = beaucoup de fausses alertes (fatigue de l'analyste). La matrice permet de voir *le type* d'erreur, que l'accuracy masque.

### Limites

Effectifs bruts : elle ne se compare pas directement entre jeux de tailles différentes, ni entre seuils différents sans normalisation. Les valeurs de la matrice de confusion du modèle retenu au seuil 0,21 ne sont **pas disponibles dans les artefacts**.

### Utilité dans le projet

Elle est indispensable pour le débrief métier : elle répond à « combien de phishings avons-nous laissé passer ? » et « combien de messages légitimes avons-nous inquiété à tort ? ». Le coût métier étant asymétrique, la case **FN** est la plus surveillée.

---

## 2. Accuracy (exactitude)

### Définition

Proportion de prédictions correctes, toutes classes confondues.

### Formule

\[
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN} = \frac{TP + TN}{N}
\]

Exemple illustratif : `(15 + 77) / 100 = 92 / 100 = 0,92`.

### Interprétation faible / élevé

Élevée = beaucoup de bonnes prédictions globalement. Faible = beaucoup d'erreurs globalement. **Mais** l'accuracy est fortement influencée par la classe majoritaire.

### Limites

Ici, 71,9 % des messages sont `Non`. Un modèle qui prédit **toujours `Non`** obtiendrait une accuracy de **71,9 %** sans détecter le moindre phishing. L'accuracy seule ne peut donc pas valider un détecteur. Elle est en outre dépendante du seuil de décision.

### Utilité dans le projet

Métrique de contexte, jamais critère unique. Elle est rapportée dans les comparaisons historiques (0,798 pour `Random_Forest`, 0,721 pour `Regression_logistique` et `SVM_RBF`) et en validation croisée (0,839 / 0,810 / 0,815), mais elle est systématiquement accompagnée du F1, de l'AUC et de l'AP.

---

## 3. Precision (précision)

### Définition

Parmi les messages **signalés comme malveillants**, quelle proportion l'est vraiment ? C'est une mesure de la fiabilité d'une alerte.

### Formule

\[
\text{Precision} = \frac{TP}{TP + FP}
\]

Exemple illustratif : `15 / (15 + 3) = 15 / 18 ≈ 0,833`. *(La précision du modèle retenu à son seuil de 0,21 n'est pas disponible dans les artefacts.)*

### Interprétation faible / élevé

Élevée = peu de fausses alertes ; quand le modèle sonne l'alarme, on peut y croire. Faible = beaucoup de bruit, l'analyste perd du temps à vérifier des messages légitimes.

### Limites

Elle ignore les FN : un modèle extrêmement sélectif peut afficher une précision parfaite en ne signalant qu'un seul cas certain et en manquant tous les autres. Elle s'effondre si la prévalence de phishing augmente en production. Une précision calculée à un seuil donné ne dit rien du comportement aux autres seuils.

### Utilité dans le projet

Mesure directe de la charge de travail de l'analyste. Les valeurs historiques sont des **précisions macro** : 0,752 (`Random_Forest`), 0,692 (`Regression_logistique` et `SVM_RBF`).

---

## 4. Recall (rappel / sensibilité / TPR)

### Définition

Parmi les messages **réellement malveillants**, quelle proportion le modèle a-t-il détectée ?

### Formule

\[
\text{Recall} = \frac{TP}{TP + FN}
\]

Exemple illustratif : `15 / (15 + 5) = 15 / 20 = 0,75`.

### Interprétation faible / élevé

Élevé = peu de menaces manquées. Faible = beaucoup de phishings arrivent à destination. C'est la métrique la plus alignée sur le risque métier en sécurité.

### Limites

Elle ignore les FP : un modèle qui classe **tout** comme malveillant a un rappel de 1,00 et une précision égale à la prévalence (28,1 % ici). Le rappel et la précision doivent donc toujours être lus ensemble.

### Utilité dans le projet

Le seuil 0,21 du modèle retenu a précisément pour effet de favoriser le rappel sur la classe `Oui` par rapport au seuil implicite de 0,50 des comparaisons historiques. Les rappels macro historiques sont de 0,723 (`Random_Forest`) et 0,733 (`Regression_logistique`, `SVM_RBF`).

---

## 5. F1 et F1 macro

### Définition

Le **F1** est la moyenne harmonique de la précision et du rappel pour une classe donnée. Il pénalise les déséquilibres entre les deux (contrairement à une moyenne arithmétique). Le **F1 macro** fait la moyenne **non pondérée** des F1 de chaque classe : chaque classe compte autant, quelle que soit sa fréquence.

### Formule

\[
F1 = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
    = \frac{2TP}{2TP + FP + FN}
\]

\[
F1_{\text{macro}} = \frac{1}{K}\sum_{k=1}^{K} F1_k \qquad (K = 2 \text{ ici : } Non \text{ et } Oui)
\]

Exemple illustratif pour la classe `Oui` : `F1 = 2 × 0,833 × 0,75 / (0,833 + 0,75) ≈ 0,789`. Le F1 macro moyennerait ce résultat avec le F1 calculé pour la classe `Non`.

### Interprétation faible / élevé

Élevé = bon compromis précision/rappel. Faible = l'un des deux aspects (ou les deux) est dégradé. En biclasse déséquilibrée, le F1 macro est plus informatif que l'accuracy car la classe `Oui` pèse autant que `Non`.

### Limites

Le F1 est **une valeur à un seuil donné** : le modifier change complètement le résultat. Il dépend aussi de la prévalence. Deux modèles avec le même F1 peuvent avoir des profils d'erreurs très différents (beaucoup de FP pour l'un, beaucoup de FN pour l'autre). Enfin, il ne dit rien de la qualité du classement ni de la calibration.

### Utilité dans le projet

C'est la métrique principale des comparaisons historiques et de la validation croisée : F1 macro test de 0,734 / 0,694 / 0,694 ; F1 macro CV de 0,791 ± 0,051 / 0,785 ± 0,067 / 0,784 ± 0,018. Le modèle retenu affiche un **F1 macro de 0,712 au seuil 0,21**. Attention : ce F1 n'est pas directement comparable aux 0,734 historiques mesurés à un autre seuil et avec un autre jeu de caractéristiques.

---

## 6. ROC-AUC (aire sous la courbe ROC)

### Définition

L'aire sous la courbe du **Taux de Vrais Positifs (TPR = rappel)** en fonction du **Taux de Faux Positifs (FPR = FP / (FP + TN))**, tracée pour tous les seuils possibles. Interprétation équivalente : la probabilité qu'un message malveillant reçoive un score plus élevé qu'un message légitime, tirés au hasard.

### Formule

\[
\text{ROC-AUC} = \int_0^1 \text{TPR}(t)\, d\,\text{FPR}(t)
               = P(s_{\text{Oui}} > s_{\text{Non}}) + \tfrac{1}{2}P(s_{\text{Oui}} = s_{\text{Non}})
\]

Exemple illustratif : classer 15 vrais malveillants devant 77 vrais légitimes donne une AUC maximale dans cet exemple simplifié ; en pratique, les scores se chevauchent et l'AUC est comprise entre 0 et 1. Le calcul détaillé des scores n'est **pas disponible dans les artefacts**.

### Interprétation : repères indicatifs

| ROC-AUC | Lecture indicative |
|---|---|
| 0,50 | Hasard (équivalent à un classement aléatoire) |
| 0,60 – 0,70 | Faible |
| 0,70 – 0,80 | Acceptable |
| 0,80 – 0,90 | Bon |
| 0,90 – 1,00 | Excellent |

> **Ces paliers sont des repères indicatifs**, pas des seuils de décision normatifs. Leur pertinence dépend du domaine, du coût des erreurs et de la prévalence.

### Limites

L'AUC est **insensible à la prévalence** (elle utilise TPR et FPR, pas la précision) : elle peut paraître élevée alors que la précision en production est médiocre si les phishings deviennent rares. Elle évalue le **classement**, pas la calibration des probabilités, et ne fournit aucun seuil opérationnel. Une AUC élevée ne garantit pas un bon F1 au seuil choisi.

### Utilité dans le projet

C'est le critère principal de sélection du modèle final : le modèle retenu atteint **0,910**, contre 0,866 pour le Random Forest historique, 0,834 pour le SVM et 0,832 pour la régression logistique brute. Son caractère indépendant du seuil en fait un bon critère de comparaison entre modèles.

---

## 7. Average Precision (AP)

### Définition

L'AP résume la **courbe Précision–Rappel** : c'est une somme pondérée des précisions obtenues aux successifs niveaux de rappel. Elle mesure la qualité du classement des positifs, en accordant de l'importance au fait qu'ils apparaissent en tête de liste. Elle est aussi appelée *area under the precision–recall curve*.

### Formule

\[
AP = \sum_{k} (R_k - R_{k-1}) \, P_k
\]

où `P_k` et `R_k` sont la précision et le rappel au rang `k` de la liste triée par score décroissant.

Exemple illustratif : si les 15 vrais malveillants sont tous classés avant les 85 autres messages, la précision reste élevée sur presque toute la course du rappel et l'AP est proche de 1 ; si les vrais malveillants sont éparpillés, l'AP chute. Le détail des scores n'est **pas disponible dans les artefacts**.

### Interprétation faible / élevé

Élevée = les malveillants sont bien concentrés en tête de la file de scores. Faible = l'analyste doit parcourir beaucoup de messages légitimes avant de tomber sur les vrais.

### Limites

L'AP est **sensible à la prévalence** (contrairement à l'AUC) : une même qualité de classement donnera une AP plus basse si les positifs sont plus rares. Elle ne fournit pas non plus de seuil de décision.

### **AP ≠ Recall**

Le **rappel** est une valeur **à un seul seuil** : proportion de malveillants effectivement détectés. L'**AP** résume **tous les seuils** à la fois, en combinant précision et rappel le long du classement. Un rappel de 0,733 et une AP de 0,698 décrivent deux choses différentes et ne sont pas comparables.

### **ROC-AUC ≠ AP**

L'AUC utilise le couple **TPR / FPR** et est insensible à la prévalence ; l'AP utilise le couple **Précision / Rappel** et y est sensible. Dans ce projet, le modèle retenu affiche AUC 0,910 et AP 0,810 : ces deux nombres ne doivent ni être confondus ni être comparés directement entre eux.

### Utilité dans le projet

Avec 28,1 % de positifs, l'AP complète utilement l'AUC pour juger le modèle retenu (**0,810**, contre 0,698 pour le Random Forest historique, 0,656 pour la régression logistique brute et 0,633 pour le SVM). Elle est particulièrement pertinente pour une file de tri priorisée par score.

---

## 8. Brier score

### Définition

Erreur quadratique moyenne entre la **probabilité prédite** et l'étiquette réelle (0 ou 1). Il mesure la **calibration** : les probabilités annoncées correspondent-elles à la fréquence observée ?

### Formule

\[
\text{Brier} = \frac{1}{N}\sum_{i=1}^{N} (p_i - y_i)^2
\]

Exemple illustratif : pour un message légitime (`y = 0`) auquel on attribue `p = 0,2`, la contribution est `(0,2 − 0)² = 0,04` ; pour un phishing (`y = 1`) auquel on attribue `p = 0,9`, elle est `(0,9 − 1)² = 0,01`.

### Interprétation faible / élevé

**Plus bas, c'est mieux** (0 = probabilités parfaites). Élevé = probabilités mal calibrées : le modèle est trop sûr de lui quand il se trompe, ou trop timide quand il a raison.

### Limites

Le Brier dépend de la prévalence (une référence « toujours la prévalence » donne une valeur non nulle). Il ne dit rien du classement : un modèle peut avoir un bon Brier et une AUC médiocre, ou l'inverse. Il n'est pas directement interprétable en nombre d'erreurs métier. Le Brier des modèles historiques n'est **pas disponible dans les artefacts** ; seule la valeur du modèle retenu l'est.

### Utilité dans le projet

Le modèle retenu affiche un **Brier de 0,123**. Cela conforte l'usage de ses probabilités pour fixer un seuil adapté au coût métier et pour prioriser l'analyse, au-delà du seul classement binaire.

---

## 9. OOF — *Out-of-Fold*

### Définition

Les prédictions **OOF** sont obtenues en entraînant le modèle sur `K − 1` folds et en prédisant le fold laissé de côté, puis en répétant l'opération pour chacun des `K` folds. Chaque observation reçoit ainsi une prédiction produite par un modèle **qui ne l'a jamais vue**.

### Formule / principe

Pour un split en `K` plis :

\[
\hat{y}_i^{OOF} = \text{prédiction de } \mathcal{M}_{-k(i)} \text{ sur } x_i
\]

où `k(i)` est le fold contenant l'observation `i` et `\mathcal{M}_{-k(i)}` le modèle entraîné sur tous les autres plis. On calcule ensuite une métrique (F1, AUC, Brier,…) sur l'ensemble de ces prédictions.

Exemple illustratif : avec 5 folds sur les 416 lignes d'entraînement, chaque ligne est prédite exactement une fois par un modèle entraîné sur les 4 autres cinquièmes. Les 104 lignes de test ne sont **pas** utilisées pour produire ces prédictions.

### Interprétation faible / élevé

Ce n'est **pas une valeur** : il n'y a pas d'OOF « faible » ou « élevé ». Ce qui est faible ou élevé, c'est la **métrique calculée sur les prédictions OOF**. L'OOF est une **méthode d'estimation**, plus stable que l'évaluation sur un unique split, car elle utilise toutes les lignes d'entraînement pour l'évaluation sans les voir à l'apprentissage.

### Limites

Elle ne remplace pas un jeu de test final intact : elle estime la performance pendant le développement, sur le train. Si le même OOF sert à choisir le modèle **et** le seuil, une part d'optimisme subsiste (sélection multiple). Les étapes apprenantes doivent être réajustées dans chaque fold, sinon l'OOF fuit. Le détail des prédictions OOF du modèle retenu n'est **pas disponible dans les artefacts** ; seules les métriques de la CV à 5 folds sont rapportées.

### Utilité dans le projet

La validation croisée à 5 folds (§15) est précisément une estimation de type OOF au sens où chaque observation est évaluée hors de son fold d'apprentissage : F1 macro 0,791 ± 0,051 pour le Random Forest, 0,785 ± 0,067 pour la régression logistique, 0,784 ± 0,018 pour le SVM. C'est sur ce type d'estimation que le choix devrait être fondé, avant évaluation finale sur les 104 lignes de test.

---

## 10. Tableau synthèse

| Terme | Nature | Utilité dans le projet |
|---|---|---|
| **Accuracy** | Métrique | Contexte global ; trompeuse avec 71,9 % de `Non` (seuil constant = 71,9 %) |
| **Precision** | Métrique | Fiabilité d'une alerte ; charge de travail de l'analyste |
| **Recall** | Métrique | Couverture des phishings ; menaces manquées |
| **F1** | Métrique | Compromis précision / rappel pour une classe à un seuil donné |
| **ROC-AUC** | Métrique | Qualité du classement indépendamment du seuil ; critère principal de sélection (0,910) |
| **AP** | Métrique | Qualité du classement des positifs, sensible à la prévalence (0,810) |
| **Brier** | Métrique | Calibration des probabilités (0,123) |
| **OOF** | **Méthode — PAS une métrique** | Estimer la performance en développement sans toucher au test final ; supporter la CV 5 folds |

Matrice de confusion et courbes (ROC, précision–rappel) sont des **outils de visualisation / de diagnostic**, pas des métriques scalaires à part entière.

---

## 11. Trois confusions à ne pas commettre

1. **OOF n'est PAS une métrique.** C'est une manière de produire des prédictions hors échantillon d'apprentissage, sur lesquelles on calcule ensuite une métrique.
2. **AP ≠ Recall.** Le rappel est calculé à un seuil ; l'AP résume tous les seuils de la courbe précision–rappel.
3. **ROC-AUC ≠ AP.** La première utilise TPR/FPR et ignore la prévalence ; la seconde utilise précision/rappel et en dépend. Les valeurs 0,910 et 0,810 du modèle retenu décrivent deux propriétés distinctes.

---

## 12. Valeurs de référence du projet (récapitulatif)

| Modèle / jeu | Accuracy | Precision macro | Recall macro | F1 macro | ROC-AUC | AP |
|---|---:|---:|---:|---:|---:|---:|
| `Random_Forest` (test 104) | 0,798 | 0,752 | 0,723 | 0,734 | 0,866 | 0,698 |
| `Regression_logistique` (test 104) | 0,721 | 0,692 | 0,733 | 0,694 | 0,832 | 0,656 |
| `SVM_RBF` (test 104) | 0,721 | 0,692 | 0,733 | 0,694 | 0,834 | 0,633 |
| **Modèle retenu** (test) | 0,721 | 0,740 | 0,796 | 0,712 (seuil 0,21) | **0,910** | **0,810** |

Autres valeurs du modèle retenu : Brier **0,123**. CV 5 folds : **0,791 ± 0,051** (RF), **0,785 ± 0,067** (LR), **0,784 ± 0,018** (SVM) en F1 macro ; accuracy CV **0,839 / 0,810 / 0,815**. Les entrées historiques `Dummy` et `KNN` ont été **retirées de `model_meta.json`** : aucune cellule du notebook ne les produit.
