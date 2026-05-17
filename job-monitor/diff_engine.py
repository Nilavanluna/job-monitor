import json
import os

STATE_FILE = "state.json"

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def find_new_jobs(current_jobs: list[dict], state: dict) -> list[dict]:
    """
    Returns jobs whose ID wasn't in the previous state.
    State is a flat dict of {job_id: True}.
    """
    new_jobs = []
    for job in current_jobs:
        job_id = job["id"]
        if job_id and job_id not in state:
            new_jobs.append(job)
    return new_jobs

def update_state(state: dict, jobs: list[dict]) -> dict:
    for job in jobs:
        if job["id"]:
            state[job["id"]] = True
    return state
