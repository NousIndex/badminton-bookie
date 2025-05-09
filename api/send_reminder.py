import os
import telegram
from telegram.ext import ContextTypes
from fastapi import FastAPI, Request
from pytz import timezone
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import hashlib
import base64
from typing import Dict
import time
from pymongo import MongoClient

app = FastAPI()

TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("TELE_GROUP_CHAT_ID")
CHAT_ID2 = os.getenv("TELE_GROUP_CHAT_ID2")
AUTH_KEY = os.getenv("AUTH_KEY_DECODER")
KEY_WORD = os.getenv("KEY_WORD")
MONGODB_URI = os.getenv("MONGODB")

client = MongoClient(MONGODB_URI)
db = client["BadmintonBookie"]
collection = db["DeleteMessages"]
collection2 = db["BookedCourts"]

sg_timezone = timezone("Asia/Singapore")

today_date = datetime.today()
bot = telegram.Bot(token=TOKEN)

now_sgt = datetime.now(sg_timezone)
future_date_plus1 = now_sgt + timedelta(days=1)
current_date_str = now_sgt.strftime("%Y-%m-%d")
future_date_plus1_str = future_date_plus1.strftime("%Y-%m-%d")


def unpad(s):
    return s[: -ord(s[-1])]


def save_message(chat_id: str, message_id: str):
    collection.insert_one(
        {
            "Date": future_date_plus1_str,
            "ChatId": str(chat_id),
            "MessageId": str(message_id),
        }
    )


async def delete_message_today():
    result = collection.find({"Date": current_date_str})
    for doc in result:
        print(doc)
        try:
            await bot.delete_message(chat_id=doc["ChatId"], message_id=doc["MessageId"])
            collection.delete_one(
                {"ChatId": doc["ChatId"], "MessageId": doc["MessageId"]}
            )
        except Exception as e:
            print(f"Failed to delete message: {e}")


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

    msg = await bot.send_message(
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
    save_message(msg.chat.id, msg.message_id)


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

    msg = await bot.send_message(
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
    save_message(msg.chat.id, msg.message_id)


def getLocationByTitle(title):
    if title == "SBH@Sims":
        return "https://maps.app.goo.gl/e7KPiqXSaXxaaLX69"
    elif title == "OBA Arena@Sprout Hub":
        return "https://maps.app.goo.gl/syLNgLojyv8dBWf48"
    elif title == "KFF Arena":
        return "https://maps.app.goo.gl/5UyCTGS2FnGryXeW6"
    elif title == "Delta Sports Hall":
        return "https://maps.app.goo.gl/m3XJfJu4ZNRZ5bhb7"
    elif title == "Stadium":
        return "https://maps.app.goo.gl/3eV9hyNuNThAyyLC8"
    else:
        return ""


def getMRTByTitle(title):
    if title == "SBH@Sims":
        return "Aljunied MRT"
    elif title == "OBA Arena@Sprout Hub":
        return "Redhill MRT"
    elif title == "KFF Arena":
        return "Aljunied MRT"
    elif title == "Delta Sports Hall":
        return "Redhill MRT"
    elif title == "Stadium":
        return "Stadium MRT"
    else:
        return ""


async def court_reminder_work(courtdate, location, timeslot, court):
    await bot.send_message(
        chat_id=CHAT_ID2,
        text="<b>Court Reminder For Tomorrow:</b> \n📍: "
        + location
        + "\n📅: "
        + courtdate
        + "\n⏰: "
        + timeslot
        + "\n🏸: Court "
        + court
        + "\n\n🗺️ : "
        + getLocationByTitle(location),
        parse_mode="HTML",
    )


async def court_place_poll_work(courtdate, location, timeslot):
    poll_message = await bot.send_poll(
        chat_id=CHAT_ID2,
        question="Badminton Session (Preferably 6-8 Pax)"
        + "\n📍: "
        + location
        + "("
        + getMRTByTitle(location)
        + ")\n📅: "
        + courtdate
        + " ("
        + timeslot
        + ")",
        options=["Attending", "Not Attending"],
        is_anonymous=False,
        allows_multiple_answers=False,
    )

    await bot.pin_chat_message(chat_id=CHAT_ID2, message_id=poll_message.message_id)


async def court_place(courtdate, location, timeslot, court):
    msg = await bot.send_message(
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
    save_message(msg.chat.id, msg.message_id)


@app.get("/")
def home():
    return {"status": "Bot is running!"}


@app.get("/send_reminder")
async def manual_trigger(request: Request):
    headers = dict(request.headers)
    # print(headers)
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
    # print(headers)
    try:
        if aes_decrypt(headers["auth_key"], AUTH_KEY) == KEY_WORD:
            await send_reminder2()
        else:
            print("FAILED")
    except:
        print("FAILED EXCEPT")
    return {"message": "Reminder sent!"}


@app.get("/delete_message_today")
async def manual_trigger3(request: Request):
    headers = dict(request.headers)
    # print(headers)
    try:
        if aes_decrypt(headers["auth_key"], AUTH_KEY) == KEY_WORD:
            await delete_message_today()
        else:
            print("FAILED")
    except:
        print("FAILED EXCEPT")
    return {"message": "Reminder sent!"}


@app.post("/send_reminder_court")
async def manual_trigger2(request: Request):
    headers = dict(request.headers)
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


@app.post("/send_reminder_court_work")
async def manual_trigger2(request: Request):
    headers = dict(request.headers)
    try:
        if aes_decrypt(headers["auth_key"], AUTH_KEY) == KEY_WORD:
            future_date = today_date + timedelta(days=1)
            future_date_str = future_date.strftime("%Y-%m-%d")
            future_date_str2 = future_date.strftime("%d-%m-%Y")
            results = list(collection2.find({"start": {"$regex": future_date_str}}))
            # Process data
            for doc in results:
                start_str = doc["start"]
                end_str = doc["end"]

                start_time = datetime.fromisoformat(start_str)
                end_time = datetime.fromisoformat(end_str)

                start_hour = start_time.strftime("%I").lstrip("0")
                end_hour = end_time.strftime("%I").lstrip("0")
                meridiem = end_time.strftime("%p").lower()

                # Combine into string
                time_range = f"{start_hour}-{end_hour}{meridiem}"
                await court_reminder_work(
                    future_date_str2,
                    doc["title"],
                    time_range,
                    doc["court_no"],
                )
        else:
            print("FAILED")
    except:
        print("FAILED EXCEPT")
    return {"message": "Reminder sent!"}


@app.post("/court_place_poll_work")
async def manual_trigger2(request: Request):
    headers = dict(request.headers)
    try:
        if aes_decrypt(headers["auth_key"], AUTH_KEY) == KEY_WORD:
            # await send_reminder()
            body: Dict = await request.json()  # Parse JSON body
            # Process data
            start_str = body["start"]
            end_str = body["end"]

            start_time = datetime.fromisoformat(start_str)
            end_time = datetime.fromisoformat(end_str)
            date_str = start_time.strftime("%d-%m-%Y")

            start_hour = start_time.strftime("%I").lstrip("0")
            end_hour = end_time.strftime("%I").lstrip("0")
            meridiem = end_time.strftime("%p").lower()

            # Combine into string
            time_range = f"{start_hour}-{end_hour}{meridiem}"
            await court_place_poll_work(
                date_str,
                body["location"],
                time_range,
            )
        else:
            print("FAILED")
    except:
        print("FAILED EXCEPT")
    return {"message": "Reminder sent!"}
