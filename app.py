"""
ATJ Facebook Catalog Generator - CLI entry point.
Run this directly for a no-GUI batch conversion, or launch gui/main_window.py
for the desktop interface.
"""
import logging
import sys
from pathlib import Path

from config import INPUT_FOLDER, LOG_FOLDER, APP_NAME, APP_VERSION
from core.excel_reader import ERPReader
from core.facebook_mapper import FacebookMapper
from core.image_matcher import ImageMatcher
from core.validator import CatalogValidator
from core.exporter import CatalogExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FOLDER / "atj_catalog.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ATJ.app")


def run(verify_images: bool = False) -> int:
    print("=" * 60)
    print(f"{APP_NAME} v{APP_VERSION}")
    print("=" * 60)

    erp_files = list(INPUT_FOLDER.glob("*.xlsx")) + list(INPUT_FOLDER.glob("*.xls"))
    if not erp_files:
        print(f"\u274c Error: No Excel file found in '{INPUT_FOLDER}/'.")
        print("Place your ERP Excel export file in the 'input/' folder and re-run.")
        return 1

    erp_file = erp_files[0]
    print(f"\U0001F4C1 Processing ERP File: {erp_file.name}")

    try:
        reader = ERPReader(erp_file)
        records = reader.get_records()
        print(f"\U0001F4CA Loaded {len(records):,} vehicle records.")

        print("\U0001F504 Mapping fields to Facebook Catalog template...")
        mapper = FacebookMapper()
        mapped_products = mapper.map_all(records)

        if verify_images:
            print("\U0001F5BC\uFE0F  Verifying image URLs (this can take a while)...")
            matcher = ImageMatcher(verify=True)
            mapped_products = matcher.verify_all(mapped_products)

        print("\u2705 Validating rows against Meta catalog requirements...")
        validator = CatalogValidator()
        result = validator.validate_all(mapped_products)
        print(f"   {result.summary()}")
        if result.invalid_rows:
            print(f"   \u26A0\uFE0F  {len(result.invalid_rows)} rows had issues \u2014 see logs/atj_catalog.log")

        export_rows = result.valid_rows if result.valid_rows else mapped_products
        print("\U0001F4BE Exporting catalog files...")
        exporter = CatalogExporter()
        out = exporter.export(export_rows)

        print("\n" + "=" * 60)
        print("\u2705 SUCCESS!")
        print(f"\U0001F4C4 Excel output: {out['excel']}")
        print(f"\U0001F4C4 CSV output:   {out['csv']}")
        print(f"\U0001F4C8 Total rows:   {out['total_records']:,}")
        print("=" * 60)
        return 0

    except Exception as exc:  # noqa: BLE001
        logger.exception("Fatal error during processing")
        print(f"\n\u274c FAILED: {exc}")
        print(f"See {LOG_FOLDER / 'atj_catalog.log'} for full details.")
        return 1


def main():
    verify = "--verify-images" in sys.argv
    sys.exit(run(verify_images=verify))


if __name__ == "__main__":
    main()
