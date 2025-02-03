from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import asyncio
import os
from pytz import timezone

TOKEN = os.getenv("TELE_TOKEN")
GROUP_CHAT_ID = int(os.getenv("TELE_GROUP_CHAT_ID"))

# Create a scheduler
scheduler = BackgroundScheduler()
scheduler.start()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Use /remindme <time_in_minutes> <message> to set a reminder.")

async def remindme(update: Update, context: CallbackContext) -> None:
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text("Usage: /remindme <time_in_minutes> <message>")
        return
    
    try:
        minutes = int(args[0])
        reminder_text = " ".join(args[1:])
        remind_time = datetime.now() + timedelta(minutes=minutes)
        
        # Schedule the reminder using asyncio.run() to execute async function
        scheduler.add_job(
            lambda: asyncio.run(send_reminder(reminder_text)),
            'date',
            run_date=remind_time
        )
        
        await update.message.reply_text(f"Reminder set for {minutes} minutes: {reminder_text}")
    
    except ValueError:
        await update.message.reply_text("Invalid time format. Please enter time in minutes.")

async def send_reminder(message):
    """Sends a reminder to the group"""
    app = Application.builder().token(TOKEN).build()
    await app.bot.send_message(GROUP_CHAT_ID, f"⏰ Reminder: {message}")
    
sg_timezone = timezone("Asia/Singapore")

# Schedule recurring reminders every Saturday & Sunday at 10:00 AM
scheduler.add_job(
    lambda: asyncio.run(send_reminder("📢 Weekend Reminder: Don't forget to relax!")),
    'cron',
    day_of_week='mon,sat,sun',
    hour=19,
    minute=25,
    timezone=sg_timezone
)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remindme", remindme))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
