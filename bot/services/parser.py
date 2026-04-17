from __future__ import annotations

import logging
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession as CurlSession

from bot.utils.cache import rates_cache

logger = logging.getLogger(__name__)

ABANK_URL = "https://abank.kg/"
TBANK_URL = "https://api.tbank.ru/v1/currency_rates?from=RUB&to=KGS"

ABANK_CACHE_KEY = "rates"
TBANK_CACHE_KEY = "tbank_rate"

# Категория T-Банка для переводов в ЕАЭС (Кыргызстан входит в союз)
TBANK_CATEGORY = "CUTransfersPrivate"


@dataclass
class Rates:
    usd_buy: float
    usd_sell: float
    rub_buy: float
    rub_sell: float


class ParserError(Exception):
    pass


_manual_tbank_rate: float | None = None


def set_manual_tbank_rate(rate: float) -> None:
    global _manual_tbank_rate
    _manual_tbank_rate = rate


def reset_manual_tbank_rate() -> None:
    global _manual_tbank_rate
    _manual_tbank_rate = None


def get_manual_tbank_rate() -> float | None:
    return _manual_tbank_rate


async def _fetch_html() -> str:
    async with CurlSession(impersonate="chrome120") as session:
        resp = await session.get(ABANK_URL, timeout=15)
        resp.raise_for_status()
        return resp.text


def _parse_rates(html: str) -> Rates:
    soup = BeautifulSoup(html, "lxml")
    found: dict[str, tuple[float, float]] = {}

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
    if not force:
        cached = rates_cache.get(ABANK_CACHE_KEY)
        if cached is not None:
            return cached

    try:
        html = await _fetch_html()
        rates = _parse_rates(html)
        rates_cache.set(ABANK_CACHE_KEY, rates)
        logger.info("Ayil Bank rates refreshed: USD sell=%.4f", rates.usd_sell)
        return rates
    except Exception as exc:
        logger.warning("Failed to fetch Ayil Bank rates: %s", exc)
        stale = rates_cache.get_stale(ABANK_CACHE_KEY)
        if stale is not None:
            return stale
        raise ParserError(str(exc)) from exc


async def fetch_tbank_rate(force: bool = False) -> float:
    """Return T-Bank's RUB→KGS transfer rate (KGS per 1 RUB)."""
    if _manual_tbank_rate is not None:
        return _manual_tbank_rate

    if not force:
        cached = rates_cache.get(TBANK_CACHE_KEY)
        if cached is not None:
            return cached

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                TBANK_URL,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)

        rates_list = data.get("payload", data) if isinstance(data, dict) else data
        if isinstance(rates_list, dict):
            rates_list = rates_list.get("rates", [])

        rate = None
        for entry in rates_list:
            if entry.get("category") == TBANK_CATEGORY:
                rate = float(entry["buy"])
                break

        if rate is None:
            raise ParserError(f"Category '{TBANK_CATEGORY}' not found in T-Bank response")

        rates_cache.set(TBANK_CACHE_KEY, rate)
        logger.info("T-Bank rate refreshed: 1 RUB = %.4f KGS", rate)
        return rate

    except Exception as exc:
        logger.warning("Failed to fetch T-Bank rate: %s", exc)
        stale = rates_cache.get_stale(TBANK_CACHE_KEY)
        if stale is not None:
            return stale
        raise ParserError(str(exc)) from exc
