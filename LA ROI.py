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

    if "error" in claninfo:
        await update.message.reply_text(f"❌ Error: {claninfo.get('reason')}")
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
    
    if "error" in claninfo or "memberList" not in claninfo:
        await update.message.reply_text("⚠️ Could not fetch member list.")
        return

    members_list = claninfo['memberList']
    members_sorted = sorted(members_list, key=lambda x: x.get('trophies', 0), reverse=True)
    topmembers = members_sorted[:10]

    LRE, PDF = "\u202A", "\u202C"
    text = "🏰 <b>Clan Leaderboard</b>\n━━━━━━━━━━━━━━━━━━\n\n"

    for i, memb in enumerate(topmembers, start=1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        name = f"{LRE}{memb['name']}{PDF}"
        text += f"{medal} <b>{name}</b>\n🏆 Trophies: <code>{memb.get('trophies', 0)}</code>\n━━━━━━━━━━━━━━━━━━\n"

    await update.message.reply_text(text, parse_mode="HTML")

async def war(update: Update, context: ContextTypes.DEFAULT_TYPE):
    warinfo = getinfo(f"clans/{CLAN_TAG.replace('#','%23')}/currentwar")

    if "error" in warinfo or "clan" not in warinfo:
        await update.message.reply_text("⚠️ War information unavailable or Clan not in war.")
        return

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
    await update.message.reply_text(text, parse_mode='HTML')
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔎 <i>Consulting the War Archives...</i>", parse_mode='HTML')
    
    Elites = []
    ELITE_TAGS = ["#P0VQQ8CJ0", "#PVQPQY0P9", "#GPY00V9LG", "#90V9UUCLL", "#9JGY9Q98"]
    
    for playertag in ELITE_TAGS: 
        playerinfo = getinfo(f"players/{playertag.replace('#','%23')}")
        
        if 'error' not in playerinfo:
            Elites.append({
                'name': playerinfo.get('name', "Unknown"),
                'th': playerinfo.get('townHallLevel', 0), 
                'trophies': playerinfo.get('trophies', 0),
                'stars': playerinfo.get('warStars', 0)
            })

    
    sortedlist = sorted(Elites, key=lambda x: x['stars'], reverse=True)
    
    text = "🎖️ <b>LA ROI: WAR LEGENDS</b> 🎖️\n"
    text += "━━━━━━━━━━━━━━━━━━\n\n"

    for i, p in enumerate(sortedlist, start=1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "🎖️")
        
        # We use <code> to force Monospace font which helps alignment
        # We also keep the LRE/PDF shield just in case
        safe_name = f"\u202A{p['name'].upper()}\u202C"
        
        text += f"{medal} <code><b>{safe_name}</b></code>\n"
        text += f"⭐ War Stars: <code>{p['stars']}</code>\n"
        text += f"🏰 Town Hall {p['th']} | 🏆 {p['trophies']}\n"
        text += "──────────────────\n"

    await status_msg.delete()
    await update.message.reply_text(text, parse_mode='HTML')

	
# 5. EXECUTION
if __name__ == "__main__":
    if not BOT_TOKEN or not COC_TOKEN:
        print("CRITICAL: Tokens missing!")
    else:
        keep_alive()
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("help", help_command))
        app_bot.add_handler(CommandHandler("clan", clan))
        app_bot.add_handler(CommandHandler("members", members))
        app_bot.add_handler(CommandHandler("war", war))
        app_bot.add_handler(CommandHandler("top", top))
        
        print("Bot is running...")
        app_bot.run_polling()
    
