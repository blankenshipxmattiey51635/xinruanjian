"""Disabled broker interface reserved for future real trading integrations."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrokerOrderRequest:
    symbol: str
    market: str
    side: str
    quantity: int
    price: float | None = None


class BrokerInterfaceDisabled(RuntimeError):
    """Raised whenever first-version code attempts real broker trading."""


class BrokerClient:
    enabled = False

    def place_order(self, request: BrokerOrderRequest) -> None:
        raise BrokerInterfaceDisabled("第一版券商接口默认禁用：不允许自动真实下单。")

    def cancel_order(self, order_id: str) -> None:
        raise BrokerInterfaceDisabled("第一版券商接口默认禁用：不允许撤真实委托。")
