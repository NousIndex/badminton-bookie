import os
import asyncio
import telegram
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

app = FastAPI()

TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("TELE_GROUP_CHAT_ID")

bot = telegram.Bot(token=TOKEN)

async def send_reminder():
    await bot.send_message(chat_id=CHAT_ID, text="📢 Weekend Reminder: Don't forget to relax!")

scheduler = BackgroundScheduler()
sg_timezone = timezone("Asia/Singapore")

scheduler.add_job(
    lambda: asyncio.run(send_reminder()),
    CronTrigger(day_of_week="mon,sat,sun", hour=19, minute=25, timezone=sg_timezone)
)

scheduler.start()

@app.get("/")
def home():
    return {"status": "Bot is running!"}

@app.get("/send_reminder")
async def manual_trigger():
    await send_reminder()
    return {"message": "Reminder sent!"}
