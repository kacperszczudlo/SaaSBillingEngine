import unittest
from decimal import Decimal

from src.models.currency import Currency
from src.models.money import Money
from src.services.proration_engine import ProrationEngine, ProrationResult


class TestProrationEngine(unittest.TestCase):
    """Zestaw testów jednostkowych dla silnika rozliczeń proporcjonalnych ProrationEngine."""

    def setUp(self):
        self.engine = ProrationEngine()
        self.starter_price = Money(Decimal("60.00"), Currency.PLN)
        self.pro_price = Money(Decimal("120.00"), Currency.PLN)

    def test_should_calculate_full_credit_when_change_occurs_at_start_of_cycle(self):
        # Arrange
        current_day = 0
        total_cycle_days = 30

        # Act
        credit = self.engine.calculate_unused_credit(self.starter_price, current_day, total_cycle_days)

        # Assert
        self.assertEqual(credit.amount, Decimal("60.00"))

    def test_should_calculate_exact_half_credit_at_day_15_of_30_day_cycle(self):
        # Arrange
        current_day = 15
        total_cycle_days = 30

        # Act
        credit = self.engine.calculate_unused_credit(self.starter_price, current_day, total_cycle_days)

        # Assert
        self.assertEqual(credit.amount, Decimal("30.00"))

    def test_should_calculate_zero_credit_at_last_day_of_cycle(self):
        # Arrange
        current_day = 30
        total_cycle_days = 30

        # Act
        credit = self.engine.calculate_unused_credit(self.starter_price, current_day, total_cycle_days)

        # Assert
        self.assertEqual(credit.amount, Decimal("0.00"))

    def test_should_calculate_net_upgrade_amount_due_when_moving_to_higher_tier(self):
        # Arrange: dzień 15 z 30.
        # Niewykorzystany starter (60 zł) = 30 zł kredytu.
        # Nowy plan pro (120 zł) na 15 dni = 60 zł kosztu.
        # Do zapłaty netto: 60 zł - 30 zł = 30 zł.
        current_day = 15
        total_cycle_days = 30

        # Act
        result: ProrationResult = self.engine.calculate_migration(
            current_price=self.starter_price,
            new_price=self.pro_price,
            current_day=current_day,
            total_cycle_days=total_cycle_days,
        )

        # Assert
        self.assertEqual(result.net_amount_due.amount, Decimal("30.00"))

    def test_should_calculate_credit_balance_when_downgrading_to_lower_tier(self):
        # Arrange: dzień 15 z 30, przejście z Pro (120 zł) na Starter (60 zł).
        # Niewykorzystany Pro (120 zł) = 60 zł kredytu.
        # Nowy plan Starter (60 zł) na 15 dni = 30 zł kosztu.
        # Nadpłata/kredyt na koncie: 30 zł, kwota do zapłaty: 0.00 zł.
        current_day = 15
        total_cycle_days = 30

        # Act
        result: ProrationResult = self.engine.calculate_migration(
            current_price=self.pro_price,
            new_price=self.starter_price,
            current_day=current_day,
            total_cycle_days=total_cycle_days,
        )

        # Assert
        self.assertEqual(result.credit_balance.amount, Decimal("30.00"))

    def test_should_raise_value_error_when_current_day_exceeds_cycle_days(self):
        # Arrange
        invalid_day = 35
        total_cycle_days = 30

        # Act & Assert
        with self.assertRaises(ValueError):
            self.engine.calculate_unused_credit(self.starter_price, invalid_day, total_cycle_days)

    def test_should_raise_value_error_when_cycle_days_is_zero_or_negative(self):
        # Arrange
        current_day = 5
        invalid_cycle_days = 0

        # Act & Assert
        with self.assertRaises(ValueError):
            self.engine.calculate_unused_credit(self.starter_price, current_day, invalid_cycle_days)
