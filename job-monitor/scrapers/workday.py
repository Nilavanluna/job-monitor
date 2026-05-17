import requests

KEYWORDS = ["engineer", "cloud", "devops", "software", "developer", "sre", "platform", "backend", "fullstack", "graduate", "intern"]
EXCLUDE  = ["senior", "staff", "principal", "director", "manager", "lead", "vp ", "head of", "sr."]

def is_entry_level(title: str) -> bool:
    t = title.lower()
    if any(x in t for x in EXCLUDE):
        return False
    return any(x in t for x in KEYWORDS)

def scrape_microsoft() -> list[dict]:
    url = (
        "https://gcsservices.careers.microsoft.com/search/api/v1/search"
        "?lc=Dublin%2C%20Ireland&exp=Students%20and%20graduates&pgSz=20&pg=1&en=20"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("operationResult", {}).get("result", {}).get("jobs", [])
    except Exception as e:
        print(f"[Microsoft] error: {e}")
        return []

    results = []
    for job in jobs:
        title = job.get("title", "")
        if is_entry_level(title):
            results.append({
                "id":       str(job.get("jobId", "")),
                "company":  "Microsoft",
                "title":    title,
                "location": job.get("location", "Dublin, Ireland"),
                "url":      f"https://jobs.careers.microsoft.com/global/en/job/{job.get('jobId','')}",
                "source":   "microsoft",
            })
    return results


def scrape_workday_generic(company: dict) -> list[dict]:
    """
    Generic Workday API call.
    Workday exposes a JSON search endpoint at:
    https://<tenant>.wd1.myworkdayjobs.com/wday/cxs/<tenant>/<board>/jobs
    We POST with location filters.
    """
    api_url = company.get("api_url")
    name    = company["name"]
    if not api_url:
        return []

    payload = {
        "appliedFacets": {"Location_Country": ["bc33aa3152ec42d4995f4791a106ed09"]},  # Ireland
        "limit": 20,
        "offset": 0,
        "searchText": ""
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        jobs = resp.json().get("jobPostings", [])
    except Exception as e:
        print(f"[Workday] {name} error: {e}")
        return []

    results = []
    for job in jobs:
        title    = job.get("title", "")
        location = job.get("locationsText", "Ireland")
        ext_url  = job.get("externalPath", "")
        base     = api_url.split("/wday")[0]
        full_url = base + ext_url if ext_url else base
        if is_entry_level(title):
            results.append({
                "id":       job.get("bulletFields", [""])[0] or title,
                "company":  name,
                "title":    title,
                "location": location,
                "url":      full_url,
                "source":   "workday",
            })
    return results
