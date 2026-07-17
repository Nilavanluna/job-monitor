#!/usr/bin/env python3
"""Job Monitor — Main Entry Point"""
import warnings
import urllib3
import yaml

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from scrapers.greenhouse import scrape as scrape_greenhouse
from scrapers.lever import scrape as scrape_lever
from scrapers.playwright_scraper import scrape_all as scrape_playwright
from scrapers.linkedin_indeed import scrape_all as scrape_linkedin_indeed
from diff_engine import load_state, save_state, find_new_jobs, update_state
from notifier import notify_new_jobs
from scrapers.jobspy_scraper import scrape as scrape_jobspy


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
    print("\n[1/4] Scraping Greenhouse companies...")
    for company in companies.get("greenhouse", []):
        jobs = scrape_greenhouse(company)
        print(f"  {company['name']}: {len(jobs)} jobs")
        all_jobs.extend(jobs)

    # 2. Lever (kept for future use)
    lever_companies = companies.get("lever", [])
    if lever_companies:
        print("\n[2/4] Scraping Lever companies...")
        for company in lever_companies:
            jobs = scrape_lever(company)
            print(f"  {company['name']}: {len(jobs)} jobs")
            all_jobs.extend(jobs)

    # 3. Playwright (Google, Amazon, Microsoft, Meta, Apple, Intel, Workday companies)
    print("\n[3/4] Scraping career pages...")
    playwright_jobs = scrape_playwright(companies.get("playwright", []))
    print(f"  Playwright total: {len(playwright_jobs)} jobs")
    all_jobs.extend(playwright_jobs)

    # 4. Simplify
    print("\n[4/5] Scraping JobSpy jobs...")
    jobspy_jobs = scrape_jobspy()
    all_jobs.extend(jobspy_jobs)

    # 5. LinkedIn
    print("\n[4/4] Scraping LinkedIn...")
    li_jobs = scrape_linkedin_indeed()
    print(f"  LinkedIn total: {len(li_jobs)} jobs")
    all_jobs.extend(li_jobs)

    # Diff & Notify
    print(f"\nTotal jobs found this run: {len(all_jobs)}")
    state    = load_state()
    new_jobs = find_new_jobs(all_jobs, state)
    print(f"New jobs since last run: {len(new_jobs)}")

    if new_jobs:
        for job in new_jobs:
            src = job.get("source", "").upper()
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
