from jobspy import scrape_jobs
import pandas as pd

def search_jobs(job_titles: list, location: str = "Singapore", results_per_title: int = 10):
    all_jobs = []
    
    for title in job_titles:
        print(f"Searching for: {title}...")
        
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin"],
                search_term=title,
                location=location,
                results_wanted=results_per_title,
                hours_old=24  # only jobs posted in last 24 hours
            )
            all_jobs.append(jobs)
            print(f"  Found {len(jobs)} jobs for '{title}'")
            
        except Exception as e:
            print(f"  Error searching '{title}': {e}")
    
    if not all_jobs:
        return []
    
    # combine all results into one list
    combined = pd.concat(all_jobs, ignore_index=True)
    
    # remove duplicate job listings
    combined = combined.drop_duplicates(subset=["title", "company"], keep="first")
    
    # convert to simple list of dictionaries
    jobs_list = []
    for _, row in combined.iterrows():
        jobs_list.append({
            "title": str(row.get("title", "")),
            "company": str(row.get("company", "")),
            "location": str(row.get("location", "")),
            "description": str(row.get("description", ""))[:1000],  # limit length
            "job_url": str(row.get("job_url", "")),
            "date_posted": str(row.get("date_posted", ""))
        })
    
    return jobs_list

# Quick test
if __name__ == "__main__":
    titles = [
        "Senior Product Manager",
        "Product Manager",
        "Business Analyst"
    ]
    
    jobs = search_jobs(titles, location="Singapore")
    print(f"\nTotal unique jobs found: {len(jobs)}")
    
    # print first 3 as preview
    for job in jobs[:3]:
        print(f"\n--- {job['title']} at {job['company']} ---")
        print(f"Location: {job['location']}")
        print(f"URL: {job['job_url']}")