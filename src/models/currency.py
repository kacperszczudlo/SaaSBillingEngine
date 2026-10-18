from enum import Enum


class Currency(Enum):
    """Obsługiwane waluty rozliczeniowe w systemie SaaSBillingEngine."""

    PLN = "PLN"
    EUR = "EUR"
    USD = "USD"
