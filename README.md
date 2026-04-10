# CHAN-C

Labor marketplace for Guatemala's informal construction workforce. SMS and WhatsApp first — no smartphone required for workers.

## Stack

- **Backend:** FastAPI + PostgreSQL (Supabase)
- **Frontend:** Next.js + TypeScript (in progress)
- **Mobile:** Flutter (planned)
- **SMS + WhatsApp:** Twilio
- **AI Voice:** Vapi + ElevenLabs
- **Data Extraction:** Claude API
- **Hosting:** Railway + Vercel

## Structure

```
backend/   — FastAPI app, models, services, API routes
frontend/  — Next.js web app (in progress)
docs/      — Architecture and runbooks
```

## Setup

1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill values
6. `alembic upgrade head`
7. `python scripts/create_admin.py email password`
8. `uvicorn app.main:app --reload --port 8001`

## API Docs

http://localhost:8001/docs

## Environment Variables

See `backend/.env.example` for all required variables.

## Roadmap

- WhatsApp chatbot channel (built, pending Twilio config)
- Automated scheduler for AI pipeline
- Flutter mobile app for companies
- AI voice in K'iche' and Mam
- Multi-city expansion beyond Guatemala City
- B2C homeowner flow

## Note

Private repository. Do not share or distribute.
