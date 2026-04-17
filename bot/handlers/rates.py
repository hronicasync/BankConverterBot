from __future__ import annotations

import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.calculator import fmt_rates
from bot.services.parser import ParserError, fetch_rates, fetch_tbank_rate
from bot.utils.cache import rates_cache

router = Router()


def _updated_at(cache_key: str) -> str:
    age = rates_cache.age_seconds(cache_key)
    if age is None:
        return "неизвестно"
    updated = datetime.datetime.now() - datetime.timedelta(seconds=age)
    return updated.strftime("%H:%M, %d.%m.%Y")


@router.message(Command("rates"))
async def cmd_rates(message: Message) -> None:
    try:
        ayil_rates = await fetch_rates()
        tbank_rate = await fetch_tbank_rate()
        await message.answer(fmt_rates(
            ayil_rates, tbank_rate,
            ayil_updated_at=_updated_at("rates"),
            tbank_updated_at=_updated_at("tbank_rate"),
        ))
    except ParserError as e:
        await message.answer(
            f"❌ Не удалось получить курсы: {e}\n\nПопробуй /refresh"
        )


@router.message(Command("refresh"))
async def cmd_refresh(message: Message) -> None:
    await message.answer("🔄 Обновляю курсы...")
    rates_cache.invalidate("rates")
    rates_cache.invalidate("tbank_rate")
    try:
        ayil_rates = await fetch_rates(force=True)
        tbank_rate = await fetch_tbank_rate(force=True)
        await message.answer(
            "✅ Курсы обновлены!\n\n" + fmt_rates(
                ayil_rates, tbank_rate,
                ayil_updated_at=_updated_at("rates"),
                tbank_updated_at=_updated_at("tbank_rate"),
            )
        )
    except ParserError as e:
        await message.answer(f"❌ Не удалось обновить курсы: {e}")
