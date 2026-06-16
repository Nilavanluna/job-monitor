#!/usr/bin/env python3
"""Greenhouse scraper — filters to Ireland only."""
import requests
from scrapers._keywords import KEYWORDS, HARD_EXCLUDE, IRELAND_TERMS


def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in HARD_EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)


def is_ireland(location: str) -> bool:
    loc = location.lower()
    return any(term in loc for term in IRELAND_TERMS)


def scrape(company: dict) -> list[dict]:
    slug = company["slug"]
    name = company["name"]
    url  = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
    except Exception as e:
        print(f"[Greenhouse] {name} error: {e}")
        return []

    results = []
    for job in jobs:
        title    = job.get("title", "")
        location = job.get("location", {}).get("name", "")
        if not is_ireland(location):
            continue
        if not is_entry_level(title):
            continue
        results.append({
            "id":       str(job["id"]),
            "company":  name,
            "title":    title,
            "location": location,
            "url":      job.get("absolute_url", ""),
            "source":   "greenhouse",
        })
    return results
