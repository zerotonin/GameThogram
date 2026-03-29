#!/usr/bin/env bash
# ╔═══════════════════════════════════════════════════════════╗
# ║  GameThogram — local PyInstaller build script             ║
# ║  Run from the project root:  bash scripts/build_local.sh  ║
# ╚═══════════════════════════════════════════════════════════╝
set -e

echo "╔═══════════════════════════════════════╗"
echo "║  Building GameThogram with PyInstaller ║"
echo "╚═══════════════════════════════════════╝"

# Check we're in the right directory
if [ ! -f "gamethogram.spec" ]; then
    echo "ERROR: Run this from the project root (where gamethogram.spec lives)"
    exit 1
fi

# Install PyInstaller if needed
python -m pip show pyinstaller > /dev/null 2>&1 || {
    echo "Installing PyInstaller..."
    pip install pyinstaller
}

# Clean previous builds
rm -rf build/ dist/

# Build
echo "Running PyInstaller..."
pyinstaller gamethogram.spec

# Check result
if [ -d "dist/GameThogram" ]; then
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║  Build succeeded!                      ║"
    echo "╚═══════════════════════════════════════╝"
    echo ""
    echo "Output: dist/GameThogram/"
    echo ""
    du -sh dist/GameThogram/
    echo ""
    echo "Test it:  ./dist/GameThogram/GameThogram"
    echo ""
    echo "To package for distribution:"
    echo "  Linux:   cd dist && tar czf GameThogram-Linux.tar.gz GameThogram/"
    echo "  macOS:   cd dist && zip -r GameThogram-macOS.zip GameThogram/"
    echo "  Windows: cd dist && 7z a GameThogram-Windows.zip GameThogram/"
else
    echo ""
    echo "ERROR: Build failed — check output above"
    exit 1
fi
