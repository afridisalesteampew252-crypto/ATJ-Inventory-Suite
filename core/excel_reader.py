"""
Handles loading and normalizing raw ERP vehicle export files (97-column XLSX).
"""
from pathlib import Path
import logging

import pandas as pd

from config import COLUMN_ALIASES

logger = logging.getLogger("ATJ.excel_reader")


class ERPReader:
    """Loads an ERP Excel export and exposes normalized records."""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.df: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"ERP export file not found at: {self.file_path}")

        try:
            self.df = pd.read_excel(self.file_path, engine="openpyxl")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to read ERP file: %s", self.file_path)
            raise RuntimeError(f"Could not read Excel file '{self.file_path.name}': {exc}") from exc

        # Sanitize column names (strip whitespace, collapse internal spaces)
        self.df.columns = [str(c).strip() for c in self.df.columns]

        # Drop fully empty rows (common at the end of ERP exports)
        self.df = self.df.dropna(how="all").reset_index(drop=True)

        logger.info("Loaded %d rows, %d columns from %s", len(self.df), len(self.df.columns), self.file_path.name)
        return self.df

    def get_records(self) -> list[dict]:
        if self.df is None:
            self.load()
        # Replace NaN with empty string so downstream code doesn't have to handle floats('nan')
        clean_df = self.df.where(self.df.notnull(), "")
        return clean_df.to_dict(orient="records")

    @staticmethod
    def resolve_field(record: dict, field_key: str, default=""):
        """
        Look up a logical field (e.g. 'stock_id') in a raw record using the
        alias list in config.COLUMN_ALIASES. Returns the first match found.
        """
        for alias in COLUMN_ALIASES.get(field_key, []):
            if alias in record and str(record[alias]).strip() not in ("", "nan", "None"):
                return record[alias]
        return default
