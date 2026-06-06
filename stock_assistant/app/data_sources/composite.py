"""Composite real quote provider selecting a market-specific free source."""
from __future__ import annotations

from app.data_sources.base import DataResult
from app.data_sources.eastmoney import EastmoneyQuoteProvider
from app.data_sources.unavailable import UnavailableQuoteProvider
from app.data_sources.yahoo import YahooQuoteProvider


class CompositeQuoteProvider:
    """Route A-share/index quotes to Eastmoney and US quotes to Yahoo Finance."""

    name = "真实免费行情组合源"

    def __init__(self, eastmoney: EastmoneyQuoteProvider | None = None, yahoo: YahooQuoteProvider | None = None) -> None:
        self.eastmoney = eastmoney or EastmoneyQuoteProvider()
        self.yahoo = yahoo or YahooQuoteProvider()
        self.unavailable = UnavailableQuoteProvider()

    def get_quote(self, symbol: str, market: str) -> DataResult:
        if market in {"A股", "ETF", "可转债"}:
            return self.eastmoney.get_quote(symbol, market)
        if market == "美股":
            return self.yahoo.get_quote(symbol, market)
        if market == "指数":
            eastmoney_result = self.eastmoney.get_quote(symbol, market)
            if eastmoney_result.ok:
                return eastmoney_result
            yahoo_result = self.yahoo.get_quote(symbol, market)
            if yahoo_result.ok:
                return yahoo_result
            return DataResult(
                False,
                self.name,
                None,
                f"指数 {symbol} 数据源不可用。东方财富：{eastmoney_result.message}；Yahoo：{yahoo_result.message}",
            )
        return self.unavailable.get_quote(symbol, market)
