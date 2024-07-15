# Product Scraping Tool

This is a Python FastAPI-based web application for scraping product information from a target website. The tool scrapes product names, prices, and images, stores the data in a database, and supports various configurable settings such as limiting the number of pages to scrape and using a proxy for scraping.

## Features

- Scrapes product name, price, and image from the target website.
- Supports limiting the number of pages to scrape.
- Supports using a proxy for scraping.
- Stores scraped information in a local JSON file.
- Notifies about the scraping status.
- Includes a simple authentication mechanism using a static token.
- Implements scraping results caching to avoid redundant updates.

