from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.data_sources.eastmoney import EastmoneyQuoteProvider
from app.data_sources.market_symbols import eastmoney_secid, yahoo_symbol
from app.data_sources.yahoo import YahooQuoteProvider
from app.database.db import Database, WatchItem
from app.services.quote_service import QuoteService


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.payload)


def test_symbol_normalization():
    assert eastmoney_secid("600519", "A股") == "1.600519"
    assert eastmoney_secid("300750", "A股") == "0.300750"
    assert eastmoney_secid("000001.SH", "指数") == "1.000001"
    assert yahoo_symbol("IXIC", "指数") == "^IXIC"
    assert yahoo_symbol("AAPL", "美股") == "AAPL"


def test_eastmoney_quote_provider_normalizes_real_payload():
    payload = {
        "data": {
            "f57": "600519",
            "f58": "贵州茅台",
            "f43": 150000,
            "f169": 123,
            "f170": 82,
            "f46": 149000,
            "f60": 148770,
            "f44": 151000,
            "f45": 148000,
            "f47": 10000,
            "f48": 150000000,
            "f19": 149990,
            "f39": 150010,
            "f168": 55,
            "f162": 2500,
            "f167": 800,
            "f116": 1880000000000,
            "f117": 1880000000000,
        }
    }
    provider = EastmoneyQuoteProvider(session=FakeSession(payload))
    result = provider.get_quote("600519", "A股")
    assert result.ok
    assert result.data["price"] == 1500
    assert result.data["change_percent"] == 0.82
    assert result.data["turnover_rate"] == 0.55
    assert result.data["name"] == "贵州茅台"


def test_yahoo_quote_provider_normalizes_real_payload():
    payload = {
        "quoteResponse": {
            "result": [
                {
                    "symbol": "AAPL",
                    "shortName": "Apple Inc.",
                    "regularMarketPrice": 200.5,
                    "regularMarketChange": 1.5,
                    "regularMarketChangePercent": 0.75,
                    "regularMarketOpen": 199,
                    "regularMarketPreviousClose": 199,
                    "regularMarketDayHigh": 201,
                    "regularMarketDayLow": 198,
                    "regularMarketVolume": 123456,
                    "bid": 200.4,
                    "ask": 200.6,
                    "marketCap": 3000000000000,
                    "fiftyTwoWeekHigh": 250,
                    "fiftyTwoWeekLow": 150,
                    "preMarketPrice": 201,
                }
            ]
        }
    }
    provider = YahooQuoteProvider(session=FakeSession(payload))
    result = provider.get_quote("AAPL", "美股")
    assert result.ok
    assert result.data["price"] == 200.5
    assert result.data["week52_high"] == 250
    assert result.data["pre_market_price"] == 201


def test_quote_service_persists_successful_quote(tmp_path):
    payload = {"data": {"f57": "600519", "f58": "贵州茅台", "f43": 150000}}
    provider = EastmoneyQuoteProvider(session=FakeSession(payload))
    db = Database(tmp_path / "quotes.sqlite3")
    db.initialize()
    service = QuoteService(db, provider)
    result = service.quote_for(WatchItem("600519", "贵州茅台", "A股"))
    assert result.ok
    latest = db.latest_quotes()
    assert len(latest) == 1
    assert latest[0]["price"] == 1500
    db.close()
