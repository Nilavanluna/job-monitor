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
    url  = f"https://api.lever.co/v0/postings/{slug}?mode=json&location=Dublin"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        jobs = resp.json()
    except Exception as e:
        print(f"[Lever] {name} error: {e}")
        return []

    results = []
    for job in jobs:
        title    = job.get("text", "")
        location = job.get("categories", {}).get("location", "")
        if is_entry_level(title):
            results.append({
                "id":       job.get("id", ""),
                "company":  name,
                "title":    title,
                "location": location,
                "url":      job.get("hostedUrl", ""),
                "source":   "lever",
            })
    return results
