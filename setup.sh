#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1
sudo apt install -y playerctl

python3 -m venv "$PROJECT_DIR/venv" --system-site-packages
source "$PROJECT_DIR/venv/bin/activate"
pip3 install pywebview
deactivate

cat > "$PROJECT_DIR/run.sh" << EOF
#!/bin/bash
cd "$PROJECT_DIR"
source venv/bin/activate
python3 main.py
EOF

chmod u+x "$PROJECT_DIR/run.sh"

DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
mkdir -p "$DESKTOP_DIR"
DESKTOP_FILE="$DESKTOP_DIR/mini-player.desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Exec=/bin/bash -c 'cd "$PROJECT_DIR" && ./run.sh'
Type=Application
Terminal=false
Name=Mini player
Icon=$PROJECT_DIR/icon.png
EOF

chmod u+x "$DESKTOP_FILE"

echo "Setup terminé ! Un raccourci a été placé sur le bureau."
