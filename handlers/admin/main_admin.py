from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from utils.admin_filter import IsAdmin
from database.crud import CrudCategory, CrudFurniture, CrudCountry, CrudFurnitureType
from database.models import Furniture

from keyboard.button_template import (
    admin_kb, build_cancel_kb, country_of_origin_kb,
    furniture_cancel_kb, kitchen_type_kb,
)
from keyboard.keyboard_builder import make_button
from states.states import AddCategoryState, AddFurnitureState

router = Router(name="admin_main")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin_panel"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔧 <b>Панель администратора</b>\nВыберите действие:",
                         reply_markup=make_button(admin_kb, sizes=(2, 2, 1)), parse_mode="HTML")


@router.callback_query(F.data == "settings_bot")
async def settings_bot(callback: CallbackQuery):
    await callback.message.edit_text("🔧 <b>Панель администратора</b>\nВыберите действие:",
                                     reply_markup=make_button(admin_kb, sizes=(2, 2, 1)), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🔧 <b>Панель администратора</b>\nВыберите действие:",
                                     reply_markup=make_button(admin_kb, sizes=(2, 2, 1)), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "new_category_furniture")
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategoryState.name)
    await callback.message.edit_text("Введите название новой категории:",
                                     reply_markup=make_button(build_cancel_kb, sizes=(1,)))
    await callback.answer()


@router.message(AddCategoryState.name)
async def process_cat_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("⚠️ Название не может быть пустым.")
        return
    await state.update_data(name=name)
    await state.set_state(AddCategoryState.description)
    await message.answer("Введите описание категории или напишите «пропустить»:",
                         reply_markup=make_button(build_cancel_kb, sizes=(1,)))


@router.message(AddCategoryState.description)
async def process_cat_desc(message: Message, state: FSMContext, session: AsyncSession):
    text = (message.text or "").strip()
    if not text:
        await message.answer("⚠️ Отправьте текстовое описание или «пропустить».")
        return

    data = await state.get_data()
    crud = CrudCategory(session)
    success = await crud.add_category(name=data["name"])

    await state.clear()
    await message.answer(
        "✅ Категория создана." if success else "⚠️ Ошибка при создании категории.",
        reply_markup=make_button(admin_kb, sizes=(2, 2, 1)),
    )


@router.callback_query(F.data == "new_furniture")
async def start_add_furniture(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    crud = CrudCategory(session)
    categories = await crud.get_all_categories()

    if not categories:
        await callback.answer("Сначала добавьте категорию.", show_alert=True)
        return

    buttons = [(category.name, f"admin_category:{category.id}") for category in categories]
    buttons.append(("⬅️ Назад", "back_to_admin"))
    await state.set_state(AddFurnitureState.category)
    await callback.message.edit_text("Шаг 1. Выберите категорию:",
                                     reply_markup=make_button(buttons, sizes=(1,)))
    await callback.answer()


@router.callback_query(AddFurnitureState.category, F.data.startswith("admin_category:"))
async def select_admin_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    category_id = int(callback.data.split(":", 1)[1])

    crud = CrudCategory(session)
    categories = await crud.get_all_categories()

    category = next((item for item in categories if item.id == category_id), None)
    if category is None:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    await state.update_data(category_id=category.id, category_name=category.name)

    if category.name.lower() in {"кухонная мебель", "кухни"}:
        await state.set_state(AddFurnitureState.kitchen_type)
        await callback.message.edit_text("Шаг 2. Выберите тип кухни:",
                                         reply_markup=make_button(kitchen_type_kb, sizes=(1,)))
    else:
        await state.update_data(furniture_type="Обычная")
        await state.set_state(AddFurnitureState.country)
        await callback.message.edit_text("Шаг 2. Выберите страну производства:",
                                         reply_markup=make_button(country_of_origin_kb, sizes=(1,)))
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    crud = CrudCategory(session)
    categories = await crud.get_all_categories()
    buttons = [(c.name, f"admin_category:{c.id}") for c in categories]
    buttons.append(("⬅️ Назад", "back_to_admin"))
    await state.set_state(AddFurnitureState.category)
    await callback.message.edit_text("Шаг 1. Выберите категорию:",
                                     reply_markup=make_button(buttons, sizes=(1,)))
    await callback.answer()


@router.callback_query(AddFurnitureState.kitchen_type, F.data.in_({"straight_kitchen", "corner_kitchen"}))
async def select_kitchen_type(callback: CallbackQuery, state: FSMContext):
    kitchen_type = {"straight_kitchen": "Прямая кухня", "corner_kitchen": "Угловая кухня"}[callback.data]
    await state.update_data(furniture_type=kitchen_type)
    await state.set_state(AddFurnitureState.country)
    await callback.message.edit_text("Шаг 3. Выберите страну производства:",
                                     reply_markup=make_button(country_of_origin_kb, sizes=(1,)))
    await callback.answer()


@router.callback_query(AddFurnitureState.country, F.data.in_({"russia_origin", "turkey_origin"}))
async def select_country(callback: CallbackQuery, state: FSMContext):
    country = {"russia_origin": "Россия", "turkey_origin": "Турция"}[callback.data]
    await state.update_data(country_origin=country)
    await state.set_state(AddFurnitureState.description)
    await callback.message.edit_text("Следующий шаг. Отправьте полное описание товара:",
                                     reply_markup=make_button(furniture_cancel_kb, sizes=(1,)))
    await callback.answer()


@router.callback_query(F.data.in_({"cancel_category", "cancel_furniture"}))
async def cancel_admin_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено.", reply_markup=make_button(admin_kb, sizes=(2, 2, 1)))
    await callback.answer()


@router.message(AddFurnitureState.description)
async def process_furniture_description(message: Message, state: FSMContext):
    description = (message.text or "").strip()
    if not description:
        await message.answer("⚠️ Описание не может быть пустым.")
        return
    await state.update_data(description=description, photos=[])
    await state.set_state(AddFurnitureState.photos)
    await message.answer(
        "📸 Отправьте от 1 до 10 фотографий.\nПосле этого нажмите «Завершить загрузку фото».",
        reply_markup=make_button([("Завершить загрузку фото", "finish_photos"), ("❌ Отменить", "cancel_furniture")],
                                 sizes=(1,)),
    )


@router.callback_query(F.data == "list_categories")
async def list_categories(callback: CallbackQuery, session: AsyncSession):
    crud = CrudCategory(session)
    categories = await crud.get_all_categories()

    if not categories:
        await callback.message.edit_text(
            "📋 Список категорий пуст.",
            reply_markup=make_button([("⬅️ Назад", "back_to_admin")], sizes=(1,)),
        )
        await callback.answer()
        return

    text = "📋 <b>Список категорий:</b>\n\n"
    for i, cat in enumerate(categories, 1):
        text += f"{i}. {cat.name}\n"

    await callback.message.edit_text(
        text,
        reply_markup=make_button([("⬅️ Назад", "back_to_admin")], sizes=(1,)),
        parse_mode="HTML",
    )
    await callback.answer()

@router.message(AddFurnitureState.photos, F.photo)
async def process_furniture_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 10:
        await message.answer("⚠️ Максимум 10 фотографий. Нажмите «Завершить загрузку фото».")
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"📸 Фото получено: {len(photos)}/10")


@router.callback_query(AddFurnitureState.photos, F.data == "finish_photos")
async def finish_furniture(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await callback.answer("Загрузите хотя бы 1 фотографию.", show_alert=True)
        return

    crud_country = CrudCountry(session)
    crud_type = CrudFurnitureType(session)
    crud_furniture = CrudFurniture(session)

    country_obj = await crud_country.get_or_create_country(data["country_origin"])
    type_obj = await crud_type.get_or_create_type(data["furniture_type"])

    furniture = await crud_furniture.add_furniture(
        title=f"Товар {data['category_name']}",
        description=data["description"],
        category_id=data["category_id"],
        country_id=country_obj.id,
        type_id=type_obj.id,
    )

    for file_id in photos:
        await crud_furniture.add_furniture_photo(furniture_id=furniture.id, file_id=file_id)

    await state.clear()
    await callback.message.edit_text("✅ Товар успешно добавлен и сохранен в базу данных!",
                                     reply_markup=make_button(admin_kb, sizes=(2, 2, 1)))
    await callback.answer()


@router.callback_query(F.data == "delete_furniture_menu")
async def admin_delete_list(callback: CallbackQuery, session: AsyncSession):
    result = await session.execute(select(Furniture))
    products = result.scalars().all()

    if not products:
        await callback.answer("В базе данных пока нет товаров для удаления.", show_alert=True)
        return

    buttons = []
    for product in products:
        buttons.append((f"❌ Удалить: {product.title} (ID: {product.id})", f"confirm_delete:{product.id}"))
    buttons.append(("⬅️ Назад", "back_to_admin"))

    await callback.message.edit_text("Выберите товар, который нужно полностью удалить:",
                                     reply_markup=make_button(buttons, sizes=(1,)))
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete:"))
async def admin_confirm_delete(callback: CallbackQuery, session: AsyncSession):
    furniture_id = int(callback.data.split(":", 1)[1])
    crud_furniture = CrudFurniture(session)
    success = await crud_furniture.delete_furniture(furniture_id)
    if success:
        await callback.message.edit_text("✅ Товар и все связанные фотографии успешно удалены из базы данных!",
                                         reply_markup=make_button(admin_kb, sizes=(2, 2, 1)))
    else:
        await callback.message.edit_text("⚠️ Ошибка: товар не найден в базе данных.",
                                         reply_markup=make_button(admin_kb, sizes=(2, 2, 1)))
    await callback.answer()