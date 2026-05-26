from dotenv import load_dotenv
from agent.searcher import search_jobs
from agent.brain import score_job
from agent.notifier import send_daily_digest

load_dotenv()

JOB_TITLES = [
    "Senior Product Manager",
    "Product Manager",
    "Project Manager",
    "Business Analyst",
]
LOCATION = "Singapore"
RESULTS_PER_TITLE = 10
SCORE_THRESHOLD = 7


def main():
    print("=" * 50)
    print("Job Hunting Agent Starting...")
    print("=" * 50)

    print(f"\n[1/3] Searching for jobs in {LOCATION}...")
    raw_jobs = search_jobs(JOB_TITLES, location=LOCATION, results_per_title=RESULTS_PER_TITLE)
    print(f"      Found {len(raw_jobs)} unique jobs.")

    if not raw_jobs:
        send_daily_digest([])
        return

    print(f"\n[2/3] Scoring {len(raw_jobs)} jobs with Claude...")
    scored_jobs = []
    for i, job in enumerate(raw_jobs, 1):
        print(f"      {i}/{len(raw_jobs)}: {job['title']} @ {job['company']}...", end=" ", flush=True)
        result = score_job(job)
        scored_jobs.append(result)
        print(f"{result['score']}/10")

    print(f"\n[3/3] Filtering scores >= {SCORE_THRESHOLD}...")
    passing_jobs = sorted(
        [j for j in scored_jobs if j["score"] >= SCORE_THRESHOLD],
        key=lambda j: j["score"],
        reverse=True,
    )
    print(f"      {len(passing_jobs)} jobs passed (out of {len(scored_jobs)} scored).")

    print("\nSending Telegram digest...")
    send_daily_digest(passing_jobs)
    print("Done! Check your Telegram. 🎯")
    print("=" * 50)


if __name__ == "__main__":
    main()
