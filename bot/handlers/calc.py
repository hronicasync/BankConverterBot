from __future__ import annotations

import datetime
import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import load_config
from bot.services.calculator import calculate, fmt_calc
from bot.services.parser import ParserError, fetch_rates, fetch_tbank_rate, get_manual_tbank_rate
from bot.utils.cache import rates_cache

router = Router()

_AMOUNT_RE = re.compile(r"^\$?(\d+(?:[.,]\d+)?)\$?$")


def _parse_amount(text: str) -> float | None:
    m = _AMOUNT_RE.match(text.strip())
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def _fmt_updated_at(cache_key: str) -> str:
    age = rates_cache.age_seconds(cache_key)
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
    warnings: list[str] = []

    try:
        ayil_rates = await fetch_rates()
    except ParserError:
        ayil_rates = rates_cache.get_stale("rates")
        if ayil_rates is None:
            await message.answer(
                "❌ Не удалось получить курсы Айыл Банка.\n\n"
                "Проверь сайт вручную: https://abank.kg\n"
                "Или попробуй /refresh"
            )
            return
        warnings.append("⚠️ Курс Айыл Банка устаревший — попробуй /refresh")

    try:
        tbank_rate = await fetch_tbank_rate()
    except ParserError:
        tbank_rate = rates_cache.get_stale("tbank_rate")
        if tbank_rate is None:
            await message.answer(
                "❌ Не удалось получить курс T-Банка.\n\n"
                "Попробуй /refresh"
            )
            return
        warnings.append("⚠️ Курс T-Банка устаревший — попробуй /refresh")

    try:
        result = calculate(usd_amount, ayil_rates, tbank_rate, config.rates_buffer_percent)
    except ValueError as e:
        await message.answer(f"⚠️ {e}")
        return

    tbank_label = "ручной курс" if get_manual_tbank_rate() is not None else _fmt_updated_at("tbank_rate")
    text = fmt_calc(
        result,
        ayil_updated_at=_fmt_updated_at("rates"),
        tbank_updated_at=tbank_label,
    )

    if warnings:
        text += "\n\n" + "\n".join(warnings)

    await message.answer(text, parse_mode="HTML")
