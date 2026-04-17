from __future__ import annotations

import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.calculator import fmt_rates
from bot.services.parser import ParserError, fetch_rates
from bot.utils.cache import rates_cache

router = Router()


def _updated_at() -> str:
    age = rates_cache.age_seconds("rates")
    if age is None:
        return "неизвестно"
    updated = datetime.datetime.now() - datetime.timedelta(seconds=age)
    return updated.strftime("%H:%M, %d.%m.%Y")


def _stale_warning() -> str:
    age = rates_cache.age_seconds("rates")
    if age is None:
        return ""
    hours = int(age // 3600)
    minutes = int((age % 3600) // 60)
    if hours:
        ago = f"{hours} ч {minutes} мин назад"
    else:
        ago = f"{minutes} мин назад"
    return f"\n\n⚠️ Используются устаревшие данные (обновлено {ago})\nПопробуй /refresh"


@router.message(Command("rates"))
async def cmd_rates(message: Message) -> None:
    try:
        rates = await fetch_rates()
        await message.answer(fmt_rates(rates, _updated_at()))
    except ParserError:
        await message.answer(
            "❌ Не удалось получить курсы с сайта Айыл Банка.\n\n"
            "Проверь сайт вручную: https://abank.kg\n"
            "Или попробуй /refresh"
        )


@router.message(Command("refresh"))
async def cmd_refresh(message: Message) -> None:
    await message.answer("🔄 Обновляю курсы...")
    rates_cache.invalidate("rates")
    try:
        rates = await fetch_rates(force=True)
        await message.answer(
            "✅ Курсы обновлены!\n\n" + fmt_rates(rates, _updated_at())
        )
    except ParserError:
        await message.answer(
            "❌ Не удалось получить курсы с сайта Айыл Банка.\n\n"
            "Проверь сайт вручную: https://abank.kg"
        )
