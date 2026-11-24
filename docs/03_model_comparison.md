# 03 — Comparaison des modèles et choix final

> **Source de vérité.** Sorties réelles des cellules 60 et 79 du notebook `notebook_ML_IA_confiance_numerique.ipynb`, complétées par `model.joblib` et `model_meta.json`. Données synthétiques et pédagogiques : aucune validation sur de vraies campagnes. Les chiffres historiques annoncés dans les markdown du notebook sont signalés en section 6 lorsqu'ils divergent des sorties réelles ; ils ne sont **pas corrigés** dans le notebook.

---

## 1. Méthodologie de comparaison

### Protocole historique (cellule 60)

1. Jeu de 520 lignes uniques, après suppression de 4 doublons exacts.
2. Split `train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)` : 416 lignes d'entraînement, 104 lignes de test.
3. Trois modèles entraînés sur les mêmes 416 lignes et évalués sur les mêmes 104 lignes : `Random_Forest`, `Regression_logistique`, `SVM_RBF`.
4. Métriques rapportées : accuracy, precision macro, recall macro, F1 macro, ROC-AUC et Average Precision (AP). Les F1 du tableau historique correspondent au seuil implicite de 0,50.

Comparer sur **le même split** est indispensable : toute différence de résultat est alors attribuable au modèle, et non à une partition différente.

### Protocole de validation croisée (cellule 79)

Validation croisée à **5 folds simples** sur le jeu d'entraînement : F1 macro moyen avec écart-type, et accuracy moyenne. La CV donne une estimation plus stable que l'évaluation sur un seul split, car chaque observation sert tour à tour à l'apprentissage et à la validation. Les étapes apprenantes (imputation, standardisation) doivent être réajustées dans chaque fold — c'est précisément ce que garantit l'usage d'un `Pipeline`.

---

## 2. Résultats historiques sur le jeu de test (104 lignes)

| Modèle | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) | ROC-AUC | AP |
|---|---:|---:|---:|---:|---:|---:|
| `Random_Forest` | 0,798 | 0,752 | 0,723 | **0,734** | **0,866** | **0,698** |
| `Regression_logistique` | 0,721 | 0,692 | 0,733 | 0,694 | 0,832 | 0,656 |
| `SVM_RBF` | 0,721 | 0,692 | 0,733 | 0,694 | 0,834 | 0,633 |

Lectures :

- Le **Random Forest** domine sur cinq métriques sur six dans ce tableau : accuracy 0,798, précision macro 0,752 et F1 macro 0,734, mais aussi classement (AUC 0,866, AP 0,698).
- La **régression logistique historique** et le **SVM RBF** affichent des résultats identiques en accuracy, précision, recall et F1 macro (0,721 / 0,692 / 0,733 / 0,694). Leurs scores de classement diffèrent légèrement : AUC 0,832 contre 0,834, AP 0,656 contre 0,633.
- Le recall macro (0,733) est supérieur à la précision macro (0,692) pour les deux modèles linéaires : ils ratent moins de messages malveillants mais déclenchent plus de fausses alertes. Le Random Forest présente le profil inverse (précision 0,752 > recall 0,723).

**Toutes les cases du tableau sont renseignées** dans les sorties de la cellule 60. Aucune valeur n'est manquante ici.

---

## 3. Résultats de validation croisée (5 folds, cellule 79)

| Modèle | F1 macro (moyenne ± écart-type) | Accuracy (moyenne) |
|---|---|---:|
| `Random_Forest` | **0,791 ± 0,051** | **0,839** |
| `Regression_logistique` | 0,785 ± 0,067 | 0,810 |
| `SVM_RBF` | 0,784 ± 0,018 | 0,815 |

Lectures :

- Les trois F1 macro moyens sont très proches (0,791 / 0,785 / 0,784). Aucun écart n'est décisif à lui seul.
- La dispersion du SVM (écart-type 0,018) est la plus faible : ses performances sont les plus stables d'un fold à l'autre. Celle de la régression logistique est la plus forte (0,067).
- L'accuracy CV du Random Forest (0,839) est la plus élevée, en cohérence avec son accuracy sur le test (0,798).

**Précision de vocabulaire** : l'écart-type rapporté ici est celui des folds tel qu'affiché par le notebook. La nature exacte de cette dispersion (écart-type des scores par fold ou erreur standard) n'est **pas disponible dans les artefacts** ; elle est donc reportée telle quelle, sans réinterprétation.

---

## 4. Modèle retenu : régression logistique améliorée

Le modèle final n'est pas la régression logistique « brute » du tableau historique, mais une **régression logistique avec feature engineering** (`FeaturesPhishing`), décrite dans `02_preprocessing_and_pipeline.md`.

| Métrique du modèle retenu | Valeur |
|---|---:|
| ROC-AUC (test) | **0,910** |
| Average Precision / AP (test) | **0,810** |
| Brier score (test) | **0,123** |
| F1 macro (test, au seuil 0,21) | **0,712** |

### Justification du choix

1. **Meilleur classement indépendant du seuil.** L'AUC (0,910) et l'AP (0,810) du modèle retenu sont supérieures à celles du Random Forest historique (0,866 / 0,698). Contrairement au F1, ces métriques évaluent la qualité de l'ordre des scores sans fixer de seuil de décision : elles mesurent la capacité du modèle à placer les messages malveillants devant les légitimes.
2. **Qualité des probabilités.** Le Brier de 0,123 renseigne sur la calibration ; une probabilité bien calibrée est utile pour prioriser une file d'analyse et pour fixer un seuil selon le coût métier.
3. **Coût métier maîtrisé.** Le seuil 0,21 (inférieur à 0,50) traduit le choix de privilégier le rappel sur la classe `Oui` : on accepte quelques fausses alertes pour limiter les menaces manquées, privilège accordé ici à l'interprétabilité et au classement plutôt qu'au F1 brut.
4. **Interprétabilité.** En sécurité, un analyste doit pouvoir comprendre *pourquoi* un message est flaglé. La régression logistique fournit des coefficients signés, directement lisibles en termes de contribution au score de risque — ce qu'un ensemble de centaines d'arbres ne fournit pas aussi simplement. Les coefficients se lisent comme des contributions au score de risque, en lien avec les signaux identifiés dans le document `01` (âge du domaine, urgence, expéditeur connu, nombre de liens). **Les valeurs numériques exactes des coefficients ne sont pas disponibles dans les artefacts** : aucun signe ni aucune grandeur individuelle n'est donc affirmé ici.

### Réserve importante sur le F1

Le **Random Forest affiche le F1 macro brut le plus élevé du tableau historique (0,734 au seuil 0,50)**, contre 0,712 pour le modèle retenu au seuil 0,21. Deux précisions s'imposent :

- les deux F1 ne sont **pas mesurés dans les mêmes conditions** (seuil 0,50 pour le tableau historique, seuil 0,21 pour le modèle final, avec en plus un feature engineering différent) : leur comparaison directe n'est pas pertinente ;
- choisir un modèle **parce qu'il a le meilleur F1 sur le jeu de test** reviendrait à utiliser le test comme critère de sélection : le test devient alors à la fois juge et partie, et la performance rapportée est **biaisée à l'optimisme**. Le choix doit être fait sur la validation croisée ou sur des prédictions OOF, puis confirmé une seule fois sur le test.

Autrement dit : **un F1 élevé à un seuil donné ne fait pas le meilleur modèle global**. Le F1 dépend du seuil, de la prévalence et de l'équilibre souhaité entre précision et rappel ; l'AUC et l'AP décrivent le classement sur tous les seuils.

---

## 5. Avantages et limites de chaque algorithme

| Algorithme | Avantages | Limites dans ce projet |
|---|---|---|
| **Random Forest** | Capture les non-linéarités et les interactions sans feature engineering explicite ; tolérant au bruit ; résultats historiques solides (accuracy 0,798 ; F1 macro 0,734 ; AUC 0,866 ; AP 0,698 ; F1 CV 0,791 ± 0,051). | Interprétabilité faible pour un analyste sécurité ; modèle plus lourd ; Brier **non disponible dans les artefacts** pour cette version ; son F1 historique au seuil 0,50 ne peut pas justifier à lui seul un choix final sans biais de sélection sur le test. |
| **Régression logistique** | Simple, rapide, coefficients interprétables, probabilités exploitables ; base du modèle retenu après feature engineering (AUC 0,910 ; AP 0,810 ; Brier 0,123). | La forme log-linéaire suppose une relation linéaire entre les log-odds et les caractéristiques : d'où la nécessité du `log1p` et des produits d'interaction ; la version historique brute (AUC 0,832 ; AP 0,656) est moins performante que la version améliorée. |
| **SVM RBF** | Frontière de décision non linéaire flexible ; F1 CV 0,784 ± 0,018, dispersion la plus faible des trois ; AUC 0,834. | Moins interprétable ; pas de probabilités natives directement calibrées dans ce protocole (Brier **non disponible dans les artefacts**) ; AP 0,633, la plus faible du tableau ; accuracy et F1 historiques égaux à ceux de la régression logistique brute, sans gain net. |

---

## 6. Incohérences documentées (ne pas corriger le notebook)

### 6.1 Écart entre markdown de la cellule 64 et sorties réelles

Le markdown de la **cellule 64** annonce pour le Random Forest :

| Quantité | Annoncé (cellule 64) | Sortie réelle | Écart |
|---|---:|---:|---|
| Accuracy (test) | 0,788 | 0,798 (cellule 60) | +0,010 |
| F1 macro (test) | 0,747 | 0,734 (cellule 60) | −0,013 |
| F1 macro CV | 0,771 ± 0,048 | 0,791 ± 0,051 (cellule 79) | +0,020 sur la moyenne |

**Les sorties réelles des cellules 60 et 79 font foi.** Le texte de la cellule 64 doit être lu comme une valeur annoncée non concordante. Consigne : **ne pas modifier le notebook**, uniquement signaler l'écart.

### 6.2 Valeurs historiques déclarées dans `model_meta.json`

`model_meta.json` contient en outre :

| Entrée | Valeur | Statut |
|---|---:|---|
| `Dummy` | 0,419 | **Valeur historique déclarée, non reproductible depuis les cellules actuelles** |
| `KNN` | 0,6314 | **Valeur historique déclarée, non reproductible depuis les cellules actuelles** |

Les cellules 57–60 du notebook ne comparent que **trois** modèles (`Random_Forest`, `Regression_logistique`, `SVM_RBF`) : ni `Dummy` ni `KNN` n'y sont réentraînés ni réévalués. La métrique exacte associée à ces deux nombres n'est **pas disponible dans les artefacts** ; ils ne doivent donc pas être insérés dans le tableau comparatif de la section 2 ni présentés comme des résultats du protocole actuel.

---

## 7. Synthèse

Sur le split historique, le Random Forest est en tête sur la plupart des métriques (accuracy 0,798 ; F1 macro 0,734 ; AUC 0,866 ; AP 0,698) et sur la CV (F1 macro 0,791 ± 0,051). Le modèle final retenu est néanmoins la **régression logistique améliorée**, parce qu'elle offre le meilleur classement hors seuil (AUC 0,910 ; AP 0,810), des probabilités calibrées (Brier 0,123) et l'interprétabilité requise en sécurité, avec un F1 macro de 0,712 au seuil 0,21. Le F1 brut du Random Forest ne justifie pas un choix final s'il est lu sur le test lui-même. Deux séries de valeurs historiques (cellule 64, `model_meta.json`) sont signalées comme non concordantes ou non reproductibles, sans correction du notebook.
