from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Config:
    bot_token: str
    proxy_url: str | None
    rates_cache_ttl: int
    rates_buffer_percent: float


def load_config() -> Config:
    # TODO: validate that BOT_TOKEN is set, raise clear error if missing
    return Config(
        bot_token=os.environ["BOT_TOKEN"],
        proxy_url=os.getenv("PROXY_URL"),
        rates_cache_ttl=int(os.getenv("RATES_CACHE_TTL", "1800")),
        rates_buffer_percent=float(os.getenv("RATES_BUFFER_PERCENT", "1.0")),
    )
