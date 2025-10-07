# Repository Guidelines

## Project Structure & Module Organization
- `src/app` hosts App Router entry points and layouts; keep route folders kebab-case and add `'use client'` when a page needs browser APIs.
- UI building blocks live in `src/components`, hooks in `src/hooks`, helpers in `src/lib`, configs in `src/config`; import them via the `@/` alias. Static assets stay in `public/`.
- Automation sits in `scripts/` (see `scripts/deploy.sh`), while Playwright suites live in `tests/e2e/*.spec.ts` and emit artifacts into `playwright-report/` and `test-results/`.

## Build, Test, and Development Commands
- `npm run dev` → Next.js dev server at `http://localhost:3000`; use `.env.local` for environment overrides.
- `npm run build` (alias `npm run build:nix`) produces the production bundle; `npm start` serves the compiled app.
- `npm run lint` executes the flat ESLint stack; `npm test`, `npm run test:ui`, and `npm run test:report` cover headless runs, the inspector, and report review.
- `npm run deploy` runs tests, triggers `sudo nixos-rebuild switch`, and performs a health check—coordinate with operations before executing.

## Coding Style & Naming Conventions
- TypeScript is strict-mode; keep two-space indentation and prefer single quotes outside JSX.
- Components stay PascalCase, hooks start with `use`, utilities are camelCase, and Tailwind classes should read layout → spacing → color.
- Husky’s pre-commit hook calls `npx lint-staged`, so expect ESLint autofixes and targeted Playwright runs on staged `.ts`/`.tsx` files.

## Testing Guidelines
- Playwright loads `.env.local`; set `NEXT_PUBLIC_BASE_URL` if the default `http://localhost:3005` is not suitable.
- Keep specs focused and descriptive (`dashboard.spec.ts`, `api-health.spec.ts`); prune `test-results/` and stale reports before committing to avoid churn.
- Traces collect on first retry only; download assets if a failure needs deeper analysis.

## Commit & Pull Request Guidelines
- History currently contains the Create Next App scaffold, so establish imperative, present-tense subjects (optionally Conventional Commit prefixes such as `feat:`).
- Verify `npm run lint` and `npm test` manually before pushing to mirror the pre-commit hook.
- PRs should link issues, call out risk areas, attach UI screenshots when visuals change, and update `.env.example` plus docs when configuration shifts.

## Security & Configuration Notes
- Never commit secrets; copy `.env.example` to `.env.local` for local work and prefix browser-exposed values with `NEXT_PUBLIC_`.
- `playwright.config.ts` targets Chromium at `/run/current-system/sw/bin/chromium`; adjust when running outside the NixOS host.
