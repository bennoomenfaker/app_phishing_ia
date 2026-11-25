# Plan PPTX — 15 diapositives

> **But de ce fichier.** Fournir, diapositive par diapositive, le titre, les 3 à 5 messages à l'oral,
> les **valeurs exactes** à afficher et l'**image précise** à insérer. Toutes les valeurs proviennent
> du notebook `notebook_ML_IA_confiance_numerique.ipynb` réexécuté (82 cellules, 0 erreur), de
> `model_meta.json` et de `app.py`. Aucune valeur n'est recopiée d'une version historique.

---

## 0. Règles de fabrication

| Élément | Choix |
|---|---|
| Format | 16:9, 13,333 × 7,5 pouces |
| Police | Aptos ou Calibri ; titres 24–28 pt, corps 12–14 pt, sources 9–10 pt |
| Couleurs | marine `#0F2743`, bleu `#1F5FA8`, ambre `#E8A33D`, rouge `#C0392B`, gris `#5B6B78`, fond blanc |
| Images | PNG extraits **sans redessin** dans `artefacts/pptx/` (voir §2) ; conserver les titres d'origine, ils portent le protocole |
| Règle d'or | une diapo = une idée ; les chiffres affichés sont ceux des sorties, pas des arrondis « ronds » |
| Pagination | `n/15` en bas à droite ; pied de page « IA & confiance numérique — pré-détection phishing (Master VIC, ESEN–ISCAE) » |

**Ce qu'il ne faut PAS afficher** : `0,814`, `0,771`, les scores `Dummy` / `KNN`, une heatmap
calculée sur 520 lignes, une importance par permutation calculée sur le test. Ces éléments ont été
retirés des artefacts.

---

## 1. Vue d'ensemble des 15 diapositives

| # | Titre | Image | Valeurs clés |
|---|---|---|---|
| 1 | Titre | — (fond uni) | — |
| 2 | Le phishing à l'ère de l'IA | `05_processus_ml.png` (option) | — |
| 3 | Problématique et objectif | — (schéma texte) | coût FN = 5 × FP |
| 4 | Données et variables | `01_repartition_cible.png` | 524 → 520 ; 374 / 146 ; 9 variables |
| 5 | Qualité et nettoyage | — (tableau) | 4 doublons ; 10 NA ; `date` exclue |
| 6 | EDA — distributions | `02_histogrammes.png` | âge domaine max 5 874 j |
| 7 | EDA — heatmap train | `03_heatmap_train.png` | 416 lignes ; max \|r\| explicatif 0,089 |
| 8 | EDA — signaux de la cible | `04_association_cible.png` | −0,322 / +0,285 / −0,278 / +0,244 |
| 9 | Protocole et pipeline anti-fuite | `05_processus_ml.png` | 416 / 104 ; imputation par fold |
| 10 | Modèles comparés (CV 5-fold) | `10_comparaison_metriques.png` | RF 0,791 ; LR 0,785 ; SVM 0,784 ; LR amél. 0,815 |
| 11 | Matrice de confusion du RF | `07_confusion_random_forest.png` | 67 / 8 / 13 / 16 ; coût 73 → 38 |
| 12 | Modèle retenu et seuil appris | `09_confusion_modele_retenu.png` | seuil 0,21 ; OOF 182/117/3/114 |
| 13 | Évaluation finale sur le test | `11_courbes_roc_pr.png` | 47/28/1/28 ; AUC 0,910 ; AP 0,810 |
| 14 | Importance des variables et erreurs | `12_importance_variables.png` | 0,2429 / 0,1558 / 0,1469 / 0,1012 |
| 15 | Conclusion, limites, application | — (captures app) | 61/104 ; 1 FN ; 1 FP ; 43 revues |

---

## 2. Catalogue des images (`artefacts/pptx/`)

Toutes les images sont des sorties **réelles** du notebook, extraites octet par octet.

| Fichier | Contenu | Cellule source | Usage conseillé |
|---|---|---|---|
| `01_repartition_cible.png` | Effectifs `Non` / `Oui` dans le train (299 / 117) | 24 | diapo 4 |
| `02_histogrammes.png` | Histogrammes des variables numériques (train) | 26 | diapo 6 |
| `02b_nb_liens.png` | Répartition de la cible selon `nb_liens` | 28 | diapo 6 ou 8 (option) |
| `02b_urgence_score.png` | Répartition selon `urgence_score` | 28 | diapo 6 ou 8 (option) |
| `02b_fautes_langue.png` | Répartition selon `fautes_langue` | 28 | diapo 8 (contre-intuitif) |
| `02b_expediteur_connu.png` | Répartition selon `expediteur_connu` | 28 | diapo 8 |
| `02b_piece_jointe.png` | Répartition selon `piece_jointe` | 28 | annexe (option) |
| `02b_personnalisation_score.png` | Répartition selon `personnalisation_score` | 28 | annexe (option) |
| `03_heatmap_train.png` | Heatmap Pearson + cible, **train seul 416** | 31 | diapo 7 |
| `04_association_cible.png` | Barres des corrélations avec la cible | 33 | diapo 8 |
| `05_processus_ml.png` | Schéma du processus ML (10 étapes) | 13 | diapos 2 et 9 |
| `06_confusion_regression_logistique.png` | Matrice LR de référence (test, 0,50) | 58 | annexe (option) |
| `07_confusion_random_forest.png` | Matrice RF de référence (test, 0,50) | 58 | diapo 11 |
| `08_confusion_svm.png` | Matrice SVM de référence (test, 0,50) | 58 | annexe (option) |
| `09_confusion_modele_retenu.png` | Matrice LR améliorée, test, seuil 0,21 | 65 | diapo 12 ou 13 |
| `10_comparaison_metriques.png` | Barres Accuracy / Precision / Recall / F1 | 68 | diapo 10 |
| `11_courbes_roc_pr.png` | Courbes ROC et Precision-Recall | 70 | diapo 13 |
| `12_importance_variables.png` | Permutation importance sur le **train** | 73 | diapo 14 |

`artefacts/matrice_correlation_eda.png` est **identique** à `03_heatmap_train.png` (même SHA-256
`5ddaa6e4c3bb234f4a6df3f2d83da4b09560308ccf684ec115c95212dd45196d`) : utiliser l'un ou l'autre.

> **Note.** `scripts/make_pptx.py` est un générateur **antérieur** (20 diapositives) qui pointe vers
> des noms de fichiers liés aux anciens numéros de cellules (`cell54_0.png`, `boxplots_compact.png`…)
> et ne correspond pas au découpage en 15 diapositives ci-dessous. Ce plan-ci est la référence ;
> le script n'est pas utilisé pour produire cette version.

---

## 3. Détail des diapositives

### Diapositive 1 — Titre

**Titre :** Détection de messages malveillants par apprentissage supervisé
**Sous-titre :** IA et confiance numérique — pré-détection du phishing assistée par Machine Learning
**Ligne 3 :** Master VIC — ESEN / ISCAE · données synthétiques · novembre 2026
**Image :** aucune (fond marine, filet ambre).
**Notes orales :** annoncer en 20 s le fil rouge : « partir d'un message, produire une probabilité,
la transformer en décision **avec un humain dans la boucle** ».

---

### Diapositive 2 — Le phishing à l'ère de l'IA

**Messages**
1. Le phishing est une **arnaque par message** : un attaquant se fait passer pour une banque, un collègue, un support IT.
2. Chaîne classique : **appât → pression → piège (lien / pièce jointe) → action → profit**.
3. L'IA générative supprime les anciens signaux : texte **sans fautes**, **personnalisé**, ton crédible.
4. Conséquence : la faute d'orthographe n'est plus un détecteur fiable — c'est aussi ce que montre le dataset.
**Image :** `05_processus_ml.png` en bandeau bas, ou un schéma appât → piège → action.
**Valeurs :** aucune (diapo qualitative).
**Notes :** ne pas promettre la détection parfaite ; annoncer que le projet mesure surtout la **qualité de la décision**.

---

### Diapositive 3 — Problématique et objectif

**Messages**
1. Comment **prioriser** les messages suspects sans supprimer automatiquement ?
2. Deux erreurs n'ont pas le même prix : **rater un phishing** (FN) coûte **5 fois** plus cher qu'une **fausse alerte** (FP).
3. Objectif : un score `P(Oui)` **calibré**, un seuil **appris sur le train**, et un **triage 3 zones**.
4. Le test de 104 messages n'est lu **qu'une seule fois**, à la fin.
**Valeurs à afficher :** `coût = 5 × FN + FP` ; `seuil = 0,21` ; `triage 0,20 / 0,88`.
**Notes :** expliquer que ce ratio 5:1 est une **hypothèse métier**, à valider avec les analystes.

---

### Diapositive 4 — Données et variables

**Messages**
1. Jeu **synthétique** pédagogique : **524 lignes brutes → 520 lignes uniques**.
2. Cible : `message_malveillant` — **374 `Non` (71,9 %)** / **146 `Oui` (28,1 %)**.
3. **9 variables numériques** : heure, longueur, liens, urgence, âge du domaine, fautes, expéditeur connu, pièce jointe, personnalisation.
4. La colonne `date` est **exclue** : variable calendaire sans justification métier.
**Image :** `01_repartition_cible.png` (train : 299 / 117).
**Valeurs :** 524 → 520 ; 374 / 146 ; 9 variables ; déséquilibre 2,6 : 1.
**Notes :** préciser que le déséquilibre est **modéré** et justifie le F1 macro plutôt que l'accuracy.

---

### Diapositive 5 — Qualité et nettoyage

**Messages**
1. **4 doublons exacts** supprimés (524 → 520).
2. **10 valeurs manquantes**, toutes sur `domaine_age_jours`, imputées par la **médiane**.
3. L'imputation vit **dans le pipeline** : elle est apprise sur le train de chaque fold, jamais sur le test.
4. Aucune ligne supprimée pour valeur manquante.
**Valeurs :** 524 → 520 ; 10 NA ; médiane apprise par fold.
**Notes :** insister sur l'anti-fuite : imputer avant le split serait une fuite.

---

### Diapositive 6 — EDA : distributions

**Messages**
1. `domaine_age_jours` est très asymétrique : moyenne **739,33**, médiane **516**, maximum **5 874** (524 lignes brutes).
2. Cette asymétrie justifie `log1p(âge)` dans le modèle retenu.
3. Les autres variables restent dans des plages plausibles (liens 0–5, urgence 0–10).
4. Les distributions se **chevauchent** : aucune variable ne suffit seule.
**Image :** `02_histogrammes.png` (train) ; option : `02b_nb_liens.png`.
**Valeurs :** 739,33 / 516 / 5 874 ; longueur 60–896 ; liens 0–5.
**Notes :** ne pas parler de « valeurs aberrantes » : le maximum est une donnée synthétique valide.

---

### Diapositive 7 — EDA : heatmap sur le train

**Messages**
1. Heatmap de Pearson **avec la cible**, calculée sur le **train seul (416 messages)**.
2. Entre variables explicatives, **aucune redondance** : `|r| ≤ 0,089`.
3. La cible se lit sur la dernière ligne : les signaux sont **modérés**, jamais décisifs seuls.
4. Le test (104) n'apparaît **pas** dans cette matrice.
**Image :** `03_heatmap_train.png`.
**Valeurs :** 416 lignes ; max explicatif `expediteur_connu` / `domaine_age_jours` = **+0,089**.
**Notes :** rappeler que Pearson ne capte que le linéaire ; le SVM RBF peut capter autre chose.

---

### Diapositive 8 — EDA : signaux associés à la cible

**Messages**
1. Quatre signaux dominants, tous **modérés** : âge du domaine, urgence, expéditeur inconnu, nombre de liens.
2. **`fautes_langue` ≈ 0** : résultat clé pour le thème « IA et confiance numérique ».
3. Les moyennes par classe confirment : domaine **886,66 vs 340,72** jours, urgence **4,15 vs 5,63**, liens **1,20 vs 1,83**.
4. Médianes : domaine **650 vs 234,5**, urgence **4 vs 6**, liens **1 vs 2**.
**Image :** `04_association_cible.png` ; option : `02b_expediteur_connu.png` ou `02b_fautes_langue.png`.
**Valeurs :** `domaine_age_jours −0,322` · `urgence_score +0,285` · `expediteur_connu −0,278` · `nb_liens +0,244` · `personnalisation_score +0,133` · `longueur_message −0,114` · `piece_jointe +0,060` · `heure_envoi −0,027` · `fautes_langue −0,022`.
**Notes :** ne pas surinterpréter `personnalisation_score` : corrélation faible et contre-intuitive.

---

### Diapositive 9 — Protocole et pipeline anti-fuite

**Messages**
1. Split **80 / 20 stratifié** (`random_state=42`) : **416 train / 104 test** (299/117 et 75/29).
2. Pipeline : `FeaturesPhishing → imputation médiane → StandardScaler → LogisticRegression`.
3. `FeaturesPhishing` construit `log_age`, `urg_x_inconnu`, `liens_x_inconnu` ; il n'apprend **rien** dans `fit`.
4. Imputation et standardisation sont **dans** le pipeline : ajustées par fold, jamais sur le test.
**Image :** `05_processus_ml.png`.
**Valeurs :** 416 / 104 ; 299 / 117 ; 75 / 29 ; 9 variables ; `date` exclue.
**Notes :** la diapo répond à la question jury « où est la fuite ? » : nulle part dans ce pipeline.

---

### Diapositive 10 — Modèles comparés et validation croisée

**Messages**
1. Trois références : régression logistique, Random Forest (300 arbres, `min_samples_leaf=2`), SVM RBF.
2. **CV 5-fold simple sur le train** : RF **0,791 ± 0,051**, LR **0,785 ± 0,067**, SVM **0,784 ± 0,018**.
3. LR améliorée, **même protocole** : **0,8152 ± 0,0660** — meilleur F1 macro.
4. La CV 5×5 répétée donne AUC **0,9092 ± 0,0031**, AP **0,8119 ± 0,0034**.
5. Le choix se fait sur la CV, **pas** sur le test.
**Image :** `10_comparaison_metriques.png` (attention : barres du **test**, à titre descriptif) ; préférer un tableau si l'on veut insister sur la CV.
**Valeurs test descriptives (0,50) :** RF 0,798 / 0,752 / 0,723 / 0,734 · AUC 0,866 · AP 0,698 ; LR 0,721 / 0,692 / 0,733 / 0,694 · AUC 0,832 · AP 0,656 ; SVM idem F1 · AUC 0,834 · AP 0,633.
**Notes :** ne jamais comparer directement 0,791 (CV 5-fold) et 0,8082 (OOF 5×5) : protocoles différents.

---

### Diapositive 11 — Matrice de confusion du Random Forest

**Messages**
1. Au seuil **0,50**, le RF manque **13** phishing (`FN = 13`) pour **8** fausses alertes : coût **73**.
2. Au seuil **0,30**, il n'en manque plus que **3**, mais génère **23** fausses alertes : coût **38**.
3. Ce seuil 0,30 était **posé à la main** : c'est ce que le protocole suivant corrige.
4. Le RF reste une **référence comparative**, pas le modèle déployé.
**Image :** `07_confusion_random_forest.png`.
**Valeurs :** 0,50 → `TN 67 · FP 8 · FN 13 · TP 16` (accuracy 0,798, rappel 0,552) ; 0,30 → `TN 52 · FP 23 · FN 3 · TP 26` (coût 38).
**Notes :** expliquer que le coût 5·FN+FP transforme un débat de métrique en arbitrage métier.

---

### Diapositive 12 — Modèle retenu et seuil appris

**Messages**
1. Modèle retenu : **régression logistique améliorée** (`log_age` + interactions, bruit retiré, `class_weight="balanced"`).
2. Le seuil **0,21** vient d'un **plateau de coût** en CV : `0,20–0,22` (coût min 128 à 0,20 ; 132 à 0,21).
3. Matrice **OOF** sur le train : `TN 182 · FP 117 · FN 3 · TP 114` — chaque ligne est prédite hors de son pli.
4. Sensibilité au coût : `c_FN = 3` → seuil 0,47 ; `c_FN = 10` → seuil 0,20.
**Image :** `09_confusion_modele_retenu.png` (matrice **test**) ou un tableau OOF ; ne pas confondre les deux matrices.
**Valeurs :** seuil 0,21 ; plateau 0,20–0,22 ; OOF 182/117/3/114 ; coût 132.
**Notes :** la matrice de cette diapo peut être lue comme la matrice OOF (train) ; la diapo 13 montre le test.

---

### Diapositive 13 — Évaluation finale sur le test

**Messages**
1. Test lu **une seule fois**, au seuil 0,21 : `TN 47 · FP 28 · FN 1 · TP 28`.
2. Rappel `Oui` **96,6 %**, précision `Oui` **50,0 %**, accuracy **72,1 %**, F1 macro **0,712**, coût **33**.
3. Classement indépendant du seuil : **AUC 0,910**, **AP 0,810**, Brier **0,123**.
4. À 0,50 : `58/17/5/24`, F1 **0,763**, coût **42** — moins d'alertes, mais 5 attaques manquées.
5. IC95 % bootstrap : rappel **[0,886 ; 1,000]**, précision **[0,368 ; 0,636]**, fausse alerte **[0,262 ; 0,481]**.
**Image :** `11_courbes_roc_pr.png` + `09_confusion_modele_retenu.png` (deux vignettes).
**Valeurs :** 47/28/1/28 ; 0,966 / 0,500 / 0,721 / 0,712 / 33 ; AUC 0,910 ; AP 0,810 ; Brier 0,123.
**Notes :** assumer les 28 fausses alertes : c'est le prix d'un rappel de 96,6 % sur 104 messages.

---

### Diapositive 14 — Importance des variables et analyse des erreurs

**Messages**
1. Permutation importance calculée **sur le train (416)**, 15 répétitions, sans relire le test.
2. Ordre : `domaine_age_jours` **0,2429**, `urgence_score` **0,1558**, `expediteur_connu` **0,1469**, `nb_liens` **0,1012**.
3. Puis `longueur_message` 0,0492, `personnalisation_score` 0,0438, `heure_envoi` 0,0394, `fautes_langue` 0,0202, `piece_jointe` 0,0115.
4. Importance ≠ causalité : elle mesure la dépendance du modèle, pas le risque réel.
**Image :** `12_importance_variables.png`.
**Valeurs :** les neuf valeurs ci-dessus.
**Notes :** faire le lien avec les corrélations : même tête de classement, ce qui rassure sur la cohérence.

---

### Diapositive 15 — Conclusion, limites, application

**Messages**
1. **Triage 3 zones** (0,20 / 0,88) : **61/104** messages automatisés avec seulement **1 FN** et **1 FP** ; **43** cas ambigus confiés à l'analyste.
2. Variante `0,07 / 0,98` : **0 FN / 0 FP** sur la partie automatisée, mais **30** messages automatisés et **74** revues — l'arbitrage est explicite.
3. Application Streamlit **12 pages** : EDA, heatmap, comparaison, prédiction, explication des attributs, mode présentation.
4. Scénarios vérifiés : normal **0,06 %** → `Non` / NORMAL ; phishing IA **100 %** → `Oui` / ALERTE ; à surveiller **47,09 %** → `Oui` / VIGILANCE.
5. Limites : données synthétiques, test de 104 messages, IC larges, hypothèse de coût 5:1, pas de validation temporelle.
**Image :** une capture de l'application (page 7 ou 12) ; sinon `05_processus_ml.png` en rappel.
**Valeurs :** 61/104 ; 1 FN ; 1 FP ; 43 revues ; 30 / 74 ; 12 pages ; 0,06 % / 100 % / 47,09 %.
**Notes :** terminer sur la phrase de gouvernance : « aide à la décision, validation humaine obligatoire, aucune suppression automatique ».

---

## 4. Ordre de génération conseillé

1. Créer le masque 16:9 et les styles (marine, bleu, ambre).
2. Poser les diapos 2, 3, 9, 15 en texte seul (structure narrative).
3. Insérer les images dans l'ordre : 4 → 18 (elles portent les titres et les protocoles).
4. Ajouter les tableaux de valeurs (diapos 10 à 14) : **ne pas arrondir** au-delà de ce qui est écrit ici.
5. Relire chaque chiffre contre ce fichier, puis contre le notebook.

## 5. Contrôle avant export

- [ ] Aucune occurrence de `0,814`, `0,771`, `Dummy`, `KNN`, « 520 lignes avant split ».
- [ ] La diapo 7 précise bien **train seul, 416 messages**.
- [ ] La diapo 13 distingue **matrice OOF (train)** et **matrice test**.
- [ ] Les diapos 11 et 13 ne mélangent pas seuil 0,50 et seuil 0,21.
- [ ] Les images sont celles de `artefacts/pptx/` (extraites du notebook), pas des graphiques redessinés.
- [ ] La pagination est en `n/15`.
