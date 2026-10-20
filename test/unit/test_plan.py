import unittest
from decimal import Decimal

from src.models.currency import Currency
from src.models.money import Money
from src.models.plan import Plan, PlanTier


class TestPlan(unittest.TestCase):
    """Zestaw testów jednostkowych dla modelu Plan i wyliczenia PlanTier."""

    def test_should_instantiate_plan_with_valid_parameters(self):
        # Arrange
        tier = PlanTier.PRO
        name = "Pro Plan"
        price = Money(Decimal("149.00"), Currency.PLN)
        included_requests = 5000

        # Act
        plan = Plan(tier=tier, name=name, base_price=price, included_requests=included_requests)

        # Assert
        self.assertEqual(plan.name, "Pro Plan")

    def test_should_raise_type_error_when_tier_is_invalid_type(self):
        # Arrange
        price = Money(Decimal("149.00"), Currency.PLN)

        # Act & Assert
        with self.assertRaises(TypeError):
            Plan(tier="INVALID_TIER", name="Pro", base_price=price, included_requests=5000)  # type: ignore

    def test_should_raise_type_error_when_base_price_is_not_money_instance(self):
        # Arrange & Act & Assert
        with self.assertRaises(TypeError):
            Plan(tier=PlanTier.STARTER, name="Starter", base_price=Decimal("49.00"), included_requests=1000)  # type: ignore

    def test_should_raise_value_error_when_included_requests_is_negative(self):
        # Arrange
        price = Money(Decimal("49.00"), Currency.PLN)

        # Act & Assert
        with self.assertRaises(ValueError):
            Plan(tier=PlanTier.STARTER, name="Starter", base_price=price, included_requests=-100)
