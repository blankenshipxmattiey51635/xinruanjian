from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.schemas import Prediction, TrainRequest, TrainResult


@dataclass
class TinyTrendModel:
    symbol: str
    version: str
    threshold: float
    accuracy_estimate: float


class LocalAITrainer:
    """Small trainable baseline model; replace with a feature store + ML stack in production."""

    def __init__(self, model_dir: Path = Path("data/models")) -> None:
        self._model_dir = model_dir
        self._model_dir.mkdir(parents=True, exist_ok=True)

    def train(self, request: TrainRequest) -> TrainResult:
        returns = [
            (request.prices[index] - request.prices[index - 1]) / request.prices[index - 1]
            for index in range(1, len(request.prices))
            if request.prices[index - 1] > 0
        ]
        threshold = sum(returns) / len(returns)
        correct = sum(1 for value in returns if (value >= threshold) == (returns[-1] >= threshold))
        accuracy = correct / len(returns)
        model = TinyTrendModel(
            symbol=request.symbol.upper(),
            version="tiny-trend-v1",
            threshold=threshold,
            accuracy_estimate=accuracy,
        )
        self._path(model.symbol).write_text(json.dumps(asdict(model), indent=2), encoding="utf-8")
        return TrainResult(
            symbol=model.symbol,
            model_version=model.version,
            samples=len(request.prices),
            threshold=round(model.threshold, 6),
            accuracy_estimate=round(model.accuracy_estimate, 4),
        )

    def predict(self, symbol: str, prices: list[float]) -> Prediction:
        model = self._load(symbol.upper())
        if len(prices) < 2 or prices[-2] <= 0:
            return Prediction(
                symbol=symbol.upper(),
                model_version=model.version,
                signal="hold",
                confidence=0.5,
                explanation="样本不足，保持观望。",
            )
        latest_return = (prices[-1] - prices[-2]) / prices[-2]
        gap = latest_return - model.threshold
        signal = "buy" if gap > 0.003 else "sell" if gap < -0.003 else "hold"
        confidence = min(0.95, 0.5 + abs(gap) * 20 + model.accuracy_estimate / 4)
        return Prediction(
            symbol=symbol.upper(),
            model_version=model.version,
            signal=signal,
            confidence=round(confidence, 3),
            explanation=f"最新收益率 {latest_return:.4%} 与训练阈值 {model.threshold:.4%} 比较后生成信号。",
        )

    def _load(self, symbol: str) -> TinyTrendModel:
        path = self._path(symbol)
        if not path.exists():
            return TinyTrendModel(symbol=symbol, version="tiny-trend-v1", threshold=0, accuracy_estimate=0.5)
        return TinyTrendModel(**json.loads(path.read_text(encoding="utf-8")))

    def _path(self, symbol: str) -> Path:
        return self._model_dir / f"{symbol}.json"
