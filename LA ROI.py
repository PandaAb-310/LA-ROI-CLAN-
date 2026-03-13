from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import requests
from flask import Flask
from threading import Thread

# 1. SAFEGUARDED TOKENS
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
    url = f"https://cocproxy.royaleapi.dev/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {COC_TOKEN}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Safety: Check if we got a successful response (Status 200)
        if response.status_code == 200:
            return response.json()
        else:
            # Return the error code so we know what went wrong
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
    # Kept exactly as you requested to help you remember!
    help_text = """
🏰 *Clan Bot Commands*

📌 /start – Start the bot  
📊 /clan – Clan information  
👥 /members – Top clan members  
🏆 /top – Top players  
🎯 /donations – Donation leaderboard  
⚔️ /war – Current war status  
🚨 /missed – Missed war attacks  
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def clan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    encoded_tag = CLAN_TAG.replace('#', '%23')
    claninfo = getinfo(f"clans/{encoded_tag}")

    # Safety: Check if claninfo is actually the data or an error
    if "error" in claninfo:
        await update.message.reply_text(f"❌ Error: {claninfo.get('reason')}")
        return

    text = f"""
🏰 *Clan Information*
*Name:* {claninfo.get('name', 'N/A')}
*Tag:* {CLAN_TAG}
*Level:* {claninfo.get('clanLevel', 'N/A')}
👥 *Members:* {claninfo.get('members', '0')}/50
📝 *Description:* {claninfo.get('description', 'No description set.')}
"""
    await update.message.reply_text(text, parse_mode="Markdown")

async def war(update: Update, context: ContextTypes.DEFAULT_TYPE):
    encoded_tag = CLAN_TAG.replace('#', '%23')
    warinfo = getinfo(f"clans/{encoded_tag}/currentwar")

    # Safety: Ensure the war data exists before trying to read it
    if "error" in warinfo:
        await update.message.reply_text("⚠️ War information unavailable (Check if War Log is Public).")
        return
    
    # Safety: Handle the case where the clan is NOT in a war
    if "state" not in warinfo or warinfo['state'] == 'notInWar':
        await update.message.reply_text("💤 The clan is not currently in a war.")
        return

    text = f"""
⚔️ *WAR BATTLE REPORT*
🏰 *Clan:* {warinfo['clan']['name']}
🛡 *Opponent:* {warinfo['opponent']['name']}
⭐ Stars: {warinfo['clan']['stars']} — {warinfo['opponent']['stars']}
⏳ Status: {warinfo['state'].upper()}
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# 5. EXECUTION
if __name__ == "__main__":
    if not BOT_TOKEN or not COC_TOKEN:
        print("CRITICAL: Tokens missing!")
    else:
        keep_alive()
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Adding your handlers
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("help", help_command))
        app_bot.add_handler(CommandHandler("clan", clan))
        app_bot.add_handler(CommandHandler("war", war))
        
        print("Bot is running...")
        app_bot.run_polling()
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
async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):

    claninfo = getinfo(f"clans/{CLAN_TAG.replace('#','%23')}")

    members = claninfo['memberList']

    # Sort by trophies (highest first)
    members_sorted = sorted(members, key=lambda x: x['trophies'], reverse=True)

    topmembers = members_sorted[:10]

    # Direction control characters
    LRE = "\u202A"
    PDF = "\u202C"

    text = "🏰 <b>Clan Leaderboard</b>\n"
    text += "━━━━━━━━━━━━━━━━━━\n\n"

    for i, memb in enumerate(topmembers, start=1):

        # Medal system
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."

        # Force left-to-right for name
        name = f"{LRE}{memb['name']}{PDF}"

        text += f"{medal} <b>{name}</b>\n"
        text += f"🏆 Trophies: <code>{memb['trophies']}</code>\n"
        text += "━━━━━━━━━━━━━━━━━━\n"

    await update.message.reply_text(text, parse_mode="HTML")
async def war(update: Update, context: ContextTypes.DEFAULT_TYPE):
    warinfo = getinfo(f"clans/{CLAN_TAG.replace('#','%23')}/currentwar")
    text = f"""
⚔️ <b>WAR BATTLE REPORT</b>
━━━━━━━━━━━━━━━━━━
🛡️ <b>DEFENDER:</b> {warinfo['clan']['name']}
🏹 <b>OPPONENT:</b> {warinfo['opponent']['name']}

📊 <b>SCOREBOARD</b>
{warinfo['clan']['stars']} ⭐ <b>VS</b> ⭐ {warinfo['opponent']['stars']}

💥 <b>DESTRUCTION</b>
└ {warinfo['clan']['destructionPercentage']}% 🟥🟥⬜⬜ {warinfo['opponent']['destructionPercentage']}%

⏳ <b>STATUS:</b> <code>{warinfo['state'].upper()}</code>
👥 <b>SIZE:</b> {warinfo['teamSize']} vs {warinfo['teamSize']}
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text,parse_mode='html')
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
        app_bot.add_handler(CommandHandler("members", members))
        app_bot.add_handler(CommandHandler("war", war))
        

        print("Bot is running...")
        app_bot.run_polling()
