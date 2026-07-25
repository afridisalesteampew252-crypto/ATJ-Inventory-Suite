"""
Validates and, where possible, repairs image URLs for catalog rows.
Supports JFIF, PNG, and JPG stock/auction image conventions.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm

from config import IMAGE_PATHS

logger = logging.getLogger("ATJ.image_matcher")

# Extensions to try, in priority order, when the default extension 404s.
FALLBACK_EXTENSIONS = {
    "stock": ["1.jfif", "1.jpg", "1.png", "1.jpeg"],
    "auction": ["F.png", "F.jpg", "F.jfif", "1.png"],
}

TIMEOUT_SECONDS = 6


class ImageMatcher:
    """Checks whether generated image URLs actually resolve, with graceful fallback."""

    def __init__(self, max_workers: int = 8, verify: bool = True):
        self.max_workers = max_workers
        self.verify = verify

    def _url_exists(self, url: str) -> bool:
        try:
            resp = requests.head(url, timeout=TIMEOUT_SECONDS, allow_redirects=True)
            if resp.status_code == 405:  # some servers disallow HEAD
                resp = requests.get(url, timeout=TIMEOUT_SECONDS, stream=True)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def resolve_image_for_stock(self, stock_id: str, image_type: str = "stock") -> str:
        """Try the default pattern first, then fall back through known extensions."""
        base_template = IMAGE_PATHS.get(image_type, IMAGE_PATHS["stock"])
        default_url = base_template.format(stock_id)

        if not self.verify:
            return default_url

        if self._url_exists(default_url):
            return default_url

        for filename in FALLBACK_EXTENSIONS.get(image_type, []):
            candidate = base_template.rsplit("/", 1)[0] + f"/{stock_id}/{filename}"
            if self._url_exists(candidate):
                return candidate

        logger.warning("No valid image found for stock_id=%s (type=%s)", stock_id, image_type)
        return default_url  # return best-guess even if unverified, so pipeline doesn't break

    def verify_all(self, products: list[dict]) -> list[dict]:
        """
        Runs concurrent verification across all products' image_link fields.
        Mutates and returns the same list with corrected image_link values.
        """
        if not self.verify:
            return products

        def _check(idx_product):
            idx, product = idx_product
            stock_id = product.get("id", "")
            if not stock_id:
                return idx, product.get("image_link", "")
            resolved = self.resolve_image_for_stock(stock_id)
            return idx, resolved

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(_check, item) for item in enumerate(products)]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Verifying images"):
                idx, resolved_url = future.result()
                products[idx]["image_link"] = resolved_url

        return products
