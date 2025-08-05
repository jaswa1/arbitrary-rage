"""
Arbitrage opportunity models for tracking profitable opportunities.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ArbitrageOpportunity(Base):
    """
    Model for tracking arbitrage opportunities between sealed products and singles.
    
    This model stores calculated arbitrage opportunities with margins, confidence scores,
    and risk assessments.
    """
    
    __tablename__ = "arbitrage_opportunities"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign key to sealed product
    sealed_product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("products.id"), 
        nullable=False,
        index=True
    )
    
    # Financial data
    sealed_price = Column(DECIMAL(10, 2), nullable=False)
    singles_value = Column(DECIMAL(10, 2), nullable=False)
    margin_percentage = Column(DECIMAL(5, 2), nullable=False, index=True)
    
    # Risk assessment
    confidence_score = Column(DECIMAL(3, 2), nullable=False)  # 0.00 to 1.00
    risk_level = Column(String(20), nullable=False, index=True)  # 'low', 'medium', 'high'
    
    # Market data
    seller_count = Column(Integer, nullable=True)
    competition_level = Column(String(20), default="unknown")  # 'low', 'medium', 'high'
    
    # Status tracking
    status = Column(String(20), default="active", nullable=False, index=True)  # 'active', 'expired', 'executed'
    execution_quantity = Column(Integer, default=0)
    execution_notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sealed_product = relationship("Product", foreign_keys=[sealed_product_id])
    alerts = relationship("UserAlert", back_populates="opportunity")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_opportunity_margin_confidence', 'margin_percentage', 'confidence_score'),
        Index('idx_opportunity_status_created', 'status', 'created_at'),
        Index('idx_opportunity_risk_margin', 'risk_level', 'margin_percentage'),
        Index('idx_opportunity_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<ArbitrageOpportunity(id={self.id}, margin={self.margin_percentage}%, status='{self.status}')>"
    
    @property
    def potential_profit(self) -> float:
        """Calculate potential profit in dollars."""
        net_singles_value = float(self.singles_value) * 0.85  # Assuming 15% fees
        return net_singles_value - float(self.sealed_price)
    
    @property
    def is_active(self) -> bool:
        """Check if opportunity is still active."""
        return self.status == "active"
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if opportunity has high confidence."""
        return float(self.confidence_score) >= 0.8


class ProductSingle(Base):
    """
    Mapping table between sealed products and their component singles.
    
    This model defines what singles are contained in each sealed product
    and in what quantities.
    """
    
    __tablename__ = "product_singles"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Foreign keys
    sealed_product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("products.id"), 
        nullable=False
    )
    single_product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("products.id"), 
        nullable=False
    )
    
    # Quantity information
    quantity = Column(Integer, nullable=False, default=1)
    guaranteed = Column(String(10), default="true", nullable=False)  # vs. random pull
    
    # Rarity/probability information (for booster products)
    rarity = Column(String(20), nullable=True)  # 'common', 'uncommon', 'rare', 'mythic'
    pull_probability = Column(DECIMAL(5, 4), nullable=True)  # Probability of pulling this card
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    sealed_product = relationship("Product", foreign_keys=[sealed_product_id])
    single_product = relationship("Product", foreign_keys=[single_product_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('sealed_product_id', 'single_product_id', name='uq_sealed_single'),
        Index('idx_product_singles_sealed', 'sealed_product_id'),
        Index('idx_product_singles_single', 'single_product_id'),
    )
    
    def __repr__(self):
        return f"<ProductSingle(sealed={self.sealed_product_id}, single={self.single_product_id}, qty={self.quantity})>"