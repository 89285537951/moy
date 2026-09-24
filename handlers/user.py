from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InputMediaPhoto, Message, URLInputFile

from database.requests import get_categories, get_furniture_by_category, set_user
from keyboard.keyboard_builder import make_button

router = Router(name="user")


async def send_main_menu(message: Message):
    categories = await get_categories()

    # Динамический список категорий в самом тексте со значками "•"
    categories_list_text = "\n".join([f"• {cat.name}" for cat in categories]) if categories else "• Каталог пополняется"

    # Кнопки категорий с эмодзи 🔹 как на слайде
    buttons = [(f"🔹 {category.name}", f"catalog_category:{category.id}") for category in categories]
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
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await send_main_menu(message)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await send_main_menu(callback.message)
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
async def select_category(callback: CallbackQuery):
    category_id = int(callback.data.split(":", 1)[1])
    categories = await get_categories()
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
        "Отлично! Теперь выберите страну производства:",
        reply_markup=make_button(buttons, sizes=(1,)),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("catalog_country:"))
async def show_products(callback: CallbackQuery):
    _, category_id, country = callback.data.split(":", 2)
    categories = await get_categories()
    category = next((item for item in categories if str(item.id) == category_id), None)
    if category is None:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    products = await get_furniture_by_category(category.name, country)
    if not products:
        await callback.message.edit_text(
            f"⚠️ В категории <b>{category.name}</b> для страны <b>{country}</b> пока нет товаров.",
            reply_markup=make_button([
                ("⬅️ Назад к странам", f"catalog_category:{category.id}"),
                ("🏠 В главное меню", "back_to_main"),
            ], sizes=(1,)),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📦 <b>{category.name}</b> — {country}\n\nНайдено товаров: {len(products)}",
        reply_markup=make_button([
            ("⬅️ Назад к странам", f"catalog_category:{category.id}"),
            ("🏠 В главное меню", "back_to_main"),
        ], sizes=(1,)),
        parse_mode="HTML",
    )
    await callback.answer()

    for index, item in enumerate(products, 1):
        # Эмодзи и структура карточки как на слайдах
        type_line = f"• <b>Тип кухни:</b> {item.furniture_type}\n" if item.furniture_type else ""

        caption = (
            f"📌 <b>{category.name}</b>\n\n"
            f"{item.description}\n\n"
            f"{type_line}"
            f"• <b>Страна производства:</b> {item.country_origin}\n\n"
            f"💬 <b>Для заказа этой мебели:</b>\n"
            f"Telegram: @suleymanovv076\n"
            f"Телефон: +7 (995) 333-44-56\n\n"
            f"<i>Показано {index} из {len(products)} товаров в категории</i>"
        )

        def photo_input(value: str):
            if value.startswith(("http://", "https://")):
                return URLInputFile(value)
            return value

        if not item.photos:
            await callback.message.answer(caption, parse_mode="HTML")
            continue

        if len(item.photos) == 1:
            await callback.message.answer_photo(photo=photo_input(item.photos[0].file_path), caption=caption,
                                                parse_mode="HTML")
        else:
            media = []
            for photo_index, photo in enumerate(item.photos):
                media.append(
                    InputMediaPhoto(
                        media=photo_input(photo.file_path),
                        caption=caption if photo_index == 0 else None,
                        parse_mode="HTML" if photo_index == 0 else None,
                    )
                )
            await callback.message.answer_media_group(media=media)