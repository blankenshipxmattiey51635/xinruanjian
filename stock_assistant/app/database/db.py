"""Small SQLite data-access layer for phase one."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.database.models import SCHEMA_SQL
from app.utils.paths import ensure_runtime_dirs


@dataclass(slots=True)
class WatchItem:
    symbol: str
    name: str
    market: str
    asset_type: str = "股票"
    note: str = ""
    enabled: bool = True


class Database:
    """Owns the SQLite connection and phase-one persistence methods."""

    def __init__(self, path: Path | None = None) -> None:
        dirs = ensure_runtime_dirs()
        self.path = path or dirs["data"] / "stock_assistant.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row

    def initialize(self) -> None:
        self.connection.executescript(SCHEMA_SQL)
        self._migrate_quotes_table()
        self.connection.commit()

    def _migrate_quotes_table(self) -> None:
        columns = {row["name"] for row in self.connection.execute("PRAGMA table_info(quotes)")}
        if "turnover_rate" not in columns:
            self.connection.execute("ALTER TABLE quotes ADD COLUMN turnover_rate REAL")

    def close(self) -> None:
        self.connection.close()

    def add_watch_item(self, item: WatchItem) -> None:
        self.connection.execute(
            """
            INSERT INTO watchlist(symbol, name, market, asset_type, note, enabled)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, market) DO UPDATE SET
                name=excluded.name,
                asset_type=excluded.asset_type,
                note=excluded.note,
                enabled=excluded.enabled,
                updated_at=CURRENT_TIMESTAMP
            """,
            (item.symbol.upper(), item.name, item.market, item.asset_type, item.note, int(item.enabled)),
        )
        self.connection.commit()

    def remove_watch_item(self, symbol: str, market: str) -> None:
        self.connection.execute(
            "DELETE FROM watchlist WHERE symbol = ? AND market = ?",
            (symbol.upper(), market),
        )
        self.connection.commit()

    def list_watch_items(self) -> list[WatchItem]:
        rows: Iterable[sqlite3.Row] = self.connection.execute(
            """
            SELECT symbol, name, market, asset_type, note, enabled
            FROM watchlist
            ORDER BY market, symbol
            """
        )
        return [
            WatchItem(
                symbol=row["symbol"],
                name=row["name"],
                market=row["market"],
                asset_type=row["asset_type"],
                note=row["note"],
                enabled=bool(row["enabled"]),
            )
            for row in rows
        ]

    def insert_quote(self, quote: dict) -> None:
        self.connection.execute(
            """
            INSERT INTO quotes(
                symbol, market, source, price, change_amount, change_percent,
                open_price, previous_close, high_price, low_price, volume, turnover,
                bid1, ask1, turnover_rate, pe_ratio, pb_ratio, total_market_value,
                float_market_value, week52_high, week52_low, pre_market_price,
                post_market_price, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                quote.get("symbol"), quote.get("market"), quote.get("source"), quote.get("price"),
                quote.get("change_amount"), quote.get("change_percent"), quote.get("open_price"),
                quote.get("previous_close"), quote.get("high_price"), quote.get("low_price"),
                quote.get("volume"), quote.get("turnover"), quote.get("bid1"), quote.get("ask1"),
                quote.get("turnover_rate"), quote.get("pe_ratio"), quote.get("pb_ratio"),
                quote.get("total_market_value"), quote.get("float_market_value"), quote.get("week52_high"),
                quote.get("week52_low"), quote.get("pre_market_price"), quote.get("post_market_price"),
                quote.get("fetched_at"),
            ),
        )
        self.connection.commit()

    def latest_quotes(self, limit: int = 100) -> list[sqlite3.Row]:
        return list(
            self.connection.execute(
                """
                SELECT * FROM quotes
                ORDER BY fetched_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )
        )

    def log(self, level: str, message: str, context_json: str = "{}") -> None:
        self.connection.execute(
            "INSERT INTO app_logs(level, message, context_json) VALUES (?, ?, ?)",
            (level, message, context_json),
        )
        self.connection.commit()
