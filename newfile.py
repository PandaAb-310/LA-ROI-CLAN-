from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv(".env")
Token = os.getenv("BOT_TOKEN")

print("Loaded token:", Token)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userid = update.effective_user
    await update.message.reply_text(f"Hey there! {userid.first_name}👋\nI’m your Clash of Clans helper bot! 🏰⚔️\n\nI can give you information about LA ROI, players, and more.\nTry sending /help to see what I can do!"
    )
    with open('user_id.txt','r')as r:
    	txt = r.read()
    if str(userid.id) not in txt:
	    with open('user_id.txt','a') as f:
	    	users = f.write(str(userid.id)+ '\n')
	    	print(userid.id)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "*Here’s what I can do for you:*\n📜 /start – Say hi and get started\n🏰 /clan – Get info about your clan\n👤 /player – Check stats for a player\n⚔️ /war – Show current war status\n🎯 /donations – Check clan donations\n🕒 /nextwar – See when the next war starts\n\nJust type any command and I’ll fetch the info for you!"
    await update.message.reply_text(help_text, parse_mode='Markdown')

app = ApplicationBuilder().token(Token).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help))
app.run_polling()