"""Main trading-assistant desktop window for phase one."""
from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import AppSettings, SettingsStore
from app.database.db import Database
from app.services.quote_service import QuoteService
from app.services.market_scan_service import MarketScanService
from app.services.risk import RISK_DISCLOSURE, SIMULATION_LABEL
from app.services.watchlist_service import WatchlistService
from app.ui.setup_wizard import SetupWizard
from app.ui.themes import DARK_STYLE, LIGHT_STYLE


class MainWindow(QMainWindow):
    """Professional dark desktop shell with honest data-source status labels."""

    def __init__(self, db: Database, settings_store: SettingsStore, settings: AppSettings) -> None:
        super().__init__()
        self.db = db
        self.settings_store = settings_store
        self.settings = settings
        self.watchlist = WatchlistService(db)
        self.quotes = QuoteService(db)
        self.market_scanner = MarketScanService(self.quotes)
        self.setWindowTitle("个人炒股辅助软件 - 第二阶段（真实行情）")
        self.resize(1500, 900)
        self.setStyleSheet(DARK_STYLE if settings.theme == "dark" else LIGHT_STYLE)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._build_ui()
        self._build_refresh_timer()
        self.reload_watchlist()
        if self.settings.first_run:
            QTimer.singleShot(200, self.show_setup_wizard)

    def _build_ui(self) -> None:
        root = QSplitter(Qt.Horizontal)
        root.addWidget(self._build_left_panel())
        root.addWidget(self._build_center_panel())
        root.addWidget(self._build_right_panel())
        root.setSizes([330, 850, 360])
        bottom_tabs = self._build_bottom_tabs()
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self._risk_banner())
        layout.addWidget(root, stretch=7)
        layout.addWidget(bottom_tabs, stretch=2)
        self.setCentralWidget(container)

    def _risk_banner(self) -> QLabel:
        banner = QLabel(RISK_DISCLOSURE)
        banner.setWordWrap(True)
        banner.setStyleSheet("color: #ffcc66; font-weight: bold; padding: 6px; border: 1px solid #665200;")
        return banner

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form_box = QGroupBox("自选股管理")
        form = QFormLayout(form_box)
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("例如 600519 / AAPL / 000001.SH")
        self.name_input = QLineEdit()
        self.market_input = QComboBox()
        self.market_input.addItems(["A股", "美股", "指数", "ETF", "可转债"])
        self.asset_input = QComboBox()
        self.asset_input.addItems(["股票", "ETF", "指数", "可转债"])
        add_button = QPushButton("添加/更新自选")
        remove_button = QPushButton("删除选中")
        add_button.clicked.connect(self.add_watch_item)
        remove_button.clicked.connect(self.remove_selected_watch_item)
        form.addRow("代码", self.symbol_input)
        form.addRow("名称", self.name_input)
        form.addRow("市场", self.market_input)
        form.addRow("类型", self.asset_input)
        form.addRow(add_button, remove_button)
        layout.addWidget(form_box)
        self.watch_table = QTableWidget(0, 21)
        self.watch_table.setHorizontalHeaderLabels([
            "代码", "名称", "市场", "当前价", "涨跌额", "涨跌幅%", "开盘", "昨收",
            "最高", "最低", "成交量", "成交额", "买一", "卖一", "换手率%",
            "市盈率", "市净率", "总市值", "流通市值", "数据源", "数据状态",
        ])
        self.watch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.watch_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.watch_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.watch_table, stretch=1)
        return panel

    def _build_center_panel(self) -> QWidget:
        tabs = QTabWidget()
        tabs.addTab(self._placeholder_chart("分时图", "第二阶段已接入真实报价刷新；分时/K线绘图将在第三阶段基于真实历史行情实现。"), "分时")
        tabs.addTab(self._placeholder_chart("K线图 + 成交量 + 技术指标", "第三阶段实现 MA/MACD/KDJ/RSI/BOLL 和 B/S 点。"), "K线")
        tabs.addTab(self._placeholder_chart("多股票对比图", "第三阶段接入真实历史行情后支持缩放、拖动、十字光标和导出图片。"), "对比")
        return tabs

    def _placeholder_chart(self, title: str, body: str) -> QWidget:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; color: #f5c542;")
        body_label = QLabel(body)
        body_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(body_label)
        layout.addStretch(1)
        return frame

    def _build_right_panel(self) -> QWidget:
        tabs = QTabWidget()
        self.news_text = QTextEdit()
        self.news_text.setReadOnly(True)
        self.news_text.setText("暂无真实数据：新闻/公告/研报标题抓取将在第四阶段接入真实数据源；当前不会伪造新闻。")
        tabs.addTab(self.news_text, "新闻/公告")
        self.ai_text = QTextEdit()
        self.ai_text.setReadOnly(True)
        self.ai_text.setText("AI 未配置。AI 建议必须显示风险提示，且第一版不得自动真实下单。")
        tabs.addTab(self.ai_text, "AI分析")
        info = QTextEdit()
        info.setReadOnly(True)
        info.setText("个股资料将在真实数据源可用后显示；接口不可用时必须显示“数据源不可用”。")
        tabs.addTab(info, "个股资料")
        return tabs

    def _build_bottom_tabs(self) -> QTabWidget:
        tabs = QTabWidget()
        self.signal_table = QTableWidget(0, 6)
        self.signal_table.setHorizontalHeaderLabels(["股票", "策略", "B/S", "理由", "风险", "时间"])
        self.selection_table = QTableWidget(0, 8)
        self.selection_table.setHorizontalHeaderLabels(["代码", "名称", "策略", "AI评分", "技术强度", "新闻相关度", "风险", "更新时间"])
        self.holding_table = QTableWidget(0, 7)
        self.holding_table.setHorizontalHeaderLabels(["模拟标记", "代码", "数量", "成本", "现价", "盈亏", "收益率"])
        self.backtest_text = QTextEdit()
        self.backtest_text.setReadOnly(True)
        self.backtest_text.setText("回测模块将在第六阶段实现，所有报告基于真实历史行情。")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setText(SIMULATION_LABEL)
        tabs.addTab(self.signal_table, "策略信号")
        tabs.addTab(self.selection_table, "选股结果")
        tabs.addTab(self.holding_table, "模拟持仓")
        tabs.addTab(self.backtest_text, "回测结果")
        tabs.addTab(self.log_text, "日志提示")
        return tabs

    def _build_refresh_timer(self) -> None:
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_quotes)
        self.refresh_timer.start(self.settings.quote_refresh_seconds * 1000)
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.scan_common_indices)
        self.scan_timer.start(self.settings.market_scan_minutes * 60 * 1000)

    def show_setup_wizard(self) -> None:
        wizard = SetupWizard(self.settings)
        if wizard.exec() == SetupWizard.Accepted:
            self.settings = wizard.apply_to_settings()
            self.settings_store.save(self.settings)
            self.refresh_timer.setInterval(self.settings.quote_refresh_seconds * 1000)
            self.scan_timer.setInterval(self.settings.market_scan_minutes * 60 * 1000)
            self.status.showMessage("设置已保存，将按真实行情源可用性刷新和扫描。", 8000)

    def add_watch_item(self) -> None:
        try:
            self.watchlist.add(
                self.symbol_input.text(),
                self.name_input.text(),
                self.market_input.currentText(),
                self.asset_input.currentText(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "无法添加", str(exc))
            return
        self.symbol_input.clear()
        self.name_input.clear()
        self.reload_watchlist()

    def remove_selected_watch_item(self) -> None:
        row = self.watch_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "请选择", "请先在自选股表格中选择一行。")
            return
        symbol = self.watch_table.item(row, 0).text()
        market = self.watch_table.item(row, 2).text()
        self.watchlist.remove(symbol, market)
        self.reload_watchlist()

    def reload_watchlist(self) -> None:
        items = self.watchlist.list_all()
        self.watch_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [item.symbol, item.name, item.market] + ["--"] * 16 + ["未刷新", "暂无真实数据"]
            for col, value in enumerate(values):
                self.watch_table.setItem(row, col, QTableWidgetItem(value))
        self.refresh_quotes()

    def refresh_quotes(self) -> None:
        items = self.watchlist.list_all()
        for row, item in enumerate(items):
            result = self.quotes.quote_for(item)
            if result.ok and isinstance(result.data, dict):
                data = result.data
                if data.get("name") and not self.watch_table.item(row, 1).text():
                    self.watch_table.setItem(row, 1, QTableWidgetItem(str(data.get("name"))))
                fields = [
                    data.get("price"), data.get("change_amount"), data.get("change_percent"),
                    data.get("open_price"), data.get("previous_close"), data.get("high_price"),
                    data.get("low_price"), data.get("volume"), data.get("turnover"), data.get("bid1"),
                    data.get("ask1"), data.get("turnover_rate"), data.get("pe_ratio"), data.get("pb_ratio"),
                    data.get("total_market_value"), data.get("float_market_value"), data.get("source"), "已获取真实行情",
                ]
                for offset, value in enumerate(fields, start=3):
                    self.watch_table.setItem(row, offset, QTableWidgetItem(self._fmt(value)))
            else:
                for col in range(3, 19):
                    self.watch_table.setItem(row, col, QTableWidgetItem("--"))
                self.watch_table.setItem(row, 19, QTableWidgetItem(result.source))
                self.watch_table.setItem(row, 20, QTableWidgetItem(result.message or "数据源不可用"))
        self.status.showMessage(f"自选股刷新周期：{self.settings.quote_refresh_seconds} 秒；真实接口失败时不显示伪造行情。", 5000)

    @staticmethod
    def _fmt(value: object) -> str:
        if value is None or value == "":
            return "--"
        if isinstance(value, float):
            return f"{value:.4f}".rstrip("0").rstrip(".")
        return str(value)

    def scan_common_indices(self) -> None:
        indices = self.market_scanner.common_indices()
        ok, failed, messages = self.market_scanner.scan(indices)
        detail = "\n".join(messages) if messages else "全部扫描项已返回真实行情。"
        self.log_text.setText(
            f"全市场扫描周期：{self.settings.market_scan_minutes} 分钟\n"
            f"本阶段先扫描主要大盘指数作为真实接口健康检查。成功：{ok}，失败：{failed}。\n"
            f"{detail}"
        )
