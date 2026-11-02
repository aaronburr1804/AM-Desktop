#!/usr/bin/env bash
# Installs the flickering ASCII desktop widget + minimal wallpaper.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
D="$HOME/.local/share/mechanicus-ascii"
echo "→ packages"
sudo pacman -S --needed --noconfirm gtk4 gtk4-layer-shell python-gobject python-cairo
mkdir -p "$D" "$HOME/.config/autostart" "$HOME/Pictures/Wallpapers/Mechanicus"
cp "$HERE/ascii_flicker.py" "$D/"
cp "$HERE/art.txt" "$D/art.txt"
cp "$HERE/../wallpaper/mechanicus-minimal-3840x2160.png" "$HOME/Pictures/Wallpapers/Mechanicus/"
cat > "$HOME/.config/autostart/mechanicus-ascii.desktop" << DESK
[Desktop Entry]
Type=Application
Name=Mechanicus ASCII widget
Exec=/usr/bin/python3 $D/ascii_flicker.py
X-GNOME-Autostart-enabled=true
NoDisplay=true
DESK
pkill -f ascii_flicker.py 2>/dev/null || true
setsid -f /usr/bin/python3 "$D/ascii_flicker.py" >/tmp/mechanicus-ascii.log 2>&1 || true
cat << MSG
→ widget started (log: /tmp/mechanicus-ascii.log), autostarts at login via ~/.config/autostart.
→ Set the wallpaper: Settings > Desktop > Wallpaper > ~/Pictures/Wallpapers/Mechanicus/mechanicus-minimal-3840x2160.png
Tune placement:  python3 $D/ascii_flicker.py --always-on --x 0.76 --y 0.5 --scale 0.72
Change the Exec= line in ~/.config/autostart/mechanicus-ascii.desktop once you like it (add --monitor all for every screen).
Stop it:  pkill -f ascii_flicker.py
MSG
