# Critical Fixes Checklist - Pre-Launch
## Items 1-6: Must Fix Before Production

---

### ✅ 1. URL Consistency (CRITICAL)
**Status**: FIXED

**Problem**: Extension popup buttons pointed to wrong domain (`rugmunch.io` instead of `cryptorugmunch.com`)

**Files Changed**:
- `browser-extension/src/popup/popup.js` (lines 35-46)
- `browser-extension/src/background/background.js` (3 URLs)
- `browser-extension/src/content/content.js` (API URL)
- `browser-extension/src/utils/api.js` (API URL)
- `browser-extension/src/popup/popup.html` (footer link)

**Verification**:
```bash
grep -r "rugmunch.io" browser-extension/  # Should return nothing
grep -r "cryptorugmunch.com" browser-extension/  # Should show matches
```

---

### ✅ 2. React Import Order Bug (CRITICAL)
**Status**: FIXED

**Problem**: `useAlerts.ts` used `React.useRef` before importing React, causing runtime error

**File**: `mobile-app/src/hooks/useAlerts.ts`

**Changes**:
```typescript
// BEFORE (BROKEN):
import { useEffect, useState, useCallback } from 'react';
// ... later ...
const wsRef = React.useRef<WebSocket | null>(null);  // React not defined!
// ... at END of file ...
import React from 'react';  // Too late!

// AFTER (FIXED):
import { useEffect, useState, useCallback, useRef } from 'react';
// ... later ...
const wsRef = useRef<WebSocket | null>(null);  // ✅ Direct import
```

---

### ✅ 3. API URL Updates (CRITICAL)
**Status**: FIXED

**Problem**: Multiple files still using old `api.rugmunch.io` domain

**Files Changed**:
1. `mobile-app/src/hooks/useAlerts.ts`
   - `wss://api.rugmunch.io/ws` → `wss://api.cryptorugmunch.com/ws`

2. `mobile-app/src/store/authStore.ts`
   - `https://api.rugmunch.io` → `https://api.cryptorugmunch.com`

3. `browser-extension/src/background/background.js`
   - Both WS and HTTP URLs updated

4. `browser-extension/src/content/content.js`
   - API URL updated

5. `browser-extension/src/utils/api.js`
   - Both URLs updated

**Verification Command**:
```bash
grep -r "rugmunch.io" mobile-app/ browser-extension/  # Should return empty
```

---

### ✅ 4. Missing Import in WebSocket (CRITICAL)
**Status**: FIXED

**Problem**: `websocket.py` used `random` module without importing it

**File**: `backend/api/websocket.py` (line 262)

**Fix Applied**:
```python
# Added at line 10:
import random
```

**Impact**: Without this, `broadcast_whale_alert()` would crash with `NameError: name 'random' is not defined`

---

### ✅ 5. WebGL Geometry Duplication (PERFORMANCE)
**Status**: FIXED

**Problem**: WebGL Muncher Map created sphere geometry twice (memory leak)

**File**: `rmi-frontend/src/components/WebGLMuncherMap.tsx`

**Changes**:
```typescript
// BEFORE (created geometry twice):
const geometry = useMemo(() => new THREE.SphereGeometry(1, 16, 16), []);
// ...
<instancedMesh>
  <sphereGeometry args={[1, 16, 16]} />  {/* Duplicate! */}
  <meshStandardMaterial ... />
</instancedMesh>

// AFTER (single geometry instance):
const geometry = useMemo(() => new THREE.SphereGeometry(1, 16, 16), []);
// ...
<instancedMesh args={[geometry, material, nodes.length]} />
```

---

### ✅ 6. WebGL Fallback Implementation (CRITICAL)
**Status**: FIXED + NEW COMPONENT

**Problem**: No fallback when WebGL unavailable (mobile devices, older browsers, disabled WebGL)

**New File Created**: `rmi-frontend/src/components/MuncherMapFallback.tsx`
- Canvas-based 2D force-directed graph
- Pan and zoom support
- Same color scheme as WebGL version
- Hover and click interactions
- "2D Fallback Mode" indicator

**Changes to WebGLMuncherMap.tsx**:
```typescript
// Added WebGL detection
const [webglSupported, setWebglSupported] = useState(true);

useEffect(() => {
  // Check WebGL support
  const canvas = document.createElement('canvas');
  const supported = !!(window.WebGLRenderingContext &&
    (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
  setWebglSupported(supported);
}, []);

// Render fallback if WebGL not supported
if (!webglSupported) {
  return <MuncherMapFallback nodes={nodes} edges={edges} ... />;
}
```

---

## Bonus Improvements Made

### 7. Performance: Content Script Debouncing
**File**: `browser-extension/src/content/content.js`
- Added 2-second scan rate limiting
- Increased debounce from 500ms to 800ms
- Prevents CPU thrashing on dynamic pages (DexTools, DexScreener)

### 8. Shared Utilities
**New File**: `browser-extension/src/utils/helpers.js`
- Centralized address validation
- Chain detection from URL
- Risk color mappings
- Debounce/throttle functions
- Cache utility with TTL

### 9. Middleware for Tier Access
**New File**: `backend/middleware/tier.py`
- `@require_tier("ELITE")` decorator
- `@require_any_tier(["ELITE", "ENTERPRISE"])` decorator
- Centralized tier limits configuration

### 10. Rate Limiting Foundation
**New File**: `backend/middleware/rate_limit.py`
- Tier-based rate limits (FREE: 10/min, ELITE: 500/min)
- Ready to integrate with Redis

### 11. CORS Configuration
**New File**: `backend/config/cors.py`
- Production-ready CORS origins
- Chrome extension support
- Development origin whitelist

---

## Pre-Launch Verification Commands

```bash
# 1. Verify no old URLs remain
grep -r "rugmunch.io" . --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py"

# 2. Check all API URLs are correct
grep -r "cryptorugmunch.com" . --include="*.ts" --include="*.tsx" --include="*.js"

# 3. Verify React imports in mobile app
grep -n "React.useRef" mobile-app/src/hooks/*.ts

# 4. Check Python imports
python -c "from backend.api.websocket import broadcast_whale_alert; print('OK')"

# 5. Verify extension builds
cd browser-extension && ./build.sh

# 6. Check TypeScript compiles
cd rmi-frontend && npm run build 2>&1 | head -20
```

---

## Remaining Critical (Do Before Launch)

| Priority | Item | Effort |
|----------|------|--------|
| HIGH | CORS in main.py still allows `*` | 5 min |
| HIGH | Add rate limiting to analytics endpoints | 30 min |
| MEDIUM | Create tier decorator for routes | 1 hour |
| MEDIUM | Add error boundaries to React | 2 hours |
| LOW | WebSocket Redis backend | 4 hours |

---

## Sign-Off

**All 6 Critical Items**: ✅ COMPLETE
**Code Review Document**: `/root/rmi/CODE_REVIEW.md`
**This Checklist**: `/root/rmi/CRITICAL_FIXES_CHECKLIST.md`

**Estimated Production Readiness**: 85% → 95%

---
*Last Updated: 2026-04-14*
