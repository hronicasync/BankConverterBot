"""Standalone script to verify both parsers work against live sources."""

import asyncio
from bot.services.parser import fetch_rates, fetch_tbank_rate
from bot.services.calculator import calculate, fmt_calc


async def main() -> None:
    print("Fetching rates from abank.kg...")
    rates = await fetch_rates(force=True)
    print(f"USD: buy={rates.usd_buy:.4f}  sell={rates.usd_sell:.4f}")
    print(f"RUB: buy={rates.rub_buy:.4f}  sell={rates.rub_sell:.4f}")

    print("\nFetching RUB→KGS rate from T-Bank...")
    tbank_rate = await fetch_tbank_rate(force=True)
    print(f"T-Bank: 1 RUB = {tbank_rate:.4f} KGS")

    result = calculate(20.0, rates, tbank_rate, buffer_percent=1.0)
    print()
    print(fmt_calc(result, ayil_updated_at="сейчас", tbank_updated_at="сейчас"))


if __name__ == "__main__":
    asyncio.run(main())
