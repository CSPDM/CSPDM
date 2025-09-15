import logging
import requests
from flask import Flask, request as flask_request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

# إعداد Flask
app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إعداد التوكن والرابط
BOT_TOKEN = "7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o"
WEBHOOK_URL = "https://cspdm-zvoq.onrender.com"

# تعريف دالة الرد على /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت CSPDM ✅")

# إنشاء التطبيق
application = Application.builder().token(BOT_TOKEN).request(HTTPXRequest()).build()
application.add_handler(CommandHandler("start", start))

# تشغيل البوت
application.run_polling(stop_signals=None)  # ← هذا ضروري لتشغيل الـ update_queue

# تعريف مسار استقبال التحديثات من Telegram
@app.route("/", methods=["GET", "HEAD", "POST"])
def root():
    if flask_request.method == "POST":
        data = flask_request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.update_queue.put(update)
        return "", 200
    return "OK", 200

# تسجيل الـ Webhook
requests.get(f"https://api.telegram.org/bot{BO7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73oT_TOKEN}/setWebhook?url={https://cspdm-zvoq.onrender.com}")
