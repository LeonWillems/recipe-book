"""
Recipe Book PDF Generator
Generates an A5-format recipe book from recipes.json, one recipe per page.
Uses Microsoft Edge (headless) to convert HTML to PDF.
"""

import json
import base64
import subprocess
from pathlib import Path

from .html_objects import (
    PAGE_WIDTH_MM, PAGE_HEIGHT_MM,
    render_stars, render_subassembly, render_notes,
    render_recipe, render_html_page,
)

# Browser path (Edge). Change to Chrome path if preferred.
BROWSER_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

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


def process_recipe(key: str, recipe: dict) -> str:
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
        ingr_rows += (
            f"<tr{cls}><td class='amount'>{item[0]}</td>"
            f"<td>{item[1]}</td></tr>\n"
        )

    # Subassembly
    sub_html = ""
    if subassembly:
        sub_rows = "".join(
            f"<tr><td class='amount'>{it[0]}</td><td>{it[1]}</td></tr>\n"
            for it in subassembly
        )
        sub_html = render_subassembly(sub_rows)

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
            specs_cells += (
                f"<div class='spec-item'><span class='spec-label'>{label}"
                f"</span><span class='spec-value'>{val}</span></div>\n"
            )

    # Notes
    notes_items = "\n".join(f"<li>{n}</li>" for n in notes if n)
    notes_html = ""
    if notes_items:
        notes_html = render_notes(notes_items)

    return render_recipe(
        photo_html, ingr_rows, sub_html, name,
        proc_items, specs_cells, notes_html,
    )


def generate_html(recipes: dict) -> str:
    pages = "\n".join(process_recipe(k, v) for k, v in recipes.items())
    return render_html_page(pages)


def html_to_pdf(html_path: Path, pdf_path: Path):
    """Use Edge/Chrome headless to print HTML to PDF."""
    browser = Path(BROWSER_PATH)
    if not browser.exists():
        chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        if chrome.exists():
            browser = chrome
        else:
            print(f"ERROR: Browser not found at {BROWSER_PATH}")
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
