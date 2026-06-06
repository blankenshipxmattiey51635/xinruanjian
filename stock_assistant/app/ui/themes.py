"""Qt stylesheet snippets for dark and light trading layouts."""

DARK_STYLE = """
QMainWindow, QDialog, QWidget { background: #101418; color: #d7dde5; font-family: Microsoft YaHei, Segoe UI; }
QTableWidget, QListWidget, QTextEdit { background: #151b22; color: #e7edf5; gridline-color: #28313d; border: 1px solid #2b3440; }
QHeaderView::section { background: #202936; color: #f5c542; padding: 5px; border: 1px solid #2b3440; }
QPushButton { background: #263447; color: #ffffff; border: 1px solid #3c4b61; padding: 6px 10px; border-radius: 3px; }
QPushButton:hover { background: #33506f; }
QLineEdit, QComboBox, QSpinBox { background: #17202a; color: #ffffff; border: 1px solid #34465d; padding: 5px; }
QTabWidget::pane { border: 1px solid #2b3440; }
QTabBar::tab { background: #1b2430; color: #c9d1d9; padding: 7px 14px; }
QTabBar::tab:selected { color: #f5c542; background: #263447; }
"""

LIGHT_STYLE = """
QMainWindow, QDialog, QWidget { background: #f7f9fb; color: #1f2933; font-family: Microsoft YaHei, Segoe UI; }
QTableWidget, QListWidget, QTextEdit { background: #ffffff; color: #1f2933; gridline-color: #d8dee6; border: 1px solid #c9d2dc; }
QHeaderView::section { background: #e9eef5; color: #9a3412; padding: 5px; border: 1px solid #c9d2dc; }
QPushButton { background: #e4ebf4; color: #1f2933; border: 1px solid #b8c4d2; padding: 6px 10px; border-radius: 3px; }
QPushButton:hover { background: #d0ddea; }
QLineEdit, QComboBox, QSpinBox { background: #ffffff; color: #1f2933; border: 1px solid #b8c4d2; padding: 5px; }
"""
