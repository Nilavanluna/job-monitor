#!/usr/bin/env python3
"""
IrishJobs.ie + Jobs.ie scraper via Playwright.

Both sites lack RSS/API access — scraped via rendered search result pages.
Selectors use multiple fallback patterns since exact DOM structure can't be
verified outside a live browser session; the run logs will tell us which
selector set actually matches and we'll prune the rest.
"""
from playwright.sync_api import TimeoutError as PWTimeout
from scrapers._keywords import KEYWORDS, HARD_EXCLUDE, IRELAND_TERMS, EXCLUDE_NON_IRELAND_CITIES


def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in HARD_EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)


def is_ireland(location: str) -> bool:
    loc = location.lower()
    if any(city in loc for city in EXCLUDE_NON_IRELAND_CITIES):
        return False
    # IrishJobs/Jobs.ie results are already Ireland-only by definition,
    # but verify when location text is present
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


# ---------------------------------------------------------------------------
# IrishJobs.ie — StepStone-platform listing page
# Common selector patterns for StepStone-family sites (IrishJobs is owned
# by Saongroup/StepStone). Tries several fallback patterns.
# ---------------------------------------------------------------------------
def parse_irishjobs(page) -> list[dict]:
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


# ---------------------------------------------------------------------------
# Jobs.ie — independent Irish job board
# ---------------------------------------------------------------------------
def parse_jobsie(page) -> list[dict]:
    results = []
    selector = (
        "div.job-listing, li.job-listing, "
        "div.search-result, article.job"
    )
    cards = _wait_and_select(page, selector, timeout=20000)
    for card in cards:
        title_el = card.query_selector("h2 a, h3 a, a.job-title, .title a")
        company_el = card.query_selector(".company, .employer, span.company-name")
        location_el = card.query_selector(".location, span.job-location")
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        company  = company_el.inner_text().strip() if company_el else "Unknown"
        location = location_el.inner_text().strip() if location_el else "Ireland"
        href     = title_el.get_attribute("href") or ""
        url      = href if href.startswith("http") else "https://www.jobs.ie" + href

        if not is_ireland(location):
            continue
        if not is_entry_level(title):
            continue

        results.append({
            "id": url or title, "company": company, "title": title,
            "location": location, "url": url, "source": "jobsie",
        })
    return results


PARSERS = {
    "IrishJobs": parse_irishjobs,
    "JobsIE":    parse_jobsie,
}


def scrape_irish_boards(page_factory, companies: list[dict]) -> list[dict]:
    """
    page_factory: a callable that returns a fresh Playwright page from the
    same browser context used by playwright_scraper.py (passed in to avoid
    spinning up a second browser instance).
    """
    all_jobs = []
    for entry in companies:
        name = entry["name"]
        url  = entry["url"]
        print(f"[Playwright] Scraping {name} ...")
        try:
            page = page_factory()
            page.goto(url, timeout=45000, wait_until="domcontentloaded")
            parser = PARSERS.get(name)
            if parser:
                jobs = parser(page)
                print(f"  {name}: {len(jobs)} jobs")
            else:
                print(f"  {name}: no parser, skipping")
                jobs = []
            all_jobs.extend(jobs)
            page.close()
        except Exception as e:
            print(f"[Playwright] {name} failed: {e}")
    return all_jobs
