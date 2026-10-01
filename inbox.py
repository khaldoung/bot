import logging

from telegram import Bot

from database import (
    claim_message,
    delete_message_claim,
    get_users_with_email,
    update_saved_message,
)
from mailtm import MailTMError

logger = logging.getLogger(__name__)

# =========================================================
# HELPERS
# =========================================================


def get_sender_info(sender):
    if not sender:
        return "Unknown", "Unknown"

    if isinstance(sender, dict):
        name = sender.get("name") or "Unknown"
        address = sender.get("address") or "Unknown"
        return name, address

    return "Unknown", "Unknown"


def extract_message_text(message):
    """استخراج محتوى الرسالة من Mail.tm.

    نحاول أولاً text، وإذا لم يوجد نستخدم html.
    """

    text = message.get("text")

    if text:
        return str(text)

    html = message.get("html")

    if isinstance(html, list):
        return "\n".join(str(item) for item in html)

    if html:
        return str(html)

    return "No content"


def clean_text(text, limit=3500):
    if not text:
        return "No content"

    text = str(text)

    if len(text) > limit:
        text = text[:limit] + "\n..."

    return text


# =========================================================
# BUILD TELEGRAM MESSAGE
# =========================================================


def build_telegram_message(
    language,
    email,
    subject,
    sender_name,
    sender_address,
    message_text,
    received_at,
):

    message_text = clean_text(message_text)
    subject = subject or "No subject"
    sender_name = sender_name or "Unknown"
    sender_address = sender_address or "Unknown"
    received_at = str(received_at) if received_at else "Unknown"

    if language == "ar":
        return (
            "📩 <b>رسالة جديدة</b>\n\n"
            f"📧 <b>البريد:</b>\n"
            f"<code>{email}</code>\n\n"
            f"👤 <b>المرسل:</b>\n"
            f"{sender_name}\n"
            f"<code>{sender_address}</code>\n\n"
            f"📌 <b>الموضوع:</b>\n"
            f"{subject}\n\n"
            f"🕘 <b>وقت الاستلام:</b>\n"
            f"{received_at}\n\n"
            "━━━━━━━━━━━━━━\n\n"
            f"{message_text}"
        )

    return (
        "📩 <b>New Email</b>\n\n"
        f"📧 <b>Email:</b>\n"
        f"<code>{email}</code>\n\n"
        f"👤 <b>Sender:</b>\n"
        f"{sender_name}\n"
        f"<code>{sender_address}</code>\n\n"
        f"📌 <b>Subject:</b>\n"
        f"{subject}\n\n"
        f"🕘 <b>Received:</b>\n"
        f"{received_at}\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"{message_text}"
    )


# =========================================================
# CHECK ALL INBOXES
# =========================================================


async def check_all_inboxes(
    pool,
    mail_client,
    bot: Bot,
):

    users = await get_users_with_email(pool)

    if not users:
        return

    for user in users:

        telegram_id = user["telegram_id"]
        language = user["language"] or "en"
        email = user["email"]
        token = user["mail_token"]

        if not token:
            continue

        try:

            # =============================================
            # GET MESSAGE LIST
            # =============================================

            messages = await mail_client.get_messages(token)

            if not messages:
                continue

            # Mail.tm قد يعيد: list أو dict يحتوي hydra:member
            if isinstance(messages, dict):
                messages = messages.get("hydra:member", [])

            if not isinstance(messages, list):
                continue

            # =============================================
            # PROCESS MESSAGES
            # =============================================

            for message in messages:

                if not isinstance(message, dict):
                    continue

                mail_message_id = message.get("id")

                if not mail_message_id:
                    continue

                # =========================================
                # CLAIM MESSAGE
                # =========================================

                claimed = await claim_message(
                    pool,
                    telegram_id,
                    mail_message_id,
                )

                # الرسالة تم إرسالها سابقًا
                if not claimed:
                    continue

                try:

                    # =====================================
                    # GET FULL MESSAGE
                    # =====================================

                    full_message = await mail_client.get_message(
                        token,
                        mail_message_id,
                    )

                    if not full_message:
                        raise RuntimeError(
                            "Mail.tm returned empty message"
                        )

                    # =====================================
                    # SENDER
                    # =====================================

                    sender_name, sender_address = get_sender_info(
                        full_message.get("from")
                    )

                    # =====================================
                    # SUBJECT
                    # =====================================

                    subject = (
                        full_message.get("subject") or "No subject"
                    )

                    # =====================================
                    # MESSAGE TEXT
                    # =====================================

                    message_text = extract_message_text(
                        full_message
                    )

                    # =====================================
                    # RECEIVED TIME
                    # =====================================

                    received_at = full_message.get(
                        "createdAt"
                    ) or message.get("createdAt")

                    # =====================================
                    # BUILD TELEGRAM MESSAGE
                    # =====================================

                    telegram_message = build_telegram_message(
                        language=language,
                        email=email,
                        subject=subject,
                        sender_name=sender_name,
                        sender_address=sender_address,
                        message_text=message_text,
                        received_at=received_at,
                    )

                    # =====================================
                    # SEND TO TELEGRAM
                    # =====================================

                    try:

                        await bot.send_message(
                            chat_id=telegram_id,
                            text=telegram_message,
                            parse_mode="HTML",
                        )

                    except Exception:

                        logger.exception(
                            "Failed to send message to Telegram: %s",
                            telegram_id,
                        )

                        # السماح بإعادة المحاولة
                        await delete_message_claim(
                            pool,
                            telegram_id,
                            mail_message_id,
                        )

                        continue

                    # =====================================
                    # SAVE MESSAGE DATA
                    # =====================================

                    try:

                        await update_saved_message(
                            pool=pool,
                            telegram_id=telegram_id,
                            mail_message_id=mail_message_id,
                            subject=subject,
                            sender_name=sender_name,
                            sender_address=sender_address,
                            message_text=message_text,
                            received_at=received_at,
                        )

                    except Exception:

                        logger.exception(
                            "Telegram message was sent but database update failed for message %s",
                            mail_message_id,
                        )

                        # لا نحذف الحجز هنا لمنع التكرار
                        continue

                except Exception:

                    logger.exception(
                        "Failed processing Mail.tm message %s for user %s",
                        mail_message_id,
                        telegram_id,
                    )

                    # إزالة الحجز للمحاولة لاحقًا
                    await delete_message_claim(
                        pool,
                        telegram_id,
                        mail_message_id,
                    )

                    continue

        except MailTMError:

            logger.exception(
                "Mail.tm error for user %s",
                telegram_id,
            )

        except Exception:

            logger.exception(
                "Unexpected inbox error for user %s",
                telegram_id,
            )
