# 06 — Évaluation finale sur le jeu de test

## 1. Protocole

Le jeu de test est lu **une seule fois**, après la sélection du modèle et du seuil. Il contient **104 observations** : 75 `Non` et 29 `Oui`. Le seuil appliqué est **0,21**, appris sur les probabilités OOF du train (voir `docs/05_oof_and_threshold.md`) ; il n'a pas été ajusté sur le test.

## 2. Matrice de confusion (seuil 0,21)

|  | Prédit : Non | Prédit : Oui | Total |
|---|---:|---:|---:|
| **Réel : Non** | TN = 47 | FP = 28 | 75 |
| **Réel : Oui** | FN = 1 | TP = 28 | 29 |
| **Total** | 48 | 56 | 104 |

## 3. Métriques finales

| Métrique | Valeur exacte | Valeur affichée | Lecture |
|---|---:|---:|---|
| Accuracy | 72,1 % | 72,1 % | Part des décisions correctes, mais trompeuse avec des classes déséquilibrées |
| Rappel `Oui` | 96,6 % | 96,6 % | 28 attaques détectées sur 29 |
| Précision `Oui` | 50,0 % | 50,0 % | Une alerte sur deux est une vraie attaque |
| F1 macro | 0,7115 | 0,712 | Équilibre entre précision et rappel, sans favoriser la classe majoritaire |
| ROC-AUC | 0,9099 | 0,910 | Qualité du classement des messages, indépendante du seuil |
| AP (*average precision*) | 0,8095 | 0,810 | Qualité de la courbe Précision-Rappel pour la classe `Oui` |
| Brier score | 0,1234 | 0,123 | Qualité de calibration des probabilités (plus proche de 0 = meilleur) |
| Coût métier `5·FN + FP` | 33 | 33 | `5 × 1 + 28 = 33` |

À titre de comparaison descriptive, sur **le même test au seuil 0,50** : **TN 58 · FP 17 · FN 5 · TP 24**, **F1 macro 0,763**, **coût 42**. Ce résultat illustre le compromis : moins de fausses alertes, mais cinq attaques manquées au lieu d'une. Il ne remet pas en cause le seuil 0,21, qui reste appris sur le train. L'AUC et l'AP, indépendantes du seuil, restent 0,9099 et 0,8095.

## 4. Comparaison CV / OOF / Test sans confusion

| Ensemble | Taille | Seuil | AUC | AP | F1 macro | Coût |
|---|---:|---:|---:|---:|---:|---:|
| CV (train, 5 plis × 5 répétitions) | 416 | — | 0,9092 ± 0,0031 | 0,8119 ± 0,0034 | non disponible dans les artefacts | non disponible dans les artefacts |
| Probabilités OOF moyennées (train) | 416 | 0,21 | 0,9112 | 0,8154 | non disponible dans les artefacts | 132 |
| Test final | 104 | 0,21 | 0,9099 | 0,8095 | 0,7115 | 33 |
| Test final (comparaison descriptive) | 104 | 0,50 | 0,9099 | 0,8095 | 0,763 | 42 |

Points de vigilance :

- la CV et l'OOF décrivent le **train** ; le test décrit la **généralisation** ;
- l'AUC OOF (0,9112), l'AUC CV moyenne (0,9092) et l'AUC test (0,9099) sont proches, ce qui est cohérent mais ne doit pas être présenté comme une preuve d'égalité ;
- le F1 macro dépend du seuil : celui du test à 0,21 (0,7115) et celui à 0,50 (0,763) ne sont pas calculés dans les mêmes conditions ;
- le coût OOF (132) et le coût test (33) portent sur des échantillons de tailles différentes (416 contre 104) et ne sont pas comparables directement.

## 5. Lecture métier pour l'analyste

- **28 attaques détectées** sur 29 : le rappel de 96,6 % traduit une couverture élevée du phishing.
- **1 attaque manquée** (`FN = 1`) : c'est l'erreur la plus coûteuse selon le rapport 5:1 retenu.
- **28 fausses alertes** (`FP = 28`) : chaque fausse alerte consomme du temps analyste, d'où l'intérêt du triage.
- **Coût métier : 33**, soit `5 × 1 + 28`.

Le triage issu du train répartit les 104 messages ainsi : **61/104 automatisés**, dont **1 FN et 1 FP dans la partie automatisée**, et **43 cas en revue humaine**.

| Zone de triage | Réel Non | Réel Oui | Total |
|---|---:|---:|---:|
| Alerte | 1 | 14 | 15 |
| Normal | 45 | 1 | 46 |
| Revue humaine | 29 | 14 | 43 |
| **Total** | 75 | 29 | 104 |

Un verdict `Malveillant` déclenche une **vérification humaine**, jamais une suppression automatique. La zone « revue humaine » concentre 43 messages sur 104 : le système ne remplace pas l'analyste, il priorise son travail.

## 6. Intervalles de confiance bootstrap

Sur le test, **2 000 tirages bootstrap** donnent les intervalles à 95 % suivants :

| Métrique | IC95 % |
|---|---|
| Rappel `Oui` | [0,886 ; 1,000] |
| Précision `Oui` | [0,368 ; 0,636] |
| Taux de fausse alerte | [0,262 ; 0,481] |

Ces intervalles mesurent l'incertitude d'échantillonnage sur le jeu de test. **Ils ne constituent pas une validation du seuil** : le seuil 0,21 provient exclusivement des probabilités OOF du train. La largeur de l'intervalle de précision rappelle qu'avec 29 positifs seulement, la précision observée (50,0 %) est assez imprécise.

## 7. Limites de généralisation

- Le jeu est **synthétique**, généré pour un usage pédagogique : aucune donnée personnelle, aucun vrai e-mail. La performance sur des campagnes réelles : **non disponible dans les artefacts**.
- Le test ne compte que **104 messages**, dont **29 malveillants** : les IC95 sont larges, en particulier pour la précision.
- Il n'y a pas de validation temporelle ni de test sur une autre population : la robustesse face à la dérive des campagnes : **non disponible dans les artefacts**.
- Le rapport de coûts 5:1 est une **hypothèse métier** à valider par un responsable sécurité ; un autre rapport conduirait à un autre seuil (voir la sensibilité en `docs/05`).
- Aucun déploiement ni publication automatique n'a été effectué ; le rendu Streamlit réel n'a pas pu être testé dans l'environnement de vérification (`streamlit` absent).

Ces limites invitent à présenter les résultats comme une **preuve de concept**, pas comme une garantie opérationnelle.
