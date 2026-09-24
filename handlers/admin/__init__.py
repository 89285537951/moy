from aiogram import Router
from .main_admin import router as main_admin_router

admin_router = Router()
admin_router.include_router(main_admin_router)