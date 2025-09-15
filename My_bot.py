import logging
import re
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest
import time
from collections import defaultdict
from flask import Flask, request as flask_request

# تكوين التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# إعداد Flask
from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD", "POST"])
def root():
                          if flask_request.method == "POST":
             data = flask_request.get_json(force=True)
        update = Update.de_json(data, application.bot)
                  application.update_queue.put(update)
        return "", 200
          return "OK", 200

BOT_TOKEN = "7674783654:AAEsfosyZs40Aklk8hzB5L6fWMuiNQXa73o"
WEBHOOK_URL = "https://cspdm-zvoq.onrender.com/"
  # يجب تغيير هذا إلى رابطك الحقيقي 
WEBHOOK_PORT = 4000  # أو أي بورت تفضله

# معرف المستخدم الذي تريد البوت أن يرد عند مراسلته
TARGET_USERNAME = "@developers_Ahmad"

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

# قائمة الكلمات البذيئة (يمكن إضافة المزيد)
BAD_WORDS = [
    'كس', 'طيز', 'شرموطة', 'عاهر', 'زبالة', 'قحبة', 'منيوك', 'منiوكة', 'كلب', 'ابن الكلب',
    'خرا', 'عير', 'زق', 'فاجر', 'فاجرة', 'دعارة', 'زاني', 'زانية', 'فحل', 'فحلة',
    'قحاب', 'شراميط', 'أولاد الحرام', 'بنات الحرام', 'يلعن', 'يلعنه', 'يلعنك', 'سب',
    'اشتم', 'قحبه', 'شرموطه', 'زق', 'خرة', 'طيزه', 'طيزك'
]

# تخزين تحذيرات المستخدمين
user_warnings = defaultdict(int)

# ردود تلقائية للرسائل في الخاص
AUTO_RESPONSES = {
    "hello": ["مرحبا", "هلا", "السلام عليكم", "اهلا", "اهلين", "hello", "hi", "اهلاً"],
    "thanks": ["شكرا", "شكراً", "thank you", "thanks", "متشكر", "مشكور"],
    "how_are_you": ["كيفك", "كيف الحال", "شونك", "أخبارك", "how are you"]
}

# قائمة بأوامر النظام التي يجب تجاهلها (لتفادي التكرار)
SYSTEM_COMMANDS = ['/start', '/resetwarnings', '/help', '/settings']

# تهيئة تطبيق Telegram
request = HTTPXRequest(connection_pool_size=8)
application = Application.builder().token(BOT_TOKEN).request(request).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """القائمة الرئيسية"""
    try:
        # التحقق إذا كانت المحادثة مجموعة
        if update.message.chat.type in ['group', 'supergroup']:
            await update.message.reply_text(
                "👋 أنا بوت الخدمات! للتفاعل معي راسلني خاص"
            )
            return
            
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

async def handle_all_private_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد على جميع الرسائل في الخاص"""
    try:
        # التحقق إذا كانت المحادثة خاصة
        if update.message.chat.type != 'private':
            return
            
        # تخطي الرسائل من البوت نفسه
        if update.message.from_user and update.message.from_user.is_bot:
            return
            
        # تخطي الأوامر (يتم التعامل معها بواسطة handlers أخرى)
        if update.message.text and any(update.message.text.startswith(cmd) for cmd in SYSTEM_COMMANDS):
            return
            
        user_id = update.message.from_user.id
        message_text = update.message.text.lower() if update.message.text else ""
        
        # الرد التلقائي بناءً على نوع المحتوى
        if update.message.text:
            # الرد على الرسائل النصية
            response = None
            
            # التحقق من نوع الرسالة وإرسال رد مناسب
            for word in AUTO_RESPONSES["hello"]:
                if word in message_text:
                    response = "أهلاً وسهلاً بك! 😊\nكيف يمكنني مساعدتك اليوم؟"
                    break
                    
            if not response:
                for word in AUTO_RESPONSES["thanks"]:
                    if word in message_text:
                        response = "العفو! 😊\nدائماً بخدمتك. هل هناك شيء آخر تحتاجه؟"
                        break
                        
            if not response:
                for word in AUTO_RESPONSES["how_are_you"]:
                    if word in message_text:
                        response = "الحمد لله بخير! 😊\nشكراً لسؤالك. كيف يمكنني مساعدتك؟"
                        break
                        
            # إذا لم يكن هناك رد محدد، نرسل رداً عاماً
            if not response:
                response = (
                    "شكراً لتواصلك معنا! 😊\n"
                    "يمكنني مساعدتك في:\n"
                    "• 📱 التسويق الإلكتروني\n"
                    "• 🔒 الأمن السيبراني\n"
                    "• 💻 تصميم مواقع ويب\n\n"
                    "اكتب /start لرؤية القائمة الرئيسية."
                )
            
            # إرسال الرد
            await update.message.reply_text(response)
            
        elif update.message.photo:
            # الرد على الصور
            await update.message.reply_text(
                "شكراً لك على الصورة! 📸\n"
                "كيف يمكنني مساعدتك؟ اكتب /start لرؤية الخدمات المتاحة."
            )
            
        elif update.message.video:
            # الرد على الفيديوهات
            await update.message.reply_text(
                "شكراً لك على الفيديو! 🎥\n"
                "كيف يمكنني مساعدتك؟ اكتب /start لرؤية الخدمات المتاحة."
            )
            
        elif update.message.document:
            # الرد على المستندات
            await update.message.reply_text(
                "شكراً لك على المستند! 📄\n"
                "كيف يمكنني مساعدتك؟ اكتب /start لرؤية الخدمات المتاحة."
            )
            
        elif update.message.voice:
            # الرد على الرسائل الصوتية
            await update.message.reply_text(
                "شكراً لك على الرسالة الصوتية! 🎙\n"
                "كيف يمكنني مساعدتك؟ اكتب /start لرؤية الخدمات المتاحة."
            )
            
        elif update.message.sticker:
            # الرد على الملصقات (لا نرد عليها عادةً لتجنب التكرار)
            pass
            
        else:
            # الرد على أي نوع آخر من المحتوى
            await update.message.reply_text(
                "شكراً لك على رسالتك! 💬\n"
                "كيف يمكنني مساعدتك؟ اكتب /start لرؤية الخدمات المتاحة."
            )
            
    except Exception as e:
        logger.error(f"Error handling private message: {e}")

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل في المجموعات فقط"""
    try:
        # التحقق إذا كانت المجموعة
        if update.message.chat.type not in ['group', 'supergroup']:
            return
            
        # تخطي الرسائل من البوت نفسه
        if update.message.from_user and update.message.from_user.is_bot:
            return
            
        user_id = update.message.from_user.id
        chat_id = update.message.chat.id
        message_text = update.message.text.lower() if update.message.text else ""
        
        # التحقق من الكلمات البذيئة
        found_bad_word = False
        for word in BAD_WORDS:
            if word in message_text:
                found_bad_word = True
                break
                
        if found_bad_word:
            # حذف الرسالة
            try:
                await update.message.delete()
                logger.info(f"Deleted message with bad word from user {user_id}")
            except Exception as delete_error:
                logger.error(f"Error deleting message: {delete_error}")
                await context.bot.send_message(chat_id, "❌ لا أستطيع حذف الرسالة. تأكد من أن لدي صلاحية حذف الرسائل.")
                return
            
            # إضافة تحذير للمستخدم
            user_warnings[user_id] += 1
            
            warning_msg = ""
            if user_warnings[user_id] == 1:
                warning_msg = f"⚠ تحذير للمستخدم {update.message.from_user.first_name}! هذه المرة الأولى."
            elif user_warnings[user_id] == 2:
                warning_msg = f"⚠ تحذير ثاني للمستخدم {update.message.from_user.first_name}! هذه المرة الثانية."
            else:
                # حذف المستخدم بعد 3 تحذيرات
                try:
                    await context.bot.ban_chat_member(chat_id, user_id)
                    warning_msg = f"🚫 تم حظر المستخدم {update.message.from_user.first_name} بسبب تكرار الإساءة."
                    user_warnings[user_id] = 0  # إعادة الضبط
                    logger.info(f"Banned user {user_id} for repeated bad words")
                except Exception as ban_error:
                    warning_msg = f"❌ لا يمكنني حظر المستخدم. تأكد من أن لدي الصلاحيات الكافية."
                    logger.error(f"Ban error: {ban_error}")
            
            await context.bot.send_message(chat_id, warning_msg)
                
    except Exception as e:
        logger.error(f"Error in group message handling: {e}")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد عندما يتم ذكر المعرف @developers_Ahmad في المجموعات"""
    try:
        # التحقق إذا كانت المجموعة
        if update.message.chat.type not in ['group', 'supergroup']:
            return
            
        # تخطي الرسائل من البوت نفسه
        if update.message.from_user and update.message.from_user.is_bot:
            return
            
        message_text = update.message.text or ""
        
        # التحقق إذا تم ذكر المعرف
        if TARGET_USERNAME.lower() in message_text.lower():
            # الرد على التاغ
            response = (
                f"شكراً لتواصلك مع {TARGET_USERNAME}! 👋\n"
                "أنا بوت المساعدة، يمكنني تقديم الخدمات التالية:\n\n"
                "• 📱 التسويق الإلكتروني\n"
                "• 🔒 الأمن السيبراني\n"
                "• 💻 تصميم مواقع ويب\n\n"
                "راسلني خاص للاستفادة من خدماتنا! 💬"
            )
            
            await update.message.reply_text(response)
            
    except Exception as e:
        logger.error(f"Error handling mention: {e}")

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
            f"• Telegram: @developers_Ahmad\n"
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
        try:
            service = category_data["services"][service_id]
            message = (
                f"🔍 {service['name']}\n\n"
                f"💰 السعر: {service['price']}\n"
                f"⏰ المدة: {service['duration']}\n\n"
                f"📞 للطلب أو الاستفسار:\n"
                f"• Telegram: @developers_Ahmad\n"
                f"• WhatsApp: +963957248651\n\n"
                f"💬 تواصل معنا الآن لبدء المشروع!"
            )
            await query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=None
            )
        except:
            await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")

async def show_contact(query):
    """عرض معلومات التواصل"""
    try:
        message = (
            "📞 التواصل المباشر:\n\n"
            "👤 المسؤول: أحمد أبو يوسف\n"
            "📱 Telegram: @developers_Ahmad\n"
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
        # محاولة بدون ماركداون في حالة الخطأ
        try:
            message = (
                "📞 التواصل المباشر:\n\n"
                "👤 المسؤول: أحمد أبو يوسف\n"
                "📱 Telegram: @developers_Ahmad\n"
                "📞 WhatsApp: +963957248651\n"
                "🕒 الوقت: 24/7\n\n"
                "💬 تواصل معنا الآن للبدء بمشروعك!"
            )
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=None
            )
        except Exception as e2:
            logger.error(f"Second error in contact: {e2}")
            await query.edit_message_text("❌ حدث خطأ ما. يرجى المحاولة مرة أخرى.")

async def reset_warnings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعادة ضبط تحذيرات المستخدم (للمشرفين)"""
    try:
        if update.message.chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ هذا الأمر للمجموعات فقط!")
            return
            
        # التحقق إذا كان المستخدم مشرف
        user = await update.message.chat.get_member(update.message.from_user.id)
        if user.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
            return
            
        if context.args:
            user_id = int(context.args[0])
            user_warnings[user_id] = 0
            await update.message.reply_text(f"✅ تم إعادة ضبط تحذيرات المستخدم {user_id}.")
        else:
            await update.message.reply_text("⚠ يرجى تحديد ID المستخدم: /resetwarnings <user_id>")
            
    except Exception as e:
        logger.error(f"Error in reset_warnings: {e}")
        await update.message.reply_text("❌ حدث خطأ في الأمر.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"حدث خطأ: {context.error}", exc_info=context.error)

# إضافة handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("resetwarnings", reset_warnings))
application.add_handler(CallbackQueryHandler(handle_button_click))

# معالجة جميع الرسائل في الخاص (بأولوية منخفضة)
all_messages_handler = MessageHandler(
    filters.ChatType.PRIVATE & ~filters.COMMAND,
    handle_all_private_messages
)
application.add_handler(all_messages_handler)

# معالجة الرد على التاغات في المجموعات
mention_handler = MessageHandler(
    filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND,
    handle_mention
)
application.add_handler(mention_handler)

# معالجة رسائل المجموعات فقط (بأولوية منخفضة)
group_handler = MessageHandler(
    filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND,
    handle_group_message
)
application.add_handler(group_handler)

application.add_error_handler(error_handler)

@app.route('/webhook', methods=['POST'])
async def webhook():
    """معالجة webhook"""
    try:
        # تحديث البيانات الواردة من Telegram
        update = Update.de_json(await request.get_json(), application.bot)
        await application.process_update(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    """تعيين webhook"""
    try:
        # حذف webhook الحالي أولاً
        await application.bot.delete_webhook()
        
        # تعيين webhook جديد
        result = await application.bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
        
        if result:
            return jsonify({"status": "success", "message": "Webhook set successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to set webhook"}), 500
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """فحص صحة الخدمة"""
    return jsonify({"status": "healthy", "bot": "running"})

import os

if __name__ == "__main__":
    try:
        # تسجيل Webhook عند Telegram
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
        )
        print("✅ Webhook تم تسجيله بنجاح")

        # تشغيل Flask على البورت اللي Render يحدّده
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"❌ فشل التشغيل: {e}")
