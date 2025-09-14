from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o"

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Bot is running ✅", 200
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "ok", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً أحمد! البوت شغّال ✅")

application.add_handler(CommandHandler("start", start))

import asyncio
import requests

if __name__ == "__main__":
    asyncio.run(application.initialize())
    requests.get(f"https://api.telegram.org/bot7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o/setWebhook?url=https://cspdm.onrender.com/")
    app.run(host="0.0.0.0", port=5000)





