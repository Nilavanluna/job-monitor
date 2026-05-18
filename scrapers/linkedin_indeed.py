"""
LinkedIn and Indeed scraper using their public job search URLs.
Uses Playwright to load results and extract job cards.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

KEYWORDS = [
    "cloud engineer", "devops engineer", "software engineer", "sre",
    "platform engineer", "backend engineer", "fullstack engineer",
    "graduate engineer", "junior engineer", "intern engineer",
    "junior developer", "graduate developer", "cloud developer",
    "junior software", "graduate software", "cloud intern",
    "devops intern", "software intern"
]

LEVEL_KEYWORDS = ["graduate", "junior", "intern", "entry", "associate", "apprentice"]
TECH_KEYWORDS  = ["cloud", "devops", "sre", "software", "engineer", "developer",
                   "platform", "backend", "fullstack", "infrastructure"]
EXCLUDE        = ["senior", "staff", "principal", "director", "manager",
                  "lead ", "vp ", "head of", "sr.", "architect"]

def is_relevant(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in EXCLUDE):
        return False
    has_level = any(x in t for x in LEVEL_KEYWORDS)
    has_tech  = any(x in t for x in TECH_KEYWORDS)
    return has_level or has_tech


LINKEDIN_SEARCHES = [
    "https://www.linkedin.com/jobs/search/?keywords=cloud+engineer+graduate&location=Dublin%2C+Ireland&f_E=1%2C2&f_JT=F%2CI",
    "https://www.linkedin.com/jobs/search/?keywords=junior+software+engineer&location=Dublin%2C+Ireland&f_E=1%2C2&f_JT=F%2CI",
    "https://www.linkedin.com/jobs/search/?keywords=devops+engineer+graduate&location=Dublin%2C+Ireland&f_E=1%2C2&f_JT=F%2CI",
    "https://www.linkedin.com/jobs/search/?keywords=software+engineer+intern+ireland&location=Dublin%2C+Ireland&f_JT=I",
]

INDEED_SEARCHES = [
    "https://ie.indeed.com/jobs?q=cloud+engineer+graduate&l=Dublin&fromage=1",
    "https://ie.indeed.com/jobs?q=junior+software+engineer&l=Dublin&fromage=1",
    "https://ie.indeed.com/jobs?q=devops+engineer&l=Dublin&jt=internship&fromage=1",
    "https://ie.indeed.com/jobs?q=graduate+software+engineer&l=Dublin&fromage=1",
]


def scrape_linkedin(page, url: str) -> list[dict]:
    results = []
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        cards = page.query_selector_all("div.base-card")
        for card in cards:
            title_el    = card.query_selector("h3.base-search-card__title")
            company_el  = card.query_selector("h4.base-search-card__subtitle")
            location_el = card.query_selector("span.job-search-card__location")
            link_el     = card.query_selector("a.base-card__full-link")
            if not title_el:
                continue
            title    = title_el.inner_text().strip()
            company  = company_el.inner_text().strip() if company_el else "Unknown"
            location = location_el.inner_text().strip() if location_el else "Dublin, Ireland"
            link     = link_el.get_attribute("href") if link_el else ""
            if is_relevant(title):
                results.append({
                    "id":       link or title,
                    "company":  company,
                    "title":    title,
                    "location": location,
                    "url":      link,
                    "source":   "linkedin",
                })
    except PWTimeout:
        print(f"[LinkedIn] Timeout on {url}")
    except Exception as e:
        print(f"[LinkedIn] Error: {e}")
    return results


def scrape_indeed(page, url: str) -> list[dict]:
    results = []
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        cards = page.query_selector_all("div.job_seen_beacon")
        for card in cards:
            title_el    = card.query_selector("h2.jobTitle span")
            company_el  = card.query_selector("span.companyName")
            location_el = card.query_selector("div.companyLocation")
            link_el     = card.query_selector("a.jcs-JobTitle")
            if not title_el:
                continue
            title    = title_el.inner_text().strip()
            company  = company_el.inner_text().strip() if company_el else "Unknown"
            location = location_el.inner_text().strip() if location_el else "Dublin, Ireland"
            href     = link_el.get_attribute("href") if link_el else ""
            link     = "https://ie.indeed.com" + href if href.startswith("/") else href
            if is_relevant(title):
                results.append({
                    "id":       link or title,
                    "company":  company,
                    "title":    title,
                    "location": location,
                    "url":      link,
                    "source":   "indeed",
                })
    except PWTimeout:
        print(f"[Indeed] Timeout on {url}")
    except Exception as e:
        print(f"[Indeed] Error: {e}")
    return results


def scrape_all() -> list[dict]:
    all_jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )

        print("[LinkedIn] Scraping job searches...")
        for url in LINKEDIN_SEARCHES:
            page = context.new_page()
            jobs = scrape_linkedin(page, url)
            print(f"  Found {len(jobs)} relevant jobs")
            all_jobs.extend(jobs)
            page.close()

        print("[Indeed] Scraping job searches...")
        for url in INDEED_SEARCHES:
            page = context.new_page()
            jobs = scrape_indeed(page, url)
            print(f"  Found {len(jobs)} relevant jobs")
            all_jobs.extend(jobs)
            page.close()

        browser.close()

    # Deduplicate by ID
    seen = set()
    unique = []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique.append(job)
    return unique
