import os
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
MAX_MSG_LENGTH = 4096
NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def send_telegram_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env")
        return False
    try:
        response = requests.post(TELEGRAM_API_URL, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        })
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Telegram send failed: {e}")
        return False


def format_job_block(job: dict, index: int) -> str:
    emoji = NUMBER_EMOJIS[index] if index < len(NUMBER_EMOJIS) else f"{index + 1}."
    score = job.get("score", 0)
    url = job.get("job_url", "")
    lines = [
        f"{emoji} *{job.get('title', '')}* @ {job.get('company', '')}",
        f"📍 {job.get('location', '')}",
        f"🏅 {'⭐️' * score} {score}/10",
        f"💡 _{job.get('reason', '')}_",
    ]
    if url and url != "nan":
        lines.append(f"🔗 {url}")
    return "\n".join(lines)


def send_daily_digest(jobs: list) -> None:
    today = date.today().strftime("%B %d, %Y")

    if not jobs:
        send_telegram_message(f"*Job Hunt — {today}*\n\nNo new matching jobs today. Keep going! 🎯")
        return

    header = f"*Job Hunt — {today}*\n*{len(jobs)} match{'es' if len(jobs) != 1 else ''} found* 🔍\n"
    footer = "\nHappy hunting! 🎯"
    current_chunk = header
    chunks = []

    for i, job in enumerate(jobs):
        block = "\n\n" + format_job_block(job, i)
        if len(current_chunk) + len(block) + len(footer) > MAX_MSG_LENGTH:
            chunks.append(current_chunk + footer)
            current_chunk = f"*Job Hunt — {today} (cont.)*"
        current_chunk += block

    chunks.append(current_chunk + footer)

    for chunk in chunks:
        send_telegram_message(chunk)
