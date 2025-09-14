from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import requests

# إعداد البوت
BOT_TOKEN = "7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o"
application = ApplicationBuilder().token(BOT_TOKEN).build()

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً أحمد! البوت شغّال ✅")

application.add_handler(CommandHandler("start", start))

# إعداد Flask
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Bot is running ✅", 200
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "ok", 200

# تشغيل التطبيق
if __name__ == "__main__":
    asyncio.run(application.initialize())
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://cspdm-zvoq.onrender.com/")
    app.run(host="0.0.0.0", port=5000)
