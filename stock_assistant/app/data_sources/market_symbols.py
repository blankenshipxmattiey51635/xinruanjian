"""Market symbol normalization helpers.

The second-stage providers are public/free web quote endpoints. They can change
or rate-limit, so callers must surface provider errors instead of fabricating
fallback prices.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IndexSymbol:
    display: str
    eastmoney_secid: str | None = None
    yahoo_symbol: str | None = None


COMMON_INDICES: dict[str, IndexSymbol] = {
    "000001.SH": IndexSymbol("上证指数", "1.000001", "000001.SS"),
    "399001.SZ": IndexSymbol("深证成指", "0.399001", "399001.SZ"),
    "399006.SZ": IndexSymbol("创业板指", "0.399006", "399006.SZ"),
    "000688.SH": IndexSymbol("科创50", "1.000688", "000688.SS"),
    "000300.SH": IndexSymbol("沪深300", "1.000300", "000300.SS"),
    "000905.SH": IndexSymbol("中证500", "1.000905", "000905.SS"),
    "IXIC": IndexSymbol("纳斯达克指数", None, "^IXIC"),
    "GSPC": IndexSymbol("标普500", None, "^GSPC"),
    "DJI": IndexSymbol("道琼斯指数", None, "^DJI"),
    "RUT": IndexSymbol("罗素2000", None, "^RUT"),
    "VIX": IndexSymbol("VIX", None, "^VIX"),
}


def eastmoney_secid(symbol: str, market: str) -> str | None:
    """Return Eastmoney secid for A-share/ETF/CB/index symbols where possible."""
    clean = symbol.strip().upper()
    if clean in COMMON_INDICES and COMMON_INDICES[clean].eastmoney_secid:
        return COMMON_INDICES[clean].eastmoney_secid
    if clean.endswith(".SH"):
        return f"1.{clean[:-3]}"
    if clean.endswith(".SZ"):
        return f"0.{clean[:-3]}"
    if clean.endswith(".BJ"):
        return f"0.{clean[:-3]}"
    if market == "指数":
        index = COMMON_INDICES.get(clean)
        return index.eastmoney_secid if index else None
    code = clean.split(".", 1)[0]
    if not code.isdigit():
        return None
    if code.startswith(("6", "5", "9")):
        return f"1.{code}"
    if code.startswith(("0", "1", "2", "3", "4", "8")):
        return f"0.{code}"
    return None


def yahoo_symbol(symbol: str, market: str) -> str:
    """Return Yahoo Finance symbol for US stocks and known indices."""
    clean = symbol.strip().upper()
    if clean in COMMON_INDICES and COMMON_INDICES[clean].yahoo_symbol:
        return COMMON_INDICES[clean].yahoo_symbol or clean
    aliases = {"NASDAQ": "^IXIC", "SP500": "^GSPC", "S&P500": "^GSPC", "DOW": "^DJI"}
    return aliases.get(clean, clean)
