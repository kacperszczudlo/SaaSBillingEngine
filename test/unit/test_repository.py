import unittest
from decimal import Decimal

from src.models.currency import Currency
from src.models.money import Money
from src.models.plan import Plan, PlanTier
from src.models.subscription import Subscription, SubscriptionStatus
from src.repositories.in_memory import InMemorySubscriptionRepository


class TestInMemorySubscriptionRepository(unittest.TestCase):
    """Zestaw testów jednostkowych dla repozytorium pamięciowego InMemorySubscriptionRepository."""

    def setUp(self):
        self.repository = InMemorySubscriptionRepository()
        self.plan = Plan(
            tier=PlanTier.STARTER,
            name="Starter Plan",
            base_price=Money(Decimal("49.00"), Currency.PLN),
            included_requests=1000,
        )
        self.subscription = Subscription(
            id="sub-101",
            customer_id="cust-001",
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
        )

    def test_should_save_and_retrieve_subscription_by_id(self):
        # Act
        self.repository.save(self.subscription)
        retrieved = self.repository.get_by_id("sub-101")

        # Assert
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "sub-101")  # type: ignore

    def test_should_return_none_when_subscription_not_found(self):
        # Act
        result = self.repository.get_by_id("non-existent-id")

        # Assert
        self.assertIsNone(result)

    def test_should_list_all_saved_subscriptions(self):
        # Arrange
        second_sub = Subscription(
            id="sub-102",
            customer_id="cust-002",
            plan=self.plan,
            status=SubscriptionStatus.TRIAL,
        )
        self.repository.save(self.subscription)
        self.repository.save(second_sub)

        # Act
        all_subs = self.repository.list_all()

        # Assert
        self.assertEqual(len(all_subs), 2)

    def test_should_delete_subscription_by_id(self):
        # Arrange
        self.repository.save(self.subscription)

        # Act
        self.repository.delete("sub-101")

        # Assert
        self.assertIsNone(self.repository.get_by_id("sub-101"))

    def test_should_clear_all_subscriptions_from_repository(self):
        # Arrange
        self.repository.save(self.subscription)

        # Act
        self.repository.clear()

        # Assert
        self.assertEqual(len(self.repository.list_all()), 0)
