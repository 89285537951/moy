import os
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

load_dotenv()

_admin_raw = os.getenv("ADMIN_IDS") or os.getenv("ADMIN_ID") or ""
ADMIN_IDS = [int(x.strip()) for x in _admin_raw.replace(";", ",").split(",") if x.strip().isdigit()]


class IsAdmin(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        if not event.from_user:
            return False
        return event.from_user.id in ADMIN_IDS