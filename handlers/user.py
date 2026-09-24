from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InputMediaPhoto, Message, URLInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import CrudCategory, CrudFurniture, CrudUser
from keyboard.keyboard_builder import make_button

router = Router(name="user")


async def send_main_menu(message: Message, session: AsyncSession):
    crud = CrudCategory(session)
    categories = await crud.get_all_categories()

    categories_list_text = "\n".join([f"• {cat.name}" for cat in categories]) if categories else "• Каталог пополняется"
    buttons = [(f"🔹 {category.name}", f"catalog_category:{category.id}") for category in
               categories] if categories else []
    buttons += [
        ("ℹ️ О компании / Контакты", "about_company"),
        ("🤝 Сотрудничество", "cooperation_company"),
    ]

    await message.answer(
        "⭐️ <b>Добро пожаловать в наш мебельный бот!</b> ⭐️\n\n"
        "Здесь вы найдете стильную и качественную мебель для любого интерьера.\n\n"
        "📦 <b>Наш каталог включает:</b>\n"
        f"{categories_list_text}\n\n"
        "🛠 <b>Как сделать заказ:</b>\n"
        "1. Выберите категорию мебели\n"
        "2. Просмотрите модели\n"
        "3. Свяжитесь с нами для заказа\n\n"
        "👇 <b>Выберите категорию из меню ниже:</b>",
        reply_markup=make_button(buttons, sizes=(1,)),
        parse_mode="HTML",
    )


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    crud_user = CrudUser(session)
    await crud_user.set_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    await send_main_menu(message, session)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, session: AsyncSession):
    crud = CrudCategory(session)
    categories = await crud.get_all_categories()

    categories_list_text = "\n".join([f"• {cat.name}" for cat in categories]) if categories else "• Каталог пополняется"
    buttons = [(f"🔹 {category.name}", f"catalog_category:{category.id}") for category in
               categories] if categories else []
    buttons += [
        ("ℹ️ О компании / Контакты", "about_company"),
        ("🤝 Сотрудничество", "cooperation_company"),
    ]

    text = (
        "⭐️ <b>Добро пожаловать в наш мебельный бот!</b> ⭐️\n\n"
        "Здесь вы найдете стильную и качественную мебель для любого интерьера.\n\n"
        "📦 <b>Наш каталог включает:</b>\n"
        f"{categories_list_text}\n\n"
        "🛠 <b>Как сделать заказ:</b>\n"
        "1. Выберите категорию мебели\n"
        "2. Просмотрите модели\n"
        "3. Свяжитесь с нами для заказа\n\n"
        "👇 <b>Выберите категорию из меню ниже:</b>"
    )
    await callback.message.edit_text(text, reply_markup=make_button(buttons, sizes=(1,)), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "about_company")
async def about_company(callback: CallbackQuery):
    text = (
        "ℹ️ <b>О нашей компании</b>\n\n"
        "Мы создаем и поставляем качественную современную мебель для дома и офиса.\n\n"
        "📍 <b>Адрес:</b> г. Грозный, ул. Мебельная, д. 15\n"
        "📞 <b>Телефон:</b> +7 (995) 333-44-56\n"
        "🕘 <b>График:</b> Пн-Вс 09:00–20:00"
    )
    await callback.message.edit_text(text, reply_markup=make_button([("⬅️ Назад", "back_to_main")], sizes=(1,)),
                                     parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "cooperation_company")
async def cooperation(callback: CallbackQuery):
    text = (
        "🤝 <b>Сотрудничество</b>\n\n"
        "Приглашаем к сотрудничеству дизайнеров, архитекторов, дилеров и поставщиков.\n\n"
        "📧 ansarium@mail.ru\n"
        "Telegram: @suleymanovv076"
    )
    await callback.message.edit_text(text, reply_markup=make_button([("⬅️ Назад", "back_to_main")], sizes=(1,)),
                                     parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("catalog_category:"))
async def select_category(callback: CallbackQuery, session: AsyncSession):
    category_id = int(callback.data.split(":", 1)[1])
    crud = CrudCategory(session)
    categories = await crud.get_all_categories()

    category = next((item for item in categories if item.id == category_id), None)
    if category is None:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    buttons = [
        ("🇷🇺 Россия", f"catalog_country:{category.id}:Россия"),
        ("🇹🇷 Турция", f"catalog_country:{category.id}:Турция"),
        ("⬅️ Назад", "back_to_main"),
    ]
    await callback.message.edit_text(
        f"Отлично! Вы выбрали <b>{category.name}</b>.\nТеперь выберите страну производства:",
        reply_markup=make_button(buttons, sizes=(1,)),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("catalog_country:"))
async def show_products(callback: CallbackQuery, session: AsyncSession):
    _, category_id, country = callback.data.split(":", 2)

    crud_cat = CrudCategory(session)
    categories = await crud_cat.get_all_categories()
    category = next((item for item in categories if str(item.id) == category_id), None)

    if category is None:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    crud_furn = CrudFurniture(session)
    filtered_products = await crud_furn.get_by_category_and_country(
        category_id=category.id,
        country_name=country,
    )

    if not filtered_products:
        await callback.message.edit_text(
            f"⚠️ В категории <b>{category.name}</b> ({country}) пока нет товаров.",
            reply_markup=make_button([
                ("⬅️ Назад к странам", f"catalog_category:{category.id}"),
                ("🏠 В главное меню", "back_to_main"),
            ], sizes=(1,)),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📦 <b>{category.name}</b> — {country}\n\nНайдено товаров: {len(filtered_products)}",
        reply_markup=make_button([
            ("⬅️ Назад к странам", f"catalog_category:{category.id}"),
            ("🏠 В главное меню", "back_to_main"),
        ], sizes=(1,)),
        parse_mode="HTML",
    )
    await callback.answer()

    # ─── Показ товаров ───
    for index, item in enumerate(filtered_products, 1):
        f_type = getattr(item, 'furniture_type', getattr(item, 'type', ''))
        type_name = f_type.name if hasattr(f_type, 'name') else f_type
        type_line = f"• <b>Тип мебели:</b> {type_name}\n" if type_name else ""

        caption = (
            f"📌 <b>{item.title if hasattr(item, 'title') else category.name}</b>\n\n"
            f"{item.description}\n\n"
            f"{type_line}"
            f"• <b>Страна производства:</b> {country}\n\n"
            f"💬 <b>Для заказа этой мебели:</b>\n"
            f"Telegram: @suleymanovv076\n"
            f"Телефон: +7 (995) 333-44-56\n\n"
            f"<i>Показано {index} из {len(filtered_products)} товаров в категории</i>"
        )

        def get_photo_val(photo_obj):
            val = getattr(photo_obj, 'file_id', getattr(photo_obj, 'photo_id', ''))
            if isinstance(val, str) and val.startswith(("http://", "https://")):
                return URLInputFile(val)
            return val

        item_photos = await crud_furn.get_furniture_photos(item.id)

        if not item_photos:
            await callback.message.answer(caption, parse_mode="HTML")
            continue

        if len(item_photos) == 1:
            await callback.message.answer_photo(
                photo=get_photo_val(item_photos[0]),
                caption=caption,
                parse_mode="HTML"
            )
        else:
            media = []
            for photo_index, photo in enumerate(item_photos[:10]):
                media.append(
                    InputMediaPhoto(
                        media=get_photo_val(photo),
                        caption=caption if photo_index == 0 else None,
                        parse_mode="HTML" if photo_index == 0 else None,
                    )
                )
            await callback.message.answer_media_group(media=media)

    # ─── Кнопки навигации ПОСЛЕ всех товаров ───
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=make_button([
            ("⬅️ Назад к странам", f"catalog_category:{category.id}"),
            ("🏠 В главное меню", "back_to_main"),
        ], sizes=(1,))
    )