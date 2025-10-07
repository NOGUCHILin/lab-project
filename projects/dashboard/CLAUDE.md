# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Unified Dashboard** - a Next.js 15 application that serves as a centralized service registry and monitoring dashboard for NixOS-hosted services. The architecture follows a **frontend-only approach**, acting as a UI layer that connects to various backend services through a service registry pattern.

### Core Architecture

```
[Unified Dashboard] ←→ [External Services]
  (Frontend UI)         (AI APIs, Code Server, Syncthing, etc.)
     ↓                      ↓
  - Service monitoring    - Individual backend services
  - UI/UX dashboard      - Each with their own APIs
  - Health checking      - Accessed via proxy or direct calls
  - Service management   - No backend logic in dashboard
```

**Key Principle**: This dashboard is purely a frontend orchestrator - all business logic resides in the external services it connects to.

## Development Commands

### Core Development
```bash
npm run dev          # Start development server (with Turbopack)
npm run build        # Production build (with Turbopack)
npm run build:nix    # Production build for NixOS (no Turbopack)
npm run start        # Start production server
```

### Quality Assurance
```bash
npm run lint         # Run ESLint
npm run test         # Run Playwright E2E tests
npm run test:ui      # Run E2E tests with UI mode
npm run test:report  # Show test report
```

### Deployment
```bash
npm run deploy       # Full deployment (runs tests + NixOS rebuild)
./scripts/deploy.sh  # Direct script execution
```

The deployment script automatically:
1. Runs E2E tests
2. Rebuilds NixOS system with new dashboard version
3. Performs health checks post-deployment

## Service Registry System

### Adding New Services

Services are configured in `src/lib/config/services.config.ts`. To add a new service:

```typescript
{
  id: 'my-service',
  name: 'My Service',
  port: 8080,
  path: 'https://nixos.tail4ed625.ts.net:8080/',
  icon: '🔧',
  description: 'Service description',
  healthCheck: '/health',
  apiPrefix: '/api/v1',
  category: 'development', // ai | development | storage | infrastructure
  enabled: true,
  config: {
    timeout: 30000,
    external: true  // For services with full URLs
  }
}
```

### Service Architecture Components

- **Service Registry** (`src/lib/services/registry.ts`): Core service management, health checking, caching
- **Service Types** (`src/lib/services/types.ts`): TypeScript definitions for all service-related types
- **Service Hooks** (`src/lib/services/hooks.tsx`): React context and hooks for service state management
- **Service Components**: 
  - `ServiceCard.tsx`: Individual service display cards
  - `ServiceGrid.tsx`: Grid layout for service cards
  - `ProxyTest.tsx`: Service connectivity testing

### Health Check System

- **30-second TTL cache** for health check results
- **Unified API approach**: Uses dashboard's `/api/health/[port]` endpoint
- **Multi-environment support**: Works in both client and server contexts
- **Automatic retry logic** with configurable timeouts

## API Routes & Proxy System

### Health Check API
- `/api/health/[port]` - Health check proxy for any service port

### Service Proxies
- `/api/proxy/[...path]` - Generic service proxy
- `/api/proxy/code/[...path]` - Code Server specific proxy
- `/api/proxy/syncthing/[...path]` - Syncthing specific proxy
- `/api/proxy/voice/[...path]` - Voice service proxy
- `/api/proxy/websocket/[service]` - WebSocket proxy handler

### System APIs
- `/api/system/info` - System information endpoint
- `/api/session` - Session management

## NixOS Integration

### System Service
The dashboard is deployed as a systemd service via NixOS registry-based module (`registry-based/unified-dashboard.nix`):
- Runs under `noguchilin` user
- Automatic restart on failure
- Security hardening enabled
- Production build before start

### Network Configuration
- **Tailscale integration** for secure remote access
- **HTTPS via Tailscale Serve** for external access
- **Internal service discovery** via localhost ports

## Testing Strategy

### E2E Testing with Playwright
- **Configuration**: `playwright.config.ts`
- **Test directory**: `tests/e2e/`
- **Base URL**: `https://nixos.tail4ed625.ts.net` (production URL)
- **Browser**: NixOS Chromium (`/run/current-system/sw/bin/chromium`)
- **CI/CD integration**: Tests run before every deployment

### Test Patterns
- Dashboard load testing
- Service health check validation
- UI interaction testing
- Service grid functionality

## Code Style & Quality

### TypeScript Configuration
- Strict mode enabled
- Path aliases: `@/*` → `./src/*`
- Next.js App Router compatible

### ESLint Setup
- Next.js + TypeScript presets
- Ignores: `.next/`, `out/`, `build/`, `node_modules/`

### Git Hooks (Husky + lint-staged)
- Pre-commit: ESLint auto-fix + E2E tests
- Ensures code quality before commits

## Key Files for New Contributors

### Configuration
- `src/lib/config/services.config.ts` - Service definitions
- `src/lib/services/registry.ts` - Core service management logic
- `src/lib/services/types.ts` - TypeScript interfaces

### Components
- `src/app/page.tsx` - Main dashboard page
- `src/components/services/ServiceGrid.tsx` - Service display logic
- `src/components/services/ServiceCard.tsx` - Individual service cards

### API Layer
- `src/lib/proxy/ProxyHandler.ts` - Proxy request handling
- `src/app/api/health/[port]/route.ts` - Health check implementation

## Development Workflow

1. **Service Changes**: Update `services.config.ts` → Test locally → Deploy
2. **UI Changes**: Modify components → Test with `npm run test:ui` → Deploy
3. **API Changes**: Update route handlers → Test health checks → Deploy
4. **System Changes**: Update NixOS module → Test deployment script

The system is designed for **declarative management** - all configuration is code-based with no manual service administration required.