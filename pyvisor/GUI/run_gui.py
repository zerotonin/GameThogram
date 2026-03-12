from pathlib import Path
import shutil

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from pyvisor.GUI.main_gui import MovScoreGUI
from pyvisor.paths import ensure_tmp_icon_dir, ensure_user_data_dir
from pyvisor.resources import resource_path


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
    app.setWindowIcon(QIcon(str(resource_path('gamethogram_48.png'))))

    # ── Global dark theme ────────────────────────────────────────
    app.setStyleSheet("""
        QWidget {
            background-color: #3c3f41;
            color: #d4d4d4;
            font-size: 12px;
        }
        QTabWidget::pane { border: 1px solid #555; }
        QTabBar::tab {
            background: #484b4d; color: #ccc;
            padding: 6px 14px; margin-right: 2px;
            border: 1px solid #555; border-bottom: none;
            border-top-left-radius: 4px; border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background: #3c3f41; color: #fff; font-weight: bold;
        }
        QPushButton {
            background: #505356; color: #e0e0e0;
            border: 1px solid #666; border-radius: 3px;
            padding: 4px 10px;
        }
        QPushButton:hover { background: #5a5d60; }
        QPushButton:pressed { background: #656870; }
        QComboBox {
            background: #505356; color: #e0e0e0;
            border: 1px solid #666; border-radius: 3px;
            padding: 3px 8px;
        }
        QComboBox QAbstractItemView {
            background: #484b4d; color: #e0e0e0;
            selection-background-color: #5a5d60;
        }
        QLabel { background: transparent; }
        QLineEdit {
            background: #484b4d; color: #e0e0e0;
            border: 1px solid #666; border-radius: 2px;
            padding: 2px 4px;
        }
        QCheckBox { background: transparent; spacing: 6px; color: #d4d4d4; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 2px solid #888; border-radius: 3px;
            background: #555;
        }
        QCheckBox::indicator:unchecked:hover {
            border-color: #aaa;
            background: #606060;
        }
        QCheckBox::indicator:checked {
            background: #5a9bd5;
            border-color: #4a8bc5;
        }
        QCheckBox::indicator:checked:hover {
            background: #6aabee;
            border-color: #5a9bd5;
        }
        QSpinBox {
            background: #484b4d; color: #e0e0e0;
            border: 1px solid #666;
        }
        QGroupBox {
            border: 1px solid #666; border-radius: 4px;
            margin-top: 8px; padding-top: 14px;
            color: #ccc; font-weight: bold;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        QScrollArea { border: none; background: transparent; }
        QFrame { border-color: #666; }
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
