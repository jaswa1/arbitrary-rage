"""
System configuration model for storing application settings.
"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class SystemConfig(Base):
    """
    Model for storing system-wide configuration settings.
    
    This model allows for dynamic configuration changes without
    requiring application restarts.
    """
    
    __tablename__ = "system_config"
    
    # Primary key (configuration key)
    key = Column(String(100), primary_key=True)
    
    # Configuration value
    value = Column(Text, nullable=False)
    
    # Metadata
    description = Column(Text, nullable=True)
    data_type = Column(String(20), default="string", nullable=False)  # 'string', 'int', 'float', 'bool', 'json'
    category = Column(String(50), default="general", nullable=False)  # 'scraping', 'alerts', 'business', etc.
    
    # Access control
    is_sensitive = Column(String(10), default="false", nullable=False)  # Contains sensitive data
    is_editable = Column(String(10), default="true", nullable=False)   # Can be edited via UI
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value[:50]}...')>"
    
    @property
    def value_as_bool(self) -> bool:
        """Get value as boolean."""
        return self.value.lower() in ('true', '1', 'yes', 'on')
    
    @property
    def value_as_int(self) -> int:
        """Get value as integer."""
        return int(self.value)
    
    @property
    def value_as_float(self) -> float:
        """Get value as float."""
        return float(self.value)
    
    @classmethod
    def get_default_configs(cls):
        """Get default system configurations."""
        return [
            {
                'key': 'min_margin_threshold',
                'value': '25.0',
                'description': 'Minimum margin percentage to flag opportunities',
                'data_type': 'float',
                'category': 'business'
            },
            {
                'key': 'max_risk_level',
                'value': 'medium',
                'description': 'Maximum risk level for auto-alerts',
                'data_type': 'string',
                'category': 'business'
            },
            {
                'key': 'price_update_interval',
                'value': '14400',
                'description': 'Price update interval in seconds (4 hours)',
                'data_type': 'int',
                'category': 'scraping'
            },
            {
                'key': 'default_price_floor',
                'value': '0.35',
                'description': 'Default minimum price for MTG singles',
                'data_type': 'float',
                'category': 'business'
            },
            {
                'key': 'scraping_delay_ms',
                'value': '2000',
                'description': 'Delay between scraping requests in milliseconds',
                'data_type': 'int',
                'category': 'scraping'
            },
            {
                'key': 'max_concurrent_scraping',
                'value': '10',
                'description': 'Maximum concurrent scraping requests',
                'data_type': 'int',
                'category': 'scraping'
            },
            {
                'key': 'enable_auto_alerts',
                'value': 'true',
                'description': 'Enable automatic alert sending',
                'data_type': 'bool',
                'category': 'alerts'
            },
            {
                'key': 'alert_cooldown_minutes',
                'value': '60',
                'description': 'Minimum minutes between alerts for same opportunity',
                'data_type': 'int',
                'category': 'alerts'
            }
        ]