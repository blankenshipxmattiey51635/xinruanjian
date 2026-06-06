from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_quote_endpoint() -> None:
    response = client.get("/api/quotes/aapl")
    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert payload["price"] > 0
    assert payload["ask"] > payload["bid"]


def test_strategy_endpoint() -> None:
    response = client.post(
        "/api/strategies/run",
        json={
            "universe": ["AAPL", "MSFT"],
            "rule": {"min_price": 1, "max_price": 1000, "min_volume": 1, "min_momentum_percent": -100},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert all("reasons" in pick for pick in payload)


def test_ai_train_and_predict() -> None:
    prices = [100, 101, 102, 101, 103, 104, 105, 106, 107, 108]
    train_response = client.post("/api/ai/train", json={"symbol": "AAPL", "prices": prices})
    assert train_response.status_code == 200
    assert train_response.json()["symbol"] == "AAPL"

    predict_response = client.post("/api/ai/predict/AAPL", json=prices)
    assert predict_response.status_code == 200
    assert predict_response.json()["signal"] in {"buy", "hold", "sell"}


def test_paper_order() -> None:
    response = client.post(
        "/api/broker/orders",
        json={"symbol": "AAPL", "side": "buy", "quantity": 1, "order_type": "market"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "filled"
    assert payload["filled_price"] > 0
