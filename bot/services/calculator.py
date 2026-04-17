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


def calculate(usd_amount: float, rates: Rates, buffer_percent: float = 1.0) -> CalcResult:
    if usd_amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")

    kgs_needed = usd_amount * rates.usd_sell
    rub_exact = kgs_needed / rates.rub_sell
    rub_buffered = rub_exact * (1 + buffer_percent / 100)

    return CalcResult(
        usd_amount=usd_amount,
        kgs_needed=kgs_needed,
        rub_exact=rub_exact,
        rub_buffered=rub_buffered,
        buffer_percent=buffer_percent,
        rates=rates,
    )


def fmt_calc(result: CalcResult, updated_at: str) -> str:
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
        f"📈 Курсы Айыл Банка (на {updated_at})\n"
        f"  USD → {r.rates.usd_sell:.2f} KGS\n"
        f"  1 RUB → {r.rates.rub_sell:.4f} KGS\n"
        f"\n"
        f"Цепочка: {rub_exact_fmt} ₽ → {kgs_fmt} KGS → {r.usd_amount:.2f}$"
    )


def fmt_rates(rates: Rates, updated_at: str) -> str:
    return (
        f"📊 Курсы Айыл Банка\n"
        f"Обновлено: {updated_at}\n"
        f"\n"
        f"🇺🇸 USD/KGS\n"
        f"  Покупка: {rates.usd_buy:.2f} сом\n"
        f"  Продажа: {rates.usd_sell:.2f} сом\n"
        f"\n"
        f"🇷🇺 RUB/KGS\n"
        f"  Покупка: {rates.rub_buy:.4f} сом\n"
        f"  Продажа: {rates.rub_sell:.4f} сом"
    )
