"""Quote orchestration service.

The service is deliberately honest: if no real provider is available it returns
"数据源不可用" instead of generating placeholder prices.
"""
from __future__ import annotations

from app.data_sources.base import DataResult, QuoteProvider
from app.data_sources.unavailable import UnavailableQuoteProvider
from app.database.db import WatchItem


class QuoteService:
    def __init__(self, provider: QuoteProvider | None = None) -> None:
        self.provider = provider or UnavailableQuoteProvider()

    def quote_for(self, item: WatchItem) -> DataResult:
        return self.provider.get_quote(item.symbol, item.market)
