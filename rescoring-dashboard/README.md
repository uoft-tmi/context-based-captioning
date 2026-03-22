# Rescoring Monitoring Dashboard

A production-grade Next.js application designed to provide visibility, auditing, and continuous improvement tools for autonomous human speech transcript modifications.

## Deployment on Vercel

This application is fully optimized and ready to deploy on Vercel with a connected PosgreSQL database.

### 1. Database Setup
1. Create a Vercel Postgres, Neon.tech, or Supabase PostgreSQL database.
2. In your Vercel project settings, add the connection string to the `DATABASE_URL` environment variable.

### 2. Deployment
1. Push this repository to GitHub.
2. Import the repository in Vercel.
3. The framework preset should automatically detect Next.js.
4. Set the Root Directory to `rescoring-dashboard` if you are deploying from a monorepo.
5. In the Build Command, ensure it runs: `prisma generate && next build` (Configured in `vercel.json`).
6. Deploy!

### 3. Database Migration
Since Vercel Edge functions cannot run full Prisma migrations securely on build, you must push the schema manually to your production database:
```bash
npx prisma db push
```

### 4. Connecting the Python Rescorer
Update your Python ingestion scripts to pass the deployed Next.js URL.
```bash
export DASHBOARD_API_URL="https://your-vercel-domain.vercel.app"
python rescoring_system.py
```
The python `DashboardLogger` will automatically batch and sync decisions via HTTP POST requests to `/api/decisions`.

## Local Development
*(Note: Requires Node.js and a local Postgres or SQLite config)*
1. `npm install`
2. Configure `.env.example` -> `.env`
3. `npx prisma db push`
4. `npm run dev`
