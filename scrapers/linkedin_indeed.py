#!/usr/bin/env python3
"""
LinkedIn scraper — uses LinkedIn's guest jobs API.
Indeed RSS is blocked from GitHub Actions IPs. Removed entirely.
"""
import re
import requests
from scrapers._keywords import KEYWORDS, HARD_EXCLUDE, IRELAND_TERMS, EXCLUDE_NON_IRELAND_CITIES

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IE,en;q=0.9",
}

# geoId: 90009856 = Dublin, 104738515 = Ireland
LINKEDIN_SEARCHES = [
    ("cloud engineer",              "104738515"),
    ("devops engineer",             "104738515"),
    ("software engineer",           "104738515"),
    ("junior software engineer",    "104738515"),
    ("graduate software engineer",  "104738515"),
    ("site reliability engineer",   "104738515"),
    ("backend engineer",            "104738515"),
    ("data engineer",               "104738515"),
    ("machine learning engineer",   "104738515"),
    ("platform engineer",           "104738515"),
    ("infrastructure engineer",     "104738515"),
    ("graduate developer",          "104738515"),
    ("associate software engineer", "104738515"),
    ("early careers technology",    "104738515"),
    ("graduate programme technology","104738515"),
    ("automation engineer software","104738515"),
    ("solutions engineer",          "104738515"),
    ("support engineer",            "104738515"),
]


def is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in HARD_EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)


def is_ireland(location: str) -> bool:
    loc = location.lower()
    # Reject if it's clearly a non-Ireland city
    if any(city in loc for city in EXCLUDE_NON_IRELAND_CITIES):
        return False
    return any(term in loc for term in IRELAND_TERMS)


def scrape_linkedin() -> list[dict]:
    results = []
    for keywords, geo_id in LINKEDIN_SEARCHES:
        url = (
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={requests.utils.quote(keywords)}"
            f"&location=Ireland&geoId={geo_id}"
            "&f_E=1%2C2"       # entry + associate level
            "&f_TPR=r172800"   # past 48h
            "&sortBy=DD"
            "&start=0&count=25"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            _parse_html(resp.text, results)
        except Exception as e:
            print(f"[LinkedIn] Error for '{keywords}': {e}")
    return results


def _parse_html(html: str, results: list) -> None:
    titles = re.findall(
        r'class="base-search-card__title"[^>]*>\s*(.*?)\s*</h3>', html
    )
    companies = re.findall(
        r'class="base-search-card__subtitle"[^>]*>.*?<a[^>]*>\s*(.*?)\s*</a>',
        html, re.DOTALL
    )
    locations = re.findall(
        r'class="job-search-card__location"[^>]*>\s*(.*?)\s*</span>', html
    )
    urls = re.findall(
        r'<a[^>]*class="base-card__full-link[^"]*"[^>]*href="([^"?]+)', html
    )

    count = min(len(titles), len(urls))
    for i in range(count):
        title    = titles[i].strip()
        company  = companies[i].strip() if i < len(companies) else "Unknown"
        location = locations[i].strip() if i < len(locations) else "Ireland"
        url      = urls[i].strip()

        job_id_match = re.search(r'(\d{8,})', url)
        job_id = job_id_match.group(1) if job_id_match else url

        if not is_relevant(title):
            continue
        if not is_ireland(location):
            continue

        results.append({
            "id":       job_id,
            "company":  company,
            "title":    title,
            "location": location,
            "url":      url,
            "source":   "linkedin",
        })


def scrape_all() -> list[dict]:
    print("[LinkedIn] Scraping job listings...")
    jobs = scrape_linkedin()

    seen, unique = set(), []
    for job in jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique.append(job)

    print(f"  Found {len(unique)} unique jobs from LinkedIn")
    return unique
