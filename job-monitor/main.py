#!/usr/bin/env python3
"""
Job Monitor — Main Entry Point
Runs all scrapers, diffs against state, sends Telegram alerts for new jobs.
"""
import yaml
from scrapers.greenhouse import scrape as scrape_greenhouse
from scrapers.lever import scrape as scrape_lever
from scrapers.workday import scrape_microsoft, scrape_workday_generic
from scrapers.playwright_scraper import scrape_all as scrape_playwright
from diff_engine import load_state, save_state, find_new_jobs, update_state
from notifier import notify_new_jobs

def load_companies(path="companies.yml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    print("=" * 50)
    print("🔍 Job Monitor starting...")
    print("=" * 50)

    companies = load_companies()
    all_jobs  = []

    # ── Greenhouse ──────────────────────────────────────
    print("\n[1/4] Scraping Greenhouse companies...")
    for company in companies.get("greenhouse", []):
        jobs = scrape_greenhouse(company)
        print(f"  {company['name']}: {len(jobs)} entry-level jobs in Dublin")
        all_jobs.extend(jobs)

    # ── Lever ───────────────────────────────────────────
    print("\n[2/4] Scraping Lever companies...")
    for company in companies.get("lever", []):
        jobs = scrape_lever(company)
        print(f"  {company['name']}: {len(jobs)} entry-level jobs in Dublin")
        all_jobs.extend(jobs)

    # ── Workday / Microsoft ─────────────────────────────
    print("\n[3/4] Scraping Workday companies...")
    ms_jobs = scrape_microsoft()
    print(f"  Microsoft: {len(ms_jobs)} entry-level jobs in Dublin")
    all_jobs.extend(ms_jobs)

    for company in companies.get("workday", []):
        if company["name"] == "Microsoft":
            continue  # already handled above
        jobs = scrape_workday_generic(company)
        print(f"  {company['name']}: {len(jobs)} entry-level jobs")
        all_jobs.extend(jobs)

    # ── Playwright ──────────────────────────────────────
    print("\n[4/4] Scraping custom career pages with Playwright...")
    playwright_companies = companies.get("playwright", [])
    playwright_jobs = scrape_playwright(playwright_companies)
    print(f"  Playwright total: {len(playwright_jobs)} entry-level jobs found")
    all_jobs.extend(playwright_jobs)

    # ── Diff & Notify ────────────────────────────────────
    print(f"\n📋 Total jobs found this run: {len(all_jobs)}")

    state    = load_state()
    new_jobs = find_new_jobs(all_jobs, state)

    print(f"🆕 New jobs since last run: {len(new_jobs)}")

    if new_jobs:
        for job in new_jobs:
            print(f"  ✅ {job['company']} — {job['title']} ({job['location']})")
        notify_new_jobs(new_jobs)
        state = update_state(state, new_jobs)
        save_state(state)
        print("💾 State updated.")
    else:
        print("😴 No new jobs. Nothing to notify.")

    print("\n✅ Done.")

if __name__ == "__main__":
    main()
