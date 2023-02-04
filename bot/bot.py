from telegram.ext import AIORateLimiter, ApplicationBuilder

from bot.get_id import setup_get_id
# from bot.subscription.__main__ import setup_cancel, setup_conversation
from config import telegram_config


limiter = AIORateLimiter(max_retries=10)
application = ApplicationBuilder().token(telegram_config.token_antalya_bot).rate_limiter(limiter).build()
# setup_conversation(application)
# setup_cancel(application)
setup_get_id(application)


def start_bot() -> None:
    application.run_polling()
