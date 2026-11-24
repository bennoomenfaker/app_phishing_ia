# 07 — Application Streamlit : architecture et comportement

L'application `app.py` est un prototype pédagogique d'aide à la décision. Elle ne remplace pas l'analyste : elle propose un verdict binaire, une probabilité et une priorité de vérification. La version initiale (commit `f573fc9`) comptait cinq pages ; la phase 3 la porte à douze entrées sans supprimer les précédentes.

## 1. Architecture du fichier

`app.py` est un fichier unique organisé en plusieurs blocs :

| Bloc | Rôle |
|---|---|
| `CFG` | Configuration centrale : titre, jeux de données, cible, seuil, libellés, scénarios, règles d'explication |
| Constantes de chemin | `ROOT`, `DATA_PATH`, `MODEL_PATH` (`model.joblib`), `META_PATH` (`model_meta.json`), `NOTEBOOK` |
| Constantes de décision | `SEUIL = 0,21`, `SEUIL_BAS = 0,20`, `SEUIL_HAUT = 0,88`, lus dans `model_meta.json` |
| Navigation | `PAGES` : 11 entrées, dont le mode présentation académique |
| Fonctions de chargement | `load_model`, `load_data`, `get_train_split`, `get_train_correlation`, `get_deployed_test_metrics` |
| Fonctions métier | `prepare_xy`, `FeaturesPhishing`, `make_modele_ameliore`, `predire`, `expliquer` |
| Fonctions de restitution | `render_notebook`, graphiques, `heatmap_cm`, `render_correlation_page`, `render_process_page`, `render_comparison_page`, `render_evaluation_page`, `render_about_page`, `render_presentation_mode` |
| Interface | `st.set_page_config`, barre latérale `st.sidebar.radio`, dispatch par numéro de page (`page_no`) |

### Chargement et cache

```python
@st.cache_resource
def load_model(model_path, meta_path):
    return joblib.load(model_path), json.loads(Path(meta_path).read_text(encoding="utf-8"))

@st.cache_data
def load_data(data_path, colonnes_exclues, empreinte):
    ...
```

- `@st.cache_resource` charge **une seule fois** le pipeline `model.joblib` et les métadonnées JSON.
- `@st.cache_data` charge le CSV ; **l'empreinte SHA-256 du fichier fait partie de la clé de cache**. Si le dataset est remplacé, l'application recharge les données au lieu de servir un ancien cache.
- `get_train_split()` reproduit le split 80/20 stratifié (`random_state=42`) ; `get_train_correlation()` et `get_cv_confusion()` travaillent sur ce train, jamais sur le test.
- `get_deployed_test_metrics()` évalue le pipeline **sauvegardé** sur le test sans le réentraîner.
- Aucun réentraînement n'a lieu pendant une prédiction : le pipeline déployé est réutilisé tel quel.

## 2. Pipeline déployé

`model.joblib` contient exactement :

**FeaturesPhishing → SimpleImputer(strategy="median") → StandardScaler → LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42)**

`FeaturesPhishing` ne apprend rien (`fit` est l'identité) et construit :

- `log_age = log1p(domaine_age_jours)` ;
- `log_age` conservé avec `urgence_score`, `nb_liens`, `expediteur_connu`, `piece_jointe`, `personnalisation_score` ;
- `urg_x_inconnu = urgence_score × (1 - expediteur_connu)` ;
- `liens_x_inconnu = nb_liens × (1 - expediteur_connu)`.

L'imputation médiane et la standardisation sont **à l'intérieur du Pipeline** : elles sont ajustées sur le train uniquement pendant la validation croisée, puis sur le train complet pour l'export. Aucune fuite de données dans le pipeline déployé.

## 3. Navigation actuelle : 12 entrées

| Page | Contenu |
|---|---|
| **1. Accueil / Vue d'ensemble** | Contexte IA générative, questions de recherche, coût du faux négatif, rôle de pré-dépistage |
| **2. Exploration des données (EDA)** | Métriques du dataset, distribution de la cible, histogrammes par classe, corrélation sur le train |
| **3. Analyse des corrélations** | Heatmap train, classement commenté, limites de Pearson et de causalité |
| **4. Processus Machine Learning** | 12 étapes du CSV au déploiement, détail des 5 plis × 5 répétitions |
| **5. Comparaison des modèles** | Scores réels, F1 / AUC / AP, justification du choix, valeurs historiques signalées |
| **6. Évaluation et métriques** | Matrices OOF et test annotées, métriques du pipeline sauvegardé, courbe de coût |
| **7. Prédiction d'un message** | Trois scénarios pédagogiques, formulaire synchronisé, probabilités, verdict, triage, décomposition réelle de `P(Oui)` |
| **8. Explication des attributs** | Dictionnaire des variables, définition, échelle, rôle dans le modèle |
| **9. À propos / Limites** | Données synthétiques, périmètre d'aide à la décision, traçabilité |
| **10. Guide de présentation** | Explication pédagogique d'AUC, AP, OOF, du seuil et des matrices de confusion |
| **11. 🎓 Mode présentation académique** | 14 étapes navigables pour une projection, chiffres lus dans les artefacts |
| **12. 🎓 Comprendre le Machine Learning** | Module A–F : apprentissage, vrais coefficients, calcul de `P(Oui)`, seuil, OOF, évaluation test et lien avec le formulaire |

La mission demandait **8 onglets + un mode présentation** : les cinq pages historiques ont été conservées et sept vues ajoutées, ce qui dépasse le minimum demandé sans rien détruire. L'ancien « Guide de présentation » devient la page 10 ; le véritable mode présentation est la page 11 ; le module pédagogique ML est la page 12. Voir `docs/09_audit_findings.md`, point 7.

## 4. Formulaire et décision

Le formulaire contient **9 champs numériques**, définis dans `model_meta.json` :

`heure_envoi`, `longueur_message`, `nb_liens`, `urgence_score`, `domaine_age_jours`, `fautes_langue`, `expediteur_connu`, `piece_jointe`, `personnalisation_score`.

Trois scénarios sont proposés : **normal**, **phishing typé IA**, **à surveiller**. Le bouton
« Charger ce scénario » synchronise désormais `session_state["scenario"]` **et** les clés
`n_*` / `c_*` des widgets : Streamlit conserve en effet l'état d'un widget identifié par `key`,
et `value=` est ignoré lors des reruns suivants. Sans ce correctif, changer de scénario après
une première instanciation ne mettait pas à jour les champs affichés.

Après une prédiction, la page 7 affiche aussi la barre de probabilité avec le seuil, puis le
détail `intercept + Σ(coef × valeur standardisée) → sigmoïde → P(Oui)`, avec l'écart numérique
avec `predict_proba()` ( voir `docs/10_probability_and_learning.md`).

Chaîne de décision :

1. la ligne saisie est complétée si nécessaire avec les médianes du `meta` ;
2. le pipeline transforme les 9 variables brutes en features ;
3. `predict_proba()` renvoie `P(Non)` et `P(Oui)` (classes binaires) ;
4. **verdict binaire** : `P(Oui) ≥ 0,21` → **Malveillant**, sinon **Non malveillant** ;
5. **triage secondaire** : `P(Oui) < 0,20` → 🟢 NORMAL ; `0,20 ≤ P(Oui) < 0,88` → 🟠 VIGILANCE ; `P(Oui) ≥ 0,88` → 🔴 ALERTE ;
6. un mécanisme d'explication met en avant les signaux dominants (âge du domaine, urgence, liens, pièce jointe, expéditeur connu) ;
7. la décision finale reste humaine : aucun blocage ni suppression automatique.

## 5. Résultats réels des trois scénarios

Recalculés depuis `model.joblib` :

| Scénario | `P(Oui)` | Verdict (seuil 0,21) | Zone de triage |
|---|---:|---|---|
| 1. Message normal | 0,0006 | Non malveillant | 🟢 NORMAL |
| 2. Phishing typé IA | 1,0000 | Malveillant | 🔴 ALERTE |
| 3. À surveiller | 0,4709 | Malveillant | 🟠 VIGILANCE |

Exemple vérifié : `P(Oui) = 0,28` → **Malveillant** car 0,28 ≥ 0,21, tout en restant en zone **VIGILANCE** car 0,28 est entre 0,20 et 0,88.

## 6. Pièges à éviter lors de la démonstration

1. **Confiance maximale ≠ `P(Oui)`.** La valeur maximale de `predict_proba()` peut être `P(Non)` ; c'est bien la colonne `Oui` qui est comparée au seuil. Un message normal a une forte confiance « globale » mais un `P(Oui)` très faible.
2. **Pas de réentraînement à chaque prédiction.** Le modèle est chargé et mis en cache ; l'application ne réapprend rien à partir des saisies utilisateur.
3. **Le seuil n'est pas 0,50.** La décision utilise 0,21, appris sur les probabilités OOF du train avec le coût `5·FN + FP`.
4. **Le triage n'est pas une troisième classe.** Il y a toujours deux verdicts ; les trois zones sont des actions de priorisation.
5. **AP ≠ rappel.** Une AP de 0,8095 ne signifie pas que 81 % des attaques sont détectées ; le rappel observé sur le test est de 96,6 %.
6. **Aucune action automatique.** L'application est un outil pédagogique ; la validation humaine est obligatoire.
7. **Rendu non vérifié en environnement hors-ligne.** `streamlit` est absent de l'environnement de vérification : seules les fonctions ont été exécutées via un stub local. Le rendu réel dans un navigateur : **non disponible dans les artefacts**.

## 7. État du déploiement

Aucun déploiement ni publication automatique n'a été effectué. Les artefacts livrés sont `app.py`, `model.joblib`, `model_meta.json`, le CSV synthétique et les neuf documents de `docs/`. L'évolution vers les 8 onglets demandés et le mode présentation est finalisée dans les fichiers locaux ; aucun `commit` ni `push` n'a été effectué pour ces changements.
