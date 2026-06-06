from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config.settings import AppSettings, SettingsStore
from app.database.db import Database
from app.services.watchlist_service import WatchlistService


def test_settings_normalize(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    settings = AppSettings(quote_refresh_seconds=1, market_scan_minutes=0, theme="bad")
    store.save(settings)
    loaded = store.load()
    assert loaded.quote_refresh_seconds == 5
    assert loaded.market_scan_minutes == 1
    assert loaded.theme == "dark"


def test_watchlist_add_update_remove(tmp_path):
    db = Database(tmp_path / "test.sqlite3")
    db.initialize()
    service = WatchlistService(db)
    service.add("aapl", "Apple", "美股")
    service.add("AAPL", "Apple Inc.", "美股")
    items = service.list_all()
    assert len(items) == 1
    assert items[0].symbol == "AAPL"
    assert items[0].name == "Apple Inc."
    service.remove("AAPL", "美股")
    assert service.list_all() == []
    db.close()
