# Changelog

All notable changes to BankConverterBot will be documented here.

Format: `[version] YYYY-MM-DD — description`

---

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
