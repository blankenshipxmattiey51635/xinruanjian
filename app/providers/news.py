from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from app.schemas import NewsItem


class NewsProvider:
    async def get_news(self, symbol: str | None = None, limit: int = 10) -> list[NewsItem]:
        symbols = [symbol.upper()] if symbol else ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]
        items: list[NewsItem] = []
        now = datetime.now(timezone.utc)
        for index in range(limit):
            current_symbol = symbols[index % len(symbols)]
            digest = hashlib.sha1(f"{current_symbol}:{index}:{now.date()}".encode()).hexdigest()[:10]
            items.append(
                NewsItem(
                    id=digest,
                    symbol=current_symbol,
                    title=f"{current_symbol} 实时资讯占位：行情、财报与行业消息聚合 #{index + 1}",
                    source="SimulatedNewsWire",
                    url=f"https://example.com/news/{digest}",
                    sentiment=["positive", "neutral", "negative"][index % 3],
                    published_at=now - timedelta(minutes=index * 3),
                )
            )
        return items
