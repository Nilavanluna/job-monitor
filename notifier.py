import os
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

def send_message(text: str):
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[Telegram] Failed to send message: {e}")

def notify_new_jobs(new_jobs: list[dict]):
    if not new_jobs:
        return

    # Send one message per job (Telegram looks clean this way)
    for job in new_jobs:
        emoji = "☁️" if any(x in job["title"].lower() for x in ["cloud", "devops", "sre", "platform", "infrastructure"]) else "💻"
        msg = (
            f"{emoji} *New Job Alert!*\n\n"
            f"🏢 *{job['company']}*\n"
            f"💼 {job['title']}\n"
            f"📍 {job['location']}\n"
            f"🔗 [Apply Here]({job['url']})"
        )
        send_message(msg)

    # Also send a summary if more than 3 new jobs
    if len(new_jobs) > 3:
        summary = f"📊 *{len(new_jobs)} new jobs found across your watchlist!*\n\n"
        companies = list({j["company"] for j in new_jobs})
        summary += "Companies: " + ", ".join(companies)
        send_message(summary)
