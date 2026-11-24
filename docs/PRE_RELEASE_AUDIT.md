# HealthTrend AI — pre-release technical audit

Audit date: 24 November 2026  
Repository: https://github.com/NAGESWAR-BELLAMKONDA/HealthTrendAI  
Production URL: https://nageswar-bellamkonda.github.io/HealthTrendAI/

## Verified and corrected

- Supabase disease fact table was audited after detecting duplicated January–September 2023 rows.
- Exact duplicate rows were removed. The table now contains 31 rows across 31 distinct months, with no duplicate (date, location, disease, source) combinations.
- A database uniqueness constraint now prevents the same source/month fact from being inserted twice under a different source-record label.
- The MMIS ingestion script now uses the same natural key for upserts, so repeat ingestion is idempotent.
- Authenticated browser grants were reduced to the read/update operations required by the app. Anonymous table grants and anonymous RLS policies are absent. Server-side ETL retains service-role access.
- Mining results now use a stable unique key and upsert instead of insert, preventing duplicate history rows on repeated pipeline runs.
- CI checks passed before the final idempotency changes; the latest CI run is validating those changes.
- GitHub Pages deployment completed successfully for commit 7916ebd3e7aefca60c87e43a356668a6b06b026e (the duplicate-data correction release).

## Current verified data

| Measure | Current state |
|---|---:|
| Exact national malaria observations | 31 |
| Distinct monthly dates | 31 |
| Date range | Jan 2023–Oct 2025 |
| Duplicate fact combinations | 0 |
| Estimated rows | 0 |
| Hospital admission observations | 0 |
| Model runs | 0 |
| Forecast points | 0 |
| Persisted mining analyses | 2 |

The malaria series has a three-month gap in 2023 (October–December). It is national surveillance data, not hospital admissions, district-level data, or a real-time feed. Model comparison remains intentionally blocked until at least 36 contiguous monthly observations are available. No values are interpolated.

## Open release gates

1. **Owner/admin provisioning:** one account exists with the default viewer role. Confirm the account is the intended owner and email verification is complete, then promote it to admin. Do not grant admin to an unverified or unintended account.
2. **Auth security setting:** Supabase Security Advisor currently warns that leaked-password protection is disabled. Enable it in Supabase Authentication password/security settings.
3. **Email delivery:** configure custom SMTP and test signup verification and password reset using a normal Gmail inbox. Supabase's default mailer is not production email delivery.
4. **ETL credentials and execution:** add/verify repository Actions secrets `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`, then manually run the monthly pipeline and inspect its logs. Never put the service-role key in Vite or commit it.
5. **ETL observability:** the current monthly workflow does not write a start/success/failure row to `etl_logs`. Add structured pipeline logging and failure reporting before production operations.
6. **Live authentication QA:** test sign-up, verification, sign-in, sign-out, reset, viewer access, analyst/researcher access and admin role changes in a browser with separate test accounts.
7. **Production smoke test:** verify the deployed app in desktop and mobile browsers, including page refresh/deep-link behavior, charts, empty states, loading/error states and realtime updates.
8. **Source refresh:** the scheduled pipeline currently downloads a fixed report set ending October 2025; it does not discover new MMIS reports automatically. Update the source discovery process before claiming current monthly data.
9. **Data completeness:** obtain a validated monthly HMIS M14 inpatient-admissions series before claiming hospital admission forecasting is operational.

## CI and deployment

- Frontend: TypeScript typecheck and Vite production build.
- Backend: Python pytest suite.
- Pages: GitHub Actions deployment workflow.
- Latest CI run for mining idempotency change: https://github.com/NAGESWAR-BELLAMKONDA/HealthTrendAI/actions/runs/45332970235
- Earlier successful deployment for duplicate-data correction: https://github.com/NAGESWAR-BELLAMKONDA/HealthTrendAI/actions/runs/45331862970

## Release decision

**Not approved for an unconditional production/client handover yet.** The web build and Pages deployment work, duplicate data is corrected, and database browser permissions have been tightened. The remaining gates above require owner action, live-user testing, a verified ETL run, and more complete source data. The product must be described as an aggregate public-health research and data-mining application, not a clinical decision-support system.
