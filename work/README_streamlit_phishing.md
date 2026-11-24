# Application Streamlit — Détection de messages malveillants

## Fichiers conservés

Ce dossier est gardé comme **référence méthodologique** (validation croisée imbriquée et OOF sur 520 lignes). Il contient :

- `classification_binaire_phishing.ipynb` : notebook reproductible et son explication OOF ;
- `dataset_phishing_ia.xlsx` : classeur utilisé pour l'EDA ;
- `modele_phishing_pipeline_tuned.joblib` : pipeline de régression logistique réajusté sur les données disponibles ;
- `comparaison_nested_cv.csv` : comparaison des modèles par validation imbriquée ;
- `predictions_nested_oof.csv` : prédictions hors pli utilisées pour la matrice ;
- `requirements_streamlit.txt` : dépendances Python.

L'ancienne application autonome `app_streamlit_phishing.py` et l'ancien notebook `classification_binaire_phishing_execute.ipynb` ont été supprimés comme demandé : ils étaient redondants avec `../app.py` et le notebook principal.

## Application finale

L'application à utiliser est **`../app.py`** (verdict binaire **Malveillant / Non malveillant**, matrice OOF de validation croisée, probabilité en information secondaire). Son lancement est documenté dans le `README.md` racine du projet. Les sections ci-dessous décrivent la méthode de référence du dossier `work/`.

Le protocole compare quatre modèles avec **validation croisée imbriquée stratifiée** : 5 plis externes pour l'évaluation et 3 plis internes pour régler les hyperparamètres au F1 macro. La logistique a été retenue: son F1 macro moyen externe est d'environ 0,795 (écart-type 0,043), très proche du SVM RBF (0,794 ± 0,065). La logistique est préférée pour sa simplicité; cette faible différence ne prouve pas une supériorité statistique.

La matrice OOF agrégée compte TN=318, FP=56, FN=34 et TP=112 sur 520 observations. Elle représente l'évaluation hors pli de la procédure; le modèle Joblib livré est ensuite réajusté sur toutes les lignes, et n'est donc pas lui-même un jeu de test indépendant. F1 macro, ROC-AUC et les autres métriques sont expliquées dans l'application et dans le notebook.

Le verdict binaire est produit par `predict()`; aucun seuil n'est réglable. La probabilité estimée est informative uniquement. Les exemples sont construits pour la démonstration et ne proviennent pas de courriels réels.

## Limites

Le classeur contient 520 observations uniques, est petit et présenté comme synthétique/pédagogique. Le modèle ne lit pas le texte d'un courriel, ne visite pas les URL et ne scanne pas les pièces jointes. Il reste 34 faux négatifs et 56 faux positifs dans les prédictions OOF. On ne peut pas garantir FN=0 et FP=0 simultanément; TP est une détection correcte qu'on cherche à augmenter, pas à ramener à zéro. Une validation externe sur des données réelles représentatives est indispensable avant tout usage de sécurité.

Le fichier Joblib est sérialisé par Python; ne chargez jamais un Joblib reçu d'une source non fiable.
