#!/bin/bash
# Multi-Commit installer
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=============================="
echo "  Multi-Commit Installer"
echo "=============================="
echo ""

# ── Dependencies ──
echo "→ Installing dependencies..."
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0

# ── __init__.py files ──
touch "$SCRIPT_DIR/core/__init__.py"
touch "$SCRIPT_DIR/ui/__init__.py"

# ── Make executable ──
chmod +x "$SCRIPT_DIR/main.py"

# ── .desktop file (app menu + panel launcher) ──
DESKTOP_SRC="$SCRIPT_DIR/multi-commit.desktop"
cat > "$DESKTOP_SRC" <<EOF
[Desktop Entry]
Name=Multi-Commit
GenericName=Git GUI
Comment=Commit and push to multiple git remotes
Exec=python3 $SCRIPT_DIR/main.py
Icon=$SCRIPT_DIR/assets/icon.png
Terminal=false
Type=Application
Categories=Development;Utility;
Keywords=git;commit;push;github;
StartupNotify=true
StartupWMClass=multi-commit
EOF

# Install to user apps (Ulauncher + app menu)
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
cp "$DESKTOP_SRC" "$APPS_DIR/multi-commit.desktop"
chmod +x "$APPS_DIR/multi-commit.desktop"
update-desktop-database "$APPS_DIR" 2>/dev/null || true

# ── Panel launcher copy ──
PANEL_DIR="$HOME/.local/share/multi-commit"
mkdir -p "$PANEL_DIR"
cp "$DESKTOP_SRC" "$PANEL_DIR/multi-commit.desktop"

echo ""
echo "=============================="
echo "  ✅ Installation complete!"
echo "=============================="
echo ""
echo "Launch options:"
echo "  Terminal:   python3 $SCRIPT_DIR/main.py"
echo "  Ulauncher:  Ctrl+Space → type 'Multi-Commit'"
echo "  App menu:   Right-click desktop → Applications"
echo ""
echo "To add to Cinnamon panel:"
echo "  See PANEL_SETUP.md in this folder"
echo ""