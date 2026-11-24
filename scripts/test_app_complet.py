from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"
at = AppTest.from_file(str(APP), default_timeout=600).run()
assert not at.exception, [str(e.value) for e in at.exception]

PAGES = ["1. Contexte & Problématique", "2. Processus ML (pas à pas)",
         "3. Prédiction / Verdict", "4. Notebook", "5. Soutenance (12 points)",
         "6. Présentation (soutenance)"]


def goto(page):
    global at
    r = [w for w in at.radio if w.label == 'Navigation'][0]
    r.set_value(page)
    at = at.run()
    assert not at.exception, f'{page}: ' + str([str(e.value) for e in at.exception])


def textes():
    out = []
    for kind in ('markdown', 'caption', 'text', 'info', 'warning', 'error', 'success'):
        for el in at.get(kind):
            out.append(str(el.value))
    return '\n'.join(out)


for p in PAGES:
    goto(p)
    print('OK page :', p)

# --- page 3 : trois verdicts distincts ---
goto('3. Prédiction / Verdict')
t3 = textes()
assert 'Oui — malveillant probable' in t3
assert 'Non — légitime' in t3
assert 'VIGILANCE' in t3 and 'ALERTE' in t3 and 'NORMAL' in t3
print('page 3 : 3 verdicts distincts OK')

[b for b in at.button if 'Charger' in b.label][2].click()
at = at.run()
[b for b in at.button if 'Prédire' in b.label][0].click()
at = at.run()
assert not at.exception, [str(e.value) for e in at.exception]

tables = {}
for df in at.dataframe:
    v = df.value
    if hasattr(v, 'columns'):
        tables[tuple(v.columns)] = v

comparaison = [v for k, v in tables.items() if 'Zone de triage' in k]
assert comparaison, list(tables)
comp = comparaison[0]
print('\n--- comparaison des modèles ---')
print(comp.to_string(index=False))
assert set(comp['Classe (seuil 0.21)']) <= {'Oui — malveillant', 'Non — légitime'}
assert 'À vérifier' not in set(comp['Classe (seuil 0.21)'])
assert comp['Zone de triage'].str.contains('VIGILANCE').any()
assert comp['Zone de triage'].str.contains('NORMAL').any()

seuils = [v for k, v in tables.items() if 'Seuil' in k]
assert seuils, list(tables)
print('\n--- seuils test ---')
print(seuils[0].to_string(index=False))

triage = [v for k, v in tables.items() if 'Automatisés' in k]
assert triage, list(tables)
print('\n--- triage test ---')
print(triage[0].to_string(index=False))
assert (triage[0]['FN (auto)'] == 0).any() and (triage[0]['FP (auto)'] == 0).any()
print('\npage 3 : tableaux FN/FP et triage zéro erreur OK')

# --- page 6 : présentation markdown ---
goto('6. Présentation (soutenance)')
t6 = textes()
for marqueur in ('1. Page de garde', '6. Architecture globale', '14. Résultats expérimentaux',
                 '18. Conclusion', '19. Annexe A', '20. Annexe B',
                 'personnalisation_score', 'Triage 0,07 / 0,98',
                 'AUC', 'R²', 'MAE', 'RMSE', 'MSE', 'Accuracy',
                 'Merci pour votre attention'):
    assert marqueur in t6, marqueur
assert 'slide' not in t6.lower()
print('page 6 : 18 sections + glossaire des métriques OK')

# --- page 2 : matrice de corrélation avec la cible ---
goto('2. Processus ML (pas à pas)')
cols2 = [tuple(df.value.columns) for df in at.dataframe if hasattr(df.value, 'columns')]
assert any('corrélation_avec_cible' in c for c in cols2), cols2
t2 = textes()
assert 'La cible est dans la matrice' in t2
print('page 2 : matrice de corrélation avec la cible OK')

# --- page 5 : R² / MAE / MSE ---
goto('5. Soutenance (12 points)')
t5 = textes()
for m in ('R²', 'MAE', 'MSE', 'RMSE', 'Accuracy'):
    assert m in t5, m
print('page 5 : métriques OK')
print('\nTOUTES LES PAGES OK')
