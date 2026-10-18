from abc import ABC, abstractmethod
from decimal import Decimal

from src.config import (
    MIN_USAGE_UNITS,
    TIER_ONE_RATE_PER_REQUEST,
    TIER_ONE_REQUEST_LIMIT,
    TIER_TWO_RATE_PER_REQUEST,
)
from src.models.money import Money
from src.models.plan import Plan


class PricingStrategy(ABC):
    """Abstrakcyjny interfejs wzorca Strategy do obliczania całkowitej ceny planu."""

    @abstractmethod
    def calculate_total(self, plan: Plan, usage_units: int) -> Money:
        """Oblicza całkowity koszt planu uwzględniając wykorzystane jednostki."""
        pass


class FlatRatePricingStrategy(PricingStrategy):
    """Strategia stałej ceny abonamentowej (ryczałt), niezależnie od liczby zapytań."""

    def calculate_total(self, plan: Plan, usage_units: int) -> Money:
        if usage_units < MIN_USAGE_UNITS:
            raise ValueError("Usage units cannot be negative.")
        return plan.base_price


class TieredUsagePricingStrategy(PricingStrategy):
    """Strategia cennika progowego z dopłatami za zapytania ponad limit w planie."""

    def calculate_total(self, plan: Plan, usage_units: int) -> Money:
        if usage_units < MIN_USAGE_UNITS:
            raise ValueError("Usage units cannot be negative.")

        if usage_units <= plan.included_requests:
            return plan.base_price

        overage_requests = usage_units - plan.included_requests
        overage_cost_amount = self._calculate_overage_amount(usage_units, plan.included_requests)

        overage_money = Money(overage_cost_amount, plan.base_price.currency)
        return plan.base_price + overage_money

    def _calculate_overage_amount(self, total_usage: int, included_requests: int) -> Decimal:
        """Oblicza koszt nadmiarowych jednostek w przedziałach progowych."""
        total_overage_cost = Decimal("0.00")

        # Rozbicie na przedziały:
        # Przedział 1: zapytania od included_requests do TIER_ONE_REQUEST_LIMIT
        tier_one_units = max(0, min(total_usage, TIER_ONE_REQUEST_LIMIT) - included_requests)
        total_overage_cost += Decimal(tier_one_units) * TIER_ONE_RATE_PER_REQUEST

        # Przedział 2: zapytania powyżej TIER_ONE_REQUEST_LIMIT
        tier_two_units = max(0, total_usage - max(included_requests, TIER_ONE_REQUEST_LIMIT))
        total_overage_cost += Decimal(tier_two_units) * TIER_TWO_RATE_PER_REQUEST

        return total_overage_cost
