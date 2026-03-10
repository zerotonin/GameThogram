"""Results Overview tab — live analysis plots with export.

Displays behaviour percentages, bout durations and a transition‐probability
heatmap computed from the current scoring session.  Each plot can be exported
individually as CSV, PNG or SVG.
"""
from __future__ import annotations

import os
from typing import Optional

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QScrollArea, QSizePolicy, QGroupBox,
)

from .model.gui_data_interface import GUIDataInterface
from ..analysis.ethogram_analysis import (
    analyse_ethogram,
    stats_to_dataframe,
    transition_matrix_to_dataframe,
    AnalysisResult,
)

HERE = os.path.dirname(os.path.abspath(__file__))

# Matplotlib style defaults — keep text as text in SVG
matplotlib.rcParams["svg.fonttype"] = "none"

# Colour palette (colour‐blind friendly, based on Tol's muted scheme)
_PALETTE = [
    "#332288", "#88CCEE", "#44AA99", "#117733",
    "#999933", "#DDCC77", "#CC6677", "#882255",
    "#AA4499", "#661100", "#6699CC", "#AA4466",
]


def _pick_colours(n: int):
    return [_PALETTE[i % len(_PALETTE)] for i in range(n)]


class TabResults(QWidget):
    """Fourth tab of the pyVISOR main GUI — analysis & export."""

    def __init__(self, parent: QWidget, gui_data_interface: GUIDataInterface):
        super().__init__()
        self.parent = parent
        self.gui_data_interface = gui_data_interface
        self._result: Optional[AnalysisResult] = None
        self._cbar = None
        self._init_UI()

    # ──────────────────────────────────────────────────────────────
    #  UI construction
    # ──────────────────────────────────────────────────────────────
    def _init_UI(self):
        # main layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        # refresh button row
        btn_row = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh analysis from scorer")
        self.btn_refresh.setStyleSheet(
            "color: #fff; background: #336699; font-weight: bold; padding: 6px 16px;")
        self.btn_refresh.clicked.connect(self._on_refresh)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        outer.addLayout(btn_row)

        # scrollable area for the three plot groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent;")
        scroll_content = QWidget()
        self._plots_layout = QVBoxLayout(scroll_content)
        self._plots_layout.setSpacing(16)

        # percentage plot
        self._fig_pct, self._ax_pct, self._canvas_pct, grp_pct = \
            self._make_plot_group("Behaviour Percentages", height=280)
        self._plots_layout.addWidget(grp_pct)

        # bout duration plot
        self._fig_bout, self._ax_bout, self._canvas_bout, grp_bout = \
            self._make_plot_group("Mean Bout Duration", height=280)
        self._plots_layout.addWidget(grp_bout)

        # transition matrix
        self._fig_trans, self._ax_trans, self._canvas_trans, grp_trans = \
            self._make_plot_group("Transition Matrix", height=360)
        self._plots_layout.addWidget(grp_trans)

        self._plots_layout.addStretch()
        scroll.setWidget(scroll_content)
        outer.addWidget(scroll, stretch=1)

        # placeholder label
        self._placeholder = QLabel(
            "Press  \"Refresh analysis from scorer\"  after scoring a video "
            "to see results here.")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet(
            "color: #fff; background: rgba(0,0,0,120); padding: 24px; "
            "font-size: 14px;")
        self._plots_layout.insertWidget(0, self._placeholder)

    def _make_plot_group(self, title: str, height: int = 300):
        """Create a titled group box containing a matplotlib canvas + export buttons."""
        grp = QGroupBox(title)
        grp.setStyleSheet(
            "QGroupBox { color: #fff; font-weight: bold; font-size: 13px; "
            "border: 1px solid rgba(255,255,255,80); border-radius: 4px; "
            "margin-top: 8px; padding-top: 16px; background: rgba(0,0,0,100); }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        vbox = QVBoxLayout(grp)

        fig = Figure(figsize=(7, 3), dpi=100, facecolor="none")
        fig.patch.set_alpha(0.0)
        ax = fig.add_subplot(111)
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(height)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        canvas.setStyleSheet("background: transparent;")
        vbox.addWidget(canvas)

        # export buttons
        btn_row = QHBoxLayout()
        for fmt in ("CSV", "PNG", "SVG"):
            btn = QPushButton(f"Export {fmt}")
            btn.setStyleSheet(
                "color: #fff; background: #555; padding: 4px 10px;")
            btn.clicked.connect(
                lambda checked, t=title, f=fmt: self._export(t, f))
            btn_row.addWidget(btn)
        btn_row.addStretch()
        vbox.addLayout(btn_row)

        grp.setVisible(False)  # hidden until analysis runs
        return fig, ax, canvas, grp

    # ──────────────────────────────────────────────────────────────
    #  Analysis trigger
    # ──────────────────────────────────────────────────────────────
    def _on_refresh(self):
        scorer = self.gui_data_interface.manual_scorer
        if scorer is None:
            QMessageBox.warning(
                self, "No scorer running",
                "You need to run the scorer and annotate some video before "
                "analysis results can be shown.",
                QMessageBox.Ok)
            return

        data = scorer.get_data()
        if data is False or data is None or (hasattr(data, 'size') and data.size == 0):
            QMessageBox.warning(
                self, "No data yet",
                "The scorer has not recorded any annotation data yet. "
                "Please score at least part of a video first.",
                QMessageBox.Ok)
            return

        labels = scorer.get_labels()
        fps = 25.0
        if hasattr(scorer, 'movie') and scorer.movie is not None:
            fps = float(getattr(scorer.movie, '_movie_fps',
                                getattr(scorer.movie, 'fps', 25)))

        self._result = analyse_ethogram(data, labels, fps)
        self._draw_all()

    # ──────────────────────────────────────────────────────────────
    #  Drawing
    # ──────────────────────────────────────────────────────────────
    def _draw_all(self):
        if self._result is None:
            return
        self._placeholder.setVisible(False)
        self._draw_percentages()
        self._draw_bout_durations()
        self._draw_transition_matrix()

    def _draw_percentages(self):
        r = self._result
        ax = self._ax_pct
        ax.clear()

        stats = r.behaviour_stats
        labels = [s.label for s in stats]
        values = [s.percentage for s in stats]
        colours = _pick_colours(len(stats))
        short = [_short(l) for l in labels]

        y_pos = np.arange(len(stats))
        ax.barh(y_pos, values, color=colours, edgecolor="white", linewidth=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(short, fontsize=9, color="white")
        ax.set_xlabel("% of total frames", fontsize=10, color="white")
        ax.set_xlim(0, max(max(values) * 1.15, 1))
        ax.invert_yaxis()
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
            spine.set_alpha(0.4)
        ax.set_facecolor("none")

        # value annotations
        for i, v in enumerate(values):
            ax.text(v + 0.3, i, f"{v:.1f}%", va="center",
                    fontsize=8, color="white")

        self._fig_pct.tight_layout()
        self._canvas_pct.draw()
        self._canvas_pct.parentWidget().setVisible(True)

    def _draw_bout_durations(self):
        r = self._result
        ax = self._ax_bout
        ax.clear()

        stats = r.behaviour_stats
        labels = [_short(s.label) for s in stats]
        means = [s.bout_mean_s for s in stats]
        stds = [s.bout_std_s for s in stats]
        colours = _pick_colours(len(stats))

        x_pos = np.arange(len(stats))
        ax.bar(x_pos, means, yerr=stds, color=colours,
               edgecolor="white", linewidth=0.5, capsize=3,
               error_kw={"ecolor": "white", "elinewidth": 1})
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=9, color="white", rotation=30,
                           ha="right")
        ax.set_ylabel("Duration (s)", fontsize=10, color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
            spine.set_alpha(0.4)
        ax.set_facecolor("none")

        self._fig_bout.tight_layout()
        self._canvas_bout.draw()
        self._canvas_bout.parentWidget().setVisible(True)

    def _draw_transition_matrix(self):
        r = self._result
        ax = self._ax_trans
        ax.clear()

        mat = r.transition_matrix
        labels = r.transition_labels
        n = mat.shape[0]

        im = ax.imshow(mat, cmap="YlOrRd", aspect="auto",
                       vmin=0, vmax=max(mat.max(), 0.01))

        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(labels, fontsize=8, color="white", rotation=45, ha="right")
        ax.set_yticklabels(labels, fontsize=8, color="white")
        ax.set_xlabel("To", fontsize=10, color="white")
        ax.set_ylabel("From", fontsize=10, color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
            spine.set_alpha(0.4)
        ax.set_facecolor("none")

        # annotate cells
        thresh = mat.max() / 2.0
        for i in range(n):
            for j in range(n):
                val = mat[i, j]
                color = "white" if val < thresh else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=7, color=color)

        # colour bar
        if hasattr(self, '_cbar') and self._cbar is not None:
            self._cbar.remove()
        self._cbar = self._fig_trans.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        self._cbar.ax.tick_params(colors="white", labelsize=8)
        self._cbar.outline.set_edgecolor("white")
        self._cbar.outline.set_alpha(0.4)

        self._fig_trans.tight_layout()
        self._canvas_trans.draw()
        self._canvas_trans.parentWidget().setVisible(True)

    # ──────────────────────────────────────────────────────────────
    #  Export
    # ──────────────────────────────────────────────────────────────
    def _export(self, plot_title: str, fmt: str):
        if self._result is None:
            QMessageBox.warning(self, "No data",
                                "Run the analysis first.", QMessageBox.Ok)
            return

        # choose file
        ext_map = {"CSV": "*.csv", "PNG": "*.png", "SVG": "*.svg"}
        filt = ext_map.get(fmt, "*.*")
        path, _ = QFileDialog.getSaveFileName(
            self, f"Export {plot_title} as {fmt}", "", filt)
        if not path:
            return

        try:
            if fmt == "CSV":
                self._export_csv(plot_title, path)
            elif fmt in ("PNG", "SVG"):
                self._export_figure(plot_title, path, fmt.lower())
            QMessageBox.information(
                self, "Export complete",
                f"Saved to:\n{path}", QMessageBox.Ok)
        except Exception as exc:
            QMessageBox.critical(
                self, "Export failed",
                f"Could not export:\n{exc}", QMessageBox.Ok)

    def _export_csv(self, plot_title: str, path: str):
        if "Percentage" in plot_title:
            df = stats_to_dataframe(self._result)
            df.to_csv(path, index=False)
        elif "Bout" in plot_title:
            df = stats_to_dataframe(self._result)
            df.to_csv(path, index=False)
        elif "Transition" in plot_title:
            df = transition_matrix_to_dataframe(self._result)
            df.to_csv(path)
        else:
            df = stats_to_dataframe(self._result)
            df.to_csv(path, index=False)

    def _export_figure(self, plot_title: str, path: str, fmt: str):
        fig = self._get_fig_for_title(plot_title)
        # For export, create a clean copy with white text on transparent bg
        fig.savefig(path, format=fmt, dpi=200, transparent=False,
                    facecolor="#2b2b2b", edgecolor="none",
                    bbox_inches="tight")

    def _get_fig_for_title(self, title: str) -> Figure:
        if "Percentage" in title:
            return self._fig_pct
        elif "Bout" in title:
            return self._fig_bout
        elif "Transition" in title:
            return self._fig_trans
        return self._fig_pct

    # ──────────────────────────────────────────────────────────────
    #  Qt overrides
    # ──────────────────────────────────────────────────────────────
    def resizeEvent(self, event):
        pass


def _short(label: str) -> str:
    """'animal_0 : aggression' → 'A0: aggression'"""
    if " : " in label:
        parts = label.split(" : ", 1)
        animal = parts[0].strip()
        behav = parts[1].strip()
        # try to abbreviate 'animal_0' → 'A0'
        for prefix in ("animal_", "Animal_", "animal ", "Animal "):
            if animal.startswith(prefix):
                animal = "A" + animal[len(prefix):]
                break
        return f"{animal}: {behav}"
    return label
