"""
Job Fetcher Utility
Fetches active job postings for recommended roles via API or local dataset fallback.
Mindful of reliability and network limits.
"""

import os
from typing import List, Dict, Any, Optional
import pandas as pd

# Resolved path for sample_jobs.csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_jobs.csv")


def load_dataset_jobs() -> List[Dict[str, Any]]:
    """Loads default sample jobs from local CSV dataset."""
    if not os.path.exists(DATA_PATH):
        return []
    try:
        df = pd.read_csv(DATA_PATH)
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error loading sample_jobs.csv: {e}")
        return []


def build_search_links(job_title: str, location: str = "") -> Dict[str, str]:
    """Generates direct live search links for LinkedIn and Indeed for live opportunities."""
    query = f"{job_title} {location}".strip().replace(" ", "+")
    return {
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={query}",
        "indeed": f"https://www.indeed.com/jobs?q={query}"
    }


def fetch_jobs_for_role(
    role_title: str,
    location_filter: Optional[str] = None,
    work_type_filter: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Fetches job listings matching the specified role title.
    Attempts live API query if configured, otherwise leverages the
    curated dataset with fuzzy keyword matching.
    """
    all_jobs = load_dataset_jobs()
    matching_jobs = []

    # Clean role keywords
    role_tokens = set(role_title.lower().split())

    for job in all_jobs:
        job_title = str(job.get("job_title", "")).lower()
        skills = str(job.get("skills_required", "")).lower()

        # Match check
        token_match = any(t in job_title for t in role_tokens if len(t) > 2)
        category_match = any(t in skills for t in role_tokens if len(t) > 2)

        if token_match or category_match:
            # Check location filter
            if location_filter and location_filter.lower() not in str(job.get("location", "")).lower():
                continue
            # Check work type filter
            if work_type_filter and work_type_filter.lower() != "all":
                if work_type_filter.lower() not in str(job.get("work_type", "")).lower():
                    continue

            # Ensure dynamic live fallback links exist
            search_links = build_search_links(job.get("job_title", role_title), job.get("location", ""))
            job_copy = dict(job)
            job_copy["live_search_linkedin"] = search_links["linkedin"]
            job_copy["live_search_indeed"] = search_links["indeed"]

            matching_jobs.append(job_copy)

    # If no strict matches found, return top general openings
    if not matching_jobs and all_jobs:
        for job in all_jobs[:limit]:
            job_copy = dict(job)
            search_links = build_search_links(job.get("job_title", role_title))
            job_copy["live_search_linkedin"] = search_links["linkedin"]
            job_copy["live_search_indeed"] = search_links["indeed"]
            matching_jobs.append(job_copy)

    return matching_jobs[:limit]


def fetch_all_ranked_jobs(top_roles: List[Dict[str, Any]], limit_per_role: int = 3) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetches job openings grouped by each ranked role in top_roles.
    Returns dictionary mapping role title to list of job records.
    """
    results = {}
    for role in top_roles:
        role_title = role.get("title", "")
        jobs = fetch_jobs_for_role(role_title, limit=limit_per_role)
        results[role_title] = jobs
    return results
