from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import requests
from flask import Flask
from threading import Thread

# 1. SAFEGUARDED TOKENS
# These fetch from Render's Environment Variables
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
COC_TOKEN = os.environ.get('COC_API_KEY')
CLAN_TAG = "#2GGRVV2YJ"

# 2. FLASK KEEP-ALIVE SERVER
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# 3. HELPER FUNCTIONS
def getinfo(endpoint):
    # Fixed URL for CoC Proxy
    url = f"https://cocproxy.royaleapi.dev/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {COC_TOKEN}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Check if the response is actually JSON
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": True, "reason": f"Status {response.status_code}"}
    except Exception as e:
        return {"error": True, "reason": str(e)}

# 4. COMMAND HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hey there {user.first_name}! 👋\n\n"
        "I’m your Clash of Clans helper bot 🏰⚔️\n"
        "Use /help to see what I can do!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
*Here’s what I can do:*
📜 /start – Start the bot  
🏰 /clan – Show clan information  
👤 /player – Player stats (soon)
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def clan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Properly encoding the tag
    encoded_tag = CLAN_TAG.replace('#', '%23')
    claninfo = getinfo(f"clans/{encoded_tag}")

    # Check for the errors we managed in getinfo()
    if "error" in claninfo or "reason" in claninfo:
        await update.message.reply_text("⚠️ Sorry, I couldn't reach the village. Check the proxy or API key.")
        return

    text = f"""
🏰 *Clan Information*
*Name:* {claninfo.get('name', 'N/A')}
*Tag:* {CLAN_TAG}
*Level:* {claninfo.get('clanLevel', 'N/A')}

👥 *Members:* {claninfo.get('members', '0')}/50
🎯 *Required Trophies:* {claninfo.get('requiredTrophies', 'N/A')}

📝 *Description:* {claninfo.get('description', 'No description set.')}
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# 5. EXECUTION
if __name__ == "__main__":
    if not BOT_TOKEN or not COC_TOKEN:
        print("CRITICAL: Tokens missing in Environment Variables!")
    else:
        keep_alive() # Starts the Flask server for UptimeRobot
        
        # Build and run the Telegram bot
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("help", help_command))
        app_bot.add_handler(CommandHandler("clan", clan))

        print("Bot is running...")
        app_bot.run_polling()
