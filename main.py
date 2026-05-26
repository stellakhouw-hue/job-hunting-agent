from datetime import datetime, timezone, timedelta
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
SEEN_JOBS_FILE = "data/seen_jobs.txt"

SGT = timezone(timedelta(hours=8))
BURST_MODE_UNTIL = datetime(2026, 5, 27, 23, 59, tzinfo=SGT)  # tomorrow EOD SGT


def load_seen_urls() -> set:
    try:
        with open(SEEN_JOBS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_seen_urls(urls: set) -> None:
    with open(SEEN_JOBS_FILE, "w") as f:
        f.write("\n".join(sorted(urls)))


def main():
    now_sgt = datetime.now(SGT)

    # After burst mode ends, only run at 8am SGT
    if now_sgt > BURST_MODE_UNTIL and now_sgt.hour != 8:
        print(f"Skipping — burst mode ended. Next run at 8am SGT. (Current SGT: {now_sgt.strftime('%H:%M')})")
        return

    print("=" * 50)
    print("Job Hunting Agent Starting...")
    print(f"SGT time: {now_sgt.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    print(f"\n[1/3] Searching for jobs in {LOCATION}...")
    raw_jobs = search_jobs(JOB_TITLES, location=LOCATION, results_per_title=RESULTS_PER_TITLE)
    print(f"      Found {len(raw_jobs)} unique jobs.")

    # Filter out already-seen jobs
    seen_urls = load_seen_urls()
    new_jobs = [j for j in raw_jobs if j.get("job_url") and j["job_url"] not in seen_urls and j["job_url"] != "nan"]
    print(f"      {len(new_jobs)} are new (unseen before).")

    if not new_jobs:
        print("      No new jobs to score today.")
        send_daily_digest([])
        return

    print(f"\n[2/3] Scoring {len(new_jobs)} new jobs with Claude...")
    scored_jobs = []
    for i, job in enumerate(new_jobs, 1):
        print(f"      {i}/{len(new_jobs)}: {job['title']} @ {job['company']}...", end=" ", flush=True)
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

    # Save all seen URLs (including ones that didn't pass — no point re-scoring them)
    new_urls = {j["job_url"] for j in new_jobs if j.get("job_url")}
    save_seen_urls(seen_urls | new_urls)
    print(f"      Saved {len(new_urls)} new URLs to seen list.")

    print("\nSending Telegram digest...")
    send_daily_digest(passing_jobs)
    print("Done! Check your Telegram. 🎯")
    print("=" * 50)


if __name__ == "__main__":
    main()
