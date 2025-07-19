# Data Flow Documentation

This document visualizes how data flows through the Mids Hero Web system, from import to user interaction.

## Complete Data Flow Overview

```mermaid
graph TB
    subgraph "Data Sources"
        MidsReborn[MidsReborn<br/>Application]
        Homecoming[Homecoming<br/>Servers]
        UserInput[User<br/>Input]
    end
    
    subgraph "Data Pipeline"
        Export[DataExporter<br/>.NET]
        JSON[JSON Files]
        Import[Import Scripts<br/>Python]
        Validate[Validation<br/>Layer]
    end
    
    subgraph "Storage"
        DB[(PostgreSQL<br/>Database)]
        Cache[(Redis<br/>Cache)]
        S3[(S3<br/>Storage)]
    end
    
    subgraph "Application"
        API[FastAPI<br/>Backend]
        BuildEngine[Build<br/>Calculator]
        ExportEngine[Export<br/>Service]
    end
    
    subgraph "Frontend"
        React[React<br/>UI]
        State[Redux<br/>State]
        LocalStorage[Local<br/>Storage]
    end
    
    MidsReborn --> Export
    Export --> JSON
    JSON --> Import
    Import --> Validate
    Validate --> DB
    
    UserInput --> React
    React --> State
    State --> API
    
    API --> Cache
    Cache --> DB
    API --> BuildEngine
    BuildEngine --> DB
    
    API --> ExportEngine
    ExportEngine --> S3
    
    React --> LocalStorage
    
    Homecoming -.->|Future| API
    
    classDef source fill:#e3f2fd
    classDef pipeline fill:#fff3e0
    classDef storage fill:#e8f5e9
    classDef app fill:#f3e5f5
    classDef frontend fill:#fce4ec
    
    class MidsReborn,Homecoming,UserInput source
    class Export,JSON,Import,Validate pipeline
    class DB,Cache,S3 storage
    class API,BuildEngine,ExportEngine app
    class React,State,LocalStorage frontend
```

## Import Data Flow

```mermaid
flowchart TD
    Start[MHD Files]
    
    subgraph "DataExporter Process"
        Init[Initialize<br/>MidsReborn API]
        Load[Load MHD<br/>Files]
        Parse[Parse Binary<br/>Data]
        Convert[Convert to<br/>JSON]
        Write[Write JSON<br/>Files]
    end
    
    subgraph "Import Process"
        Read[Read JSON<br/>Files]
        Val1[Schema<br/>Validation]
        Val2[Reference<br/>Validation]
        Val3[Game Rule<br/>Validation]
        Transform[Transform<br/>Data]
        Batch[Batch<br/>Operations]
        Insert[Database<br/>Insert]
    end
    
    subgraph "Post-Processing"
        Index[Update<br/>Indexes]
        Cache[Warm<br/>Cache]
        Stats[Update<br/>Statistics]
    end
    
    Start --> Init
    Init --> Load
    Load --> Parse
    Parse --> Convert
    Convert --> Write
    
    Write --> Read
    Read --> Val1
    Val1 --> Val2
    Val2 --> Val3
    Val3 --> Transform
    Transform --> Batch
    Batch --> Insert
    
    Insert --> Index
    Index --> Cache
    Cache --> Stats
    
    style Start fill:#4caf50
    style Write fill:#ff9800
    style Insert fill:#2196f3
    style Stats fill:#9c27b0
```

## User Interaction Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant React
    participant Redux
    participant API
    participant Cache
    participant DB
    
    User->>Browser: Select Archetype
    Browser->>React: onChange Event
    React->>Redux: Dispatch Action
    Redux->>Redux: Update State
    Redux->>React: State Changed
    React->>Browser: Re-render UI
    
    React->>API: GET /powersets?archetype=1
    API->>Cache: Check Cache
    
    alt Cache Hit
        Cache-->>API: Cached Data
    else Cache Miss
        API->>DB: Query Powersets
        DB-->>API: Powerset Data
        API->>Cache: Store in Cache
    end
    
    API-->>React: Powerset List
    React->>Redux: Update Powersets
    Redux->>React: State Changed
    React->>Browser: Show Powersets
    Browser-->>User: Display Options
```

## Build Calculation Data Flow

```mermaid
graph TB
    subgraph "Input Data"
        Build[Build<br/>Configuration]
        Powers[Selected<br/>Powers]
        Slots[Enhancement<br/>Slots]
    end
    
    subgraph "Calculation Pipeline"
        Base[Calculate<br/>Base Stats]
        Enhance[Apply<br/>Enhancements]
        ED[Enhancement<br/>Diversification]
        Sets[Set Bonus<br/>Calculation]
        Stack[Apply<br/>Stacking Rules]
        Cap[Apply<br/>Stat Caps]
    end
    
    subgraph "Output"
        Stats[Final<br/>Statistics]
        Valid[Validation<br/>Results]
        Warnings[Build<br/>Warnings]
    end
    
    Build --> Base
    Powers --> Base
    
    Base --> Enhance
    Slots --> Enhance
    
    Enhance --> ED
    ED --> Sets
    Sets --> Stack
    Stack --> Cap
    
    Cap --> Stats
    Cap --> Valid
    Cap --> Warnings
    
    style Build fill:#4caf50
    style Stats fill:#2196f3
```

## Real-time Update Flow

```mermaid
sequenceDiagram
    participant User1
    participant User2
    participant API
    participant WebSocket
    participant Redis
    participant DB
    
    Note over User1,User2: Both editing same build
    
    User1->>API: PUT /builds/123
    API->>DB: Update Build
    DB-->>API: Success
    API->>Redis: Publish Update
    API-->>User1: 200 OK
    
    Redis->>WebSocket: Build Update Event
    
    WebSocket->>User2: Build Changed
    User2->>User2: Show Notification
    User2->>API: GET /builds/123
    API->>DB: Get Latest
    DB-->>API: Updated Build
    API-->>User2: Latest Data
    User2->>User2: Update UI
```

## Cache Strategy Flow

```mermaid
graph TD
    Request[API Request]
    
    subgraph "Cache Layers"
        L1[L1: Local<br/>Memory Cache]
        L2[L2: Redis<br/>Cache]
        L3[L3: Database]
    end
    
    subgraph "Cache Logic"
        Check1{In L1?}
        Check2{In L2?}
        GetDB[Get from DB]
        StoreL2[Store in L2]
        StoreL1[Store in L1]
    end
    
    Response[API Response]
    
    Request --> Check1
    Check1 -->|Hit| Response
    Check1 -->|Miss| Check2
    Check2 -->|Hit| StoreL1
    Check2 -->|Miss| GetDB
    GetDB --> StoreL2
    StoreL2 --> StoreL1
    StoreL1 --> Response
    
    style L1 fill:#4caf50
    style L2 fill:#ff9800
    style L3 fill:#2196f3
```

## Export Data Flow

```mermaid
graph LR
    subgraph "Export Request"
        User[User]
        Format[Select Format<br/>MHD/JSON/URL]
    end
    
    subgraph "Processing"
        Load[Load Build<br/>Data]
        Enrich[Enrich with<br/>Game Data]
        Convert[Convert to<br/>Format]
        Compress[Compress<br/>Optional]
    end
    
    subgraph "Delivery"
        Direct[Direct<br/>Download]
        S3[Upload to<br/>S3]
        Share[Generate<br/>Share URL]
    end
    
    User --> Format
    Format --> Load
    Load --> Enrich
    Enrich --> Convert
    Convert --> Compress
    
    Compress --> Direct
    Compress --> S3
    S3 --> Share
    
    style User fill:#4caf50
    style Convert fill:#ff9800
    style Share fill:#2196f3
```

## Error Handling Flow

```mermaid
flowchart TD
    Operation[Any Operation]
    
    subgraph "Error Detection"
        Try[Try Operation]
        Catch{Error<br/>Occurred?}
    end
    
    subgraph "Error Classification"
        Validation[Validation<br/>Error]
        Business[Business<br/>Logic Error]
        System[System<br/>Error]
        External[External<br/>Service Error]
    end
    
    subgraph "Error Handling"
        Log[Log Error]
        Transform[Transform to<br/>User Error]
        Retry{Retryable?}
        Alert{Critical?}
    end
    
    subgraph "Response"
        UserMsg[User-Friendly<br/>Message]
        DevMsg[Developer<br/>Details]
        Support[Support<br/>Ticket]
    end
    
    Operation --> Try
    Try --> Catch
    
    Catch -->|No| Success[Success Response]
    Catch -->|Yes| Validation
    Catch -->|Yes| Business
    Catch -->|Yes| System
    Catch -->|Yes| External
    
    Validation --> Log
    Business --> Log
    System --> Log
    External --> Log
    
    Log --> Transform
    Transform --> UserMsg
    Transform --> DevMsg
    
    System --> Retry
    External --> Retry
    
    Retry -->|Yes| Try
    Retry -->|No| Alert
    
    Alert -->|Yes| Support
    
    style Success fill:#4caf50
    style Support fill:#f44336
```

## Performance Optimization Flow

```mermaid
graph TB
    subgraph "Request Analysis"
        Incoming[Incoming<br/>Request]
        Analyze[Analyze<br/>Pattern]
        Frequent{Frequent<br/>Request?}
    end
    
    subgraph "Optimization Strategies"
        Cache[Cache<br/>Response]
        Batch[Batch<br/>Similar]
        Async[Process<br/>Async]
        Preload[Preload<br/>Next]
    end
    
    subgraph "Execution"
        Fast[Fast Path<br/>< 50ms]
        Normal[Normal Path<br/>< 200ms]
        Slow[Slow Path<br/>> 200ms]
    end
    
    subgraph "Monitoring"
        Metrics[Collect<br/>Metrics]
        Analyze2[Analyze<br/>Performance]
        Optimize[Optimize<br/>Further]
    end
    
    Incoming --> Analyze
    Analyze --> Frequent
    
    Frequent -->|Yes| Cache
    Frequent -->|No| Normal
    
    Cache --> Fast
    Batch --> Fast
    Async --> Normal
    Preload --> Fast
    
    Normal --> Slow
    
    Fast --> Metrics
    Normal --> Metrics
    Slow --> Metrics
    
    Metrics --> Analyze2
    Analyze2 --> Optimize
    
    style Fast fill:#4caf50
    style Normal fill:#ff9800
    style Slow fill:#f44336
```

## Data Validation Flow

```mermaid
graph TD
    Input[Input Data]
    
    subgraph "Validation Layers"
        Schema[Schema<br/>Validation]
        Type[Type<br/>Validation]
        Range[Range<br/>Validation]
        Reference[Reference<br/>Validation]
        Business[Business<br/>Rule Validation]
    end
    
    subgraph "Validation Results"
        Valid[Valid Data]
        Invalid[Invalid Data]
        Warnings[Warnings]
    end
    
    subgraph "Error Details"
        Field[Field-Level<br/>Errors]
        Global[Global<br/>Errors]
        Suggest[Suggestions]
    end
    
    Input --> Schema
    Schema -->|Pass| Type
    Schema -->|Fail| Invalid
    
    Type -->|Pass| Range
    Type -->|Fail| Invalid
    
    Range -->|Pass| Reference
    Range -->|Fail| Invalid
    
    Reference -->|Pass| Business
    Reference -->|Fail| Invalid
    
    Business -->|Pass| Valid
    Business -->|Fail| Invalid
    Business -.->|Issues| Warnings
    
    Invalid --> Field
    Invalid --> Global
    Invalid --> Suggest
    
    style Valid fill:#4caf50
    style Invalid fill:#f44336
    style Warnings fill:#ff9800
```

## Session Management Flow

```mermaid
stateDiagram-v2
    [*] --> Anonymous
    
    Anonymous --> Authenticating: Login/Register
    Authenticating --> Authenticated: Success
    Authenticating --> Anonymous: Failure
    
    Authenticated --> Active: User Activity
    Active --> Active: Activity
    Active --> Idle: No Activity
    Idle --> Active: Resume Activity
    Idle --> Expired: Timeout
    
    Authenticated --> RefreshingToken: Token Expiry
    RefreshingToken --> Authenticated: New Token
    RefreshingToken --> Anonymous: Refresh Failed
    
    Expired --> Anonymous: Session End
    Authenticated --> Anonymous: Logout
    
    Active --> [*]: Close App
    Authenticated --> [*]: Close App
```

This data flow documentation provides a comprehensive view of how data moves through the system, from import to user interaction, including error handling and optimization strategies.