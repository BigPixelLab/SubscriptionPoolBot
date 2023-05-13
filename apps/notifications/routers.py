import aiogram

from apps.notifications import handlers

notifications_router = aiogram.Router()

notifications_router.startup.register(
    handlers.startup_handler
)
