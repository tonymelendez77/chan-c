# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important: Next.js Version

This project uses **Next.js 16** with **React 19**. APIs and conventions may differ from training data. Always read `node_modules/next/dist/docs/` before writing new Next.js code. Heed deprecation notices.

## Commands

```bash
npm run dev      # Start dev server
npm run build    # Production build
npm run lint     # ESLint (flat config, no --fix script)
npm run start    # Start production server
```

No test framework is currently configured.

## Architecture

### Route Groups (App Router)

- `(auth)/` — Login and registration pages (public)
- `(dashboard)/` — Company-facing portal (authenticated, role: company). Uses `Header` + `Sidebar` layout components.
- `(admin)/` — Admin ops dashboard for Cece and Josue (authenticated, role: admin). Self-contained layout with fixed sidebar nav and "manual mode" toggle that pauses the AI pipeline.
- `/` root `page.tsx` — Public landing page

### Auth

Client-side JWT auth via `localStorage` (`chanc_token`). No server-side session or middleware.

- `src/lib/auth.ts` — Token CRUD + JWT decode helpers (`isAuthenticated`, `getCurrentUser`)
- Route protection is done via `useEffect` redirects in each layout, not middleware

### API Layer

- `src/lib/api.ts` — Axios instance pointing to `NEXT_PUBLIC_API_URL` (default `localhost:8001`). Auto-attaches Bearer token; 401s clear token and redirect to `/login`.
- `src/lib/admin-api.ts` — All admin API calls (dashboard stats, matches, workers, jobs, recruitment, AI pipeline, SMS)
- `src/lib/types.ts` — Shared TypeScript types/enums mirroring the FastAPI backend. Includes Spanish display labels (`TRADE_LABELS`, `SKILL_LABELS`).

### Styling

- **Tailwind CSS v4** with `@tailwindcss/postcss`
- Admin dashboard uses CSS custom properties (`--admin-*`) for theming
- Fonts: DM Sans (body), Syne (headings), JetBrains Mono (mono) — loaded via Google Fonts in root layout

### i18n

`next-intl` with `src/i18n/es.json` (Spanish, primary) and `en.json`. Default language is Spanish (`lang="es"` on `<html>`).

### Key Conventions

- Path alias: `@/*` maps to `./src/*`
- Forms: `react-hook-form` + `zod` for validation
- Icons: `lucide-react`
- Currency: Guatemalan Quetzal (Q), formatted via `formatCurrency()` in `utils.ts`
- Dates: `es-GT` locale formatting via `formatDate()` in `utils.ts`
- All user-facing text is in Spanish
