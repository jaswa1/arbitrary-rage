# Technical Specifications: Arbitrage Detection System MVP

## System Architecture Overview

The Arbitrage Detection System is built using a modern microservices architecture designed for scalability, maintainability, and performance.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Processing     │    │   User Interface│
│                 │    │                 │    │                 │
│ • TCGPlayer     │────│ • Web Scrapers  │────│ • Dashboard     │
│ • eBay          │    │ • Price Engine  │    │ • API Endpoints │
│ • Distributors  │    │ • Alert System  │    │ • Admin Panel   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Data Layer    │
                    │                 │
                    │ • PostgreSQL    │
                    │ • Redis Cache   │
                    │ • File Storage  │
                    └─────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy ORM
- **Cache**: Redis 7+ for caching and session management
- **Task Queue**: Celery with Redis broker for background processing
- **Web Scraping**: aiohttp, BeautifulSoup, Scrapy for data collection

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS for utility-first styling
- **State Management**: React Query for server state management
- **UI Components**: Headless UI for accessible components

### Infrastructure
- **Containerization**: Docker & Docker Compose for development
- **Cloud**: AWS/GCP for production deployment
- **Monitoring**: Prometheus + Grafana for metrics and monitoring
- **CI/CD**: GitHub Actions for automated testing and deployment

## Database Schema

### Core Tables

#### Products Table
Stores information about both sealed products and individual cards.

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    set_name VARCHAR(100),
    product_type VARCHAR(50) NOT NULL, -- 'sealed', 'single'
    category VARCHAR(50) NOT NULL, -- 'mtg', 'pokemon', 'yugioh'
    tcg_product_id VARCHAR(100) UNIQUE,
    ebay_product_id VARCHAR(100),
    amazon_asin VARCHAR(20),
    description TEXT,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Price History Table
Tracks price changes over time from various sources.

```sql
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    price DECIMAL(10,2) NOT NULL,
    condition VARCHAR(20) DEFAULT 'near_mint',
    source VARCHAR(50) NOT NULL, -- 'tcgplayer', 'ebay', 'amazon'
    source_url VARCHAR(500),
    seller_count INTEGER,
    available_quantity INTEGER,
    shipping_cost DECIMAL(10,2),
    price_type VARCHAR(20) DEFAULT 'market',
    is_foil BOOLEAN DEFAULT FALSE,
    confidence_level VARCHAR(20) DEFAULT 'high',
    data_source_quality DECIMAL(3,2) DEFAULT 1.0,
    recorded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Arbitrage Opportunities Table
Stores calculated arbitrage opportunities with risk assessment.

```sql
CREATE TABLE arbitrage_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sealed_product_id UUID REFERENCES products(id),
    sealed_price DECIMAL(10,2) NOT NULL,
    singles_value DECIMAL(10,2) NOT NULL,
    margin_percentage DECIMAL(5,2) NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL, -- 0.00 to 1.00
    risk_level VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high'
    seller_count INTEGER,
    competition_level VARCHAR(20) DEFAULT 'unknown',
    status VARCHAR(20) DEFAULT 'active',
    execution_quantity INTEGER DEFAULT 0,
    execution_notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    executed_at TIMESTAMP
);
```

#### Product Singles Mapping
Defines the relationship between sealed products and their component singles.

```sql
CREATE TABLE product_singles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sealed_product_id UUID REFERENCES products(id),
    single_product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    guaranteed BOOLEAN DEFAULT TRUE, -- vs. random pull
    rarity VARCHAR(20),
    pull_probability DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sealed_product_id, single_product_id)
);
```

## API Design

### RESTful Endpoints

#### Products API
- `GET /api/v1/products/` - List products with filtering
- `POST /api/v1/products/` - Create new product
- `GET /api/v1/products/{id}` - Get specific product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Soft delete product
- `GET /api/v1/products/{id}/price-history` - Get price history
- `POST /api/v1/products/{id}/refresh-price` - Trigger price refresh

#### Opportunities API
- `GET /api/v1/opportunities/` - List opportunities with filtering
- `GET /api/v1/opportunities/{id}` - Get specific opportunity
- `POST /api/v1/opportunities/{id}/execute` - Execute opportunity
- `PUT /api/v1/opportunities/{id}` - Update opportunity
- `DELETE /api/v1/opportunities/{id}` - Cancel opportunity
- `GET /api/v1/opportunities/stats/summary` - Get statistics
- `POST /api/v1/opportunities/analyze-all` - Trigger analysis

### Request/Response Models

All API endpoints use Pydantic models for request validation and response serialization:

```python
class ProductCreate(BaseModel):
    name: str
    product_type: str  # 'sealed' or 'single'
    category: str      # 'mtg', 'pokemon', 'yugioh'
    set_name: Optional[str] = None
    tcg_product_id: Optional[str] = None

class ArbitrageOpportunity(BaseModel):
    id: UUID4
    sealed_product_id: UUID4
    sealed_price: Decimal
    singles_value: Decimal
    margin_percentage: Decimal
    confidence_score: Decimal
    risk_level: str
    status: str
    created_at: datetime
```

## Background Processing

### Celery Task Queue

The system uses Celery for background processing with two main queues:

#### Scraping Queue
- `update_product_prices()` - Update prices for specific products
- `update_all_prices()` - Update prices for all tracked products
- `scrape_new_products()` - Discover new products

#### Analysis Queue
- `analyze_product_arbitrage()` - Analyze single product for opportunities
- `analyze_all_products()` - Analyze all products for opportunities
- `cleanup_expired_opportunities()` - Remove expired opportunities
- `send_opportunity_alert()` - Send notifications for new opportunities

### Scheduled Tasks

```python
beat_schedule = {
    'update-prices-every-4-hours': {
        'task': 'app.tasks.scraping_tasks.update_all_prices',
        'schedule': 4 * 60 * 60,  # Every 4 hours
    },
    'analyze-opportunities-every-6-hours': {
        'task': 'app.tasks.analysis_tasks.analyze_all_products',
        'schedule': 6 * 60 * 60,  # Every 6 hours
    },
}
```

## Web Scraping Architecture

### Base Scraper Pattern

```python
class BaseScraper(ABC):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.rate_limit_delay = settings.SCRAPING_DELAY_MS / 1000
        
    @abstractmethod
    async def scrape_product_price(self, product_id: str) -> Optional[ScrapedPrice]:
        pass
    
    @abstractmethod
    async def search_products(self, query: str) -> List[Dict]:
        pass
```

### Site-Specific Scrapers
- **TCGPlayerScraper**: Primary source for MTG pricing
- **eBayScraper**: Secondary pricing and availability data
- **AmazonScraper**: Retail pricing for sealed products
- **CardMarketScraper**: European pricing data (future)

### Rate Limiting & Ethics
- Respectful scraping with 2-second delays between requests
- User-Agent rotation and proxy support
- Compliance with robots.txt
- Error handling and retry logic

## Arbitrage Detection Algorithm

### Core Analysis Process

1. **Price Collection**: Gather latest prices for sealed products and singles
2. **Margin Calculation**: Calculate profit margins after fees and shipping
3. **Risk Assessment**: Evaluate market conditions and competition
4. **Confidence Scoring**: Multi-factor confidence algorithm
5. **Opportunity Ranking**: Prioritize by margin, confidence, and risk

### Confidence Scoring Factors

```python
confidence_weights = {
    'price_stability': 0.3,    # Lower volatility = higher confidence
    'seller_count': 0.2,       # Fewer sellers = higher opportunity
    'volume_history': 0.2,     # Consistent volume = higher confidence  
    'margin_size': 0.3         # Realistic margins = higher confidence
}
```

### Risk Level Assessment

- **Low Risk**: High confidence (≥0.8) + High margin (≥50%)
- **Medium Risk**: Medium confidence (≥0.6) + Medium margin (≥30%)
- **High Risk**: All other combinations

## Performance Considerations

### Database Optimization
- Strategic indexing on frequently queried columns
- Connection pooling for efficient database access
- Query optimization using SQLAlchemy ORM best practices
- Partitioning for large price history tables

### Caching Strategy
- Redis caching for frequently accessed product data
- API response caching for static data
- Database query result caching for expensive operations

### Background Processing
- Distributed task processing using Celery workers
- Task prioritization and retry logic
- Graceful error handling and alerting

## Security & Compliance

### Data Protection
- Environment variable management for sensitive configuration
- Database connection encryption
- API authentication and authorization
- Input validation and sanitization

### Scraping Ethics
- Respect for website terms of service
- Rate limiting to avoid overwhelming target sites
- Proper attribution and data usage policies
- Compliance with GDPR and data protection regulations

## Monitoring & Observability

### Metrics Collection
- Application performance metrics via Prometheus
- Business metrics (opportunities found, margins, etc.)
- Infrastructure metrics (database, Redis, API response times)
- Custom dashboards in Grafana

### Logging Strategy
- Structured logging using structlog
- Different log levels for development vs. production
- Error tracking and alerting
- Audit logging for important business events

## Deployment Architecture

### Development Environment
- Docker Compose for local development
- Hot reloading for rapid development
- Separate containers for each service
- Volume mounting for code changes

### Production Environment
- Kubernetes deployment for scalability
- Horizontal pod autoscaling
- Load balancing and service discovery  
- Managed database and Redis instances
- CI/CD pipeline with automated testing

This technical specification provides the foundation for building a robust, scalable arbitrage detection system capable of identifying and capitalizing on market inefficiencies across multiple product categories.