from dataclasses import dataclass
from enum import Enum

from src.models.plan import Plan


class InvalidStateTransitionError(ValueError):
    """Wyjątek rzucany przy próbie wykonania niedozwolonego przejścia stanu subskrypcji."""

    pass


class SubscriptionStatus(Enum):
    """Stany cyklu życia subskrypcji (Wzorzec State)."""

    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"


@dataclass
class Subscription:
    """Reprezentacja subskrypcji klienta z maszyną stanów."""

    id: str
    customer_id: str
    plan: Plan
    status: SubscriptionStatus = SubscriptionStatus.TRIAL
    current_cycle_day: int = 1
    usage_units: int = 0

    def activate(self) -> None:
        """Aktywuje subskrypcję ze stanu TRIAL lub PAST_DUE."""
        if self.status in (SubscriptionStatus.TRIAL, SubscriptionStatus.PAST_DUE):
            self.status = SubscriptionStatus.ACTIVE
        elif self.status == SubscriptionStatus.ACTIVE:
            pass
        else:
            raise InvalidStateTransitionError(
                f"Cannot activate subscription from status '{self.status.value}'."
            )

    def mark_past_due(self) -> None:
        """Oznacza subskrypcję jako zaległą w płatnościach (PAST_DUE)."""
        if self.status == SubscriptionStatus.ACTIVE:
            self.status = SubscriptionStatus.PAST_DUE
        else:
            raise InvalidStateTransitionError(
                f"Cannot mark subscription as past due from status '{self.status.value}'."
            )

    def cancel(self) -> None:
        """Anuluje subskrypcję."""
        self.status = SubscriptionStatus.CANCELLED

    def record_usage(self, units: int) -> None:
        """Rejestruje wykonane zapytania API / jednostki zużycia."""
        if units < 0:
            raise ValueError("Usage units cannot be negative.")
        self.usage_units += units

    def change_plan(self, new_plan: Plan) -> None:
        """Zmienia przypisany plan subskrypcyjny."""
        if not isinstance(new_plan, Plan):
            raise TypeError("New plan must be an instance of Plan.")
        self.plan = new_plan
