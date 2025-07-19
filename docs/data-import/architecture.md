# Data Import Architecture

This document provides a comprehensive overview of the Mids Hero Web data import system architecture, including component relationships, data flow, and technical specifications.

## Table of Contents
- [System Architecture](#system-architecture)
- [Component Overview](#component-overview)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Scalability Design](#scalability-design)
- [Security Considerations](#security-considerations)
- [Future Architecture](#future-architecture)

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "External Systems"
        MR[MidsReborn<br/>Application]
        HC[Homecoming<br/>Servers]
    end
    
    subgraph "Data Layer"
        MHD[(MHD Files<br/>Binary Format)]
        JSON[(JSON Files<br/>Structured Data)]
    end
    
    subgraph "Processing Layer"
        DE[DataExporter<br/>.NET/C#]
        IP[Import Pipeline<br/>Python/FastAPI]
        Cache[(Redis Cache)]
        Queue[Task Queue<br/>Celery]
    end
    
    subgraph "Storage Layer"
        PG[(PostgreSQL<br/>Primary DB)]
        S3[(S3/Storage<br/>Backups)]
    end
    
    subgraph "Application Layer"
        API[FastAPI<br/>Backend]
        React[React<br/>Frontend]
    end
    
    MR --> MHD
    HC -.->|Future| API
    MHD --> DE
    DE --> JSON
    JSON --> IP
    IP --> Cache
    IP --> Queue
    IP --> PG
    PG --> S3
    Cache --> API
    PG --> API
    API --> React
    
    classDef external fill:#e1f5fe
    classDef data fill:#f3e5f5
    classDef processing fill:#fff3e0
    classDef storage fill:#e8f5e9
    classDef app fill:#fce4ec
    
    class MR,HC external
    class MHD,JSON data
    class DE,IP,Cache,Queue processing
    class PG,S3 storage
    class API,React app
```

### Detailed Component Architecture

```mermaid
graph LR
    subgraph "Import Pipeline Components"
        CLI[CLI Interface<br/>import_cli.py]
        Manager[Import Manager<br/>import_manager.py]
        
        subgraph "Importers"
            Base[BaseImporter<br/>Abstract]
            Arch[ArchetypeImporter]
            Power[PowerImporter]
            I12[I12StreamingParser]
            Enh[EnhancementImporter]
        end
        
        subgraph "Services"
            Valid[Validation Service]
            Trans[Transform Service]
            Cache[Cache Service]
            Monitor[Monitor Service]
        end
        
        CLI --> Manager
        Manager --> Base
        Base --> Arch
        Base --> Power
        Base --> I12
        Base --> Enh
        
        Arch --> Valid
        Power --> Valid
        I12 --> Valid
        Enh --> Valid
        
        Valid --> Trans
        Trans --> Cache
        Manager --> Monitor
    end
    
    style CLI fill:#4caf50
    style Manager fill:#2196f3
    style Base fill:#ff9800
    style Monitor fill:#9c27b0
```

## Component Overview

### DataExporter (.NET/C#)

```mermaid
classDiagram
    class Program {
        +Main(args)
        -ParseArguments()
        -ExecuteExport()
    }
    
    class MidsRebornExporter {
        -inputPath: string
        -outputPath: string
        +Export()
        -InitializeConfiguration()
        -LoadAllData()
        -ExportToJson()
    }
    
    class DirectDataLoader {
        +LoadDirectly()
        -LoadArchetypes()
        -LoadPowers()
        -LoadEnhancements()
    }
    
    class JsonArchiveExtractor {
        +ExtractArchive()
        -ProcessZipFile()
        -ExtractJsonFiles()
    }
    
    class TextToJsonParser {
        +ParseTextData()
        -ParseI12Format()
        -ConvertToJson()
    }
    
    Program --> MidsRebornExporter
    Program --> DirectDataLoader
    MidsRebornExporter --> JsonArchiveExtractor
    Program --> TextToJsonParser
```

### Import Pipeline (Python)

```mermaid
classDiagram
    class ImportManager {
        -importers: Dict
        -db_session: Session
        +import_all()
        +import_type()
        -get_importer()
    }
    
    class BaseImporter {
        <<abstract>>
        #db: Session
        #batch_size: int
        #errors: List
        +run()
        +validate_data()*
        +transform_data()*
        #import_batch()
    }
    
    class PowerImporter {
        -archetype_cache: Dict
        -powerset_cache: Dict
        +validate_data()
        +transform_data()
        -resolve_prerequisites()
    }
    
    class I12StreamingParser {
        -chunk_size: int
        -memory_limit: float
        -progress_tracker: Progress
        +stream_process()
        -parse_chunk()
        -process_power_entry()
    }
    
    class CacheService {
        -redis_client: Redis
        -local_cache: LRU
        +get()
        +set()
        +invalidate()
    }
    
    ImportManager --> BaseImporter
    BaseImporter <|-- PowerImporter
    BaseImporter <|-- I12StreamingParser
    PowerImporter --> CacheService
    I12StreamingParser --> CacheService
```

## Data Flow

### Import Process Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant ImportManager
    participant Importer
    participant Validator
    participant Database
    participant Cache
    
    User->>CLI: just import-all data/
    CLI->>ImportManager: execute_import(path)
    
    loop For each data type
        ImportManager->>Importer: run(file_path)
        Importer->>Importer: read_json_file()
        
        loop For each record
            Importer->>Validator: validate_data(record)
            alt Valid data
                Validator-->>Importer: True
                Importer->>Importer: transform_data(record)
                Importer->>Cache: cache_lookup(refs)
                Cache-->>Importer: cached_ids
            else Invalid data
                Validator-->>Importer: False, errors
                Importer->>Importer: log_error()
            end
        end
        
        Importer->>Database: bulk_insert(batch)
        Database-->>Importer: success/failure
        Importer->>Cache: update_cache()
        Importer-->>ImportManager: import_stats
    end
    
    ImportManager-->>CLI: complete_stats
    CLI-->>User: Import complete
```

### I12 Streaming Process

```mermaid
graph TD
    subgraph "I12 Streaming Import"
        Start[Start Import]
        Open[Open File<br/>Stream]
        Read[Read Chunk<br/>8MB]
        Parse[Parse JSON<br/>Objects]
        Validate[Validate<br/>Power Data]
        Transform[Transform to<br/>DB Format]
        Cache[Update<br/>Cache]
        Batch[Add to<br/>Batch]
        Full{Batch<br/>Full?}
        Insert[Bulk Insert<br/>to DB]
        More{More<br/>Data?}
        End[End Import]
        
        Start --> Open
        Open --> Read
        Read --> Parse
        Parse --> Validate
        Validate --> Transform
        Transform --> Cache
        Cache --> Batch
        Batch --> Full
        Full -->|Yes| Insert
        Full -->|No| More
        Insert --> More
        More -->|Yes| Read
        More -->|No| End
    end
    
    style Start fill:#4caf50
    style End fill:#4caf50
    style Insert fill:#2196f3
    style Validate fill:#ff9800
```

## Technology Stack

### Core Technologies

```mermaid
graph TD
    subgraph "Languages & Frameworks"
        Python[Python 3.11+<br/>Core Language]
        NET[.NET 8<br/>DataExporter]
        TS[TypeScript<br/>Frontend]
        SQL[SQL<br/>Database]
    end
    
    subgraph "Frameworks"
        FastAPI[FastAPI<br/>REST API]
        React[React 19<br/>UI Framework]
        SQLAlchemy[SQLAlchemy<br/>ORM]
        Pydantic[Pydantic<br/>Validation]
    end
    
    subgraph "Infrastructure"
        PG[PostgreSQL 14+<br/>Database]
        Redis[Redis<br/>Cache]
        Docker[Docker<br/>Containers]
        Nginx[Nginx<br/>Reverse Proxy]
    end
    
    subgraph "Tools"
        Git[Git<br/>Version Control]
        GH[GitHub<br/>Repository]
        Just[Just<br/>Task Runner]
        UV[UV<br/>Package Manager]
    end
    
    style Python fill:#4caf50
    style FastAPI fill:#2196f3
    style PG fill:#ff9800
    style Docker fill:#9c27b0
```

### Database Schema

```mermaid
erDiagram
    archetype ||--o{ powerset : has
    powerset ||--o{ power : contains
    power ||--o{ power_prerequisite : requires
    power ||--o{ power_allowed_enhancement : allows
    enhancement }o--|| enhancement_set : belongs_to
    enhancement_set ||--o{ enhancement_set_bonus : provides
    recipe ||--o{ recipe_salvage : requires
    recipe }o--|| enhancement : creates
    salvage ||--o{ recipe_salvage : used_in
    
    archetype {
        int id PK
        string name UK
        string display_name
        float hit_points_base
        json modifiers
        timestamp created_at
        timestamp updated_at
    }
    
    power {
        int id PK
        int powerset_id FK
        string name
        int level_available
        json effects
        json allowed_enhancements
        timestamp created_at
    }
    
    import_log {
        int id PK
        string import_type
        string file_name
        int records_processed
        int records_imported
        json errors
        timestamp started_at
        timestamp completed_at
    }
```

## Scalability Design

### Horizontal Scaling Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/HAProxy]
    end
    
    subgraph "Application Servers"
        API1[API Server 1]
        API2[API Server 2]
        API3[API Server 3]
    end
    
    subgraph "Import Workers"
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]
        W4[Worker 4]
    end
    
    subgraph "Data Layer"
        subgraph "Cache Cluster"
            R1[Redis Primary]
            R2[Redis Replica]
        end
        
        subgraph "Database Cluster"
            PG1[PostgreSQL Primary]
            PG2[PostgreSQL Replica]
            PG3[PostgreSQL Replica]
        end
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> R1
    API2 --> R1
    API3 --> R1
    R1 --> R2
    
    W1 --> PG1
    W2 --> PG1
    W3 --> PG1
    W4 --> PG1
    
    PG1 --> PG2
    PG1 --> PG3
    
    style LB fill:#4caf50
    style PG1 fill:#2196f3
    style R1 fill:#ff9800
```

### Performance Optimization Points

```mermaid
graph LR
    subgraph "Optimization Strategies"
        Batch[Batch Processing<br/>Reduce DB Calls]
        Index[Database Indexes<br/>Speed Queries]
        Cache[Multi-tier Cache<br/>Redis + LRU]
        Stream[Streaming Parser<br/>Memory Efficient]
        Async[Async Processing<br/>Parallel Tasks]
        Pool[Connection Pool<br/>Reuse Connections]
    end
    
    Batch --> Performance[Improved<br/>Performance]
    Index --> Performance
    Cache --> Performance
    Stream --> Performance
    Async --> Performance
    Pool --> Performance
    
    style Performance fill:#4caf50
```

## Security Considerations

### Security Architecture

```mermaid
graph TD
    subgraph "Security Layers"
        WAF[Web Application<br/>Firewall]
        SSL[SSL/TLS<br/>Encryption]
        Auth[Authentication<br/>JWT/OAuth2]
        RBAC[Role-Based<br/>Access Control]
        Valid[Input<br/>Validation]
        Audit[Audit<br/>Logging]
    end
    
    subgraph "Threats Mitigated"
        SQLi[SQL Injection]
        XSS[Cross-Site<br/>Scripting]
        CSRF[CSRF Attacks]
        DoS[Denial of<br/>Service]
        Unauth[Unauthorized<br/>Access]
    end
    
    WAF --> DoS
    SSL --> MITM[Man in Middle]
    Auth --> Unauth
    Valid --> SQLi
    Valid --> XSS
    RBAC --> Unauth
    Audit --> Forensics[Security<br/>Forensics]
    
    style WAF fill:#f44336
    style Auth fill:#4caf50
    style Valid fill:#ff9800
```

### Data Security Flow

```mermaid
sequenceDiagram
    participant Client
    participant WAF
    participant API
    participant Auth
    participant Validator
    participant Database
    
    Client->>WAF: HTTPS Request
    WAF->>WAF: Check Rules
    alt Threat Detected
        WAF-->>Client: 403 Forbidden
    else Clean Request
        WAF->>API: Forward Request
        API->>Auth: Verify Token
        
        alt Invalid Token
            Auth-->>Client: 401 Unauthorized
        else Valid Token
            Auth->>API: User Context
            API->>Validator: Validate Input
            
            alt Invalid Input
                Validator-->>Client: 400 Bad Request
            else Valid Input
                API->>Database: Parameterized Query
                Database-->>API: Results
                API-->>Client: 200 OK + Data
            end
        end
    end
```

## Future Architecture

### Planned Enhancements

```mermaid
graph TB
    subgraph "Current State"
        Current[Manual Export<br/>→ Import]
    end
    
    subgraph "Phase 1: Automation"
        Auto[Automated<br/>Import Pipeline]
        Schedule[Scheduled<br/>Updates]
        Notify[Update<br/>Notifications]
    end
    
    subgraph "Phase 2: Real-time"
        Stream[Streaming<br/>Updates]
        Event[Event-Driven<br/>Architecture]
        Sync[Live Server<br/>Sync]
    end
    
    subgraph "Phase 3: Analytics"
        ML[Machine Learning<br/>Build Optimization]
        Analytics[Usage<br/>Analytics]
        Recommend[Build<br/>Recommendations]
    end
    
    Current --> Auto
    Auto --> Schedule
    Auto --> Notify
    Schedule --> Stream
    Notify --> Event
    Stream --> Sync
    Event --> ML
    Sync --> Analytics
    ML --> Recommend
    
    style Current fill:#ff9800
    style Auto fill:#4caf50
    style Stream fill:#2196f3
    style ML fill:#9c27b0
```

### Microservices Architecture (Future)

```mermaid
graph TB
    subgraph "API Gateway"
        GW[Kong/Traefik]
    end
    
    subgraph "Core Services"
        Auth[Auth Service]
        User[User Service]
        Build[Build Service]
        Import[Import Service]
    end
    
    subgraph "Data Services"
        Power[Power Service]
        Enhance[Enhancement Service]
        Recipe[Recipe Service]
    end
    
    subgraph "Support Services"
        Search[Search Service]
        Export[Export Service]
        Notify[Notification Service]
    end
    
    subgraph "Infrastructure"
        MQ[Message Queue<br/>RabbitMQ]
        ES[Elasticsearch]
        Cache[(Redis)]
        DB[(PostgreSQL)]
    end
    
    GW --> Auth
    GW --> User
    GW --> Build
    GW --> Import
    
    Build --> Power
    Build --> Enhance
    Build --> Recipe
    
    Power --> Cache
    Enhance --> Cache
    Recipe --> Cache
    
    Build --> Search
    Build --> Export
    Import --> Notify
    
    Search --> ES
    All --> MQ
    All --> DB
    
    style GW fill:#4caf50
    style Build fill:#2196f3
    style MQ fill:#ff9800
```

## Architecture Decision Records (ADRs)

### ADR-001: Use DataExporter with MidsReborn API

**Status**: Accepted  
**Context**: Need to parse MHD binary files  
**Decision**: Use MidsReborn's official API via DataExporter  
**Consequences**: 
- ✅ Accurate parsing
- ✅ Maintained by community
- ❌ Dependency on external project
- ❌ Windows/Mono requirement

### ADR-002: Streaming Parser for I12 Data

**Status**: Accepted  
**Context**: I12 file contains 360K+ records  
**Decision**: Implement streaming JSON parser  
**Consequences**:
- ✅ Memory efficient
- ✅ Handles large files
- ✅ Progress tracking
- ❌ More complex implementation

### ADR-003: PostgreSQL as Primary Database

**Status**: Accepted  
**Context**: Need reliable, scalable database  
**Decision**: Use PostgreSQL 14+  
**Consequences**:
- ✅ JSONB support
- ✅ Strong consistency
- ✅ Advanced indexing
- ❌ Requires administration

## Monitoring and Observability

```mermaid
graph TD
    subgraph "Metrics Collection"
        App[Application<br/>Metrics]
        DB[Database<br/>Metrics]
        Sys[System<br/>Metrics]
    end
    
    subgraph "Processing"
        Prom[Prometheus]
        Loki[Loki<br/>Log Aggregation]
        Trace[Jaeger<br/>Tracing]
    end
    
    subgraph "Visualization"
        Graf[Grafana<br/>Dashboards]
        Alert[Alert Manager]
    end
    
    App --> Prom
    DB --> Prom
    Sys --> Prom
    
    App --> Loki
    App --> Trace
    
    Prom --> Graf
    Loki --> Graf
    Trace --> Graf
    
    Prom --> Alert
    
    style Prom fill:#ff9800
    style Graf fill:#4caf50
    style Alert fill:#f44336
```

This architecture provides a solid foundation for the Mids Hero Web import system while allowing for future growth and enhancement.