"""
Playwright-based scraper for companies with custom career pages.
Runs headless Chromium. Each company has a custom parse function
because every career page is different.
"""
import re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

KEYWORDS = ["engineer", "cloud", "devops", "software", "developer", "sre", "platform",
            "backend", "fullstack", "full-stack", "graduate", "intern"]
EXCLUDE  = ["senior", "staff", "principal", "director", "manager", "lead", "vp ",
            "head of", "sr."]

def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)

# ── helpers ────────────────────────────────────────────────────────────────

def _get_text_links(page, selector_title, selector_link=None):
    """Generic: grab all matching title elements + their href."""
    items = []
    try:
        els = page.query_selector_all(selector_title)
        for el in els:
            title = el.inner_text().strip()
            href  = ""
            if selector_link:
                link_el = el.query_selector(selector_link)
                href = link_el.get_attribute("href") if link_el else ""
            else:
                href = el.get_attribute("href") or ""
            items.append((title, href))
    except Exception:
        pass
    return items

# ── per-company parsers ─────────────────────────────────────────────────────

def parse_google(page) -> list[dict]:
    results = []
    try:
        page.wait_for_selector("li.lLd3Je", timeout=15000)
        cards = page.query_selector_all("li.lLd3Je")
        for card in cards:
            title_el = card.query_selector("h3.QJPWVe")
            link_el  = card.query_selector("a")
            if not title_el:
                continue
            title = title_el.inner_text().strip()
            url   = "https://careers.google.com" + (link_el.get_attribute("href") or "") if link_el else ""
            if is_entry_level(title):
                results.append({"id": url, "company": "Google", "title": title,
                                 "location": "Dublin, Ireland", "url": url, "source": "playwright"})
    except PWTimeout:
        print("[Playwright] Google timed out")
    return results


def parse_amazon(page) -> list[dict]:
    results = []
    try:
        page.wait_for_selector("div.job-tile", timeout=15000)
        cards = page.query_selector_all("div.job-tile")
        for card in cards:
            title_el = card.query_selector("h3.job-title")
            link_el  = card.query_selector("a.job-link")
            if not title_el:
                continue
            title = title_el.inner_text().strip()
            url   = "https://www.amazon.jobs" + (link_el.get_attribute("href") or "") if link_el else ""
            if is_entry_level(title):
                results.append({"id": url, "company": "Amazon", "title": title,
                                 "location": "Dublin, Ireland", "url": url, "source": "playwright"})
    except PWTimeout:
        print("[Playwright] Amazon timed out")
    return results


def parse_oracle(page) -> list[dict]:
    results = []
    try:
        page.wait_for_selector("article.job", timeout=15000)
        cards = page.query_selector_all("article.job")
        for card in cards:
            title_el = card.query_selector("h2")
            link_el  = card.query_selector("a")
            if not title_el:
                continue
            title = title_el.inner_text().strip()
            url   = link_el.get_attribute("href") or "" if link_el else ""
            if is_entry_level(title):
                results.append({"id": url, "company": "Oracle", "title": title,
                                 "location": "Dublin, Ireland", "url": url, "source": "playwright"})
    except PWTimeout:
        print("[Playwright] Oracle timed out")
    return results


def parse_generic(page, company_name: str, url_base: str) -> list[dict]:
    """Fallback: grab any <a> whose text looks like a job title."""
    results = []
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
        links = page.query_selector_all("a")
        seen  = set()
        for link in links:
            title = link.inner_text().strip()
            href  = link.get_attribute("href") or ""
            if len(title) < 5 or title in seen:
                continue
            if is_entry_level(title):
                full_url = href if href.startswith("http") else url_base + href
                seen.add(title)
                results.append({"id": full_url or title, "company": company_name,
                                 "title": title, "location": "Dublin, Ireland",
                                 "url": full_url, "source": "playwright"})
    except Exception as e:
        print(f"[Playwright] {company_name} generic error: {e}")
    return results


PARSERS = {
    "Google":   parse_google,
    "Amazon":   parse_amazon,
    "Oracle":   parse_oracle,
}

# ── main entry ─────────────────────────────────────────────────────────────

def scrape_all(companies: list[dict]) -> list[dict]:
    all_jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        for company in companies:
            name = company["name"]
            url  = company["url"]
            print(f"[Playwright] Scraping {name} ...")
            try:
                page = context.new_page()
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                parser = PARSERS.get(name)
                if parser:
                    jobs = parser(page)
                else:
                    url_base = "/".join(url.split("/")[:3])
                    jobs = parse_generic(page, name, url_base)
                all_jobs.extend(jobs)
                page.close()
            except Exception as e:
                print(f"[Playwright] {name} failed: {e}")
        browser.close()
    return all_jobs
