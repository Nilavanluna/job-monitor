#!/usr/bin/env python3
"""
Job Monitor — Main Entry Point
Runs all scrapers, diffs against state, sends Gmail alerts for new jobs.
"""
import yaml
from scrapers.greenhouse import scrape as scrape_greenhouse
from scrapers.lever import scrape as scrape_lever
from scrapers.workday import scrape_microsoft, scrape_workday_generic
from scrapers.playwright_scraper import scrape_all as scrape_playwright
from scrapers.linkedin_indeed import scrape_all as scrape_linkedin_indeed
from diff_engine import load_state, save_state, find_new_jobs, update_state
from notifier import notify_new_jobs

def load_companies(path="companies.yml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    print("=" * 50)
    print("Job Monitor starting...")
    print("=" * 50)

    companies = load_companies()
    all_jobs  = []

    # 1. Greenhouse
    print("\n[1/5] Scraping Greenhouse companies...")
    for company in companies.get("greenhouse", []):
        jobs = scrape_greenhouse(company)
        print(f"  {company['name']}: {len(jobs)} jobs")
        all_jobs.extend(jobs)

    # 2. Lever
    print("\n[2/5] Scraping Lever companies...")
    for company in companies.get("lever", []):
        jobs = scrape_lever(company)
        print(f"  {company['name']}: {len(jobs)} jobs")
        all_jobs.extend(jobs)

    # 3. Workday / Microsoft
    print("\n[3/5] Scraping Workday companies...")
    ms_jobs = scrape_microsoft()
    print(f"  Microsoft: {len(ms_jobs)} jobs")
    all_jobs.extend(ms_jobs)
    for company in companies.get("workday", []):
        if company["name"] == "Microsoft":
            continue
        jobs = scrape_workday_generic(company)
        print(f"  {company['name']}: {len(jobs)} jobs")
        all_jobs.extend(jobs)

    # 4. Playwright (custom career pages)
    print("\n[4/5] Scraping custom career pages...")
    playwright_jobs = scrape_playwright(companies.get("playwright", []))
    print(f"  Playwright total: {len(playwright_jobs)} jobs")
    all_jobs.extend(playwright_jobs)

    # 5. LinkedIn + Indeed
    print("\n[5/5] Scraping LinkedIn and Indeed...")
    li_jobs = scrape_linkedin_indeed()
    print(f"  LinkedIn + Indeed total: {len(li_jobs)} jobs")
    all_jobs.extend(li_jobs)

    # Diff & Notify
    print(f"\nTotal jobs found this run: {len(all_jobs)}")
    state    = load_state()
    new_jobs = find_new_jobs(all_jobs, state)
    print(f"New jobs since last run: {len(new_jobs)}")

    if new_jobs:
        for job in new_jobs:
            src = job.get('source','').upper()
            print(f"  [{src}] {job['company']} - {job['title']} ({job['location']})")
        notify_new_jobs(new_jobs)
        state = update_state(state, new_jobs)
        save_state(state)
        print("State updated.")
    else:
        print("No new jobs. Nothing to notify.")

    print("\nDone.")

if __name__ == "__main__":
    main()
