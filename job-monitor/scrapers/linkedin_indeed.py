import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

LEVEL_KEYWORDS = ["graduate", "junior", "intern", "entry", "associate", "apprentice"]
TECH_KEYWORDS  = ["cloud", "devops", "sre", "software", "engineer", "developer",
                  "platform", "backend", "fullstack", "infrastructure"]
EXCLUDE        = ["senior", "staff", "principal", "director", "manager",
                  "lead ", "vp ", "head of", "sr."]

def is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in EXCLUDE):
        return False
    return any(x in t for x in LEVEL_KEYWORDS) or any(x in t for x in TECH_KEYWORDS)

def is_recent(pub_date: str, hours=2) -> bool:
    if not pub_date:
        return True
    try:
        posted = parsedate_to_datetime(pub_date)
        age_hours = (datetime.now(timezone.utc) - posted).total_seconds() / 3600
        return age_hours <= hours
    except Exception:
        return True

INDEED_RSS_FEEDS = [
    "https://ie.indeed.com/rss?q=cloud+engineer&l=Dublin&sort=date",
    "https://ie.indeed.com/rss?q=junior+software+engineer&l=Dublin&sort=date",
    "https://ie.indeed.com/rss?q=graduate+software+engineer&l=Dublin&sort=date",
    "https://ie.indeed.com/rss?q=devops+engineer&l=Dublin&sort=date",
    "https://ie.indeed.com/rss?q=software+engineer+intern&l=Dublin&sort=date",
]

LINKEDIN_RSS_FEEDS = [
    "https://www.linkedin.com/jobs/search/?keywords=cloud+engineer&location=Dublin&f_TPR=r3600&f_E=1%2C2&format=rss",
    "https://www.linkedin.com/jobs/search/?keywords=junior+software+engineer&location=Dublin&f_TPR=r3600&format=rss",
    "https://www.linkedin.com/jobs/search/?keywords=graduate+engineer&location=Dublin&f_TPR=r3600&format=rss",
]

def parse_rss(url: str, source: str) -> list[dict]:
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if channel is None:
            return []
        for item in channel.findall("item"):
            title    = item.findtext("title", "").strip()
            link     = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            company  = item.findtext("source", "Unknown").strip()

            if not is_relevant(title):
                continue
            if not is_recent(pub_date, hours=2):
                continue

            results.append({
                "id":       link,
                "company":  company or "Via " + source.title(),
                "title":    title,
                "location": "Dublin, Ireland",
                "url":      link,
                "source":   source,
            })
    except Exception as e:
        print(f"[{source.upper()}] RSS error for {url}: {e}")
    return results

def scrape_all() -> list[dict]:
    all_jobs = []

    print("[Indeed] Scraping RSS feeds...")
    for url in INDEED_RSS_FEEDS:
        jobs = parse_rss(url, "indeed")
        print(f"  Found {len(jobs)} relevant jobs")
        all_jobs.extend(jobs)

    print("[LinkedIn] Scraping RSS feeds...")
    for url in LINKEDIN_RSS_FEEDS:
        jobs = parse_rss(url, "linkedin")
        print(f"  Found {len(jobs)} relevant jobs")
        all_jobs.extend(jobs)

    # Deduplicate
    seen, unique = set(), []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique.append(job)

    return unique
