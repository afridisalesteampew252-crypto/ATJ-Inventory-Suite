"""
Maps normalized ERP records to Meta (Facebook) Product Catalog schema fields.
Reference: https://www.facebook.com/business/help/120325381656392
"""
import logging

from config import BASE_URL, DEFAULT_CURRENCY, IMAGE_PATHS
from core.excel_reader import ERPReader

logger = logging.getLogger("ATJ.facebook_mapper")


class FacebookMapper:
    """Maps ERP record keys to standard Meta Facebook Catalog fields."""

    def map_record(self, record: dict) -> dict:
        resolve = ERPReader.resolve_field

        stock_id = str(resolve(record, "stock_id")).strip()
        year = str(resolve(record, "year")).strip()
        make = str(resolve(record, "make")).strip()
        model = str(resolve(record, "model")).strip()
        mileage = str(resolve(record, "mileage")).strip()
        transmission = str(resolve(record, "transmission")).strip()
        fuel = str(resolve(record, "fuel")).strip()
        color = str(resolve(record, "color")).strip()
        engine_cc = str(resolve(record, "engine_cc")).strip()
        image_type = str(resolve(record, "image_type")).strip().lower() or "stock"

        if not stock_id:
            logger.warning("Record missing Stock ID, skipping image link generation")

        # Build image URL using stock/auction fallback logic
        image_key = "auction" if image_type == "auction" else "stock"
        image_url = IMAGE_PATHS[image_key].format(stock_id) if stock_id else ""

        title = f"{year} {make} {model}".strip()
        title = " ".join(title.split())  # collapse extra whitespace
        if not title:
            title = f"Vehicle {stock_id}" if stock_id else "Vehicle"

        price_raw = resolve(record, "price", 0)
        try:
            price_val = float(str(price_raw).replace(",", "").strip() or 0)
        except ValueError:
            price_val = 0.0
        formatted_price = f"{price_val:.2f} {DEFAULT_CURRENCY}"

        desc_parts = [title]
        if mileage:
            desc_parts.append(f"Mileage: {mileage} km")
        if transmission:
            desc_parts.append(f"Transmission: {transmission}")
        if fuel:
            desc_parts.append(f"Fuel: {fuel}")
        if color:
            desc_parts.append(f"Color: {color}")
        if engine_cc:
            desc_parts.append(f"Engine: {engine_cc}cc")
        desc_parts.append(f"Stock ID: {stock_id}. Inspected quality import from Afridi Trading Japan.")
        description = ". ".join(desc_parts)

        return {
            "id": stock_id,
            "title": title,
            "description": description,
            "availability": "in stock",
            "condition": "used",
            "price": formatted_price,
            "link": f"{BASE_URL}/vehicle/{stock_id}" if stock_id else BASE_URL,
            "image_link": image_url,
            "brand": make or "Afridi Trading",
            "year": year,
            "model": model,
            "mileage": mileage,
            "transmission": transmission,
            "fuel_type": fuel,
            "color": color,
        }

    def map_all(self, records: list[dict]) -> list[dict]:
        mapped = []
        for i, rec in enumerate(records):
            if not rec:
                continue
            try:
                mapped.append(self.map_record(rec))
            except Exception:  # noqa: BLE001
                logger.exception("Failed to map record at index %d", i)
        return mapped
