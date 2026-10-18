from dataclasses import dataclass
from enum import Enum

from src.models.money import Money


class PlanTier(Enum):
    """Poziomy planów subskrypcyjnych."""

    FREE = "FREE"
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


@dataclass(frozen=True)
class Plan:
    """Reprezentacja planu subskrypcyjnego w systemie."""

    tier: PlanTier
    name: str
    base_price: Money
    included_requests: int
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.tier, PlanTier):
            raise TypeError("Plan tier must be an instance of PlanTier enum.")
        if not isinstance(self.base_price, Money):
            raise TypeError("base_price must be an instance of Money.")
        if self.included_requests < 0:
            raise ValueError("included_requests cannot be negative.")
