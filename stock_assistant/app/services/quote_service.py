"""Quote orchestration service."""
from __future__ import annotations

from app.data_sources.base import DataResult, QuoteProvider
from app.data_sources.composite import CompositeQuoteProvider
from app.database.db import Database, WatchItem


class QuoteService:
    """Fetch and persist real quotes.

    If a provider cannot return real data, the DataResult contains a user-facing
    error message. The service never creates synthetic quote values.
    """

    def __init__(self, db: Database | None = None, provider: QuoteProvider | None = None) -> None:
        self.db = db
        self.provider = provider or CompositeQuoteProvider()

    def quote_for(self, item: WatchItem) -> DataResult:
        result = self.provider.get_quote(item.symbol, item.market)
        if result.ok and isinstance(result.data, dict) and self.db is not None:
            self.db.insert_quote(result.data)
        return result

    def batch_quotes(self, items: list[WatchItem]) -> list[tuple[WatchItem, DataResult]]:
        return [(item, self.quote_for(item)) for item in items]
