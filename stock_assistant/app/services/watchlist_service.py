"""Business logic for watchlist management."""
from __future__ import annotations

from app.database.db import Database, WatchItem


class WatchlistService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, symbol: str, name: str, market: str, asset_type: str = "股票", note: str = "") -> None:
        clean_symbol = symbol.strip().upper()
        if not clean_symbol:
            raise ValueError("股票代码不能为空")
        if market not in {"A股", "美股", "指数", "ETF", "可转债"}:
            raise ValueError("市场类型不支持")
        self.db.add_watch_item(WatchItem(clean_symbol, name.strip(), market, asset_type, note.strip()))

    def remove(self, symbol: str, market: str) -> None:
        self.db.remove_watch_item(symbol.strip().upper(), market)

    def list_all(self) -> list[WatchItem]:
        return self.db.list_watch_items()
