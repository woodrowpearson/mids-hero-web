# API Specifications

This document provides detailed API specifications with visual diagrams for the Mids Hero Web REST API.

## API Overview

```mermaid
graph TB
    subgraph "API Endpoints"
        subgraph "Authentication"
            POST_Login[POST /auth/login]
            POST_Register[POST /auth/register]
            POST_Refresh[POST /auth/refresh]
            POST_Logout[POST /auth/logout]
        end
        
        subgraph "Character Data"
            GET_Archetypes[GET /archetypes]
            GET_Powersets[GET /powersets]
            GET_Powers[GET /powers]
            GET_Enhancements[GET /enhancements]
        end
        
        subgraph "Builds"
            GET_Builds[GET /builds]
            POST_Build[POST /builds]
            GET_Build["GET /builds/{id}"]
            PUT_Build["PUT /builds/{id}"]
            DELETE_Build["DELETE /builds/{id}"]
        end
        
        subgraph "Import/Export"
            POST_Import[POST /import]
            GET_Export["GET /export/{id}"]
            GET_ImportStatus["GET /import/status/{job_id}"]
        end
    end
    
    style POST_Login fill:#4caf50
    style POST_Register fill:#4caf50
    style GET_Builds fill:#2196f3
    style POST_Import fill:#ff9800
```

## Authentication Endpoints

### POST /auth/login

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Validator
    participant AuthService
    participant Database
    participant Response
    
    Client->>API: POST /auth/login<br/>{email, password}
    API->>Validator: Validate Input
    
    alt Invalid Input
        Validator-->>API: ValidationError
        API-->>Client: 400 Bad Request
    else Valid Input
        Validator->>AuthService: Authenticate
        AuthService->>Database: Find User
        
        alt User Not Found
            Database-->>AuthService: null
            AuthService-->>API: UserNotFound
            API-->>Client: 401 Unauthorized
        else User Found
            Database-->>AuthService: User
            AuthService->>AuthService: Verify Password
            
            alt Invalid Password
                AuthService-->>API: InvalidPassword
                API-->>Client: 401 Unauthorized
            else Valid Password
                AuthService->>AuthService: Generate Tokens
                AuthService-->>API: {access_token, refresh_token}
                API-->>Client: 200 OK<br/>{tokens, user}
            end
        end
    end
```

**Request Schema:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response Schema:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "string",
    "username": "string"
  }
}
```

### POST /auth/register

```mermaid
graph TD
    Start[Client Request]
    Validate[Validate Input]
    CheckEmail{Email Exists?}
    CheckUsername{Username Exists?}
    CreateUser[Create User]
    HashPassword[Hash Password]
    SaveUser[Save to DB]
    GenerateTokens[Generate Tokens]
    Success[Return Success]
    Error400[400 Bad Request]
    Error409[409 Conflict]
    
    Start --> Validate
    Validate -->|Invalid| Error400
    Validate -->|Valid| CheckEmail
    CheckEmail -->|Yes| Error409
    CheckEmail -->|No| CheckUsername
    CheckUsername -->|Yes| Error409
    CheckUsername -->|No| HashPassword
    HashPassword --> CreateUser
    CreateUser --> SaveUser
    SaveUser --> GenerateTokens
    GenerateTokens --> Success
```

## Character Data Endpoints

### GET /archetypes

```mermaid
graph LR
    Request[GET /archetypes]
    Cache{Cached?}
    Database[(Database)]
    Transform[Transform Data]
    Response[JSON Response]
    
    Request --> Cache
    Cache -->|Hit| Response
    Cache -->|Miss| Database
    Database --> Transform
    Transform --> Cache
    Transform --> Response
    
    style Cache fill:#ff9800
    style Database fill:#4caf50
```

**Response Schema:**
```json
{
  "archetypes": [
    {
      "id": 1,
      "name": "Blaster",
      "display_name": "Blaster",
      "description": "Offensive ranged damage dealer",
      "icon": "blaster.png",
      "primary_category": "Ranged",
      "secondary_category": "Support",
      "hit_points_base": 1204.8,
      "hit_points_max": 1606.4,
      "inherent_powers": ["Defiance"]
    }
  ],
  "total": 13
}
```

### GET /powers

```mermaid
graph TD
    Request[GET /powers]
    
    subgraph "Query Parameters"
        Powerset[?powerset_id=1]
        Level[?max_level=20]
        Search[?search=fire]
        Page[?page=1&size=50]
    end
    
    subgraph "Processing"
        BuildQuery[Build Query]
        ApplyFilters[Apply Filters]
        Paginate[Paginate Results]
        EnrichData[Enrich Data]
    end
    
    Response[Paginated Response]
    
    Request --> Powerset
    Request --> Level
    Request --> Search
    Request --> Page
    
    Powerset --> BuildQuery
    Level --> ApplyFilters
    Search --> ApplyFilters
    Page --> Paginate
    
    BuildQuery --> ApplyFilters
    ApplyFilters --> Paginate
    Paginate --> EnrichData
    EnrichData --> Response
```

**Query Parameters:**
- `powerset_id` (optional): Filter by powerset
- `archetype_id` (optional): Filter by archetype
- `max_level` (optional): Maximum level available
- `search` (optional): Search in name/description
- `page` (default: 1): Page number
- `size` (default: 50): Page size

## Build Management Endpoints

### POST /builds

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Validator
    participant BuildService
    participant Database
    
    Client->>API: POST /builds<br/>Authorization: Bearer token
    API->>Auth: Verify Token
    
    alt Unauthorized
        Auth-->>API: Invalid Token
        API-->>Client: 401 Unauthorized
    else Authorized
        Auth-->>API: User Context
        API->>Validator: Validate Build Data
        
        alt Invalid Build
            Validator-->>API: Validation Errors
            API-->>Client: 400 Bad Request
        else Valid Build
            Validator->>BuildService: Create Build
            BuildService->>BuildService: Validate Game Rules
            
            alt Rule Violation
                BuildService-->>API: Rule Errors
                API-->>Client: 422 Unprocessable
            else Rules Pass
                BuildService->>Database: Save Build
                Database-->>BuildService: Build ID
                BuildService->>BuildService: Calculate Stats
                BuildService-->>API: Complete Build
                API-->>Client: 201 Created
            end
        end
    end
```

**Request Schema:**
```json
{
  "name": "Fire/Fire Blaster",
  "archetype_id": 1,
  "primary_powerset_id": 1,
  "secondary_powerset_id": 2,
  "powers": [
    {
      "power_id": 101,
      "level_taken": 1,
      "slots": [
        {
          "level": 1,
          "enhancement_id": 501
        }
      ]
    }
  ]
}
```

### GET /builds/{id}

```mermaid
graph TD
    Request["GET /builds/{id}"]
    Auth{Authorized?}
    CheckOwner{Is Owner?}
    CheckPublic{Is Public?}
    LoadBuild[Load Build]
    EnrichData[Enrich Data]
    CalcStats[Calculate Stats]
    Response[Build Response]
    Error401[401 Unauthorized]
    Error403[403 Forbidden]
    Error404[404 Not Found]
    
    Request --> Auth
    Auth -->|No| Error401
    Auth -->|Yes| LoadBuild
    LoadBuild -->|Not Found| Error404
    LoadBuild -->|Found| CheckOwner
    CheckOwner -->|Yes| EnrichData
    CheckOwner -->|No| CheckPublic
    CheckPublic -->|No| Error403
    CheckPublic -->|Yes| EnrichData
    EnrichData --> CalcStats
    CalcStats --> Response
```

## Import/Export Endpoints

### POST /import

```mermaid
graph TB
    Request[POST /import<br/>multipart/form-data]
    
    subgraph "Validation"
        FileType{Valid Type?}
        FileSize{Size OK?}
        FileScan[Scan Content]
    end
    
    subgraph "Processing"
        Queue[Add to Queue]
        Worker[Background Worker]
        Parse[Parse Data]
        Validate[Validate Data]
        Import[Import to DB]
    end
    
    subgraph "Response"
        JobID[Return Job ID]
        Status[Check Status]
        Complete[Import Complete]
    end
    
    Request --> FileType
    FileType -->|No| Error400[400 Bad Request]
    FileType -->|Yes| FileSize
    FileSize -->|Too Large| Error413[413 Too Large]
    FileSize -->|OK| FileScan
    FileScan --> Queue
    Queue --> JobID
    
    Queue -.-> Worker
    Worker --> Parse
    Parse --> Validate
    Validate --> Import
    Import --> Complete
    
    JobID --> Status
    Status --> Complete
```

**File Upload Schema:**
```
Content-Type: multipart/form-data

file: build_data.mhd (binary)
type: "mhd" | "json" | "mxd"
options: {
  "override_existing": false,
  "validate_only": false
}
```

### GET /import/status/{job_id}

```mermaid
stateDiagram-v2
    [*] --> Queued
    Queued --> Processing
    Processing --> Validating
    Validating --> Importing
    Importing --> Completed
    Importing --> Failed
    Processing --> Failed
    Validating --> Failed
    
    Completed --> [*]
    Failed --> [*]
```

**Response Schema:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 45,
  "total_records": 1000,
  "processed_records": 450,
  "errors": [],
  "started_at": "2025-01-19T10:00:00Z",
  "completed_at": null,
  "result": null
}
```

## Error Response Format

```mermaid
graph TD
    Error[Error Occurred]
    
    subgraph "Error Types"
        Val[Validation Error<br/>400]
        Auth[Auth Error<br/>401/403]
        NotFound[Not Found<br/>404]
        Conflict[Conflict<br/>409]
        Server[Server Error<br/>500]
    end
    
    subgraph "Error Response"
        Status[HTTP Status Code]
        Body[JSON Error Body]
        Headers[Error Headers]
    end
    
    Error --> Val
    Error --> Auth
    Error --> NotFound
    Error --> Conflict
    Error --> Server
    
    Val --> Status
    Auth --> Status
    NotFound --> Status
    Conflict --> Status
    Server --> Status
    
    Status --> Body
    Status --> Headers
```

**Standard Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_errors": {
        "email": ["Invalid email format"],
        "password": ["Password too short"]
      }
    },
    "request_id": "req_123456",
    "timestamp": "2025-01-19T10:00:00Z"
  }
}
```

## Rate Limiting

```mermaid
graph LR
    Request[API Request]
    RateLimit{Rate Limit<br/>Check}
    Counter[Request Counter]
    Window[Time Window]
    Allow[Allow Request]
    Deny[429 Too Many]
    
    Request --> RateLimit
    RateLimit --> Counter
    Counter --> Window
    
    Window -->|Under Limit| Allow
    Window -->|Over Limit| Deny
    
    style Deny fill:#f44336
    style Allow fill:#4caf50
```

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1737284400
X-RateLimit-Window: 3600
```

## API Versioning

```mermaid
graph TD
    Request[Client Request]
    
    subgraph "Version Selection"
        Header[Accept Header<br/>application/vnd.midshero.v2+json]
        URL[URL Path<br/>/api/v2/builds]
        Default[Default Version<br/>Latest Stable]
    end
    
    subgraph "Version Handling"
        Router[Version Router]
        V1[v1 Handlers]
        V2[v2 Handlers]
        V3[v3 Handlers<br/>Beta]
    end
    
    Request --> Header
    Request --> URL
    Request --> Default
    
    Header --> Router
    URL --> Router
    Default --> Router
    
    Router --> V1
    Router --> V2
    Router --> V3
```

## WebSocket Events

```mermaid
sequenceDiagram
    participant Client
    participant WebSocket
    participant Auth
    participant BuildService
    participant Redis
    
    Client->>WebSocket: Connect + Token
    WebSocket->>Auth: Verify Token
    Auth-->>WebSocket: User Context
    WebSocket->>Client: Connected
    
    Client->>WebSocket: Subscribe to Build
    WebSocket->>Redis: Subscribe Channel
    
    Note over BuildService: Another user updates build
    
    BuildService->>Redis: Publish Update
    Redis->>WebSocket: Build Updated
    WebSocket->>Client: Build Update Event
    
    Client->>WebSocket: Disconnect
    WebSocket->>Redis: Unsubscribe
    WebSocket->>Client: Disconnected
```

**WebSocket Events:**
- `build.updated`: Build data changed
- `build.deleted`: Build was deleted
- `import.progress`: Import job progress
- `import.complete`: Import job finished

This API specification provides a comprehensive overview of all endpoints, their behavior, and data formats.