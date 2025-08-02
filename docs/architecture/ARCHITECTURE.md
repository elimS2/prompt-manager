# Architecture Documentation

## Overview

Prompt Manager follows a clean architecture pattern with clear separation of concerns. The application is structured in layers, each with specific responsibilities and dependencies flowing inward.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Presentation Layer                      │
│  ┌─────────────────┐          ┌──────────────────────────┐  │
│  │   Web UI        │          │      RESTful API         │  │
│  │  (Templates)    │          │   (API Controllers)      │  │
│  └────────┬────────┘          └──────────┬───────────────┘  │
└───────────┼───────────────────────────────┼─────────────────┘
            │                               │
┌───────────┼───────────────────────────────┼─────────────────┐
│           │         Controller Layer      │                  │
│  ┌────────▼────────┐          ┌──────────▼───────────────┐  │
│  │ Web Controllers │          │    API Controllers       │  │
│  │(prompt_controller)         │   (api_controller)       │  │
│  └────────┬────────┘          └──────────┬───────────────┘  │
└───────────┼───────────────────────────────┼─────────────────┘
            │                               │
┌───────────┼───────────────────────────────┼─────────────────┐
│           │         Service Layer         │                  │
│  ┌────────▼──────────────────────────────▼───────────────┐  │
│  │              Business Logic Services                   │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │  │
│  │  │PromptService│ │ TagService   │ │ MergeService   │ │  │
│  │  └──────┬──────┘ └──────┬───────┘ └────────┬───────┘ │  │
│  └─────────┼───────────────┼──────────────────┼─────────┘  │
└────────────┼───────────────┼──────────────────┼────────────┘
             │               │                  │
┌────────────┼───────────────┼──────────────────┼────────────┐
│            │      Repository Layer           │             │
│  ┌─────────▼────┐ ┌────────▼──────┐ ┌───────▼─────────┐  │
│  │PromptRepo    │ │ TagRepo       │ │ BaseRepository  │  │
│  └─────────┬────┘ └────────┬──────┘ └────────┬────────┘  │
└────────────┼───────────────┼─────────────────┼────────────┘
             │               │                 │
┌────────────┼───────────────┼─────────────────┼────────────┐
│            │         Model Layer             │             │
│  ┌─────────▼────┐ ┌────────▼──────┐ ┌───────▼─────────┐  │
│  │ Prompt       │ │ Tag           │ │ BaseModel       │  │
│  └──────────────┘ └───────────────┘ └─────────────────┘  │
└────────────────────────────────────────────────────────────┘
             │               │                 │
┌────────────▼───────────────▼─────────────────▼────────────┐
│                      Database (SQLite)                     │
└────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Presentation Layer
- **Templates**: Jinja2 HTML templates for web UI
- **Static Assets**: CSS, JavaScript, images
- **Responsibilities**: 
  - Render HTML pages
  - Handle user interactions
  - Display data to users

### 2. Controller Layer
- **Web Controllers**: Handle HTTP requests for web interface
- **API Controllers**: Handle RESTful API requests
- **Responsibilities**:
  - Route requests to appropriate services
  - Validate request data
  - Format responses
  - Handle HTTP-specific concerns

### 3. Service Layer
- **Business Logic**: Core application functionality
- **Responsibilities**:
  - Implement business rules
  - Orchestrate operations
  - Validate business logic
  - Handle transactions

### 4. Repository Layer
- **Data Access**: Abstract database operations
- **Responsibilities**:
  - CRUD operations
  - Complex queries
  - Data persistence
  - Database abstraction

### 5. Model Layer
- **Domain Entities**: Core business objects
- **Responsibilities**:
  - Define data structure
  - Implement entity-specific logic
  - Validate entity state

## Design Patterns Used

### Repository Pattern
Provides an abstraction over data access, allowing the business logic to remain agnostic of the data source.

```python
class BaseRepository(Generic[ModelType]):
    def get_by_id(self, id: int) -> Optional[ModelType]
    def create(self, **data) -> ModelType
    def update(self, id: int, **data) -> Optional[ModelType]
    def delete(self, id: int) -> bool
```

### Service Layer Pattern
Encapsulates business logic and orchestrates operations across multiple repositories.

```python
class PromptService:
    def __init__(self, prompt_repo, tag_repo):
        self.prompt_repo = prompt_repo
        self.tag_repo = tag_repo
    
    def create_prompt(self, data: Dict) -> Prompt:
        # Business logic here
```

### Factory Pattern
Application factory creates app instances for different environments.

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Initialize extensions
    return app
```

### Dependency Injection
Services receive their dependencies rather than creating them.

```python
# Dependencies injected via constructor
service = PromptService(
    prompt_repo=PromptRepository(),
    tag_repo=TagRepository()
)
```

## Key Architectural Decisions

### 1. Layered Architecture
**Decision**: Use a layered architecture with clear boundaries
**Rationale**: 
- Separation of concerns
- Easy to test individual layers
- Flexibility to change implementations
- Clear dependency flow

### 2. Repository Pattern
**Decision**: Abstract data access behind repositories
**Rationale**:
- Decouple business logic from database
- Easier testing with mocks
- Potential to switch databases
- Consistent data access patterns

### 3. Service Layer
**Decision**: Implement business logic in service classes
**Rationale**:
- Keep controllers thin
- Reusable business logic
- Transaction boundaries
- Easier testing

### 4. Server-Side Rendering
**Decision**: Use Jinja2 templates instead of SPA
**Rationale**:
- Simpler architecture
- Better SEO
- Works without JavaScript
- Faster initial page load

### 5. Dual Interface (Web + API)
**Decision**: Provide both web UI and RESTful API
**Rationale**:
- Support different client types
- API for automation/integration
- Web UI for human users
- Shared business logic

## Data Flow Example

Here's how a request flows through the layers:

1. **User Action**: User clicks "Create Prompt" button
2. **HTTP Request**: POST /prompts/create
3. **Controller**: 
   - `prompt_controller.create()` receives request
   - Extracts data from form
   - Calls service layer
4. **Service**: 
   - `PromptService.create_prompt()` validates business rules
   - Processes tags
   - Calls repository
5. **Repository**: 
   - `PromptRepository.create()` persists to database
   - Returns created entity
6. **Response**: 
   - Controller renders success page
   - Or returns JSON for API

## Security Considerations

### Input Validation
- Controllers validate request format
- Services validate business rules
- Models validate data integrity

### SQL Injection Prevention
- Use SQLAlchemy ORM with parameterized queries
- Never construct SQL strings manually

### XSS Prevention
- Jinja2 auto-escapes template variables
- Validate and sanitize user input

### CSRF Protection
- Flask-WTF CSRF tokens for forms
- Can be enabled via configuration

## Performance Optimizations

### Database
- Indexes on frequently queried fields
- Lazy loading for relationships
- Pagination for large datasets

### Caching Strategy
- Static assets cached by browser
- Database query results (future enhancement)
- Template caching (future enhancement)

### Query Optimization
- Eager loading for known relationships
- Bulk operations where possible
- Efficient filtering at database level

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock dependencies
- Focus on business logic

### Integration Tests
- Test component interactions
- Use test database
- Verify API contracts

### Test Organization
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_repositories.py
│   └── test_services.py
├── integration/
│   └── test_api.py
└── conftest.py  # Shared fixtures
```

## Future Enhancements

### Scalability
- Database connection pooling
- Redis for caching
- Background job queue
- Horizontal scaling with load balancer

### Features
- User authentication
- Real-time collaboration
- Prompt versioning
- Export/Import functionality

### Technical Debt
- Add comprehensive logging
- Implement rate limiting
- Add API versioning
- Database migrations