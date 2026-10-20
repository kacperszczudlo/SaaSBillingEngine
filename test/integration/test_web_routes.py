import unittest
from http import HTTPStatus

from src.models.plan import PlanTier
from src.web.app import create_app


class TestWebRoutes(unittest.TestCase):
    """Zestaw testów integracyjnych dla tras i widoków aplikacji webowej Flask (min. 10 testów)."""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_should_render_dashboard_with_200_ok(self):
        # Act
        response = self.client.get("/")

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_return_plans_catalog_via_json_api(self):
        # Act
        response = self.client.get("/api/plans")

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_calculate_proration_via_rest_api(self):
        # Arrange: zmiana z STARTER na PRO w 15. dniu cyklu
        payload = {
            "from_tier": PlanTier.STARTER.value,
            "to_tier": PlanTier.PRO.value,
            "current_day": 15,
            "total_cycle_days": 30,
        }

        # Act
        response = self.client.post("/api/proration/calculate", json=payload)
        data = response.get_json()

        # Assert
        # Starter 49 zł / 2 = 24.50 zł kredytu
        # Pro 149 zł / 2 = 74.50 zł kosztu
        # Net due = 50.00 zł
        self.assertEqual(data["net_amount_due"], "50.00")

    def test_should_return_400_when_proration_api_receives_invalid_payload(self):
        # Arrange
        invalid_payload = {"from_tier": "NON_EXISTENT_PLAN"}

        # Act
        response = self.client.post("/api/proration/calculate", json=invalid_payload)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_should_return_422_when_proration_api_receives_out_of_bound_day(self):
        # Arrange: dzień 35 przekracza 30 dni cyklu
        payload = {
            "from_tier": PlanTier.STARTER.value,
            "to_tier": PlanTier.PRO.value,
            "current_day": 35,
            "total_cycle_days": 30,
        }

        # Act
        response = self.client.post("/api/proration/calculate", json=payload)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_should_create_new_subscription_via_form_post(self):
        # Arrange
        form_data = {
            "customer_id": "Test-Client-Corp",
            "plan_tier": PlanTier.PRO.value,
        }

        # Act
        response = self.client.post("/subscriptions", data=form_data, follow_redirects=True)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_return_400_when_creating_subscription_with_missing_fields(self):
        # Arrange: brak customer_id
        invalid_form = {"plan_tier": PlanTier.PRO.value}

        # Act
        response = self.client.post("/subscriptions", data=invalid_form)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_should_return_400_when_creating_subscription_with_invalid_tier(self):
        # Arrange
        invalid_form = {"customer_id": "Acme", "plan_tier": "INVALID_TIER"}

        # Act
        response = self.client.post("/subscriptions", data=invalid_form)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_should_migrate_subscription_and_redirect_to_dashboard(self):
        # Arrange: domyślnie istnieje sub-001 (Starter)
        migration_data = {
            "target_tier": PlanTier.PRO.value,
            "current_day": "15",
        }

        # Act
        response = self.client.post("/subscriptions/sub-001/migrate", data=migration_data, follow_redirects=True)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_return_404_when_migrating_non_existent_subscription(self):
        # Arrange
        migration_data = {
            "target_tier": PlanTier.PRO.value,
            "current_day": "15",
        }

        # Act
        response = self.client.post("/subscriptions/sub-999-missing/migrate", data=migration_data)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_should_return_400_when_migrating_with_invalid_day_format(self):
        # Arrange
        migration_data = {
            "target_tier": PlanTier.PRO.value,
            "current_day": "not-a-number",
        }

        # Act
        response = self.client.post("/subscriptions/sub-001/migrate", data=migration_data)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_should_return_422_when_migrating_with_day_exceeding_cycle(self):
        # Arrange: dzień 45 w cyklu 30-dniowym
        migration_data = {
            "target_tier": PlanTier.PRO.value,
            "current_day": "45",
        }

        # Act
        response = self.client.post("/subscriptions/sub-001/migrate", data=migration_data)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_should_cancel_subscription_via_form_post(self):
        # Act
        response = self.client.post("/subscriptions/sub-001/cancel", follow_redirects=True)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_return_404_when_cancelling_non_existent_subscription(self):
        # Act
        response = self.client.post("/subscriptions/sub-999-missing/cancel")

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_should_render_invoice_page_with_200_ok(self):
        # Act
        response = self.client.get("/subscriptions/sub-001/invoice")

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_should_return_404_when_viewing_invoice_for_non_existent_subscription(self):
        # Act
        response = self.client.get("/subscriptions/sub-999-missing/invoice")

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
