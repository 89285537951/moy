from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from utils.admin_filter import IsAdmin

from database.requests import add_category, add_furniture, get_all_furniture, get_categories, delete_furniture
from keyboard.button_template import admin_kb, build_cancel_kb, country_of_origin_kb, furniture_cancel_kb, kitchen_type_kb
from keyboard.keyboard_builder import make_button
from states.states import AddCategoryState, AddFurnitureState

router = Router(name="admin_main")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin_panel"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔧 <b>Панель администратора</b>\nВыберите действие:", reply_markup=make_button(admin_kb, sizes=(2, 2, 1)), parse_mode="HTML")


@router.callback_query(F.data == "settings_bot")
async def settings_bot(callback: CallbackQuery):
    await callback.message.edit_text("🔧 <b>Панель администратора</b>\nВыберите действие:", reply_markup=make_button(admin_kb, sizes=(2, 2, 1)), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🔧 <b>Панель администратора</b>\nВыберите действие:", reply_markup=make_button(admin_kb, sizes=(2, 2, 1)), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "new_category_furniture")
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategoryState.name)
    await callback.message.edit_text("Введите название новой категории:", reply_markup=make_button(build_cancel_kb, sizes=(1,)))
    await callback.answer()


@router.message(AddCategoryState.name)
async def process_cat_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("⚠️ Название не может быть пустым.")
        return
    await state.update_data(name=name)
    await state.set_state(AddCategoryState.description)
    await message.answer("Введите описание категории или напишите «пропустить»:", reply_markup=make_button(build_cancel_kb, sizes=(1,)))


@router.message(AddCategoryState.description)
async def process_cat_desc(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("⚠️ Отправьте текстовое описание или «пропустить».")
        return
    data = await state.get_data()
    description = None if text.lower() == "пропустить" else text
    success = await add_category(data["name"], description)
    await state.clear()
    await message.answer(
        "✅ Категория создана." if success else "⚠️ Такая категория уже существует.",
        reply_markup=make_button(admin_kb, sizes=(2, 2, 1)),
    )


@router.callback_query(F.data == "new_furniture")
async def start_add_furniture(callback: CallbackQuery, state: FSMContext):
    categories = await get_categories()
    if not categories:
        await callback.answer("Сначала добавьте категорию.", show_alert=True)
        return

    buttons = [(category.name, f"admin_category:{category.id}") for category in categories]
    buttons.append(("⬅️ Назад", "back_to_admin"))
    await state.set_state(AddFurnitureState.category)
    await callback.message.edit_text("Шаг 1. Выберите категорию:", reply_markup=make_button(buttons, sizes=(1,)))
    await callback.answer()


@router.callback_query(AddFurnitureState.category, F.data.startswith("admin_category:"))
async def select_admin_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":", 1)[1])
    categories = await get_categories()
    category = next((item for item in categories if item.id == category_id), None)
    if category is None:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    await state.update_data(category_name=category.name)
    if category.name.lower() in {"кухонная мебель", "кухни"}:
        await state.set_state(AddFurnitureState.kitchen_type)
        await callback.message.edit_text("Шаг 2. Выберите тип кухни:", reply_markup=make_button(kitchen_type_kb, sizes=(1,)))
    else:
        await state.set_state(AddFurnitureState.country)
        await callback.message.edit_text("Шаг 2. Выберите страну производства:", reply_markup=make_button(country_of_origin_kb, sizes=(1,)))
    await callback.answer()


@router.callback_query(AddFurnitureState.kitchen_type, F.data.in_({"straight_kitchen", "corner_kitchen"}))
async def select_kitchen_type(callback: CallbackQuery, state: FSMContext):
    kitchen_type = {"straight_kitchen": "Прямая кухня", "corner_kitchen": "Угловая кухня"}[callback.data]
    await state.update_data(furniture_type=kitchen_type)
    await state.set_state(AddFurnitureState.country)
    await callback.message.edit_text("Шаг 3. Выберите страну производства:", reply_markup=make_button(country_of_origin_kb, sizes=(1,)))
    await callback.answer()


@router.callback_query(AddFurnitureState.country, F.data.in_({"russia_origin", "turkey_origin"}))
async def select_country(callback: CallbackQuery, state: FSMContext):
    country = {"russia_origin": "Россия", "turkey_origin": "Турция"}[callback.data]
    await state.update_data(country_origin=country)
    await state.set_state(AddFurnitureState.description)
    await callback.message.edit_text("Следующий шаг. Отправьте полное описание товара:", reply_markup=make_button(furniture_cancel_kb, sizes=(1,)))
    await callback.answer()


@router.callback_query(F.data.in_({"cancel_category", "cancel_furniture"}))
async def cancel_admin_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено.", reply_markup=make_button(admin_kb, sizes=(2, 2, 1)))
    await callback.answer()


@router.callback_query(AddFurnitureState.kitchen_type, F.data == "back_to_categories")
@router.callback_query(AddFurnitureState.country, F.data == "back_to_categories")
async def back_from_furniture_step(callback: CallbackQuery, state: FSMContext):
    categories = await get_categories()
    buttons = [(category.name, f"admin_category:{category.id}") for category in categories]
    buttons.append(("⬅️ Назад", "back_to_admin"))
    await state.set_state(AddFurnitureState.category)
    await callback.message.edit_text("Шаг 1. Выберите категорию:", reply_markup=make_button(buttons, sizes=(1,)))
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
        reply_markup=make_button([("Завершить загрузку фото", "finish_photos"), ("❌ Отменить", "cancel_furniture")], sizes=(1,)),
    )


@router.message(AddFurnitureState.photos, F.photo)
async def process_furniture_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 10:
        await message.answer("⚠️ Максимум 10 фотографий.")
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"📸 Фото получено: {len(photos)}/10")


@router.callback_query(AddFurnitureState.photos, F.data == "finish_photos")
async def finish_furniture(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await callback.answer("Загрузите хотя бы 1 фотографию.", show_alert=True)
        return

    await add_furniture(
        description=data["description"],
        category_name=data["category_name"],
        country_origin=data["country_origin"],
        furniture_type=data.get("furniture_type"),
        photos=photos,
    )
    await state.clear()
    await callback.message.edit_text("✅ Мебель успешно добавлена в каталог.", reply_markup=make_button(admin_kb, sizes=(2, 2, 1)))
    await callback.answer()


@router.callback_query(F.data == "remowed_furniture")
async def start_delete_furniture(callback: CallbackQuery):
    furniture_list = await get_all_furniture()
    if not furniture_list:
        await callback.answer("В базе данных нет мебели.", show_alert=True)
        return
    buttons = [
        (f"🗑 {item.id} | {item.category_name} | {item.description[:30]}", f"delete_furniture:{item.id}")
        for item in furniture_list
    ]
    buttons.append(("⬅️ Назад", "back_to_admin"))
    await callback.message.edit_text("🗑 <b>Выберите мебель для удаления:</b>", reply_markup=make_button(buttons, sizes=(1,)), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("delete_furniture:"))
async def delete_furniture_handler(callback: CallbackQuery):
    furniture_id = int(callback.data.split(":", 1)[1])
    if not await delete_furniture(furniture_id):
        await callback.answer("Товар не найден.", show_alert=True)
        return
    await callback.answer("✅ Мебель удалена.", show_alert=True)
    furniture_list = await get_all_furniture()
    if not furniture_list:
        await callback.message.edit_text("🗑 Все товары удалены.", reply_markup=make_button([("⬅️ Назад", "back_to_admin")], sizes=(1,)))
        return
    buttons = [(f"🗑 {item.id} | {item.category_name} | {item.description[:30]}", f"delete_furniture:{item.id}") for item in furniture_list]
    buttons.append(("⬅️ Назад", "back_to_admin"))
    await callback.message.edit_text("🗑 <b>Выберите мебель для удаления:</b>", reply_markup=make_button(buttons, sizes=(1,)), parse_mode="HTML")
