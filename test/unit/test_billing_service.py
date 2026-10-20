import unittest
from decimal import Decimal

from src.models.currency import Currency
from src.models.money import Money
from src.models.plan import Plan, PlanTier
from src.models.subscription import SubscriptionStatus
from src.repositories.in_memory import InMemorySubscriptionRepository
from src.services.billing_service import BillingService
from src.services.pricing_strategy import TieredUsagePricingStrategy
from src.services.proration_engine import ProrationEngine


class TestBillingService(unittest.TestCase):
    """Zestaw testów jednostkowych dla serwisu aplikacyjnego BillingService."""

    def setUp(self):
        self.repository = InMemorySubscriptionRepository()
        self.proration_engine = ProrationEngine()
        self.pricing_strategy = TieredUsagePricingStrategy()
        self.service = BillingService(
            repository=self.repository,
            proration_engine=self.proration_engine,
            pricing_strategy=self.pricing_strategy,
        )

        self.starter_plan = Plan(
            tier=PlanTier.STARTER,
            name="Starter Plan",
            base_price=Money(Decimal("50.00"), Currency.PLN),
            included_requests=1000,
        )
        self.pro_plan = Plan(
            tier=PlanTier.PRO,
            name="Pro Plan",
            base_price=Money(Decimal("150.00"), Currency.PLN),
            included_requests=5000,
        )

    def test_should_create_and_persist_active_subscription(self):
        # Act
        sub = self.service.create_subscription(
            subscription_id="sub-001",
            customer_id="cust-001",
            plan=self.starter_plan,
            activate=True,
        )

        # Assert
        self.assertEqual(sub.status, SubscriptionStatus.ACTIVE)

    def test_should_calculate_monthly_bill_using_pricing_strategy(self):
        # Arrange
        sub = self.service.create_subscription(
            subscription_id="sub-001",
            customer_id="cust-001",
            plan=self.starter_plan,
        )
        sub.record_usage(1500)  # 500 nadmiarowych x 0.05 PLN = 25.00 PLN dopłaty

        # Act
        bill = self.service.calculate_monthly_bill("sub-001")

        # Assert
        self.assertEqual(bill.amount, Decimal("75.00"))

    def test_should_raise_key_error_when_calculating_bill_for_non_existent_subscription(self):
        # Act & Assert
        with self.assertRaises(KeyError):
            self.service.calculate_monthly_bill("non-existent-sub")

    def test_should_migrate_subscription_plan_and_update_repository(self):
        # Arrange: dzień 15 z 30 (połowa cyklu)
        self.service.create_subscription(
            subscription_id="sub-001",
            customer_id="cust-001",
            plan=self.starter_plan,
        )

        # Act: migracja ze Starter (50 zł) na Pro (150 zł) w połowie miesiąca
        result = self.service.migrate_plan(
            subscription_id="sub-001",
            new_plan=self.pro_plan,
            current_day=15,
            total_cycle_days=30,
        )

        # Assert
        # Kredyt ze starego planu: 25.00 zł
        # Koszt nowego planu na 15 dni: 75.00 zł
        # Dopłata netto: 50.00 zł
        self.assertEqual(result.net_amount_due.amount, Decimal("50.00"))

    def test_should_raise_key_error_when_migrating_non_existent_subscription(self):
        # Act & Assert
        with self.assertRaises(KeyError):
            self.service.migrate_plan(
                subscription_id="non-existent",
                new_plan=self.pro_plan,
                current_day=15,
            )

    def test_should_cancel_subscription_and_persist_state(self):
        # Arrange
        self.service.create_subscription(
            subscription_id="sub-001",
            customer_id="cust-001",
            plan=self.starter_plan,
        )

        # Act
        self.service.cancel_subscription("sub-001")
        cancelled_sub = self.service.get_subscription("sub-001")

        # Assert
        self.assertEqual(cancelled_sub.status, SubscriptionStatus.CANCELLED)  # type: ignore

    def test_should_raise_key_error_when_cancelling_non_existent_subscription(self):
        # Act & Assert
        with self.assertRaises(KeyError):
            self.service.cancel_subscription("non-existent-sub")

    def test_should_list_all_subscriptions_from_service(self):
        # Arrange
        self.service.create_subscription("sub-001", "cust-001", self.starter_plan)
        self.service.create_subscription("sub-002", "cust-002", self.pro_plan)

        # Act
        all_subs = self.service.list_subscriptions()

        # Assert
        self.assertEqual(len(all_subs), 2)
