import logging
import requests
from flask import Flask, request as flask_request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
import os

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# تخزين الطلبات مؤقتًا داخل الذاكرة
REQUESTS_LOG = []

SERVICES = {
    "marketing": {
        "name": "📱 التسويق الإلكتروني",
        "services": {
            "m1": {"name": "صفحات تواصل احترافية", "price": "$50–100", "duration": "3–5 أيام"},
            "m2": {"name": "تصميم لوغو", "price": "$30–80", "duration": "2–3 أيام"},
            "m3": {"name": "تحرير مناشير", "price": "$20–50", "duration": "1–2 أيام"}
        }
    },
    "security": {
        "name": "🔒 الأمن السيبراني",
        "services": {
            "s1": {"name": "حماية المواقع", "price": "$300–600", "duration": "7–14 يوم"},
            "s2": {"name": "اختبار الاختراق", "price": "$400–800", "duration": "10–15 يوم"}
        }
    },
    "design": {
        "name": "💻 تصميم مواقع ويب",
        "services": {
            "d1": {"name": "مواقع متجاوبة", "price": "$200–500", "duration": "7–14 يوم"},
            "d2": {"name": "متاجر إلكترونية", "price": "$400–1000", "duration": "14–30 يوم"}
        }
    }
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت CSPDM ✅")

# أمر /services التفاعلي
async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 التسويق", callback_data="marketing")],
        [InlineKeyboardButton("🔒 الأمن السيبراني", callback_data="security")],
        [InlineKeyboardButton("💻 تصميم المواقع", callback_data="design")]
    ]
    await update.message.reply_text("اختر القسم:", reply_markup=InlineKeyboardMarkup(keyboard))

# عرض الخدمات مع زر طلب الخدمة
async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    section = SERVICES.get(category)
    if not section:
        await query.edit_message_text("القسم غير موجود.")
        return

    for code, service in section["services"].items():
        text = f"🔹 {service['name']}\n💰 السعر: {service['price']}\n⏱️ المدة: {service['duration']}"
        button = InlineKeyboardMarkup([[InlineKeyboardButton("📝 طلب الخدمة", callback_data=f"order|{category}|{code}")]])
        await query.message.reply_text(text, reply_markup=button)

# معالجة طلب الخدمة
async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, category, code = query.data.split("|")
    section = SERVICES.get(category)
    service = section["services"].get(code)
    username = query.from_user.username or "بدون اسم"

    REQUESTS_LOG.append({
        "user": username,
        "service": service["name"],
        "category": section["name"],
        "price": service["price"]
    })

    # إشعار داخلي (يمكن تغييره ليصل إلى مسؤول)
    await query.message.reply_text(f"✅ تم تسجيل طلبك: {service['name']}")

# أمر /dashboard لعرض الطلبات
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not REQUESTS_LOG:
        await update.message.reply_text("لا توجد طلبات حتى الآن.")
        return

    text = "📋 الطلبات المسجلة:\n\n"
    for req in REQUESTS_LOG:
        text += f"👤 {req['user']}\n🔹 {req['service']}\n📂 {req['category']}\n💰 {req['price']}\n\n"
    await update.message.reply_text(text)

# إعداد التطبيق
application = Application.builder().token(BOT_TOKEN).request(HTTPXRequest()).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("services", services_command))
application.add_handler(CommandHandler("dashboard", dashboard))
application.add_handler(CallbackQueryHandler(show_services, pattern="^(marketing|security|design)$"))
application.add_handler(CallbackQueryHandler(handle_order, pattern="^order\|"))

# استقبال التحديثات من Telegram
@app.route("/", methods=["POST"])
def root():
    data = flask_request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put(update)
    return "", 200

# تسجيل Webhook
requests.get(f"https://api.telegram.org/bot{7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o}/setWebhook?url={https://cspdm-zvoq.onrender.com}")
