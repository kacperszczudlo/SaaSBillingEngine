from typing import Optional

from src.models.subscription import Subscription


class InMemorySubscriptionRepository:
    """Implementacja repozytorium subskrypcji w pamięci operacyjnej."""

    def __init__(self) -> None:
        self._storage: dict[str, Subscription] = {}

    def save(self, subscription: Subscription) -> None:
        self._storage[subscription.id] = subscription

    def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        return self._storage.get(subscription_id)

    def list_all(self) -> list[Subscription]:
        return list(self._storage.values())

    def delete(self, subscription_id: str) -> None:
        self._storage.pop(subscription_id, None)

    def clear(self) -> None:
        """Czyści pamięć podręczną (przydatne w testach)."""
        self._storage.clear()
