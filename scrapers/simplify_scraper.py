#!/usr/bin/env python3
import requests
from scrapers._keywords import HARD_EXCLUDE

LISTINGS_URL = "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json"

US_FALSE_POSITIVES = [
    "dublin, oh", "dublin, ca", "dublin, ga", "dublin, tx",
    "cork, ar", "limerick, pa", "shannon, ms",
]

def is_ireland(locations):
    for loc in locations:
        loc_lower = loc.lower()
        if any(fp in loc_lower for fp in US_FALSE_POSITIVES):
            continue
        if any(term in loc_lower for term in ["ireland", ", ie", "(ie)", "irl"]):
            return True
        for city in ["dublin", "cork", "galway", "limerick"]:
            if city in loc_lower:
                if not any(us in loc_lower for us in [", oh", ", ca", ", ga", ", tx", ", pa", ", ms"]):
                    return True
    return False

def scrape():
    try:
        resp = requests.get(LISTINGS_URL, timeout=15)
        resp.raise_for_status()
        listings = resp.json()
    except Exception as e:
        print(f"[Simplify] Error: {e}")
        return []

    results = []
    for job in listings:
        if not job.get("active", True):
            continue
        title = job.get("title", "")
        company = job.get("company_name", "")
        locations = job.get("locations", [])
        url = job.get("url", "")

        if not is_ireland(locations):
            continue

        # Only exclude obvious non-tech senior roles
        t = title.lower()
        if any(x in t for x in HARD_EXCLUDE):
            continue

        results.append({
            "id": f"simplify_{job.get('id', company + title)}",
            "company": company,
            "title": title,
            "location": ", ".join(locations),
            "url": url,
            "source": "simplify",
        })
    print(f"  Found {len(results)} Ireland jobs from Simplify")
    return results
