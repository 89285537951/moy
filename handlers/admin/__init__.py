from aiogram import Router

from utils.admin_filter import IsAdmin
from .main_admin import router as main_admin_router
from .list_category_furniture_handler import router as list_category_router

admin_router = Router(name="admin")
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())
admin_router.include_router(main_admin_router)
admin_router.include_router(list_category_router)
