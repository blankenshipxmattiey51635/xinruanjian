"""Eastmoney public quote provider for A-share, ETF, convertible bond and CN index quotes."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.data_sources.base import DataResult
from app.data_sources.market_symbols import eastmoney_secid
from app.data_sources.quote_model import Quote
from app.data_sources.http_client import HttpClientError, UrllibSession


def _num(value: Any, scale: float = 1.0) -> float | None:
    if value in (None, "", "-", "--"):
        return None
    try:
        return float(value) / scale
    except (TypeError, ValueError):
        return None


class EastmoneyQuoteProvider:
    """Fetch real quotes from Eastmoney's public quote endpoint.

    This provider never fabricates fallback values. Network errors, missing
    symbols and changed response shapes are returned as DataResult(ok=False).
    """

    name = "东方财富公开行情"
    endpoint = "https://push2.eastmoney.com/api/qt/stock/get"
    fields = ",".join(
        [
            "f57",  # code
            "f58",  # name
            "f43",  # latest price * 100
            "f169",  # change amount * 100
            "f170",  # change percent * 100
            "f46",  # open * 100
            "f60",  # previous close * 100
            "f44",  # high * 100
            "f45",  # low * 100
            "f47",  # volume
            "f48",  # turnover amount
            "f19",  # bid 1 * 100
            "f39",  # ask 1 * 100
            "f168",  # turnover rate * 100
            "f162",  # PE * 100
            "f167",  # PB * 100
            "f116",  # total market value
            "f117",  # float market value
            "f86",  # timestamp
        ]
    )

    def __init__(self, session: object | None = None, timeout: float = 4.0) -> None:
        self.session = session or UrllibSession()
        self.timeout = timeout

    def get_quote(self, symbol: str, market: str) -> DataResult:
        secid = eastmoney_secid(symbol, market)
        if not secid:
            return DataResult(False, self.name, None, f"{market} {symbol} 无法识别为东方财富支持的 A股/指数代码。")
        try:
            response = self.session.get(
                self.endpoint,
                params={"secid": secid, "fields": self.fields, "invt": "2", "fltt": "1"},
                headers={"User-Agent": "Mozilla/5.0 StockAssistant/0.2"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except HttpClientError as exc:
            return DataResult(False, self.name, None, f"东方财富行情请求失败：{exc}")
        except ValueError as exc:
            return DataResult(False, self.name, None, f"东方财富返回非 JSON 数据：{exc}")
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            return DataResult(False, self.name, None, f"{market} {symbol} 数据源不可用：东方财富未返回有效行情。")
        quote = Quote(
            symbol=str(data.get("f57") or symbol).upper(),
            name=str(data.get("f58") or ""),
            market=market,
            source=self.name,
            price=_num(data.get("f43"), 100),
            change_amount=_num(data.get("f169"), 100),
            change_percent=_num(data.get("f170"), 100),
            open_price=_num(data.get("f46"), 100),
            previous_close=_num(data.get("f60"), 100),
            high_price=_num(data.get("f44"), 100),
            low_price=_num(data.get("f45"), 100),
            volume=_num(data.get("f47")),
            turnover=_num(data.get("f48")),
            bid1=_num(data.get("f19"), 100),
            ask1=_num(data.get("f39"), 100),
            turnover_rate=_num(data.get("f168"), 100),
            pe_ratio=_num(data.get("f162"), 100),
            pb_ratio=_num(data.get("f167"), 100),
            total_market_value=_num(data.get("f116")),
            float_market_value=_num(data.get("f117")),
            fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            raw=data,
        )
        if quote.price is None:
            return DataResult(False, self.name, None, f"{market} {symbol} 暂无真实价格，可能停牌、休市或接口字段变化。")
        return DataResult(True, self.name, quote.to_dict(), "")
