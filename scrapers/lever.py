#!/usr/bin/env python3
"""
Lever scraper — fetches all postings, filters to Ireland client-side.
Lever's ?location= param does nothing on the public API.
"""
import requests
from scrapers._keywords import KEYWORDS, HARD_EXCLUDE, IRELAND_TERMS


def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in HARD_EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)


def is_ireland(job: dict) -> bool:
    location = job.get("categories", {}).get("location", "") or ""
    tags     = " ".join(job.get("tags", []))
    combined = f"{location} {tags}".lower()
    return any(term in combined for term in IRELAND_TERMS)


def scrape(company: dict) -> list[dict]:
    slug = company["slug"]
    name = company["name"]
    url  = f"https://api.lever.co/v0/postings/{slug}?mode=json&limit=500"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        jobs = resp.json()
        if not isinstance(jobs, list):
            jobs = jobs.get("data", [])
    except Exception as e:
        print(f"[Lever] {name} error: {e}")
        return []

    results = []
    for job in jobs:
        title    = job.get("text", "")
        location = job.get("categories", {}).get("location", "Unknown")
        if not is_ireland(job):
            continue
        if not is_entry_level(title):
            continue
        results.append({
            "id":       job.get("id", ""),
            "company":  name,
            "title":    title,
            "location": location,
            "url":      job.get("hostedUrl", ""),
            "source":   "lever",
        })
    return results
