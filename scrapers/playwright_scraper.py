#!/usr/bin/env python3
"""
IrishJobs.ie scraper via Playwright — multi-keyword search.

Jobs.ie removed: it now redirects through TotalJobs/StepStone's broken
search flow that throws JS errors and never renders results client-side.
Confirmed via console trace showing 'ReferenceError: s is not defined'
in their search page script — not a selector problem, the search itself
fails. IrishJobs.ie is a separate, working property and is kept.
"""
from playwright.sync_api import TimeoutError as PWTimeout
from scrapers._keywords import KEYWORDS, HARD_EXCLUDE, IRELAND_TERMS, EXCLUDE_NON_IRELAND_CITIES

# Multiple keyword searches against IrishJobs.ie, same pattern as LinkedIn.
# Each search URL targets a different role family.
IRISHJOBS_SEARCHES = [
    "software-engineer",
    "cloud-engineer",
    "devops-engineer",
    "graduate-software-engineer",
    "junior-software-engineer",
    "site-reliability-engineer",
    "platform-engineer",
    "data-engineer",
]

IRISHJOBS_BASE = "https://www.irishjobs.ie/jobs/{slug}?location=Ireland&sort=2"


def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in HARD_EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)


def is_ireland(location: str) -> bool:
    loc = location.lower()
    if any(city in loc for city in EXCLUDE_NON_IRELAND_CITIES):
        return False
    if not location:
        return True
    return any(term in loc for term in IRELAND_TERMS)


def _wait_and_select(page, selector: str, timeout: int = 20000) -> list:
    page.wait_for_timeout(2500)
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return page.query_selector_all(selector)
    except PWTimeout:
        return []


def _parse_irishjobs_page(page) -> list[dict]:
    """Parse a single IrishJobs.ie search results page."""
    results = []
    selector = (
        "article[data-at='job-item'], "
        "div[data-genesis-element='CARD'], "
        "li.job-result, "
        "div.job-card"
    )
    cards = _wait_and_select(page, selector, timeout=20000)
    for card in cards:
        title_el = card.query_selector(
            "h2 a, h3 a, a[data-at='job-item-title'], a.job-title"
        )
        company_el = card.query_selector(
            "[data-at='job-item-company-name'], span.company-name, .job-company"
        )
        location_el = card.query_selector(
            "[data-at='job-item-location'], span.location, .job-location"
        )
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        company  = company_el.inner_text().strip() if company_el else "Unknown"
        location = location_el.inner_text().strip() if location_el else "Ireland"
        href     = title_el.get_attribute("href") or ""
        url      = href if href.startswith("http") else "https://www.irishjobs.ie" + href

        if not is_ireland(location):
            continue
        if not is_entry_level(title):
            continue

        results.append({
            "id": url or title, "company": company, "title": title,
            "location": location, "url": url, "source": "irishjobs",
        })
    return results


def scrape_irishjobs_multi(context) -> list[dict]:
    """
    Runs multiple keyword searches against IrishJobs.ie using a shared
    browser context (passed in from playwright_scraper.py).
    """
    all_jobs = []
    for slug in IRISHJOBS_SEARCHES:
        url = IRISHJOBS_BASE.format(slug=slug)
        print(f"[Playwright] Scraping IrishJobs ({slug}) ...")
        try:
            page = context.new_page()
            page.goto(url, timeout=45000, wait_until="domcontentloaded")
            jobs = _parse_irishjobs_page(page)
            print(f"  IrishJobs ({slug}): {len(jobs)} jobs")
            all_jobs.extend(jobs)
            page.close()
        except Exception as e:
            print(f"[Playwright] IrishJobs ({slug}) failed: {e}")

    # Deduplicate by URL/id since searches overlap heavily
    seen, unique = set(), []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique.append(job)
    print(f"  IrishJobs total unique: {len(unique)} jobs")
    return unique


# Kept for backward compatibility with single-page callers
def parse_irishjobs(page) -> list[dict]:
    return _parse_irishjobs_page(page)
