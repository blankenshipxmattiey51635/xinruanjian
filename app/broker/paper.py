from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.providers.market import MarketDataProvider
from app.schemas import Order, OrderRequest


class PaperBroker:
    """Paper-trading adapter that mirrors the interface expected from real broker gateways."""

    def __init__(self, market_provider: MarketDataProvider) -> None:
        self._market_provider = market_provider
        self._orders: list[Order] = []

    async def submit_order(self, request: OrderRequest) -> Order:
        quote = await self._market_provider.get_quote(request.symbol)
        if request.order_type == "limit" and request.limit_price is None:
            status = "rejected"
            filled_price = None
            message = "限价单必须提供 limit_price。"
        else:
            status = "filled"
            filled_price = quote.ask if request.side == "buy" else quote.bid
            message = "纸面交易成交；接入真实券商前不会发送真实委托。"
        order = Order(
            id=str(uuid.uuid4()),
            symbol=request.symbol.upper(),
            side=request.side,
            quantity=request.quantity,
            order_type=request.order_type,
            status=status,
            submitted_at=datetime.now(timezone.utc),
            filled_price=filled_price,
            message=message,
        )
        self._orders.append(order)
        return order

    def list_orders(self) -> list[Order]:
        return self._orders
