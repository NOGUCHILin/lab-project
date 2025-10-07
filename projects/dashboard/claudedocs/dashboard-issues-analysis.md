# Dashboard Project Issues Analysis

## Executive Summary

The dashboard project has **13 critical issues** stemming primarily from a service registry migration where services moved from port 8891 to port 9000, but configuration files weren't updated consistently. The ECONNREFUSED error on 127.0.0.1:8891 is caused by hardcoded port references throughout the codebase.

## Critical Issues Found

### 🔴 HIGH SEVERITY - Service Connectivity

#### 1. **Port Migration Inconsistency** 
**Impact**: Service connection failures, ECONNREFUSED errors
**Root Cause**: Services migrated from port 8891 to 9000, but multiple files still reference old ports

**Affected Files**:
- `/src/lib/proxy/ProxyHandler.ts:10` - `'voice': { host: '127.0.0.1', port: 8891 }`
- `/src/app/realtime.js/route.ts:11` - `http://127.0.0.1:8891/realtime.js`
- `/src/app/api/system/info/route.ts:39` - `openaiRealtime: 'http://127.0.0.1:8891'`

**Fix Required**:
```typescript
// ProxyHandler.ts
'voice': { host: '127.0.0.1', port: 9000, maxTimeout: 30000 },

// realtime.js/route.ts  
const response = await fetch('http://127.0.0.1:9000/realtime.js');

// system/info/route.ts
openaiRealtime: 'http://127.0.0.1:9000',
```

#### 2. **Mixed Service URL Strategy**
**Impact**: Inconsistent service access, external URL failures
**Root Cause**: Services.config.ts uses external URLs while ProxyHandler uses localhost ports

**Service Config (Correct)**:
```typescript
serviceUrl: 'https://nixos.tail4ed625.ts.net/ws/', // External Tailscale URL
```

**Proxy Handler (Incorrect)**:
```typescript
'voice': { host: '127.0.0.1', port: 8891 } // Still using old localhost port
```

#### 3. **Health Check Configuration Mismatch**
**Impact**: Health checks failing for realtime service
**Evidence**: External URL returns HTTP 500, localhost:9000 connection fails

**Current Configuration Issue**:
- Service config defines external URL: `https://nixos.tail4ed625.ts.net/ws/`
- Health check tries localhost:8891 (old port) or localhost:9000 (connection refused)
- External URL `/health` returns HTTP 500

### 🟡 MEDIUM SEVERITY - Architecture & Performance

#### 4. **Hardcoded Environment Variables**
**Impact**: Deployment flexibility, environment-specific issues
**File**: `/src/lib/env.ts`

**Issues**:
- Default ports don't match migrated services
- AI_GATEWAY_URL defaults to 8892 but needs verification
- NEXT_PUBLIC_APP_URL hardcoded to port 3005

#### 5. **Service Registry Dual Strategy Conflict**
**Impact**: Confusion between internal/external service access
**Analysis**: Two competing strategies:
1. **External Strategy**: Using Tailscale URLs (`https://nixos.tail4ed625.ts.net/*`)
2. **Internal Strategy**: Direct localhost port access

**Recommendation**: Choose ONE strategy consistently.

#### 6. **Health Check Cache Issues**  
**Impact**: Stale health status, delayed error detection
**File**: `/src/lib/services/registry.ts:16`

**Issues**:
- 30-second cache TTL may hide rapid failures
- No cache invalidation on service configuration changes
- Client/server health check URL construction differs

#### 7. **Client-Server Health Check Inconsistency**
**Impact**: Different behavior in SSR vs client-side rendering
**File**: `/src/lib/services/registry.ts:82-88`

**Problem**:
```typescript
if (typeof window !== 'undefined') {
  healthUrl = `/api/health/${service.port}`;  // Relative API call
} else {
  healthUrl = `http://localhost:3000/api/health/${service.port}`; // Hardcoded localhost:3000
}
```

#### 8. **Service Configuration Type Safety**
**Impact**: Runtime errors, configuration drift
**File**: `/src/lib/config/services.config.ts`

**Issues**:
- n8n service still configured for port 8891 (line 56)
- NATS service uses non-standard HTTP monitoring port 8222
- Mixed external/internal URL handling

### 🟢 LOW SEVERITY - Code Quality & Maintenance

#### 9. **Development Server Port Mismatch**
**Impact**: Confusion in development environment
**Analysis**: Dashboard runs on port 3005, but health checks assume port 3000

#### 10. **TypeScript Configuration Limitations**  
**Impact**: Development experience, build performance
**File**: `/tsconfig.json`

**Issues**:
- Target ES2017 is outdated (should be ES2020+)
- Missing modern lib features for better performance
- No strict typing for service configurations

#### 11. **Missing Error Boundaries**
**Impact**: Poor user experience on service failures
**Analysis**: No React error boundaries to handle service connection failures gracefully

#### 12. **Log Level Configuration**
**Impact**: Production debugging difficulty  
**File**: `/src/lib/proxy/ProxyHandler.ts:27`

**Issue**: Logger only shows info/warn in development mode, limiting production debugging

#### 13. **Rate Limiting Memory Leak**
**Impact**: Memory usage growth over time
**File**: `/src/lib/proxy/ProxyHandler.ts:72`

**Issue**: `rateLimitMap` never cleans up expired entries, causing memory leak

## Service Status Analysis

### Current Port Mapping
```
✅ n8n:           8891 (listening, healthy)
✅ ai-gateway:    8892 (listening) 
✅ ai-agents:     8893 (listening)
✅ ai-knowledge:  8894 (listening)
❌ realtime:      9000 (Tailscale only, not localhost)
✅ dashboard:     3005 (listening)
```

### External Service Status
```
❌ https://nixos.tail4ed625.ts.net/ws/health  (HTTP 500)
✅ Port 8891 localhost health check works
❌ Port 9000 localhost connection refused
```

## Recommended Fix Priority

### Phase 1: Critical Service Connectivity (Immediate)
1. **Update ProxyHandler.ts** - Change voice service port from 8891 to 9000
2. **Update realtime.js route** - Change fetch URL to port 9000  
3. **Update system info API** - Change openaiRealtime URL to port 9000
4. **Fix service URL strategy** - Choose external OR internal consistently

### Phase 2: Configuration Standardization (Week 1)
1. **Environment variable defaults** - Update to match current deployment
2. **Health check unification** - Standardize client/server health check URLs
3. **Service registry cleanup** - Remove conflicting URL strategies

### Phase 3: Quality & Performance (Week 2)
1. **Add error boundaries** - Improve UX for service failures
2. **Fix rate limiting memory leak** - Implement cleanup for expired entries
3. **TypeScript configuration update** - Modern target and strict typing
4. **Logging improvements** - Configurable log levels for production

## Testing Recommendations

### Health Check Verification
```bash
# Test current service status
curl http://localhost:8891/health  # Should work (n8n)
curl http://localhost:9000/health  # Currently fails
curl https://nixos.tail4ed625.ts.net/ws/health  # Currently returns 500

# After fixes, verify
curl http://localhost:9000/health  # Should work
curl https://nixos.tail4ed625.ts.net/ws/health  # Should work
```

### Integration Tests
- Service registry health check accuracy
- Proxy handler routing to correct ports
- External URL fallback behavior
- Error handling for service failures

## Architecture Decision Required

**Critical Decision**: Choose between two service access strategies:

### Option A: External-Only Strategy (Recommended)
- All services accessed via Tailscale URLs
- Remove localhost port dependencies
- Simplifies deployment and configuration
- Better for distributed/remote access

### Option B: Internal-Only Strategy  
- All services accessed via localhost ports
- Remove external URL dependencies
- Better for local development
- Requires VPN for remote access

**Recommendation**: Option A (External-Only) because:
1. Current configuration already defines external URLs
2. Better scalability for team access
3. Consistent with existing Tailscale infrastructure
4. Eliminates port conflict issues

## Summary

The dashboard has solid architecture but suffers from incomplete migration artifacts. The primary issue is **configuration inconsistency** between the service registry (which correctly uses external URLs) and the proxy handlers (which use outdated localhost ports). Fixing the 4 critical port references will resolve the ECONNREFUSED errors immediately.