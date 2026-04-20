from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.parser import get_manual_tbank_rate, reset_manual_tbank_rate, set_manual_tbank_rate

router = Router()


@router.message(Command("emojiid"))
async def cmd_emojiid(message: Message) -> None:
    """Usage: /emojiid <custom emoji> — returns its custom_emoji_id."""
    custom_emojis = [e for e in (message.entities or []) if e.type == "custom_emoji"]
    if not custom_emojis:
        await message.answer(
            "Напиши команду вместе с кастомным эмодзи в одном сообщении:\n"
            "<code>/emojiid </code>🔥&lt;— вставь сюда кастомный эмодзи",
            parse_mode="HTML",
        )
        return

    lines = []
    for e in custom_emojis:
        placeholder = (message.text or "")[e.offset : e.offset + e.length]
        lines.append(f"ID: <code>{e.custom_emoji_id}</code>  (заглушка: {placeholder})")

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("setrate"))
async def cmd_setrate(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        current = get_manual_tbank_rate()
        status = f"Сейчас: ручной курс {current:.4f} KGS/RUB" if current else "Сейчас: авто (T-Банк API)"
        await message.answer(
            f"Укажи курс RUB→KGS: /setrate 0.0152\n"
            f"Для сброса на авто: /resetrate\n\n"
            f"{status}"
        )
        return

    raw = parts[1].strip().replace(",", ".")
    try:
        rate = float(raw)
        if rate <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Не могу распознать курс. Пример: /setrate 0.0152")
        return

    set_manual_tbank_rate(rate)
    await message.answer(
        f"✅ Ручной курс установлен: 1 RUB = {rate:.4f} KGS\n\n"
        f"Для сброса на T-Банк API: /resetrate"
    )


@router.message(Command("resetrate"))
async def cmd_resetrate(message: Message) -> None:
    was_manual = get_manual_tbank_rate() is not None
    reset_manual_tbank_rate()
    if was_manual:
        await message.answer("✅ Ручной курс сброшен. Теперь используется курс T-Банка API.")
    else:
        await message.answer("Ручной курс не был установлен. Уже используется T-Банк API.")
