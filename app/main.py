from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.ai.trainer import LocalAITrainer
from app.broker.paper import PaperBroker
from app.providers.market import SimulatedMarketDataProvider
from app.providers.news import NewsProvider
from app.schemas import Order, OrderRequest, Prediction, StrategyPick, StrategyRequest, TrainRequest, TrainResult
from app.strategies.engine import StrategyEngine

app = FastAPI(title="炒股辅助软件原型", version="0.1.0")
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

market_provider = SimulatedMarketDataProvider()
news_provider = NewsProvider()
strategy_engine = StrategyEngine(market_provider)
ai_trainer = LocalAITrainer()
paper_broker = PaperBroker(market_provider)


@app.get("/")
async def dashboard() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/quotes/{symbol}")
async def quote(symbol: str):
    return await market_provider.get_quote(symbol)


@app.get("/api/indicators/{symbol}")
async def indicators(symbol: str, points: int = Query(default=120, ge=20, le=240)):
    return await market_provider.get_history(symbol, points)


@app.get("/api/news")
async def news(symbol: str | None = None, limit: int = Query(default=10, ge=1, le=50)):
    return await news_provider.get_news(symbol, limit)


@app.post("/api/strategies/run", response_model=list[StrategyPick])
async def run_strategy(request: StrategyRequest):
    return await strategy_engine.run(request)


@app.post("/api/ai/train", response_model=TrainResult)
async def train(request: TrainRequest):
    return ai_trainer.train(request)


@app.post("/api/ai/predict/{symbol}", response_model=Prediction)
async def predict(symbol: str, prices: list[float]):
    return ai_trainer.predict(symbol, prices)


@app.post("/api/broker/orders", response_model=Order)
async def submit_order(request: OrderRequest):
    return await paper_broker.submit_order(request)


@app.get("/api/broker/orders", response_model=list[Order])
async def list_orders():
    return paper_broker.list_orders()


@app.websocket("/ws/quotes/{symbols}")
async def quote_stream(websocket: WebSocket, symbols: str):
    await websocket.accept()
    watchlist = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    if not watchlist:
        watchlist = ["AAPL"]
    try:
        while True:
            quotes = [await market_provider.get_quote(symbol) for symbol in watchlist]
            await websocket.send_json([quote.model_dump(mode="json") for quote in quotes])
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return
