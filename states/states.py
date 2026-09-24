from aiogram.fsm.state import State, StatesGroup


class AddCategoryState(StatesGroup):
    name = State()
    description = State()


class AddFurnitureState(StatesGroup):
    category = State()
    kitchen_type = State()
    country = State()
    description = State()
    photos = State()
