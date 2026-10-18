import unittest
from decimal import Decimal

from src.models.currency import Currency
from src.models.money import Money
from src.models.plan import Plan, PlanTier
from src.models.subscription import (
    InvalidStateTransitionError,
    Subscription,
    SubscriptionStatus,
)


class TestSubscription(unittest.TestCase):
    """Zestaw testów jednostkowych dla cyklu życia i maszyny stanów subskrypcji."""

    def setUp(self):
        self.plan = Plan(
            tier=PlanTier.STARTER,
            name="Starter Plan",
            base_price=Money(Decimal("49.00"), Currency.PLN),
            included_requests=1000,
            description="Dla małych zespołów",
        )
        self.subscription = Subscription(
            id="sub-101",
            customer_id="cust-001",
            plan=self.plan,
            status=SubscriptionStatus.TRIAL,
            current_cycle_day=1,
        )

    def test_should_initialize_subscription_in_trial_status_by_default(self):
        # Assert
        self.assertEqual(self.subscription.status, SubscriptionStatus.TRIAL)

    def test_should_transition_from_trial_to_active_status(self):
        # Act
        self.subscription.activate()

        # Assert
        self.assertEqual(self.subscription.status, SubscriptionStatus.ACTIVE)

    def test_should_transition_from_active_to_past_due_status(self):
        # Arrange
        self.subscription.activate()

        # Act
        self.subscription.mark_past_due()

        # Assert
        self.assertEqual(self.subscription.status, SubscriptionStatus.PAST_DUE)

    def test_should_transition_from_past_due_to_active_status(self):
        # Arrange
        self.subscription.activate()
        self.subscription.mark_past_due()

        # Act
        self.subscription.activate()

        # Assert
        self.assertEqual(self.subscription.status, SubscriptionStatus.ACTIVE)

    def test_should_cancel_active_subscription(self):
        # Arrange
        self.subscription.activate()

        # Act
        self.subscription.cancel()

        # Assert
        self.assertEqual(self.subscription.status, SubscriptionStatus.CANCELLED)

    def test_should_raise_error_when_attempting_to_activate_cancelled_subscription(self):
        # Arrange
        self.subscription.cancel()

        # Act & Assert
        with self.assertRaises(InvalidStateTransitionError):
            self.subscription.activate()

    def test_should_record_usage_units_and_prevent_negative_usage(self):
        # Arrange
        self.subscription.activate()

        # Act
        self.subscription.record_usage(250)

        # Assert
        self.assertEqual(self.subscription.usage_units, 250)
