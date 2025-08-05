"""
Web scraping modules for collecting price data from various sources.
"""

from .base_scraper import BaseScraper, ScrapedPrice
from .tcgplayer_scraper import TCGPlayerScraper

__all__ = [
    "BaseScraper",
    "ScrapedPrice", 
    "TCGPlayerScraper"
]