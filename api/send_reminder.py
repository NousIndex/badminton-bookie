import os
import asyncio
import telegram
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import hashlib
import base64
import time

app = FastAPI()

TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("TELE_GROUP_CHAT_ID")
AUTH_KEY = os.getenv("AUTH_KEY_DECODER")
KEY_WORD = os.getenv("KEY_WORD")

today_date = datetime.today()
future_date = today_date + timedelta(days=14)
future_date_str = future_date.strftime("%Y-%m-%d")

bot = telegram.Bot(token=TOKEN)

scheduler = BackgroundScheduler()
scheduler.start()
sg_timezone = timezone("Asia/Singapore")

timestamp_3pm = int(
    time.mktime(future_date.replace(hour=15, minute=0, second=0).timetuple())
)
timestamp_4pm = int(
    time.mktime(future_date.replace(hour=16, minute=0, second=0).timetuple())
)


def unpad(s):
    return s[: -ord(s[-1])]


def aes_decrypt(encrypted_text, key):
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_text = cipher.decrypt(base64.b64decode(encrypted_text)).decode()
    return unpad(decrypted_text)


async def send_reminder():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="Ballot Reminder:\nhttps://activesg.gov.sg/venues/WYfbYK8b8mvlTx7iiCIJp/activities/YLONatwvqJfikKOmB5N9U/timeslots?date="
        + future_date_str
        + "&timeslots="
        + str(timestamp_3pm)
        + "&timeslots="
        + str(timestamp_4pm),
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
async def manual_trigger(request: Request):
    headers = dict(request.headers)
    print(headers)
    try:
        if aes_decrypt(headers["auth_key"], AUTH_KEY) == KEY_WORD:
            await send_reminder()
        else:
            print("FAILED")
            pass
    except:
        print("FAILED EXCEPT")
        pass
    return {"message": "Reminder sent!"}
