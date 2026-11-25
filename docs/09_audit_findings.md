# 09 — Rapport d'audit des artefacts

Périmètre : notebook `notebook_ML_IA_confiance_numerique.ipynb`, `model.joblib`, `model_meta.json`, CSV synthétique et `app.py`.

Historique des phases : la phase 3 a corrigé `app.py` et `README.md` ; la phase 4 a ajouté le module pédagogique et la page 12 ; la **phase 5** corrige le notebook lui-même (heatmap train, markdowns, importance par permutation), régénère `model.joblib` / `model_meta.json` et aligne `app.py`, le README et les docs sur les sorties réelles. Aucun paquet n'a été installé ; le `commit` / `push` final est effectué après la vérification.

## 1. Tableau synthétique

| Problème | Gravité | Origine | Impact scientifique | Correction recommandée | Correction appliquée |
|---|---|---|---|---|---|
| Heatmap de corrélation calculée sur `df` complet avant split | MOYENNE | Notebook, §9 | Les 104 lignes du test influençaient l'EDA ; règle « train uniquement » non respectée | Recalculer sur le train seul | **Corrigée en phase 5** : heatmap recalculée sur les 416 lignes du train (§9), image `artefacts/matrice_correlation_eda.png` régénérée (SHA `5ddaa6e4…`) |
| Markdown RF : accuracy 0,788 / F1 macro 0,747 / CV F1 0,771 ± 0,048 | MOYENNE | Notebook, §16 | Les sorties réelles donnent 0,798 / 0,734 / 0,791 ± 0,051 | Aligner le markdown sur les sorties réelles | **Corrigée en phase 5** : le markdown cite désormais 0,798 / 0,734 / 0,791 ± 0,051 |
| `model_meta.json` : `Dummy 0,419` et `KNN 0,6314` sans code correspondant | FAIBLE | `model_meta.json`, `scores_f1_macro` | Valeurs non reproductibles depuis le notebook (3 modèles comparés) | Supprimer les entrées sans code source | **Corrigée en phase 5** : `model_meta.json` régénéré, `Dummy` et `KNN` retirés |
| Coût OOF à 0,21 annoncé 128 au lieu de 132 | CORRIGÉE | Anciennes versions du notebook et du README | Erreur d'interprétation : 128 est le coût au seuil 0,20 (`5×2+118`) ; à 0,21 le coût est `5×3+117 = 132` | Corriger le texte et la matrice associée | **Correction déjà appliquée** dans le notebook et le README (commit `f573fc9`) |
| Importance par permutation calculée sur le test | FAIBLE | Notebook, §19 | « Peek » sur le test après évaluation | Calculer l'importance sur le train | **Corrigée en phase 5** : `permutation_importance(..., X_train, y_train)` ; classement réel : domaine_age 0,2429, urgence 0,1558, expéditeur 0,1469, nb_liens 0,1012 |
| Trois modèles évalués sur le test avant le modèle retenu | FAIBLE | Notebook, §16 | Risque d'illusion d'une sélection sur le test ; le choix final vient de la CV du train | Signaler la comparaison comme descriptive a posteriori | **Corrigée en phase 5** : §16 titré « comparaison descriptive (a posteriori) », protocoles explicités |
| Application simplifiée de 6 à 5 pages alors que la mission demande 8 onglets + mode présentation | CONTRAINTES | `app.py`, commit `f573fc9`, arbitrage utilisateur | Écart entre le livrable et le cahier des charges | Réconcilier le nombre d'onglets et le mode présentation | **Appliquée** : 12 entrées de navigation, dont un mode présentation académique à 14 étapes et le module « Comprendre le ML » ; les 5 pages historiques sont conservées |
| `streamlit` absent de l'environnement de vérification | INFORMATION | Environnement hors-ligne | Test de rendu réel impossible ; seule une exécution via stub local est possible | Installer Streamlit puis tester le rendu dans un navigateur | **Non appliquée** : installation non autorisée |
| Aucune fuite détectée dans le pipeline déployé | CONTRÔLE POSITIF | `model.joblib` + protocole du notebook | Aucune invalidation des métriques ; résultat à affirmer seulement avec sa justification | Maintenir le protocole et sa documentation | **Confirmée** par l'examen du code (voir détail 9) |
| Page 5 de `app.py` : « F1 en CV (seuil neutre 0,50) = 0,814 » et « F1 Random Forest (seuil 0,50) = 0,771 » | MOYENNE | `app.py`, page 5, tableau « Résultat du modèle retenu » | Aucune valeur 0,814 n'est reproductible depuis les artefacts ; recalcul OOF 5×5 au seuil 0,50 = **0,8082** et moyenne des 25 F1 par fold = **0,8073 ± 0,0466** ; le F1 macro CV réel du RF est **0,791 ± 0,051**, pas 0,771 | Corriger l'application à **0,808** et **0,791** et étiqueter chaque valeur selon son protocole | **Appliquée en phase 3** : `app.py` (pages 5, 6, 10) et `README.md` affichent 0,808 (OOF 5×5) et 0,791 (CV 5-fold RF) avec leur protocole |
| Comparaison de protocoles CV différents : §15 (5-fold simple, seed 42) vs §17 (5 plis × 5 répétitions) | FAIBLE | Notebook, §15 et §17 | Les deux F1 macro ne sont pas directement comparables ; risque de conclure à une différence de performance qui n'est qu'un effet de protocole | Étiqueter explicitement le protocole de chaque valeur affichée | **Appliquée en phase 3** : protocoles étiquetés dans l'app (pages 5, 6, 10, 11) et le README |
| Boutons « Charger ce scénario » : les champs du formulaire ne se mettaient pas à jour | MOYENNE | `app.py`, page 7 | `st.session_state["scenario"]` changeait mais les `number_input` / `selectbox` avec `key` gardaient leur état : le scénario affiché ne correspondait pas au scénario chargé | Écrire aussi les clés `n_*` / `c_*` des widgets | **Appliquée en phase 4** : `charger_scenario()` synchronise le scénario et toutes les clés de widgets |
| `P(Oui)` calculée par le modèle mais non expliquée dans l'application | MOYENNE | `app.py`, version initiale | Risque de confondre la probabilité et le verdict, ou d'utiliser un indice de classe supposé | Afficher intercept, coefficients réels, sigmoïde et contrôle `predict_proba()` | **Appliquée en phase 4** : `details_probabilite()` (pages 7 et 12), module page 12, `docs/10`, §17.2 du notebook |
| `artefacts/processus_phishing_ia.png` référençait un fichier absent | FAIBLE | Notebook, §13 | Image du processus non reproductible depuis le dépôt | Restaurer le PNG depuis l'image embarquée dans le notebook | **Appliquée en phase 4** : PNG extrait du notebook (SHA-256 `9da203856455…`), aucun visuel inventé |

## 2. Détails des constats

### 1. Corrélation calculée avant le split — MOYENNE

**Origine.** La heatmap était calculée sur `df` complet, avant la séparation train/test.

**Impact.** Les 104 lignes du test participaient à l'analyse exploratoire. Aucune variable n'a été supprimée sur cette base, donc l'impact pratique était limité, mais la règle « train uniquement » n'était pas respectée.

**Correction recommandée.** Recalculer la matrice sur le train seul.

**Correction réellement appliquée.** Phase 5 : la heatmap de la cellule 31 est calculée sur `df_train_eda` (**416 messages**, split stratifié `random_state=42`), avec la cible incluse (`cible (Oui = 1)`). L'image `artefacts/matrice_correlation_eda.png` a été régénérée depuis cette sortie (SHA-256 `5ddaa6e4c3bb234f4a6df3f2d83da4b09560308ccf684ec115c95212dd45196d`) et `app.py` vérifie cette empreinte.

### 2. Markdown non aligné sur les sorties Random Forest — MOYENNE

**Origine.** Un ancien markdown annonçait accuracy **0,788**, F1 macro **0,747**, F1 macro CV **0,771 ± 0,048**.

**Impact.** Les sorties réelles donnent **0,798**, **0,734**, **0,791 ± 0,051**. Un lecteur qui citait le markdown rapportait des chiffres erronés.

**Correction recommandée.** Aligner le markdown sur les sorties réelles.

**Correction réellement appliquée.** Phase 5 : le markdown du §16 cite désormais **0,798 / 0,734 / 0,791 ± 0,051** (valeurs des sorties) et présente le tableau comme descriptif a posteriori.

### 3. Scores historiques dans `model_meta.json` — FAIBLE

**Origine.** `scores_f1_macro` contenait `Dummy : 0,419` et `KNN : 0,6314`, sans code correspondant dans le notebook, où seuls 3 modèles de référence sont comparés.

**Impact.** Ces valeurs étaient déclarées mais non reproductibles.

**Correction recommandée.** Recomputer ces scores ou les retirer.

**Correction réellement appliquée.** Phase 5 : `model_meta.json` a été **régénéré par le notebook**. `scores_f1_macro` ne contient plus que `LogisticRegression`, `RandomForest`, `SVM_RBF` et `LogisticRegression_amelioree`. L'écart-type du F1 CV 5-fold du modèle retenu est désormais exposé (`0,0660`).

### 4. Coût OOF au seuil 0,21 — CORRIGÉE

**Origine.** D'anciennes versions du notebook et du README annonçaient un coût de **128** au seuil 0,21.

**Impact.** 128 correspond au seuil **0,20** (`5×2 + 118`). Au seuil retenu **0,21**, la matrice OOF est **TN 182 · FP 117 · FN 3 · TP 114**, soit un coût de **132** (`5×3 + 117`). Au seuil 0,22 : FN 4, FP 114, coût 134.

**Correction recommandée.** Corriger le texte et la matrice associée.

**Correction réellement appliquée.** Correction **déjà appliquée** dans le notebook et le README (commit `f573fc9`). Le présent document et `docs/05`, `docs/06`, `docs/08` utilisent 132.

### 5. Importance par permutation sur le test — FAIBLE

**Origine.** L'importance par permutation était calculée sur le test, comme analyse descriptive.

**Impact.** « Peek » sur le test après l'évaluation finale. Aucune sélection de variable n'avait été fondée sur ce résultat, donc la métrique finale n'était pas biaisée, mais la discipline « test lu une seule fois » était fragilisée.

**Correction recommandée.** Faire cette analyse sur le train.

**Correction réellement appliquée.** Phase 5 : `permutation_importance(..., X_train, y_train)`, 15 répétitions, `random_state=42`. Classement réel : `domaine_age_jours` **0,2429**, `urgence_score` **0,1558**, `expediteur_connu` **0,1469**, `nb_liens` **0,1012**, puis `longueur_message` 0,0492, `personnalisation_score` 0,0438, `heure_envoi` 0,0394, `fautes_langue` 0,0202, `piece_jointe` 0,0115.

### 6. Comparaison de modèles sur le test avant le §17 — FAIBLE

**Origine.** Trois modèles étaient évalués sur le test avant le modèle retenu.

**Impact.** Risque d'illusion d'une sélection de modèle sur le test. En réalité, le choix final a été fait sur la validation croisée du train ; le test n'a servi qu'à l'évaluation finale.

**Correction recommandée.** Signaler explicitement ce tableau comme une comparaison descriptive, sans rôle dans la sélection.

**Correction réellement appliquée.** Phase 5 : le §16 est titré « Comparaison descriptive des trois modèles de référence sur le test (a posteriori) », chaque F1 est rattaché à son protocole (test à 0,50 vs CV 5-fold du train), et le markdown précise que la LR améliorée est retenue sur la CV, pas sur ce tableau. La heatmap affichée est bien celle du §9 (train seul).

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

**Portée.** Cette affirmation est valable pour le pipeline déployé et le protocole décrit. Depuis la phase 5, les points 1, 5 et 6 (analyse exploratoire et analyses descriptives) sont eux aussi calculés sur le train : la heatmap, les moyennes/médianes par classe et l'importance par permutation ne relisent plus le test.

### 10. F1 CV du modèle retenu annoncé dans l'application — MOYENNE

**Origine.** `app.py`, page 5, tableau « Résultat du modèle retenu » : « F1 en CV (seuil neutre 0,50) = 0,814 » et « F1 Random Forest (seuil 0,50) = 0,771 ».

**Impact.** Le recalcul selon le protocole exact du notebook (StratifiedKFold à 5 plis, `shuffle=True`, graines 42 à 46, probabilités moyennées sur les cinq vecteurs OOF) donne un **F1 macro de 0,8082 au seuil 0,50**. La moyenne des **25 scores F1 macro par fold** est de **0,8073**, avec un écart-type de **0,0466**. **Aucune valeur 0,814 n'est reproductible depuis les artefacts.** Pour le Random Forest, la sortie réelle du §15 donne **0,791 ± 0,051** en F1 macro CV ; le chiffre **0,771** provient uniquement du markdown historique de la cellule 64 (voir constat 2).

**Correction recommandée.** Remplacer 0,814 par **0,8082** (F1 macro OOF 5×5 au seuil 0,50) et 0,771 par **0,791** (F1 macro CV du Random Forest, §15), en précisant le protocole associé à chaque nombre.

**Correction réellement appliquée.** Phase 3 : le tableau de l'ancienne page 5 (devenue page 10) affiche désormais « F1 macro — OOF 5×5 du modèle retenu (seuil 0,50) = **0,8082** » et « F1 macro — CV 5-fold du Random Forest (§15) = **0,791** ». La page 6 et le README portent les mêmes valeurs étiquetées. Le notebook a depuis été aligné en phase 5 (voir §6).

### 11. Protocoles CV différents présentés comme comparables — FAIBLE

**Origine.** Le §15 du notebook utilise une **CV 5-fold simple avec seed 42**, tandis que le §17 utilise la **CV répétée 5 plis × 5 graines (42–46)** dont sont issus les probabilités OOF.

**Impact.** Les deux F1 macro (0,791 ± 0,051 pour le RF en §15 ; 0,8082 pour le modèle retenu sur les OOF 5×5 au seuil 0,50) ne sont pas directement comparables : les découpages, le nombre d'entraînements et la manière d'agréger les prédictions diffèrent. Les présenter dans un même tableau sans étiquette peut suggérer à tort une différence de performance.

**Correction recommandée.** Étiqueter chaque valeur par son protocole (CV 5-fold simple seed 42 / OOF 5×5 répétée) et éviter la comparaison directe.

**Correction réellement appliquée.** Phase 3 : les pages 5, 6, 10 et 11 de l'application et la section « Validation croisée » du README séparent explicitement la **CV 5-fold simple (§15)** de la **CV 5×5 répétée (§17)** et évitent toute comparaison directe des deux F1.

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
| Contrôle complémentaire des F1 CV | Selon le protocole 5×5 du notebook, F1 macro sur probabilités OOF au seuil 0,50 = **0,8082** ; moyenne des 25 F1 macro par fold = **0,8073 ± 0,0466** ; **0,814 non reproductible** ; F1 macro CV du RF (§15) = **0,791 ± 0,051** |
| Corrélations train-only affichées | `domaine_age_jours −0,322`, `urgence_score +0,285`, `expediteur_connu −0,278`, `nb_liens +0,244` — recalculées depuis `get_train_correlation()` sur 416 lignes |
| Exécution des 12 pages | **12 entrées × 2 états du formulaire (`FAKE_SUBMIT` 0 et 1)** exécutées via un stub local (Streamlit simulé), sans erreur dans les fonctions appelées, y compris le mode présentation et le module page 12 |
| Cohérence probabilité / coefficients | `intercept + Σ(coef × variable standardisée)` = `decision_function` ; sigmoïde = `predict_proba()['Oui']`, écart **0,00** ; intercept **−0,764195** ; 8 coefficients lus dans `model.joblib` |
| Courbe de coût OOF tracée en page 12 | Minimum **128** à 0,20 ; coût **132** au seuil retenu 0,21 — identiques à `docs/05` et aux sorties du notebook |
| Images du notebook | **19 PNG** intégrés au `.ipynb` vérifiés byte-à-byte (SHA-256) contre `notebook_ML_IA_confiance_numerique_files/` ; `artefacts/processus_phishing_ia.png` restauré depuis l'image encodée du §13 |
| installations | **Aucune bibliothèque installée** ; `commit` / `push` effectués à la fin de la mission (voir §5) |

## 4. Limite finale

**Rendu Streamlit réel non testé.** `streamlit` est absent de l'environnement de vérification et son installation n'était pas autorisée : le comportement des widgets, la mise en page et l'affichage des graphiques dans un navigateur n'ont pas pu être validés. Les douze entrées ont uniquement été exécutées au niveau Python via un stub local. Le déploiement/publication automatique : **non disponible dans les artefacts**.

## 5. Phase 4 — module pédagogique et formulaire

- `app.py` : correction de `charger_scenario()` (synchronisation des clés de widgets) ; ajout de `details_probabilite()` ; barre de probabilité et décomposition dans la page 7 ; nouvelle page 12 « Comprendre le Machine Learning » (sections A–F) ; `get_feature_names_out()` ajouté à `FeaturesPhishing` pour nommer les 8 variables réellement produites ; indice de `Oui` déduit de `classes_`.
- `notebook_ML_IA_confiance_numerique.ipynb` et `.md` : ajout d'une section « 17.2 » sur la sigmoïde, les coefficients réels, le coût OOF et le caractère secondaire du triage. Aucune cellule de code ni sortie existante n'a été modifiée.
- `docs/10_probability_and_learning.md` : récapitulatif des nombres vérifiés et du protocole.
- `artefacts/processus_phishing_ia.png` : image du notebook restaurée, sans valeur ni visuel inventé.

## 6. Phase 5 — correction du notebook et alignement des artefacts

**Date :** 25 novembre 2026. **Périmètre :** notebook, `model.joblib`, `model_meta.json`, `app.py`, README, `docs/01`, `03`, `04`, `08`, `10`.

### 6.1 Notebook

- **82 cellules** (contre 84 avant restructuration), **exécuté de zéro, 0 erreur** via `nbclient` ; le notebook enregistré est celui qui a produit les sorties.
- Titres et numérotation nettoyés : doublons de titres supprimés, plan continu §0 → §20, annexe finale.
- **Split défini au §8, avant toute statistique** : `train = 416`, `test = 104` (`random_state=42`, stratifié). Le test n'est relu qu'au §16 et au §18.
- **EDA train seul** : heatmap (§9, 416 lignes), corrélations cible (§9), moyennes et médianes par classe (§9).
- **CV 5-fold des trois modèles déplacée avant l'évaluation test** : plus de sélection implicite sur le test.
- **Permutation importance sur `X_train, y_train`** (§19), 15 répétitions.
- Deux valeurs citées dans les markdowns sont désormais **imprimées** par le notebook : F1 macro OOF 5×5 au seuil 0,50 = **0,8082** et moyenne des 25 plis = **0,8073 ± 0,0466**.
- R² sur les probabilités du test = **0,386** (le markdown annonçait « ≈ 0,40 »).

### 6.2 Artefacts régénérés

- `model.joblib` et `artefacts/modele_phishing_ia.joblib` : tous deux réécrits par le notebook avec le **même pipeline retenu** (LR améliorée, seuils 0,21 / 0,20 / 0,88). Le fichier `artefacts/` passe ainsi de l'ancien sérialisé (2,6 Mo) au pipeline effectivement déployé (2,5 Ko) : taille et contenu sont désormais strictement identiques à `model.joblib`.
- `model_meta.json` : `Dummy` et `KNN` **supprimés** ; ajout de `f1_macro_cv_5fold_modele_retenu = 0,8151726278683105` et `f1_macro_cv_5fold_ecart_type = 0,06603735756226287`.
- `artefacts/matrice_correlation_eda.png` : extraite octet par octet de la sortie du §9 (train seul, `vlag`, 12×9), SHA-256 `5ddaa6e4c3bb234f4a6df3f2d83da4b09560308ccf684ec115c95212dd45196d`.

### 6.3 Valeurs de référence après phase 5

| Élément | Valeur |
|---|---|
| Split | 416 train / 104 test (299/117 et 75/29) |
| RF de référence, test 0,50 | accuracy 0,798 · F1 macro 0,734 · AUC 0,866 · AP 0,698 |
| LR / SVM, test 0,50 | 0,721 / 0,692 / 0,733 / 0,694 |
| CV 5-fold simple | RF 0,791 ± 0,051 · LR 0,785 ± 0,067 · SVM 0,784 ± 0,018 |
| LR améliorée, CV 5-fold | **0,8152 ± 0,0660** |
| LR améliorée, CV 5×5 | AUC 0,9092 ± 0,0031 · AP 0,8119 ± 0,0034 · F1 OOF 5×5 @0,50 0,8082 · 25 plis 0,8073 ± 0,0466 |
| Seuil | plateau 0,20–0,22, retenu **0,21** (coût min 128 à 0,20 ; 132 à 0,21) |
| OOF train (0,21) | TN 182 · FP 117 · FN 3 · TP 114 |
| Test (0,21) | TN 47 · FP 28 · FN 1 · TP 28 · F1 macro 0,712 · AUC 0,910 · AP 0,810 · Brier 0,123 · coût 33 |
| Triage 0,20/0,88 (test) | 61/104 automatisés · 1 FN · 1 FP · 43 revues |
| IC95 bootstrap | rappel [0,886 ; 1,000] · précision [0,368 ; 0,636] · fausse alerte [0,262 ; 0,481] |

### 6.4 Application et documentation

- `app.py` : `COMPARISON_MODEL` ne contient plus de lignes `Dummy`/`KNN` ; le code live de comparaison de scénarios reste inchangé. Heatmap : contrôle du nouveau SHA-256, corrélations `−0,322 / +0,285 / −0,278 / +0,244`, moyennes par classe train-only réaffichées. Textes « historique » et « 0,814 / 0,771 » supprimés.
- `README.md` : valeurs 0,8082 / 0,8073 ± 0,0466, heatmap train (416 lignes), 82 cellules, tableau des scénarios remplacé par les trois probabilités vérifiées (0,06 % / 100,00 % / 47,09 %).
- `docs/01` : statistiques descriptives recalées sur la sortie réelle (524 lignes brutes), moyennes et médianes par classe sur le train, section heatmap réécrite, `|r| ≤ 0,09` entre explicatives.
- `docs/03`, `04`, `08`, `10` : écarts historiques convertis en « corrigés », références de cellules remplacées par des renvois de section.

### 6.5 Contrôle final

- Toutes les valeurs citées dans les markdowns du notebook ont été relues contre les sorties de `/tmp/opencode/dump2.txt` (extraction source + outputs de l'ipynb).
- `python3 -m py_compile app.py` : OK.
- `git status` / `git diff` relus avant commit ; `commit` puis `push` sur la branche courante.
