"""JSON settings management with safe defaults for phase one."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.utils.paths import ensure_runtime_dirs


@dataclass(slots=True)
class AppSettings:
    """User-editable application settings."""

    first_run: bool = True
    theme: str = "dark"
    enabled_markets: list[str] = field(default_factory=lambda: ["A股", "美股", "指数"])
    quote_refresh_seconds: int = 5
    market_scan_minutes: int = 5
    data_retention_days: int = 0
    data_path: str = "data"
    alert_popup: bool = True
    alert_sound: bool = False
    alert_system_notification: bool = True
    autostart: bool = False
    mini_window: bool = False
    default_ai_provider: str = "未配置"
    default_ai_model: str = ""

    def normalize(self) -> None:
        self.quote_refresh_seconds = max(5, int(self.quote_refresh_seconds))
        self.market_scan_minutes = max(1, int(self.market_scan_minutes))
        if self.theme not in {"dark", "light"}:
            self.theme = "dark"


class SettingsStore:
    """Load and save settings as UTF-8 JSON."""

    def __init__(self, path: Path | None = None) -> None:
        dirs = ensure_runtime_dirs()
        self.path = path or dirs["config"] / "settings.json"

    def load(self) -> AppSettings:
        if not self.path.exists():
            settings = AppSettings()
            self.save(settings)
            return settings
        data = json.loads(self.path.read_text(encoding="utf-8"))
        settings = AppSettings(**self._merge_defaults(data))
        settings.normalize()
        return settings

    def save(self, settings: AppSettings) -> None:
        settings.normalize()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _merge_defaults(data: dict[str, Any]) -> dict[str, Any]:
        defaults = asdict(AppSettings())
        defaults.update(data)
        return defaults
