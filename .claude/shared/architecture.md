# System Architecture

## Overview

Mids Hero Web follows a modern three-tier architecture with clear separation of concerns.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React Frontend │────▶│  FastAPI Backend│────▶│   PostgreSQL    │
│   (TypeScript)  │     │    (Python)     │     │    Database     │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                            Docker Compose
```

## Frontend Architecture

### Technology Stack

- **React 19.1.0** - UI framework
- **TypeScript** - Type safety
- **React Router** - Client-side routing
- **Redux Toolkit** (planned) - State management
- **Material-UI** (planned) - Component library

### Component Structure

```
frontend/src/
├── components/          # UI components
│   ├── common/         # Shared components
│   ├── character/      # Character builder
│   ├── powers/         # Power selection
│   └── enhancements/   # Enhancement UI
├── services/           # API integration
├── store/             # Redux store
├── types/             # TypeScript types
└── utils/             # Helper functions
```

### Design Patterns

- **Container/Presentational** - Smart vs dumb components
- **Custom Hooks** - Reusable logic
- **Context API** - Cross-cutting concerns
- **Error Boundaries** - Graceful error handling

## Backend Architecture

### Technology Stack

- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **asyncpg** - Async PostgreSQL driver

### Application Structure

```
backend/app/
├── routers/        # API endpoints
├── models.py       # Database models
├── schemas.py      # Pydantic models
├── crud.py         # Database operations
├── database.py     # DB configuration
├── auth.py         # Authentication
└── calculations/   # Game mechanics
```

### API Design Principles

- **RESTful** - Standard HTTP methods
- **Versioned** - `/api/v1/` prefix
- **Consistent** - Predictable patterns
- **Documented** - OpenAPI/Swagger

## Database Architecture

### Schema Design

```sql
-- Core entities
archetypes
├── id, name, description
└── primary_group, secondary_group

powersets
├── id, name, archetype_id
└── powerset_type (primary/secondary/pool/epic)

powers
├── id, name, powerset_id
├── level_available, prerequisites
└── base_stats (damage, recharge, etc.)

enhancements
├── id, name, enhancement_type
└── bonuses (accuracy, damage, etc.)

set_bonuses
├── id, set_id
├── pieces_required
└── bonus_effects
```

### Relationships

- **Archetype** → has many → **Powersets**
- **Powerset** → has many → **Powers**
- **Power** → can slot → **Enhancements**
- **Enhancement Set** → provides → **Set Bonuses**

### Performance Considerations

- Indexed foreign keys
- Composite indexes for common queries
- Materialized views for calculations
- Connection pooling with asyncpg

## Data Flow

### Character Build Creation

```
1. User selects archetype
   └─> GET /api/v1/archetypes/{id}

2. User picks powersets
   └─> GET /api/v1/powersets?archetype_id={id}

3. User selects powers
   └─> GET /api/v1/powers?powerset_id={id}

4. User slots enhancements
   └─> GET /api/v1/enhancements?power_id={id}

5. Calculate build stats
   └─> POST /api/v1/builds/calculate
```

### State Management

```
Frontend State Tree:
{
  character: {
    archetype: {...},
    powersets: {...},
    powers: [...],
    enhancements: {...}
  },
  ui: {
    loading: false,
    errors: [],
    activeTab: 'powers'
  },
  gameData: {
    archetypes: [...],
    powersets: [...],
    powers: [...],
    enhancements: [...]
  }
}
```

## Security Architecture

### Authentication & Authorization

- JWT tokens for API access
- Role-based permissions (future)
- Secure password hashing with bcrypt
- CORS configuration for frontend

### Data Validation

- Pydantic schemas for input validation
- SQL injection prevention via ORM
- XSS protection in React
- CSRF tokens for state-changing operations

## Deployment Architecture

### Container Strategy

```yaml
services:
  frontend:
    - Multi-stage build
    - Nginx for serving
    - Optimized bundle size

  backend:
    - Python 3.11 slim
    - Uvicorn with workers
    - Health checks

  database:
    - PostgreSQL 15
    - Persistent volumes
    - Automated backups
```

### Scaling Considerations

- Horizontal scaling for backend
- CDN for static assets
- Database read replicas
- Redis for caching (configured)

## Integration Points

### External Systems

1. **Game Data Sources**

   - Homecoming update server
   - Manual .mhd file imports
   - Community data contributions

2. **Future Integrations**
   - OAuth providers (Google, Discord)
   - Game server APIs
   - Community build databases

### Internal APIs

- RESTful HTTP for frontend-backend
- WebSocket for real-time updates (planned)
- PostgreSQL for data persistence
- Redis for caching and sessions

## Performance Architecture

### Optimization Strategies

1. **Frontend**

   - Code splitting
   - Lazy loading
   - Memoization
   - Virtual scrolling

2. **Backend**

   - Async operations
   - Connection pooling
   - Query optimization
   - Response caching

3. **Database**
   - Proper indexing
   - Query analysis
   - Batch operations
   - Materialized views

### Monitoring

- Application metrics (Prometheus format)
- Error tracking (Sentry planned)
- Performance monitoring
- User analytics (privacy-respecting)
