import os
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # reads your .env file

client = Anthropic()

def ask_claude(prompt: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text

CV_SUMMARY = """
Candidate: Kiendl Valavani Setio — Senior Product Manager, Singapore PR.
Current: Monee (ShopeePay) since Mar 2022. Owns Wallet & Payment Acquiring: P2P transfers,
cross-border payments (Western Union), Google Play acquiring, SNAP Open API regulatory compliance.
Previous: Xfers/Payfazz PM (Feb 2020–Feb 2022). Scaled B2B payment APIs 0→100+ clients, $100M+ GTV.
Intern: Gojek GoFix.
Skills: Payment infrastructure, acquiring gateways, P2P/cross-border transfers, reconciliation,
fraud/AML, API design, SQL, JIRA, GTM, stakeholder management, SEA markets.
Target: Senior PM / PM / Project Manager / Business Analyst in Singapore.
"""

def score_job(job: dict) -> dict:
    prompt = f"""You are evaluating a job posting against a candidate profile.

CANDIDATE PROFILE:
{CV_SUMMARY}

JOB POSTING:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Description: {job.get('description', '')}

Score how well this job fits the candidate on a scale of 1–10.
A 7+ means strong alignment: fintech/payments/product domain, matching seniority,
Singapore or remote location, and directly relevant skills.
Score below 7 for weak alignment: wrong domain, wrong seniority, or unrelated skills.

Reply with ONLY these two lines, nothing else:
SCORE: <number 1-10>
REASON: <one sentence explaining the match or mismatch>"""

    try:
        result = ask_claude(prompt)
        print(f"        Claude raw response: {repr(result[:100])}")
        score_match = re.search(r'SCORE:\s*(\d+)', result)
        reason_match = re.search(r'REASON:\s*(.+)', result)
        score = int(score_match.group(1)) if score_match else 0
        reason = reason_match.group(1).strip() if reason_match else "No reason parsed"
        return {**job, "score": score, "reason": reason}
    except Exception as e:
        print(f"        Scoring exception: {e}")
        return {**job, "score": 0, "reason": f"Scoring error: {e}"}


# Quick test
if __name__ == "__main__":
    result = ask_claude("Say hello and confirm you are working!")
    print(result)