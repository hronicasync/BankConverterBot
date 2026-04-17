from __future__ import annotations

import logging
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup

from bot.utils.cache import rates_cache

logger = logging.getLogger(__name__)

ABANK_URL = "https://abank.kg/ru"
CACHE_KEY = "rates"


@dataclass
class Rates:
    usd_buy: float
    usd_sell: float
    rub_buy: float
    rub_sell: float


class ParserError(Exception):
    pass


async def _fetch_html(session: aiohttp.ClientSession) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BankConverterBot/1.0)"}
    async with session.get(ABANK_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        resp.raise_for_status()
        return await resp.text()


def _parse_rates(html: str) -> Rates:
    soup = BeautifulSoup(html, "lxml")

    found: dict[str, tuple[float, float]] = {}

    # abank.kg has multiple identical-structure tables (cash, non-cash, NBK).
    # We want the first table that contains both USD and RUB — that's the cash table.
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            label = cells[0].get_text(strip=True)
            for currency in ("USD", "RUB"):
                if currency in label and currency not in found:
                    try:
                        buy = float(cells[1].get_text(strip=True).replace(",", "."))
                        sell = float(cells[2].get_text(strip=True).replace(",", "."))
                        found[currency] = (buy, sell)
                    except ValueError:
                        pass
        if "USD" in found and "RUB" in found:
            break

    if "USD" not in found or "RUB" not in found:
        raise ParserError(f"Could not find rates in page. Found: {list(found.keys())}")

    return Rates(
        usd_buy=found["USD"][0],
        usd_sell=found["USD"][1],
        rub_buy=found["RUB"][0],
        rub_sell=found["RUB"][1],
    )


async def fetch_rates(force: bool = False) -> Rates:
    """Return rates from cache or fetch fresh. Raises ParserError on failure with no stale cache."""
    if not force:
        cached = rates_cache.get(CACHE_KEY)
        if cached is not None:
            return cached

    try:
        async with aiohttp.ClientSession() as session:
            html = await _fetch_html(session)
        rates = _parse_rates(html)
        rates_cache.set(CACHE_KEY, rates)
        logger.info("Rates refreshed: USD sell=%.4f, RUB sell=%.4f", rates.usd_sell, rates.rub_sell)
        return rates
    except Exception as exc:
        logger.warning("Failed to fetch rates: %s", exc)
        stale = rates_cache.get_stale(CACHE_KEY)
        if stale is not None:
            return stale
        raise ParserError(str(exc)) from exc
