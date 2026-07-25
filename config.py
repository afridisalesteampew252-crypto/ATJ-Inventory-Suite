"""
Centralized configuration: paths, URL patterns, and constants.
"""
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
INPUT_FOLDER = BASE_DIR / "input"
OUTPUT_FOLDER = BASE_DIR / "output"
LOG_FOLDER = BASE_DIR / "logs"

# Ensure output & log directories exist at import time
OUTPUT_FOLDER.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)
INPUT_FOLDER.mkdir(exist_ok=True)

# URL & Image Endpoints
BASE_URL = "https://www.afriditrading.com"
DEFAULT_CURRENCY = "USD"

IMAGE_PATHS = {
    "stock": "https://erp.afriditrading.com/storage/stock-images/{}/1.jfif",
    "auction": "https://erp.afriditrading.com/storage/auction-stock-images/{}/F.png",
}

# Column aliases the ERP reader will try, in priority order, per logical field.
# This makes the mapper resilient to header-name drift in ERP exports.
COLUMN_ALIASES = {
    "stock_id": ["Stock ID", "stock_id", "StockID", "Stock No", "Stock Number"],
    "year": ["Year", "Model Year"],
    "make": ["Make", "Maker", "Manufacturer"],
    "model": ["Model", "Model Name"],
    "price": ["Price", "FOB Price", "FOB", "Sale Price"],
    "mileage": ["Mileage", "Odometer", "KM"],
    "transmission": ["Transmission", "Gearbox"],
    "fuel": ["Fuel", "Fuel Type"],
    "color": ["Color", "Colour"],
    "engine_cc": ["Engine CC", "Displacement", "CC"],
    "image_type": ["Image Type", "Source Type"],  # "stock" or "auction"
}

APP_NAME = "ATJ Facebook Catalog Generator"
APP_VERSION = "1.0.0"
