"""Yahoo Finance public quote provider for US stocks, ETFs and US indices."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.data_sources.base import DataResult
from app.data_sources.market_symbols import yahoo_symbol
from app.data_sources.quote_model import Quote
from app.data_sources.http_client import HttpClientError, UrllibSession


def _num(value: Any) -> float | None:
    if value in (None, "", "-", "--"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class YahooQuoteProvider:
    """Fetch real quotes from Yahoo Finance's public quote endpoint."""

    name = "Yahoo Finance 公开行情"
    endpoint = "https://query1.finance.yahoo.com/v7/finance/quote"

    def __init__(self, session: object | None = None, timeout: float = 4.0) -> None:
        self.session = session or UrllibSession()
        self.timeout = timeout

    def get_quote(self, symbol: str, market: str) -> DataResult:
        yf_symbol = yahoo_symbol(symbol, market)
        try:
            response = self.session.get(
                self.endpoint,
                params={"symbols": yf_symbol, "formatted": "false"},
                headers={"User-Agent": "Mozilla/5.0 StockAssistant/0.2"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except HttpClientError as exc:
            return DataResult(False, self.name, None, f"Yahoo Finance 行情请求失败：{exc}")
        except ValueError as exc:
            return DataResult(False, self.name, None, f"Yahoo Finance 返回非 JSON 数据：{exc}")
        result = (((payload or {}).get("quoteResponse") or {}).get("result") or []) if isinstance(payload, dict) else []
        if not result:
            return DataResult(False, self.name, None, f"{market} {symbol} 数据源不可用：Yahoo Finance 未返回有效行情。")
        item = result[0]
        quote = Quote(
            symbol=str(item.get("symbol") or yf_symbol),
            name=str(item.get("shortName") or item.get("longName") or item.get("displayName") or ""),
            market=market,
            source=self.name,
            price=_num(item.get("regularMarketPrice")),
            change_amount=_num(item.get("regularMarketChange")),
            change_percent=_num(item.get("regularMarketChangePercent")),
            open_price=_num(item.get("regularMarketOpen")),
            previous_close=_num(item.get("regularMarketPreviousClose")),
            high_price=_num(item.get("regularMarketDayHigh")),
            low_price=_num(item.get("regularMarketDayLow")),
            volume=_num(item.get("regularMarketVolume")),
            bid1=_num(item.get("bid")),
            ask1=_num(item.get("ask")),
            pe_ratio=_num(item.get("trailingPE")),
            total_market_value=_num(item.get("marketCap")),
            week52_high=_num(item.get("fiftyTwoWeekHigh")),
            week52_low=_num(item.get("fiftyTwoWeekLow")),
            pre_market_price=_num(item.get("preMarketPrice")),
            post_market_price=_num(item.get("postMarketPrice")),
            fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            raw=item,
        )
        if quote.price is None:
            return DataResult(False, self.name, None, f"{market} {symbol} 暂无真实价格，可能休市或接口字段变化。")
        return DataResult(True, self.name, quote.to_dict(), "")
