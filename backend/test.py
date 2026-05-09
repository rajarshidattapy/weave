import os
import time
import requests

BASE = "https://api.anakin.io/v1"
API_KEY = os.environ.get("ANAKIN_API_KEY")
if not API_KEY:
    raise SystemExit("ANAKIN_API_KEY is not set")

session = requests.Session()
session.headers.update({"X-API-Key": API_KEY, "Content-Type": "application/json"})


def request(method: str, path: str, json=None):
    try:
        resp = session.request(method, BASE + path, json=json, timeout=30)
        return resp.json()
    except requests.RequestException:
        return None  # caller retries on None


def scrape(url: str) -> dict:
    submitted = request("POST", "/url-scraper", {"url": url})
    job_id = submitted["jobId"]

    for _ in range(60):
        job = request("GET", f"/url-scraper/{job_id}")
        if job is None:
            time.sleep(3)  # retry transient errors
            continue
        if job["status"] == "completed":
            return job
        if job["status"] == "failed":
            raise RuntimeError(f"scrape failed: {job.get('error')}")
        time.sleep(3)
    raise TimeoutError("timed out after 3 minutes")


if __name__ == "__main__":
    job = scrape("https://example.com")
    print(job["markdown"])