import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request, jsonify

# تكوين التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# متغيرات البيئة
# استخدم os.environ.get() بدلاً من os.getenv() للوصول المباشر إلى المتغيرات
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", "8000"))

# قاعدة البيانات للخدمات والأسعار
SERVICES = {
    "marketing": {
        "name": "📱 التسويق الإلكتروني",
        "services": {
            "m1": {"name": "إنشاء صفحات تواصل احترافية", "price": "50-100$", "duration": "3-5 أيام"},
            "m2": {"name": "تصميم لوغو احترافي", "price": "30-80$", "duration": "2-3 أيام"},
            "m3": {"name": "كتابة وتحرير مناشير", "price": "20-50$", "duration": "1-2 أيام"},
            "m4": {"name": "دراسة حالة العملاء", "price": "100-200$", "duration": "5-7 أيام"},
            "m5": {"name": "تقييم الصفحات وطرق التطوير", "price": "80-150$", "duration": "3-4 أيام"},
            "m6": {"name": "تصميم فيديوهات قصيرة", "price": "40-100$", "duration": "2-4 أيام"},
            "m7": {"name": "حملات إعلانية على السوشيال ميديا", "price": "200-500$", "duration": "شهري"},
            "m8": {"name": "تصميم بوتات رد تلقائي", "price": "150-300$", "duration": "5-10 أيام"},
            "m9": {"name": "دراسة المحتوى لزيادة التفاعل", "price": "120-250$", "duration": "4-6 أيام"},
            "m10": {"name": "استشارات دائمة بعد انتهاء العرض", "price": "50-100$", "duration": "شهري"}
        }
    },
    "security": {
        "name": "🔒 الأمن السيبراني",
        "services": {
            "s1": {"name": "حماية المواقع من الاختراق", "price": "300-600$", "duration": "7-14 يوم"},
            "s2": {"name": "اختبار الاختراق (Penetration Testing)", "price": "400-800$", "duration": "10-15 يوم"},
            "s3": {"name": "مراقبة الشبكات 24/7", "price": "200-400$", "duration": "شهري"},
            "s4": {"name": "استشارات أمنية", "price": "100-250$", "duration": "حسب الطلب"},
            "s5": {"name": "تدريب موظفين على الأمن", "price": "150-300$", "duration": "3-5 أيام"}
        }
    },
    "design": {
        "name": "💻 تصميم مواقع ويب",
        "services": {
            "d1": {"name": "مواقع متجاوبة (Responsive)", "price": "200-500$", "duration": "7-14 يوم"},
            "d2": {"name": "متاجر إلكترونية", "price": "400-1000$", "duration": "14-30 يوم"},
            "d3": {"name": "مواقع شركات", "price": "300-700$", "duration": "10-20 يوم"},
            "d4": {"name": "تطبيقات ويب", "price": "500-1500$", "duration": "20-40 يوم"},
            "d5": {"name": "صيانة وتحديث المواقع", "price": "100-300$", "duration": "حسب الطلب"}
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """القائمة الرئيسية"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup # يتم استيرادها هنا لتجنب مشاكل الاستيراد الدائري
    try:
        keyboard = [
            [InlineKeyboardButton("📱 التسويق الإلكتروني", callback_data="category_marketing")],
            [InlineKeyboardButton("🔒 الأمن السيبراني", callback_data="category_security")],
            [InlineKeyboardButton("💻 تصميم مواقع ويب", callback_data="category_design")],
            [InlineKeyboardButton("📞 التواصل المباشر", callback_data="contact")]
        ]
        
        await update.message.reply_text(
            "🚀 *مرحباً! اختر القسم الذي تريده:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("category_"):
            category = data.split("_")[1]
            await show_services(query, category)
            
        elif data.startswith("service_"):
            parts = data.split("_")
            service_id = parts[1]
            category = parts[2]
            await show_service_details(query, service_id, category)
            
        elif data == "contact":
            await show_contact(query)
            
        elif data == "back":
            await start_from_query(query)
            
    except Exception as e:
        logger.error(f"Error in button click: {e}")
        try:
            await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")
        except:
            pass

async def start_from_query(query):
    """بدء البوت من استعلام (لزر الرجوع)"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup # يتم استيرادها هنا
    try:
        keyboard = [
            [InlineKeyboardButton("📱 التسويق الإلكتروني", callback_data="category_marketing")],
            [InlineKeyboardButton("🔒 الأمن السيبراني", callback_data="category_security")],
            [InlineKeyboardButton("💻 تصميم مواقع ويب", callback_data="category_design")],
            [InlineKeyboardButton("📞 التواصل المباشر", callback_data="contact")]
        ]
        
        await query.edit_message_text(
            "🚀 *مرحباً! اختر القسم الذي تريده:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start from query: {e}")

async def show_services(query, category):
    """عرض خدمات القسم"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    try:
        category_data = SERVICES.get(category)
        if not category_data:
            await query.edit_message_text("❌ القسم غير موجود.")
            return
        
        keyboard = []
        for service_id, service in category_data["services"].items():
            keyboard.append([InlineKeyboardButton(
                f"• {service['name']}",
                callback_data=f"service_{service_id}_{category}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back")])
        
        await query.edit_message_text(
            f"📋 *{category_data['name']}*\n\n"
            "اختر الخدمة التي تريدها:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing services: {e}")
        await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")

async def show_service_details(query, service_id, category):
    """عرض تفاصيل الخدمة"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    try:
        category_data = SERVICES.get(category)
        if not category_data or service_id not in category_data["services"]:
            await query.edit_message_text("❌ الخدمة غير موجودة.")
            return
        
        service = category_data["services"][service_id]
        
        message = (
            f"🔍 {service['name']}\n\n"
            f"💰 السعر: {service['price']}\n"
            f"⏰ المدة: {service['duration']}\n\n"
            f"📞 للطلب أو الاستفسار:\n"
            f"• Telegram: @Cyber_Engineer_Ahmed\n"
            f"• WhatsApp: +963957248651\n\n"
            f"💬 تواصل معنا الآن لبدء المشروع!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع للخدمات", callback_data=f"category_{category}")],
            [InlineKeyboardButton("📞 التواصل المباشر", callback_data="contact")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error showing service details: {e}")
        await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")

async def show_contact(query):
    """عرض معلومات التواصل"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    try:
        message = (
            "📞 التواصل المباشر:\n\n"
            "👤 المسؤول: المهندس أحمد\n"
            "📱 Telegram: @Cyber_Engineer_Ahmed\n"
            "📞 WhatsApp: +963957248651\n"
            "🕒 الوقت: 24/7\n\n"
            "💬 تواصل معنا الآن للبدء بمشروعك!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back")]
        ]
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error showing contact: {e}")
        await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"حدث خطأ: {context.error}", exc_info=context.error)

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    # تهيئة كائن البوت والتطبيق
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in environment variables.")
        return
    
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL is not set in environment variables.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # إعداد handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    application.add_error_handler(error_handler)

    # تشغيل الـ webhook
    logger.info("🚀 Starting bot with webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

if __name__ == '__main__':
    main()
