# Seuil retenu : 0,21

## Décision

Le seuil de classification retenu est **0,21**. Il est appris sur les probabilités OOF du train (416 messages) avec la règle de coût `5·FN + 1·FP` : un phishing manqué coûte cinq fois plus cher qu'une fausse alerte. Le test (104 messages) n'a servi qu'à la mesure finale, jamais au choix du seuil.

## Résultats sur le test

| Seuil | Modèle | Accuracy | FP | FN | Rappel « Oui » | F1 macro | AUC | AP | Coût `5·FN+FP` |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,55 | Référence — avant | 0,750 | 18 | 8 | 0,724 | 0,716 | 0,832 | 0,656 | 58 |
| 0,35 | Référence — travail initial | 0,663 | 28 | 7 | 0,759 | 0,643 | 0,832 | 0,656 | 63 |
| **0,21** | **Modèle amélioré — retenu** | **0,721** | **28** | **1** | **0,966** | **0,712** | **0,910** | **0,810** | **33** |

## Points clés

- **Détection des malveillants** : 28 phishing détectés sur 29, soit un rappel de **96,6 %** et seulement **1 faux négatif**, contre 8 avec le seuil 0,55 et 7 avec le seuil 0,35.
- **Fausses alertes** : 28 faux positifs. Le compromis est assumé : réduire ce nombre reviendrait à rater davantage de phishing, ce que le coût métier pénalise davantage.
- **Accuracy** : 0,721. Ce n'est pas le score le plus élevé possible, mais le seuil optimise le coût métier, pas l'exactitude brute.
- **Distinction du modèle** : AUC **0,910** et AP **0,810**, contre 0,832 et 0,656 pour le modèle de référence. Cette amélioration vient du modèle (`log_age` + interactions, `class_weight="balanced"`), pas du seuil : **l'AUC et l'AP ne changent pas avec le seuil**.

## Formulation pour la soutenance

> « Nous conservons le seuil 0,21, appris sur la validation croisée du train avec un coût cinq fois supérieur pour un phishing manqué. Sur le test, il détecte 96,6 % des messages malveillants avec un seul manqué. L'AUC passe de 0,832 à 0,910 grâce au modèle amélioré ; le seuil, lui, ne modifie pas le classement. »

Le détail de la comparaison se trouve dans `notebook_ML_IA_confiance_numerique.ipynb`, section **18.7**.
