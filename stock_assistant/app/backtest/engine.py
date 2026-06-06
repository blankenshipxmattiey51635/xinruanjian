"""Backtest extension point.

The first stage only provides the interface placeholder. Later stages must feed
this engine with real historical行情 data; no synthetic prices are allowed.
"""
from __future__ import annotations


class BacktestEngine:
    def run(self) -> None:
        raise NotImplementedError("第六阶段实现：需要真实历史行情数据后才能回测。")
