from typing import Optional, Protocol

from src.models.subscription import Subscription


class SubscriptionRepository(Protocol):
    """Abstrakcyjny interfejs repozytorium subskrypcji (zasada Dependency Inversion)."""

    def save(self, subscription: Subscription) -> None:
        """Zapisuje lub aktualizuje subskrypcję."""
        ...

    def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """Pobiera subskrypcję po identyfikatorze lub zwraca None."""
        ...

    def list_all(self) -> list[Subscription]:
        """Zwraca listę wszystkich subskrypcji."""
        ...

    def delete(self, subscription_id: str) -> None:
        """Usuwa subskrypcję po identyfikatorze."""
        ...
