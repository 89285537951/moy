from aiogram import F, Router
from aiogram.types import CallbackQuery

from utils.admin_filter import IsAdmin

from database.requests import get_categories
from keyboard.keyboard_builder import make_button

router = Router(name="admin_categories")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "list_categories")
async def list_category_furniture(callback: CallbackQuery):
    categories = await get_categories()

    if not categories:
        await callback.message.edit_text(
            "📋 Категорий пока нет.",
            reply_markup=make_button([("⬅️ Назад", "back_to_admin")], sizes=(1,)),
        )
        await callback.answer()
        return

    text = "📋 <b>Список категорий:</b>\n\n"
    text += "\n".join(f"{index}. {category.name} — ID: {category.id}" for index, category in enumerate(categories, 1))

    await callback.message.edit_text(
        text,
        reply_markup=make_button([("⬅️ Назад", "back_to_admin")], sizes=(1,)),
        parse_mode="HTML",
    )
    await callback.answer()
