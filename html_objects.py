# ============================================================
# SPACING & LAYOUT SETTINGS (tweak these to adjust the layout)
# ============================================================

# Page dimensions (A5 in mm)
PAGE_WIDTH_MM = 148
PAGE_HEIGHT_MM = 210

# Accent bar at the top (mm)
ACCENT_BAR = 0.8

# Margins (mm)
MARGIN_FROM_ACCENT_BAR = 8  # Measured below ACCENT_BAR
MARGIN_TOP = 8 + ACCENT_BAR
MARGIN_BOTTOM = 8
MARGIN_LEFT = 8
MARGIN_RIGHT = 8

# Column split: left column width as percentage of content area
LEFT_COL_PERCENT = 38

# Gap between left and right column (mm)
COLUMN_GAP = 4

# Photo
PHOTO_MAX_HEIGHT_MM = 55  # max height for the photo area
PHOTO_BORDER_RADIUS = 6   # px

# Font sizes (pt)
FONT_SIZE_TITLE = 16
FONT_SIZE_PROCEDURE = 8
FONT_SIZE_INGREDIENTS = 8
FONT_SIZE_SPECS = 7
FONT_SIZE_NOTES = 7
FONT_SIZE_SECTION_HEADER = 9

# Spacing (mm)
SECTION_GAP = 3          # gap between sections
INGREDIENT_LINE_GAP = 1  # gap between ingredient lines
PROCEDURE_LINE_GAP = 1   # gap between procedure steps
NOTE_LINE_GAP = 1

# Colors (warm palette)
COLOR_BACKGROUND = "#fdf6ee"
COLOR_CARD_BG = "#fffaf3"
COLOR_TITLE = "#5a3a1a"
COLOR_SECTION_HEADER = "#8b5e3c"
COLOR_TEXT = "#3e2c1a"
COLOR_ACCENT = "#c97b3a"
COLOR_BORDER = "#e0cbb0"
COLOR_SPECS_BG = "#f5ebdb"
COLOR_NOTES_BG = "#f9f0e3"
COLOR_INGREDIENT_ALT = "#faf3e8"

# Star rating
STAR_FILLED = "★"
STAR_EMPTY = "☆"
MAX_STARS = 5


# ===================================================================
# HTML RENDERING TEMPLATES (to avoid abundance of code in other file)
# ===================================================================

def render_stars(rating: int) -> str:
    rating = max(0, min(rating, MAX_STARS))
    return (STAR_FILLED * rating) + (STAR_EMPTY * (MAX_STARS - rating))


def render_subassembly(sub_rows: str) -> str:
    return f"""
<div class="section">
    <div class="section-header">Subassembly</div>
    <table class="ingredients-table">{sub_rows}</table>
</div>
"""


def render_notes(notes_items: str) -> str:
    return f"""
<div class="section notes">
    <div class="section-header">Notes</div>
    <ul class="notes-list">{notes_items}</ul>
</div>"""


def render_recipe(
    photo_html: str,
    ingr_rows: str,
    sub_html: str,
    name: str,
    proc_items: str,
    specs_cells_top: str,
    specs_cells_bottom: str,
    notes_html: str,
) -> str:
    return f"""
<div class="page">
    <div class="accent-bar"></div>
    <div class="left-col">
        <div class="photo-container">{photo_html}</div>
        <div class="section">
            <div class="section-header">Ingredients</div>
            <table class="ingredients-table">{ingr_rows}</table>
        </div>
        {sub_html}
    </div>
    <div class="right-col">
        <h1 class="recipe-title">{name}</h1>
        <div class="section">
            <div class="section-header">Procedure</div>
            <ol class="procedure-list">{proc_items}</ol>
        </div>
        <div class="section specs">
            <div class="specs-grid">{specs_cells_top}</div>
            <div class="specs-grid">{specs_cells_bottom}</div>
        </div>
        {notes_html}
    </div>
</div>
"""


def render_html_page(pages: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Recipe Book</title>
<style>
@page {{
    size: {PAGE_WIDTH_MM}mm {PAGE_HEIGHT_MM}mm;
    margin: 0;
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    color: {COLOR_TEXT};
    background: {COLOR_BACKGROUND};
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

.page {{
    width: {PAGE_WIDTH_MM}mm;
    height: {PAGE_HEIGHT_MM}mm;
    padding: {MARGIN_TOP}mm {MARGIN_RIGHT}mm {MARGIN_BOTTOM}mm {MARGIN_LEFT}mm;
    background: {COLOR_CARD_BG};
    display: flex;
    gap: {COLUMN_GAP}mm;
    page-break-after: always;
    overflow: hidden;
    position: relative;
    border-bottom: 2px solid {COLOR_BORDER};
}}

.accent-bar {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: {ACCENT_BAR}mm;
    background: linear-gradient(
        90deg, {COLOR_ACCENT}, {COLOR_BORDER}, {COLOR_ACCENT}
    );
}}

.left-col {{
    width: {LEFT_COL_PERCENT}%;
    display: flex;
    flex-direction: column;
    gap: {SECTION_GAP}mm;
}}

.right-col {{
    width: {100 - LEFT_COL_PERCENT}%;
    display: flex;
    flex-direction: column;
    gap: {SECTION_GAP}mm;
}}

.photo-container {{
    width: 100%;
    max-height: {PHOTO_MAX_HEIGHT_MM}mm;
    overflow: hidden;
    border-radius: {PHOTO_BORDER_RADIUS}px;
    border: 1.5px solid {COLOR_BORDER};
}}

.photo {{
    width: 100%;
    height: auto;
    max-height: {PHOTO_MAX_HEIGHT_MM}mm;
    object-fit: cover;
    display: block;
    border-radius: {PHOTO_BORDER_RADIUS}px;
}}

.photo-placeholder {{
    width: 100%;
    height: {PHOTO_MAX_HEIGHT_MM}mm;
    background: {COLOR_SPECS_BG};
    display: flex;
    align-items: center;
    justify-content: center;
    color: {COLOR_SECTION_HEADER};
    font-style: italic;
    font-size: {FONT_SIZE_SPECS}pt;
    border-radius: {PHOTO_BORDER_RADIUS}px;
}}

.recipe-title {{
    font-size: {FONT_SIZE_TITLE}pt;
    color: {COLOR_TITLE};
    font-weight: bold;
    border-bottom: 1.5px solid {COLOR_ACCENT};
    padding-bottom: 1.5mm;
    line-height: 1.2;
}}

.section-header {{
    font-size: {FONT_SIZE_SECTION_HEADER}pt;
    color: {COLOR_SECTION_HEADER};
    font-weight: bold;
    margin-bottom: 1mm;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.ingredients-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: {FONT_SIZE_INGREDIENTS}pt;
}}

.ingredients-table td {{
    padding: {INGREDIENT_LINE_GAP}mm 1mm;
    vertical-align: top;
}}

.ingredients-table td.amount {{
    width: 35%;
    font-weight: bold;
    color: {COLOR_ACCENT};
    white-space: nowrap;
}}

.ingredients-table tr.alt {{
    background: {COLOR_INGREDIENT_ALT};
}}

.procedure-list {{
    font-size: {FONT_SIZE_PROCEDURE}pt;
    padding-left: 4mm;
    line-height: 1.4;
}}

.procedure-list li {{
    margin-bottom: {PROCEDURE_LINE_GAP}mm;
}}

.procedure-list li::marker {{
    color: {COLOR_ACCENT};
    font-weight: bold;
}}

.specs {{
    display: flex;
    gap: {SECTION_GAP}mm;
}}

.specs-grid {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.8mm;
    background: {COLOR_SPECS_BG};
    border-radius: 4px;
    padding: 1.5mm 2mm;
    font-size: {FONT_SIZE_SPECS}pt;
    border: 1px solid {COLOR_BORDER};
}}

.spec-item {{
    display: flex;
    justify-content: space-between;
    gap: 1mm;
}}

.spec-label {{
    font-weight: bold;
    color: {COLOR_SECTION_HEADER};
}}

.spec-value {{
    text-align: right;
}}

.notes {{
    background: {COLOR_NOTES_BG};
    border-radius: 4px;
    padding: 1.5mm 2mm;
    border-left: 2px solid {COLOR_ACCENT};
}}

.notes-list {{
    font-size: {FONT_SIZE_NOTES}pt;
    padding-left: 3.5mm;
    line-height: 1.35;
}}

.notes-list li {{
    margin-bottom: {NOTE_LINE_GAP}mm;
}}

@media print {{
    body {{
        background: white;
    }}
    .page {{
        border-bottom: none;
    }}
}}
</style>
</head>
<body>
{pages}
</body>
</html>
"""
