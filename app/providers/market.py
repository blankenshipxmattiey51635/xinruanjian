from __future__ import annotations

import hashlib
import math
import random
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Protocol

from app.schemas import IndicatorPoint, Quote


class MarketDataProvider(Protocol):
    async def get_quote(self, symbol: str) -> Quote: ...
    async def get_history(self, symbol: str, points: int = 120) -> list[IndicatorPoint]: ...


class SimulatedMarketDataProvider:
    """Deterministic market-data adapter used until real vendor adapters are configured."""

    def __init__(self) -> None:
        self._history: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=240))
        self._last_seen: dict[str, float] = {}

    async def get_quote(self, symbol: str) -> Quote:
        start = time.perf_counter()
        symbol = symbol.upper()
        price = self._next_price(symbol)
        previous = self._history[symbol][-2] if len(self._history[symbol]) > 1 else price
        change = price - previous
        latency_ms = max(1, int((time.perf_counter() - start) * 1000))
        return Quote(
            symbol=symbol,
            price=round(price, 2),
            change=round(change, 2),
            change_percent=round((change / previous) * 100 if previous else 0, 2),
            volume=self._volume(symbol),
            bid=round(price - 0.01, 2),
            ask=round(price + 0.01, 2),
            latency_ms=latency_ms,
        )

    async def get_history(self, symbol: str, points: int = 120) -> list[IndicatorPoint]:
        symbol = symbol.upper()
        while len(self._history[symbol]) < points:
            self._next_price(symbol)
        prices = list(self._history[symbol])[-points:]
        now = datetime.now(timezone.utc)
        return [
            IndicatorPoint(
                timestamp=now - timedelta(seconds=(len(prices) - index) * 5),
                price=round(price, 2),
                ma5=round(self._ma(prices, index, 5), 2),
                ma20=round(self._ma(prices, index, 20), 2),
                rsi14=round(self._rsi(prices[: index + 1], 14), 2),
            )
            for index, price in enumerate(prices)
        ]

    def _next_price(self, symbol: str) -> float:
        seed = int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)
        base = 20 + seed % 500
        last = self._history[symbol][-1] if self._history[symbol] else float(base)
        tick = self._last_seen.get(symbol, time.time())
        elapsed = max(1.0, time.time() - tick)
        self._last_seen[symbol] = time.time()
        wave = math.sin(time.time() / 20 + seed) * 0.2
        random_walk = random.Random(f"{symbol}:{int(time.time() / 2)}").uniform(-0.35, 0.35)
        next_price = max(0.01, last + wave + random_walk * elapsed)
        self._history[symbol].append(next_price)
        return next_price

    def _volume(self, symbol: str) -> int:
        seed = int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)
        return 100_000 + seed % 5_000_000 + int(time.time()) % 50_000

    @staticmethod
    def _ma(prices: list[float], index: int, window: int) -> float:
        samples = prices[max(0, index - window + 1) : index + 1]
        return sum(samples) / len(samples)

    @staticmethod
    def _rsi(prices: list[float], window: int) -> float:
        if len(prices) < 2:
            return 50.0
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))][-window:]
        gains = [delta for delta in deltas if delta > 0]
        losses = [-delta for delta in deltas if delta < 0]
        avg_gain = sum(gains) / window if gains else 0.001
        avg_loss = sum(losses) / window if losses else 0.001
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
