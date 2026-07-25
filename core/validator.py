"""
Pre-export validation checks for mapped Facebook catalog rows.
Ensures required fields are present and well-formed before writing output.
"""
import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger("ATJ.validator")

REQUIRED_FIELDS = ["id", "title", "availability", "condition", "price", "link", "image_link"]
VALID_AVAILABILITY = {"in stock", "out of stock", "preorder", "available for order", "discontinued"}
VALID_CONDITION = {"new", "used", "refurbished"}
PRICE_PATTERN = re.compile(r"^\d+(\.\d{1,2})?\s+[A-Z]{3}$")


@dataclass
class ValidationResult:
    valid_rows: list[dict] = field(default_factory=list)
    invalid_rows: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.valid_rows) + len(self.invalid_rows)

    def summary(self) -> str:
        return (
            f"{len(self.valid_rows)}/{self.total} rows passed validation "
            f"({len(self.invalid_rows)} rejected)."
        )


class CatalogValidator:
    """Validates mapped product dicts against Meta catalog requirements."""

    def validate_record(self, record: dict, row_index: int) -> list[str]:
        row_errors = []

        for field_name in REQUIRED_FIELDS:
            value = record.get(field_name, "")
            if value in ("", None):
                row_errors.append(f"Row {row_index}: missing required field '{field_name}'")

        availability = str(record.get("availability", "")).lower()
        if availability and availability not in VALID_AVAILABILITY:
            row_errors.append(f"Row {row_index}: invalid availability '{availability}'")

        condition = str(record.get("condition", "")).lower()
        if condition and condition not in VALID_CONDITION:
            row_errors.append(f"Row {row_index}: invalid condition '{condition}'")

        price = str(record.get("price", ""))
        if price and not PRICE_PATTERN.match(price):
            row_errors.append(f"Row {row_index}: price '{price}' not in '<number> <CUR>' format")

        link = str(record.get("link", ""))
        if link and not link.startswith(("http://", "https://")):
            row_errors.append(f"Row {row_index}: link '{link}' is not a valid URL")

        image_link = str(record.get("image_link", ""))
        if image_link and not image_link.startswith(("http://", "https://")):
            row_errors.append(f"Row {row_index}: image_link '{image_link}' is not a valid URL")

        return row_errors

    def validate_all(self, records: list[dict]) -> ValidationResult:
        result = ValidationResult()

        for i, record in enumerate(records, start=1):
            row_errors = self.validate_record(record, i)
            if row_errors:
                result.invalid_rows.append(record)
                result.errors.extend(row_errors)
                for err in row_errors:
                    logger.warning(err)
            else:
                result.valid_rows.append(record)

        logger.info(result.summary())
        return result
