#!/usr/bin/env bash
# Adeptus Mechanicus desktop installer for CachyOS + COSMIC.
# Usage: ./install.sh [--panel] [--pulse] [--skip-rgb] [--skip-packages]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PANEL=0; PULSE=0; RGB=1; PKGS=1
for a in "$@"; do
  case "$a" in
    --panel) PANEL=1 ;;
    --pulse) PULSE=1 ;;
    --skip-rgb) RGB=0 ;;
    --skip-packages) PKGS=0 ;;
    -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
    *) echo "unknown option: $a"; exit 1 ;;
  esac
done
say() { printf '\n\033[1;33m⚙ %s\033[0m\n' "$*"; }
backup() { [ -e "$1" ] && [ ! -e "$1.pre-mechanicus" ] && cp -a "$1" "$1.pre-mechanicus" || true; }

if [ "$PKGS" = 1 ]; then
  say "Packages (fastfetch, openrgb, python)"
  sudo pacman -S --needed --noconfirm fastfetch openrgb python python-pip
fi

say "Fastfetch: logo + config"
mkdir -p ~/.config/fastfetch
backup ~/.config/fastfetch/config.jsonc
cp "$HERE/fastfetch/logo.txt" ~/.config/fastfetch/mechanicus-logo.txt
cp "$HERE/fastfetch/config.jsonc" ~/.config/fastfetch/config.jsonc
echo "  try it: fastfetch"

say "Wallpaper"
WP=~/Pictures/Wallpapers/Mechanicus
mkdir -p "$WP"
cp "$HERE"/wallpaper/mechanicus-minimal-3840x2160.png "$HERE"/wallpaper/mechanicus-minimal.svg "$WP"/
echo "  copied to $WP"

if [ "$RGB" = 1 ]; then
  say "OpenRGB: Razer keyboard + mouse scheme"
  if ! ls /usr/lib/udev/rules.d/*openrgb* /etc/udev/rules.d/*openrgb* >/dev/null 2>&1; then
    echo "  ! no OpenRGB udev rules found; devices may need root. Install the 'openrgb' package (ships 60-openrgb.rules) and re-plug devices."
  fi
  if systemctl is-active --quiet openrazer-daemon 2>/dev/null || pgrep -x openrazer-daemon >/dev/null 2>&1; then
    echo "  ! openrazer-daemon is running; it can fight OpenRGB for the same devices. Stop/disable it if lights misbehave."
  fi
  D=~/.local/share/mechanicus-rgb
  mkdir -p "$D" ~/.config/systemd/user
  cp "$HERE/rgb/mechanicus_rgb.py" "$D/"
  [ -d "$D/venv" ] || python -m venv "$D/venv"
  "$D/venv/bin/pip" install -q --upgrade openrgb-python
  cp "$HERE/rgb/openrgb-server.service" ~/.config/systemd/user/
  cp "$HERE/rgb/mechanicus-rgb.service" ~/.config/systemd/user/
  if [ "$PULSE" = 1 ]; then
    sed -i 's|mechanicus_rgb.py$|mechanicus_rgb.py --pulse|; /^RemainAfterExit/d' ~/.config/systemd/user/mechanicus-rgb.service
  fi
  systemctl --user daemon-reload
  systemctl --user enable --now openrgb-server.service mechanicus-rgb.service || \
    echo "  ! could not start services now; they will start at next login."
  echo "  list LED names any time: $D/venv/bin/python $D/mechanicus_rgb.py --list"
fi

say "COSMIC theme"
python3 "$HERE/cosmic/cosmic_theme.py" theme || true
if [ "$PANEL" = 1 ]; then
  say "Panel + dock tint"
  python3 "$HERE/cosmic/cosmic_theme.py" panel
fi

cat <<MSG

Done. Remaining clicks in COSMIC Settings (about two minutes):
  1. Desktop > Appearance: import ~/.local/share/mechanicus-cosmic/mechanicus-dark.ron
     then set Dark mode, window corners "Square", frosted/translucency off.
  2. Desktop > Wallpaper: pick $WP/mechanicus-minimal-3840x2160.png (fit: Zoom).
  3. Desktop > Dock & Panel: Appearance "Dark" (or run ./install.sh --panel for the tint), gap off, rounded corners off.
  4. Add 'fastfetch' to the end of your shell rc (fish: ~/.config/fish/config.fish) if you want it on every terminal.
MSG
