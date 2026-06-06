"""Timed market scan orchestration for phase two."""
from __future__ import annotations

from app.data_sources.market_symbols import COMMON_INDICES
from app.database.db import WatchItem
from app.services.quote_service import QuoteService


class MarketScanService:
    """Scan configured symbols using real quote providers only."""

    def __init__(self, quotes: QuoteService) -> None:
        self.quotes = quotes

    def common_indices(self) -> list[WatchItem]:
        return [
            WatchItem(symbol=symbol, name=index.display, market="指数", asset_type="指数")
            for symbol, index in COMMON_INDICES.items()
        ]

    def scan(self, items: list[WatchItem]) -> tuple[int, int, list[str]]:
        ok = 0
        failed = 0
        messages: list[str] = []
        for item, result in self.quotes.batch_quotes(items):
            if result.ok:
                ok += 1
            else:
                failed += 1
                messages.append(f"{item.market} {item.symbol}: {result.message}")
        return ok, failed, messages[:10]
