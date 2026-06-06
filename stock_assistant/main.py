"""Application entry point."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app.config.settings import SettingsStore
from app.database.db import Database
from app.services.risk import RISK_DISCLOSURE
from app.ui.main_window import MainWindow
from app.utils.paths import ensure_runtime_dirs


def main() -> int:
    ensure_runtime_dirs()
    db = Database()
    db.initialize()
    settings_store = SettingsStore()
    settings = settings_store.load()
    app = QApplication(sys.argv)
    QMessageBox.information(None, "风险提示", RISK_DISCLOSURE)
    window = MainWindow(db, settings_store, settings)
    window.show()
    exit_code = app.exec()
    db.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
