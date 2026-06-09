import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER         = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

def send_email(subject: str, body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = GMAIL_USER

    text_part = MIMEText(body, "plain")
    html_body = body.replace("\n", "<br>")
    html_part = MIMEText(f"<pre style='font-family:sans-serif'>{html_body}</pre>", "html")

    msg.attach(text_part)
    msg.attach(html_part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        print(f"[Gmail] Email sent: {subject}")
    except Exception as e:
        print(f"[Gmail] Failed to send email: {e}")


def notify_new_jobs(new_jobs: list[dict]):
    if not new_jobs:
        return

    by_company: dict[str, list] = {}
    for job in new_jobs:
        by_company.setdefault(job["company"], []).append(job)

    subject = f"[Job Monitor] {len(new_jobs)} new job(s) in Dublin - {', '.join(by_company.keys())}"

    lines = ["New Dublin Jobs Found!", "=" * 50, ""]
    for company, jobs in by_company.items():
        lines.append(f"--- {company} ({len(jobs)} role(s)) ---")
        for job in jobs:
            lines.append(f"  Role:     {job['title']}")
            lines.append(f"  Location: {job['location']}")
            lines.append(f"  Source:   {job.get('source','').upper()}")
            lines.append(f"  Link:     {job['url']}")
            lines.append("")
        lines.append("")

    body = "\n".join(lines)
    send_email(subject, body)
