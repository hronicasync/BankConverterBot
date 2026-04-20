from __future__ import annotations

from dataclasses import dataclass

from bot.services.parser import Rates


@dataclass
class CalcResult:
    usd_amount: float
    kgs_needed: float
    rub_exact: float
    rub_buffered: float
    buffer_percent: float
    rates: Rates
    rub_kgs_rate: float


def calculate(
    usd_amount: float,
    rates: Rates,
    rub_kgs_rate: float,
    buffer_percent: float = 1.0,
) -> CalcResult:
    if usd_amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")

    kgs_needed = usd_amount * rates.usd_sell
    rub_exact = kgs_needed / rub_kgs_rate
    rub_buffered = rub_exact * (1 + buffer_percent / 100)

    return CalcResult(
        usd_amount=usd_amount,
        kgs_needed=kgs_needed,
        rub_exact=rub_exact,
        rub_buffered=rub_buffered,
        buffer_percent=buffer_percent,
        rates=rates,
        rub_kgs_rate=rub_kgs_rate,
    )


def _e(emoji_id: str, placeholder: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{placeholder}</tg-emoji>'


_MONEY  = _e("5404874922180748672", "💰")
_WHITE  = _e("5382020701119080886", "⚪️")
_GREEN  = _e("5382245959268859585", "🟢")
_CHART  = _e("5258391025281408576", "📈")
_BLACK  = _e("5229098454969507977", "⚫️")
_ARROWS = _e("5435972693016982433", "↕️")


def fmt_calc(result: CalcResult, ayil_updated_at: str, tbank_updated_at: str) -> str:
    r = result
    rub_exact_fmt = f"{r.rub_exact:,.0f}".replace(",", " ")
    rub_buf_fmt = f"{r.rub_buffered:,.0f}".replace(",", " ")
    kgs_fmt = f"{r.kgs_needed:,.1f}".replace(",", " ")

    tbank_note = " <i>(ручной)</i>" if tbank_updated_at == "ручной курс" else ""

    return (
        f"{_MONEY} <b>Расчёт для {r.usd_amount:.2f}$</b>\n"
        f"\n"
        f"Нужно отправить:\n"
        f"{_WHITE}≈ {rub_exact_fmt} ₽ (точно)\n"
        f"{_GREEN}≈ {rub_buf_fmt} ₽ (с запасом {r.buffer_percent:.0f}%)\n"
        f"\n"
        f"Цепочка:\n"
        f"{rub_exact_fmt} ₽ → {kgs_fmt} KGS → {r.usd_amount:.2f}$\n"
        f"\n"
        f"{_CHART} <i>Курсы на {ayil_updated_at}</i>\n"
        f"\n"
        f"{_BLACK}Айыл Банк:\n"
        f"{_ARROWS}1 USD → {r.rates.usd_sell:.2f} KGS\n"
        f"\n"
        f"{_BLACK}T-Банк{tbank_note}:\n"
        f"{_ARROWS}1 RUB → {r.rub_kgs_rate:.4f} KGS"
    )


def fmt_rates(rates: Rates, tbank_rate: float, ayil_updated_at: str, tbank_updated_at: str) -> str:
    return (
        f"{_CHART} <b>Курсы валют</b>\n"
        f"\n"
        f"{_BLACK}Айыл Банк <i>(на {ayil_updated_at})</i>:\n"
        f"{_ARROWS}1 USD → {rates.usd_sell:.2f} KGS (продажа)\n"
        f"{_ARROWS}1 USD → {rates.usd_buy:.2f} KGS (покупка)\n"
        f"\n"
        f"{_BLACK}T-Банк <i>(на {tbank_updated_at})</i>:\n"
        f"{_ARROWS}1 RUB → {tbank_rate:.4f} KGS"
    )
