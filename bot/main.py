import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand

from bot.config import load_config
from bot.handlers import admin, calc, rates, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = load_config()

    session = AiohttpSession(proxy=config.proxy_url or None)
    bot = Bot(token=config.bot_token, session=session)

    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(rates.router)
    dp.include_router(admin.router)
    dp.include_router(calc.router)  # last — catches plain text / numbers

    await bot.set_my_commands([
        BotCommand(command="calc", description="Рассчитать сколько ₽ нужно для указанных $"),
        BotCommand(command="rates", description="Текущие курсы Айыл Банка"),
        BotCommand(command="refresh", description="Принудительно обновить курсы"),
        BotCommand(command="setrate", description="Установить курс RUB→KGS вручную"),
        BotCommand(command="resetrate", description="Сбросить на курс T-Банка API"),
        BotCommand(command="help", description="Помощь"),
    ])

    logger.info("BankConverterBot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
