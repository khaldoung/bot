import secrets
import string
from typing import Optional

import httpx


class MailTMError(Exception):
    """خطأ خاص بخدمة Mail.tm."""
    pass


class MailTMClient:
    BASE_URL = "https://api.mail.tm"

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    async def close(self):
        await self.client.aclose()

    async def get_domains(self):
        """جلب النطاقات المتاحة من Mail.tm."""

        try:
            response = await self.client.get("/domains")
            response.raise_for_status()

        except httpx.HTTPError as e:
            raise MailTMError(
                f"Failed to get domains: {e}"
            )

        data = response.json()

        # Mail.tm قد يرجع البيانات كقائمة مباشرة
        # أو داخل hydra:member.
        if isinstance(data, list):
            items = data

        elif isinstance(data, dict):
            items = data.get("hydra:member", [])

        else:
            items = []

        domains = []

        for item in items:
            if not isinstance(item, dict):
                continue

            # بعض استجابات Mail.tm تحتوي isActive
            # وبعضها قد لا تحتويه، لذلك نتحقق من وجود النطاق.
            domain = item.get("domain")

            if not domain:
                continue

            # إذا كانت isActive موجودة يجب أن تكون True.
            if "isActive" in item and item["isActive"] is not True:
                continue

            domains.append(domain)

        if not domains:
            raise MailTMError(
                "No active Mail.tm domains available."
            )

        return domains

    @staticmethod
    def generate_username(length: int = 12):
        """إنشاء اسم عشوائي لصندوق البريد."""

        characters = (
            string.ascii_lowercase
            + string.digits
        )

        return "tm" + "".join(
            secrets.choice(characters)
            for _ in range(length)
        )

    @staticmethod
    def generate_password(length: int = 24):
        """إنشاء كلمة مرور قوية لحساب Mail.tm."""

        characters = (
            string.ascii_letters
            + string.digits
            + "!@#$%^&*"
        )

        return "".join(
            secrets.choice(characters)
            for _ in range(length)
        )

    async def create_account(
        self,
        username: Optional[str] = None,
        max_attempts: int = 10,
    ):
        """
        إنشاء صندوق بريد جديد.

        إذا كان الاسم مستخدمًا من قبل،
        يتم إنشاء اسم آخر تلقائيًا.
        """

        domains = await self.get_domains()

        for _ in range(max_attempts):

            if username:
                local_part = username
            else:
                local_part = self.generate_username()

            domain = secrets.choice(domains)

            email = f"{local_part}@{domain}"
            password = self.generate_password()

            try:
                response = await self.client.post(
                    "/accounts",
                    json={
                        "address": email,
                        "password": password,
                    },
                )

                if response.status_code == 201:
                    account = response.json()

                    token_data = await self.get_token(
                        email,
                        password,
                    )

                    return {
                        "id": account.get("id"),
                        "email": email,
                        "password": password,
                        "token": token_data["token"],
                    }

                # الاسم مستخدم مسبقًا
                # أو البيانات غير مقبولة.
                if response.status_code in (
                    400,
                    409,
                    422,
                ):
                    username = None
                    continue

                raise MailTMError(
                    "Mail.tm account creation failed: "
                    f"{response.status_code} "
                    f"{response.text}"
                )

            except httpx.HTTPError as e:
                raise MailTMError(
                    "Connection error while "
                    f"creating account: {e}"
                )

        raise MailTMError(
            "Could not create a unique "
            "Mail.tm account."
        )

    async def get_token(
        self,
        email: str,
        password: str,
    ):
        """الحصول على Token لحساب Mail.tm."""

        try:
            response = await self.client.post(
                "/token",
                json={
                    "address": email,
                    "password": password,
                },
            )

        except httpx.HTTPError as e:
            raise MailTMError(
                "Connection error while "
                f"getting token: {e}"
            )

        if response.status_code != 200:
            raise MailTMError(
                "Could not get Mail.tm token: "
                f"{response.status_code}"
            )

        return response.json()

    async def get_messages(
        self,
        token: str,
        page: int = 1,
    ):
        """جلب الرسائل الموجودة في صندوق البريد."""

        try:
            response = await self.client.get(
                "/messages",
                params={
                    "page": page,
                },
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

        except httpx.HTTPError as e:
            raise MailTMError(
                "Connection error while "
                f"getting messages: {e}"
            )

        if response.status_code != 200:
            raise MailTMError(
                "Could not get messages: "
                f"{response.status_code}"
            )

        return response.json()

    async def get_message(
        self,
        token: str,
        message_id: str,
    ):
        """جلب تفاصيل رسالة واحدة."""

        try:
            response = await self.client.get(
                f"/messages/{message_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

        except httpx.HTTPError as e:
            raise MailTMError(
                "Connection error while "
                f"getting message: {e}"
            )

        if response.status_code != 200:
            raise MailTMError(
                "Could not get message: "
                f"{response.status_code}"
            )

        return response.json()

    async def delete_account(
        self,
        token: str,
        account_id: str,
    ):
        """حذف حساب Mail.tm القديم."""

        try:
            response = await self.client.delete(
                f"/accounts/{account_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

        except httpx.HTTPError as e:
            raise MailTMError(
                "Connection error while "
                f"deleting account: {e}"
            )

        if response.status_code not in (
            200,
            204,
        ):
            raise MailTMError(
                "Could not delete account: "
                f"{response.status_code}"
            )

        return True
