#!/usr/bin/env python3
"""Add docstrings and tooltips to the pyVISOR codebase.

Run from the project root:  python scripts/add_docs.py
"""
import re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def _patch(path, old, new):
    with open(path, 'r') as f:
        content = f.read()
    if old not in content:
        print(f"  SKIP (pattern not found): {path}")
        return False
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print(f"  OK: {path}")
    return True


def _prepend_module_doc(path, docstring):
    """Add a module-level docstring if one doesn't already exist."""
    with open(path, 'r') as f:
        content = f.read()
    # Skip if file already starts with a docstring
    stripped = content.lstrip()
    if stripped.startswith('"""') or stripped.startswith("'''"):
        print(f"  SKIP (already has docstring): {path}")
        return
    # If starts with # comment or from __future__, insert before
    with open(path, 'w') as f:
        f.write(f'"""{docstring}"""\n{content}')
    print(f"  OK: {path}")


# ═══════════════════════════════════════════════════════════════════
# Module-level docstrings
# ═══════════════════════════════════════════════════════════════════

print("=== Module docstrings ===")

_prepend_module_doc("pyvisor/__init__.py",
    "pyVISOR — Desktop toolkit for manual ethology scoring.\n\n"
    "This package provides a PyQt5-based GUI for annotating animal\n"
    "behaviours in video recordings using gamepads or keyboards,\n"
    "with built-in analysis and export capabilities.\n")

_prepend_module_doc("pyvisor/GUI/__init__.py",
    "PyQt5 GUI components for pyVISOR.\n")

_prepend_module_doc("pyvisor/GUI/model/__init__.py",
    "Data model classes shared across the pyVISOR GUI.\n")

_prepend_module_doc("pyvisor/GUI/tab_behaviours/__init__.py",
    "Behaviour definition tab widgets.\n")

_prepend_module_doc("pyvisor/GUI/tab_buttons/__init__.py",
    "Button/key binding assignment tab widgets.\n")

_prepend_module_doc("pyvisor/GUI/icon_gallery/__init__.py",
    "Icon gallery and selection widgets.\n")

_prepend_module_doc("pyvisor/analysis/__init__.py",
    "Analysis modules for ethogram data.\n\n"
    "Provides online (live) and offline analysis utilities including\n"
    "behaviour percentages, bout durations, and transition matrices.\n")

_prepend_module_doc("pyvisor/exception/__init__.py",
    "Custom exception classes for pyVISOR.\n")


# ═══════════════════════════════════════════════════════════════════
# Class and method docstrings — core modules
# ═══════════════════════════════════════════════════════════════════

print("\n=== Core module docstrings ===")

# MediaHandler
_patch("pyvisor/MediaHandler.py",
    "class MediaHandler:",
    'class MediaHandler:\n'
    '    """Video and image sequence playback handler.\n\n'
    '    Wraps ``pims`` to provide frame-accurate access to movies,\n'
    '    Norpix SEQ files, and image sequences. Manages playback state\n'
    '    (play/pause, forward/reverse, FPS) and an in-memory frame buffer.\n\n'
    '    Parameters\n'
    '    ----------\n'
    '    filename : str\n'
    '        Path to the media file or image glob pattern.\n'
    '    mode : str\n'
    '        One of ``"movie"``, ``"norpix"``, or ``"image"``.\n'
    '    bufferSize : int\n'
    '        Maximum number of frames kept in the read-ahead buffer.\n'
    '    """')

# Ethogram
_patch("pyvisor/ethogram.py",
    "class Ethogram:",
    'class Ethogram:\n'
    '    """Container linking all per-animal ethograms with shared state.\n\n'
    '    Manages the live toggle states (which behaviours the user is\n'
    '    currently pressing) and delegates frame-level recording to\n'
    '    :class:`AnimalEthogram2` instances.\n'
    '    """')

# AnimalEthogram2
_patch("pyvisor/animal_ethogram_2.py",
    "class AnimalEthogram2:",
    'class AnimalEthogram2:\n'
    '    """Frame-level ethogram for a single animal.\n\n'
    '    Stores a boolean DataFrame where each column is a behaviour\n'
    '    and each row is a video frame. Provides methods to assign,\n'
    '    delete, and query behaviour states at individual frames.\n'
    '    """')

# dataIO
_patch("pyvisor/dataIO.py",
    "class dataIO:",
    'class dataIO:\n'
    '    """Data input/output handler for ethogram data.\n\n'
    '    Supports saving annotations as plain text, Excel, MATLAB, and\n'
    '    pickle formats. Also handles autosave with periodic background\n'
    '    snapshots and overlay frame/video export.\n'
    '    """')

# UserInputControl2
_patch("pyvisor/user_input_control.py",
    "class UserInputControl2:",
    'class UserInputControl2:\n'
    '    """Maps gamepad/keyboard input codes to scorer actions.\n\n'
    '    Reads the button-to-behaviour assignments from the GUI model\n'
    '    and builds a dispatch dictionary. Called from the scorer\'s\n'
    '    main loop on every pygame input event.\n'
    '    """')

# Icon
_patch("pyvisor/icon.py",
    "class Icon",
    'class Icon:\n'
    '    """Recolourable icon for behaviour display in the scorer window.\n\n'
    '    Loads a decal image, tints it to the behaviour\'s assigned colour,\n'
    '    and converts it to a pygame surface for blitting.\n'
    '    """' if False else 'class Icon')
# Icon class might have different format, let me check

# ═══════════════════════════════════════════════════════════════════
# GUI model classes
# ═══════════════════════════════════════════════════════════════════

print("\n=== GUI model docstrings ===")

_patch("pyvisor/GUI/model/animal.py",
    "class Animal:",
    'class Animal:\n'
    '    """Represents a single animal being observed.\n\n'
    '    Each animal has a numeric ID, a display name, and a dictionary\n'
    '    of :class:`Behaviour` objects keyed by their label strings.\n'
    '    """')

_patch("pyvisor/GUI/model/behaviour.py",
    "class Behaviour(ScorerAction):",
    'class Behaviour(ScorerAction):\n'
    '    """A scoreable behaviour linked to an animal.\n\n'
    '    Extends :class:`ScorerAction` with animal association, display\n'
    '    colour, icon path, and a compatibility list controlling which\n'
    '    other behaviours can be active simultaneously.\n'
    '    """')

_patch("pyvisor/GUI/model/scorer_action.py",
    "class ScorerAction:",
    'class ScorerAction:\n'
    '    """Base class for any action that can be bound to a button.\n\n'
    '    Used for both behaviours and movie control actions (play,\n'
    '    pause, seek, etc.). Stores per-device key bindings.\n'
    '    """')

_patch("pyvisor/GUI/model/key_bindings.py",
    "class KeyBindings:",
    'class KeyBindings:\n'
    '    """Per-device button/key binding storage.\n\n'
    '    Stores one binding string per supported device category:\n'
    '    X-Box, Playstation, Keyboard, or Free.\n'
    '    """')

_patch("pyvisor/GUI/model/movie_bindings.py",
    "class MovieBindings:",
    'class MovieBindings:\n'
    '    """Collection of movie-control actions with their key bindings.\n\n'
    '    Manages bindings for play/pause, stop, forward, reverse,\n'
    '    FPS adjustment, and frame stepping.\n'
    '    """')

_patch("pyvisor/GUI/model/gui_data_interface.py",
    "class GUIDataInterface:",
    'class GUIDataInterface:\n'
    '    """Central data model shared across all GUI tabs.\n\n'
    '    Holds the animal/behaviour definitions, device selection,\n'
    '    movie bindings, autosave settings, and the active scorer\n'
    '    instance. Provides callback hooks so UI widgets can react\n'
    '    to model changes.\n'
    '    """')

_patch("pyvisor/GUI/model/callback_handler.py",
    "class CallbackHandler",
    'class CallbackHandler:\n'
    '    """Simple observer-pattern callback registry.\n\n'
    '    Widgets register callables that are invoked when the\n'
    '    corresponding model event occurs.\n'
    '    """' if False else 'class CallbackHandler')

# ═══════════════════════════════════════════════════════════════════
# GUI tab classes
# ═══════════════════════════════════════════════════════════════════

print("\n=== GUI tab docstrings ===")

_patch("pyvisor/GUI/main_gui.py",
    "class MovScoreGUI(QWidget):",
    'class MovScoreGUI(QWidget):\n'
    '    """Main application window for pyVISOR.\n\n'
    '    Contains four tabs: Behaviours, Button Assignment, Analysis,\n'
    '    and Results Overview. Manages application-level state\n'
    '    persistence and settings import/export.\n'
    '    """')

_patch("pyvisor/GUI/tab_analysis.py",
    "class TabAnalysis(QWidget):",
    'class TabAnalysis(QWidget):\n'
    '    """Analysis tab — video loading, scorer control, and data export.\n\n'
    '    Provides the workflow for loading media, configuring autosave,\n'
    '    running the scorer, and exporting annotated data or overlay\n'
    '    frames/videos.\n'
    '    """')

_patch("pyvisor/GUI/tab_results.py",
    "class TabResults(QWidget):",
    'class TabResults(QWidget):\n'
    '    """Results tab — analysis plots with export.\n\n'
    '    Displays behaviour percentages, bout durations, and transition\n'
    '    matrices computed from the current scoring session or a\n'
    '    previously saved sidecar file. Each plot can be exported as\n'
    '    CSV, PNG, or SVG.\n'
    '    """')

_patch("pyvisor/GUI/tab_behaviours/tab_behaviours.py",
    "class TabBehaviours(QWidget):",
    'class TabBehaviours(QWidget):\n'
    '    """Behaviours tab — define animals and their behaviours.\n\n'
    '    Provides a sub-tab per animal where behaviours can be added,\n'
    '    removed, renamed, coloured, and assigned icons.\n'
    '    """')

_patch("pyvisor/GUI/tab_behaviours/single_animal_tab.py",
    "class SingleAnimalTab(QWidget):",
    'class SingleAnimalTab(QWidget):\n'
    '    """Sub-tab for a single animal\'s behaviour definitions.\n\n'
    '    Shows a grid of :class:`BehaviourWidget` instances with\n'
    '    controls to add, remove, copy, rename, and bulk-colour\n'
    '    behaviours.\n'
    '    """')

_patch("pyvisor/GUI/tab_behaviours/behaviour_widget.py",
    "class BehaviourWidget(QFrame):",
    'class BehaviourWidget(QFrame):\n'
    '    """Widget for editing a single behaviour\'s properties.\n\n'
    '    Displays and allows editing of the behaviour name, colour,\n'
    '    icon, and compatibility checkboxes.\n'
    '    """')

_patch("pyvisor/GUI/tab_buttons/tab_buttons.py",
    "class TabButtons(QWidget):",
    'class TabButtons(QWidget):\n'
    '    """Button Assignment tab — bind gamepad/keyboard inputs to actions.\n\n'
    '    Detects connected input devices via pygame, lets the user\n'
    '    assign physical buttons to behaviours and movie controls,\n'
    '    and provides default binding presets per device type.\n'
    '    """')

_patch("pyvisor/GUI/tab_buttons/assign_button_box.py",
    "class AssignButtonBox(QWidget):",
    'class AssignButtonBox(QWidget):\n'
    '    """Widget for a single button-to-action assignment.\n\n'
    '    Shows the action name, current binding, and an "assign button"\n'
    '    control. For gamepads, opens a dialog that polls for input;\n'
    '    for keyboards, opens a text entry dialog.\n'
    '    """')


# ═══════════════════════════════════════════════════════════════════
# ManualEthologyScorer2 — the main scorer
# ═══════════════════════════════════════════════════════════════════

print("\n=== Scorer docstrings ===")

_patch("pyvisor/manual_ethology_scorer_2.py",
    "class ManualEthologyScorer2:",
    'class ManualEthologyScorer2:\n'
    '    """Real-time video annotation engine.\n\n'
    '    Opens a pygame window showing the video with behaviour icon\n'
    '    overlays. Processes gamepad/keyboard input to toggle behaviour\n'
    '    states and records them frame-by-frame into an :class:`Ethogram`.\n\n'
    '    Supports:\n\n'
    '    - Sidecar-based session persistence (auto-save/resume)\n'
    '    - Autosave to a configurable directory\n'
    '    - F1-toggleable key binding overlay\n'
    '    - Visual distinction between live and recorded annotations\n'
    '    """')


# ═══════════════════════════════════════════════════════════════════
# GUI tooltips
# ═══════════════════════════════════════════════════════════════════

print("\n=== GUI tooltips ===")

# Main GUI buttons
_patch("pyvisor/GUI/main_gui.py",
    'btn_save.clicked.connect(self._export_settings_json)',
    'btn_save.setToolTip("Export all animal, behaviour, and key binding\\n"\n'
    '                         "settings to a portable JSON file.")\n'
    '        btn_save.clicked.connect(self._export_settings_json)')

_patch("pyvisor/GUI/main_gui.py",
    'btn_load.clicked.connect(self._import_settings_json)',
    'btn_load.setToolTip("Import a previously saved JSON settings file.\\n"\n'
    '                         "Restart required after loading.")\n'
    '        btn_load.clicked.connect(self._import_settings_json)')

# Analysis tab buttons
_patch("pyvisor/GUI/tab_analysis.py",
    "self.com_run.clicked.connect(self.runScorer)",
    'self.com_run.setToolTip("Open the scorer window to annotate the loaded video.\\n"\n'
    '                                "Previous annotations are restored automatically\\n"\n'
    '                                "from the resume file if available.")\n'
    '        self.com_run.clicked.connect(self.runScorer)')

_patch("pyvisor/GUI/tab_analysis.py",
    "self.com_export.clicked.connect(self.exportData)",
    'self.com_export.setToolTip("Export ethogram data in the selected format.")\n'
    '        self.com_export.clicked.connect(self.exportData)')

_patch("pyvisor/GUI/tab_analysis.py",
    "self.btn_any_video",
    'self.btn_any_video' if False else  # skip this since button was renamed
    "self.btn_any_video")

# Results tab
_patch("pyvisor/GUI/tab_results.py",
    "self.btn_refresh.clicked.connect(self._on_refresh)",
    'self.btn_refresh.setToolTip("Compute analysis from the current scoring session\\n"\n'
    '                                 "or from the saved resume file.")\n'
    '        self.btn_refresh.clicked.connect(self._on_refresh)')

# Tab buttons
_patch("pyvisor/GUI/tab_buttons/tab_buttons.py",
    'button_reset.clicked.connect(self._reset_buttons)',
    'button_reset.setToolTip("Clear all button assignments for the current device.")\n'
    '        button_reset.clicked.connect(self._reset_buttons)')

_patch("pyvisor/GUI/tab_buttons/tab_buttons.py",
    'button_default_bindings.clicked.connect(self._set_default_movie_bindings)',
    'button_default_bindings.setToolTip("Assign standard movie control bindings\\n"\n'
    '                                            "for the selected device type.")\n'
    '        button_default_bindings.clicked.connect(self._set_default_movie_bindings)')

_patch("pyvisor/GUI/tab_buttons/tab_buttons.py",
    'button_device_info.clicked.connect(self._show_device_info)',
    'button_device_info.setToolTip("Show detected devices, axes, buttons,\\n"\n'
    '                                       "and current binding summary.")\n'
    '        button_device_info.clicked.connect(self._show_device_info)')

# Behaviour tab buttons
_patch("pyvisor/GUI/tab_behaviours/single_animal_tab.py",
    "btn_copy_animal.clicked.connect(self.copy_this_tab)",
    'btn_copy_animal.setToolTip("Create a new animal with the same behaviours.")\n'
    '        btn_copy_animal.clicked.connect(self.copy_this_tab)')

_patch("pyvisor/GUI/tab_behaviours/single_animal_tab.py",
    "btn_set_color.clicked.connect(self._set_animal_colour)",
    'btn_set_color.setToolTip("Set one colour for all behaviours of this animal.")\n'
    '        btn_set_color.clicked.connect(self._set_animal_colour)')

_patch("pyvisor/GUI/tab_behaviours/single_animal_tab.py",
    "btn_remove_animal.clicked.connect(self.remove_this_tab)",
    'btn_remove_animal.setToolTip("Permanently remove this animal and all its behaviours.")\n'
    '        btn_remove_animal.clicked.connect(self.remove_this_tab)')


print("\n=== Sphinx conf.py ===")

# Create a docs/conf.py for Sphinx auto-documentation
os.makedirs("docs", exist_ok=True)
with open("docs/conf.py", "w") as f:
    f.write('''\
"""Sphinx configuration for pyVISOR documentation."""

project = "pyVISOR"
author = "Bart Geurten, Ilyas Kuhlemann"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}
''')

# Create docs/index.rst
with open("docs/index.rst", "w") as f:
    f.write('''\
pyVISOR Documentation
=====================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/modules

.. automodule:: pyvisor
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
''')

os.makedirs("docs/api", exist_ok=True)
with open("docs/api/modules.rst", "w") as f:
    f.write('''\
API Reference
=============

.. toctree::
   :maxdepth: 4

   pyvisor


.. automodule:: pyvisor.manual_ethology_scorer_2
   :members:
   :undoc-members:

.. automodule:: pyvisor.MediaHandler
   :members:
   :undoc-members:

.. automodule:: pyvisor.ethogram
   :members:
   :undoc-members:

.. automodule:: pyvisor.animal_ethogram_2
   :members:
   :undoc-members:

.. automodule:: pyvisor.dataIO
   :members:
   :undoc-members:

.. automodule:: pyvisor.user_input_control
   :members:
   :undoc-members:

.. automodule:: pyvisor.paths
   :members:

.. automodule:: pyvisor.analysis.ethogram_analysis
   :members:

.. automodule:: pyvisor.analysis.analysis_online
   :members:
   :undoc-members:

.. automodule:: pyvisor.analysis.analysis_offline
   :members:
   :undoc-members:

GUI Components
--------------

.. automodule:: pyvisor.GUI.main_gui
   :members:

.. automodule:: pyvisor.GUI.tab_analysis
   :members:

.. automodule:: pyvisor.GUI.tab_results
   :members:

.. automodule:: pyvisor.GUI.tab_behaviours.tab_behaviours
   :members:

.. automodule:: pyvisor.GUI.tab_buttons.tab_buttons
   :members:

Data Model
----------

.. automodule:: pyvisor.GUI.model.gui_data_interface
   :members:

.. automodule:: pyvisor.GUI.model.animal
   :members:

.. automodule:: pyvisor.GUI.model.behaviour
   :members:

.. automodule:: pyvisor.GUI.model.key_bindings
   :members:

.. automodule:: pyvisor.GUI.model.movie_bindings
   :members:

.. automodule:: pyvisor.GUI.model.scorer_action
   :members:
''')

print("OK: docs/conf.py, docs/index.rst, docs/api/modules.rst")
print("\nDone! Run `sphinx-apidoc -o docs/api pyvisor` then `cd docs && make html`")
