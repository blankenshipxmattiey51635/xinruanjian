"""Explicit unavailable providers used before real data adapters are wired."""
from __future__ import annotations

from app.data_sources.base import DataResult


class UnavailableQuoteProvider:
    name = "未配置真实行情源"

    def get_quote(self, symbol: str, market: str) -> DataResult:
        return DataResult(
            ok=False,
            source=self.name,
            data=None,
            message=f"{market} {symbol} 数据源不可用：第一阶段尚未接入真实行情接口，界面不会显示伪造行情。",
        )


class UnavailableNewsProvider:
    name = "未配置真实新闻源"

    def search_news(self, keyword: str) -> DataResult:
        return DataResult(
            ok=False,
            source=self.name,
            data=None,
            message=f"{keyword} 暂无真实数据：第一阶段尚未接入真实新闻接口。",
        )
