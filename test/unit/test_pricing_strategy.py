import unittest
from decimal import Decimal

from src.models.currency import Currency
from src.models.money import Money
from src.models.plan import Plan, PlanTier
from src.services.pricing_strategy import (
    FlatRatePricingStrategy,
    TieredUsagePricingStrategy,
)


class TestPricingStrategy(unittest.TestCase):
    """Zestaw testów jednostkowych dla wzorca Strategy w wyliczaniu kosztów subskrypcji."""

    def setUp(self):
        self.starter_plan = Plan(
            tier=PlanTier.STARTER,
            name="Starter Plan",
            base_price=Money(Decimal("49.00"), Currency.PLN),
            included_requests=1000,
            description="Dla małych zespołów",
        )
        self.flat_strategy = FlatRatePricingStrategy()
        self.tiered_strategy = TieredUsagePricingStrategy()

    def test_should_calculate_flat_rate_pricing_regardless_of_usage(self):
        # Arrange
        usage_requests = 7500

        # Act
        total_price = self.flat_strategy.calculate_total(self.starter_plan, usage_requests)

        # Assert
        self.assertEqual(total_price.amount, Decimal("49.00"))

    def test_should_calculate_zero_additional_charge_when_usage_within_included_requests(self):
        # Arrange
        usage_requests = 800  # mniej niż 1000 w planie

        # Act
        total_price = self.tiered_strategy.calculate_total(self.starter_plan, usage_requests)

        # Assert
        self.assertEqual(total_price.amount, Decimal("49.00"))

    def test_should_calculate_tiered_surcharge_for_tier_one_overage(self):
        # Arrange
        # 1000 w cenie, 500 nadmiarowych po 0.05 PLN = 25.00 PLN dopłaty. Łącznie: 49.00 + 25.00 = 74.00 PLN
        usage_requests = 1500

        # Act
        total_price = self.tiered_strategy.calculate_total(self.starter_plan, usage_requests)

        # Assert
        self.assertEqual(total_price.amount, Decimal("74.00"))

    def test_should_calculate_tiered_surcharge_across_multiple_overage_brackets(self):
        # Arrange
        # 1000 w cenie
        # Następne 4000 (do 5000) po 0.05 PLN = 200.00 PLN
        # Powyżej 5000: 1000 po 0.02 PLN = 20.00 PLN
        # Łącznie: 49.00 + 200.00 + 20.00 = 269.00 PLN
        usage_requests = 6000

        # Act
        total_price = self.tiered_strategy.calculate_total(self.starter_plan, usage_requests)

        # Assert
        self.assertEqual(total_price.amount, Decimal("269.00"))

    def test_should_raise_value_error_when_usage_units_is_negative(self):
        # Arrange
        negative_usage = -50

        # Act & Assert
        with self.assertRaises(ValueError):
            self.tiered_strategy.calculate_total(self.starter_plan, negative_usage)
