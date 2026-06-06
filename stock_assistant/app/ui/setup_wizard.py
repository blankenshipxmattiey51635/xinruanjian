"""First-run setup wizard for non-technical users."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.config.settings import AppSettings
from app.services.risk import RISK_DISCLOSURE


class SetupWizard(QDialog):
    """Collect essential first-run settings without requiring code edits."""

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.setWindowTitle("首次启动设置向导")
        self.settings = settings
        self.market_a = QCheckBox("A股")
        self.market_us = QCheckBox("美股")
        self.market_index = QCheckBox("指数")
        for box in (self.market_a, self.market_us, self.market_index):
            box.setChecked(box.text() in settings.enabled_markets)
        self.refresh_seconds = QSpinBox()
        self.refresh_seconds.setRange(5, 3600)
        self.refresh_seconds.setValue(settings.quote_refresh_seconds)
        self.scan_minutes = QSpinBox()
        self.scan_minutes.setRange(1, 1440)
        self.scan_minutes.setValue(settings.market_scan_minutes)
        self.ai_provider = QComboBox()
        self.ai_provider.addItems(["未配置", "OpenAI", "Gemini", "Claude", "DeepSeek", "通义千问", "Kimi", "智谱", "百度千帆", "Ollama"])
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.data_path = QLineEdit(settings.data_path)
        self.popup_alert = QCheckBox("弹窗提醒")
        self.popup_alert.setChecked(settings.alert_popup)
        self.sound_alert = QCheckBox("声音提醒")
        self.sound_alert.setChecked(settings.alert_sound)
        self.autostart = QCheckBox("开机自启动（后续阶段实现写入系统设置）")
        self.autostart.setChecked(settings.autostart)
        self.mini_window = QCheckBox("启用小窗口模式（后续阶段完善）")
        self.mini_window.setChecked(settings.mini_window)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        risk = QLabel(RISK_DISCLOSURE)
        risk.setWordWrap(True)
        layout.addWidget(risk)
        form = QFormLayout()
        markets = QHBoxLayout()
        markets.addWidget(self.market_a)
        markets.addWidget(self.market_us)
        markets.addWidget(self.market_index)
        form.addRow("选择市场", markets)
        form.addRow("自选股刷新频率（秒，最低5秒）", self.refresh_seconds)
        form.addRow("全市场扫描周期（分钟）", self.scan_minutes)
        form.addRow("AI 模型供应商", self.ai_provider)
        form.addRow("API Key（可暂不填写，本地加密保存预留）", self.api_key)
        form.addRow("数据保存路径", self.data_path)
        alerts = QHBoxLayout()
        alerts.addWidget(self.popup_alert)
        alerts.addWidget(self.sound_alert)
        form.addRow("提醒方式", alerts)
        form.addRow("启动选项", self.autostart)
        form.addRow("小窗口", self.mini_window)
        layout.addLayout(form)
        buttons = QHBoxLayout()
        save = QPushButton("保存并进入软件")
        cancel = QPushButton("取消")
        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def apply_to_settings(self) -> AppSettings:
        markets = []
        if self.market_a.isChecked():
            markets.append("A股")
        if self.market_us.isChecked():
            markets.append("美股")
        if self.market_index.isChecked():
            markets.append("指数")
        self.settings.enabled_markets = markets or ["A股"]
        self.settings.quote_refresh_seconds = self.refresh_seconds.value()
        self.settings.market_scan_minutes = self.scan_minutes.value()
        self.settings.default_ai_provider = self.ai_provider.currentText()
        self.settings.data_path = self.data_path.text().strip() or "data"
        self.settings.alert_popup = self.popup_alert.isChecked()
        self.settings.alert_sound = self.sound_alert.isChecked()
        self.settings.autostart = self.autostart.isChecked()
        self.settings.mini_window = self.mini_window.isChecked()
        self.settings.first_run = False
        self.settings.normalize()
        return self.settings
