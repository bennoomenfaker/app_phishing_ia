# -*- coding: utf-8 -*-
"""Génère la présentation PowerPoint du projet Phishing IA à partir des sorties réelles du notebook."""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

BASE = Path(__file__).resolve().parents[1]
IMG = BASE / 'artefacts' / 'pptx'
OUT = BASE / 'Presentation_Projet_Phishing_IA.pptx'

# Charte inspirée de la présentation VIC de référence : fond blanc, titres
# bleu marine, cartes bleues / gris clair, accent ambre.
GREEN = RGBColor(0x0F, 0x27, 0x43)
GREEN2 = RGBColor(0x1F, 0x5F, 0xA8)
TEAL = RGBColor(0x3E, 0x7C, 0xB1)
LIGHT = RGBColor(0xF1, 0xF5, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x1F, 0x29, 0x33)
GRAY = RGBColor(0x5B, 0x6B, 0x78)
AMBER = RGBColor(0xE8, 0xA3, 0x3D)
RED = RGBColor(0xC0, 0x39, 0x2B)
BORDER = RGBColor(0xD7, 0xE0, 0xEA)
LIGHTBLUE = RGBColor(0xB9, 0xD3, 0xEE)

prs = Presentation()
prs.slide_width = Inches(13.333333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333333, 7.5
N = 18


def rect(slide, x, y, w, h, fill, line=None, radius=False, line_w=1.0):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    return shp


def textbox(slide, x, y, w, h, text, size=13, color=DARK, bold=False,
            align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, italic=False,
            font='Aptos', margin=0.02, line_spacing=1.05):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    lines = text if isinstance(text, (list, tuple)) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = str(line)
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(4)
        for r in p.runs:
            r.font.name = font
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color
    return box


def bullets(slide, x, y, w, h, items, size=12.5, color=DARK, gap=6, bullet='• '):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.02)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = bullet + item
        p.space_after = Pt(gap)
        p.line_spacing = 1.06
        for r in p.runs:
            r.font.name = 'Aptos'
            r.font.size = Pt(size)
            r.font.color.rgb = color
    return box


def base_slide(idx, kicker, title):
    """Diapositive claire : titre bleu marine à gauche, filet d'accent, pied de page."""
    slide = prs.slides.add_slide(BLANK)
    rect(slide, 0, 0, SW, SH, WHITE)
    rect(slide, 0.55, 0.24, 0.07, 0.66, TEAL)
    textbox(slide, 0.78, 0.12, 11.6, 0.24, kicker.upper(), 9.5, TEAL, True)
    textbox(slide, 0.78, 0.36, 11.9, 0.56, title, 24, GREEN, True)
    rect(slide, 0.55, 7.08, 12.23, 0.012, BORDER)
    textbox(slide, 0.55, 7.13, 8.0, 0.22, 'IA & confiance numérique — pré-détection phishing (Master VIC, ESEN–ISCAE)',
            8.5, GRAY)
    textbox(slide, 11.9, 7.13, 0.9, 0.22, f'{idx:02d}/{N}', 8.5, GRAY, align=PP_ALIGN.RIGHT)
    return slide


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def card(slide, x, y, w, h, title, body, fill=LIGHT, accent=TEAL, title_size=13, body_size=11):
    rect(slide, x, y, w, h, fill, BORDER, radius=True)
    rect(slide, x, y, 0.075, h, accent)
    textbox(slide, x + 0.2, y + 0.12, w - 0.35, 0.34, title, title_size, GREEN, True)
    textbox(slide, x + 0.2, y + 0.50, w - 0.35, h - 0.62, body, body_size, DARK)


def table(slide, x, y, w, h, headers, rows, widths=None, font=10, header_font=10,
          first_col_bold=False):
    shp = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(x), Inches(y),
                                 Inches(w), Inches(h))
    tbl = shp.table
    if widths:
        total = sum(widths)
        for j, cw in enumerate(widths):
            tbl.columns[j].width = Inches(w * cw / total)
    for j, head in enumerate(headers):
        c = tbl.cell(0, j)
        c.fill.solid()
        c.fill.fore_color.rgb = GREEN
        c.text = str(head)
        c.margin_left = c.margin_right = Inches(0.05)
        c.margin_top = c.margin_bottom = Inches(0.03)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        for p in c.text_frame.paragraphs:
            p.alignment = PP_ALIGN.LEFT
            for r in p.runs:
                r.font.name = 'Aptos'
                r.font.size = Pt(header_font)
                r.font.bold = True
                r.font.color.rgb = WHITE
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if i % 2 else LIGHT
            c.text = str(val)
            c.margin_left = c.margin_right = Inches(0.05)
            c.margin_top = c.margin_bottom = Inches(0.025)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            for p in c.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                for r in p.runs:
                    r.font.name = 'Aptos'
                    r.font.size = Pt(font)
                    r.font.bold = first_col_bold and j == 0
                    r.font.color.rgb = DARK
    tbl.rows[0].height = Inches(h / (len(rows) + 1))
    for i in range(1, len(rows) + 1):
        tbl.rows[i].height = Inches(h / (len(rows) + 1))
    return tbl


def image_fit(slide, path, x, y, w, h):
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    slide.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2),
                             Inches(pw), Inches(ph))


def panel(slide, x, y, w, h, path, title, legend, interpretation, conclusion,
          img_ratio=0.60, cap_size=9):
    rect(slide, x, y, w, h, WHITE, BORDER, radius=True)
    textbox(slide, x + 0.12, y + 0.07, w - 0.24, 0.28, title, 11, GREEN2, True)
    ih = h * img_ratio
    image_fit(slide, path, x + 0.10, y + 0.36, w - 0.20, ih)
    cy = y + 0.40 + ih
    textbox(slide, x + 0.12, cy, w - 0.24, h - (cy - y) - 0.08,
            [f'Légende : {legend}',
             f'Lecture : {interpretation}',
             f'Conclusion : {conclusion}'], cap_size, DARK)


# ---------------------------------------------------------------------------
# 1 — Page de garde
# ---------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, GREEN)
rect(s, 0, 0, 0.28, SH, TEAL)
rect(s, 0.85, 1.15, 1.6, 0.06, AMBER)
textbox(s, 0.85, 1.45, 11.6, 1.9,
        'IA et confiance numérique : mise en place d\'une approche de\n'
        'pré-détection des messages malveillants (phishing)\n'
        'assistée par le Machine Learning', 27, WHITE, True, line_spacing=1.12)
textbox(s, 0.85, 3.62, 11.4, 0.5,
        'Pré-détection des messages potentiellement malveillants par classification binaire supervisée',
        16, LIGHTBLUE)
textbox(s, 0.85, 4.30, 11.4, 0.4, 'Master Veille et Intelligence Compétitive (VIC) — ESEN–ISCAE',
        14, WHITE, True)
rect(s, 0.85, 5.05, 11.55, 0.9, GREEN2, RGBColor(0x2A, 0x7A, 0x62), radius=True)
textbox(s, 1.05, 5.20, 11.1, 0.62,
        'Membres de l\'équipe, encadrant et année universitaire : non renseignés dans le notebook '
        '— à compléter avant la soutenance.\nTous les chiffres de cette présentation proviennent du notebook exécuté du 23 novembre 2026.',
        10.5, WHITE)
textbox(s, 0.85, 6.75, 11.5, 0.3,
        'Présentation conforme au notebook réellement exécuté — aucune métrique inventée',
        10, LIGHTBLUE, italic=True)
notes(s, """À dire : présenter le projet comme une aide à la décision, pas comme un filtre automatique.\n"
"Pourquoi : le jury attend une démarche de veille, pas un produit de sécurité certifié.\n"
"Questions possibles : « Qui a fait le projet ? » → les informations d'équipe ne figurent pas dans le notebook fourni ; elles seront ajoutées sur la page de garde avant soutenance.""")

# ---------------------------------------------------------------------------
# 2 — Contexte
# ---------------------------------------------------------------------------
s = base_slide(2, '01 — Cadrage', 'Contexte général')
card(s, 0.55, 1.35, 5.95, 1.85, 'Phishing : un risque massif et banalisé',
     'Courriels, SMS, messageries et réseaux sociaux imitent une source de confiance pour obtenir '
     'des identifiants, un paiement ou l\'ouverture d\'une pièce jointe.')
card(s, 6.80, 1.35, 5.95, 1.85, 'L\'IA générative change les signaux',
     'CISA souligne qu\'une faute de frappe n\'est plus un signe fiable : les messages générés '
     'peuvent avoir une grammaire parfaite et être personnalisés à grande échelle.')
card(s, 0.55, 3.45, 5.95, 1.85, 'Risques concrets',
     'Pour l\'individu : vol d\'identité et perte financière. Pour l\'organisation : compromission '
     'du SI, fuite de données, interruption d\'activité et atteinte à la réputation.')
card(s, 6.80, 3.45, 5.95, 1.85, 'Veille stratégique et confiance numérique',
     'Détecter tôt les signaux faibles, documenter les limites du modèle et garder un humain '
     'dans la boucle renforce la confiance dans les outils d\'aide à la décision.')
rect(s, 0.55, 5.60, 12.20, 0.95, LIGHT, BORDER, radius=True)
textbox(s, 0.75, 5.76, 11.8, 0.65,
        'Message clé — notre classifieur ne lit pas le texte brut : il exploite 9 signaux structurés '
        'déjà extraits du message (urgence, liens, âge du domaine, expéditeur, etc.). Il s\'agit d\'une '
        'pré-détection assistée, jamais d\'une preuve d\'authenticité.',
        11, GREEN2, True)
textbox(s, 0.55, 6.70, 12.2, 0.3,
        'Sources publiques : CISA, Recognize and Report Phishing ; CISA/NSA/FBI/MS-ISAC, Phishing Guidance (2023) ; '
        'Centre canadien de cybersécurité, ITSAP.00.101.', 8.5, GRAY)
notes(s, """À dire : le phishing reste un vecteur d'entrée majeur ; l'IA générative rend l'écriture soignée, donc l'ancien réflexe « chercher les fautes » ne suffit plus.\n"
"Pourquoi ce choix : notre jeu de données encode justement des signaux comportementaux (urgence, domaine jeune, expéditeur inconnu) plutôt que du texte.\n"
"Lecture : ne pas présenter le modèle comme un antivirus.\n"
"Question jury : « Le modèle analyse-t-il le contenu du mail ? » → Non, il travaille sur 9 variables numériques extraites en amont ; c'est une limite assumée (slide 17).""")

# ---------------------------------------------------------------------------
# 3 — Problématique et objectifs
# ---------------------------------------------------------------------------
s = base_slide(3, '01 — Cadrage', 'Problématique et objectifs')
card(s, 0.55, 1.35, 6.0, 2.25, 'Problématique',
     '« Comment exploiter les caractéristiques d\'un message numérique pour identifier '
     'automatiquement les messages potentiellement malveillants et assister la détection du phishing ? »',
     fill=GREEN2, accent=AMBER, body_size=13, title_size=14)
# texte blanc sur la carte problématique
s.shapes[-1].text_frame.paragraphs[0].runs[0].font.color.rgb = WHITE
card(s, 6.80, 1.35, 5.95, 2.25, 'Objectif général',
     'Construire et évaluer un classifieur binaire reproductible, capable d\'estimer une probabilité '
     'de malveillance et de proposer un triage explicable à un analyste.')
card(s, 0.55, 3.85, 7.45, 2.55, 'Objectifs spécifiques',
     '1. Auditer et nettoyer un jeu local de 524 messages.\n'
     '2. Comparer plusieurs algorithmes sur un split stratifié 80/20.\n'
     '3. Apprendre le seuil de décision sur le train seul (coût 5·FN + FP).\n'
     '4. Publier les matrices TP/TN/FP/FN et les intervalles de confiance.\n'
     '5. Intégrer le modèle dans une application Streamlit auditable.')
card(s, 8.25, 3.85, 4.50, 2.55, 'Garde-fou métier',
     'Aucun blocage automatique :\n'
     '• zone verte → message traité comme normal ;\n'
     '• zone orange → revue humaine ;\n'
     '• zone rouge → alerte prioritaire, toujours confirmée par une personne.',
     accent=RED)
notes(s, """À dire : reformuler la problématique avec les mots du jury : « prédire un risque à partir de signaux », pas « deviner le contenu ».\n"
"Pourquoi : le seuil appris et le triage répondent au coût métier asymétrique (un phishing manqué coûte plus cher qu'une fausse alerte).\n"
"Lecture : les objectifs 3 et 4 sont ceux qui distinguent cette version d'un notebook de démonstration.\n"
"Question jury : « Pourquoi ne pas bloquer automatiquement ? » → 28 fausses alertes sur 104 messages : un blocage automatique pénaliserait les utilisateurs ; la décision finale reste humaine.""")
# correction couleur du titre de la carte problématique (texte blanc sur fond vert)
for shp in s.shapes:
    if hasattr(shp, 'text') and shp.text.startswith('Problématique'):
        for p in shp.text_frame.paragraphs:
            for r in p.runs:
                r.font.color.rgb = WHITE

# ---------------------------------------------------------------------------
# 4 — Solutions existantes
# ---------------------------------------------------------------------------
s = base_slide(4, '01 — Cadrage', 'Solutions existantes et limites')
table(s, 0.55, 1.35, 8.65, 4.75,
      ['Approche', 'Principe', 'Limite documentée'],
      [['Filtres anti-spam', 'Règles, réputation d\'expéditeur, mots-clés',
        'Contournables ; le texte généré par IA ne contient plus les fautes classiques.'],
       ['Listes de blocage', 'Domaines / URL / IP connus comme malveillants',
        'Réactives : un domaine tout juste créé échappe à la liste.'],
       ['Analyse d\'URL / domaine', 'Âge du domaine, WHOIS, détours de lien',
        'Signal utile mais insuffisant seul (un domaine légitime peut être compromis).'],
       ['Machine Learning tabulaire', 'Apprend des combinaisons de signaux',
        'Dépend du jeu d\'entraînement, du seuil et de la qualité des signaux extraits.']],
      widths=[2.0, 3.0, 3.65], font=9.5)
card(s, 9.45, 1.35, 3.30, 4.75, 'Repères bibliographiques',
     '• CISA — Recognize and Report Phishing\n'
     '(urgences, liens raccourcis, pièges variés)\n\n'
     '• CISA / NSA / FBI / MS-ISAC — Phishing Guidance: Stopping the Attack Cycle at Phase One (2023)\n\n'
     '• Centre canadien de cybersécurité — ITSAP.00.101 : IA et hameçonnage\n\n'
     'Ces références décrivent le risque ; elles ne valident pas notre modèle.',
     body_size=9.5)
textbox(s, 0.55, 6.25, 12.2, 0.55,
        'Distinction importante : les limites ci-dessus sont documentées dans les sources publiques ; '
        'les performances de notre modèle, elles, sont calculées sur notre jeu local ( slides 14–17).',
        10, GRAY, italic=True)
notes(s, """À dire : positionner notre travail comme un complément des filtres existants, pas comme un remplacement.\n"
"Pourquoi : le dataset est local et synthétique ; nous ne revendiquons aucune performance industrielle.\n"
"Question jury : « Avez-vous comparé à une solution commerciale ? » → Non, hors périmètre : le comparateur retenu est la baseline majoritaire et les 3 algorithmes du notebook.""")
# ---------------------------------------------------------------------------
# 5 — Approche retenue
# ---------------------------------------------------------------------------
s = base_slide(5, '02 — Méthode', 'Approche retenue et valeur ajoutée')
card(s, 0.55, 1.35, 6.05, 4.85, 'Classification binaire supervisée',
     '• Classe Non : message légitime (374 cas, 71,92 %).\n'
     '• Classe Oui : message malveillant (146 cas, 28,08 %).\n'
     '• 9 variables explicatives numériques, date et semaine exclues.\n'
     '• Pipelines identiques : imputation médiane → standardisation → modèle.\n'
     '• Comparaison de 3 algorithmes, puis amélioration de la régression logistique.\n'
     '• Seuil 0,21 et triage 0,20 / 0,88 appris sur le train.\n'
     '• Sortie : probabilité + verdict + examen humain des cas ambigus.',
     body_size=12)
card(s, 6.85, 1.35, 5.90, 3.15, 'Ce que la solution apporte',
     '• Un score reproductible (seed 42, notebook fourni).\n'
     '• Une décision calibrée et expliquée (AUC, AP, Brier, permutation).\n'
     '• Une réduction de la charge analyste : 61 messages sur 104 traités automatiquement.',
     body_size=12)
card(s, 6.85, 4.75, 5.90, 1.45, 'Ce que la solution ne fait pas',
     'Expérimentale : elle ne remplace ni une passerelle mail, ni un EDR, ni l\'analyse humaine. '
     'Aucun message n\'est bloqué automatiquement.', accent=AMBER, body_size=11)
notes(s, """À dire : montrer le compromis rappel/précision et le triage comme la vraie valeur ajoutée.\n"
"Pourquoi : une accuracy de 72 % est déjà obtenue en prédisant toujours « Non », donc la mesure doit être F1 macro + rappel Oui.\n"
"Question jury : « Pourquoi trois verdicts et pas deux ? » → la zone orange réduit le risque de faux négatifs tout en évitant de noyer l'analyste sous les fausses alertes.""")
# ---------------------------------------------------------------------------
# 6 — Architecture
# ---------------------------------------------------------------------------
s = base_slide(6, '02 — Méthode', 'Architecture globale de la solution')
steps = ['Dataset CSV', 'Exploration et\ndiagnostic', 'Nettoyage', 'Analyse\nexploratoire',
         'Construction\nde X et y', 'Train / Test\nsplit', 'Pipeline anti-fuite\nimputation + scaling',
         'Entraînement\n3 modèles + LR améliorée', 'Validation croisée\n5-fold / 5×5',
         'Seuil appris\nsur le train', 'Évaluation test\nune seule fois', 'Sauvegarde\nJoblib + méta',
         'Streamlit\n+ triage humain']
for i, label in enumerate(steps[:7]):
    x = 0.45 + i * 1.82
    rect(s, x, 1.45, 1.66, 0.95, LIGHT, BORDER, radius=True)
    textbox(s, x + 0.05, 1.57, 1.56, 0.72, label, 9.2, GREEN2, True, PP_ALIGN.CENTER)
    if i < 6:
        textbox(s, x + 1.66, 1.75, 0.16, 0.25, '→', 13, TEAL, True, PP_ALIGN.CENTER)
textbox(s, 12.05, 2.48, 0.28, 0.4, '↓', 15, TEAL, True, PP_ALIGN.CENTER)
for k, label in enumerate(steps[7:]):
    i = 7 + k
    x = 0.45 + (12 - i) * 1.82
    rect(s, x, 3.35, 1.66, 0.95, LIGHT, BORDER, radius=True)
    textbox(s, x + 0.05, 3.47, 1.56, 0.72, label, 9.2, GREEN2, True, PP_ALIGN.CENTER)
    if k < 5:
        textbox(s, x - 0.17, 3.65, 0.17, 0.25, '←', 13, TEAL, True, PP_ALIGN.CENTER)
    else:
        textbox(s, x - 0.17, 3.65, 0.17, 0.25, '←', 13, TEAL, True, PP_ALIGN.CENTER)
rect(s, 0.55, 4.75, 12.20, 1.55, GREEN2, radius=True)
textbox(s, 0.80, 4.92, 11.7, 1.25,
        'Règle d\'intégrité — le jeu test (104 messages) n\'est utilisé qu\'à l\'étape 11, après le choix du modèle et du seuil.\n'
        'Imputation, standardisation, validation croisée, sélection du seuil et triage sont appris sur le train (416 messages).\n'
        'Aucune variable calendaire (date, semaine) n\'entre dans X ; aucune variable catégorielle textuelle n\'impose de one-hot encoding.',
        10.5, WHITE)
notes(s, """À dire : suivre le flux de gauche à droite en haut puis de droite à gauche en bas.\n"
"Pourquoi : cette architecture garantit l'absence de data leakage ; c'est le point le plus souvent attaqué par un jury.\n"
"Question jury : « Où est calculé le seuil ? » → à l'étape 10, uniquement avec les probabilités out-of-fold du train.""")

# ---------------------------------------------------------------------------
# 7 — Processus (schéma corrigé)
# ---------------------------------------------------------------------------
s = base_slide(7, '02 — Méthode', 'Processus Machine Learning — schéma corrigé')
image_fit(s, IMG / 'cell54_0.png', 0.60, 1.30, 12.10, 4.15)
rect(s, 0.55, 5.60, 12.20, 1.15, LIGHT, BORDER, radius=True)
textbox(s, 0.75, 5.72, 11.8, 0.92,
        'Légende : 10 étapes, du CSV brut à l\'application Streamlit ; les couleurs séparent données, '
        'modélisation, décision et restitution.\n'
        'Lecture et conclusion : la correction essentielle porte sur l\'ordre — le test n\'est consulté '
        'qu\'à l\'étape 8 et le one-hot encoding a été retiré car les 9 variables sont numériques.',
        10.5, DARK)
notes(s, """À dire : montrer ce schéma comme la « colonne vertébrale » du projet ; il est identique dans l'app et le notebook.\n"
"Pourquoi : le schéma initial fourni comportait des erreurs (test utilisé trop tôt, one-hot inexistant) ; il a été corrigé puis régénéré depuis la fonction process_figure() de app.py.\n"
"Question jury : « Pourquoi le seuil avant l'évaluation test ? » → parce que choisir le seuil sur le test optimiserait biaisément les métriques finales.""")
# tableau de correspondance des 10 étapes
# (déjà intégré dans l'image ; on garde la slide lisible)

# ---------------------------------------------------------------------------
# 8 — Dataset
# ---------------------------------------------------------------------------
s = base_slide(8, '03 — Données', 'Jeu de données et variables')
for x, val, lab in [(0.55, '524', 'lignes brutes · 11 colonnes'),
                    (3.65, '520', 'lignes propres (4 doublons retirés)'),
                    (6.75, '374', 'Non · 71,92 %'),
                    (9.85, '146', 'Oui · 28,08 %')]:
    rect(s, x, 1.28, 2.90, 0.90, GREEN2, radius=True)
    textbox(s, x + 0.12, 1.36, 2.65, 0.38, val, 21, WHITE, True, PP_ALIGN.CENTER)
    textbox(s, x + 0.10, 1.78, 2.70, 0.30, lab, 9.5, LIGHTBLUE, align=PP_ALIGN.CENTER)
table(s, 0.55, 2.45, 8.65, 3.95,
      ['Variable ( brute )', 'Rôle dans le projet', 'Traitement'],
      [['heure_envoi', 'Horaire du message', 'Retirée du modèle final (bruit)'],
       ['longueur_message', 'Longueur du message', 'Retirée du modèle final (bruit)'],
       ['nb_liens', 'Nombre de liens', 'Conservée + interaction'],
       ['urgence_score', 'Ton urgent / pressant', 'Conservée + interaction'],
       ['domaine_age_jours', 'Âge du domaine', 'log1p + médiane + scaling'],
       ['fautes_langue', 'Nombre de fautes', 'Retirée du modèle final (bruit)'],
       ['expediteur_connu', 'Expéditeur connu ?', 'Conservée (binaire)'],
       ['piece_jointe', 'Présence d\'une pièce jointe', 'Conservée (binaire)'],
       ['personnalisation_score', 'Degré de personnalisation', 'Conservée']],
      widths=[2.6, 3.0, 3.05], font=9.3)
card(s, 9.45, 2.45, 3.30, 3.95, 'Cible et exclusions',
     'Cible : message_malveillant\n(Oui / Non).\n\n'
     'date et semaine : exclues de X (variables calendaires sans justification métier).\n\n'
     'Origine du CSV : fichier local mentionné comme synthétique dans le notebook ; source externe non documentée.',
     body_size=10.5, accent=AMBER)
textbox(s, 0.55, 6.55, 12.2, 0.35,
        'Le modèle final n\'utilise que 6 des 9 variables brutes : retrait de heure_envoi, longueur_message et fautes_langue, '
        'ajout de urg_x_inconnu et liens_x_inconnu.', 9.5, GRAY, italic=True)
notes(s, """À dire : insister sur la cible binaire et sur le caractère local du dataset.\n"
"Pourquoi : la question de l'origine du jeu est récurrente en soutenance ; le notebook parle de données synthétiques, nous ne prétendons pas qu'il vient d'UCI ou Kaggle.\n"
"Question jury : « Pourquoi exclure la date ? » → risque d'apprendre une tendance temporelle du jeu synthétique, sans justification métier ; la règle du projet est de ne jamais mettre la cible ni la date dans X.""")
# correction couleur des KPI (déjà blancs)

# ---------------------------------------------------------------------------
# 9 — Nettoyage
# ---------------------------------------------------------------------------
s = base_slide(9, '03 — Données', 'Nettoyage et qualité des données')
table(s, 0.55, 1.35, 7.55, 3.75,
      ['Action', 'Résultat observé', 'Justification'],
      [['Suppression des doublons', '4 lignes retirées → 520', 'Évite de compter deux fois le même message'],
       ['Valeurs manquantes', '10 NA dans domaine_age_jours (1,91 %)', 'Aucune NA dans les autres colonnes'],
       ['Imputation', 'Médiane, apprise sur le train', 'Robuste aux valeurs extrêmes (1 à 5 874 jours)'],
       ['Transformation', 'log1p(domaine_age_jours)', 'Réduit l\'asymétrie de la distribution'],
       ['Standardisation', 'StandardScaler dans le pipeline', 'Nécessaire pour LR et SVM ; évite la fuite'],
       ['Encodage', 'Aucun one-hot', 'Aucune variable catégorielle non numérique']],
      widths=[2.1, 2.7, 2.75], font=9.5)
card(s, 8.35, 1.35, 4.40, 3.75, 'Pourquoi la médiane ?',
     'L\'âge du domaine est très étalé : quelques domaines très anciens tirent la moyenne. '
     'La médiane represente mieux un cas typique et elle est calculée sur le train uniquement, '
     'puis réutilisée telle quelle sur le test.\n\n'
     'C\'est le même réflexe pour le scaling : les statistiques sont apprises sur le train, '
     'pas sur l\'ensemble du jeu.', body_size=11)
rect(s, 0.55, 5.35, 12.20, 1.35, LIGHT, BORDER, radius=True)
textbox(s, 0.75, 5.52, 11.8, 1.05,
        'Résultat : 520 observations propres, 374 Non / 146 Oui, 9 variables explicatives numériques.\n'
        'Les variables calendaires (date, semaine) sont écartées sans être utilisées comme prédicteurs ; '
        'la cible n\'entre jamais dans X.', 11, GREEN2, True)
notes(s, """À dire : la médiane et le scaling sont dans le Pipeline scikit-learn ; c'est ce qui garantit l'absence de fuite.\n"
"Question jury : « Pourquoi pas la moyenne ? » → distribution très asymétrique (log1p ensuite), la médiane résiste aux outliers.\n"
"Question jury : « Pourquoi pas de one-hot ? » → toutes les variables sont déjà numériques ; le code initial prévoyait un ColumnTransformer mais aucun encodage n'est appliqué.""")
for shp in s.shapes:
    if hasattr(shp, 'text') and 'represente' in shp.text:
        for p in shp.text_frame.paragraphs:
            for r in p.runs:
                r.text = r.text.replace('represente', 'représente')

# ---------------------------------------------------------------------------
# 10 — EDA
# ---------------------------------------------------------------------------
s = base_slide(10, '03 — Données', 'Analyse exploratoire (EDA)')
panel(s, 0.55, 1.32, 4.00, 4.10, IMG / 'cell31_0.png',
      'Répartition de la cible',
      'Effectifs Non = 374, Oui = 146.',
      'Classe minoritaire à 28,08 %.',
      'justifie class_weight="balanced" et le F1 macro.', img_ratio=0.55, cap_size=8.6)
panel(s, 4.70, 1.32, 4.00, 4.10, IMG / 'boxplots_compact.png',
      'Boxplots par classe',
      'Distributions des variables numériques selon Oui / Non.',
      'Âge du domaine et urgence séparent le plus les classes.',
      'une variable seule ne suffit pas.', img_ratio=0.55, cap_size=8.6)
panel(s, 8.85, 1.32, 3.90, 4.10, IMG / 'cell33_0.png',
      'Histogrammes',
      'Forme des distributions, pics et queues.',
      'domaine_age_jours très asymétrique (1 → 5 874).',
      'log1p avant standardisation.', img_ratio=0.55, cap_size=8.6)
rect(s, 0.55, 5.62, 12.20, 1.10, LIGHT, BORDER, radius=True)
textbox(s, 0.75, 5.76, 11.8, 0.85,
        'Lecture croisée : l\'âge du domaine, le score d\'urgence, le nombre de liens et le caractère '
        'inconnu de l\'expéditeur présentent les écarts les plus nets entre classes. '
        'Une différence de moyenne n\'est pas une preuve de pouvoir prédictif : elle est confirmée '
        'ensuite par la validation croisée et la permutation importance.', 10.5, DARK)
notes(s, """À dire : commenter les graphiques comme des signaux, pas comme des preuves causales.\n"
"Question jury : « Une corrélation forte suffit-elle ? » → Non : nous utilisons un modèle multivarié et la permutation importance sur le test.""")

# ---------------------------------------------------------------------------
# 11 — Corrélation
# ---------------------------------------------------------------------------
s = base_slide(11, '03 — Données', 'Matrice de corrélation et associations à la cible')
panel(s, 0.55, 1.32, 6.30, 4.55, IMG / 'cell39_0.png',
      'Matrice de Pearson (variables explicatives)',
      'Couleur : corrélation de −1 (vert) à +1 (brun).',
      'Peu de fortes corrélations entre variables ; aucune causalité démontrée.',
      'le modèle gère les interactions.', img_ratio=0.62, cap_size=9)
panel(s, 7.10, 1.32, 5.65, 4.55, IMG / 'cell41_0.png',
      'Association de chaque variable avec Oui',
      'Corrélation de Pearson avec la cible binaire (Oui = 1).',
      'domaine_age_jours et urgence_score ressortent en tête.',
      'ces signaux sont retenus dans le modèle final.', img_ratio=0.62, cap_size=9)
textbox(s, 0.55, 6.05, 12.2, 0.65,
        'Précaution : une corrélation proche de zéro n\'implique pas l\'indépendance (des relations non linéaires '
        'peuvent exister), et la matrice ci-dessus n\'inclut pas la cible — d\'où le second graphique.',
        10, GRAY, italic=True)
notes(s, """À dire : distinguer corrélation entre prédicteurs et association avec la cible.\n"
"Question jury : « Pourquoi garder des variables peu corrélées ? » → une faible corrélation linéaire n'exclut pas un apport en combinaison ; le SVM RBF peut capter des interactions.""")

# ---------------------------------------------------------------------------
# 12 — Préparation / split
# ---------------------------------------------------------------------------
s = base_slide(12, '02 — Méthode', 'Préparation et séparation des données')
card(s, 0.55, 1.35, 6.20, 3.10, 'Construction de X et y',
     '• X : 9 variables explicatives numériques ; date, semaine et cible exclues.\n'
     '• y : message_malveillant codé Non / Oui.\n'
     '• Version améliorée : log1p(âge du domaine), retrait de 3 variables bruitées, '
     'ajout de urg_x_inconnu et liens_x_inconnu.\n'
     '• random_state = 42, stratification sur y.', body_size=11.5)
card(s, 7.00, 1.35, 5.75, 3.10, 'Split stratifié 80 / 20',
     'Train : 416 observations — sert à entraîner, à faire la validation croisée '
     'et à choisir le seuil / le triage.\n\n'
     'Test : 104 observations — lu une seule fois, à la fin, pour l\'évaluation.\n\n'
     'Le déséquilibre Non / Oui est conservé dans les deux ensembles.', body_size=11.5)
rect(s, 0.55, 4.70, 12.20, 1.95, GREEN2, radius=True)
textbox(s, 0.80, 4.90, 11.7, 1.55,
        'Anti-data-leakage — imputation (médiane), standardisation, sélection du modèle et apprentissage '
        'des seuils sont contenus dans le pipeline et estimés sur le train.\n'
        'Le test n\'intervient ni dans le choix du seuil 0,21, ni dans celui du triage 0,20 / 0,88, '
        'ni dans la sélection du modèle retenu. Le rapport final est donc une estimation honnête.',
        11, WHITE)
notes(s, """À dire : montrer la séparation train/test comme un contrat.\n"
"Question jury : « Le test a-t-il servi à choisir 0,21 ? » → Non : le plateau de coût vient des probabilités out-of-fold du train.""")

# ---------------------------------------------------------------------------
# 13 — Modèles et protocole
# ---------------------------------------------------------------------------
s = base_slide(13, '04 — Modélisation', 'Modèles comparés et protocole expérimental')
table(s, 0.55, 1.32, 12.20, 3.55,
      ['Modèle', 'Principe', 'Paramètres clés', 'Avantage', 'Limite'],
      [['Régression logistique', 'Frontière linéaire, probabilités calibrées',
        'max_iter=2000, class_weight=balanced', 'Interprétable, rapide', 'Interactions linéaires seulement'],
       ['Random Forest', 'Ensemble d\'arbres, votes majoritaires',
        '300 arbres, min_samples_leaf=2', 'Capte les non-linéarités', 'Moins lisible, sensible au petit test'],
       ['SVM RBF', 'Marge maximale dans un espace non linéaire',
        'C=1, gamma=scale, probability=True', 'Très stable en CV (σ = 0,018)', 'Moins interprétable, plus lent']],
      widths=[2.0, 3.0, 2.9, 2.2, 2.3], font=9.5)
card(s, 0.55, 5.10, 5.95, 1.60, 'Protocole',
     'Entraînement sur 416 lignes → validation croisée StratifiedKFold 5 plis '
     '(plus une CV répétée 5×5 pour le seuil) → évaluation finale sur 104 lignes.',
     body_size=10.5)
card(s, 6.80, 5.10, 5.95, 1.60, 'Métrique de sélection',
     'F1 macro avant tout, complété par le rappel Oui, l\'AUC, l\'AP et la matrice de confusion. '
     'L\'accuracy seule est trompeuse (72 % en prédisant toujours Non).',
     body_size=10.5, accent=AMBER)
notes(s, """À dire : les 3 modèles sont bien présents et exécutés dans les sorties du notebook (cellules 54, 59, 63, 71, 73, 76).\n"
"Question jury : « Pourquoi 3 modèles ? » → un linéaire interprétable, un ensemble non linéaire, un modèle à marge réputé stable sur petits jeux numériques.\n"
"Question jury : « CV ou test ? » → la CV estime la stabilité sur le train ; le test est le contrôle final unique.""")

# ---------------------------------------------------------------------------
# 14 — Résultats comparatifs
# ---------------------------------------------------------------------------
s = base_slide(14, '04 — Modélisation', 'Résultats expérimentaux — comparaison réelle')
chart_data = CategoryChartData()
chart_data.categories = ['Random Forest', 'Régression logistique', 'SVM RBF']
chart_data.add_series('F1 macro — test (104)', (0.734, 0.694, 0.694))
chart_data.add_series('F1 macro — CV 5-fold (train)', (0.791, 0.785, 0.784))
gframe = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.55), Inches(1.32),
                            Inches(7.25), Inches(3.60), chart_data)
chart = gframe.chart
chart.has_title = True
chart.chart_title.text_frame.text = 'F1 macro : test vs validation croisée'
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.include_in_layout = False
chart.value_axis.minimum_scale = 0
chart.value_axis.maximum_scale = 1
chart.plots[0].series[0].format.fill.solid()
chart.plots[0].series[0].format.fill.fore_color.rgb = AMBER
chart.plots[0].series[1].format.fill.solid()
chart.plots[0].series[1].format.fill.fore_color.rgb = TEAL
for ax in (chart.category_axis, chart.value_axis):
    ax.tick_labels.font.size = Pt(9)
chart.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
chart.legend.font.size = Pt(9)
table(s, 8.05, 1.32, 4.70, 3.60,
      ['Modèle', 'AUC test', 'AP test', 'F1 CV'],
      [['Random Forest', '0,866', '0,698', '0,791'],
       ['Régression logistique', '0,832', '0,656', '0,785'],
       ['SVM RBF', '0,834', '0,633', '0,784'],
       ['LR améliorée (retenue)', '0,910', '0,810', '0,814']],
      widths=[2.2, 1.0, 1.0, 0.9], font=9.5)
textbox(s, 8.10, 4.98, 4.6, 0.30, 'F1 CV = moyenne des 5 plis sur le train ; la LR améliorée est meilleure en CV et en AUC/AP.',
        8, GRAY, italic=True)
rect(s, 0.55, 5.15, 12.20, 1.60, LIGHT, BORDER, radius=True)
textbox(s, 0.75, 5.30, 11.8, 1.35,
        'Validation croisée 5-fold (train) — critère de sélection : LR améliorée 0,814 > Random Forest 0,791 '
        '> LR 0,785 > SVM 0,784. Le meilleur modèle en CV est donc la LR améliorée, également meilleure '
        'en AUC/AP (0,910 / 0,810) et en coût métier (33). Le test de 104 messages ne sert qu\'au contrôle final.\n'
        'Métriques adaptées à la classification : Accuracy, Précision, Rappel, F1, AUC. R² n\'est pas pertinent '
        'ici ; MAE / MSE sur probabilités ne mesurent que l\'erreur probabiliste (Brier = 0,123).',
        10, DARK)
notes(s, """À dire : bien séparer les deux tableaux — CV = estimation sur train, test = contrôle final.\n"
"Pourquoi la LR améliorée : AUC/AP supérieurs (0,910 / 0,810), coût 5·FN+FP le plus bas (33), explications lisibles ; le RF reste référence historique.\n"
"Question jury : « R², MAE, MSE ? » → ce n'est pas une régression : R² sur classes prédites n'a pas de sens ; MAE/MSE sur probabilités sont des mesures d'erreur probabiliste, discutées avec le Brier score.""")

# ---------------------------------------------------------------------------
# 15 — Matrice de confusion
# ---------------------------------------------------------------------------
s = base_slide(15, '05 — Décision', 'Matrice de confusion et coût métier')
textbox(s, 0.55, 1.25, 5.20, 0.30, 'Modèle retenu — seuil 0,21 (test, 104 messages)', 11, GREEN2, True)
table(s, 0.55, 1.60, 5.20, 2.20,
      ['Réel \\ Prédit', 'Oui', 'Non'],
      [['Oui (malveillant)', 'TP = 28', 'FN = 1'],
       ['Non (légitime)', 'FP = 28', 'TN = 47']],
      widths=[2.4, 1.4, 1.4], font=11, header_font=10)
textbox(s, 0.55, 3.92, 5.20, 0.85,
        'FN = attaque manquée (coût critique) · FP = fausse alerte (coût analyste). '
        'Rappel Oui = 96,6 % ; précision = 50,0 % ; F1 macro = 0,712.', 10, DARK)
textbox(s, 6.05, 1.25, 3.05, 0.30, 'Référence historique (RF)', 11, GREEN2, True)
image_fit(s, IMG / 'cell63_1.png', 6.05, 1.60, 3.05, 2.75)
textbox(s, 6.05, 4.42, 3.05, 0.45,
        'Légende : matrice du Random Forest sur le test. Lecture : plus de FN qu\'avec le modèle retenu.',
        8.5, DARK)
textbox(s, 9.40, 1.25, 3.35, 0.30, 'Arbitrage du seuil', 11, GREEN2, True)
table(s, 9.40, 1.60, 3.35, 2.10,
      ['Seuil', 'FN', 'FP', 'Coût 5·FN+FP'],
      [['0,50', '5', '17', '42'],
       ['0,21', '1', '28', '33']],
      widths=[0.9, 0.7, 0.7, 1.5], font=9.5)
textbox(s, 9.40, 3.82, 3.35, 0.95,
        'Conclusion : baisser le seuil augmente le rappel mais aussi les fausses alertes ; '
        'le plateau de coût en validation croisée 0,20–0,22 donne 0,21.', 9.5, DARK)
rect(s, 0.55, 5.05, 12.20, 1.65, GREEN2, radius=True)
textbox(s, 0.80, 5.22, 11.7, 1.35,
        'Contrôle immédiat après validation croisée — le test n\'est lu qu\'ici. '
        'TN = 47 · FP = 28 · FN = 1 · TP = 28 : un seul phishing manqué sur 29, '
        'au prix de 28 fausses alertes qui restent soumises à l\'analyste.\n'
        'Le coût métier 5·FN + FP passe de 42 (seuil par défaut 0,50) à 33 (seuil appris 0,21).',
        10.5, WHITE)
notes(s, """À dire : expliquer les 4 cases dans l'ordre TP, TN, FP, FN et leur traduction métier.\n"
"Question jury : « Pourquoi accepter 28 fausses alertes ? » → le coût attribué (5·FN + FP) traduit qu'un phishing manqué coûte ~5 fois une fausse alerte ; le seuil est un choix métier, pas une vérité.\n"
"Question jury : « Et à 0,89 / 0,90 ? » → le modèle amélioré donne 1 FP mais 15 à 18 FN, donc ce n'est pas acceptable. Le triage 0,20 / 0,88 donne 1 FN et 1 FP sur la partie automatisée, et envoie les 15 à 20 cas douteux en revue humaine au lieu de les classer automatiquement.\n"
"Question jury : « Peut-on avoir FN = 0 et FP = 0 ? » → Non sur ce jeu : à 0,10 on annule FN mais on crée ~41 FP ; à 0,98 on annule FP mais on manque ~26 phishings. Les distributions se chevauchent ; il faut améliorer le classement, pas seulement le seuil.""")

# ---------------------------------------------------------------------------
# 16 — Importance
# ---------------------------------------------------------------------------
s = base_slide(16, '05 — Décision', 'Importance des variables et analyse des erreurs')
panel(s, 0.55, 1.32, 7.20, 4.65, IMG / 'cell78_0.png',
      'Permutation importance (15 répétitions, scoring F1 macro)',
      'Baisse du F1 macro lorsqu\'une variable est permutée.',
      'domaine_age_jours domine (0,140), puis urgence_score (0,056).',
      'expediteur_connu (0,036) et nb_liens (0,023) complètent.', img_ratio=0.62, cap_size=9.2)
card(s, 8.00, 1.32, 4.75, 2.55, 'Variables les plus contributives',
     '1. domaine_age_jours : 0,140 ± 0,043\n'
     '2. urgence_score : 0,056 ± 0,044\n'
     '3. expediteur_connu : 0,036 ± 0,037\n'
     '4. nb_liens : 0,023 ± 0,027', body_size=11)
card(s, 8.00, 4.05, 4.75, 1.92, 'Lecture prudente',
     'L\'importance mesure la dépendance du modèle à une variable, pas une relation causale. '
     'Les variables retirées (heure_envoi, longueur_message, fautes_langue) ont une importance '
     'nulle ou négative dans la version historique.', accent=AMBER, body_size=10.5)
textbox(s, 0.55, 6.15, 12.2, 0.55,
        'Analyse d\'erreurs : le FN unique est un phishing classé « Non » ; les 28 FP sont des messages '
        'légitimes envoyés à la revue humaine. Le triage 3 zones limite l\'impact de ces erreurs.',
        10, GRAY, italic=True)
notes(s, """À dire : l'importance confirme l'EDA mais ne prouve pas la causalité.\n"
"Question jury : « Pourquoi certaines importances négatives ? » → permuter une variable bruitée peut améliorer légèrement le F1 ; c'est un signal pour retirer la variable, pas un effet réel.""")

# ---------------------------------------------------------------------------
# 17 — Triage, limites, perspectives
# ---------------------------------------------------------------------------
s = base_slide(17, '05 — Décision', 'Triage 3 zones, limites et perspectives')
table(s, 0.55, 1.32, 6.25, 2.55,
      ['Zone (P(Oui))', 'Réels Non', 'Réels Oui', 'Décision'],
      [['🟢 Normal (< 0,20)', '45', '1', 'Traitement automatique'],
       ['🟠 Revue (0,20 – 0,88)', '29', '14', 'Analyse humaine'],
       ['🔴 Alerte (≥ 0,88)', '1', '14', 'Priorité analyste']],
      widths=[2.4, 1.1, 1.1, 1.9], font=9.5)
card(s, 7.05, 1.32, 5.70, 2.55, 'Incertitude mesurée (bootstrap 2 000)',
     'Rappel Oui : [0,886 ; 1,000]\n'
     'Précision Oui : [0,368 ; 0,636]\n'
     'Taux de fausses alertes : [0,262 ; 0,481]\n\n'
     '61 messages sur 104 traités automatiquement (1 FN, 1 FP) ; 43 confiés à l\'analyste.',
     body_size=10.5)
card(s, 0.55, 4.10, 6.25, 2.55, 'Limites',
     '• Jeu synthétique de 520 lignes, origine à documenter.\n'
     '• Pas de texte brut ni d\'URL complète en entrée.\n'
     '• Aucun test sur un dataset externe indépendant.\n'
     '• 104 messages seulement en test, dont 29 malveillants.\n'
     '• Résultat sensible au seuil et à la composition du jeu.',
     accent=RED, body_size=10.5)
card(s, 7.05, 4.10, 5.70, 2.55, 'Perspectives',
     '• Valider sur des messages réels et diversifiés.\n'
     '• Ajouter des signaux extraits des URL et du contenu.\n'
     '• Étudier les seuils avec le RSSI (c_FN = 3 → 0,47 ; 10 → 0,20).\n'
     '• Conserver la revue humaine et tracer les alertes.\n'
     '• Renforcer l\'explicabilité et tester la robustesse aux nouveaux phishings.',
     body_size=10.5)
notes(s, """À dire : la zone orange n'est pas une réussite du classifieur mais une délégation explicite à l'humain.\n"
"Question jury : « Le triage est-il fiable ? » → sur le test, 61/104 automatiques avec 1 FN et 1 FP ; les IC bootstrap sont larges, donc nous ne sur-affirmons pas la performance.""")

# ---------------------------------------------------------------------------
# 18 — Conclusion
# ---------------------------------------------------------------------------
s = base_slide(18, '06 — Conclusion', 'Synthèse et questions')
card(s, 0.55, 1.32, 7.85, 4.85, 'Ce que nous avons démontré',
     '• Une démarche complète, du CSV brut à une application Streamlit, sans fuite de données.\n'
     '• 3 algorithmes comparés sur un split stratifié, avec validation croisée sur le train.\n'
     '• Un seuil binaire appris (0,21) et un triage 3 zones appris sur le train seul.\n'
     '• Le modèle retenu : LogisticRegression_amelioree — AUC 0,910, AP 0,810, Brier 0,123.\n'
     '• Au seuil 0,21 : TP 28 · TN 47 · FP 28 · FN 1, rappel 96,6 %, F1 macro 0,712, coût 33.\n'
     '• Des limites explicites et une validation humaine obligatoire.\n\n'
     'Valeur ajoutée : outiller la veille et la confiance numérique avec un score auditable, '
     'pas avec une boîte noire qui décide à la place de l\'analyste.', body_size=11.5)
rect(s, 8.65, 1.32, 4.10, 4.85, GREEN2, radius=True)
textbox(s, 8.90, 1.55, 3.60, 4.40,
        'CHIFFRES CLÉS\n\n'
        '520\nmessages propres\n\n'
        '416 / 104\ntrain / test\n\n'
        '0,910 / 0,810\nAUC / AP\n\n'
        '96,6 %\nrappel Oui\n\n'
        '61 / 104\ntraités automatiquement',
        13, WHITE, True, line_spacing=1.18)
textbox(s, 0.55, 6.40, 12.2, 0.5, 'Merci pour votre attention — Questions ?',
        20, GREEN, True, PP_ALIGN.CENTER)
notes(s, """À dire : conclure sur la démarche scientifique plus que sur le score brut.\n"
"Pourquoi : la fidélité au notebook est la priorité ; toute question chiffrée doit renvoyer aux slides 14–17.\n"
"Questions jury utiles : pourquoi la médiane (asymétrie), pourquoi standardiser (LR/SVM), pourquoi F1 macro (classes déséquilibrées), pourquoi pas l'accuracy seule (72 % sans détection), pourquoi la CV puis le test (sélection puis contrôle), pourquoi le jeu synthétique limite la généralisation, pourquoi R² n'est pas adapté, pourquoi un seuil plus bas augmente rappel et fausses alertes.""")

# Nettoyage des guillemets parasite laissés par les chaînes de notes multilignes
import re
for slide in prs.slides:
    tf = slide.notes_slide.notes_text_frame
    txt = tf.text
    txt = re.sub(r'\n"+\n', '\n', txt)
    txt = '\n'.join(line[1:] if line.startswith('"') else line for line in txt.split('\n'))
    if txt != tf.text:
        tf.text = txt

prs.save(OUT)
print('OK', OUT, OUT.stat().st_size, 'bytes,', len(prs.slides.__iter__.__self__._sldIdLst), 'slides')
