# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for GameThogram.

Build locally:
    pip install pyinstaller
    pyinstaller gamethogram.spec

Output goes to dist/GameThogram/
"""
import sys
from pathlib import Path

block_cipher = None

# ── Paths ──────────────────────────────────────────────────
HERE = Path(SPECPATH)
RESOURCES = HERE / "pyvisor" / "resources"
ICON_ICO = str(RESOURCES / "gamethogram.ico")

# ── Collect all resource files (icons, logos) ──────────────
resource_datas = []
for f in RESOURCES.rglob("*"):
    if f.is_file() and "__pycache__" not in str(f):
        dest = str(f.parent.relative_to(HERE))
        resource_datas.append((str(f), dest))

# ── Analysis ───────────────────────────────────────────────
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# ── Collect package metadata that importlib.metadata needs ─
extra_datas = []
for pkg in ('imageio', 'pims', 'av', 'numpy', 'pandas', 'matplotlib',
            'PIL', 'pillow', 'scipy', 'tqdm', 'xlsxwriter', 'dill',
            'appdirs', 'pygame'):
    try:
        extra_datas += copy_metadata(pkg)
    except Exception:
        pass

# Also collect imageio plugin data files
try:
    extra_datas += collect_data_files('imageio')
except Exception:
    pass

a = Analysis(
    ["pyvisor/GUI/run_gui.py"],
    pathex=[str(HERE)],
    binaries=[],
    datas=resource_datas + extra_datas,
    hiddenimports=[
        "pygame",
        "pygame.mixer",
        "pygame.joystick",
        "pygame.display",
        "pygame.event",
        "pygame.image",
        "pygame.font",
        "pygame.surfarray",
        "pygame.time",
        "PIL",
        "PIL.Image",
        "pims",
        "pims.image_reader",
        "pims.image_sequence",
        "pims.api",
        "imageio",
        "imageio.core",
        "imageio.plugins",
        "av",
        "appdirs",
        "xlsxwriter",
        "scipy.io",
        "scipy.io.matlab",
        "matplotlib",
        "matplotlib.backends.backend_qt5agg",
        "matplotlib.backends.backend_agg",
        "numpy",
        "pandas",
        "dill",
        "pkg_resources.extern",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "test",
        "unittest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── Build ──────────────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GameThogram",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX can break Qt plugins
    console=False,  # No terminal window
    icon=ICON_ICO if sys.platform == "win32" else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="GameThogram",
)

# ── macOS .app bundle ──────────────────────────────────────
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="GameThogram.app",
        icon=str(RESOURCES / "gamethogram_logo.png"),
        bundle_identifier="nz.ac.otago.gamethogram",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": "0.1.0",
        },
    )
