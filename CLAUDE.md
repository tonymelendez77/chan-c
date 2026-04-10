# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

CHAN-C is a skilled trades marketplace for Guatemala's informal labor market. It connects construction firms and home service businesses with pre-vetted workers (plumbers, electricians, carpenters, cleaners) who interact entirely via SMS/WhatsApp (no smartphone required).

## Tech Stack

- **Backend:** FastAPI (Python), hosted on Railway
- **Database:** PostgreSQL on Supabase
- **Frontend:** Next.js + TypeScript, hosted on Vercel
- **Mobile:** Flutter
- **SMS/WhatsApp:** Twilio
- **AI Voice (Phase 2):** Vapi + ElevenLabs

## Users

- **Companies** — construction firms, home service businesses. Post jobs, accept/reject matches via web app.
- **Workers** — no smartphones. All interaction via SMS/WhatsApp only.
- **Admins** (Cece + Josue) — manually vet workers, manage matches, ops dashboard.

## Core Flow

1. Company posts a job with requirements
2. Platform matches to pre-vetted workers
3. Worker gets SMS/WhatsApp notification
4. Worker replies YES/NO
5. If YES, company gets worker contact info (one at a time, never as a list)
6. Post-job, worker gets SMS rating request (YES/NO)

Phase 1 is fully manual — founders do all vetting and matching via the admin dashboard.
