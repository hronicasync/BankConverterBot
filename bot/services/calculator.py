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


def fmt_calc(result: CalcResult, ayil_updated_at: str, tbank_updated_at: str) -> str:
    r = result
    rub_exact_fmt = f"{r.rub_exact:,.0f}".replace(",", " ")
    rub_buf_fmt = f"{r.rub_buffered:,.0f}".replace(",", " ")
    kgs_fmt = f"{r.kgs_needed:,.0f}".replace(",", " ")

    return (
        f"💰 Расчёт для {r.usd_amount:.2f}$\n"
        f"\n"
        f"Нужно отправить:\n"
        f"  ≈ {rub_exact_fmt} ₽ (точно)\n"
        f"  ≈ {rub_buf_fmt} ₽ (с запасом {r.buffer_percent:.0f}%)\n"
        f"\n"
        f"📈 Курс Айыл Банка (на {ayil_updated_at})\n"
        f"  USD → {r.rates.usd_sell:.2f} KGS\n"
        f"🏦 Курс T-Банка (на {tbank_updated_at})\n"
        f"  1 RUB → {r.rub_kgs_rate:.4f} KGS\n"
        f"\n"
        f"Цепочка: {rub_exact_fmt} ₽ → {kgs_fmt} KGS → {r.usd_amount:.2f}$"
    )


def fmt_rates(rates: Rates, tbank_rate: float, ayil_updated_at: str, tbank_updated_at: str) -> str:
    return (
        f"📊 Курсы валют\n"
        f"\n"
        f"🏦 Айыл Банк (на {ayil_updated_at})\n"
        f"  🇺🇸 USD продажа: {rates.usd_sell:.2f} KGS\n"
        f"  🇺🇸 USD покупка: {rates.usd_buy:.2f} KGS\n"
        f"\n"
        f"🏦 T-Банк (на {tbank_updated_at})\n"
        f"  🇷🇺 1 RUB → {tbank_rate:.4f} KGS (перевод)"
    )
