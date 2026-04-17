import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from bot.config import load_config
from bot.handlers import calc, rates, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = load_config()

    if config.proxy_url:
        from aiohttp_socks import ProxyConnector
        connector = ProxyConnector.from_url(config.proxy_url)
        session = AiohttpSession(connector=connector)
    else:
        session = AiohttpSession()

    bot = Bot(token=config.bot_token, session=session)

    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(rates.router)
    dp.include_router(calc.router)  # last — catches plain text / numbers

    logger.info("BankConverterBot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
