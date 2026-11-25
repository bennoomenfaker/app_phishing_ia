# 01 — Jeu de données et analyse exploratoire (EDA)

> **Périmètre et statut des données.** Le jeu de données utilisé dans `notebook_ML_IA_confiance_numerique.ipynb` est **synthétique et pédagogique**. Il ne contient aucune donnée personnelle et n'a fait l'objet d'aucune validation sur de vraies campagnes de phishing. Les résultats présentés dans cette série de documents sont donc des résultats d'exercice, **pas une mesure de performance opérationnelle**.

> **Source de vérité.** Notebook `notebook_ML_IA_confiance_numerique.ipynb`, `model.joblib`, `model_meta.json` et le CSV `dataset_phishing_ia - dataset_phishing_ia.csv`. Toute valeur non disponible dans ces artefacts est explicitement signalée comme telle.

---

## 1. Provenance, intégrité et nettoyage

| Élément | Valeur vérifiée |
|---|---|
| Fichier source | `dataset_phishing_ia - dataset_phishing_ia.csv` |
| Empreinte d'intégrité | SHA-256, préfixe `9383a1b70165` |
| Lignes brutes | 524 |
| Doublons exacts supprimés | 4 |
| Lignes uniques retenues | 520 |
| Structure | 1 colonne `date` + 9 variables numériques + 1 cible `message_malveillant` |
| Variables catégorielles | Aucune |

Le nettoyage s'est limité à la suppression de **4 doublons exacts**. Aucune autre règle de nettoyage (bornage, correction de valeurs aberrantes, suppression de lignes) n'est documentée dans les artefacts : elle est donc réputée **non disponible dans les artefacts**.

La conservation des doublons aurait artificiellement répété certaines observations dans l'entraînement et dans le test, faussant à la fois les statistiques descriptives et l'estimation de performance. Leur retrait en amont de toute analyse est une condition minimale de rigueur.

---

## 2. Dictionnaire des variables

Les « définitions » ci-dessous décrivent le **libellé** et l'échelle observée. Les règles exactes de calcul des scores (urgence, personnalisation, fautes de langue) ne sont **pas disponibles dans les artefacts**.

| Variable | Libellé / contenu | Échelle observée (min – max) | Rôle dans le projet |
|---|---|---|---|
| `date` | Date associée au message | Non disponible dans les artefacts (variable calendaire) | **Exploration uniquement** ; exclue du modèle |
| `heure_envoi` | Heure d'envoi dans la journée | 0 – 23 | Explicative en EDA ; **retirée du modèle retenu** |
| `longueur_message` | Longueur du message | 60 – 896 | Explicative en EDA ; **retirée du modèle retenu** |
| `nb_liens` | Nombre de liens contenus dans le message | 0 – 5 | Explicative ; **conservée** dans le modèle retenu |
| `urgence_score` | Score d'urgence du message | 0 – 10 | Explicative ; **conservée** dans le modèle retenu |
| `domaine_age_jours` | Âge du domaine, en jours | 1 – 5 874 | Explicative ; **conservée** (transformée `log1p`) |
| `fautes_langue` | Nombre de fautes de langue | 0 – 6 | Explicative en EDA ; **retirée du modèle retenu** |
| `expediteur_connu` | Indicateur binaire : expéditeur connu (1) / non connu (0) | 0 – 1 | Explicative ; **conservée** dans le modèle retenu |
| `piece_jointe` | Indicateur binaire : présence d'une pièce jointe | 0 – 1 | Explicative ; **conservée** dans le modèle retenu |
| `personnalisation_score` | Score de personnalisation du message | 0 – 10 | Explicative ; **conservée** dans le modèle retenu |
| `message_malveillant` | Cible binaire : `Non` = légitime, `Oui` = malveillant | `Non` / `Oui` | **Variable cible** ; jamais incluse dans `X` |

### Pourquoi `date` est exclue

`date` est une variable calendaire : sa présence dans un modèle de détection introduirait une dépendance à la période d'observation sans justification métier documentée (tendance saisonnière, effet de campagne, dérive temporelle). Elle est donc réservée à l'exploration et écartée de la matrice de caractéristiques. Ce choix est reproductible et cohérent avec la logique de préprocessing décrite dans le document `02`.

---

## 3. Valeurs manquantes et déséquilibre de classe

### Valeurs manquantes

| Variable | Nombre de valeurs manquantes (sur 520) |
|---|---|
| `domaine_age_jours` | 10 |
| Toutes les autres variables | 0 |

Les 10 valeurs manquantes concernent donc **une seule variable**. Le traitement retenu n'est pas une suppression de lignes mais une **imputation par la médiane intégrée au pipeline**, apprise sur le train de chaque fold : ce point est détaillé dans `02_preprocessing_and_pipeline.md`.

### Distribution de la cible

| Classe | Effectif | Proportion |
|---|---:|---:|
| `Non` (légitime) | 374 | 71,9 % |
| `Oui` (malveillant) | 146 | 28,1 % |
| **Total** | **520** | **100 %** |

Le déséquilibre est **modéré** (ratio approximatif de 2,6 pour 1). Il n'impose pas un rééchantillonnage, mais il rend l'*accuracy* trompeuse : prédire systématiquement `Non` atteindrait 71,9 % d'accuracy sans détecter aucun message malveillant. C'est une des raisons du suivi du F1 macro, de la ROC-AUC et de l'AP.

---

## 4. Statistiques descriptives (524 lignes brutes, avant doublons)

Les valeurs ci-dessous sont celles de la cellule 11 du notebook (`df_brut.describe()`), donc sur
les **524 lignes brutes** du CSV. La déduplication en 520 lignes intervient juste après.

| Variable | Min | Max | Moyenne | Médiane | Écart-type |
|---|---:|---:|---:|---:|---:|
| `heure_envoi` | 0 | 23 | 12,24 | 13,0 | 6,89 |
| `longueur_message` | 60 | 896 | 413,23 | 423,0 | 162,77 |
| `nb_liens` | 0 | 5 | 1,39 | 1,0 | 1,17 |
| `urgence_score` | 0 | 10 | 4,52 | 4,0 | 2,37 |
| `domaine_age_jours` | 1 | 5 874 | 739,33 | 516,0 | 761,68 |
| `fautes_langue` | 0 | 6 | 2,02 | 2,0 | 1,39 |
| `expediteur_connu` | 0 | 1 | 0,44 | 0,0 | 0,50 |
| `piece_jointe` | 0 | 1 | 0,23 | 0,0 | 0,42 |
| `personnalisation_score` | 0 | 10 | 4,98 | 5,0 | 2,55 |

`domaine_age_jours` ne compte que **514 valeurs non manquantes** : les 10 valeurs manquantes du jeu
sont toutes sur cette variable.

**Lectures utiles :**

- `domaine_age_jours` est très dispersée : l'écart-type (761,68) est de l'ordre de la moyenne
  (739,33) et le maximum (5 874) est très éloigné de la médiane (516,0). Cette asymétrie justifie
  la transformation logarithmique `log1p` appliquée dans le modèle retenu.
- `expediteur_connu` et `piece_jointe` sont des indicatrices 0/1 : leur moyenne s'interprète
  directement comme une proportion (0,44 et 0,23).
- Les variables `urgence_score` et `personnalisation_score` ont des moyennes proches de 4,5 et 5
  sur une échelle 0–10 : pas de saturation apparente.

---

## 5. EDA : formes, dispersion et comparaison par classe

Les graphiques du notebook (histogrammes, comparaisons par classe et tableau des médianes) ont les objectifs suivants :

- **Histogrammes** : repérer l'asymétrie, les pics et les bornes artificielles. L'asymétrie marquée de `domaine_age_jours` est le cas le plus net.
- **Médianes et quartiles par classe** : visualiser la dispersion et les valeurs extrêmes sans être trompé par la moyenne. Le maximum de `domaine_age_jours` (5 874) ressort comme une valeur très éloignée du corps de distribution ; il s'agit d'une donnée synthétique et aucune règle de traitement n'est documentée. Les quartiles du train montrent `Non` : 325–1 175 jours, `Oui` : 72–504 jours.
- **Comparaison par classe** : vérifier si les distributions se décalent entre messages légitimes et malveillants, avant de traduire ce décalage en corrélation.

### Moyennes par classe — train seul (416 messages)

Les valeurs ci-dessous sont celles de la cellule 36 du notebook, calculées sur le **train seul**.

| Variable | Moyenne `Non` | Moyenne `Oui` | Écart observé (Oui − Non) |
|---|---:|---:|---:|
| `heure_envoi` | 12,31 | 11,89 | −0,42 |
| `longueur_message` | 424,32 | 382,06 | −42,26 |
| `nb_liens` | 1,20 | 1,83 | +0,63 |
| `urgence_score` | 4,15 | 5,63 | +1,48 |
| `domaine_age_jours` | 886,66 | 340,72 | −545,94 |
| `fautes_langue` | 2,04 | 1,97 | −0,07 |
| `expediteur_connu` | 0,54 | 0,23 | −0,31 |
| `piece_jointe` | 0,22 | 0,27 | +0,05 |
| `personnalisation_score` | 4,81 | 5,58 | +0,77 |

Les écarts les plus marqués concernent `domaine_age_jours`, `urgence_score`, `expediteur_connu` et `nb_liens` — c'est-à-dire les mêmes variables qui ressortent en tête des corrélations avec la cible. Cette cohérence entre EDA visuelle, comparaison de moyennes et corrélation est un bon signe de stabilité du signal exploratoire. À l'inverse, les écarts quasi nuls de `fautes_langue` et `heure_envoi` expliquent leur retrait du modèle amélioré.

Les **médianes** par classe (mêmes 416 lignes) confirment la lecture : `domaine_age_jours` 650,0 (`Non`) contre 234,5 (`Oui`), `urgence_score` 4,0 contre 6,0, `nb_liens` 1,0 contre 2,0, `expediteur_connu` 1,0 contre 0,0, tandis que `fautes_langue` reste à 2,0 dans les deux classes.

---

## 6. Corrélations avec la cible (version à privilégier : train uniquement)

Les coefficients ci-dessous sont les **corrélations de Pearson calculées sur le seul jeu d'entraînement (416 lignes, après split stratifié)**. Elles sont la version de référence pour ce document.

La cible étant binaire, il s'agit techniquement d'une **corrélation point-bisérielle**, cas particulier de Pearson entre une variable continue et une variable binaire.

| Variable | Corrélation avec la cible (train, n = 416) | Interprétation métier prudente |
|---|---:|---|
| `domaine_age_jours` | −0,322 | Signal le plus fort en magnitude : les domaines jeunes sont associés à plus de messages malveillants. Cohérent avec l'idée de domains éphémères, mais à confirmer sur données réelles. |
| `urgence_score` | +0,285 | Plus le ton est urgent, plus la probabilité de malveillance est élevée : pression temporelle classique des campagnes. |
| `expediteur_connu` | −0,278 | Un expéditeur connu est associé à moins de malveillance ; son absence constitue un signal de risque. |
| `nb_liens` | +0,244 | La multiplication des liens accompagne le risque : chaque lien est un point de clic potentiel. |
| `personnalisation_score` | +0,133 | Lien faible et positif, contre-intuitif à première vue. À ne pas sur-interpréter : Pearson ne capte pas d'éventuel effet non linéaire, et le jeu est synthétique. |
| `longueur_message` | −0,114 | Signal faible : les messages malveillants sont en moyenne un peu plus courts (382,06 contre 424,32 sur le train). |
| `piece_jointe` | +0,060 | Très faible signal ; la présence d'une pièce jointe est presque indépendante de la cible dans ce jeu. |
| `heure_envoi` | −0,027 | Pratiquement nul : l'heure d'envoi n'apporte pas d'information linéaire exploitable ici. |
| `fautes_langue` | −0,022 | Pratiquement nul, malgré l'intuition fréquente sur les fautes dans les phishing : l'intuition n'est pas confirmée par ce jeu synthétique. |

### Corrélations entre variables explicatives

Dans le notebook, les corrélations entre explicatives sont **toutes faibles (`|r| ≤ 0,09` sur le train)**. La plus forte est `expediteur_connu` / `domaine_age_jours` (**+0,089**), suivie de `urgence_score` / `expediteur_connu` (**+0,069**) et `piece_jointe` / `expediteur_connu` (**−0,067**). Il n'y a donc **pas de multicolinéarité préoccupante** entre variables brutes. Les interactions construites ensuite dans le modèle (`urgence_score × (1 − expediteur_connu)` et `nb_liens × (1 − expediteur_connu)`) introduisent des dépendances algébriques avec leurs facteurs par construction ; elles sont traitées dans le document `02`.

### Heatmap et corrélations : un seul périmètre, le train

La heatmap du notebook (cellule 31) est calculée sur **`df_train_eda`, soit 416 messages**, avec le
même split stratifié (`random_state=42`) que le reste du projet. Le test (104 messages) n'est ni
affiché ni utilisé dans l'EDA.

- **Pourquoi c'est important** : une heatmap calculée sur le jeu complet « verrait » les lignes
  d'évaluation et pourrait orienter le choix des variables à partir du test. Ce n'est plus le cas.
- **Cohérence** : le tableau de corrélations ci-dessus, le classement de la cellule 33 et la heatmap
  de la cellule 31 portent tous sur les mêmes 416 lignes. Un seul protocole, donc des chiffres
  directement comparables.
- **Affichage dans l'application** : les pages 2 et 3 affichent la **heatmap exacte du notebook**
  (image extraite sans redessin dans `artefacts/matrice_correlation_eda.png`, SHA-256
  `5ddaa6e4c3bb234f4a6df3f2d83da4b09560308ccf684ec115c95212dd45196d`).

---

## 7. Limites de l'EDA

1. **Jeu synthétique et pédagogique** : les relations observées sont celles d'un générateur de données, pas celles d'une menace réelle. Aucune validation sur de vraies campagnes n'a été effectuée.
2. **Corrélation ≠ causalité** : une corrélation négative entre `domaine_age_jours` et la cible ne signifie pas qu'un domaine jeune *cause* la malveillance. Elle peut refléter une variable commune non observée.
3. **Pearson ne capte que le linéaire** : une relation non monotone ou non linéaire peut passer inaperçue (coefficient proche de 0 malgré un signal réel). C'est une limite directe pour `fautes_langue` et `personnalisation_score`.
4. **Corrélation point-bisérielle** : avec une cible binaire, le coefficient dépend de la proportion de chaque classe ; il n'est pas directement comparable à une corrélation calculée sur une autre population déséquilibrée autrement.
5. **Taille modérée** : 520 lignes uniques, 416 en train. Les coefficients de corrélation et les moyennes par classe ont donc une incertitude non négligeable.
6. **Valeurs manquantes** : 10 observations de `domaine_age_jours` sont imputées ; l'EDA descriptive et l'EDA sur train doivent garder cette information visible.
7. **Déséquilibre** : 71,9 % de `Non` ; toute lecture globale doit être replacée dans ce contexte (voir l'*accuracy* constante à 71,9 %).

---

## 8. Synthèse

Le jeu contient 520 messages uniques, majoritairement légitimes (71,9 %), décrits par 9 variables numériques et une date non utilisée en modèle. Le signal exploratoire est porté principalement par l'âge du domaine, le score d'urgence, la connaissance de l'expéditeur et le nombre de liens. La heatmap, les corrélations et les moyennes par classe sont toutes calculées sur le **train (416 lignes)**, conformément à la règle anti-fuite : le test n'est lu qu'au §18 du notebook. L'ensemble reste un exercice pédagogique sur données synthétiques, sans portée opérationnelle.
