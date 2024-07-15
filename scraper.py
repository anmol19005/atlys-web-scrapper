import asyncio
import json
from typing import List, Dict

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

import config
from notifier import ConsoleNotifier, Notifier
from models import Product
from schemas import ScrapeSettings
from utils import save_image, get_redis_client


class Scraper:
    def __init__(self, settings: ScrapeSettings, db: Session,notifier: Notifier = ConsoleNotifier()):
        self.settings = settings
        self.db = db
        self.client = httpx.AsyncClient(
            proxies={"http": settings.proxy, "https": settings.proxy} if settings.proxy else None)
        self.redis = get_redis_client()
        self.notifier = notifier

    async def fetch_page(self, page: int):
        base_url = config.Config.WEBSITE_URL
        url = base_url if page == 1 else f"{base_url}page/{page}"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError:
            await asyncio.sleep(2)
            return await self.fetch_page(page)

    async def scrape(self):
        scraped_count = 0
        scraped_products = []
        for page in range(1, self.settings.pages + 1):
            html = await self.fetch_page(page)
            soup = BeautifulSoup(html, "html.parser")
            products = soup.select("ul.products .product")

            for product in products:
                title_element = product.select_one("div.mf-product-thumbnail img")
                if title_element:
                    title = title_element.get("title", "").strip()
                else:
                    title = "No title found"

                discounted_price_element = product.select_one("span.price ins .woocommerce-Price-amount")
                original_price_element = product.select_one("span.price .woocommerce-Price-amount bdi")

                if discounted_price_element:
                    price = float(discounted_price_element.text.strip().replace("₹", "").replace(",", ""))
                else:
                    if original_price_element:
                        price = float(original_price_element.text.strip().replace("₹", "").replace(",", ""))
                    else:
                        price = 0.0

                image_url = product.select_one(".mf-product-thumbnail img")["data-lazy-src"]

                if not self.is_updated(title, price):
                    image_path = await save_image(image_url)
                    product_data = Product(title=title, price=price, image_path=image_path)
                    self.save_product(product_data)
                    scraped_products.append({
                        "product_title": title,
                        "product_price": price,
                        "path_to_image": image_path
                    })

                    self.export_to_json(scraped_products)
                    scraped_count += 1

        await self.client.aclose()
        self.notifier.notify(f"Scraped {scraped_count} products")
        # print(f"Scraped {scraped_count} products")
        return {"scraped": scraped_count}

    def is_updated(self, title: str, price: float):
        try:
            cached_price = self.redis.get(title)
            if cached_price is not None and float(cached_price) == price:
                return True
            self.redis.set(title, price)
            return False
        except Exception as e:
            print(f"Error in is_updated for title '{title}': {e}")
            return False

    def save_product(self, product_data: Product):
        try:
            self.db.add(product_data)
            self.db.commit()
            self.db.refresh(product_data)
            print(f"Inserted product: {product_data.title}")
        except Exception as e:
            self.db.rollback()
            print(f"Failed to insert product: {product_data.title}. Error: {str(e)}")

    def export_to_json(self, data: List[Dict]):
        summary = {"new_records": 0, "existing_records": 0}

        try:
            with open('scraped_data.json', 'r+') as f:
                file_data = json.load(f)

                existing_titles = {item["product_title"] for item in file_data}
                new_data = [item for item in data if item["product_title"] not in existing_titles]

                if new_data:
                    file_data.extend(new_data)
                    f.seek(0)
                    json.dump(file_data, f, indent=4)

        except FileNotFoundError:
            with open('scraped_data.json', 'w') as f:
                json.dump(data, f, indent=4)
