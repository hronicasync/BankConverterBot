"""Standalone script to verify the parser works against live abank.kg."""

import asyncio
from bot.services.parser import fetch_rates


async def main() -> None:
    print("Fetching rates from abank.kg...")
    rates = await fetch_rates(force=True)
    print(f"USD: buy={rates.usd_buy:.4f}  sell={rates.usd_sell:.4f}")
    print(f"RUB: buy={rates.rub_buy:.4f}  sell={rates.rub_sell:.4f}")

    from bot.services.calculator import calculate, fmt_calc
    result = calculate(20.0, rates, buffer_percent=1.0)
    print()
    print(fmt_calc(result, "сейчас"))


if __name__ == "__main__":
    asyncio.run(main())
