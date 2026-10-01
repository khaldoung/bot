import os
import json
import hmac
import hashlib
import urllib.parse
from datetime import datetime, timezone
from typing import Optional

from aiohttp import web

from database import (
    get_user,
    update_language,
    save_email_account,
    get_email_accounts,
    get_current_email_account,
    switch_email_account,
    create_or_update_user,
)

from mailtm import MailTMClient


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = 8612310722:AAG5NWNSJHmnpRZrhT3oXDUE88yGqLe9klE

WEB_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "web"
)


# =========================================================
# TELEGRAM INIT DATA VERIFICATION
# =========================================================

def verify_telegram_init_data(
    init_data: str
) -> Optional[dict]:

    if not init_data or not BOT_TOKEN:
        return None

    try:

        parsed = urllib.parse.parse_qsl(
            init_data,
            keep_blank_values=True
        )

        data = dict(parsed)

        received_hash = data.pop(
            "hash",
            None
        )

        if not received_hash:
            return None

        data_check_string = "\n".join(
            f"{key}={value}"
            for key, value in sorted(
                data.items()
            )
        )

        # Telegram WebApp secret key
        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(
            calculated_hash,
            received_hash
        ):
            return None

        # Extract Telegram user
        user_json = data.get("user")

        if not user_json:
            return None

        telegram_user = json.loads(
            user_json
        )

        telegram_id = telegram_user.get(
            "id"
        )

        if not telegram_id:
            return None

        return {
            "telegram_id": int(telegram_id),
            "user": telegram_user,
        }

    except Exception as exc:

        print(
            "Telegram initData verification error:",
            exc
        )

        return None


# =========================================================
# REQUEST USER
# =========================================================

def get_telegram_user(
    request: web.Request
) -> Optional[dict]:

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        ""
    )

    return verify_telegram_init_data(
        init_data
    )


# =========================================================
# JSON RESPONSE
# =========================================================

def json_response(
    data,
    status=200
):

    return web.json_response(
        data,
        status=status
    )


# =========================================================
# AUTH ERROR
# =========================================================

def unauthorized():

    return json_response(
        {
            "success": False,
            "error": "Unauthorized"
        },
        status=401
    )


# =========================================================
# /api/me
# =========================================================

async def api_me(
    request: web.Request
):

    auth = get_telegram_user(request)

    if not auth:
        return unauthorized()

    telegram_id = auth["telegram_id"]

    user = await get_user(
        request.app["db_pool"],
        telegram_id
    )

    if not user:

        return json_response(
            {
                "telegram_id": telegram_id,
                "language": "ar",
                "email": None
            }
        )

    return json_response(
        {
            "telegram_id": telegram_id,

            "language":
                user.get(
                    "language",
                    "ar"
                ),

            "email":
                user.get(
                    "email"
                )
        }
    )


# =========================================================
# /api/previous-emails
# =========================================================

async def api_previous_emails(
    request: web.Request
):

    auth = get_telegram_user(request)

    if not auth:
        return unauthorized()

    telegram_id = auth["telegram_id"]

    try:

        accounts = await get_email_accounts(
            request.app["db_pool"],
            telegram_id
        )

        result = []

        for account in accounts:

            result.append(
                {
                    "id": int(account["id"]),

                    "email":
                        account["email"],

                    "is_current":
                        bool(
                            account.get(
                                "is_current",
                                False
                            )
                        ),

                    "created_at":
                        (
                            account["created_at"].isoformat()
                            if account.get("created_at")
                            else None
                        )
                }
            )

        return json_response(
            {
                "success": True,
                "accounts": result
            }
        )

    except Exception as exc:

        print(
            "Previous emails error:",
            exc
        )

        return json_response(
            {
                "success": False,
                "error": str(exc)
            },
            status=500
        )


# =========================================================
# CREATE NEW MAIL.TM ACCOUNT
# =========================================================

async def create_new_mail_account(
    mail_client: MailTMClient
):

    account = await mail_client.create_account()

    return account


# =========================================================
# /api/change-email
# =========================================================

async def api_change_email(
    request: web.Request
):

    auth = get_telegram_user(request)

    if not auth:
        return unauthorized()

    telegram_id = auth["telegram_id"]

    pool = request.app["db_pool"]
    mail_client = request.app["mail_client"]

    try:

        # -------------------------------------------------
        # إنشاء حساب بريد جديد
        # -------------------------------------------------

        account = await create_new_mail_account(
            mail_client
        )

        email = (
            account.get("email")
            or account.get("address")
        )

        password = (
            account.get("password")
            or account.get("mail_password")
        )

        token = (
            account.get("token")
            or account.get("mail_token")
        )

        account_id = (
            account.get("id")
            or account.get("account_id")
        )

        if not email:
            raise RuntimeError(
                "Mail.tm did not return an email address"
            )

        if not password:
            raise RuntimeError(
                "Mail.tm did not return an account password"
            )

        if not token:
            raise RuntimeError(
                "Mail.tm did not return an account token"
            )

        # -------------------------------------------------
        # تحديث المستخدم
        # -------------------------------------------------
        #
        # مهم:
        # نستخدم أسماء المعاملات حتى لا يحدث
        # خلط بين language و email.
        #

        await create_or_update_user(
            pool=pool,
            telegram_id=telegram_id,
            language=None,
            email=email,
            mail_password=password,
            mail_token=token,
            mail_account_id=account_id
        )

        # -------------------------------------------------
        # حفظ البريد في سجل الحسابات
        # -------------------------------------------------

        await save_email_account(
            pool=pool,
            telegram_id=telegram_id,
            email=email,
            mail_password=password,
            mail_token=token,
            mail_account_id=account_id,
            is_current=True
        )

        return json_response(
            {
                "success": True,

                "email": email,

                "user": {
                    "telegram_id": telegram_id,
                    "email": email
                }
            }
        )

    except Exception as exc:

        print(
            "Change email error:",
            exc
        )

        return json_response(
            {
                "success": False,
                "error": str(exc)
            },
            status=500
        )


# =========================================================
# /api/select-email
# =========================================================

async def api_select_email(
    request: web.Request
):

    auth = get_telegram_user(request)

    if not auth:
        return unauthorized()

    telegram_id = auth["telegram_id"]

    pool = request.app["db_pool"]

    try:

        body = await request.json()

        account_id = body.get(
            "account_id"
        )

        if account_id is None:

            return json_response(
                {
                    "success": False,
                    "error": "account_id is required"
                },
                status=400
            )

        # -------------------------------------------------
        # تحويل ID إلى رقم
        # -------------------------------------------------

        try:

            account_id = int(
                account_id
            )

        except (
            TypeError,
            ValueError
        ):

            return json_response(
                {
                    "success": False,
                    "error": "Invalid account_id"
                },
                status=400
            )

        # -------------------------------------------------
        # تبديل البريد
        # -------------------------------------------------

        account = await switch_email_account(
            pool,
            telegram_id,
            account_id
        )

        if not account:

            return json_response(
                {
                    "success": False,
                    "error": "Email account not found"
                },
                status=404
            )

        return json_response(
            {
                "success": True,

                "email":
                    account["email"],

                "user": {
                    "telegram_id":
                        telegram_id,

                    "email":
                        account["email"]
                }
            }
        )

    except Exception as exc:

        print(
            "Select email error:",
            exc
        )

        return json_response(
            {
                "success": False,
                "error": str(exc)
            },
            status=500
        )


# =========================================================
# /api/language
# =========================================================

async def api_language(
    request: web.Request
):

    auth = get_telegram_user(request)

    if not auth:
        return unauthorized()

    telegram_id = auth["telegram_id"]

    try:

        body = await request.json()

        language = body.get(
            "language"
        )

        if language not in (
            "ar",
            "en"
        ):

            return json_response(
                {
                    "success": False,
                    "error": "Invalid language"
                },
                status=400
            )

        await update_language(
            request.app["db_pool"],
            telegram_id,
            language
        )

        return json_response(
            {
                "success": True,
                "language": language
            }
        )

    except Exception as exc:

        print(
            "Language update error:",
            exc
        )

        return json_response(
            {
                "success": False,
                "error": str(exc)
            },
            status=500
        )


# =========================================================
# /api/inbox
# =========================================================

async def api_inbox(
    request: web.Request
):

    auth = get_telegram_user(request)

    if not auth:
        return unauthorized()

    telegram_id = auth["telegram_id"]

    pool = request.app["db_pool"]
    mail_client = request.app["mail_client"]

    try:

        # -------------------------------------------------
        # الحصول على البريد الحالي
        # -------------------------------------------------

        account = await get_current_email_account(
            pool,
            telegram_id
        )

        if account:

            token = account.get(
                "mail_token"
            )

        else:

            user = await get_user(
                pool,
                telegram_id
            )

            if not user or not user.get(
                "email"
            ):

                return json_response(
                    {
                        "success": True,
                        "messages": []
                    }
                )

            token = user.get(
                "mail_token"
            )

        if not token:

            return json_response(
                {
                    "success": True,
                    "messages": []
                }
            )

        # -------------------------------------------------
        # جلب الرسائل من Mail.tm
        # -------------------------------------------------

        messages = await mail_client.get_messages(
            token
        )

        if isinstance(
            messages,
            dict
        ):

            messages = (
                messages.get(
                    "hydra:member"
                )
                or messages.get(
                    "messages"
                )
                or []
            )

        result = []

        for message in messages:

            sender = ""

            sender_data = message.get(
                "from"
            )

            if isinstance(
                sender_data,
                dict
            ):

                sender = (
                    sender_data.get(
                        "address"
                    )
                    or sender_data.get(
                        "name"
                    )
                    or ""
                )

            elif sender_data:

                sender = str(
                    sender_data
                )

            result.append(
                {
                    "id":
                        message.get(
                            "id"
                        ),

                    "subject":
                        message.get(
                            "subject"
                        )
                        or "",

                    "from":
                        sender,

                    "created_at":
                        message.get(
                            "createdAt"
                        )
                }
            )

        return json_response(
            {
                "success": True,
                "messages": result
            }
        )

    except Exception as exc:

        print(
            "Inbox error:",
            exc
        )

        return json_response(
            {
                "success": False,
                "error": str(exc)
            },
            status=500
        )


# =========================================================
# STATIC FILES
# =========================================================

async def index_page(
    request: web.Request
):

    index_path = os.path.join(
        WEB_DIR,
        "index.html"
    )

    return web.FileResponse(
        index_path
    )


# =========================================================
# CREATE WEB APP
# =========================================================

def create_web_app(
    db_pool,
    mail_client
):

    app = web.Application()

    # -----------------------------------------------------
    # Dependencies
    # -----------------------------------------------------

    app["db_pool"] = db_pool
    app["mail_client"] = mail_client

    # -----------------------------------------------------
    # API ROUTES
    # -----------------------------------------------------

    app.router.add_get(
        "/api/me",
        api_me
    )

    app.router.add_get(
        "/api/inbox",
        api_inbox
    )

    app.router.add_get(
        "/api/previous-emails",
        api_previous_emails
    )

    app.router.add_post(
        "/api/change-email",
        api_change_email
    )

    app.router.add_post(
        "/api/select-email",
        api_select_email
    )

    app.router.add_post(
        "/api/language",
        api_language
    )

    # -----------------------------------------------------
    # WEB APP
    # -----------------------------------------------------

    app.router.add_get(
        "/",
        index_page
    )

    app.router.add_static(
        "/",
        WEB_DIR,
        show_index=False
    )

    return app


# =========================================================
# START SERVER
# =========================================================

async def start_web_server(
    db_pool,
    mail_client
):

    app = create_web_app(
        db_pool,
        mail_client
    )

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(
        f"🌐 Temp Mailo Mini App running on port {port}"
    )

    return runner
