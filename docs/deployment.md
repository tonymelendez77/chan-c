# CHAN-C Deployment Guide

## Architecture

- **Backend:** FastAPI on Railway
- **Frontend:** Next.js on Vercel
- **Database:** PostgreSQL on Supabase
- **SMS/WhatsApp:** Twilio
- **AI Voice:** Vapi
- **Data Extraction:** Claude API (Anthropic)

## Backend — Railway

### Environment Variables

Set these in Railway dashboard → your service → Variables:

```
DATABASE_URL=postgresql+asyncpg://postgres:<password>@db.<project>.supabase.co:5432/postgres
SYNC_DATABASE_URL=postgresql+psycopg://postgres:<password>@db.<project>.supabase.co:5432/postgres
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
ENVIRONMENT=production
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
VAPI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VAPI_PHONE_NUMBER_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CONFIDENCE_THRESHOLD=0.7
```

### Deploy

1. Connect Railway to GitHub repo `tonymelendez77/chan-c`
2. Set root directory to `backend`
3. Railway auto-detects Python via `runtime.txt` and `requirements.txt`
4. Start command is in `Procfile`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Health check: `/health`

### Run Migration

In Railway dashboard → your service → Settings → Deploy:

Temporarily set start command to:
```
alembic upgrade head
```
Wait for it to run, then revert to:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Create Admin Users

Run locally pointing to production database:
```bash
cd backend
source venv/Scripts/activate  # or venv/bin/activate on Mac/Linux
SYNC_DATABASE_URL="postgresql+psycopg://postgres:<password>@db.<project>.supabase.co:5432/postgres" python scripts/create_admin.py cece@chanc.gt <password>
SYNC_DATABASE_URL="postgresql+psycopg://postgres:<password>@db.<project>.supabase.co:5432/postgres" python scripts/create_admin.py josue@chanc.gt <password>
```

## Frontend — Vercel

### Environment Variables

Set these in Vercel dashboard → your project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://<your-app>.railway.app
NEXT_PUBLIC_APP_NAME=CHAN-C
```

### Deploy

1. Import GitHub repo `tonymelendez77/chan-c` to Vercel
2. Set root directory to `frontend`
3. Framework preset: Next.js (auto-detected)
4. Build command: `npm run build`
5. Output directory: `.next`

## Twilio Webhook URLs

After Railway deploys and you have the URL, set these in Twilio console:

**SMS Incoming:**
```
https://<your-app>.railway.app/api/sms/incoming
```

**WhatsApp Incoming:**
```
https://<your-app>.railway.app/api/whatsapp/incoming
```

Method: POST for both.

## Post-Deployment Checklist

- [ ] Railway service running (check `/health`)
- [ ] Alembic migration completed (16 tables)
- [ ] Admin users created (cece@chanc.gt, josue@chanc.gt)
- [ ] Vercel deployment live
- [ ] Frontend can reach backend API (check network tab)
- [ ] Twilio webhooks configured
- [ ] Test SMS: send "TRABAJAR" to Twilio number
- [ ] Test login: admin credentials on /login
- [ ] Test dashboard: /admin loads with stats

## Monitoring

- **Railway:** Built-in logs and metrics
- **Vercel:** Analytics and logs in dashboard
- **Supabase:** Database metrics and logs
- **Health check:** GET `https://<your-app>.railway.app/health`

## Rollback

Both Railway and Vercel support instant rollback to previous deployments via their dashboards.
