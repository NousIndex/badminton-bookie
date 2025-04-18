import os
import telegram
from fastapi import FastAPI, Request
from pytz import timezone
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import hashlib
import base64
from typing import Dict
import time

app = FastAPI()

TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("TELE_GROUP_CHAT_ID")
CHAT_ID2 = os.getenv("TELE_GROUP_CHAT_ID2")
AUTH_KEY = os.getenv("AUTH_KEY_DECODER")
KEY_WORD = os.getenv("KEY_WORD")

today_date = datetime.today()
bot = telegram.Bot(token=TOKEN)

sg_timezone = timezone("Asia/Singapore")


def unpad(s):
    return s[: -ord(s[-1])]


def aes_decrypt(encrypted_text, key):
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_text = cipher.decrypt(base64.b64decode(encrypted_text)).decode()
    return unpad(decrypted_text)


async def send_reminder():
    future_date = today_date + timedelta(days=14)

    # Step 3: Set the correct time (3 PM and 4 PM SGT)
    future_date_3pm = sg_timezone.localize(
        future_date.replace(hour=15, minute=0, second=0)
    )
    future_date_4pm = sg_timezone.localize(
        future_date.replace(hour=16, minute=0, second=0)
    )

    # Step 4: Convert to Unix timestamps (seconds)
    timestamp_3pm = int(future_date_3pm.timestamp()) * 1000
    timestamp_4pm = int(future_date_4pm.timestamp()) * 1000

    await bot.send_message(
        chat_id=CHAT_ID,
        text="Ballot Reminder:\nhttps://activesg.gov.sg/venues/WYfbYK8b8mvlTx7iiCIJp/activities/YLONatwvqJfikKOmB5N9U/review/ballot"
        + "?timeslot="
        + str(timestamp_3pm)
        + "&timeslot="
        + str(timestamp_4pm),
        # text="Ballot Reminder:\nhttps://activesg.gov.sg/venues/WYfbYK8b8mvlTx7iiCIJp/activities/YLONatwvqJfikKOmB5N9U/timeslots?date="
        # + future_date_str
        # + "&timeslots="
        # + str(timestamp_3pm)
        # + "&timeslots="
        # + str(timestamp_4pm),
        disable_notification=True,
    )

async def send_reminder2():
    future_date = today_date + timedelta(days=14)

    # Step 3: Set the correct time (3 PM and 4 PM SGT)
    future_date_8pm = sg_timezone.localize(
        future_date.replace(hour=20, minute=0, second=0)
    )
    future_date_9pm = sg_timezone.localize(
        future_date.replace(hour=21, minute=0, second=0)
    )

    # Step 4: Convert to Unix timestamps (seconds)
    timestamp_8pm = int(future_date_8pm.timestamp()) * 1000
    timestamp_9pm = int(future_date_9pm.timestamp()) * 1000

    await bot.send_message(
        chat_id=CHAT_ID2,
        text="Ballot Reminder:\nhttps://activesg.gov.sg/venues/a3jznoZlsfyJrl43Tbnog/activities/YLONatwvqJfikKOmB5N9U/review/ballot"
        + "?timeslot="
        + str(timestamp_8pm)
        + "&timeslot="
        + str(timestamp_9pm),
        # text="Ballot Reminder:\nhttps://activesg.gov.sg/venues/a3jznoZlsfyJrl43Tbnog/activities/YLONatwvqJfikKOmB5N9U/timeslots?date="
        # + future_date_str
        # + "&timeslots="
        # + str(timestamp_3pm)
        # + "&timeslots="
        # + str(timestamp_4pm),
        disable_notification=True,
    )

async def court_place(courtdate, location, timeslot, court):
    await bot.send_message(
        chat_id=CHAT_ID,
        text="Court Reminder For Tomorrow:\n📍: "
        + location
        + "\n📅: "
        + courtdate
        + "\n⏰: "
        + timeslot
        + "\n🏸: Court "
        + court,
        disable_notification=True,
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
    except:
        print("FAILED EXCEPT")
    return {"message": "Reminder sent!"}

@app.get("/send_reminder_work")
async def manual_trigger(request: Request):
    headers = dict(request.headers)
    print(headers)
    try:
        if aes_decrypt(headers["auth_key"], AUTH_KEY) == KEY_WORD:
            await send_reminder2()
        else:
            print("FAILED")
    except:
        print("FAILED EXCEPT")
    return {"message": "Reminder sent!"}


@app.post("/send_reminder_court")
async def manual_trigger2(request: Request):
    headers = dict(request.headers)
    print(headers)
    try:
        if aes_decrypt(headers["auth_key"], AUTH_KEY) == KEY_WORD:
            # await send_reminder()
            body: Dict = await request.json()  # Parse JSON body

            future_date = today_date + timedelta(days=1)
            future_date_str = future_date.strftime("%-d/%-m")
            future_date_str2 = future_date.strftime("%d-%m-%Y")
            print(future_date_str)
            # Process data
            for date, details in body.items():
                if date == future_date_str:
                    await court_place(
                        future_date_str2,
                        details["location"],
                        details["timeslot"],
                        details["court"],
                    )
        else:
            print("FAILED")
    except:
        print("FAILED EXCEPT")
    return {"message": "Reminder sent!"}
