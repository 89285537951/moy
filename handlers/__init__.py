from aiogram import Router

from handlers.admin import admin_router
from handlers.user import router as user_router

router = Router(name="main")
router.include_router(admin_router)
router.include_router(user_router)
