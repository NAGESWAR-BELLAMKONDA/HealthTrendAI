# Deployment

The frontend build is already verified by GitHub Actions. The Pages artifact also builds successfully. The deployment action currently returns HTTP 404 because GitHub Pages has not yet been enabled for this repository.

## Enable GitHub Pages once
1. Open the repository: https://github.com/NAGESWAR-BELLAMKONDA/HealthTrendAI
2. Go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Save.

## Deploy
1. Open the **Actions** tab.
2. Select **Deploy HealthTrend AI to GitHub Pages**.
3. Select **Run workflow** on the main branch.
4. After the run succeeds, open the github-pages deployment environment URL shown by GitHub.

The workflow is manual until Pages is enabled, avoiding failed deployments on every normal code commit.
