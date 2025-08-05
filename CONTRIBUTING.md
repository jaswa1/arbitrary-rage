# Contributing to Arbitrary Rage

Welcome to the Arbitrary Rage development team! This document outlines our agent-based development process and contribution guidelines.

## 🏗️ Agent Team Structure

Our development is organized into specialized agent teams:

- **Team 1**: Database & Core Backend Architecture
- **Team 2**: API Development & Integration
- **Team 3**: Business Logic & Algorithms
- **Team 4**: Frontend Development & UX
- **Team 5**: DevOps & Infrastructure
- **Team 6**: Data Analytics & Intelligence
- **Team 7**: Quality Assurance & Testing

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- GitHub CLI (optional but recommended)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaswa1/arbitrary-rage.git
   cd arbitrary-rage
   ```

2. **Set up environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start development environment**
   ```bash
   docker-compose up -d
   ```

4. **Verify setup**
   ```bash
   curl http://localhost:8000/health  # Backend health check
   open http://localhost:3000         # Frontend dashboard
   ```

## 🔄 Development Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for ongoing development
- `feature/*`: Feature development branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical production fixes

### Agent Team Workflow

1. **Daily Standup** (9:00 AM EST)
   - Progress updates
   - Blockers identification
   - Cross-team coordination

2. **Feature Development**
   ```bash
   # Create feature branch
   git checkout -b feature/team1-product-service-enhancement
   
   # Make changes, commit frequently
   git add .
   git commit -m "feat(products): add bulk product creation endpoint"
   
   # Push and create PR
   git push origin feature/team1-product-service-enhancement
   gh pr create --title "Add bulk product creation" --body "Implements bulk product creation for Team 1"
   ```

3. **Code Review Process**
   - All PRs require review from Technical Lead
   - Cross-team PRs require review from affected teams
   - Automated tests must pass
   - Documentation must be updated

## 📋 Coding Standards

### Backend (Python)
```python
# Use type hints
async def get_product(product_id: UUID4) -> Optional[Product]:
    """Get product by ID with proper error handling."""
    pass

# Follow naming conventions
class ProductService:
    async def create_product_bulk(self, products: List[ProductCreate]) -> List[Product]:
        pass
```

**Style Guide:**
- Black for code formatting
- isort for import sorting
- flake8 for linting
- Comprehensive docstrings
- Type hints required

### Frontend (TypeScript/React)
```typescript
// Use proper TypeScript types
interface OpportunityFilters {
  min_margin?: number;
  max_risk?: 'low' | 'medium' | 'high';
}

// Follow component patterns
const Dashboard: React.FC = () => {
  // Component logic
  return <div>Dashboard content</div>;
};
```

**Style Guide:**
- ESLint + Prettier for formatting
- Strict TypeScript configuration
- Functional components with hooks
- Proper error boundaries

### Database
- Use Alembic for migrations
- Proper indexing strategy
- UUID primary keys
- Meaningful constraint names

## 🧪 Testing Requirements

### Test Coverage Requirements
- **Backend**: 85% minimum for business logic, 75% overall
- **Frontend**: 75% minimum for components
- **Integration**: All API endpoints tested

### Testing Strategy
```python
# Backend testing example
class TestArbitrageAnalyzer:
    async def test_margin_calculation(self):
        """Test margin calculation with mock data."""
        # Arrange
        analyzer = ArbitrageAnalyzer()
        sealed_price = Decimal('200.00')
        singles_value = Decimal('350.00')
        
        # Act
        margin = analyzer.calculate_margin(sealed_price, singles_value)
        
        # Assert
        assert margin > Decimal('25.0')
```

```typescript
// Frontend testing example
describe('OpportunityTable', () => {
  it('should display opportunities correctly', () => {
    const mockOpportunities = [/* mock data */];
    render(<OpportunityTable opportunities={mockOpportunities} />);
    expect(screen.getByText('Active Opportunities')).toBeInTheDocument();
  });
});
```

## 🔄 Agent Team Coordination

### Cross-Team Dependencies
Before starting work that affects other teams:

1. **Create coordination issue**
   ```markdown
   **Agent Teams Involved**: Team 2 (API), Team 4 (Frontend)
   **Coordination Required**: New API endpoint for opportunity execution
   **Timeline**: Week 3 Sprint
   ```

2. **API Contract Agreement**
   - Define request/response schemas
   - Error handling approach
   - Validation requirements

3. **Integration Testing**
   - Joint testing sessions
   - Mock data alignment
   - Error scenario testing

### Communication Protocols

#### Slack Channels
- `#tech-lead`: Technical Lead communications
- `#team-database`: Team 1 discussions
- `#team-api`: Team 2 discussions
- `#team-algorithms`: Team 3 discussions
- `#team-frontend`: Team 4 discussions
- `#team-devops`: Team 5 discussions
- `#team-analytics`: Team 6 discussions
- `#team-qa`: Team 7 discussions
- `#cross-team-coord`: Cross-team coordination

#### GitHub Labels
- `team:database` - Team 1 issues
- `team:api` - Team 2 issues
- `team:algorithms` - Team 3 issues
- `team:frontend` - Team 4 issues
- `team:devops` - Team 5 issues
- `team:analytics` - Team 6 issues
- `team:qa` - Team 7 issues
- `cross-team` - Multi-team coordination required
- `blocked` - Waiting on dependencies
- `critical` - High priority/blocking issue

## 📊 Performance Standards

### Backend Performance
- API response times: <200ms for simple queries
- Database queries: <50ms for indexed queries
- Background tasks: Process 1000+ products/hour
- Memory usage: <512MB per worker

### Frontend Performance
- Initial load: <3 seconds
- Time to interactive: <5 seconds
- Component updates: <100ms
- Bundle size: <2MB compressed

### Scraping Ethics
- Rate limiting: 2+ seconds between requests
- Respectful user agents
- Compliance with robots.txt
- No aggressive parallel requests

## 🔒 Security Guidelines

### Code Security
- No hardcoded secrets
- Input validation for all user data
- SQL injection prevention
- XSS protection in frontend

### Environment Security
- Environment variables for configuration
- Secure API key management
- Database connection encryption
- HTTPS in production

## 📝 Documentation Requirements

### Code Documentation
- Comprehensive docstrings for all functions
- API endpoint documentation
- Database schema documentation
- Architecture decision records (ADRs)

### User Documentation
- API documentation with examples
- Development setup guides
- Deployment instructions
- Troubleshooting guides

## 🚦 Definition of Done

For a feature to be considered complete:

- [ ] Code implemented and reviewed
- [ ] Tests written and passing (meeting coverage requirements)
- [ ] Documentation updated
- [ ] Cross-team integration tested (if applicable)
- [ ] Performance requirements met
- [ ] Security review completed (if applicable)
- [ ] Deployed to staging and validated
- [ ] Technical Lead approval obtained

## 🎯 Agent Team Specializations

### Team 1: Database & Core Backend
**Focus**: SQLAlchemy models, database optimization, core services
**Review Requirements**: Database schema changes, performance impact

### Team 2: API Development
**Focus**: FastAPI endpoints, external integrations, API design
**Review Requirements**: API contracts, error handling, authentication

### Team 3: Business Logic & Algorithms
**Focus**: Arbitrage detection, web scraping, core algorithms
**Review Requirements**: Algorithm accuracy, scraping ethics, performance

### Team 4: Frontend Development
**Focus**: React components, user experience, data visualization
**Review Requirements**: Component design, accessibility, performance

### Team 5: DevOps & Infrastructure
**Focus**: Docker, CI/CD, monitoring, deployment
**Review Requirements**: Infrastructure changes, security, scalability

### Team 6: Data Analytics
**Focus**: Analytics, reporting, machine learning
**Review Requirements**: Data accuracy, model performance, business value

### Team 7: Quality Assurance
**Focus**: Testing, quality metrics, performance validation
**Review Requirements**: Test coverage, quality standards, performance benchmarks

## 🤝 Getting Help

- **Technical Questions**: Ask in relevant team Slack channel
- **Cross-team Issues**: Use `#cross-team-coord` channel
- **Architecture Decisions**: Reach out to Technical Lead
- **Urgent Issues**: Create GitHub issue with `critical` label

## 📞 Contact

- **Technical Lead**: @technical-lead (GitHub: @jaswa1)
- **Project Repository**: https://github.com/jaswa1/arbitrary-rage
- **Documentation**: [Technical Specifications](docs/technical-specifications.md)

---

Thank you for contributing to Arbitrary Rage! Together, we're building a powerful arbitrage detection system that will revolutionize trading card game investments. 🚀