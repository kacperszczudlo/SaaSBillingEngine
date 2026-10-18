from decimal import Decimal

# Konfiguracja cyklu rozliczeniowego (Zero Magic Numbers)
DEFAULT_BILLING_CYCLE_DAYS: int = 30
MIN_BILLING_CYCLE_DAYS: int = 1
MIN_USAGE_UNITS: int = 0

# Progi i stawki opłat za nadmiarowe zapytania API (PLN)
TIER_ONE_REQUEST_LIMIT: int = 5000
TIER_ONE_RATE_PER_REQUEST: Decimal = Decimal("0.05")
TIER_TWO_RATE_PER_REQUEST: Decimal = Decimal("0.02")

# Stałe precyzji i wartości zerowe
DECIMAL_ZERO: Decimal = Decimal("0.00")
CURRENCY_QUANTIZE: Decimal = Decimal("0.01")
