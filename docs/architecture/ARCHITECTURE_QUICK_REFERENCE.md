# Architecture Quick Reference
**For day-to-day development**

---

## "Where Does This Go?" Cheat Sheet

| If you need to... | Put it in... | Example |
|-------------------|--------------|---------|
| Add an HTTP endpoint | `/backend/api/v1/{domain}/` | New wallet analysis route |
| Change business logic | `/backend/services/` | Modify scoring algorithm |
| Query database | `/backend/repositories/` | Get user by email |
| Define data structure | `/backend/models/` | Pydantic model for response |
| Add middleware | `/backend/middleware/` | Rate limiting per user |
| Change UI | `/frontend/{web|dashboard|trenches}/` | New button component |
| Store config | `/backend/config/settings.py` | API key, database URL |
| Background task | Service method + BackgroundTasks | OCR processing |

---

## Dependency Flow (Remember: Downward Only!)

```
Frontend → API Gateway → API Router → Service → Repository → Database

✅ CORRECT: API Router calls Service
❌ WRONG: Service calls API Router

✅ CORRECT: Service calls Repository
❌ WRONG: Repository has business logic

✅ CORRECT: Repository returns raw data
❌ WRONG: Repository returns HTTP response
```

---

## Layer-Specific Rules

### API Layer (`/api/v1/`)
```python
# ✅ DO: Handle HTTP concerns
@router.post("/analyze")
async def analyze(request: RequestModel):
    result = await service.analyze(request.data)
    return ResponseModel(data=result)

# ❌ DON'T: Business logic here
@router.post("/analyze")
async def analyze(request: RequestModel):
    # BAD: Calculating score directly
    score = complex_calculation(request.data)
    return {"score": score}
```

### Service Layer (`/services/`)
```python
# ✅ DO: Business logic + orchestration
class TokenService:
    async def analyze(self, address: str) -> Analysis:
        contract = await self.contract_repo.get(address)
        holders = await self.holder_repo.get_top(address)
        score = self._calculate_score(contract, holders)
        return Analysis(score=score)

# ❌ DON'T: HTTP or DB directly
class TokenService:
    async def analyze(self, address: str):
        # BAD: Direct SQL
        result = await db.execute("SELECT * FROM tokens...")
        # BAD: HTTP response
        return {"status": 200, "data": result}
```

### Repository Layer (`/repositories/` - NEW)
```python
# ✅ DO: Data access only
class TokenRepository:
    async def get(self, address: str) -> Token:
        result = await self.db.fetch_one(
            "SELECT * FROM tokens WHERE address = $1", address
        )
        return Token(**result) if result else None

# ❌ DON'T: Business logic
class TokenRepository:
    async def get_risky_tokens(self):
        # BAD: Business rule in query
        return await self.db.execute(
            "SELECT * FROM tokens WHERE score < 50"  # 50 is business rule
        )
```

---

## Common Patterns

### 1. Adding a New Feature

```
1. Define models in /backend/models/
2. Create repository in /backend/repositories/
3. Implement service in /backend/services/
4. Add API routes in /backend/api/v1/{domain}/
5. Add frontend UI in /frontend/{appropriate}/
```

### 2. Calling External APIs

```python
# Service layer handles external calls
class HeliusService:
    async def get_wallet_balance(self, address: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/balance",
                params={"address": address}
            )
            return response.json()
```

### 3. Caching Strategy

```python
# Cache at service layer
class TokenService:
    async def get_price(self, address: str):
        # Check cache first
        cached = await self.cache.get(f"price:{address}")
        if cached:
            return cached

        # Fetch from external API
        price = await self.price_feed.get(address)

        # Store in cache
        await self.cache.set(f"price:{address}", price, ttl=60)
        return price
```

---

## Error Handling by Layer

| Layer | Error Type | Example |
|-------|------------|---------|
| Repository | Database errors | `RecordNotFoundError` |
| Service | Business errors | `InsufficientCreditsError` |
| API | HTTP errors | `HTTPException(status_code=404)` |
| Frontend | User errors | "Invalid wallet address" |

---

## Testing Strategy

```
Unit Tests:
  API: Mock services, test request/response
  Service: Mock repositories, test business logic
  Repository: Mock database, test SQL

Integration Tests:
  Full flow: API → Service → Repository → Database
```

---

## Import Patterns

```python
# Within backend - use relative imports
from ..services import TokenService
from ..models import Token

# Across major boundaries - use absolute
from backend.services import TokenService
from backend.models import Token

# Avoid sys.path hacks (legacy cleanup needed)
# ❌ sys.path.insert(0, '/root/rmi')
```

---

## Quick Commands

```bash
# Start backend
cd /root/rmi/backend && python3 main.py

# Test specific module
python3 -c "from backend.api.v1.crypto import tokens; print('OK')"

# Run migrations
psql -f backend/database/unified_schema.sql

# Check structure
find backend/api/v1 -name "*.py" | head -20
```

---

## Need Help?

1. Check full architecture: `docs/architecture/SEPARATION_OF_CONCERNS.md`
2. Review existing examples in `/backend/api/v1/core/auth.py`
3. Ask: "Does this belong in this layer?"
