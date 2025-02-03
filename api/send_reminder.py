import os
import asyncio
import telegram
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime, timedelta

app = FastAPI()

TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("TELE_GROUP_CHAT_ID")
today_date = datetime.today().strftime("%Y-%m-%d")

# Add 14 days
future_date = today_date + timedelta(days=14)

# Format the future date as "YYYY-MM-DD"
future_date_str = future_date.strftime('%Y-%m-%d')

bot = telegram.Bot(token=TOKEN)

scheduler = BackgroundScheduler()
scheduler.start()
sg_timezone = timezone("Asia/Singapore")


async def send_reminder():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="Ballot Reminder:\nhttps://activesg.gov.sg/venues/WYfbYK8b8mvlTx7iiCIJp/activities/YLONatwvqJfikKOmB5N9U/timeslots?date="
        + future_date_str,
        disable_notification=True,
    )


scheduler.add_job(
    lambda: asyncio.run(send_reminder()),
    CronTrigger(day_of_week="mon,sat,sun", hour=20, minute=0, timezone=sg_timezone),
)


@app.get("/")
def home():
    return {"status": "Bot is running!"}


@app.get("/send_reminder")
async def manual_trigger():
    await send_reminder()
    return {"message": "Reminder sent!"}
