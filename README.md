# HealthTrend AI
Comparative Analysis of Machine Learning and Time-Series Models for Disease Trend Mining and Hospital Admission Forecasting.

Modules: data warehousing and preprocessing; disease trend mining with Decision Tree, Random Forest and XGBoost; forecasting with ARIMA, SARIMA and Prophet.

Stack: React + TypeScript + Vite, Supabase PostgreSQL, Python modelling pipeline, GitHub Actions.

Research integrity: the presentation's demo metrics are illustrative only. They are not experimental findings. Metrics must be computed from actual chronological holdout predictions. Use aggregate public data only; this is not a clinical diagnosis system.

Setup: copy .env.example to .env.local and set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY. Never expose a service-role key in browser code. Run npm install and npm run dev.

See docs/METHODOLOGY.md and docs/DATA_SOURCES.md.