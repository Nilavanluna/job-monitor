# 🎯 Dublin Job Monitor

Monitors 50 major Dublin tech companies for new entry-level Cloud & SDE roles.
Runs every 15 minutes via GitHub Actions. Sends instant Telegram alerts.

## How it works

```
GitHub Actions (cron every 15 min)
    → Greenhouse API  (38 companies, no scraping)
    → Lever API       (Notion etc.)
    → Workday API     (Microsoft, Visa, PayPal etc.)
    → Playwright      (Google, Amazon, Apple, Oracle etc.)
         ↓
    Diff against state.json
         ↓ new jobs found
    Telegram Bot → your phone 📱
         ↓
    Commit updated state.json back to repo
```

## Setup (15 minutes)

### 1. Create a Telegram Bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot` → follow prompts → copy the **Bot Token**
3. Start a chat with your new bot
4. Get your **Chat ID**: visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   after sending a message to the bot — look for `"chat":{"id":XXXXXXX}`

### 2. Fork / create this repo on GitHub

```bash
git init job-monitor
cd job-monitor
# copy all files here
git add .
git commit -m "init"
git remote add origin https://github.com/YOUR_USERNAME/job-monitor.git
git push -u origin main
```

### 3. Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret name          | Value                        |
|----------------------|------------------------------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHAT_ID`   | Your numeric chat ID          |

### 4. Enable GitHub Actions

Go to the **Actions** tab in your repo → click **Enable Actions**

### 5. Test it manually

Actions tab → **Job Monitor** → **Run workflow** → watch the logs

If new jobs exist, you'll get a Telegram message within seconds. 🎉

---

## Customise

### Add more companies

**Greenhouse** — find the company slug from their jobs URL:
`https://boards.greenhouse.io/SLUG` → add to `companies.yml`

**Lever** — find slug from `https://jobs.lever.co/SLUG`

**Workday** — add the `api_url` pattern from their careers site

### Change the keyword filters

Edit `KEYWORDS` and `EXCLUDE` lists in any scraper file.

### Change run frequency

Edit the cron in `.github/workflows/monitor.yml`:
- Every 15 min: `*/15 * * * *`
- Every 30 min: `*/30 * * * *`
- Every hour:   `0 * * * *`

> ⚠️ GitHub Actions free tier = 2,000 min/month.
> At 15 min intervals: ~2,880 runs/month × ~2 min each = ~5,760 min.
> **Recommendation: use 30 min intervals** to stay within free limits comfortably.

---

## File structure

```
job-monitor/
├── .github/
│   └── workflows/
│       └── monitor.yml        # GitHub Actions cron
├── scrapers/
│   ├── greenhouse.py          # Greenhouse API
│   ├── lever.py               # Lever API
│   ├── workday.py             # Workday + Microsoft APIs
│   └── playwright_scraper.py  # Custom career pages
├── companies.yml              # All 50 companies config
├── diff_engine.py             # New job detection
├── notifier.py                # Telegram alerts
├── main.py                    # Orchestrator
├── state.json                 # Job cache (auto-updated by Actions)
├── requirements.txt
└── README.md
```
