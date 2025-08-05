"""
Base scraper class with common functionality for all scrapers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import asyncio
import random

from app.core.config import settings
from app.core.logging import logger, LoggerMixin


@dataclass
class ScrapedPrice:
    """Data class for scraped price information."""
    
    product_id: str
    price: float
    condition: str
    seller_count: int
    source: str
    timestamp: datetime
    source_url: Optional[str] = None
    available_quantity: Optional[int] = None
    shipping_cost: Optional[float] = None
    confidence_level: str = "high"


class BaseScraper(ABC, LoggerMixin):
    """
    Abstract base class for all scrapers.
    
    Provides common functionality like rate limiting, error handling,
    and standard interfaces for scraping operations.
    """
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self.rate_limit_delay = settings.SCRAPING_DELAY_MS / 1000
        self.max_retries = 3
        self.timeout = aiohttp.ClientTimeout(total=30)
        
        # Common headers to appear more like a real browser
        self.headers = {
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    @abstractmethod
    async def scrape_product_price(self, product_id: str) -> Optional[ScrapedPrice]:
        """
        Scrape price for a single product.
        
        Args:
            product_id: Unique identifier for the product on the source site
            
        Returns:
            ScrapedPrice object if successful, None otherwise
        """
        pass
    
    @abstractmethod
    async def search_products(self, query: str) -> List[Dict]:
        """
        Search for products by name/query.
        
        Args:
            query: Search term or product name
            
        Returns:
            List of product dictionaries containing basic info
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this scraper's source (e.g., 'tcgplayer')."""
        pass
    
    async def rate_limit(self):
        """Apply rate limiting between requests with some randomization."""
        # Add some randomization to avoid detection
        delay = self.rate_limit_delay + random.uniform(0, 0.5)
        await asyncio.sleep(delay)
    
    async def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[aiohttp.ClientResponse]:
        """
        Make an HTTP request with error handling and retries.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for aiohttp request
            
        Returns:
            Response object if successful, None otherwise
        """
        session = self.session or aiohttp.ClientSession()
        
        for attempt in range(self.max_retries):
            try:
                await self.rate_limit()
                
                # Merge headers
                request_headers = {**self.headers, **kwargs.get('headers', {})}
                kwargs['headers'] = request_headers
                kwargs['timeout'] = self.timeout
                
                async with session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return response
                    elif response.status == 429:  # Rate limited
                        wait_time = 2 ** attempt  # Exponential backoff
                        self.logger.warning(
                            "Rate limited, waiting",
                            url=url,
                            wait_time=wait_time,
                            attempt=attempt + 1
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        self.logger.warning(
                            "HTTP error",
                            url=url,
                            status=response.status,
                            attempt=attempt + 1
                        )
                        
            except asyncio.TimeoutError:
                self.logger.warning(
                    "Request timeout",
                    url=url,
                    attempt=attempt + 1
                )
            except Exception as e:
                self.logger.error(
                    "Request error",
                    url=url,
                    error=str(e),
                    attempt=attempt + 1
                )
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        self.logger.error("All retry attempts failed", url=url)
        
        # Clean up session if we created it
        if not self.session:
            await session.close()
            
        return None
    
    async def get_page_content(self, url: str) -> Optional[str]:
        """
        Get the HTML content of a page.
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content as string if successful, None otherwise
        """
        response = await self.make_request(url)
        if response:
            try:
                content = await response.text()
                return content
            except Exception as e:
                self.logger.error("Error reading response content", url=url, error=str(e))
        
        return None
    
    def validate_price(self, price: float) -> bool:
        """
        Validate that a scraped price is reasonable.
        
        Args:
            price: Price to validate
            
        Returns:
            True if price seems valid, False otherwise
        """
        if price <= 0:
            return False
        
        # Reasonable upper bound for card prices (adjust as needed)
        if price > 10000:
            self.logger.warning("Suspiciously high price", price=price)
            return False
        
        return True
    
    def extract_numeric_value(self, text: str) -> Optional[float]:
        """
        Extract numeric value from text (e.g., '$123.45' -> 123.45).
        
        Args:
            text: Text containing a numeric value
            
        Returns:
            Extracted float value or None if not found
        """
        import re
        
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[$,\s]', '', text)
        
        # Find decimal number
        match = re.search(r'(\d+(?:\.\d{2})?)', cleaned)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        return None
    
    def extract_integer_value(self, text: str) -> Optional[int]:
        """
        Extract integer value from text.
        
        Args:
            text: Text containing an integer
            
        Returns:
            Extracted integer or None if not found
        """
        import re
        
        match = re.search(r'(\d+)', text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        
        return None