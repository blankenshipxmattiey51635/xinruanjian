from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Quote(BaseModel):
    symbol: str
    price: float = Field(gt=0)
    change: float
    change_percent: float
    volume: int = Field(ge=0)
    bid: float = Field(gt=0)
    ask: float = Field(gt=0)
    latency_ms: int = Field(ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NewsItem(BaseModel):
    id: str
    symbol: str | None = None
    title: str
    source: str
    url: str
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IndicatorPoint(BaseModel):
    timestamp: datetime
    price: float
    ma5: float
    ma20: float
    rsi14: float


class StrategyRule(BaseModel):
    min_price: float = 1
    max_price: float = 1_000_000
    min_volume: int = 0
    min_momentum_percent: float = -100


class StrategyRequest(BaseModel):
    universe: list[str] = Field(default_factory=lambda: ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"])
    rule: StrategyRule = Field(default_factory=StrategyRule)


class StrategyPick(BaseModel):
    symbol: str
    score: float
    reasons: list[str]
    quote: Quote


class OrderSide(str, Enum):
    buy = "buy"
    sell = "sell"


class OrderType(str, Enum):
    market = "market"
    limit = "limit"


class OrderRequest(BaseModel):
    symbol: str
    side: OrderSide
    quantity: int = Field(gt=0)
    order_type: OrderType = OrderType.market
    limit_price: float | None = Field(default=None, gt=0)


class Order(BaseModel):
    id: str
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    status: Literal["accepted", "rejected", "filled"]
    submitted_at: datetime
    filled_price: float | None = None
    message: str = ""


class TrainRequest(BaseModel):
    symbol: str
    prices: list[float] = Field(min_length=10)


class TrainResult(BaseModel):
    symbol: str
    model_version: str
    samples: int
    threshold: float
    accuracy_estimate: float


class Prediction(BaseModel):
    symbol: str
    model_version: str
    signal: Literal["buy", "hold", "sell"]
    confidence: float
    explanation: str
