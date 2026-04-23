# RMI Separation of Concerns Architecture
**Version:** 2.0  
**Date:** 2026-04-12  
**Status:** Design Document

---

## 1. Architectural Overview

### Core Principle
Each layer has a single responsibility and communicates through well-defined interfaces. Dependencies flow downward only.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Web App    │  │   Dashboard  │  │   Telegram │  │   Browser    │    │
│  │   (Public)   │  │   (Admin)    │  │   Bot      │  │   Extension  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │           │
│         └─────────────────┴─────────────────┴─────────────────┘           │
│                                    │                                       │
│                         HTTP/WebSocket/API Calls                          │
└────────────────────────────────────┼───────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼───────────────────────────────────────┐
│                         API GATEWAY LAYER                                  │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐  │
│  │                         FastAPI Application                          │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │  │
│  │  │   Auth     │ │  Rate      │ │  Request   │ │  Response  │        │  │
│  │  │ Middleware │ │  Limiter   │ │  Logger    │ │  Formatter │        │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼───────────────────────────────────────┐
│                         API LAYER (Routers)                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │  Core API    │  │  Crypto API  │  │   CRM API    │  │  Tools API   │     │
│  │  /api/core   │  │ /api/crypto  │  │  /api/crm    │  │ /api/tools   │     │
│  │              │  │              │  │              │  │              │     │
│  │ • Auth       │  │ • Contract   │  │ • Evidence   │  │ • Processor  │     │
│  │ • Users      │  │ • Token      │  │ • Wallets    │  │ • Tracer     │     │
│  │ • Billing    │  │ • Wallet     │  │ • Reports    │  │ • OCR        │     │
│  │ • API Keys   │  │ • Alerts     │  │ • Timeline   │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                       │
│  │  OSINT API   │  │  Token API   │  │  Admin API   │                       │
│  │ /api/osint   │  │ /api/token   │  │ /api/admin   │                       │
│  │              │  │              │  │              │                       │
│  │ • Face Rec   │  │ • Airdrop    │  │ • Dashboard  │                       │
│  │ • Dating     │  │ • Discounts  │  │ • Users      │                       │
│  │ • Scammer ID │  │ • Holdings   │  │ • System     │                       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                       │
│         │                 │                 │                                 │
│         └─────────────────┴─────────────────┘                                 │
│                      Calls Services                                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼───────────────────────────────────────────┐
│                         SERVICE LAYER (Business Logic)                     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Core Services                                     │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │    │
│  │  │   Auth     │ │   User     │ │  Billing   │ │   Credit   │      │    │
│  │  │  Service   │ │  Service   │ │  Service   │ │  Service   │      │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Crypto Services                                   │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │    │
│  │  │ Contract   │ │   Token    │ │   Wallet   │ │   Price    │      │    │
│  │  │  Analyzer  │ │  Scorer    │ │  Analyzer  │ │   Feed     │      │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Investigation Services                              │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │    │
│  │  │ Evidence   │ │   Case     │ │   Report   │ │   Wallet   │      │    │
│  │  │  Processor │ │  Manager   │ │  Generator │ │  Tracer    │      │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    External Integrations                             │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │    │
│  │  │   Helius   │ │   Arkham   │ │  Birdeye   │ │  OpenRouter│      │    │
│  │  │  (Solana)  │ │  (Intel)   │ │  (Prices) │ │   (AI)     │      │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│         Uses Data Layer                                                       │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼───────────────────────────────────────────┐
│                         DATA LAYER (Persistence)                           │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Primary Database (Supabase/PostgreSQL)            │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │    │
│  │  │   Users    │ │   Cases    │ │  Wallets   │ │ Transactions│     │    │
│  │  │   Table    │ │   Table    │ │   Table    │ │   Table     │     │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Cache Layer (Redis)                              │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │    │
│  │  │  Sessions  │ │  Rate Limit│ │  Price     │ │  API       │      │    │
│  │  │            │ │  Counters  │ │  Cache     │ │  Response  │      │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    File Storage                                      │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐                      │    │
│  │  │  Evidence  │ │  Reports   │ │  Uploads   │                      │    │
│  │  │  Files     │ │  (PDF)     │ │  (Temp)    │                      │    │
│  │  └────────────┘ └────────────┘ └────────────┘                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer Responsibilities

### 2.1 Presentation Layer
**Responsibility:** User interface and experience only

**Contains:**
- HTML templates and components
- CSS stylesheets
- JavaScript/TypeScript frontend code
- Mobile app interfaces
- Bot message handlers

**Rules:**
- NO direct database access
- NO business logic
- ONLY calls API endpoints
- Handles user input validation (client-side)
- Manages UI state only

**Location:** `/frontend/`

---

### 2.2 API Gateway Layer
**Responsibility:** Request routing, authentication, rate limiting

**Contains:**
- FastAPI application instance
- Middleware chain (auth, logging, rate limiting)
- Router registration
- Exception handlers
- CORS configuration

**Rules:**
- NO business logic
- ONLY request/response handling
- Validates JWT tokens
- Applies rate limits
- Routes to appropriate API module

**Location:** `/backend/main.py`, `/backend/middleware/`

---

### 2.3 API Layer (Routers)
**Responsibility:** HTTP interface definition, request/response models

**Contains:**
- Route definitions (GET, POST, PUT, DELETE)
- Pydantic request/response models
- Path/query parameter validation
- Calling services and returning responses

**Rules:**
- NO direct database queries
- ONLY orchestrates service calls
- Handles HTTP-specific concerns (status codes, headers)
- Maps service responses to HTTP responses

**Location:** `/backend/api/v1/`

---

### 2.4 Service Layer
**Responsibility:** Business logic, data processing, external integrations

**Contains:**
- Business rules and workflows
- Data transformation
- External API calls (Helius, Arkham, etc.)
- Caching logic
- Background task scheduling

**Rules:**
- NO HTTP-specific code
- NO direct database connections (uses repositories)
- Implements business rules
- Handles transaction boundaries
- Calls multiple repositories if needed

**Location:** `/backend/services/`

---

### 2.5 Data Layer
**Responsibility:** Data persistence and retrieval

**Contains:**
- Database models/schemas
- Repository classes (CRUD operations)
- SQL queries
- Migration scripts
- Cache operations

**Rules:**
- NO business logic
- ONLY data access
- Returns raw data or simple DTOs
- Handles connection pooling
- Manages transactions

**Location:** `/backend/database/`, `/backend/models/`

---

## 3. Dependency Flow

### Correct Flow (Top → Bottom)
```
Presentation → API Gateway → API Routers → Services → Data Layer
```

### Forbidden Flows
```
❌ Service → API Router (circular dependency)
❌ Data Layer → Service (bypassing business logic)
❌ API Router → Data Layer (bypassing services)
❌ Presentation → Service (must go through API)
```

### Cross-Cutting Concerns
```
All Layers → Config (/backend/config/)
All Layers → Logging
All Layers → Monitoring/Metrics
```

---

## 4. Module Organization

### 4.1 By Domain (Vertical Slicing)
Each domain has its own API, service, and data components:

```
Domain: Crypto
├── API: /api/v1/crypto/
│   ├── contracts.py
│   ├── tokens.py
│   ├── wallets.py
│   └── alerts.py
├── Services:
│   ├── ContractAnalyzer
│   ├── TokenScorer
│   └── WalletAnalyzer
└── Data:
    ├── token_contracts table
    ├── analyzed_wallets table
    └── wallet_transactions table

Domain: CRM Investigation
├── API: /api/v1/crm/
│   ├── evidence.py
│   ├── wallets.py
│   ├── reports.py
│   ├── timeline.py
│   └── cases.py
├── Services:
│   ├── EvidenceProcessor
│   ├── CaseManager
│   └── ReportGenerator
└── Data:
    ├── investigation_cases table
    ├── evidence_items table
    └── investigation_wallets table
```

### 4.2 By Layer (Horizontal Slicing)
All domains share the same architectural layers:

```
Layer: API
├── /api/v1/core/
├── /api/v1/crypto/
├── /api/v1/crm/
├── /api/v1/tools/
├── /api/v1/osint/
└── /api/v1/token/

Layer: Services
├── AuthService
├── UserService
├── BillingService
├── ContractAnalyzer
├── TokenScorer
├── CaseManager
└── EvidenceProcessor

Layer: Data
├── Database Connection
├── Repository Classes
└── Cache Client
```

---

## 5. Interface Contracts

### 5.1 API to Service Interface

```python
# API Layer (Router)
@router.get("/{address}/score")
async def get_token_score(address: str, chain: str):
    # Calls service, handles HTTP concerns
    score = await token_service.calculate_score(address, chain)
    return {"score": score}

# Service Layer
class TokenService:
    async def calculate_score(self, address: str, chain: str) -> TokenScore:
        # Business logic only
        contract_data = await self.contract_repo.get(address, chain)
        holder_data = await self.holder_repo.get_distribution(address, chain)
        
        score = self._calculate_risk(contract_data, holder_data)
        return TokenScore(score=score)
```

### 5.2 Service to Data Interface

```python
# Service Layer
class EvidenceService:
    def __init__(self, evidence_repo: EvidenceRepository):
        self.repo = evidence_repo
    
    async def add_evidence(self, case_id: str, file: UploadFile) -> Evidence:
        # Business logic
        file_hash = await self._calculate_hash(file)
        
        # Data access through repository
        evidence = await self.repo.create(
            case_id=case_id,
            file_hash=file_hash,
            file_size=file.size
        )
        return evidence

# Data Layer
class EvidenceRepository:
    async def create(self, case_id: str, file_hash: str, file_size: int) -> Evidence:
        # Database interaction only
        result = await self.db.execute(
            "INSERT INTO evidence_items (case_id, file_hash, file_size) VALUES ($1, $2, $3) RETURNING *",
            case_id, file_hash, file_size
        )
        return Evidence(**result)
```

---

## 6. Communication Patterns

### 6.1 Synchronous (Request/Response)
For immediate operations:
- User authentication
- Token scoring
- Evidence upload
- Wallet analysis

### 6.2 Asynchronous (Background Tasks)
For long-running operations:
- Deep contract analysis
- Multi-hop wallet tracing
- Batch evidence processing
- Report generation

Implementation:
```python
# API Layer
@router.post("/analyze-deep")
async def analyze_deep(request: AnalysisRequest, background_tasks: BackgroundTasks):
    # Queue background task
    background_tasks.add_task(contract_service.deep_analyze, request.address)
    return {"status": "processing", "job_id": generate_id()}

# Service Layer
class ContractService:
    async def deep_analyze(self, address: str):
        # Long-running operation
        await self._analyze_bytecode(address)
        await self._check_similar_contracts(address)
        await self._generate_risk_report(address)
```

---

## 7. Error Handling Strategy

### 7.1 Layer-Specific Errors

```
Data Layer:
  - DatabaseConnectionError
  - RecordNotFoundError
  - DuplicateRecordError

Service Layer:
  - BusinessRuleViolation
  - ExternalAPIError
  - InsufficientCreditsError

API Layer:
  - HTTPException (400, 401, 404, 500)
  - ValidationError (Pydantic)

Presentation Layer:
  - User-facing error messages
  - Form validation errors
```

### 7.2 Error Propagation

```python
# Data Layer raises domain-specific error
class WalletRepository:
    async def get(self, address: str) -> Wallet:
        result = await self.db.fetch_one("SELECT * FROM wallets WHERE address = $1", address)
        if not result:
            raise RecordNotFoundError(f"Wallet {address} not found")
        return Wallet(**result)

# Service layer handles or transforms
class WalletService:
    async def get_wallet(self, address: str) -> Wallet:
        try:
            return await self.repo.get(address)
        except RecordNotFoundError:
            # Fetch from blockchain instead
            return await self._fetch_from_chain(address)

# API layer converts to HTTP
@router.get("/{address}")
async def get_wallet(address: str):
    try:
        wallet = await wallet_service.get_wallet(address)
        return wallet
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Wallet not found")
```

---

## 8. Testing Strategy

### 8.1 Unit Tests (per layer)

```
Data Layer:
  - Test SQL queries
  - Mock database connection
  - Test transaction handling

Service Layer:
  - Mock repositories
  - Test business logic
  - Test external API integrations (mocked)

API Layer:
  - Mock services
  - Test request/response models
  - Test route handlers
```

### 8.2 Integration Tests

```
Cross-Layer:
  - Test full request flow
  - Test database integration
  - Test external API calls (sandbox mode)
```

---

## 9. Directory Structure

```
/root/rmi/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py          # Router aggregation
│   │       ├── core/                 # Auth, users, billing
│   │       ├── crypto/               # Contract analysis
│   │       ├── crm/                  # Investigation
│   │       ├── tools/                # Processing tools
│   │       ├── osint/                # OSINT tools
│   │       └── token/                # Tokenomics
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── billing_service.py
│   │   ├── token_scorer.py
│   │   ├── contract_analyzer.py
│   │   ├── case_manager.py
│   │   └── evidence_processor.py
│   │
│   ├── repositories/               # NEW: Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── wallet_repository.py
│   │   ├── case_repository.py
│   │   └── evidence_repository.py
│   │
│   ├── models/                     # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── wallet.py
│   │   ├── token.py
│   │   └── case.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py           # Connection pooling
│   │   ├── migrations/
│   │   └── unified_schema.sql
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py                 # JWT validation
│   │   ├── rate_limit.py
│   │   └── logging.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Pydantic Settings
│   │   └── environments/
│   │
│   └── main.py                     # App factory
│
├── frontend/
│   ├── web/                        # Public website
│   ├── dashboard/                  # Admin dashboard
│   ├── trenches/                   # Retail interface
│   └── shared/                     # Common assets
│
├── data/                          # Data files (not code)
│   ├── investigation/            # Evidence files
│   └── uploads/                  # Temporary uploads
│
├── tests/                        # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/                      # Deployment scripts
│   ├── deploy/
│   └── maintenance/
│
└── docs/                         # Documentation
    ├── architecture/
    ├── api/
    └── deployment/
```

---

## 10. Implementation Guidelines

### 10.1 Do's

✅ Keep each layer focused on its responsibility
✅ Use dependency injection (pass repositories to services)
✅ Return domain models from services
✅ Handle HTTP concerns only in API layer
✅ Use background tasks for long operations
✅ Log at all layer boundaries
✅ Validate at API layer (Pydantic)
✅ Write tests for each layer independently

### 10.2 Don'ts

❌ Don't bypass service layer from API
❌ Don't put business logic in repositories
❌ Don't access database directly from API
❌ Don't use HTTP-specific code in services
❌ Don't import presentation code into backend
❌ Don't mix async and sync I/O in same flow
❌ Don't return raw database rows from services

---

## 11. Migration Path

### Phase 1: Foundation (✅ Complete)
- ✅ Create new directory structure
- ✅ Create unified API layer
- ✅ Create unified schema

### Phase 2: Service Extraction (Next)
1. Create Repository classes
2. Migrate existing services to use repositories
3. Connect new API routes to services
4. Test each domain independently

### Phase 3: Cleanup
1. Deprecate old routes
2. Remove scattered SQL files
3. Clean up root-level files
4. Archive obsolete code

### Phase 4: Optimization
1. Add caching layer
2. Implement background tasks
3. Add monitoring
4. Performance tuning

---

**This architecture ensures maintainability, testability, and scalability as the platform grows.**
