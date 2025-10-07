# 🏗️ New Simple Architecture Design

## Core Principle
**One Config File, Zero APIs, Direct Links Only**

## New File Structure

```
src/
├── config/
│   └── services.ts              # Single source of truth
├── components/
│   ├── ServiceGrid.tsx          # Simplified grid layout
│   ├── ServiceCard.tsx          # Simple link card
│   └── HealthIndicator.tsx      # Optional health check
├── hooks/
│   └── useHealthCheck.ts        # Optional simple health check
└── app/
    ├── layout.tsx              # No complex providers
    └── page.tsx                # Simple service display
```

## Service Interface

```typescript
interface Service {
  id: string;                   // Unique identifier
  name: string;                 // Display name
  url: string;                  # Direct external URL
  icon: string;                 # Emoji or icon
  description: string;          # Brief description
  category: 'ai' | 'development' | 'storage' | 'infrastructure';
  healthCheck?: string;         # Optional health check URL
}
```

## Data Flow

```
Static Config → ServiceGrid → ServiceCard → External URL
```

**No More**:
- API routes for service management
- Dynamic service loading from NixOS
- Complex proxy systems
- Service registries
- Multiple configuration sources
- Runtime service discovery

## Current Services Mapping

Based on analysis, we have these services to migrate:
1. Code Server (8889) → 'https://nixos.tail4ed625.ts.net:8889/'
2. AI Gateway (8892) → 'https://nixos.tail4ed625.ts.net:8892/'
3. AI Agents (8893) → 'https://nixos.tail4ed625.ts.net:8893/'
4. AI Knowledge (8894) → 'https://nixos.tail4ed625.ts.net:8894/'
5. GPT Realtime Voice (8891) → 'https://nixos.tail4ed625.ts.net:8891/'
6. n8n Workflow (5678) → 'https://nixos.tail4ed625.ts.net:5678/'
7. Syncthing (8384) → 'https://nixos.tail4ed625.ts.net:8384/'
8. NATS (8222) → 'https://nixos.tail4ed625.ts.net:8222/'
9. File Manager (8082) → 'https://nixos.tail4ed625.ts.net:8082/'
10. Mumuko (8895) → 'https://nixos.tail4ed625.ts.net:8895/'
11. Dashboard (3005) → '/' (internal link)

## Health Check Strategy

Optional simple health checks using:
- `fetch()` with `mode: 'no-cors'` for basic connectivity
- 30-second intervals
- Graceful fallback when health check fails
- No complex proxy health checking

## Bundle Size Impact

**Expected Reductions**:
- Remove all API route handlers: ~50KB
- Remove complex service management: ~30KB
- Remove proxy utilities: ~20KB
- Simplified components: ~10KB
- **Total estimated reduction: ~110KB** (significant for a dashboard app)

## Migration Benefits

1. **Maintainability**: Single config file changes
2. **Reliability**: No runtime service discovery failures
3. **Performance**: Smaller bundle, faster load times
4. **Simplicity**: Anyone can add/modify services
5. **Debugging**: Clear, predictable data flow