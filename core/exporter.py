"""
Handles exporting mapped product data to XLSX and CSV formats for Meta Catalog upload.
"""
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import OUTPUT_FOLDER

logger = logging.getLogger("ATJ.exporter")

# Column order matching Meta's recommended catalog feed layout
EXPORT_COLUMNS = [
    "id", "title", "description", "availability", "condition",
    "price", "link", "image_link", "brand", "year", "model",
    "mileage", "transmission", "fuel_type", "color",
]


class CatalogExporter:
    """Exports mapped product dicts to timestamped XLSX and CSV files."""

    def export(self, products: list[dict], base_name: str = "facebook_catalog", timestamp: bool = True) -> dict:
        if not products:
            raise ValueError("No products to export. Check your ERP file and mapping step.")

        df = pd.DataFrame(products)

        # Reorder columns; keep any extras at the end
        ordered_cols = [c for c in EXPORT_COLUMNS if c in df.columns]
        extra_cols = [c for c in df.columns if c not in ordered_cols]
        df = df[ordered_cols + extra_cols]

        suffix = f"_{datetime.now():%Y%m%d_%H%M%S}" if timestamp else ""
        excel_path = OUTPUT_FOLDER / f"{base_name}{suffix}.xlsx"
        csv_path = OUTPUT_FOLDER / f"{base_name}{suffix}.csv"

        df.to_excel(excel_path, index=False, engine="openpyxl")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")  # BOM for Excel compatibility

        logger.info("Exported %d rows to %s and %s", len(df), excel_path.name, csv_path.name)

        return {
            "excel": excel_path,
            "csv": csv_path,
            "total_records": len(df),
        }
