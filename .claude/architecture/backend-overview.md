# Backend Architecture Overview

This document provides visual diagrams and explanations of the Mids Hero Web backend architecture.

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Browser<br/>React 19]
        Mobile[Mobile App<br/>Future]
    end
    
    subgraph "API Gateway"
        Nginx[Nginx<br/>Reverse Proxy]
        RateLimit[Rate Limiting]
        SSL[SSL Termination]
    end
    
    subgraph "Application Layer"
        FastAPI[FastAPI<br/>REST API]
        WebSocket[WebSocket<br/>Real-time]
        GraphQL[GraphQL<br/>Future]
    end
    
    subgraph "Business Logic"
        Auth[Auth Service]
        Build[Build Service]
        Import[Import Service]
        Export[Export Service]
        Calc[Calculation Engine]
    end
    
    subgraph "Data Layer"
        Cache[(Redis Cache)]
        Primary[(PostgreSQL<br/>Primary)]
        Replica[(PostgreSQL<br/>Read Replica)]
        S3[(S3 Storage)]
    end
    
    Web --> Nginx
    Mobile --> Nginx
    Nginx --> RateLimit
    RateLimit --> SSL
    SSL --> FastAPI
    SSL --> WebSocket
    
    FastAPI --> Auth
    FastAPI --> Build
    FastAPI --> Import
    FastAPI --> Export
    FastAPI --> Calc
    
    Auth --> Cache
    Build --> Cache
    Import --> Primary
    Export --> Cache
    Calc --> Cache
    
    Cache --> Primary
    Primary --> Replica
    Build --> S3
    
    classDef client fill:#e3f2fd
    classDef gateway fill:#f3e5f5
    classDef app fill:#fff3e0
    classDef logic fill:#e8f5e9
    classDef data fill:#fce4ec
    
    class Web,Mobile client
    class Nginx,RateLimit,SSL gateway
    class FastAPI,WebSocket,GraphQL app
    class Auth,Build,Import,Export,Calc logic
    class Cache,Primary,Replica,S3 data
```

## API Architecture

```mermaid
graph LR
    subgraph "FastAPI Application"
        Main[main.py<br/>Application Entry]
        
        subgraph "Routers"
            AuthRouter[auth.py]
            BuildRouter[builds.py]
            PowerRouter[powers.py]
            ImportRouter[import.py]
        end
        
        subgraph "Services"
            AuthService[Authentication]
            BuildService[Build Logic]
            CalcService[Calculations]
            CacheService[Caching]
        end
        
        subgraph "Models"
            SQLModels[SQLAlchemy Models]
            Pydantic[Pydantic Schemas]
        end
        
        subgraph "Database"
            DBSession[Database Sessions]
            Migrations[Alembic Migrations]
        end
    end
    
    Main --> AuthRouter
    Main --> BuildRouter
    Main --> PowerRouter
    Main --> ImportRouter
    
    AuthRouter --> AuthService
    BuildRouter --> BuildService
    BuildRouter --> CalcService
    PowerRouter --> CacheService
    
    AuthService --> SQLModels
    BuildService --> SQLModels
    CalcService --> Pydantic
    
    SQLModels --> DBSession
    DBSession --> Migrations
```

## Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Nginx
    participant FastAPI
    participant Middleware
    participant Router
    participant Service
    participant Database
    participant Cache
    
    Client->>Nginx: HTTPS Request
    Nginx->>Nginx: SSL Termination
    Nginx->>FastAPI: HTTP Request
    
    FastAPI->>Middleware: Process Request
    Note over Middleware: CORS, Auth, Logging
    
    Middleware->>Router: Route Request
    Router->>Router: Validate Input
    
    Router->>Service: Business Logic
    
    Service->>Cache: Check Cache
    alt Cache Hit
        Cache-->>Service: Cached Data
    else Cache Miss
        Service->>Database: Query Data
        Database-->>Service: Result
        Service->>Cache: Update Cache
    end
    
    Service-->>Router: Response Data
    Router-->>FastAPI: JSON Response
    FastAPI-->>Nginx: HTTP Response
    Nginx-->>Client: HTTPS Response
```

## Database Schema Overview

```mermaid
erDiagram
    USER ||--o{ BUILD : creates
    USER ||--o{ USER_SESSION : has
    BUILD ||--o{ BUILD_POWER : contains
    BUILD_POWER ||--o{ BUILD_SLOT : has
    BUILD_SLOT }o--|| ENHANCEMENT : uses
    
    ARCHETYPE ||--o{ POWERSET : has
    POWERSET ||--o{ POWER : contains
    POWER ||--o{ POWER_EFFECT : has
    POWER ||--o{ POWER_PREREQUISITE : requires
    
    ENHANCEMENT }o--|| ENHANCEMENT_SET : belongs_to
    ENHANCEMENT_SET ||--o{ SET_BONUS : provides
    RECIPE ||--o{ RECIPE_SALVAGE : requires
    RECIPE }o--|| ENHANCEMENT : creates
    
    USER {
        uuid id PK
        string email UK
        string username UK
        string password_hash
        timestamp created_at
    }
    
    BUILD {
        uuid id PK
        uuid user_id FK
        string name
        int archetype_id FK
        json build_data
        timestamp updated_at
    }
    
    POWER {
        int id PK
        int powerset_id FK
        string name
        json effects
        int level_available
    }
```

## Service Layer Architecture

```mermaid
graph TD
    subgraph "Service Layer"
        BaseService[BaseService<br/>Abstract Class]
        
        AuthService[AuthService]
        BuildService[BuildService]
        PowerService[PowerService]
        CalcService[CalculationService]
        ImportService[ImportService]
        ExportService[ExportService]
        
        BaseService --> AuthService
        BaseService --> BuildService
        BaseService --> PowerService
        BaseService --> CalcService
        BaseService --> ImportService
        BaseService --> ExportService
    end
    
    subgraph "Service Dependencies"
        BuildService --> PowerService
        BuildService --> CalcService
        ImportService --> PowerService
        ExportService --> BuildService
    end
    
    subgraph "External Dependencies"
        AuthService --> JWT[JWT Library]
        CalcService --> GameRules[Game Rules Engine]
        ImportService --> Validators[Data Validators]
        ExportService --> Formatters[Format Converters]
    end
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AuthService
    participant Database
    participant JWT
    
    User->>Frontend: Enter Credentials
    Frontend->>API: POST /auth/login
    API->>AuthService: authenticate(email, password)
    
    AuthService->>Database: Get User by Email
    Database-->>AuthService: User Data
    
    AuthService->>AuthService: Verify Password Hash
    
    alt Valid Credentials
        AuthService->>JWT: Generate Tokens
        JWT-->>AuthService: Access + Refresh Tokens
        AuthService-->>API: Auth Success
        API-->>Frontend: 200 OK + Tokens
        Frontend->>Frontend: Store Tokens
    else Invalid Credentials
        AuthService-->>API: Auth Failed
        API-->>Frontend: 401 Unauthorized
    end
    
    Note over Frontend: Subsequent Requests
    
    Frontend->>API: GET /api/resource<br/>Authorization: Bearer token
    API->>JWT: Verify Token
    
    alt Valid Token
        JWT-->>API: Token Claims
        API->>API: Process Request
        API-->>Frontend: 200 OK + Data
    else Invalid/Expired Token
        JWT-->>API: Token Invalid
        API-->>Frontend: 401 Unauthorized
        Frontend->>Frontend: Refresh Token Flow
    end
```

## Import System Architecture

```mermaid
graph TB
    subgraph "Import Pipeline"
        Entry[Import CLI<br/>Entry Point]
        Manager[Import Manager]
        Queue[Task Queue]
        
        subgraph "Workers"
            W1[Worker 1]
            W2[Worker 2]
            W3[Worker 3]
        end
        
        subgraph "Importers"
            Base[BaseImporter]
            Arch[ArchetypeImporter]
            Power[PowerImporter]
            I12[I12StreamingParser]
        end
    end
    
    subgraph "Processing"
        Valid[Validator]
        Trans[Transformer]
        Batch[Batch Processor]
    end
    
    subgraph "Storage"
        Cache[(Redis)]
        DB[(PostgreSQL)]
        Logs[(Import Logs)]
    end
    
    Entry --> Manager
    Manager --> Queue
    Queue --> W1
    Queue --> W2
    Queue --> W3
    
    W1 --> Base
    W2 --> Base
    W3 --> Base
    
    Base --> Arch
    Base --> Power
    Base --> I12
    
    Arch --> Valid
    Power --> Valid
    I12 --> Valid
    
    Valid --> Trans
    Trans --> Batch
    
    Batch --> Cache
    Batch --> DB
    Manager --> Logs
```

## Calculation Engine

```mermaid
graph LR
    subgraph "Calculation Engine"
        Input[Build Data<br/>Input]
        
        subgraph "Calculators"
            Base[Base Stats]
            Enhance[Enhancement<br/>Values]
            ED[ED Calculator]
            SetBonus[Set Bonus<br/>Calculator]
            Total[Total Stats]
        end
        
        subgraph "Rules"
            Caps[Stat Caps]
            Stacking[Stacking Rules]
            Exempt[Exemplar Rules]
        end
        
        Output[Final Stats<br/>Output]
    end
    
    Input --> Base
    Input --> Enhance
    
    Enhance --> ED
    ED --> SetBonus
    
    Base --> Total
    SetBonus --> Total
    
    Total --> Caps
    Caps --> Stacking
    Stacking --> Exempt
    
    Exempt --> Output
    
    style Input fill:#4caf50
    style Output fill:#2196f3
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        LocalDev[Local Docker<br/>Compose]
    end
    
    subgraph "CI/CD"
        GitHub[GitHub]
        Actions[GitHub Actions]
        Tests[Test Suite]
        Build[Build Images]
    end
    
    subgraph "Staging"
        StagingCluster[Kubernetes<br/>Staging]
        StagingDB[(Staging DB)]
    end
    
    subgraph "Production"
        LoadBalancer[Load Balancer]
        
        subgraph "Kubernetes Cluster"
            API1[API Pod 1]
            API2[API Pod 2]
            API3[API Pod 3]
            Worker1[Worker Pod 1]
            Worker2[Worker Pod 2]
        end
        
        subgraph "Managed Services"
            ProdDB[(RDS PostgreSQL)]
            ProdCache[(ElastiCache Redis)]
            ProdS3[(S3 Bucket)]
        end
    end
    
    LocalDev --> GitHub
    GitHub --> Actions
    Actions --> Tests
    Tests --> Build
    
    Build --> StagingCluster
    StagingCluster --> StagingDB
    
    Build --> LoadBalancer
    LoadBalancer --> API1
    LoadBalancer --> API2
    LoadBalancer --> API3
    
    API1 --> ProdDB
    API2 --> ProdCache
    API3 --> ProdS3
    
    Worker1 --> ProdDB
    Worker2 --> ProdDB
```

## Error Handling Flow

```mermaid
graph TD
    Request[Incoming Request]
    
    subgraph "Error Layers"
        Validation[Input Validation]
        Business[Business Logic]
        Database[Database Layer]
        External[External Services]
    end
    
    subgraph "Error Handlers"
        ValError[ValidationError<br/>400 Bad Request]
        AuthError[AuthError<br/>401/403]
        NotFound[NotFoundError<br/>404]
        Conflict[ConflictError<br/>409]
        DBError[DatabaseError<br/>500]
        General[GeneralError<br/>500]
    end
    
    subgraph "Response"
        ErrorResp[Error Response<br/>JSON Format]
        Logging[Error Logging]
        Monitoring[Alert System]
    end
    
    Request --> Validation
    Request --> Business
    Request --> Database
    Request --> External
    
    Validation --> ValError
    Business --> AuthError
    Business --> NotFound
    Business --> Conflict
    Database --> DBError
    External --> General
    
    ValError --> ErrorResp
    AuthError --> ErrorResp
    NotFound --> ErrorResp
    Conflict --> ErrorResp
    DBError --> ErrorResp
    General --> ErrorResp
    
    ErrorResp --> Logging
    ErrorResp --> Monitoring
```

## Performance Optimization Points

```mermaid
graph TD
    subgraph "Optimization Strategies"
        subgraph "Caching"
            Redis[Redis Cache]
            LRU[In-Memory LRU]
            CDN[CDN for Static]
        end
        
        subgraph "Database"
            Indexes[Optimized Indexes]
            Connection[Connection Pooling]
            ReadReplica[Read Replicas]
        end
        
        subgraph "Application"
            Async[Async Operations]
            Batch[Batch Processing]
            LazyLoad[Lazy Loading]
        end
        
        subgraph "Infrastructure"
            AutoScale[Auto Scaling]
            LoadBalance[Load Balancing]
            Monitoring[Performance Monitoring]
        end
    end
    
    style Redis fill:#ff9800
    style Indexes fill:#4caf50
    style Async fill:#2196f3
    style AutoScale fill:#9c27b0
```

This architecture documentation provides a comprehensive visual overview of the backend system, making it easier for developers to understand the system design and data flow.