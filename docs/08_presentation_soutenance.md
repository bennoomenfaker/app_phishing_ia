# Soutenance — Présentation pédagogique en 18 parties

Support de présentation pour un public Master VIC. Les chiffres sont ceux du notebook, de `model.joblib`, de `model_meta.json` et du CSV synthétique. Quando une information n'est pas disponible, elle est signalée explicitement.

## 1. Contexte et problématique

L'IA générative produit des e-mails de phishing sans fautes de langue, avec un ton personnalisé. Les signes classiques — fautes, style maladroit — deviennent donc moins fiables. Un responsable sécurité doit pourtant décider rapidement quels messages méritent une analyse approfondie.

**Problématique :** comment détecter un message malveillant quand les signes classiques s'estompent, tout en gardant une alerte explicable et une charge analyste maîtrisée ?

## 2. Objectif

Construire un **pré-dépistage** : un modèle qui classe un message en `Non malveillant` ou `Malveillant`, fournit une probabilité `P(Oui)` et propose une priorité de vérification. Ce n'est **pas** un filtre automatique : la décision finale appartient à l'analyste.

Deux contraintes guident le travail : détecter les attaques (rappel) et limiter le temps passé sur de fausses alertes (précision).

## 3. Dataset

Le fichier synthétique contient **524 lignes brutes**. Après nettoyage, il reste **520 messages** — aucune donnée personnelle, aucun vrai e-mail.

La cible `message_malveillant` est binaire : `Non` et `Oui`. Les classes sont déséquilibrées, ce qui rend l'accuracy seule trompeuse : prédire toujours `Non` donnerait déjà environ 72 % de bonnes réponses sans détecter la moindre attaque.

## 4. Nettoyage

Les lignes dupliquées sont supprimées (524 → 520). Les valeurs manquantes de `domaine_age_jours` sont traitées par **imputation médiane**, intégrée au Pipeline pour être apprise sur le train uniquement. La variable calendaire `date` est exclue du modèle. La cible est séparée de `X` : elle n'est jamais une variable explicative.

## 5. EDA

L'analyse exploratoire compare les distributions des variables numériques selon la classe. L'âge du domaine et le score d'urgence se révèlent être des signaux distinctifs, tandis que les fautes de langue et la personnalisation séparent moins les deux classes. Les histogrammes montrent un chevauchement partiel : **aucune variable seule ne suffit**, d'où l'intérêt d'une combinaison par un modèle.

## 6. Corrélations

La matrice de corrélation de Pearson est calculée dans le notebook (§9) sur le **train seul (416 messages)**, avec le même split stratifié que le reste du projet. Le test (104 messages) n'est ni affiché ni utilisé : la règle « train uniquement » est respectée, et le tableau de corrélations comme la heatmap portent sur les mêmes lignes. L'image affichée par l'application est extraite de cette sortie (`artefacts/matrice_correlation_eda.png`).

À retenir à l'oral : **corrélation n'est pas causalité** ; une corrélation faible n'interdit pas qu'une variable soit utile en combinaison.

## 7. Split

Séparation stratifiée 80/20, `random_state = 42` :

| Ensemble | Taille | `Non` | `Oui` |
|---|---:|---:|---:|
| Train | 416 | 299 | 117 |
| Test | 104 | 75 | 29 |

La stratification conserve la proportion des classes. Le test est mis de côté et ne sera consulté qu'une seule fois, à la fin.

## 8. Pipeline

Le modèle déployé est une chaîne anti-fuite :

**FeaturesPhishing → SimpleImputer(median) → StandardScaler → LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42)**

`FeaturesPhishing` construit `log_age = log1p(domaine_age_jours)`, `urg_x_inconnu` et `liens_x_inconnu`, et conserve `urgence_score`, `nb_liens`, `expediteur_connu`, `piece_jointe`, `personnalisation_score`. Comme l'imputation et la standardisation sont dans le Pipeline, elles sont ajustées sur chaque fold d'entraînement, jamais sur la validation.

## 9. Comparaison des modèles

Le notebook compare **3 modèles de référence** (`Random_Forest`, `Regression_logistique`, `SVM_RBF`) puis la régression logistique améliorée. Les sorties réelles donnent, pour le Random Forest, une accuracy de **0,798**, un F1 macro de **0,734** et un F1 macro en CV de **0,791 ± 0,051**. L'ancien markdown annonçait 0,788 / 0,747 / 0,771 ± 0,048 : il a été **corrigé** et cite désormais les sorties réelles.

Le choix final n'a pas été fait en regardant le test, mais à partir de la validation croisée sur le train.

## 10. Validation croisée et OOF

Pour `seed = 42, 43, 44, 45, 46` : `StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)` puis `cross_val_predict(..., method="predict_proba")` sur le **train uniquement**. Soit **5 plis × 5 répétitions = 25 entraînements**.

La moyenne des cinq vecteurs de probabilités donne une probabilité **OOF** par observation. L'OOF est une **méthode de production de prédictions**, pas une métrique.

- AUC CV moyen : **0,9092 ± 0,0031**
- AP CV moyen : **0,8119 ± 0,0034**
- AUC sur probabilités OOF moyennées : **0,9112**
- AP sur probabilités OOF moyennées : **0,8154**

## 11. Métriques

Les métriques finales sur le test, au seuil 0,21 :

| Métrique | Valeur | Question posée |
|---|---:|---|
| Accuracy | 72,1 % | Les décisions sont-elles justes en moyenne ? |
| Rappel `Oui` | 96,6 % | Les attaques sont-elles retrouvées ? |
| Précision `Oui` | 50,0 % | Les alertes sont-elles justes ? |
| F1 macro | 0,7115 | Équilibre global, classes pondérées également |
| ROC-AUC | 0,9099 | Le modèle classe-t-il bien `Oui` au-dessus de `Non` ? |
| AP | 0,8095 | Qualité du compromis précision/rappel sur `Oui` |
| Brier | 0,1234 | Les probabilités sont-elles bien calibrées ? |

Une AUC élevée ne garantit pas un faible nombre d'erreurs au seuil choisi : le seuil fixe le compromis.

## 12. Choix du modèle

Le modèle retenu et exporté dans `model.joblib` est la **régression logistique améliorée** du pipeline ci-dessus. Elle est privilégiée pour sa stabilité en validation croisée et son interprétabilité. Le seuil et le triage ont été appris sur le train, le test n'ayant servi ni à l'un ni à l'autre.

## 13. Optimisation du seuil

On balaie `np.round(np.arange(0.02, 0.99, 0.01), 2)` sur les probabilités OOF du train et on minimise :

**coût = 5 × FN + FP**

Le faux négatif est considéré cinq fois plus coûteux qu'une fausse alerte. Le plateau minimal est **0,20 – 0,22** ; le seuil retenu en est la médiane : **0,21**. Au seuil 0,21, le coût OOF est **132** et non 128 : 128 correspond au seuil 0,20.

Sensibilité : avec `c_FN = 3`, le seuil optimal est 0,47 ; avec `c_FN = 5`, 0,21 ; avec `c_FN = 10`, 0,20. Le rapport 5:1 doit être validé par un responsable sécurité.

## 14. Matrice de confusion

Train, probabilités OOF, seuil 0,21 (416 lignes) :

|  | Prédit Non | Prédit Oui |
|---|---:|---:|
| Réel Non | TN 182 | FP 117 |
| Réel Oui | FN 3 | TP 114 |

Test, seuil 0,21 (104 lignes) :

|  | Prédit Non | Prédit Oui |
|---|---:|---:|
| Réel Non | TN 47 | FP 28 |
| Réel Oui | FN 1 | TP 28 |

À l'échelle du train comme du test, le modèle sacrifie quelques fausses alertes pour éviter les attaques manquées.

## 15. Évaluation finale

Le test est lu **une seule fois**, après tous les choix. Résultats : accuracy **72,1 %**, rappel `Oui` **96,6 %**, précision `Oui` **50,0 %**, F1 macro **0,7115**, ROC-AUC **0,9099**, AP **0,8095**, Brier **0,1234**, coût métier **33**.

Les IC95 % bootstrap (2 000 tirages) sont : rappel [0,886 ; 1,000], précision [0,368 ; 0,636], fausse alerte [0,262 ; 0,481]. Ils mesurent l'incertitude sur le test, **pas une validation du seuil**.

À 0,50 sur le même test : TN 58 · FP 17 · FN 5 · TP 24, F1 macro **0,763**, coût **42** — moins d'alertes, mais cinq attaques manquées.

## 16. Application Streamlit

L'application `app.py` propose **12 pages** : 1. Accueil / Vue d'ensemble, 2. Exploration des données (EDA), 3. Analyse des corrélations, 4. Processus Machine Learning, 5. Comparaison des modèles, 6. Évaluation et métriques, 7. Prédiction d'un message, 8. Explication des attributs, 9. À propos / Limites, 10. Guide de présentation, 11. Mode présentation académique, 12. Comprendre le Machine Learning. Le formulaire contient **9 champs numériques** et trois scénarios pédagogiques.

Le verdict affiché est binaire au seuil 0,21 ; la zone NORMAL / VIGILANCE / ALERTE (0,20 / 0,88) est une **action secondaire**, jamais une classe supplémentaire. Résultats réels : normal `P(Oui) = 0,0006` → Non malveillant / NORMAL ; phishing IA `P(Oui) = 1,0000` → Malveillant / ALERTE ; à surveiller `P(Oui) = 0,4709` → Malveillant / VIGILANCE.

Les 12 pages de l'application sont décrites dans `docs/07_streamlit_application.md`.

## 17. Limites

- Jeu **synthétique** de 520 messages, test de 104 dont 29 `Oui` : les intervalles de confiance sont larges.
- Pas de validation temporelle ni sur des campagnes réelles.
- Heatmap, corrélations, moyennes et médianes par classe sont calculées sur le **train seul (416 messages)** ; le test n'est lu qu'au §18. L'importance par permutation est elle aussi calculée sur le train. Les anciens écarts (markdown du RF, entrées `Dummy`/`KNN`) ont été corrigés et sont tracés dans `docs/09_audit_findings.md`.
- Rapport de coûts 5:1 à valider ; Streamlit absent de l'environnement de vérification, rendu réel non testé ; aucun déploiement automatique.

## 18. Conclusion

Le projet démontre une démarche complète et rigoureuse : nettoyage, split stratifié, pipeline anti-fuite, validation croisée 5×5, seuil appris sur des probabilités OOF selon un coût métier, puis évaluation finale unique sur le test. Le modèle détecte **28 attaques sur 29** au prix de **28 fausses alertes**, pour un coût métier de **33**.

Le résultat est une **aide à la décision expliquable**, pas un automate : l'analyste reste responsable du verdict final. Les limites — données synthétiques, faible effectif du test, hypothèse de coût à valider — doivent être énoncées clairement en soutenance.
