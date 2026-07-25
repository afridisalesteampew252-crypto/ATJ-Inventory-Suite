# ATJ Inventory Suite \u2014 Facebook Catalog Generator

Converts Afridi Trading Japan ERP vehicle exports (97-column XLSX) into a
Meta (Facebook) Product Catalog-ready XLSX + CSV, with an optional desktop GUI
and a one-command Windows EXE build.

## Features

- Reads ERP Excel exports with resilient column-name matching (handles header drift)
- Maps vehicle records to Meta Catalog fields (id, title, price, image_link, etc.)
- Validates rows against Meta's catalog requirements before export
- Optional live image URL verification (stock vs auction image conventions, with extension fallback)
- Exports timestamped `.xlsx` and `.csv` files
- Desktop GUI (PySide6) for non-technical staff
- Packaged as a standalone Windows `.exe` via PyInstaller \u2014 no Python install needed on the target machine

## Project Structure

```
ATJ-Inventory-Suite/
\u251C\u2500\u2500 app.py                      # CLI entry point
\u251C\u2500\u2500 run_gui.py                  # GUI entry point (also the PyInstaller target)
\u251C\u2500\u2500 config.py                   # Paths, URL patterns, column aliases
\u251C\u2500\u2500 build_exe.py                # One-command EXE build helper
\u251C\u2500\u2500 ATJCatalogGenerator.spec    # PyInstaller build spec
\u251C\u2500\u2500 requirements.txt
\u251C\u2500\u2500 core/
\u2502   \u251C\u2500\u2500 excel_reader.py         # ERP file loading + normalization
\u2502   \u251C\u2500\u2500 facebook_mapper.py      # ERP \u2192 Meta Catalog field mapping
\u2502   \u251C\u2500\u2500 image_matcher.py        # Image URL validation/fallback
\u2502   \u251C\u2500\u2500 validator.py            # Pre-export row validation
\u2502   \u2514\u2500\u2500 exporter.py             # XLSX/CSV export
\u251C\u2500\u2500 gui/
\u2502   \u2514\u2500\u2500 main_window.py          # PySide6 desktop interface
\u251C\u2500\u2500 input/                      # Drop your ERP .xlsx export here
\u251C\u2500\u2500 output/                     # Generated catalog files appear here
\u2514\u2500\u2500 logs/                       # Error logs
```

## Quick Start (run from source)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# CLI mode:
python app.py
python app.py --verify-images   # also checks that image URLs actually resolve

# GUI mode:
python run_gui.py
```

Place your ERP `.xlsx` export in `input/` before running the CLI. The GUI lets
you browse to any file location instead.

## Building the Windows EXE

From the project root, inside your virtual environment:

```bash
python build_exe.py
```

This installs/updates PyInstaller and builds using `ATJCatalogGenerator.spec`.
The finished executable will be at:

```
dist/ATJCatalogGenerator.exe
```

That single file can be copied to any Windows machine and double-clicked \u2014
no Python installation required on the target PC.

### Manual build (alternative)

```bash
pip install pyinstaller
pyinstaller --clean --noconfirm ATJCatalogGenerator.spec
```

### Adding an icon

Drop an `.ico` file into an `assets/` folder and set the `icon=` parameter in
`ATJCatalogGenerator.spec` to its path, e.g. `icon='assets/icon.ico'`.

## Configuration

Edit `config.py` to adjust:

- `BASE_URL` \u2014 your storefront's base URL, used to build `link` fields
- `IMAGE_PATHS` \u2014 stock/auction image URL templates
- `COLUMN_ALIASES` \u2014 add any additional ERP header variants you encounter
- `DEFAULT_CURRENCY` \u2014 currency code used in the `price` field

## Output Format

Exported columns follow Meta's recommended catalog feed layout:

`id, title, description, availability, condition, price, link, image_link, brand, year, model, mileage, transmission, fuel_type, color`

## Troubleshooting

- **"No Excel file found in input/"** \u2014 make sure your `.xlsx`/`.xls` file is
  directly inside the `input/` folder (CLI mode only; GUI mode uses the file browser).
- **Rows rejected during validation** \u2014 check `logs/atj_catalog.log` for the
  specific field and row number that failed.
- **Image links look wrong** \u2014 run with `--verify-images` (CLI) or check the
  "Verify image URLs" box (GUI) to have the tool test and auto-correct file extensions.
