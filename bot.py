# import asyncio
# import os

# from aiogram import Bot, Dispatcher
# from aiogram.client.session.aiohttp import AiohttpSession
# from aiogram.filters import CommandStart
# from aiogram.types import Message

# TOKEN = "8627088338:AAG_WUMeTm6bxII78cdIkSiYhESIQW6lRIQ"

# proxy = os.getenv("https_proxy") or os.getenv("HTTPS_PROXY")

# session = AiohttpSession(proxy=proxy)
# bot = Bot(token=TOKEN, session=session)
# dp = Dispatcher()


# @dp.message(CommandStart())
# async def start(message: Message):
#     user_id = message.from_user.id
#     await message.answer(
#         f"مرحباً 👋\n\n"
#         f"الـ ID الخاص بك هو:\n"
#         f"`{user_id}`"
#     )


# async def main():
#     await dp.start_polling(bot)


# if __name__ == "__main__":
#     asyncio.run(main())

import os
import logging
from html import escape

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    WebAppInfo,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from database import (
    create_pool,
    init_db,
    get_user,
    create_or_update_user,
    update_language,
    save_email_account,
    get_email_accounts,
    switch_email_account,
)

from mailtm import MailTMClient, MailTMError
from inbox import check_all_inboxes
from web_server import start_web_server


# =========================================================
# إعدادات البوت
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not configured"
    )


# =========================================================
# قناة الاشتراك الإجباري
# =========================================================

FORCE_SUB_CHANNEL = "@KhaldounSoft"

FORCE_SUB_CHANNEL_URL = (
    "https://t.me/KhaldounSoft"
)


# =========================================================
# رابط Mini App
# =========================================================

WEB_APP_URL = os.getenv(
    "WEB_APP_URL",
    "https://whatsapp-bot-v1-5.onrender.com"
)


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# العملاء
# =========================================================

db_pool = None
mail_client = None
application = None
web_runner = None


# =========================================================
# Mini App - Menu Button
# =========================================================

async def setup_mini_app_menu():

    """
    إضافة زر Mini App داخل قائمة البوت.
    """

    try:

        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="📧 Temp Mailo",
                web_app=WebAppInfo(
                    url=WEB_APP_URL,
                ),
            )
        )

        logger.info(
            "Telegram Mini App menu button configured: %s",
            WEB_APP_URL,
        )

    except Exception:

        logger.exception(
            "Failed to configure Mini App menu button"
        )


# =========================================================
# تعديل الرسائل بأمان
# =========================================================

async def safe_edit_message(
    query,
    text,
    reply_markup=None,
    parse_mode=None,
):

    try:

        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )

    except Exception as e:

        error_text = str(e).lower()

        if (
            "message is not modified"
            in error_text
        ):
            return

        raise


# =========================================================
# النصوص
# =========================================================

TEXT = {

    "ar": {

        "welcome": (
            "👋 أهلاً بك في بوت البريد المؤقت!\n\n"
            "📧 يمكنك إنشاء بريد إلكتروني خاص بك "
            "واستقبال الرسائل عليه مباشرة هنا في تيليجرام.\n\n"
            "اختر اللغة:"
        ),

        "main": (
            "📧 <b>البريد المؤقت</b>\n\n"
            "اختر العملية التي تريدها:"
        ),

        "email_created": (
            "✅ تم إنشاء بريدك بنجاح!\n\n"
            "📧 البريد:\n"
            "<code>{email}</code>\n\n"
            "🔐 كلمة المرور محفوظة بأمان.\n\n"
            "يمكنك الآن استقبال الرسائل على هذا البريد."
        ),

        "creating": (
            "⏳ جارٍ إنشاء بريد جديد..."
        ),

        "error": (
            "❌ حدث خطأ أثناء إنشاء البريد.\n"
            "حاول مرة أخرى بعد قليل."
        ),

        "your_email": (
            "📧 بريدك الحالي:\n\n"
            "<code>{email}</code>"
        ),

        "no_email": (
            "⚠️ ليس لديك بريد حاليًا.\n"
            "اضغط على «إنشاء بريد» لإنشاء واحد."
        ),

        "checking": (
            "📨 جاري فحص صندوق الوارد..."
        ),

        "inbox_empty": (
            "📭 صندوق الوارد فارغ."
        ),

        "unknown_sender": (
            "غير معروف"
        ),

        "no_subject": (
            "بدون عنوان"
        ),

        "change_confirm": (
            "🔄 <b>تغيير البريد</b>\n\n"
            "هل تريد إنشاء بريد إلكتروني جديد؟"
        ),

        "previous_emails": (
            "🕘 <b>البريد السابق</b>\n\n"
            "اختر البريد الذي تريد استخدامه:"
        ),

        "no_previous_emails": (
            "🕘 لا توجد لديك إيميلات سابقة."
        ),

        "email_switched": (
            "✅ تم اختيار البريد بنجاح!\n\n"
            "📧 البريد الحالي:\n"
            "<code>{email}</code>"
        ),

        "invalid_email": (
            "❌ البريد غير صالح."
        ),

        "email_not_found": (
            "❌ البريد غير موجود."
        ),

        "selected": (
            "الحالي"
        ),

        "select": (
            "استخدام"
        ),
    },


    "en": {

        "welcome": (
            "👋 Welcome to the temporary email bot!\n\n"
            "📧 You can create your own email address "
            "and receive messages directly here in Telegram.\n\n"
            "Choose your language:"
        ),

        "main": (
            "📧 <b>Temporary Email</b>\n\n"
            "Choose an action:"
        ),

        "email_created": (
            "✅ Your email has been created successfully!\n\n"
            "📧 Email:\n"
            "<code>{email}</code>\n\n"
            "🔐 Your password is stored securely.\n\n"
            "You can now receive emails at this address."
        ),

        "creating": (
            "⏳ Creating a new email..."
        ),

        "error": (
            "❌ An error occurred while creating the email.\n"
            "Please try again later."
        ),

        "your_email": (
            "📧 Your current email:\n\n"
            "<code>{email}</code>"
        ),

        "no_email": (
            "⚠️ You don't have an email yet.\n"
            "Press «Create Email» to create one."
        ),

        "checking": (
            "📨 Checking your inbox..."
        ),

        "inbox_empty": (
            "📭 Your inbox is empty."
        ),

        "unknown_sender": (
            "Unknown"
        ),

        "no_subject": (
            "No subject"
        ),

        "change_confirm": (
            "🔄 <b>Change Email</b>\n\n"
            "Do you want to create a new email address?"
        ),

        "previous_emails": (
            "🕘 <b>Previous Emails</b>\n\n"
            "Choose the email you want to use:"
        ),

        "no_previous_emails": (
            "🕘 You don't have any previous emails."
        ),

        "email_switched": (
            "✅ Email selected successfully!\n\n"
            "📧 Current email:\n"
            "<code>{email}</code>"
        ),

        "invalid_email": (
            "❌ Invalid email."
        ),

        "email_not_found": (
            "❌ Email not found."
        ),

        "selected": (
            "Current"
        ),

        "select": (
            "Use"
        ),
    },
}


# =========================================================
# الاشتراك الإجباري
# =========================================================

async def is_subscribed(
    user_id: int,
) -> bool:

    try:

        member = (
            await application.bot.get_chat_member(
                chat_id=FORCE_SUB_CHANNEL,
                user_id=user_id,
            )
        )

        return member.status in (
            "member",
            "administrator",
            "creator",
        )

    except Exception as e:

        logger.error(
            "Subscription check failed "
            "for user %s: %s",
            user_id,
            e,
        )

        return False


def subscription_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📢 الاشتراك في قناة البوت",
                url=FORCE_SUB_CHANNEL_URL,
            )
        ],

        [
            InlineKeyboardButton(
                "✅ تحقق من الاشتراك",
                callback_data="check_subscription",
            )
        ],

    ])


async def require_subscription(
    update: Update,
) -> bool:

    user = update.effective_user

    if not user:
        return False

    subscribed = await is_subscribed(
        user.id
    )

    if subscribed:
        return True

    message = update.effective_message

    if message:

        await message.reply_text(

            "📢 <b>الاشتراك مطلوب</b>\n\n"

            "الرجاء الاشتراك بقناة البوت "
            "لتتمكن من استخدامه.\n\n"

            "بعد الاشتراك اضغط على "
            "«✅ تحقق من الاشتراك».",

            reply_markup=subscription_keyboard(),

            parse_mode="HTML",
        )

    return False


# =========================================================
# لوحة التحكم
# =========================================================

def main_keyboard(
    language: str,
):

    if language == "ar":

        buttons = [

            [
                InlineKeyboardButton(
                    "📧 إنشاء بريد",
                    callback_data="create_email",
                ),
            ],

            [
                InlineKeyboardButton(
                    "📬 بريدي الحالي",
                    callback_data="my_email",
                ),

                InlineKeyboardButton(
                    "📨 صندوق الوارد",
                    callback_data="inbox",
                ),
            ],

            [
                InlineKeyboardButton(
                    "🔄 تغيير البريد",
                    callback_data="change_email",
                ),
            ],

            [
                InlineKeyboardButton(
                    "🕘 البريد السابق",
                    callback_data="previous_emails",
                ),
            ],

            [
                InlineKeyboardButton(
                    "🌐 تغيير اللغة",
                    callback_data="language",
                ),
            ],

        ]

    else:

        buttons = [

            [
                InlineKeyboardButton(
                    "📧 Create Email",
                    callback_data="create_email",
                ),
            ],

            [
                InlineKeyboardButton(
                    "📬 My Email",
                    callback_data="my_email",
                ),

                InlineKeyboardButton(
                    "📨 Inbox",
                    callback_data="inbox",
                ),
            ],

            [
                InlineKeyboardButton(
                    "🔄 Change Email",
                    callback_data="change_email",
                ),
            ],

            [
                InlineKeyboardButton(
                    "🕘 Previous Emails",
                    callback_data="previous_emails",
                ),
            ],

            [
                InlineKeyboardButton(
                    "🌐 Change Language",
                    callback_data="language",
                ),
            ],

        ]

    return InlineKeyboardMarkup(
        buttons
    )


# =========================================================
# إنشاء بريد جديد
# =========================================================

async def create_email(
    query,
    telegram_id,
    language,
):

    await safe_edit_message(
        query,
        TEXT[language]["creating"],
    )

    try:

        account = (
            await mail_client.create_account()
        )

        email = account["email"]
        password = account["password"]
        token = account["token"]
        account_id = account["id"]

        # =============================================
        # حفظ المستخدم
        # =============================================

        await create_or_update_user(

            db_pool,

            telegram_id,

            language=language,

            email=email,

            mail_password=password,

            mail_token=token,

            mail_account_id=account_id,
        )

        # =============================================
        # حفظ البريد في سجل الإيميلات
        # =============================================

        await save_email_account(

            pool=db_pool,

            telegram_id=telegram_id,

            email=email,

            mail_password=password,

            mail_token=token,

            mail_account_id=account_id,

            is_current=True,
        )

        # =============================================
        # إرسال النتيجة
        # =============================================

        await safe_edit_message(

            query,

            TEXT[language][
                "email_created"
            ].format(
                email=escape(email)
            ),

            parse_mode="HTML",

            reply_markup=main_keyboard(
                language
            ),
        )

    except MailTMError as e:

        logger.error(
            "Mail.tm error: %s",
            e,
        )

        await safe_edit_message(

            query,

            TEXT[language]["error"],

            reply_markup=main_keyboard(
                language
            ),
        )

    except Exception:

        logger.exception(
            "Unexpected error while creating email"
        )

        await safe_edit_message(

            query,

            TEXT[language]["error"],

            reply_markup=main_keyboard(
                language
            ),
        )


# =========================================================
# /start
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    if not user:
        return

    # الاشتراك
    if not await require_subscription(
        update
    ):
        return

    # المستخدم موجود؟
    existing_user = await get_user(
        db_pool,
        user.id,
    )

    if existing_user:

        language = (
            existing_user["language"]
            or "en"
        )

        await update.message.reply_text(

            TEXT[language]["main"],

            reply_markup=main_keyboard(
                language
            ),

            parse_mode="HTML",
        )

        return

    # اختيار اللغة
    keyboard = [

        [

            InlineKeyboardButton(
                "🇸🇦 العربية",
                callback_data="lang_ar",
            ),

            InlineKeyboardButton(
                "🇺🇸 English",
                callback_data="lang_en",
            ),

        ]

    ]

    await update.message.reply_text(

        TEXT["ar"]["welcome"],

        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),

        parse_mode="HTML",
    )


# =========================================================
# Callback Handler
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    callback = query.data

    # =============================================
    # فحص الاشتراك
    # =============================================

    if callback == "check_subscription":

        if await is_subscribed(
            user.id
        ):

            db_user = await get_user(
                db_pool,
                user.id,
            )

            if db_user:

                language = (
                    db_user["language"]
                    or "en"
                )

                await safe_edit_message(

                    query,

                    TEXT[language]["main"],

                    reply_markup=main_keyboard(
                        language
                    ),

                    parse_mode="HTML",
                )

            else:

                keyboard = [

                    [

                        InlineKeyboardButton(
                            "🇸🇦 العربية",
                            callback_data="lang_ar",
                        ),

                        InlineKeyboardButton(
                            "🇺🇸 English",
                            callback_data="lang_en",
                        ),

                    ]

                ]

                await safe_edit_message(

                    query,

                    TEXT["ar"]["welcome"],

                    reply_markup=InlineKeyboardMarkup(
                        keyboard
                    ),

                    parse_mode="HTML",
                )

        else:

            await query.answer(

                "❌ لم تشترك في القناة بعد.\n"
                "اشترك أولاً ثم اضغط تحقق.",

                show_alert=True,
            )

        return

    # =============================================
    # فحص الاشتراك قبل الأزرار
    # =============================================

    if not await is_subscribed(
        user.id
    ):

        await safe_edit_message(

            query,

            "📢 <b>الاشتراك مطلوب</b>\n\n"

            "الرجاء الاشتراك بقناة البوت "
            "لتتمكن من استخدامه.\n\n"

            "بعد الاشتراك اضغط على "
            "«✅ تحقق من الاشتراك».",

            reply_markup=subscription_keyboard(),

            parse_mode="HTML",
        )

        return

    # =============================================
    # اختيار اللغة لأول مرة
    # =============================================

    if callback == "lang_ar":

        await create_or_update_user(

            db_pool,

            user.id,

            language="ar",
        )

        await safe_edit_message(

            query,

            TEXT["ar"]["main"],

            reply_markup=main_keyboard(
                "ar"
            ),

            parse_mode="HTML",
        )

        return

    if callback == "lang_en":

        await create_or_update_user(

            db_pool,

            user.id,

            language="en",
        )

        await safe_edit_message(

            query,

            TEXT["en"]["main"],

            reply_markup=main_keyboard(
                "en"
            ),

            parse_mode="HTML",
        )

        return

    # =============================================
    # الحصول على المستخدم
    # =============================================

    db_user = await get_user(
        db_pool,
        user.id,
    )

    if not db_user:
        return

    language = (
        db_user["language"]
        or "en"
    )

    # =============================================
    # إنشاء البريد
    # =============================================

    if callback == "create_email":

        if db_user["email"]:

            await safe_edit_message(

                query,

                TEXT[language][
                    "your_email"
                ].format(
                    email=escape(
                        db_user["email"]
                    )
                ),

                parse_mode="HTML",

                reply_markup=main_keyboard(
                    language
                ),
            )

            return

        await create_email(

            query,

            user.id,

            language,
        )

        return

    # =============================================
    # البريد الحالي
    # =============================================

    if callback == "my_email":

        if not db_user["email"]:

            await safe_edit_message(

                query,

                TEXT[language]["no_email"],

                reply_markup=main_keyboard(
                    language
                ),
            )

            return

        await safe_edit_message(

            query,

            TEXT[language][
                "your_email"
            ].format(
                email=escape(
                    db_user["email"]
                )
            ),

            parse_mode="HTML",

            reply_markup=main_keyboard(
                language
            ),
        )

        return

    # =============================================
    # البريد السابق
    # =============================================

    if callback == "previous_emails":

        try:

            accounts = await get_email_accounts(
                db_pool,
                user.id,
            )

            if not accounts:

                await safe_edit_message(

                    query,

                    TEXT[language][
                        "no_previous_emails"
                    ],

                    reply_markup=main_keyboard(
                        language
                    ),
                )

                return


            buttons = []

            for account in accounts:

                email = str(
                    account["email"]
                )

                account_id = int(
                    account["id"]
                )

                is_current = (
                    account["is_current"]
                    is True
                )


                if is_current:

                    button_text = (
                        f"✅ {email}"
                    )

                else:

                    button_text = (
                        f"📧 {email}"
                    )


                buttons.append([

                    InlineKeyboardButton(

                        button_text,

                        callback_data=(
                            f"select_email:"
                            f"{account_id}"
                        ),
                    )

                ])


            buttons.append([

                InlineKeyboardButton(

                    "↩️ رجوع"
                    if language == "ar"
                    else "↩️ Back",

                    callback_data="back",
                )

            ])


            await safe_edit_message(

                query,

                TEXT[language][
                    "previous_emails"
                ],

                reply_markup=InlineKeyboardMarkup(
                    buttons
                ),

                parse_mode="HTML",
            )

        except Exception:

            logger.exception(
                "Failed to load previous emails"
            )

            await safe_edit_message(

                query,

                TEXT[language]["error"],

                reply_markup=main_keyboard(
                    language
                ),
            )

        return

    # =============================================
    # اختيار بريد سابق
    # =============================================

    if callback.startswith(
        "select_email:"
    ):

        try:

            account_id = int(
                callback.split(
                    ":",
                    1
                )[1]
            )

        except (
            ValueError,
            IndexError,
        ):

            await query.answer(

                TEXT[language][
                    "invalid_email"
                ],

                show_alert=True,
            )

            return


        try:

            account = await switch_email_account(

                db_pool,

                user.id,

                account_id,
            )


            if not account:

                await query.answer(

                    TEXT[language][
                        "email_not_found"
                    ],

                    show_alert=True,
                )

                return


            email = account["email"]


            await safe_edit_message(

                query,

                TEXT[language][
                    "email_switched"
                ].format(
                    email=escape(
                        email
                    )
                ),

                reply_markup=main_keyboard(
                    language
                ),

                parse_mode="HTML",
            )


            await query.answer(

                "✅ تم اختيار البريد"
                if language == "ar"
                else "✅ Email selected"
            )

        except Exception:

            logger.exception(
                "Failed to switch email account"
            )

            await safe_edit_message(

                query,

                TEXT[language]["error"],

                reply_markup=main_keyboard(
                    language
                ),
            )

        return

    # =============================================
    # تغيير البريد
    # =============================================

    if callback == "change_email":

        keyboard = [

            [

                InlineKeyboardButton(

                    "✅ نعم"
                    if language == "ar"
                    else "✅ Yes",

                    callback_data="confirm_change",
                ),

                InlineKeyboardButton(

                    "❌ إلغاء"
                    if language == "ar"
                    else "❌ Cancel",

                    callback_data="cancel_change",
                ),

            ]

        ]

        await safe_edit_message(

            query,

            TEXT[language][
                "change_confirm"
            ],

            reply_markup=InlineKeyboardMarkup(
                keyboard
            ),

            parse_mode="HTML",
        )

        return

    # =============================================
    # تأكيد تغيير البريد
    # =============================================

    if callback == "confirm_change":

        await create_email(

            query,

            user.id,

            language,
        )

        return

    # =============================================
    # إلغاء
    # =============================================

    if callback == "cancel_change":

        await safe_edit_message(

            query,

            TEXT[language]["main"],

            reply_markup=main_keyboard(
                language
            ),

            parse_mode="HTML",
        )

        return

    # =============================================
    # اللغة
    # =============================================

    if callback == "language":

        keyboard = [

            [

                InlineKeyboardButton(
                    "🇸🇦 العربية",
                    callback_data="set_ar",
                ),

                InlineKeyboardButton(
                    "🇺🇸 English",
                    callback_data="set_en",
                ),

            ],

            [

                InlineKeyboardButton(

                    "↩️ رجوع"
                    if language == "ar"
                    else "↩️ Back",

                    callback_data="back",
                ),

            ],

        ]

        await safe_edit_message(

            query,

            "🌐 اختر اللغة / Choose language:",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            ),
        )

        return

    # =============================================
    # العربية
    # =============================================

    if callback == "set_ar":

        await update_language(

            db_pool,

            user.id,

            "ar",
        )

        await safe_edit_message(

            query,

            TEXT["ar"]["main"],

            reply_markup=main_keyboard(
                "ar"
            ),

            parse_mode="HTML",
        )

        return

    # =============================================
    # الإنجليزية
    # =============================================

    if callback == "set_en":

        await update_language(

            db_pool,

            user.id,

            "en",
        )

        await safe_edit_message(

            query,

            TEXT["en"]["main"],

            reply_markup=main_keyboard(
                "en"
            ),

            parse_mode="HTML",
        )

        return

    # =============================================
    # رجوع
    # =============================================

    if callback == "back":

        await safe_edit_message(

            query,

            TEXT[language]["main"],

            reply_markup=main_keyboard(
                language
            ),

            parse_mode="HTML",
        )

        return

    # =============================================
    # صندوق الوارد
    # =============================================

    if callback == "inbox":

        if not db_user["mail_token"]:

            await safe_edit_message(

                query,

                TEXT[language]["no_email"],

                reply_markup=main_keyboard(
                    language
                ),
            )

            return

        await safe_edit_message(

            query,

            TEXT[language]["checking"],
        )

        try:

            data = await mail_client.get_messages(

                db_user["mail_token"]
            )

            if isinstance(data, list):

                messages = data

            elif isinstance(data, dict):

                messages = data.get(
                    "hydra:member",
                    [],
                )

            else:

                messages = []

            if not messages:

                text = TEXT[language][
                    "inbox_empty"
                ]

            else:

                lines = []

                for message in messages[:10]:

                    subject = (
                        message.get(
                            "subject"
                        )
                        or TEXT[language][
                            "no_subject"
                        ]
                    )

                    sender = message.get(
                        "from",
                        {},
                    )

                    if not isinstance(
                        sender,
                        dict,
                    ):

                        sender = {}

                    sender_address = (
                        sender.get(
                            "address"
                        )
                        or TEXT[language][
                            "unknown_sender"
                        ]
                    )

                    subject = escape(
                        str(subject)
                    )

                    sender_address = escape(
                        str(sender_address)
                    )

                    lines.append(

                        f"📩 <b>{subject}</b>\n"
                        f"👤 {sender_address}"
                    )

                text = "\n\n".join(
                    lines
                )

            await safe_edit_message(

                query,

                text,

                parse_mode="HTML",

                reply_markup=main_keyboard(
                    language
                ),
            )

        except MailTMError:

            await safe_edit_message(

                query,

                TEXT[language]["error"],

                reply_markup=main_keyboard(
                    language
                ),
            )

        except Exception:

            logger.exception(
                "Unexpected error while checking inbox"
            )

            await safe_edit_message(

                query,

                TEXT[language]["error"],

                reply_markup=main_keyboard(
                    language
                ),
            )

        return


# =========================================================
# فحص البريد تلقائيًا
# =========================================================

async def check_inboxes_job(
    context: ContextTypes.DEFAULT_TYPE,
):

    try:

        await check_all_inboxes(

            bot=context.bot,

            pool=db_pool,

            mail_client=mail_client,
        )

    except Exception:

        logger.exception(
            "Inbox checker failed"
        )


# =========================================================
# بدء التشغيل
# =========================================================

async def post_init(
    application,
):

    global db_pool
    global mail_client
    global web_runner

    logger.info(
        "Initializing database..."
    )

    db_pool = await create_pool()

    await init_db(
        db_pool
    )

    mail_client = MailTMClient()

    # =============================================
    # Mini App Web Server
    # =============================================

    web_runner = await start_web_server(
        db_pool=db_pool,
        mail_client=mail_client,
    )

    # =============================================
    # Mini App Menu
    # =============================================

    await setup_mini_app_menu()

    # =============================================
    # فحص البريد كل 15 ثانية
    # =============================================

    application.job_queue.run_repeating(

        check_inboxes_job,

        interval=15,

        first=10,

        name="inbox_checker",
    )

    logger.info(
        "Database initialized."
    )

    logger.info(
        "Mail.tm client initialized."
    )

    logger.info(
        "Mini App web server started."
    )

    logger.info(
        "Inbox checker started."
    )


# =========================================================
# إيقاف البوت
# =========================================================

async def post_shutdown(
    application,
):

    global db_pool
    global mail_client
    global web_runner

    # =============================================
    # إغلاق Web Server
    # =============================================

    if web_runner:

        try:

            await web_runner.cleanup()

            logger.info(
                "Web server stopped."
            )

        except Exception:

            logger.exception(
                "Failed to stop web server"
            )

    # =============================================
    # إغلاق Mail.tm
    # =============================================

    if mail_client:

        await mail_client.close()

    # =============================================
    # إغلاق قاعدة البيانات
    # =============================================

    if db_pool:

        await db_pool.close()

    logger.info(
        "Bot stopped."
    )


# =========================================================
# تشغيل البوت
# =========================================================

def main():

    global application

    application = (

        Application.builder()

        .token(
            BOT_TOKEN
        )

        .post_init(
            post_init
        )

        .post_shutdown(
            post_shutdown
        )

        .build()
    )

    # /start
    application.add_handler(

        CommandHandler(
            "start",
            start,
        )
    )

    # الأزرار
    application.add_handler(

        CallbackQueryHandler(
            button_handler
        )
    )

    logger.info(
        "Bot is starting..."
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    main()
