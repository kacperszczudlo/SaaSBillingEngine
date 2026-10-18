from decimal import Decimal
from typing import Optional

from flask import Flask

from src.models.currency import Currency
from src.models.money import Money
from src.models.plan import Plan, PlanTier
from src.repositories.in_memory import InMemorySubscriptionRepository
from src.services.billing_service import BillingService
from src.services.pricing_strategy import TieredUsagePricingStrategy
from src.services.proration_engine import ProrationEngine
from src.web.routes import web_bp


def get_default_plans_catalog() -> dict[PlanTier, Plan]:
    """Zwraca domyślny katalog planów subskrypcyjnych."""
    return {
        PlanTier.FREE: Plan(
            tier=PlanTier.FREE,
            name="Free Tier",
            base_price=Money(Decimal("0.00"), Currency.PLN),
            included_requests=100,
            description="Dla hobbystów i małych testów integracyjnych",
        ),
        PlanTier.STARTER: Plan(
            tier=PlanTier.STARTER,
            name="Starter",
            base_price=Money(Decimal("49.00"), Currency.PLN),
            included_requests=1000,
            description="Dla rosnących mikroserwisów i startupów",
        ),
        PlanTier.PRO: Plan(
            tier=PlanTier.PRO,
            name="Pro Business",
            base_price=Money(Decimal("149.00"), Currency.PLN),
            included_requests=5000,
            description="Dla skalujących się platform z dużym ruchem API",
        ),
        PlanTier.ENTERPRISE: Plan(
            tier=PlanTier.ENTERPRISE,
            name="Enterprise Elite",
            base_price=Money(Decimal("499.00"), Currency.PLN),
            included_requests=25000,
            description="Pełne wsparcie SLA i nielimitowane stanowiska",
        ),
    }


def create_app(billing_service: Optional[BillingService] = None) -> Flask:
    """Fabryka aplikacji Flask z rejestracją Blueprintów i konfiguracji."""
    app = Flask(__name__)

    # Konfiguracja silnika i katalogu planów
    proration_engine = ProrationEngine()
    pricing_strategy = TieredUsagePricingStrategy()
    plans_catalog = get_default_plans_catalog()

    if billing_service is None:
        repository = InMemorySubscriptionRepository()
        billing_service = BillingService(
            repository=repository,
            proration_engine=proration_engine,
            pricing_strategy=pricing_strategy,
        )

        # Początkowe dane demonstracyjne
        initial_sub = billing_service.create_subscription(
            subscription_id="sub-001",
            customer_id="Acme-Corporation",
            plan=plans_catalog[PlanTier.STARTER],
            activate=True,
        )
        initial_sub.record_usage(1400)

    app.config["BILLING_SERVICE"] = billing_service
    app.config["PRORATION_ENGINE"] = proration_engine
    app.config["PRICING_STRATEGY"] = pricing_strategy
    app.config["PLANS_CATALOG"] = plans_catalog

    app.register_blueprint(web_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
