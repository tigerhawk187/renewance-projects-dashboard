# Renewance Active Projects Dashboard

Live snapshot of active projects with status, labor and materials burn, recent
daily-report narrative, and critical items. Data comes from Lift (Quickbase).
Refreshes automatically on a weekday 4am Central cron via GitHub Actions, with
no dependency on any laptop being awake.

## How it works

1. `.github/workflows/refresh.yml` runs weekdays at 09:00 UTC (4am CDT / 5am CST)
   and can also be triggered manually from the Actions tab.
2. It runs `qb_pull.py`, which reads the `QB_USER_TOKEN` secret, pulls active
   projects, expenses, and recent daily reports from the Lift Quickbase app,
   computes burn and critical items, and writes `data/projects.js`.
3. `index.html` loads `data/projects.js` (`window.DASHBOARD`) and renders the
   board client-side. No server, no build step.

## Setup

- Secret required: `QB_USER_TOKEN` (Settings, Secrets and variables, Actions).
  A Quickbase user token with app-wide read on the Renewance Lift app.
- Optional secret: `QB_REALM` (defaults to `lift.quickbase.com`).

## Publishing the link

This repo is private. Two free options for a shareable page:

- Public repo, then Settings, Pages, Deploy from branch `main` (root). Free, but
  the page and data are public. Only choose this if the content is not sensitive.
- Keep private and connect Cloudflare Pages to the repo, gated with Cloudflare
  Access (free up to 50 users). Keeps contract values and complaints private.

## Budget note

Labor hours and expense dollars are actuals from Lift and are trustworthy.
Budget targets (labor-hours plan, materials budget) are not stored in Lift;
they are extracted separately from the Commercial cost models and agreements in
SharePoint and committed as `data/agreements.js`. Until that lands, the burn
bars for discrete jobs use scheduled hours as a provisional baseline and Ongoing
O&M shows actuals only.

## Files

- `qb_pull.py` - the data pull (standard library only)
- `index.html` - the dashboard
- `data/projects.js` - generated data (committed each run)
- `.github/workflows/refresh.yml` - the 4am job
