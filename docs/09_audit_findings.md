# 09 — Rapport d'audit des artefacts

Périmètre : notebook `notebook_ML_IA_confiance_numerique.ipynb`, `model.joblib`, `model_meta.json`, CSV synthétique et `app.py` (commit `f573fc9`). Les artefacts numériques (`model.joblib`, `model_meta.json`, CSV) n'ont pas été modifiés. La phase 3 a corrigé `app.py` et `README.md` ; la phase 4 ajoute une cellule Markdown explicative dans le notebook (et sa version `.md`) sans toucher aux cellules de code ni aux sorties. Aucun paquet n'a été installé ; le `commit` / `push` final est effectué après la vérification.

## 1. Tableau synthétique

| Problème | Gravité | Origine | Impact scientifique | Correction recommandée | Correction appliquée |
|---|---|---|---|---|---|
| Heatmap de corrélation calculée sur `df` complet avant split (cellule 41) | MOYENNE | Notebook, cellule 41 | Les 104 lignes du test influencent l'EDA ; aucune variable supprimée sur cette base, impact limité, mais règle « train uniquement » non respectée | Recalculer sur `X_train` + `y_train` | Notebook non réécrit ; **appliquée dans l'application** (pages 2 et 3, 416 lignes du train) et dans `docs/01` |
| Markdown de la cellule 64 : RF accuracy 0,788 / F1 macro 0,747 / CV F1 0,771 ± 0,048 | MOYENNE | Notebook, markdown cellule 64 | Les sorties réelles (cellules 60 et 79) donnent 0,798 / 0,734 / 0,791 ± 0,051 : incohérence de reporting | Aligner le markdown sur les sorties réelles | **Non appliquée** (historique conservé) |
| `model_meta.json` : `Dummy 0,419` et `KNN 0,6314` sans code correspondant dans les cellules actuelles | FAIBLE | `model_meta.json`, `scores_f1_macro` | Valeurs historiques déclarées, non reproductibles depuis le notebook actuel (seuls 3 modèles y sont comparés) | Recomputer ces scores ou les étiqueter explicitement comme historiques | **Non appliquée** (métadonnées non modifiées) |
| Coût OOF à 0,21 annoncé 128 au lieu de 132 | CORRIGÉE | Anciennes versions du notebook et du README | Erreur d'interprétation : 128 est le coût au seuil 0,20 (`5×2+118`) ; à 0,21 le coût est `5×3+117 = 132` | Corriger le texte et la matrice associée | **Correction déjà appliquée** dans le notebook et le README (commit `f573fc9`) |
| Importance par permutation calculée sur le test (cellule 81) | FAIBLE | Notebook, cellule 81 | « Peek » sur le test après évaluation ; aucune sélection de variable basée dessus | Calculer l'importance sur le train ou la présenter clairement comme analyse descriptive | **Non appliquée** |
| Trois modèles évalués sur le test avant la section 9 bis (cellule 60) | FAIBLE | Notebook, cellule 60 | Risque d'illusion d'une sélection de modèle sur le test ; le choix final a été fait sur la CV du train | Signaler explicitement cette comparaison comme historique | **Non appliquée** ; signalée dans `docs/08` |
| Application simplifiée de 6 à 5 pages alors que la mission demande 8 onglets + mode présentation | CONTRAINTES | `app.py`, commit `f573fc9`, arbitrage utilisateur | Écart entre le livrable et le cahier des charges | Réconcilier le nombre d'onglets et le mode présentation | **Appliquée** : 12 entrées de navigation, dont un mode présentation académique à 14 étapes et le module « Comprendre le ML » ; les 5 pages historiques sont conservées |
| `streamlit` absent de l'environnement de vérification | INFORMATION | Environnement hors-ligne | Test de rendu réel impossible ; seule une exécution via stub local est possible | Installer Streamlit puis tester le rendu dans un navigateur | **Non appliquée** : installation non autorisée |
| Aucune fuite détectée dans le pipeline déployé | CONTRÔLE POSITIF | `model.joblib` + protocole du notebook | Aucune invalidation des métriques ; résultat à affirmer seulement avec sa justification | Maintenir le protocole et sa documentation | **Confirmée** par l'examen du code (voir détail 9) |
| Page 5 de `app.py` : « F1 en CV (seuil neutre 0,50) = 0,814 » et « F1 Random Forest (seuil 0,50) = 0,771 » | MOYENNE | `app.py`, page 5, tableau « Résultat du modèle retenu » | Aucune valeur 0,814 n'est reproductible depuis les artefacts ; recalcul OOF 5×5 au seuil 0,50 = **0,8082** et moyenne des 25 F1 par fold = **0,8073 ± 0,0466** ; le F1 macro CV réel du RF est **0,791 ± 0,051**, pas 0,771 | Corriger l'application à **0,808** et **0,791** et étiqueter chaque valeur selon son protocole | **Appliquée en phase 3** : `app.py` (pages 5, 6, 10) et `README.md` affichent 0,808 (OOF 5×5) et 0,791 (CV 5-fold RF) avec leur protocole |
| Comparaison de protocoles CV différents : cellule 79 (5-fold simple, seed 42) vs section 9 bis (5 plis × 5 répétitions) | FAIBLE | Notebook, cellule 79 et section 9 bis | Les deux F1 macro ne sont pas directement comparables ; risque de conclure à une différence de performance qui n'est qu'un effet de protocole | Étiqueter explicitement le protocole de chaque valeur affichée | **Appliquée en phase 3** : protocoles étiquetés dans l'app (pages 5, 6, 10, 11) et le README |
| Boutons « Charger ce scénario » : les champs du formulaire ne se mettaient pas à jour | MOYENNE | `app.py`, page 7 | `st.session_state["scenario"]` changeait mais les `number_input` / `selectbox` avec `key` gardaient leur état : le scénario affiché ne correspondait pas au scénario chargé | Écrire aussi les clés `n_*` / `c_*` des widgets | **Appliquée en phase 4** : `charger_scenario()` synchronise le scénario et toutes les clés de widgets |
| `P(Oui)` calculée par le modèle mais non expliquée dans l'application | MOYENNE | `app.py`, version initiale | Risque de confondre la probabilité et le verdict, ou d'utiliser un indice de classe supposé | Afficher intercept, coefficients réels, sigmoïde et contrôle `predict_proba()` | **Appliquée en phase 4** : `details_probabilite()` (pages 7 et 12), module page 12, `docs/10`, cellule 9 ter du notebook |
| Cellule 56 du notebook : `artefacts/processus_phishing_ia.png` referencing un fichier absent | FAIBLE | Notebook, cellule 56 | Image du processus non reproductible depuis le dépôt | Restaurer le PNG depuis l'image embarquée dans le notebook | **Appliquée en phase 4** : PNG extrait du notebook (SHA-256 `9da203856455…`), aucun visuel inventé |

## 2. Détails des constats

### 1. Corrélation calculée avant le split — MOYENNE

**Origine.** Cellule 41 du notebook : la heatmap est calculée sur `df` complet, avant la séparation train/test.

**Impact.** Les 104 lignes du test participent à l'analyse exploratoire. Aucune variable n'a été supprimée sur cette base, donc l'impact pratique est limité, mais la règle demandée est « train uniquement ».

**Correction recommandée.** Recalculer la matrice sur `X_train` + `y_train`.

**Correction réellement appliquée.** Non appliquée dans le notebook, la source de vérité n'ayant pas été réécrite. Les valeurs train-only sont utilisées dans `docs/01`.

### 2. Markdown non aligné sur les sorties Random Forest — MOYENNE

**Origine.** Markdown de la cellule 64 : accuracy **0,788**, F1 macro **0,747**, F1 macro CV **0,771 ± 0,048**.

**Impact.** Les sorties réelles des cellules 60 et 79 donnent **0,798**, **0,734**, **0,791 ± 0,051**. Un lecteur qui cite le markdown rapporte des chiffres erronés.

**Correction recommandée.** Aligner le markdown sur les sorties réelles.

**Correction réellement appliquée.** Non appliquée ; l'historique du notebook a été conservé. Le constat est documenté dans `docs/08`, partie 9.

### 3. Scores historiques dans `model_meta.json` — FAIBLE

**Origine.** `scores_f1_macro` contient `Dummy : 0,419` et `KNN : 0,6314`, sans code correspondant dans les cellules actuelles, où seuls 3 modèles sont comparés.

**Impact.** Ces valeurs sont déclarées, non reproductibles depuis le notebook actuel.

**Correction recommandée.** Recomputer ces scores ou les étiqueter explicitement comme historiques.

**Correction réellement appliquée.** Non appliquée ; `model_meta.json` n'a pas été modifié.

### 4. Coût OOF au seuil 0,21 — CORRIGÉE

**Origine.** D'anciennes versions du notebook et du README annonçaient un coût de **128** au seuil 0,21.

**Impact.** 128 correspond au seuil **0,20** (`5×2 + 118`). Au seuil retenu **0,21**, la matrice OOF est **TN 182 · FP 117 · FN 3 · TP 114**, soit un coût de **132** (`5×3 + 117`). Au seuil 0,22 : FN 4, FP 114, coût 134.

**Correction recommandée.** Corriger le texte et la matrice associée.

**Correction réellement appliquée.** Correction **déjà appliquée** dans le notebook et le README (commit `f573fc9`). Le présent document et `docs/05`, `docs/06`, `docs/08` utilisent 132.

### 5. Importance par permutation sur le test — FAIBLE

**Origine.** Cellule 81 : l'importance par permutation est calculée sur le test, comme analyse descriptive.

**Impact.** Il s'agit d'un « peek » sur le test après l'évaluation finale. Aucune sélection de variable n'a été fondée sur ce résultat, donc la métrique finale n'est pas biaisée, mais la discipline « test lu une seule fois » est lexicalement fragilisée.

**Correction recommandée.** Faire cette analyse sur le train ou l'étiqueter clairement comme descriptive post-évaluation.

**Correction réellement appliquée.** Non appliquée.

### 6. Comparaison de modèles sur le test avant la section 9 bis — FAIBLE

**Origine.** Cellule 60 : trois modèles sont évalués sur le test avant la section 9 bis.

**Impact.** Risque d'illusion d'une sélection de modèle sur le test. En réalité, le choix final a été fait sur la validation croisée du train ; le test a été lu une seule fois pour l'évaluation finale.

**Correction recommandée.** Signaler explicitement ce tableau comme une comparaison historique, sans rôle dans la sélection.

**Correction réellement appliquée.** Notebook non réécrit ; les corrélations train uniquement sont utilisées dans `docs/01`. À la demande de l'utilisateur, l'application affiche désormais la **heatmap exacte du notebook** (cellule 41) dans les pages 2 et 3, extraite byte-à-byte vers `artefacts/matrice_correlation_eda.png` (SHA-256 `631c485f…`). Le classement chiffré train seul reste affiché à part, sous un titre explicite. L'écart entre les deux protocoles reste signalé dans `docs/08`, partie 9.

### 7. Écart application / cahier des charges — CONTRAINTES

**Origine.** `app.py` (commit `f573fc9`) proposait initialement 6 pages et en propose 5 après arbitrage utilisateur, alors que la mission demande **8 onglets + un mode présentation**.

**Impact.** Le livrable ne couvre pas entièrement le cahier des charges ; la page 5 (« Guide de présentation ») ne constitue pas un mode présentation dédié.

**Correction recommandée.** Réconcilier l'architecture de navigation avec les 8 onglets demandés et ajouter le mode présentation.

**Correction réellement appliquée.** Phase 3 : la navigation passe de 5 à **11 entrées** — les cinq pages historiques sont conservées et six vues sont ajoutées (corrélations train, processus ML, comparaison des modèles, évaluation, à propos/limites) plus un **mode présentation académique à 14 étapes**. Le guide historique devient la page 10.

### 8. Absence de Streamlit — INFORMATION

**Origine.** Environnement de vérification hors-ligne : `streamlit` n'est pas installé.

**Impact.** Le rendu réel dans un navigateur n'a pas pu être testé ; seules les fonctions Python ont été exécutées via un stub local.

**Correction recommandée.** Installer Streamlit et ouvrir l'application dans un navigateur pour valider le rendu.

**Correction réellement appliquée.** Non appliquée : aucune installation de bibliothèque n'était autorisée. Voir la limite finale.

### 9. Fuite de données : contrôle négatif confirmé — CONTRÔLE POSITIF

**Constat.** Aucune fuite détectée dans le pipeline déployé.

**Justification.** `FeaturesPhishing.fit` n'apprend rien (l'expression `log1p` et les interactions sont déterministes) ; `SimpleImputer(strategy="median")` et `StandardScaler` sont **à l'intérieur du `Pipeline`**, donc ajustés par fold pendant la CV ; le seuil **0,21** et le triage **0,20 / 0,88** sont appris sur les probabilités OOF du train ; le test de 104 lignes est lu **une seule fois**, après le choix du modèle et du seuil.

**Portée.** Cette affirmation est valable pour le pipeline déployé et le protocole décrit. Elle ne couvre pas les limites mentionnées aux points 1, 5 et 6, qui concernent l'analyse exploratoire et les analyses descriptives, pas l'entraînement du modèle final.

### 10. F1 CV du modèle retenu annoncé dans l'application — MOYENNE

**Origine.** `app.py`, page 5, tableau « Résultat du modèle retenu » : « F1 en CV (seuil neutre 0,50) = 0,814 » et « F1 Random Forest (seuil 0,50) = 0,771 ».

**Impact.** Le recalcul selon le protocole exact du notebook (StratifiedKFold à 5 plis, `shuffle=True`, graines 42 à 46, probabilités moyennées sur les cinq vecteurs OOF) donne un **F1 macro de 0,8082 au seuil 0,50**. La moyenne des **25 scores F1 macro par fold** est de **0,8073**, avec un écart-type de **0,0466**. **Aucune valeur 0,814 n'est reproductible depuis les artefacts.** Pour le Random Forest, la sortie réelle de la cellule 79 donne **0,791 ± 0,051** en F1 macro CV ; le chiffre **0,771** provient uniquement du markdown historique de la cellule 64 (voir constat 2).

**Correction recommandée.** Remplacer 0,814 par **0,808** (F1 macro OOF 5×5 au seuil 0,50) et 0,771 par **0,791** (F1 macro CV du Random Forest, cellule 79), en précisant le protocole associé à chaque nombre.

**Correction réellement appliquée.** Phase 3 : le tableau de l'ancienne page 5 (devenue page 10) affiche désormais « F1 macro — OOF 5×5 du modèle retenu (seuil 0,50) = **0,808** » et « F1 macro — CV 5-fold du Random Forest (cellule 79) = **0,791** ». La page 6 et le README portent les mêmes valeurs étiquetées. Le notebook n'a pas été réécrit.

### 11. Protocoles CV différents présentés comme comparables — FAIBLE

**Origine.** La cellule 79 du notebook utilise une **CV 5-fold simple avec seed 42**, tandis que la section 9 bis utilise la **CV répétée 5 plis × 5 graines (42–46)** dont sont issus les probabilités OOF.

**Impact.** Les deux F1 macro (0,791 ± 0,051 pour le RF en cellule 79 ; 0,8082 pour le modèle retenu sur les OOF 5×5 au seuil 0,50) ne sont pas directement comparables : les découpages, le nombre d'entraînements et la manière d'agréger les prédictions diffèrent. Les présenter dans un même tableau sans étiquette peut suggérer à tort une différence de performance.

**Correction recommandée.** Étiqueter chaque valeur par son protocole (CV 5-fold simple seed 42 / OOF 5×5 répétée) et éviter la comparaison directe.

**Correction réellement appliquée.** Phase 3 : les pages 5, 6, 10 et 11 de l'application et la section « Validation croisée » du README séparent explicitement la **CV 5-fold simple (cellule 79)** de la **CV 5×5 répétée (section 9 bis)** et évitent toute comparaison directe des deux F1.

## 3. Bilan des tests hors-ligne effectués

| Contrôle | Résultat |
|---|---|
| Compilation Python (`py_compile`) de `app.py` | **OK** — aucune erreur de syntaxe |
| Lecture et parsing de `model_meta.json` | **OK** — JSON valide ; seuil 0,21, seuils de triage 0,20 / 0,88, métriques test présentes |
| Dataset | **524 → 520 lignes** après suppression des doublons |
| Split stratifié 80/20, `random_state = 42` | **416 / 104**, avec 299 `Non` / 117 `Oui` et 75 `Non` / 29 `Oui` |
| Rechargement du modèle | `joblib.load(model.joblib)` **OK** ; pipeline `FeaturesPhishing → imputation → standardisation → LogisticRegression` opérationnel |
| Métriques recalculées depuis le modèle | Accuracy **72,1 %**, rappel `Oui` **96,6 %**, précision `Oui` **50,0 %**, F1 macro **0,7115**, ROC-AUC **0,9099**, AP **0,8095**, Brier **0,1234**, coût **33** |
| Matrices conformes | OOF train : **182 / 117 / 3 / 114**, coût **132** ; test à 0,21 : **47 / 28 / 1 / 28**, coût **33** ; test à 0,50 : **58 / 17 / 5 / 24**, coût **42** |
| Scénarios de l'application | Normal `P(Oui) = 0,0006` → Non malveillant / NORMAL ; phishing IA `1,0000` → Malveillant / ALERTE ; à surveiller `0,4709` → Malveillant / VIGILANCE ; exemple `0,28` → Malveillant / VIGILANCE |
| Contrôle complémentaire des F1 CV | Selon le protocole 5×5 du notebook, F1 macro sur probabilités OOF au seuil 0,50 = **0,8082** ; moyenne des 25 F1 macro par fold = **0,8073 ± 0,0466** ; **0,814 non reproductible** ; F1 macro CV du RF (cellule 79) = **0,791 ± 0,051** |
| Corrélations train-only affichées | `domaine_age_jours −0,322`, `urgence_score +0,285`, `expediteur_connu −0,278`, `nb_liens +0,244` — recalculées depuis `get_train_correlation()` sur 416 lignes |
| Exécution des 12 pages | **12 entrées × 2 états du formulaire (`FAKE_SUBMIT` 0 et 1)** exécutées via un stub local (Streamlit simulé), sans erreur dans les fonctions appelées, y compris le mode présentation et le module page 12 |
| Cohérence probabilité / coefficients | `intercept + Σ(coef × variable standardisée)` = `decision_function` ; sigmoïde = `predict_proba()['Oui']`, écart **0,00** ; intercept **−0,764195** ; 8 coefficients lus dans `model.joblib` |
| Courbe de coût OOF tracée en page 12 | Minimum **128** à 0,20 ; coût **132** au seuil retenu 0,21 — identiques à `docs/05` et aux sorties du notebook |
| Images du notebook | **19 PNG** intégrés au `.ipynb` vérifiés byte-à-byte (SHA-256) contre `notebook_ML_IA_confiance_numerique_files/` ; `artefacts/processus_phishing_ia.png` restauré depuis l'image encodée de la cellule 56 |
| installations | **Aucune bibliothèque installée** ; `commit` / `push` effectués à la fin de la mission (voir §5) |

## 4. Limite finale

**Rendu Streamlit réel non testé.** `streamlit` est absent de l'environnement de vérification et son installation n'était pas autorisée : le comportement des widgets, la mise en page et l'affichage des graphiques dans un navigateur n'ont pas pu être validés. Les douze entrées ont uniquement été exécutées au niveau Python via un stub local. Le déploiement/publication automatique : **non disponible dans les artefacts**.

## 5. Phase 4 — module pédagogique et formulaire

- `app.py` : correction de `charger_scenario()` (synchronisation des clés de widgets) ; ajout de `details_probabilite()` ; barre de probabilité et décomposition dans la page 7 ; nouvelle page 12 « Comprendre le Machine Learning » (sections A–F) ; `get_feature_names_out()` ajouté à `FeaturesPhishing` pour nommer les 8 variables réellement produites ; indice de `Oui` déduit de `classes_`.
- `notebook_ML_IA_confiance_numerique.ipynb` et `.md` : ajout d'une section « 9 ter » sur la sigmoïde, les coefficients réels, le coût OOF et le caractère secondaire du triage. Aucune cellule de code ni sortie existante n'a été modifiée.
- `docs/10_probability_and_learning.md` : récapitulatif des nombres vérifiés et du protocole.
- `artefacts/processus_phishing_ia.png` : image du notebook restaurée, sans valeur ni visuel inventé.
