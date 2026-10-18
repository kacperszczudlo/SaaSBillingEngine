from typing import Optional

from src.config import DEFAULT_BILLING_CYCLE_DAYS
from src.models.money import Money
from src.models.plan import Plan
from src.models.subscription import Subscription, SubscriptionStatus
from src.repositories.base import SubscriptionRepository
from src.services.pricing_strategy import PricingStrategy
from src.services.proration_engine import ProrationEngine, ProrationResult


class BillingService:
    """Serwis aplikacyjny orkiestrujący cykl życia subskrypcji oraz rozliczenia."""

    def __init__(
        self,
        repository: SubscriptionRepository,
        proration_engine: ProrationEngine,
        pricing_strategy: PricingStrategy,
    ) -> None:
        self._repository = repository
        self._proration_engine = proration_engine
        self._pricing_strategy = pricing_strategy

    def create_subscription(
        self,
        subscription_id: str,
        customer_id: str,
        plan: Plan,
        activate: bool = True,
    ) -> Subscription:
        """Tworzy i utrwala nową subskrypcję w repozytorium."""
        initial_status = SubscriptionStatus.ACTIVE if activate else SubscriptionStatus.TRIAL
        subscription = Subscription(
            id=subscription_id,
            customer_id=customer_id,
            plan=plan,
            status=initial_status,
        )
        self._repository.save(subscription)
        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Pobiera subskrypcję po identyfikatorze."""
        return self._repository.get_by_id(subscription_id)

    def list_subscriptions(self) -> list[Subscription]:
        """Zwraca listę wszystkich zarejestrowanych subskrypcji."""
        return self._repository.list_all()

    def calculate_monthly_bill(self, subscription_id: str) -> Money:
        """Oblicza sumaryczną kwotę rachunku miesięcznego na podstawie wybranej strategii."""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise KeyError(f"Subscription '{subscription_id}' was not found.")

        return self._pricing_strategy.calculate_total(
            plan=subscription.plan,
            usage_units=subscription.usage_units,
        )

    def migrate_plan(
        self,
        subscription_id: str,
        new_plan: Plan,
        current_day: int,
        total_cycle_days: int = DEFAULT_BILLING_CYCLE_DAYS,
    ) -> ProrationResult:
        """Przeprowadza migrację planu subskrypcji w trakcie cyklu rozliczeniowego."""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise KeyError(f"Subscription '{subscription_id}' was not found.")

        result = self._proration_engine.calculate_migration(
            current_price=subscription.plan.base_price,
            new_price=new_plan.base_price,
            current_day=current_day,
            total_cycle_days=total_cycle_days,
        )

        subscription.change_plan(new_plan)
        self._repository.save(subscription)

        return result

    def cancel_subscription(self, subscription_id: str) -> None:
        """Anuluje wskazaną subskrypcję."""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise KeyError(f"Subscription '{subscription_id}' was not found.")

        subscription.cancel()
        self._repository.save(subscription)
