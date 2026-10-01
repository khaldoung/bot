import os
from datetime import datetime

import asyncpg


DATABASE_URL = postgresql://neondb_owner:npg_l1N7iYKCEaHB@ep-little-dream-ayhex1ku-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require


# =========================================================
# DATETIME
# =========================================================

def normalize_datetime(value):
    """
    تحويل وقت Mail.tm من string إلى datetime
    حتى يقبله PostgreSQL TIMESTAMPTZ.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    return None


# =========================================================
# DATABASE POOL
# =========================================================

async def create_pool():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=5,
        command_timeout=30,
    )


# =========================================================
# INIT DATABASE
# =========================================================

async def init_db(pool):

    async with pool.acquire() as conn:

        # =================================================
        # USERS
        # =================================================

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,

                language VARCHAR(5) NOT NULL DEFAULT 'en',

                email VARCHAR(255),
                mail_password TEXT,
                mail_token TEXT,
                mail_account_id VARCHAR(255),

                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

        # في حالة كان الجدول قديمًا
        await conn.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS mail_account_id VARCHAR(255);
        """)

        # =================================================
        # EMAIL ACCOUNTS
        # =================================================

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS email_accounts (
                id BIGSERIAL PRIMARY KEY,

                telegram_id BIGINT NOT NULL,

                email VARCHAR(255) NOT NULL,
                mail_password TEXT,
                mail_token TEXT,
                mail_account_id VARCHAR(255),

                is_current BOOLEAN NOT NULL DEFAULT FALSE,

                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                UNIQUE (
                    telegram_id,
                    email
                )
            );
        """)

        # منع وجود أكثر من بريد حالي للمستخدم
        await conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            one_current_email_per_user
            ON email_accounts (telegram_id)
            WHERE is_current = TRUE;
        """)

        # =================================================
        # MESSAGES
        # =================================================

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id BIGSERIAL PRIMARY KEY,

                telegram_id BIGINT NOT NULL,

                mail_message_id VARCHAR(255) NOT NULL,

                subject TEXT,
                sender_name TEXT,
                sender_address TEXT,
                message_text TEXT,

                received_at TIMESTAMPTZ,
                sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                UNIQUE (
                    telegram_id,
                    mail_message_id
                )
            );
        """)


# =========================================================
# USERS
# =========================================================

async def get_user(
    pool,
    telegram_id,
):
    async with pool.acquire() as conn:

        return await conn.fetchrow(
            """
            SELECT *
            FROM users
            WHERE telegram_id = $1
            """,
            telegram_id,
        )


async def create_or_update_user(
    pool,
    telegram_id,
    language="en",
    email=None,
    mail_password=None,
    mail_token=None,
    mail_account_id=None,
):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            INSERT INTO users (
                telegram_id,
                language,
                email,
                mail_password,
                mail_token,
                mail_account_id
            )

            VALUES (
                $1, $2, $3, $4, $5, $6
            )

            ON CONFLICT (telegram_id)

            DO UPDATE SET

                language = COALESCE(
                    $2,
                    users.language
                ),

                email = COALESCE(
                    $3,
                    users.email
                ),

                mail_password = COALESCE(
                    $4,
                    users.mail_password
                ),

                mail_token = COALESCE(
                    $5,
                    users.mail_token
                ),

                mail_account_id = COALESCE(
                    $6,
                    users.mail_account_id
                ),

                updated_at = NOW()
            """,

            telegram_id,
            language,
            email,
            mail_password,
            mail_token,
            mail_account_id,
        )


async def update_language(
    pool,
    telegram_id,
    language,
):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE users

            SET
                language = $1,
                updated_at = NOW()

            WHERE telegram_id = $2
            """,

            language,
            telegram_id,
        )


# =========================================================
# EMAIL ACCOUNTS
# =========================================================

async def save_email_account(
    pool,
    telegram_id,
    email,
    mail_password,
    mail_token,
    mail_account_id,
    is_current=True,
):

    async with pool.acquire() as conn:

        async with conn.transaction():

            # إذا أصبح هذا البريد الحالي
            if is_current:

                await conn.execute(
                    """
                    UPDATE email_accounts

                    SET
                        is_current = FALSE,
                        updated_at = NOW()

                    WHERE telegram_id = $1
                    """,
                    telegram_id,
                )

            await conn.execute(
                """
                INSERT INTO email_accounts (
                    telegram_id,
                    email,
                    mail_password,
                    mail_token,
                    mail_account_id,
                    is_current
                )

                VALUES (
                    $1, $2, $3, $4, $5, $6
                )

                ON CONFLICT (
                    telegram_id,
                    email
                )

                DO UPDATE SET

                    mail_password = EXCLUDED.mail_password,
                    mail_token = EXCLUDED.mail_token,
                    mail_account_id = EXCLUDED.mail_account_id,
                    is_current = EXCLUDED.is_current,
                    updated_at = NOW()
                """,

                telegram_id,
                email,
                mail_password,
                mail_token,
                mail_account_id,
                is_current,
            )


async def get_email_accounts(
    pool,
    telegram_id,
):

    async with pool.acquire() as conn:

        return await conn.fetch(
            """
            SELECT
                id,
                email,
                mail_account_id,
                is_current,
                created_at,
                updated_at

            FROM email_accounts

            WHERE telegram_id = $1

            ORDER BY
                is_current DESC,
                created_at DESC
            """,

            telegram_id,
        )


async def get_current_email_account(
    pool,
    telegram_id,
):

    async with pool.acquire() as conn:

        return await conn.fetchrow(
            """
            SELECT *

            FROM email_accounts

            WHERE telegram_id = $1
              AND is_current = TRUE

            LIMIT 1
            """,

            telegram_id,
        )


async def get_email_account(
    pool,
    telegram_id,
    account_id,
):

    async with pool.acquire() as conn:

        return await conn.fetchrow(
            """
            SELECT *

            FROM email_accounts

            WHERE telegram_id = $1
              AND id = $2

            LIMIT 1
            """,

            telegram_id,
            account_id,
        )


async def switch_email_account(
    pool,
    telegram_id,
    account_id,
):

    async with pool.acquire() as conn:

        async with conn.transaction():

            account = await conn.fetchrow(
                """
                SELECT *

                FROM email_accounts

                WHERE telegram_id = $1
                  AND id = $2

                LIMIT 1
                """,

                telegram_id,
                account_id,
            )

            if not account:
                return None

            # إلغاء البريد الحالي
            await conn.execute(
                """
                UPDATE email_accounts

                SET
                    is_current = FALSE,
                    updated_at = NOW()

                WHERE telegram_id = $1
                """,

                telegram_id,
            )

            # جعل البريد المختار حاليًا
            await conn.execute(
                """
                UPDATE email_accounts

                SET
                    is_current = TRUE,
                    updated_at = NOW()

                WHERE telegram_id = $1
                  AND id = $2
                """,

                telegram_id,
                account_id,
            )

            # تحديث users أيضًا
            await conn.execute(
                """
                UPDATE users

                SET
                    email = $1,
                    mail_password = $2,
                    mail_token = $3,
                    mail_account_id = $4,
                    updated_at = NOW()

                WHERE telegram_id = $5
                """,

                account["email"],
                account["mail_password"],
                account["mail_token"],
                account["mail_account_id"],
                telegram_id,
            )

            return account


# =========================================================
# USERS EMAIL
# =========================================================

async def update_email(
    pool,
    telegram_id,
    email,
    mail_password,
    mail_token,
    mail_account_id,
):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE users

            SET
                email = $1,
                mail_password = $2,
                mail_token = $3,
                mail_account_id = $4,
                updated_at = NOW()

            WHERE telegram_id = $5
            """,

            email,
            mail_password,
            mail_token,
            mail_account_id,
            telegram_id,
        )


async def clear_email(
    pool,
    telegram_id,
):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE users

            SET
                email = NULL,
                mail_password = NULL,
                mail_token = NULL,
                mail_account_id = NULL,
                updated_at = NOW()

            WHERE telegram_id = $1
            """,

            telegram_id,
        )


async def get_users_with_email(pool):

    async with pool.acquire() as conn:

        return await conn.fetch(
            """
            SELECT
                telegram_id,
                language,
                email,
                mail_token

            FROM users

            WHERE email IS NOT NULL
              AND mail_token IS NOT NULL
            """
        )


# =========================================================
# MESSAGES
# =========================================================

async def message_exists(
    pool,
    telegram_id,
    mail_message_id,
):

    async with pool.acquire() as conn:

        result = await conn.fetchval(
            """
            SELECT 1

            FROM messages

            WHERE telegram_id = $1
              AND mail_message_id = $2

            LIMIT 1
            """,

            telegram_id,
            mail_message_id,
        )

        return result is not None


async def claim_message(
    pool,
    telegram_id,
    mail_message_id,
):

    async with pool.acquire() as conn:

        result = await conn.fetchval(
            """
            INSERT INTO messages (
                telegram_id,
                mail_message_id
            )

            VALUES ($1, $2)

            ON CONFLICT (
                telegram_id,
                mail_message_id
            )

            DO NOTHING

            RETURNING id
            """,

            telegram_id,
            mail_message_id,
        )

        return result is not None


async def delete_message_claim(
    pool,
    telegram_id,
    mail_message_id,
):

    async with pool.acquire() as conn:

        await conn.execute(
            """
            DELETE FROM messages

            WHERE telegram_id = $1
              AND mail_message_id = $2
            """,

            telegram_id,
            mail_message_id,
        )


async def update_saved_message(
    pool,
    telegram_id,
    mail_message_id,
    subject=None,
    sender_name=None,
    sender_address=None,
    message_text=None,
    received_at=None,
):

    received_at = normalize_datetime(
        received_at
    )

    async with pool.acquire() as conn:

        await conn.execute(
            """
            UPDATE messages

            SET
                subject = $3,
                sender_name = $4,
                sender_address = $5,
                message_text = $6,
                received_at = $7,
                sent_at = NOW()

            WHERE telegram_id = $1
              AND mail_message_id = $2
            """,

            telegram_id,
            mail_message_id,
            subject,
            sender_name,
            sender_address,
            message_text,
            received_at,
        )


async def save_message(
    pool,
    telegram_id,
    mail_message_id,
    subject=None,
    sender_name=None,
    sender_address=None,
    message_text=None,
    received_at=None,
):

    received_at = normalize_datetime(
        received_at
    )

    async with pool.acquire() as conn:

        await conn.execute(
            """
            INSERT INTO messages (
                telegram_id,
                mail_message_id,
                subject,
                sender_name,
                sender_address,
                message_text,
                received_at
            )

            VALUES (
                $1, $2, $3, $4, $5, $6, $7
            )

            ON CONFLICT (
                telegram_id,
                mail_message_id
            )

            DO NOTHING
            """,

            telegram_id,
            mail_message_id,
            subject,
            sender_name,
            sender_address,
            message_text,
            received_at,
        )
