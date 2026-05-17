import os
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

def send_message(text: str):
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
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

    for job in new_jobs:
        emoji = "☁️" if any(x in job["title"].lower() for x in ["cloud", "devops", "sre", "platform", "infrastructure"]) else "💻"
        msg = (
            f"{emoji} <b>New Job Alert!</b>\n\n"
            f"🏢 <b>{job['company']}</b>\n"
            f"💼 {job['title']}\n"
            f"📍 {job['location']}\n"
            f"🔗 <a href='{job['url']}'>Apply Here</a>"
        )
        send_message(msg)

    if len(new_jobs) > 3:
        summary = f"📊 <b>{len(new_jobs)} new jobs found across your watchlist!</b>\n\n"
        companies = list({j["company"] for j in new_jobs})
        summary += "Companies: " + ", ".join(companies)
        send_message(summary)

    if len(new_jobs) > 3:
        summary = f"📊 <b>{len(new_jobs)} new jobs found across your watchlist!</b>\n\n"
        companies = list({j["company"] for j in new_jobs})
        summary += "Companies: " + ", ".join(companies)
        send_message(summary)

    # Also send a summary if more than 3 new jobs
    if len(new_jobs) > 3:
        summary = f"📊 *{len(new_jobs)} new jobs found across your watchlist!*\n\n"
        companies = list({j["company"] for j in new_jobs})
        summary += "Companies: " + ", ".join(companies)
        send_message(summary)
