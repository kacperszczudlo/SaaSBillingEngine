import unittest
from decimal import Decimal

from src.models.currency import Currency
from src.models.money import Money


class TestMoney(unittest.TestCase):
    """Zestaw testów jednostkowych dla obiektu wartości Money i waluty Currency."""

    def test_should_instantiate_money_with_decimal_and_two_decimal_places(self):
        # Arrange
        amount = Decimal("99.99")
        currency = Currency.PLN

        # Act
        money = Money(amount, currency)

        # Assert
        self.assertEqual(money.amount, Decimal("99.99"))

    def test_should_raise_type_error_when_instantiating_money_with_float(self):
        # Arrange & Act & Assert
        with self.assertRaises(TypeError):
            # Float jest zabroniony w logice finansowej ze względu na błędy precyzji
            Money(99.99, Currency.PLN)  # type: ignore

    def test_should_add_two_money_instances_of_same_currency(self):
        # Arrange
        first = Money(Decimal("50.25"), Currency.PLN)
        second = Money(Decimal("25.50"), Currency.PLN)

        # Act
        result = first + second

        # Assert
        self.assertEqual(result.amount, Decimal("75.75"))

    def test_should_raise_value_error_when_adding_different_currencies(self):
        # Arrange
        pln = Money(Decimal("50.00"), Currency.PLN)
        eur = Money(Decimal("50.00"), Currency.EUR)

        # Act & Assert
        with self.assertRaises(ValueError):
            _ = pln + eur

    def test_should_subtract_money_instances_of_same_currency(self):
        # Arrange
        first = Money(Decimal("100.00"), Currency.PLN)
        second = Money(Decimal("30.00"), Currency.PLN)

        # Act
        result = first - second

        # Assert
        self.assertEqual(result.amount, Decimal("70.00"))

    def test_should_multiply_money_by_scalar_decimal(self):
        # Arrange
        price = Money(Decimal("50.00"), Currency.PLN)
        multiplier = Decimal("1.5")

        # Act
        result = price * multiplier

        # Assert
        self.assertEqual(result.amount, Decimal("75.00"))

    def test_should_format_money_to_readable_string(self):
        # Arrange
        money = Money(Decimal("123.45"), Currency.PLN)

        # Act
        text = str(money)

        # Assert
        self.assertEqual(text, "123.45 PLN")
