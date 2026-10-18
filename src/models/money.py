from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union

from src.models.currency import Currency

DECIMAL_PLACES_QUANTIZE = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    """Niezmienny obiekt wartości (Value Object) reprezentujący kwotę pieniężną.

    Wymusza użycie typu Decimal w celu uniknięcia błędów zaokrągleń zmiennoprzecinkowych.
    """

    amount: Decimal
    currency: Currency = Currency.PLN

    def __post_init__(self) -> None:
        if isinstance(self.amount, float):
            raise TypeError("Float is strictly forbidden in Money. Use Decimal instead.")

        if not isinstance(self.amount, Decimal):
            raise TypeError(f"Amount must be a Decimal instance, got {type(self.amount).__name__}.")

        if not isinstance(self.currency, Currency):
            raise TypeError(f"Currency must be a Currency enum instance, got {type(self.currency).__name__}.")

        # Zaokrąglenie do 2 miejsc po przecinku (ROUND_HALF_UP)
        object.__setattr__(
            self,
            "amount",
            self.amount.quantize(DECIMAL_PLACES_QUANTIZE, rounding=ROUND_HALF_UP),
        )

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, scalar: Union[Decimal, int]) -> "Money":
        if isinstance(scalar, float):
            raise TypeError("Float multiplier is forbidden. Use Decimal or int.")
        if not isinstance(scalar, (Decimal, int)):
            return NotImplemented
        multiplier = Decimal(str(scalar))
        return Money(self.amount * multiplier, self.currency)

    def __rmul__(self, scalar: Union[Decimal, int]) -> "Money":
        return self.__mul__(scalar)

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_same_currency(other)
        return self.amount >= other.amount

    def _validate_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot operate on different currencies: {self.currency.value} and {other.currency.value}"
            )

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency.value}"
