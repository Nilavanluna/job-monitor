#!/usr/bin/env python3
"""
LinkedIn scraper — uses LinkedIn's guest jobs API.

Indeed RSS is blocked from GitHub Actions IPs (403). Removed entirely.
LinkedIn guest API works fine without auth.
"""
import re
import requests

# Set True to get all Ireland, False for Dublin/remote only
IRELAND_ONLY = False

LEVEL_KEYWORDS = [
    "graduate", "junior", "intern", "entry level", "entry-level",
    "associate", "apprentice", "trainee", "new grad", "early career",
]

TECH_KEYWORDS = [
    "cloud", "devops", "sre", "site reliability", "software engineer",
    "software developer", "backend", "fullstack", "full stack",
    "full-stack", "platform engineer", "infrastructure engineer",
    "data engineer", "ml engineer", "machine learning engineer",
    "ai engineer", "security engineer", "network engineer",
]

HARD_EXCLUDE = [
    "senior", "staff", "principal", "director", "manager",
    "lead ", " lead", "vp ", "head of", "sr.", "sr ",
    "architect", "consultant", "civil engineer", "structural engineer",
    "mechanical engineer", "electrical engineer", "chemical engineer",
    "process engineer", "validation engineer", "construction",
    "site engineer", "field engineer", "power engineer",
    "hvac", "bms", "building management", "building services",
    "graduate power", "graduate electrical", "graduate civil",
    "graduate structural", "graduate mechanical", "graduate construction",
    "graduate i &", "graduate i&c", "analog", "layout engineer",
    "service operations", "power apps",
]

DUBLIN_TERMS = ["dublin", "remote", "ireland"]
EXCLUDE_LOCATIONS = ["cork", "galway", "limerick", "waterford", "kilkenny",
                     "sligo", "drogheda", "kildare", "wexford", "wicklow"]

LINKEDIN_SEARCHES = [
    ("cloud engineer",             "90009856"),
    ("devops engineer",            "90009856"),
    ("software engineer",          "90009856"),
    ("junior software engineer",   "104738515"),
    ("graduate software engineer", "104738515"),
    ("site reliability engineer",  "104738515"),
    ("backend engineer",           "90009856"),
    ("data engineer",              "90009856"),
    ("machine learning engineer",  "90009856"),
    ("platform engineer",          "90009856"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IE,en;q=0.9",
}


def is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in HARD_EXCLUDE):
        return False
    return any(x in t for x in TECH_KEYWORDS)


def is_target_location(location: str) -> bool:
    loc = location.lower()
    if IRELAND_ONLY:
        return "ireland" in loc or "ie)" in loc
    if any(city in loc for city in EXCLUDE_LOCATIONS):
        return False
    return any(term in loc for term in DUBLIN_TERMS)


def scrape_linkedin() -> list[dict]:
    results = []
    for keywords, geo_id in LINKEDIN_SEARCHES:
        url = (
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={requests.utils.quote(keywords)}"
            f"&location=Ireland&geoId={geo_id}"
            "&f_E=1%2C2"
            "&f_TPR=r172800"
            "&sortBy=DD"
            "&start=0&count=25"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            _parse_linkedin_html(resp.text, results)
        except Exception as e:
            print(f"[LinkedIn] Error for '{keywords}': {e}")
    return results


def _parse_linkedin_html(html: str, results: list) -> None:
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
        if not is_target_location(location):
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
