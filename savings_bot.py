import logging
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Your Bot Token
TOKEN = "9223210771:AAFTfLMRiewNa8nvp-k1pyIDa_yUl66eDTo"

# 2. Paste your copied Chat ID here
MY_CHAT_ID = 123456789 

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Persistent data parameters
START_DATE = datetime.date(2026, 10, 26)  # Started October 26, 2026
DAILY_GOAL = 1.0                           # $1 per day Target

# In-memory storage for tracking deposits
user_savings = {"balance": 0.0, "last_deposit_date": None}

def get_journey_status():
    """Calculates progress, streaks, and current cycles dynamically."""
    today = datetime.date.today()
    
    # Calculate days since your start date
    days_since_start = (today - START_DATE).days
    
    # Logic to find which 1-month cycle we are currently in
    # (Cycles dynamically auto-reset every 30 days)
    cycle_number = (days_since_start // 30) + 1
    day_of_cycle = (days_since_start % 30) + 1
    
    return cycle_number, day_of_cycle

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cycle, day = get_journey_status()
    await update.message.reply_text(
        f"👋 Welcome back to your Automated $1/Day Savings Journey!\n\n"
        f"🗓️ Today is **Day {day}** of Cycle {cycle}.\n"
        f"🎯 Target: Save $1.00 today.\n\n"
        f"Commands:\n"
        f"/status - Check your target, current cycle balance, and progress.\n"
        f"To log your savings, just type a number!"
    )

# Command: /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cycle, day = get_journey_status()
    expected_saved = day * DAILY_GOAL
    
    msg = (
        f"📊 **Savings Journey Status**\n"
        f"─────────────────────\n"
        f"🔄 **Current Cycle:** Month {cycle}\n"
        f"📅 **Cycle Progress:** Day {day} of 30\n"
        f"💰 **Total Balance Saved:** ${user_savings['balance']:.2f}\n"
        f"🎯 **Target Balance for Day {day}:** ${expected_saved:.2f}\n"
        f"🏁 **Goal at End of Month:** $30.00\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# Message Handler: Process savings inputs
async def handle_savings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        amount = float(text)
        if amount <= 0:
            await update.message.reply_text("Please enter an amount greater than 0! ❌")
            return
            
        user_savings["balance"] += amount
        user_savings["last_deposit_date"] = datetime.date.today()
        cycle, day = get_journey_status()
        
        await update.message.reply_text(
            f"✅ Logged ${amount:.2f} successfully!\n"
            f"📈 Cycle Month {cycle} Balance: ${user_savings['balance']:.2f}\n"
            f"💪 Keep it up on Day {day}!"
        )
    except ValueError:
        await update.message.reply_text("🤖 Just send me a plain number to log your savings!")

# Reminder hook function
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    cycle, day = get_journey_status()
    await context.bot.send_message(
        chat_id=MY_CHAT_ID, 
        text=f"⏰ **Savings Nudge!** (Day {day}/30)\n\nDon't forget to put aside your $1 today to keep your streak alive! Reply with your saved amount below. 🚀"
    )

def main():
    app = Application.builder().token(TOKEN).build()

    # Routes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_savings))

    # Reminder 1: Morning nudge at 09:00 AM Local Time
    app.job_queue.run_daily(
        send_reminder, 
        time=datetime.time(hour=9, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=3))) # EAT (UTC+3)
    )

    # Reminder 2: Evening nudge at 05:00 PM (17:00) Local Time
    app.job_queue.run_daily(
        send_reminder, 
        time=datetime.time(hour=17, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=3))) # EAT (UTC+3)
    )

    print("Bot configured successfully. Running reminders at 9:00 AM and 5:00 PM EAT...")
    app.run_polling()

if __name__ == '__main__':
    main()
