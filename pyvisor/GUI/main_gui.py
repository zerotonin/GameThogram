"""
@author Ilyas Kuhlemann
@mail ilyasp.ku@gmail.com
@date 15.06.16
"""
import json
import os
import pickle

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QMessageBox,
                             QApplication, QHBoxLayout, QLabel, QPushButton,
                             QFileDialog)

from pyvisor.GUI.model.movie_bindings import MovieBindings
from .model.animal import Animal
from .model.gui_data_interface import GUIDataInterface
from .tab_analysis import TabAnalysis
from .tab_behaviours.tab_behaviours import TabBehaviours
from pyvisor.GUI.tab_buttons.tab_buttons import TabButtons
from .tab_results import TabResults
from pyvisor.resources import resource_path
from pyvisor.paths import ensure_autosave_dir, ensure_user_data_dir, settings_path

HERE = os.path.dirname(os.path.abspath(__file__))


class MovScoreGUI(QWidget):

    def __init__(self):
        """
        """    
        super(MovScoreGUI, self).__init__()
        self.gui_data_interface = GUIDataInterface()
        self._load_defaults()

        self.initUI()

    def _load_defaults(self):
        self._load_state()
        self._load_display_values()

    def _load_display_values(self):
        settings_file = settings_path('guidefaults_movscoregui.pkl')
        try:
            with settings_file.open('rb') as f:
                self.values = pickle.load(f)
        except FileNotFoundError:
            try:
                with open(HERE + "/guidefaults_movscoregui.pkl", 'rb') as f:
                    self.values = pickle.load(f)
            except FileNotFoundError:
                self.values = dict()
                self.values['display'] = dict()
                self.values['display']['geometry'] = QRect(0, 0, 640, 480)

    def _load_state(self):
        state_file = settings_path('guidefaults_animals.json')
        try:
            with state_file.open('r') as f:
                state = json.load(f)
        except FileNotFoundError:
            with open(HERE + "/guidefaults_animals.json", 'r') as f:
                state = json.load(f)

        for a in state["animals"]:
            ani = Animal.from_json_dict(a)
            self.gui_data_interface.animals[ani.number] = ani
        self.gui_data_interface.selected_device = state["selected_device"]
        if "movie_bindings" in state:
            self.gui_data_interface.movie_bindings = MovieBindings.from_dict(
                state["movie_bindings"]
            )
        autosave_state = state.get("autosave", {})
        if autosave_state.get("directory") in (None, ""):
            autosave_state["directory"] = str(ensure_autosave_dir())
        self.gui_data_interface.autosave_settings.update({
            "enabled": autosave_state.get("enabled", self.gui_data_interface.autosave_settings["enabled"]),
            "interval_seconds": autosave_state.get("interval_seconds", self.gui_data_interface.autosave_settings["interval_seconds"]),
            "directory": autosave_state.get("directory", self.gui_data_interface.autosave_settings["directory"])
        })

    def initUI(self):
        """
        """        
        self._load_size_and_position_of_last_usage()
        self.setWindowTitle('Pyvisor')
        self.setWindowIcon(QIcon(str(resource_path('icons', 'game', 'MES_trans.png'))))
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self._initiate_tabs(vbox)

    def _initiate_tabs(self, vbox):
        # ---- toolbar for save / load ----
        toolbar = QHBoxLayout()
        btn_save = QPushButton("Save settings…")
        btn_save.setStyleSheet("font-weight: bold; padding: 4px 12px;")
        btn_save.clicked.connect(self._export_settings_json)
        toolbar.addWidget(btn_save)

        btn_load = QPushButton("Load settings…")
        btn_load.setStyleSheet("font-weight: bold; padding: 4px 12px;")
        btn_load.clicked.connect(self._import_settings_json)
        toolbar.addWidget(btn_load)
        toolbar.addStretch()
        vbox.addLayout(toolbar)

        # ---- tabs ----
        self.tabs = QTabWidget()
        vbox.addWidget(self.tabs)
        self.tab_behaviours = TabBehaviours(self, self.gui_data_interface)
        self.tab_buttons = TabButtons(self, self.gui_data_interface)
        self.tab_analysis = TabAnalysis(self, self.gui_data_interface)
        self.tab_results = TabResults(self, self.gui_data_interface)
        self.tab_names = ['Behaviours',
                          'Button Assignment',
                          'Analysis',
                          'Results Overview']
        tab_list = [self.tab_behaviours, self.tab_buttons, self.tab_analysis, self.tab_results]
        for tab, name in zip(tab_list, self.tab_names):
            self.tabs.addTab(tab, name)

    def _load_size_and_position_of_last_usage(self):
        try:
            self.setGeometry(self.values['display']['geometry'])
            self.move(self.values['display']['geometry'].topLeft())
        except (KeyError, TypeError):
            self.resize(960, 680)
        self.setMinimumSize(800, 500)

    def get_animal_tabs(self):        
        return self.tab_behaviours.tabs.tabs_

    def get_assignments(self):
        raise NotImplementedError
    
    def get_UIC_layout(self):
        return self.tab_buttons.getSelectedLayout()
            
    def set_value(self, key, value):
        """
        """
        self.values[key] = value

    def closeEvent(self, event):
        """
        Pops up a dialog-window when the user wants to close the GUI's window.
        """
        self._save_display_values()
        self.gui_data_interface.save_state()

        reply = QMessageBox.question(self,
                                     'Message',
                                     "Do you really want to quit? \n(Saved everything etc.?)",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _save_display_values(self):
        self.values['display']['geometry'] = self.frameGeometry()
        ensure_user_data_dir()
        settings_file = settings_path('guidefaults_movscoregui.pkl')
        with settings_file.open('wb') as f:
            pickle.dump(self.values, f, pickle.HIGHEST_PROTOCOL)

    # ── Save / Load entire configuration as portable JSON ───────

    def _export_settings_json(self):
        """Export animals, behaviours, key bindings, and device to a JSON file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save pyVISOR settings", "",
            "JSON files (*.json)")
        if not path:
            return
        state = self.gui_data_interface.get_savable_dict()
        try:
            with open(path, 'w') as fh:
                json.dump(state, fh, indent=2)
            QMessageBox.information(self, "Settings saved",
                                    "Configuration saved to:\n{}".format(path),
                                    QMessageBox.Ok)
        except Exception as exc:
            QMessageBox.critical(self, "Save failed", str(exc),
                                 QMessageBox.Ok)

    def _import_settings_json(self):
        """Import a previously saved JSON configuration.

        This will **replace** the current animals, behaviours and key
        bindings.  The GUI must be restarted for the changes to take
        full effect.
        """
        path, _ = QFileDialog.getOpenFileName(
            self, "Load pyVISOR settings", "",
            "JSON files (*.json)")
        if not path:
            return
        try:
            with open(path, 'r') as fh:
                state = json.load(fh)
            # Persist into the user‐data directory so it is loaded on restart
            settings_file = settings_path('guidefaults_animals.json')
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            with settings_file.open('wt') as fh:
                json.dump(state, fh, indent=2)
            QMessageBox.information(
                self, "Settings loaded",
                "Configuration loaded from:\n{}\n\n"
                "Please restart pyVISOR for the changes to take effect.".format(path),
                QMessageBox.Ok)
        except Exception as exc:
            QMessageBox.critical(self, "Load failed", str(exc),
                                 QMessageBox.Ok)


if __name__ == "__main__":

    import sys
    app = QApplication(sys.argv)
    ensure_user_data_dir()
    gui = MovScoreGUI()
    gui.show()

    sys.exit(app.exec_())
