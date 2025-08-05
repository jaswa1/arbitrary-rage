"""
Arbitrage analysis service for detecting profitable opportunities.
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.product import Product
from app.models.arbitrage_opportunity import ArbitrageOpportunity, ProductSingle
from app.models.price_history import PriceHistory
from app.core.database import get_db_session
from app.core.logging import logger, LoggerMixin
from app.core.config import settings


class ArbitrageAnalyzer(LoggerMixin):
    """
    Service for analyzing products and detecting arbitrage opportunities.
    
    This service implements the core business logic for:
    - Calculating margins between sealed products and singles
    - Assessing risk and confidence levels
    - Identifying market opportunities
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.min_margin_threshold = Decimal(str(settings.MIN_MARGIN_THRESHOLD))
        self.max_seller_threshold = 15  # Flag if <15 sellers
        self.confidence_weights = {
            'price_stability': 0.3,
            'seller_count': 0.2,
            'volume_history': 0.2,
            'margin_size': 0.3
        }
    
    async def analyze_sealed_product(self, sealed_product: Product) -> Optional[ArbitrageOpportunity]:
        """
        Analyze a sealed product for arbitrage potential.
        
        Args:
            sealed_product: The sealed product to analyze
            
        Returns:
            ArbitrageOpportunity if profitable, None otherwise
        """
        try:
            # Get current sealed price
            sealed_price = await self._get_latest_price(sealed_product.id, 'sealed')
            if not sealed_price:
                self.logger.warning("No sealed price found", product_id=str(sealed_product.id))
                return None
            
            # Calculate singles value
            singles_value = await self._calculate_singles_value(sealed_product.id)
            if not singles_value:
                self.logger.warning("No singles value calculated", product_id=str(sealed_product.id))
                return None
            
            # Calculate margin (after estimated fees)
            fee_rate = Decimal('0.15')  # 15% total fees (platform + payment + shipping)
            net_singles_value = singles_value * (1 - fee_rate)
            margin_percentage = ((net_singles_value - sealed_price) / sealed_price) * 100
            
            # Skip if below threshold
            if margin_percentage < self.min_margin_threshold:
                self.logger.debug(
                    "Margin below threshold", 
                    product_id=str(sealed_product.id),
                    margin=float(margin_percentage),
                    threshold=float(self.min_margin_threshold)
                )
                return None
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence(
                sealed_product, sealed_price, singles_value, margin_percentage
            )
            
            # Determine risk level
            risk_level = self._assess_risk_level(margin_percentage, confidence_score)
            
            # Get seller count
            seller_count = await self._get_seller_count(sealed_product.id)
            
            opportunity = ArbitrageOpportunity(
                sealed_product_id=sealed_product.id,
                sealed_price=sealed_price,
                singles_value=singles_value,
                margin_percentage=margin_percentage,
                confidence_score=confidence_score,
                risk_level=risk_level,
                seller_count=seller_count,
                status='active',
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            self.logger.info(
                "Arbitrage opportunity identified",
                product_id=str(sealed_product.id),
                margin=float(margin_percentage),
                confidence=float(confidence_score),
                risk=risk_level
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(
                "Error analyzing sealed product",
                product_id=str(sealed_product.id),
                error=str(e)
            )
            return None
    
    async def _calculate_singles_value(self, sealed_product_id: str) -> Optional[Decimal]:
        """Calculate total value of singles from a sealed product."""
        try:
            if self.db:
                db = self.db
            else:
                async with get_db_session() as db:
                    return await self._calculate_singles_value_with_db(db, sealed_product_id)
            
            return await self._calculate_singles_value_with_db(db, sealed_product_id)
            
        except Exception as e:
            self.logger.error("Error calculating singles value", error=str(e))
            return None
    
    async def _calculate_singles_value_with_db(self, db: Session, sealed_product_id: str) -> Optional[Decimal]:
        """Calculate singles value with database session."""
        # Get all singles in this sealed product with their latest prices
        query = db.query(
            ProductSingle.quantity,
            PriceHistory.price
        ).join(
            PriceHistory, ProductSingle.single_product_id == PriceHistory.product_id
        ).filter(
            ProductSingle.sealed_product_id == sealed_product_id
        ).filter(
            PriceHistory.recorded_at == db.query(func.max(PriceHistory.recorded_at)).filter(
                PriceHistory.product_id == ProductSingle.single_product_id
            ).scalar_subquery()
        )
        
        singles_data = query.all()
        
        if not singles_data:
            return None
        
        total_value = Decimal('0')
        for quantity, price in singles_data:
            total_value += Decimal(str(quantity)) * Decimal(str(price))
        
        return total_value
    
    async def _get_latest_price(self, product_id: str, product_type: str) -> Optional[Decimal]:
        """Get the most recent price for a product."""
        try:
            if self.db:
                db = self.db
            else:
                async with get_db_session() as db:
                    return await self._get_latest_price_with_db(db, product_id)
            
            return await self._get_latest_price_with_db(db, product_id)
            
        except Exception as e:
            self.logger.error("Error getting latest price", error=str(e))
            return None
    
    async def _get_latest_price_with_db(self, db: Session, product_id: str) -> Optional[Decimal]:
        """Get latest price with database session."""
        latest_price = db.query(PriceHistory.price).filter(
            PriceHistory.product_id == product_id
        ).order_by(PriceHistory.recorded_at.desc()).first()
        
        return Decimal(str(latest_price[0])) if latest_price else None
    
    async def _calculate_confidence(
        self, product: Product, sealed_price: Decimal, 
        singles_value: Decimal, margin_percentage: Decimal
    ) -> Decimal:
        """Calculate confidence score (0.0 to 1.0)."""
        
        scores = {}
        
        # Price stability (lower volatility = higher confidence)
        price_volatility = await self._get_price_volatility(product.id)
        scores['price_stability'] = max(0, 1 - (price_volatility / 50))  # 50% volatility = 0 confidence
        
        # Seller count (fewer sellers = higher opportunity, but lower confidence)
        seller_count = await self._get_seller_count(product.id)
        if seller_count <= 5:
            scores['seller_count'] = 0.9  # High opportunity, medium confidence
        elif seller_count <= 10:
            scores['seller_count'] = 0.7
        else:
            scores['seller_count'] = 0.3  # Too much competition
        
        # Volume history (consistent volume = higher confidence)
        volume_consistency = await self._get_volume_consistency(product.id)
        scores['volume_history'] = volume_consistency
        
        # Margin size (very high margins are suspicious)
        margin_float = float(margin_percentage)
        if margin_float > 200:
            scores['margin_size'] = 0.5  # Too good to be true?
        elif margin_float > 100:
            scores['margin_size'] = 0.8
        elif margin_float > 50:
            scores['margin_size'] = 1.0  # Sweet spot
        else:
            scores['margin_size'] = 0.7
        
        # Weighted average
        total_score = sum(
            scores[factor] * weight 
            for factor, weight in self.confidence_weights.items()
        )
        
        return Decimal(str(round(total_score, 2)))
    
    def _assess_risk_level(self, margin_percentage: Decimal, confidence_score: Decimal) -> str:
        """Assess risk level based on margin and confidence."""
        if confidence_score >= Decimal('0.8') and margin_percentage >= 50:
            return 'low'
        elif confidence_score >= Decimal('0.6') and margin_percentage >= 30:
            return 'medium'
        else:
            return 'high'
    
    async def _get_seller_count(self, product_id: str) -> int:
        """Get the number of sellers for a product."""
        # Mock implementation - in real system, get from latest price data
        return 8
    
    async def _get_price_volatility(self, product_id: str) -> float:
        """Calculate price volatility over the last 30 days."""
        # Mock implementation - calculate standard deviation of prices
        return 15.0  # 15% volatility
    
    async def _get_volume_consistency(self, product_id: str) -> float:
        """Calculate volume consistency score."""
        # Mock implementation - analyze trading volume patterns
        return 0.75  # 75% consistency