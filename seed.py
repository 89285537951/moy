import asyncio
import os
from pathlib import Path

print("=" * 60)
print("Рабочая директория:", os.getcwd())
print("Путь к seed.py:", Path(__file__).resolve())
print("=" * 60)
from sqlalchemy import select

from database.engine import async_main, AsyncSessionLocal
from database.models import Category, Furniture, FurniturePhoto, Country, FurnitureType


ITEMS_DATA = [
    {
        "category_name": "Спальная мебель",
        "country_origin": "Россия",
        "description": (
            "🛏 <b>Кровать двуспальная «Орматек Lux»</b>\n\n"
            "Современная двуспальная кровать с мягким изголовьем из велюра. "
            "Оснащена ортопедическим основанием и подъемным механизмом.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Спальное место: 180 х 200 см\n"
            "• Внешние габариты (ДхШхВ): 215 х 192 х 110 см\n\n"
            "• <b>Материал:</b> ЛДСП, Экокожа / Велюр\n"
            "• <b>Цвет:</b> Графит / Бежевый"
        ),
        "photos": ["https://skfm-mebel.ru/wp-content/uploads/2023/07/almira_sajt.jpg"]
    },
    {
        "category_name": "Спальная мебель",
        "country_origin": "Турция",
        "description": (
            "👑 <b>Спальный гарнитур «Royal Bosphorus»</b>\n\n"
            "Премиальная кровать из турецкого массива дерева с резными элементами и патиной.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Спальное место: 200 х 200 см\n"
            "• Внешние габариты (ДхШхВ): 225 х 210 х 145 см\n\n"
            "• <b>Материал:</b> Массив бука, премиум велюр\n"
            "• <b>Цвет:</b> Слоновая кость с золотом"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTREjPqrmJBFf4U5otUGyIOQngheNUo9bEBRbQzFJR5eKps3TwoIcQZSzY&s=10"]
    },
    {
        "category_name": "Кухонная мебель",
        "country_origin": "Россия",
        "description": (
            "🍳 <b>Кухонный гарнитур «Модерн Комфорт»</b>\n\n"
            "Стильная угловая кухня с матовыми фасадами Soft-Touch и доводчиками скрытого монтажа.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Общая длина: 280 х 160 см\n"
            "• Высота нижних модулей: 85 см\n"
            "• Высота верхних шкафов: 72 см\n"
            "• Глубина столешницы: 60 см\n\n"
            "• <b>Материал:</b> МДФ, влагостойкая столешница 38 мм\n"
            "• <b>Цвет:</b> Серый бетон / Дуб Вотан"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTB6-LUv1UQWIsqig9jJSkBdy2B1JM-J7PTkLdmZixxlbuyerEaehIzE5K7&s=10"]
    },
    {
        "category_name": "Кухонная мебель",
        "country_origin": "Турция",
        "description": (
            "☕️ <b>Прямой кухонный гарнитур «Ankara Elite»</b>\n\n"
            "Современная кухня с акриловыми глянцевыми фасадами и фурнитурой Blum.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Длина гарнитура: 320 см\n"
            "• Высота: 240 см (под потолок)\n"
            "• Глубина: 60 см\n\n"
            "• <b>Материал:</b> Акрил, искусственный камень\n"
            "• <b>Цвет:</b> Белый глянец / Антрацит"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQhulB-xltwQUnU7tI2PPKuzlazMLQ0X_ETNMSJOoKdZqxb-KBiL83VGzE&s=10"]
    },
    {
        "category_name": "Мягкая мебель",
        "country_origin": "Россия",
        "description": (
            "🛋 <b>Угловой диван «Честерфилд Loft»</b>\n\n"
            "Уютный диван с механизмом трансформации «Еврокнижка» и вместительным бельевым ящиком.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• В сложенном виде (ДхШхВ): 240 х 150 х 90 см\n"
            "• Спальное место: 140 х 200 см\n"
            "• Глубина сиденья: 65 см\n\n"
            "• <b>Наполнитель:</b> Независимый пружинный блок\n"
            "• <b>Обивка:</b> Износостойкая рогожка"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQYQxpCJ355dMHxvguNeoBGq_TdNB53ng49xmkGVkPIa8PetHvvijCqY9yw&s=10"]
    },
    {
        "category_name": "Мягкая мебель",
        "country_origin": "Турция",
        "description": (
            "🛋 <b>Диван премиум «Istanbul Velvet»</b>\n\n"
            "Роскошный турецкий диван в стиле современная классика.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Длина: 260 см\n"
            "• Глубина: 100 см\n\n"
            "• <b>Материал:</b> Бархат, каркас — бук"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTDg1oYIxg2XTCXMjy8gmpI-lYwup1afR6p7AqEM0eBUrkP-7OUQiaQmOW5&s=10"]
    },
    {
        "category_name": "Детская мебель",
        "country_origin": "Россия",
        "description": (
            "🧸 <b>Детская двухъярусная кровать «Сказка»</b>\n\n"
            "Безопасная детская кровать с защитными бортиками и встроенными выдвижными ящиками для игрушек.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Спальные места: 80 х 190 см\n"
            "• Общие габариты (ДхШхВ): 198 х 88 х 165 см\n\n"
            "• <b>Материал:</b> Массив сосны / Эко-ЛДСП\n"
            "• <b>Цвет:</b> Белый / Сосна"
        ),
        "photos": ["https://babymouse.ru/wa-data/public/shop/products/28/73/37328/images/143744/143744.360x300.jpg"]
    },
    {
        "category_name": "Детская мебель",
        "country_origin": "Турция",
        "description": (
            "🚀 <b>Детская комната «Cosmo Boy»</b>\n\n"
            "Яркая модульная мебель для подростков в современном исполнении.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Кровать: 90 х 200 см\n"
            "• Письменный стол (ШхГхВ): 120 х 60 х 75 см\n\n"
            "• <b>Материал:</b> Безопасный МДФ высшего качества"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR4JKGvVsZmKvrZiqIMhowETFu5-5p0y57uBvKgc6yTiuLZv_VqOXV6sBg&s=10"]
    },
    {
        "category_name": "Столы и стулья",
        "country_origin": "Россия",
        "description": (
            "🪑 <b>Обеденный стол «Оптима» + 4 стула</b>\n\n"
            "Практичный раздвижной комплект для кухни или гостиной.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Стол: 110 (140) х 70 х 75 см\n"
            "• Стул: 45 х 45 х 90 см\n\n"
            "• <b>Материал:</b> Массив березы, ЛДСП"
        ),
        "photos": ["https://ir.ozone.ru/s3/multimedia-y/c1000/6816911002.jpg"]
    },
    {
        "category_name": "Столы и стулья",
        "country_origin": "Турция",
        "description": (
            "🪑 <b>Обеденный комплект «Istanbul Marble»</b>\n\n"
            "Раскладной стол со столешницей под мрамор и 6 мягких стульев на металлических ножках.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Стол в сложенном виде: 130 х 80 х 77 см\n"
            "• Стол в разложенном виде: 170 х 80 х 77 см\n"
            "• Стул (ШхГхВ): 48 х 52 х 92 см\n\n"
            "• <b>Материал:</b> Закаленное стекло, хромированная сталь, бархат"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQb5Y3sQJVyxWr_fyqJ2YZ1RWSGGMDbDXpRTSChnRs_LD1xU4xMM7rLZUsi&s=10"]
    },
    {
        "category_name": "Тумбы и комоды",
        "country_origin": "Россия",
        "description": (
            "🗄 <b>Комод прикроватный «Сканди 4 ящика»</b>\n\n"
            "Минималистичный комод на деревянных ножках с 4 глубокими выдвижными ящиками.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Ширина: 80 см\n"
            "• Глубина: 40 см\n"
            "• Высота: 95 см\n\n"
            "• <b>Материал:</b> ЛДСП, массив ясеня\n"
            "• <b>Цвет:</b> Белый матовый / Дуб"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSqJmfEBKeu3VE5McjvsVmoxjl69NBrFukPdWLI3LlDWrcY7pe6uwFAvEs&s=10"]
    },
    {
        "category_name": "Тумбы и комоды",
        "country_origin": "Турция",
        "description": (
            "💎 <b>Дизайнерский комод «Antik Gold»</b>\n\n"
            "Элегантный комод с зеркальными вставками и золотой фурнитурой.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Ширина: 100 см\n"
            "• Глубина: 45 см\n"
            "• Высота: 85 см\n\n"
            "• <b>Материал:</b> МДФ, зеркало, металл"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaQhRMIMqU45l-OlaxQA-iTTAAx_uZDoaSzAfzLHeeiCeh78NbLTD1XcQ&s=10"]
    },
    {
        "category_name": "Шкафы купе",
        "country_origin": "Россия",
        "description": (
            "🚪 <b>Трехдверный шкаф-купе «Сенатор Зеркало»</b>\n\n"
            "Вместительный шкаф с плавным ходом дверей, встроенной подсветкой, штангами для одежды и полками.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Ширина: 220 см\n"
            "• Глубина: 60 см\n"
            "• Высота: 240 см\n\n"
            "• <b>Материал:</b> ЛДСП 16 мм, зеркало\n"
            "• <b>Профиль:</b> Алюминиевая система Versal"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcToeyFqWtE3PjpWdCQ0J8o_ev-30lvcg1_AjqwS1FzjLsTH_-Njr1O5jW8&s=10"]
    },
    {
        "category_name": "Шкафы купе",
        "country_origin": "Турция",
        "description": (
            "🚪 <b>Шкаф-купе премиум «Bosphorus Line»</b>\n\n"
            "Современный шкаф с тонированными стеклами и системой плавного закрывания.\n\n"
            "📏 <b>Размеры (Габариты):</b>\n"
            "• Ширина: 240 см\n"
            "• Глубина: 65 см\n"
            "• Высота: 250 см\n\n"
            "• <b>Материал:</b> Ламинированная плита високого класса, тонированное стекло"
        ),
        "photos": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJOuAlywuXr7IImQhIMMBrZg4jl2dZo2d3SE7mImx7Z1JlErhrV0XNKL-d&s=10"]
    },
]


# Маппинг: страна → категория → тип мебели
TYPE_BY_CATEGORY = {
    "Кухонная мебель": "Обычная",
    "Спальная мебель": "Обычная",
    "Мягкая мебель": "Обычная",
    "Столы и стулья": "Обычная",
    "Тумбы и комоды": "Обычная",
    "Детская мебель": "Обычная",
    "Шкафы купе": "Обычная",
}


async def seed_database():
    await async_main()

    async with AsyncSessionLocal() as session:
        # 1. Категории
        category_names = {item["category_name"] for item in ITEMS_DATA}
        for name in category_names:
            if not await session.scalar(select(Category).where(Category.name == name)):
                session.add(Category(name=name))
        await session.flush()

        # 2. Страны
        country_names = {item["country_origin"] for item in ITEMS_DATA}
        countries = {}
        for name in country_names:
            country = await session.scalar(select(Country).where(Country.name == name))
            if not country:
                country = Country(name=name)
                session.add(country)
                await session.flush()
            countries[name] = country

        # 3. Типы мебели
        type_names = set(TYPE_BY_CATEGORY.values())
        types = {}
        for name in type_names:
            ftype = await session.scalar(select(FurnitureType).where(FurnitureType.name == name))
            if not ftype:
                ftype = FurnitureType(name=name)
                session.add(ftype)
                await session.flush()
            types[name] = ftype

        # 4. Категории в словарь
        categories = {}
        for name in category_names:
            cat = await session.scalar(select(Category).where(Category.name == name))
            categories[name] = cat

        # 5. Товары
        for item_data in ITEMS_DATA:
            cat = categories[item_data["category_name"]]
            country = countries[item_data["country_origin"]]
            type_name = TYPE_BY_CATEGORY.get(item_data["category_name"], "Обычная")
            ftype = types[type_name]

            # Проверка на дубликат
            exists = await session.scalar(
                select(Furniture).where(
                    Furniture.category_id == cat.id,
                    Furniture.country_id == country.id,
                    Furniture.description == item_data["description"],
                )
            )
            if exists:
                continue

            # Заголовок — вытащим из описания (первая строка)
            title = item_data["description"].split("\n")[0].replace("🛏", "").replace("👑", "").strip()
            title = title[:100]  # ограничим длину

            furniture = Furniture(
                title=title,
                description=item_data["description"],
                category_id=cat.id,
                country_id=country.id,
                type_id=ftype.id,
            )
            session.add(furniture)
            await session.flush()

            for photo_url in item_data["photos"]:
                session.add(FurniturePhoto(furniture_id=furniture.id, file_id=photo_url))

        await session.commit()
        print("✅ База успешно заполнена категориями и товарами.")


if __name__ == "__main__":
    asyncio.run(seed_database())