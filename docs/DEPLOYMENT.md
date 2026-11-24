# Deployment and production configuration

## Frontend: GitHub Pages through GitHub Actions
Repository: https://github.com/NAGESWAR-BELLAMKONDA/HealthTrendAI

The deployment workflow is `.github/workflows/deploy-pages.yml`. It builds the Vite frontend and publishes the `dist` artifact using the official Pages deployment actions. The public Supabase project URL and publishable key are supplied as Vite build-time variables; these are browser credentials designed to be public and are protected by database RLS.

One repository-owner action is still required:
1. Open **Settings → Pages** in the repository.
2. Under **Build and deployment**, select **GitHub Actions** as the source.
3. Save.
4. Open **Actions → Deploy HealthTrend AI to GitHub Pages → Run workflow** and run it on `main`.
5. Wait for the deployment environment URL to appear.

Expected Pages base URL:
`https://nageswar-bellamkonda.github.io/HealthTrendAI/`

The Pages deployment cannot be enabled by the repository contents workflow; it is a repository setting controlled by the owner. A recent build succeeded but deployment returned HTTP 404 with GitHub's explicit message to enable Pages. Verify that Settings → Pages is saved with Source = GitHub Actions, then rerun the deployment workflow.

## Supabase Auth
Project API URL: `https://ugitalbazfmeqwuscizq.supabase.co`

In Supabase Dashboard:
1. Open **Authentication → URL Configuration**.
2. Set Site URL to `https://nageswar-bellamkonda.github.io/HealthTrendAI/`.
3. Add the exact Pages URL above to the Redirect URLs allow-list.
4. Open **Authentication → Providers → Email** and enable email confirmations.
5. For production email delivery, configure a custom SMTP provider under **Authentication → SMTP Settings**. Supabase's built-in email service is rate-limited and is intended for testing.
6. Test sign-up, inbox verification, sign-in, password reset and sign-out.

The frontend constructs the redirect from Vite's base path so verification returns to the repository subpath. Local development uses the Vite origin.

## Initial administrator
New sign-ups receive the least-privilege `viewer` role. The first administrator must be assigned deliberately by the owner in the Supabase SQL Editor after that person has registered and verified their email.

Run this query after replacing the email with the intended administrator's exact verified address:

```sql
update public.app_user_roles r
set role = 'admin'
from auth.users u
where r.user_id = u.id
  and lower(u.email) = lower('YOUR_VERIFIED_ADMIN_EMAIL');
```

Confirm exactly one row was updated. Do not make public sign-ups administrators. After the first administrator is assigned, role changes are available in the app's **User Access** page and are enforced by RLS.

## GitHub Actions data-pipeline secrets
Open **Settings → Secrets and variables → Actions → New repository secret** and add:
- `SUPABASE_URL` = the Supabase project URL.
- `SUPABASE_SERVICE_ROLE_KEY` = the server-side service-role key from the intended Supabase project.

The service-role key bypasses RLS. It is used only by the scheduled GitHub Actions runner, never in Vite, browser code, repository files or public build artifacts. Never paste it into ChatGPT or commit it.

The workflow `.github/workflows/monthly-data-pipeline.yml` runs monthly and supports manual dispatch. It downloads the registered official MMIS PDFs, validates the monthly rows, upserts warehouse facts, and stores descriptive mining/anomaly/clustering results. It does not manufacture admissions records.

## Realtime and source cadence
Supabase Realtime pushes committed database changes to signed-in browsers. This makes the application database-synchronous; it does not make external government datasets live. The monthly ETL schedule revalidates and re-ingests the currently registered MMIS reports. It does not automatically ingest every newly published report: a new report must first be added to the validated source registry/parser, especially when the publisher changes the report layout or only publishes chart approximations.

## CI
`.github/workflows/ci.yml` checks TypeScript, builds the frontend and runs Python tests on each push/PR. CI runs TypeScript type-checking, a production frontend build and Python tests on each push/PR. Check the latest workflow run in the Actions tab before each release.
