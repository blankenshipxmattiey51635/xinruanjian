from __future__ import annotations

from app.providers.market import MarketDataProvider
from app.schemas import StrategyPick, StrategyRequest


class StrategyEngine:
    def __init__(self, market_provider: MarketDataProvider) -> None:
        self._market_provider = market_provider

    async def run(self, request: StrategyRequest) -> list[StrategyPick]:
        picks: list[StrategyPick] = []
        for symbol in request.universe:
            quote = await self._market_provider.get_quote(symbol)
            if not (request.rule.min_price <= quote.price <= request.rule.max_price):
                continue
            if quote.volume < request.rule.min_volume:
                continue
            if quote.change_percent < request.rule.min_momentum_percent:
                continue
            score = quote.change_percent * 2 + min(quote.volume / 1_000_000, 10)
            reasons = [
                f"价格 {quote.price} 在筛选区间内",
                f"成交量 {quote.volume:,} 满足最低要求",
                f"短线动量 {quote.change_percent}% 满足阈值",
            ]
            picks.append(StrategyPick(symbol=quote.symbol, score=round(score, 2), reasons=reasons, quote=quote))
        return sorted(picks, key=lambda pick: pick.score, reverse=True)
