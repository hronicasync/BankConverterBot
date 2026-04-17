from __future__ import annotations

import datetime
import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import load_config
from bot.services.calculator import CalcResult, calculate, fmt_calc
from bot.services.parser import ParserError, fetch_rates
from bot.utils.cache import rates_cache

router = Router()

_AMOUNT_RE = re.compile(r"^\$?(\d+(?:[.,]\d+)?)\$?$")


def _parse_amount(text: str) -> float | None:
    m = _AMOUNT_RE.match(text.strip())
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def _updated_at() -> str:
    age = rates_cache.age_seconds("rates")
    if age is None:
        return "неизвестно"
    updated = datetime.datetime.now() - datetime.timedelta(seconds=age)
    return updated.strftime("%H:%M")


@router.message(Command("calc"))
async def cmd_calc(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи сумму: /calc 50")
        return
    amount = _parse_amount(parts[1])
    if amount is None:
        await message.answer("Не могу распознать сумму. Пример: /calc 50")
        return
    await _do_calc(message, amount)


@router.message(F.text)
async def handle_plain_amount(message: Message) -> None:
    amount = _parse_amount(message.text or "")
    if amount is None:
        return
    await _do_calc(message, amount)


async def _do_calc(message: Message, usd_amount: float) -> None:
    config = load_config()
    stale = False

    try:
        rates = await fetch_rates()
    except ParserError:
        stale_rates = rates_cache.get_stale("rates")
        if stale_rates is None:
            await message.answer(
                "❌ Не удалось получить курсы с сайта Айыл Банка.\n\n"
                "Проверь сайт вручную: https://abank.kg\n"
                "Или попробуй /refresh"
            )
            return
        rates = stale_rates
        stale = True

    try:
        result = calculate(usd_amount, rates, config.rates_buffer_percent)
    except ValueError as e:
        await message.answer(f"⚠️ {e}")
        return

    text = fmt_calc(result, _updated_at())

    if stale:
        age = rates_cache.age_seconds("rates")
        hours = int((age or 0) // 3600)
        minutes = int(((age or 0) % 3600) // 60)
        ago = f"{hours} ч {minutes} мин" if hours else f"{minutes} мин"
        text += f"\n\n⚠️ Используются устаревшие курсы ({ago} назад)\nПопробуй /refresh"

    await message.answer(text)
