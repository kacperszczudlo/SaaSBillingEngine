from dataclasses import dataclass
from decimal import Decimal

from src.config import DEFAULT_BILLING_CYCLE_DAYS
from src.models.money import Money


@dataclass(frozen=True)
class ProrationResult:
    """Wynik kalkulacji migracji planu subskrypcji w trakcie cyklu rozliczeniowego."""

    unused_credit: Money
    new_plan_charge: Money
    net_amount_due: Money
    credit_balance: Money
    remaining_days: int
    total_cycle_days: int


class ProrationEngine:
    """Silnik wyliczania kwot proporcjonalnych (proration) w trakcie cyklu rozliczeniowego."""

    def calculate_unused_credit(
        self,
        current_price: Money,
        current_day: int,
        total_cycle_days: int = DEFAULT_BILLING_CYCLE_DAYS,
    ) -> Money:
        """Oblicza wartość niewykorzystanego abonamentu za pozostałe dni cyklu."""
        self._validate_cycle_days(current_day, total_cycle_days)

        remaining_days = total_cycle_days - current_day
        day_ratio = Decimal(remaining_days) / Decimal(total_cycle_days)

        return current_price * day_ratio

    def calculate_prorated_charge(
        self,
        new_price: Money,
        current_day: int,
        total_cycle_days: int = DEFAULT_BILLING_CYCLE_DAYS,
    ) -> Money:
        """Oblicza koszt nowego planu proporcjonalnie do pozostałych dni w cyklu."""
        self._validate_cycle_days(current_day, total_cycle_days)

        remaining_days = total_cycle_days - current_day
        day_ratio = Decimal(remaining_days) / Decimal(total_cycle_days)

        return new_price * day_ratio

    def calculate_migration(
        self,
        current_price: Money,
        new_price: Money,
        current_day: int,
        total_cycle_days: int = DEFAULT_BILLING_CYCLE_DAYS,
    ) -> ProrationResult:
        """Wylicza pełną kalkulację zmiany planu (upgrade lub downgrade)."""
        if current_price.currency != new_price.currency:
            raise ValueError("Both plans must have the same currency for migration.")

        unused_credit = self.calculate_unused_credit(current_price, current_day, total_cycle_days)
        new_plan_charge = self.calculate_prorated_charge(new_price, current_day, total_cycle_days)

        zero_money = Money(Decimal("0.00"), current_price.currency)

        if new_plan_charge >= unused_credit:
            net_amount_due = new_plan_charge - unused_credit
            credit_balance = zero_money
        else:
            net_amount_due = zero_money
            credit_balance = unused_credit - new_plan_charge

        remaining_days = total_cycle_days - current_day

        return ProrationResult(
            unused_credit=unused_credit,
            new_plan_charge=new_plan_charge,
            net_amount_due=net_amount_due,
            credit_balance=credit_balance,
            remaining_days=remaining_days,
            total_cycle_days=total_cycle_days,
        )

    def _validate_cycle_days(self, current_day: int, total_cycle_days: int) -> None:
        if total_cycle_days <= 0:
            raise ValueError("Total cycle days must be greater than zero.")
        if current_day < 0:
            raise ValueError("Current day cannot be negative.")
        if current_day > total_cycle_days:
            raise ValueError(
                f"Current day ({current_day}) cannot exceed total cycle days ({total_cycle_days})."
            )
