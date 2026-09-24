from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from database.requests import is_admin


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return await is_admin(event.from_user.id)
