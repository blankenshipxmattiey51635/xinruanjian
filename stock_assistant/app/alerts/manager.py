"""Alert extension point for price, volume, signal and news reminders."""
from __future__ import annotations


class AlertManager:
    def notify(self, title: str, message: str) -> str:
        return f"{title}: {message}"
