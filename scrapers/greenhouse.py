import requests

KEYWORDS = ["engineer", "cloud", "devops", "software", "developer", "sre", "platform", "backend", "fullstack", "full-stack", "graduate", "intern"]
EXCLUDE  = ["senior", "staff", "principal", "director", "manager", "lead", "vp ", "head of", "sr."]

def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)

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
        # filter: Dublin/Ireland location AND entry-level title
        if "dublin" in location.lower() or "ireland" in location.lower():
            if is_entry_level(title):
                results.append({
                    "id":       str(job["id"]),
                    "company":  name,
                    "title":    title,
                    "location": location,
                    "url":      job.get("absolute_url", ""),
                    "source":   "greenhouse",
                })
    return results
