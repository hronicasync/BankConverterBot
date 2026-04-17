from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

HELP_TEXT = """
👋 Привет! Я помогаю рассчитать, сколько рублей нужно отправить, чтобы купить доллары через Айыл Банк.

Как пользоваться:
  Просто напиши сумму в USD — например: <b>50</b> или <b>$100</b>

Команды:
  /calc &lt;сумма&gt; — расчёт для указанной суммы
  /rates — текущие курсы Айыл Банка
  /refresh — обновить курсы принудительно
  /setrate &lt;курс&gt; — задать курс RUB→KGS вручную (например: /setrate 0.0152)
  /resetrate — сбросить на автокурс T-Банка API
""".strip()


# TODO: add inline keyboard with quick amounts (e.g. $20, $50, $100) for faster UX
@router.message(Command("start", "help"))
async def cmd_start(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")
