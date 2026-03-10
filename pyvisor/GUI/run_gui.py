from pathlib import Path
import shutil

from PyQt5.QtWidgets import QApplication

from pyvisor.GUI.main_gui import MovScoreGUI
from pyvisor.paths import ensure_tmp_icon_dir, ensure_user_data_dir


def reset_directory(directory: Path) -> None:
    """Remove all contents from *directory* while keeping it available."""
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


def main():
    import sys

    ensure_user_data_dir()
    tmp_icon_dir = ensure_tmp_icon_dir()
    reset_directory(tmp_icon_dir)

    app = QApplication(sys.argv)

    # ── Global dark theme ────────────────────────────────────────
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2d30;
            color: #d4d4d4;
            font-size: 12px;
        }
        QTabWidget::pane { border: 1px solid #444; }
        QTabBar::tab {
            background: #353739; color: #ccc;
            padding: 6px 14px; margin-right: 2px;
            border: 1px solid #444; border-bottom: none;
            border-top-left-radius: 4px; border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background: #2b2d30; color: #fff; font-weight: bold;
        }
        QPushButton {
            background: #404347; color: #e0e0e0;
            border: 1px solid #555; border-radius: 3px;
            padding: 4px 10px;
        }
        QPushButton:hover { background: #505357; }
        QPushButton:pressed { background: #606367; }
        QComboBox {
            background: #404347; color: #e0e0e0;
            border: 1px solid #555; border-radius: 3px;
            padding: 3px 8px;
        }
        QComboBox QAbstractItemView {
            background: #353739; color: #e0e0e0;
            selection-background-color: #505357;
        }
        QLabel { background: transparent; }
        QLineEdit {
            background: #353739; color: #e0e0e0;
            border: 1px solid #555; border-radius: 2px;
            padding: 2px 4px;
        }
        QCheckBox { background: transparent; }
        QSpinBox {
            background: #353739; color: #e0e0e0;
            border: 1px solid #555;
        }
        QGroupBox {
            border: 1px solid #555; border-radius: 4px;
            margin-top: 8px; padding-top: 14px;
            color: #ccc; font-weight: bold;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        QScrollArea { border: none; background: transparent; }
        QFrame { border-color: #555; }
    """)

    def _cleanup_tmp_icons() -> None:
        reset_directory(tmp_icon_dir)

    app.aboutToQuit.connect(_cleanup_tmp_icons)

    gui = MovScoreGUI()
    gui.show()

    code = app.exec_()
    _cleanup_tmp_icons()
    sys.exit(code)


if __name__ == "__main__":
    main()
