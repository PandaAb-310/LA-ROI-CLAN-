from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import requests
from flask import Flask
from threading import Thread

# 1. SAFEGUARDED TOKENS (FETCHED FROM RENDER SECRETS)
# On Render, go to: Dashboard -> Environment -> Add Environment Variable
# Add 'BOT_TOKEN' and 'COC_TOKEN' there.
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
*Here’s what I can do:*
📜 /start – Start the bot  
🏰 /clan – Show clan information  
🏆 /members – Show top trophy earners
🎖️ /top – War Legends leaderboard
🎯 /donations – Donation leaderboard
⚔️ /war – Current war status
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def clan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    encoded_tag = CLAN_TAG.replace('#', '%23')
    claninfo = getinfo(f"clans/{encoded_tag}")

    if "error" in claninfo:
        await update.message.reply_text("⚠️ Sorry, I couldn't reach the village.")
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
    member_list = claninfo['memberList']
    members_sorted = sorted(member_list, key=lambda x: x['trophies'], reverse=True)
    topmembers = members_sorted[:10]

    text = "🏰 <b>Clan Leaderboard</b>\n"
    text += "━━━━━━━━━━━━━━━━━━\n\n"

    for i, memb in enumerate(topmembers, start=1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        text += f"{medal} <b>Mr. {memb['name']}</b>\n"
        text += f"🏆 Trophies: <code>{memb['trophies']}</code>\n"
        text += "━━━━━━━━━━━━━━━━━━\n"

    await update.message.reply_text(text, parse_mode="HTML")

async def war(update: Update, context: ContextTypes.DEFAULT_TYPE):
    warinfo = getinfo(f"clans/{CLAN_TAG.replace('#','%23')}/currentwar")

    if "error" in warinfo:
        await update.message.reply_text("⚠️ War information unavailable right now.")
        return

    if "clan" not in warinfo:
        await update.message.reply_text("⚠️ Your clan is currently not in war.")
        return

    text = f"""
⚔️ *WAR BATTLE REPORT*
━━━━━━━━━━━━━━━━━━

🏰 *Clan:* {warinfo['clan']['name']}
🛡 *Opponent:* {warinfo['opponent']['name']}

⭐ Stars: {warinfo['clan']['stars']} — {warinfo['opponent']['stars']}
💥 Destruction: {warinfo['clan']['destructionPercentage']}% — {warinfo['opponent']['destructionPercentage']}%

👥 War Size: {warinfo['teamSize']} vs {warinfo['teamSize']}
⏳ Status: {warinfo['state']}
"""
    await update.message.reply_text(text, parse_mode="Markdown")

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
        text += f"{medal} <code><b>Mr. {p['name'].upper()}</b></code>\n"
        text += f"⭐ War Stars: <code>{p['stars']}</code>\n"
        text += f"🏰 Town Hall {p['th']} | 🏆 {p['trophies']}\n"
        text += "──────────────────\n"

    await status_msg.delete()
    await update.message.reply_text(text, parse_mode='HTML')
    
async def donations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    claninfo = getinfo(f"clans/{CLAN_TAG.replace('#','%23')}")
    
    if 'error' in claninfo or 'memberList' not in claninfo:
        await update.message.reply_text("⚠️ <b>Service Unavailable:</b> Data sync failed.")
        return

    sorted_members = sorted(claninfo['memberList'], key=lambda x: x.get('donations', 0), reverse=True)
    top_10 = sorted_members[:10]

    text = "🎯 <b>LA ROI: DONATION ELITE</b>\n"
    text += "<i>Tracking active contributions for the season</i>\n"
    text += "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"

    for i, m in enumerate(top_10, start=1):
        rank = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f" {i} ")
        name = m.get('name', 'Unknown')
        sent = m.get('donations', 0)
        received = m.get('donationsReceived', 0)

        text += f"{rank}  <b>Mr. {name.upper()}</b>\n"
        text += f"<code>  ├─ GIVEN: {sent:<5} </code>\n"
        text += f"<code>  └─ RECVD: {received:<5} </code>\n\n"
	
    text += "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
    total_sent = sum(m.get('donations', 0) for m in claninfo['memberList'])
    text += f"📊 <b>CLAN TOTAL:</b> <code>{total_sent}</code>"
    await update.message.reply_text(text, parse_mode='HTML')
async def missed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    warinfo = getinfo(f"clans/{CLAN_TAG.replace('#','%23')}/currentwar")

    if "error" in warinfo or "state" not in warinfo:
        await update.message.reply_text("⚠️ <b>War data unavailable.</b>", parse_mode='HTML')
        return

    if warinfo['state'] == 'notInWar':
        await update.message.reply_text("🛡️ <b>LA ROI IS NOT IN WAR !!</b>", parse_mode='HTML')
        return

    missed_players = []
    for player in warinfo['clan']['members']:
        attacks_made = len(player.get('attacks', []))
        
        if attacks_made < 2:
            missed_players.append({
                'name': player['name'],
                'missed': 2 - attacks_made,
                'map_pos': player['mapPosition']
            })

    if not missed_players:
        await update.message.reply_text("✅ <b>Perfect War!</b> No missed attacks found.", parse_mode='HTML')
        return

    missed_players = sorted(missed_players, key=lambda x: x['map_pos'])

    text = "⚔️ <b>LA ROI: WAR DISCIPLINE</b>\n"
    text += "<i>Reviewing incomplete battle entries</i>\n"
    text += "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"

    for p in missed_players:
        text += f"⚠️  <b>Mr. {p['name'].upper()}</b>\n"
        text += f"<code>  ├─ POSITION: #{p['map_pos']} </code>\n"
        text += f"<code>  └─ MISSING:  {p['missed']} ATK </code>\n\n"

    text += "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>"

    await update.message.reply_text(text, parse_mode='HTML')
# 5. EXECUTION
if __name__ == "__main__":
    if not BOT_TOKEN or not COC_TOKEN:
        print("CRITICAL: TELEGRAM_TOKEN or COC_API missing in Render Environment!")
    else:
        keep_alive() 
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # All lines below are now perfectly aligned with 8 spaces
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("help", help_command))
        app_bot.add_handler(CommandHandler("clan", clan))
        app_bot.add_handler(CommandHandler("members", members))
        app_bot.add_handler(CommandHandler("war", war))
        app_bot.add_handler(CommandHandler("top", top))
        app_bot.add_handler(CommandHandler("donations", donations)) #
        app_bot.add_handler(CommandHandler("missed", missed))       # 
                 # 

        print("Bot is running...")
        app_bot.run_polling()
