# Comprendre le Machine Learning : probabilité, coefficients, seuil et évaluation

Ce document complète `docs/02` à `docs/06` et la page 12 de `app.py`. Il n'introduit aucune
valeur illustrative : chaque nombre est lu dans `model.joblib`, `model_meta.json`, le CSV ou
recalculé depuis les artefacts du projet.

## 1. Ce que le modèle apprend

Le pipeline sauvegardé a exactement quatre étapes :

```
FeaturesPhishing → SimpleImputer(strategy="median") → StandardScaler → LogisticRegression(class_weight="balanced", random_state=42)
```

`FeaturesPhishing` produit 8 variables numériques à partir des colonnes brutes du formulaire :
`log_age` (`log1p(domaine_age_jours)`), `urgence_score`, `nb_liens`, `expediteur_connu`,
`piece_jointe`, `personnalisation_score`, `urg_x_inconnu = urgence_score × (1 − expediteur_connu)`
et `liens_x_inconnu = nb_liens × (1 − expediteur_connu)`.

La régression logistique n'apprend que deux choses :

- un **intercept** (score de base) ;
- un **coefficient par variable transformée**.

Elle n'apprend **ni le seuil ni les zones de triage**. Le modèle reste binaire : `Non` / `Oui`.
Les trois zones `Normal / VIGILANCE / ALERTE` sont une action secondaire, jamais une classe.

## 2. Vrais coefficients du modèle déployé

Valeurs lues directement dans `model.joblib` (variables standardisées, donc comparables) :

| Variable transformée | Coefficient | Lecture |
|---|---:|---|
| Intercept | **−0,764195** | score de base |
| `log_age` | −1,695200 | un domaine ancien pousse vers `Non` |
| `urgence_score` | +0,966415 | l'urgence pousse vers `Oui` |
| `nb_liens` | +0,755597 | les liens poussent vers `Oui` |
| `expediteur_connu` | −0,328518 | un expéditeur connu pousse vers `Non` |
| `piece_jointe` | +0,184134 | effet faible vers `Oui` |
| `personnalisation_score` | +0,694086 | effet vers `Oui` |
| `urg_x_inconnu` | +0,475546 | urgence + expéditeur inconnu |
| `liens_x_inconnu` | +0,540464 | liens + expéditeur inconnu |

`classes_ = ['Non', 'Oui']` : l'indice de `Oui` est **1**. Le code déduit cet indice de
`classes_` (`list(modele.classes_).index("Oui")`) au lieu de le supposer.

## 3. Comment `P(Oui)` est calculée

Pour un message, le pipeline applique ses transformations puis :

```
z      = intercept + Σ(coef_i × variable_transformée_standardisée_i)
P(Oui) = 1 / (1 + exp(−z))        (fonction sigmoïde)
```

La fonction `details_probabilite()` de `app.py` recalcule exactement cette somme et compare son
résultat à `predict_proba()`. Vérification faite sur le premier scénario du formulaire :
`z = −7,492136`, `P(Oui) = 0,00055714`, écart avec `predict_proba()` = **0,00** (à la précision
numérique). `P(Non) = 1 − P(Oui)`.

La probabilité est une **estimation**, pas une certitude : le jeu est synthétique et aucune
calibration (Platt / isotonique) n'a été appliquée. C'est pourquoi le verdict reste soumis à
validation humaine.

## 4. Du score au verdict : le seuil

`P(Oui) ≥ 0,21` → **Malveillant**, sinon **Non malveillant**.

Le seuil a été choisi sur les **416 lignes du train**, à partir des probabilités OOF :

| Seuil | FN | FP | Coût `5·FN + FP` |
|---:|---:|---:|---:|
| 0,20 | 2 | 118 | **128** (minimum) |
| **0,21 (retenu)** | **3** | **117** | **132** |
| 0,22 | 4 | 114 | 134 |

Le plateau quasi minimal est **0,20 – 0,22** ; la médiane **0,21** est retenue. Sensibilités
calculées dans le notebook : `c_FN = 3 → 0,47`, `c_FN = 5 → 0,21`, `c_FN = 10 → 0,20`.

Le triage secondaire utilise `0,20` et `0,88` : `P(Oui) < 0,20` → Normal,
`0,20 ≤ P(Oui) < 0,88` → VIGILANCE, `P(Oui) ≥ 0,88` → ALERTE. Exemple : `P(Oui) = 28 %`
donne **Malveillant** (28 % ≥ 21 %) **et** VIGILANCE (21 % ≤ 28 % < 88 %). Le triage n'est pas
une troisième classe et ne modifie pas le verdict.

## 5. Validation croisée, OOF, évaluation finale

- **Cross-validation** : `StratifiedKFold(5, shuffle=True)` répété sur 5 graines (42–46), soit
  25 entraînements ; AUC CV moyen `0,9092 ± 0,0031`, AP CV `0,8119 ± 0,0034`.
- **OOF** : chaque ligne du train est prédite par un modèle qui ne l'a pas vue. Les 416
  probabilités moyennées donnent, au seuil 0,21 : **TN 182 / FP 117 / FN 3 / TP 114**
  (somme 416, coût 132). L'AUC sur ces probabilités OOF est `0,9112`.
- **Test (104 lignes)** : lu une seule fois, jamais utilisé pour choisir le modèle, les
  coefficients ou le seuil. Résultats : **TN 47 / FP 28 / FN 1 / TP 28**, accuracy `0,721`,
  précision `Oui` `0,500`, rappel `Oui` `0,966`, F1 macro `0,712`, ROC-AUC `0,9099`,
  AP `0,8095`, Brier `0,1234`, coût `33 = 5×1 + 28`.
- IC95 % bootstrap (2 000 tirages sur le test) : rappel `[0,886 ; 1,000]`, précision
  `[0,368 ; 0,636]`, fausse alerte `[0,262 ; 0,481]`.

**Protocoles distincts** : `0,8082` est le F1 macro OOF 5×5 du modèle retenu au seuil 0,50 ;
`0,791` est le F1 macro de la CV 5-fold simple du Random Forest (§15). Ils ne sont pas
directement comparables. Les anciennes valeurs `0,814` et `0,771` ne sont pas reproductibles
depuis les artefacts ; elles ont été remplacées par `0,8082` (OOF 5×5 au seuil 0,50) et
`0,8073 ± 0,0466` (moyenne des 25 plis), tous deux désormais imprimés par le notebook.

## 6. Page 12 de l'application et formulaire amélioré

La page 12 (module « Comprendre le Machine Learning ») affiche : les coefficients réels (A),
le calcul de `P(Oui)` étape par étape (B), le seuil et le triage (C), la courbe de coût OOF
train (D) et la matrice finale du test (E). La section F réutilise le dernier message saisi en
page 7, conservé dans `st.session_state["dernier_saisi"]`.

Le formulaire de la page 7 a été corrigé : les boutons « Charger ce scénario » écrivent
désormais à la fois `session_state["scenario"]` **et** les clés `n_*` / `c_*` des widgets.
Sans cette synchronisation, Streamlit ignorait `value=` lors des reruns et les champs
restaient figés sur leur première valeur. La classe réelle d'un message saisi n'étant pas
connue, l'application n'affiche aucun « bon/mauvais » prédictif pour cet exemple.
