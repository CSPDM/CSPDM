import logging
import requests
from flask import Flask, request as flask_request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# إعداد Flask
app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# بيانات الخدمات
SERVICES = {
    "marketing": {
        "name": "📱 التسويق الإلكتروني",
        "services": {
            "m1": {"name": "صفحات تواصل احترافية", "price": "$50–100", "duration": "3–5 أيام"},
            "m2": {"name": "تصميم لوغو", "price": "$30–80", "duration": "2–3 أيام"},
            "m3": {"name": "تحرير مناشير", "price": "$20–50", "duration": "1–2 أيام"},
            "m4": {"name": "دراسة العملاء", "price": "$100–200", "duration": "5–7 أيام"},
            "m5": {"name": "تقييم الصفحات", "price": "$80–150", "duration": "3–4 أيام"},
            "m6": {"name": "فيديوهات قصيرة", "price": "$40–100", "duration": "2–4 أيام"},
            "m7": {"name": "حملات إعلانية", "price": "$200–500", "duration": "شهري"},
            "m8": {"name": "بوتات رد تلقائي", "price": "$150–300", "duration": "5–10 أيام"},
            "m9": {"name": "تحليل المحتوى", "price": "$120–250", "duration": "4–6 أيام"},
            "m10": {"name": "استشارات لاحقة", "price": "$50–100", "duration": "شهري"}
        }
    },
    "security": {
        "name": "🔒 الأمن السيبراني",
        "services": {
            "s1": {"name": "حماية المواقع", "price": "$300–600", "duration": "7–14 يوم"},
            "s2": {"name": "اختبار الاختراق", "price": "$400–800", "duration": "10–15 يوم"},
            "s3": {"name": "مراقبة الشبكات", "price": "$200–400", "duration": "شهري"},
            "s4": {"name": "استشارات أمنية", "price": "$100–250", "duration": "حسب الطلب"},
            "s5": {"name": "تدريب الموظفين", "price": "$150–300", "duration": "3–5 أيام"}
        }
    },
    "design": {
        "name": "💻 تصميم مواقع ويب",
        "services": {
            "d1": {"name": "مواقع متجاوبة", "price": "$200–500", "duration": "7–14 يوم"},
            "d2": {"name": "متاجر إلكترونية", "price": "$400–1000", "duration": "14–30 يوم"},
            "d3": {"name": "مواقع شركات", "price": "$300–700", "duration": "10–20 يوم"},
            "d4": {"name": "تطبيقات ويب", "price": "$500–1500", "duration": "20–40 يوم"},
            "d5": {"name": "صيانة المواقع", "price": "$100–300", "duration": "حسب الطلب"}
        }
    }
}

# إعداد التوكن والرابط
BOT_TOKEN = os.getenv("7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o")
WEBHOOK_URL = os.getenv("https://cspdm-zvoq.onrender.com")

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت CSPDM ✅")

async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("استخدم الأمر هكذا:\n`/filter marketing 100`", parse_mode="Markdown")
        return
    category = args[0].lower()
    try:
        max_price = int(args[1])
    except ValueError:
        await update.message.reply_text("يرجى تحديد السعر كرقم صحيح.")
        return
    section = SERVICES.get(category)
    if not section:
        await update.message.reply_text(f"القسم '{category}' غير موجود.")
        return
    results = []
    for code, service in section["services"].items():
        price_range = service["price"].replace("$", "").replace("–", "-").split("-")
        try:
            max_price_val = int(price_range[-1])
        except ValueError:
            continue
        if max_price_val <= max_price:
            results.append(f"🔹 {service['name']}\n💰 السعر: {service['price']}\n⏱️ المدة: {service['duration']}")
    await update.message.reply_text("\n\n".join(results) if results else "لا توجد خدمات ضمن هذا السعر.")

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 التسويق", callback_data="marketing")],
        [InlineKeyboardButton("🔒 الأمن السيبراني", callback_data="security")],
        [InlineKeyboardButton("💻 تصميم المواقع", callback_data="design")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر القسم:", reply_markup=reply_markup)

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    section = SERVICES.get(category)
    if not section:
        await query.edit_message_text("القسم غير موجود.")
        return
    services_text = f"{section['name']}\n\n"
    for code, service in section["services"].items():
        services_text += f"🔹 {service['name']}\n💰 السعر: {service['price']}\n⏱️ المدة: {service['duration']}\n\n"
        log_request(query.from_user.username or "بدون اسم", service["name"], section["name"], service["price"])
    await query.edit_message_text(services_text)

# إنشاء التطبيق
application = Application.builder().token(BOT_TOKEN).request(HTTPXRequest()).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("filter", filter_command))
application.add_handler(CommandHandler("services", services_command))
application.add_handler(CallbackQueryHandler(show_services))

# استقبال التحديثات من Telegram
@app.route("/", methods=["POST"])
def root():
    data = flask_request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put(update)
    return "", 200

# تسجيل Webhook
requests.get(f"https://api.telegram.org/bot{7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o}/setWebhook?url={https://cspdm-zvoq.onrender.com}")
