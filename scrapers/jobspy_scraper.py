#!/usr/bin/env python3
from jobspy import scrape_jobs
from scrapers._keywords import HARD_EXCLUDE

SEARCHES = [
    "software engineer Ireland",
    "graduate developer cloud devops AI Ireland",
]

def scrape():
    all_jobs = []
    seen = set()
    for term in SEARCHES:
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "google"],
                search_term=term,
                location="Ireland",
                results_wanted=15,
                hours_old=48,
                country_indeed="Ireland",
                verbose=0,
            )
            for _, job in jobs.iterrows():
                title = str(job.get("title", ""))
                company = str(job.get("company", ""))
                location = str(job.get("location", ""))
                url = str(job.get("job_url", ""))
                key = f"{company.lower()}_{title.lower()}"
                if key in seen:
                    continue
                seen.add(key)
                if any(x in title.lower() for x in HARD_EXCLUDE):
                    continue
                all_jobs.append({"id": f"jobspy_{key}", "company": company, "title": title, "location": location, "url": url, "source": "jobspy"})
        except Exception as e:
            print(f"[JobSpy] Error for {term}: {e}")
    print(f"  Found {len(all_jobs)} Ireland jobs from JobSpy")
    return all_jobs
