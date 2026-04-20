# Changelog

All notable changes to BankConverterBot will be documented here.

Format: `[version] YYYY-MM-DD — description`

---

## [0.9.0] 2026-04-20

- Added `/emojiid` command — send it with a custom emoji in one message to get its `custom_emoji_id`
- Updated `/calc` output to use Telegram Premium custom emojis and HTML formatting (bold header, italic rates timestamp, custom emoji per line)
- Updated `/rates` output to use the same custom emoji style
- `fmt_calc` and `fmt_rates` in `calculator.py` now return HTML; all callers pass `parse_mode="HTML"`
- If manual RUB→KGS rate is active, T-Банк line in `/calc` shows `(ручной)` label

## [0.8.0] 2026-04-20

- Fixed manual RUB→KGS rate (`/setrate`) being lost on container restart — rate is now persisted to `/data/manual_rate.txt` and restored on startup
- Added `./data:/data` volume mount in `docker-compose.yml` so the rate file survives rebuilds

## [0.7.0] 2026-04-20

- Fixed KGS display in conversion chain: now shows 1 decimal place (e.g. `350.8 KGS`) instead of rounding to integer (`351 KGS`), matching T-Bank's actual credited amount

## [0.6.0] 2026-04-17

- Fixed Ayil Bank scraping: switched from aiohttp to `curl-cffi` with Chrome impersonation to bypass Cloudflare TLS fingerprinting
- Fixed `ABANK_URL`: changed from `/ru` (meta-refresh redirect, not followed by aiohttp) to `/` (real page)

## [0.5.0] 2026-04-17

- Added `.dockerignore` (excluded `.venv`, `.git`, `__pycache__` from build context)
- Updated `docker-compose.yml`: removed deprecated `version:` field, added log rotation (10MB × 3 files)
- Added `deploy.sh` — one-command SSH deploy: clones repo on first run, then `git pull + docker compose up --build`

## [0.4.0] 2026-04-17

- Added `/setrate <value>` — manual override for the RUB→KGS rate (e.g. `/setrate 0.0152`)
- Added `/resetrate` — clears the override and returns to T-Bank API rate
- When manual rate is active, `/calc` and `/rates` display "ручной курс" instead of update timestamp
- `fetch_tbank_rate()` short-circuits to manual value when override is set (bypasses cache and API)
- Registered `admin` router in `main.py`; new commands appear in the bot menu

## [0.3.0] 2026-04-17

- Added T-Bank API as source for RUB→KGS rate (`CUTransfersPrivate` category — EAEU transfers)
- `calculate()` now takes explicit `rub_kgs_rate` instead of using Ayil Bank's RUB rate
- `/rates` and `/refresh` now show both Ayil Bank and T-Bank rates with separate timestamps
- Calculation output shows both rate sources with their update times
- Fixed bot commands menu (`set_my_commands`)

## [0.2.0] 2026-04-17

- Implemented `parser.py`: scrapes abank.kg cash rates table (USD/KGS, RUB/KGS), TTL cache with stale fallback on parser failure
- Implemented `calculator.py`: RUB→KGS→USD calculation with buffer percent, `fmt_calc` and `fmt_rates` formatters
- Implemented `cache.py`: TTLCache with `get`, `set`, `invalidate`, `get_stale`, `age_seconds`
- Implemented all handlers: `/rates`, `/refresh`, `/calc <amount>`, smart plain-number input
- Fixed proxy wiring in `main.py` (SOCKS5 via aiohttp-socks connector)
- Added `test_parser.py` for standalone parser verification

## [0.1.0] 2026-04-17

- Initial project scaffold: directory structure, config, handlers, services, utils
- Added CHANGELOG, .gitignore, .env.example, requirements.txt
- Added Dockerfile and docker-compose.yml
- All modules stubbed with TODO markers, ready for implementation
