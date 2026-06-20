#!/usr/bin/env python3
"""
Playwright scraper — Google, Amazon, Microsoft, Meta, Apple, Intel,
Mastercard, Visa, CrowdStrike, Accenture, IrishJobs.ie, Jobs.ie.
Location: all of Ireland.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from scrapers._keywords import KEYWORDS, HARD_EXCLUDE, IRELAND_TERMS, EXCLUDE_NON_IRELAND_CITIES
from scrapers.irish_boards import parse_irishjobs, parse_jobsie


def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in HARD_EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)


def is_ireland(location: str) -> bool:
    loc = location.lower()
    if any(city in loc for city in EXCLUDE_NON_IRELAND_CITIES):
        return False
    return any(term in loc for term in IRELAND_TERMS)


def _wait_and_select(page, selector: str, timeout: int = 20000) -> list:
    page.wait_for_timeout(3000)
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return page.query_selector_all(selector)
    except PWTimeout:
        return []


def parse_google(page) -> list[dict]:
    results = []
    cards = _wait_and_select(page, "li.lLd3Je")
    for card in cards:
        title_el = card.query_selector("h3.QJPWVe")
        loc_el   = card.query_selector("span.r0wTof")
        link_el  = card.query_selector("a")
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        location = loc_el.inner_text().strip() if loc_el else "Ireland"
        href     = link_el.get_attribute("href") or "" if link_el else ""
        if href and not href.startswith("/"):
            href = "/" + href
        url = "https://careers.google.com" + href if href else ""
        if not is_ireland(location):
            continue
        if is_entry_level(title):
            results.append({"id": url, "company": "Google", "title": title,
                             "location": location, "url": url, "source": "playwright"})
    return results


def parse_amazon(page) -> list[dict]:
    results = []
    cards = _wait_and_select(page, "div.job-tile")
    for card in cards:
        title_el    = card.query_selector("h3.job-title")
        link_el     = card.query_selector("a.job-link")
        location_el = card.query_selector("div.location-and-id")
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        location = location_el.inner_text().strip() if location_el else ""
        href     = link_el.get_attribute("href") or "" if link_el else ""
        url      = "https://www.amazon.jobs" + href if href else ""
        if not is_ireland(location):
            continue
        if is_entry_level(title):
            results.append({"id": url, "company": "Amazon", "title": title,
                             "location": location, "url": url, "source": "playwright"})
    return results


def parse_microsoft(page) -> list[dict]:
    results = []
    cards = _wait_and_select(page, "div[class*='ms-List-cell']", timeout=25000)
    for card in cards:
        title_el    = card.query_selector("a[aria-label]")
        location_el = card.query_selector("span[class*='location']")
        if not title_el:
            continue
        title    = (title_el.get_attribute("aria-label") or title_el.inner_text()).strip()
        location = location_el.inner_text().strip() if location_el else "Ireland"
        href     = title_el.get_attribute("href") or ""
        url      = href if href.startswith("http") else "https://jobs.careers.microsoft.com" + href
        if not is_ireland(location):
            continue
        if is_entry_level(title):
            results.append({"id": url, "company": "Microsoft", "title": title,
                             "location": location, "url": url, "source": "playwright"})
    return results


def parse_meta(page) -> list[dict]:
    results = []
    cards = _wait_and_select(page, "div._8muv, [data-testid='job-result']", timeout=25000)
    for card in cards:
        title_el    = card.query_selector("span._8n2t, [data-testid='job-title']")
        location_el = card.query_selector("div._9asx span:first-child, [data-testid='job-location']")
        link_el     = card.query_selector("a")
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        location = location_el.inner_text().strip() if location_el else ""
        href     = link_el.get_attribute("href") or "" if link_el else ""
        url      = href if href.startswith("http") else "https://www.metacareers.com" + href
        if not is_ireland(location):
            continue
        if is_entry_level(title):
            results.append({"id": url, "company": "Meta", "title": title,
                             "location": location, "url": url, "source": "playwright"})
    return results


def parse_apple(page) -> list[dict]:
    results = []
    rows = _wait_and_select(page, "table#search-results tbody tr, .table-row", timeout=25000)
    for row in rows:
        title_el    = row.query_selector("td.table-col-1 a, .title a")
        location_el = row.query_selector("td.table-col-2, .location")
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        location = location_el.inner_text().strip() if location_el else ""
        href     = title_el.get_attribute("href") or ""
        url      = href if href.startswith("http") else "https://jobs.apple.com" + href
        if not is_ireland(location) and location:
            continue
        if is_entry_level(title):
            results.append({"id": url, "company": "Apple", "title": title,
                             "location": location or "Ireland", "url": url, "source": "playwright"})
    return results


def parse_intel(page) -> list[dict]:
    results = []
    cards = _wait_and_select(page, "li.job-list-item, div.job-card", timeout=25000)
    for card in cards:
        title_el    = card.query_selector("a.job-title, h2 a, h3 a")
        location_el = card.query_selector("span.job-location, .location")
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        location = location_el.inner_text().strip() if location_el else "Ireland"
        href     = title_el.get_attribute("href") or ""
        url      = href if href.startswith("http") else "https://jobs.intel.com" + href
        if not is_ireland(location) and location:
            continue
        if is_entry_level(title):
            results.append({"id": url, "company": "Intel", "title": title,
                             "location": location, "url": url, "source": "playwright"})
    return results


def parse_workday_page(page, company_name: str) -> list[dict]:
    results = []
    cards = _wait_and_select(
        page,
        "li[class*='css-'], [data-automation-id='jobItem'], ul[role='list'] li",
        timeout=25000
    )
    for card in cards:
        title_el    = card.query_selector(
            "a[data-automation-id='jobTitle'], h3 a, a.css-19uc56f"
        )
        location_el = card.query_selector(
            "div[data-automation-id='locations'], dd[data-automation-id='location'], "
            "div[class*='location'], span[class*='location']"
        )
        if not title_el:
            continue
        title    = title_el.inner_text().strip()
        location = location_el.inner_text().strip() if location_el else ""
        if not title or len(title) < 4:
            continue
        if not is_ireland(location) and location:
            continue
        if not is_entry_level(title):
            continue
        href = title_el.get_attribute("href") or ""
        base = "https://" + page.url.split("/")[2]
        url  = href if href.startswith("http") else base + href
        results.append({"id": url or title, "company": company_name, "title": title,
                         "location": location or "Ireland", "url": url, "source": "playwright"})
    return results


def parse_mastercard(page)  -> list[dict]: return parse_workday_page(page, "Mastercard")
def parse_visa(page)        -> list[dict]: return parse_workday_page(page, "Visa")
def parse_crowdstrike(page) -> list[dict]: return parse_workday_page(page, "CrowdStrike")
def parse_accenture(page)   -> list[dict]: return parse_workday_page(page, "Accenture")


PARSERS = {
    "Google":      parse_google,
    "Amazon":      parse_amazon,
    "Microsoft":   parse_microsoft,
    "Meta":        parse_meta,
    "Apple":       parse_apple,
    "Intel":       parse_intel,
    "Mastercard":  parse_mastercard,
    "Visa":        parse_visa,
    "CrowdStrike": parse_crowdstrike,
    "Accenture":   parse_accenture,
    "IrishJobs":   parse_irishjobs,
    "JobsIE":      parse_jobsie,
}


def scrape_all(companies: list[dict]) -> list[dict]:
    all_jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-IE",
        )
        for company in companies:
            if company.get("skip"):
                continue
            name = company["name"]
            url  = company["url"]
            print(f"[Playwright] Scraping {name} ...")
            try:
                page = context.new_page()
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
        browser.close()
    return all_jobs
