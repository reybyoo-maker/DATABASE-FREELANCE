# DATABASE-FREELANCE — Company Prospect Harvester

Automated, multilingual B2B prospect discovery for public business profiles. Runs on GitHub Actions, screens for a public WhatsApp contact or social-media profile, deduplicates records, creates copy-ready company need audits, and writes outreach drafts into Google Sheets.

## What it does

- Runs on a schedule (four times daily) and can be started manually from Actions.
- Finds public company/business listings via Tavily Search (when configured) and OpenStreetMap's read-only Overpass service.
- Only exports qualified records with a public WhatsApp contact or at least one social profile URL; a generic phone number alone is not treated as proof of WhatsApp.
- Captures country and city, sector, evidence/source links, public contact channels, and the date discovered.
- Uses Gemini to draft an evidence-based need audit, a 0–100 prospect score, the tier RECOMMENDED / MEDIUM / LOW, and copy/paste outreach in the likely language of the business's country.
- Sends rows to the user's Google Sheet through a Google Apps Script web app. Dedupe is done by stable prospect ID.
- Targets 100 new qualified records per Jakarta calendar day and makes repeated runs to close the gap. Public source coverage, quotas, API availability, and duplicate rates mean 100 is a target, not a guarantee; logs and the sheet show if the target was missed.

## Required GitHub Actions secrets

Go to Settings → Secrets and variables → Actions → New repository secret and create:

| Secret | Value |
|---|---|
| TAVILY_API_KEY | Tavily Search API key (needed for broader web discovery) |
| GEMINI_API_KEY | Google Gemini API key for company-need analysis and localized outreach |
| SHEET_WEBHOOK_URL | Deployed Google Apps Script Web App URL ending in /exec |
| WEBHOOK_TOKEN | Long random shared secret; must match Apps Script property WEBHOOK_TOKEN |

Optional repository variable:
- GEMINI_MODEL: model ID to use (default gemini-3.5-flash-lite; set it to a currently enabled model in your AI Studio project).
- DAILY_TARGET: desired qualified new records per Jakarta day (default 100).

Never put API keys in source code or commit them. The workflow does not send outreach messages; it only prepares drafts for manual review.

## Connect Google Sheets

1. Create a Google Sheet.
2. Open Extensions → Apps Script.
3. Replace the editor contents with apps-script/Code.gs, save.
4. In Apps Script Project Settings → Script Properties, add WEBHOOK_TOKEN with the exact same value as the GitHub secret.
5. Choose Deploy → New deployment → Web app. Execute as Me; set access to Anyone (the shared token protects the endpoint). Deploy and copy its /exec URL to SHEET_WEBHOOK_URL.
6. Add the four GitHub Actions secrets above. Then go to Actions → DATABASE-FREELANCE Daily Prospect Discovery → Run workflow.

The sheet script creates a Prospects tab and a Runs tab automatically. The Outreach Status column is manual; records are not messaged automatically.

## Website-matched outreach

Outreach is matched to a relevant example on the agency portfolio at https://agencyai.reybyoo.workers.dev/. The selected example may include B2B lead discovery, customer chat/FAQ automation, Instagram DM replies, content planning, email campaign preparation, restaurant reservations, sales reporting, competitor monitoring, payment reminders, or daily reports.

Each copy-ready DM, WhatsApp message, and email body includes:
- A sender introduction using the placeholder `[nama kamu]` from **AGA-Ai Growth Agency**.
- The main portfolio link and a sector-relevant project example link.
- A short, respectful pitch about a possible fit, written in the prospect's language when AI analysis is available.
- No claims that illustrative portfolio pages are real client case studies or proven results.

The `Prospects` tab also records `Portfolio Service Match` and `Relevant Portfolio Example URL`. If the Google Apps Script was already copied to Google from an earlier version, update it with the latest `apps-script/Code.gs` and deploy a new version for the new columns to appear. Updating the file in GitHub alone does not automatically update a separately deployed Apps Script.

## Scoring rubric

- RECOMMENDED: 75–100 — clear, evidence-supported opportunity plus usable public contact.
- MEDIUM: 45–74 — plausible fit but limited evidence or weaker opportunity signals.
- LOW: 0–44 — weak or uncertain fit; keep for later review.

The model must distinguish observed evidence from hypotheses. It must not invent company needs, contact details, budget, or buying intent. Review every draft before contacting the business.

## Sources & responsible use

This is not an unrestricted scraper and cannot access “all sources in the world.” It queries public search results and public OpenStreetMap data, respects request timeouts/rate limits, and does not bypass logins, CAPTCHAs, paywalls, robots barriers, or platform restrictions. Keep source URLs in the sheet, honor each provider's terms and local privacy/marketing laws, and stop outreach on request. Public listings can be stale; verify before use.

OpenStreetMap data is © OpenStreetMap contributors and is used under the Open Database License (ODbL). See https://www.openstreetmap.org/copyright. Tavily and Gemini usage is subject to their respective terms, plans, and quotas.

## Local check

Use Python 3.11 or newer. Install dependencies using: pip install -r requirements.txt
Copy .env.example to .env and set secrets as environment variables.
Run a no-write test with: python src/runner.py --dry-run
