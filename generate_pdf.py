"""
Recipe Book PDF Generator
Generates an A5-format recipe book from recipes.json, one recipe per page.
Uses Microsoft Edge (headless) to convert HTML to PDF.
"""

import json
import base64
import subprocess
from pathlib import Path

# ============================================================
# SPACING & LAYOUT SETTINGS (tweak these to adjust the layout)
# ============================================================

# Page dimensions (A5 in mm)
PAGE_WIDTH_MM = 148
PAGE_HEIGHT_MM = 210

# Margins (mm)
MARGIN_TOP = 8
MARGIN_BOTTOM = 8
MARGIN_LEFT = 10
MARGIN_RIGHT = 10

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

# Browser path (Edge). Change to Chrome path if preferred.
BROWSER_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ============================================================

SCRIPT_DIR = Path(__file__).parent
PHOTOS_DIR = SCRIPT_DIR / "photos"
RECIPES_FILE = SCRIPT_DIR / "recipes.json"
OUTPUT_HTML = SCRIPT_DIR / "recipe_book.html"
OUTPUT_PDF = SCRIPT_DIR / "recipe_book.pdf"


def image_to_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def render_stars(rating: int) -> str:
    rating = max(0, min(rating, MAX_STARS))
    return (STAR_FILLED * rating) + (STAR_EMPTY * (MAX_STARS - rating))


def render_recipe(key: str, recipe: dict) -> str:
    name = recipe.get("name", key)
    photo_file = recipe.get("photo", "")
    procedure = recipe.get("procedure", [])
    ingredients = recipe.get("ingredients", [])
    subassembly = recipe.get("subassembly", [])
    specs = recipe.get("specs", {})
    notes = recipe.get("notes", [])

    # Photo
    photo_path = PHOTOS_DIR / photo_file
    photo_uri = image_to_data_uri(photo_path)
    photo_html = (
        f'<img class="photo" src="{photo_uri}" alt="{name}">'
        if photo_uri
        else '<div class="photo-placeholder">No Photo</div>'
    )

    # Ingredients
    ingr_rows = ""
    for i, item in enumerate(ingredients):
        cls = ' class="alt"' if i % 2 == 1 else ""
        ingr_rows += f"<tr{cls}><td class='amount'>{item[0]}</td><td>{item[1]}</td></tr>\n"

    # Subassembly
    sub_html = ""
    if subassembly:
        sub_rows = "".join(
            f"<tr><td class='amount'>{it[0]}</td><td>{it[1]}</td></tr>\n"
            for it in subassembly
        )
        sub_html = f"""
        <div class="section">
            <div class="section-header">Subassembly</div>
            <table class="ingredients-table">{sub_rows}</table>
        </div>"""

    # Procedure
    proc_items = "\n".join(f"<li>{step}</li>" for step in procedure)

    # Specs
    spec_labels = {
        "yield": "Yield", "persons": "Persons", "type": "Type",
        "prep_time": "Prep", "cook_time": "Cook", "price": "Price",
        "diet": "Diet", "scalability": "Scale", "my_rating": "Rating",
    }
    specs_cells = ""
    for skey, label in spec_labels.items():
        if skey in specs:
            val = specs[skey]
            if skey == "my_rating":
                val = render_stars(int(val))
            specs_cells += f"<div class='spec-item'><span class='spec-label'>{label}</span><span class='spec-value'>{val}</span></div>\n"

    # Notes
    notes_items = "\n".join(f"<li>{n}</li>" for n in notes if n)
    notes_html = ""
    if notes_items:
        notes_html = f"""
        <div class="section notes">
            <div class="section-header">Notes</div>
            <ul class="notes-list">{notes_items}</ul>
        </div>"""

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
                <div class="specs-grid">{specs_cells}</div>
            </div>
            {notes_html}
        </div>
    </div>
    """


def generate_html(recipes: dict) -> str:
    pages = "\n".join(render_recipe(k, v) for k, v in recipes.items())

    return f"""<!DOCTYPE html>
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
    height: 3px;
    background: linear-gradient(90deg, {COLOR_ACCENT}, {COLOR_BORDER}, {COLOR_ACCENT});
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

.specs-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
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
</html>"""


def html_to_pdf(html_path: Path, pdf_path: Path):
    """Use Edge/Chrome headless to print HTML to PDF."""
    browser = Path(BROWSER_PATH)
    if not browser.exists():
        chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        if chrome.exists():
            browser = chrome
        else:
            print(f"ERROR: Browser not found at {BROWSER_PATH}")
            print("Set BROWSER_PATH at the top of generate_pdf.py to your Chrome or Edge path.")
            print("You can also open recipe_book.html in a browser and print to PDF (A5 paper size).")
            return

    # Convert mm to inches for the browser flag (1 inch = 25.4 mm)
    paper_w = PAGE_WIDTH_MM / 25.4
    paper_h = PAGE_HEIGHT_MM / 25.4

    cmd = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        f"--print-to-pdf-paper-width={paper_w:.4f}",
        f"--print-to-pdf-paper-height={paper_h:.4f}",
        "--print-to-pdf-margin-top=0",
        "--print-to-pdf-margin-bottom=0",
        "--print-to-pdf-margin-left=0",
        "--print-to-pdf-margin-right=0",
        str(html_path.as_uri()),
    ]
    print(f"Running: {browser.name} --headless --print-to-pdf ...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if pdf_path.exists():
        print(f"PDF generated: {pdf_path}")
    else:
        print(f"PDF generation failed (exit code {result.returncode})")
        if result.stderr:
            print(result.stderr[:500])


def main():
    with open(RECIPES_FILE, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    html = generate_html(recipes)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML generated: {OUTPUT_HTML}")

    html_to_pdf(OUTPUT_HTML, OUTPUT_PDF)


if __name__ == "__main__":
    main()
