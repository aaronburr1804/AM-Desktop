# Adeptus Mechanicus desktop — CachyOS + COSMIC

    ./install.sh              # packages, fastfetch, wallpaper, OpenRGB service, theme file
    ./install.sh --panel      # also tint panel + dock
    ./install.sh --pulse      # slow breathing RGB instead of static

## Palette (readability first)
| Role | Hex | Why |
|---|---|---|
| Background | `#150a0a` | void black, red cast |
| Text | `#eadfc4` | bone/parchment, ~14:1 contrast |
| Accent | `#d4a640` | brass, ~8:1 contrast |
| Destructive | `#f0483b` | red kept for warnings only, so it still means "danger" |
| Success / Warning | `#5cc96b` / `#e0a526` | cogitator green / amber |

Red is the *mood* (wallpaper, keyboard, logo); brass is the *UI accent*. Putting red on
selections and buttons would make errors indistinguishable from normal UI.

## Files
- `fastfetch/` config.jsonc, logo.txt (regenerate with gen_logo.py). Labels read "Forge World (OS)" etc. so the real meaning stays visible.
- `wallpaper/` 3840x2160 PNG + SVG (regenerate with gen_wallpaper.py). Emblem sits right; left side is calm for windows.
- `rgb/` mechanicus_rgb.py + two systemd user units. `--list` prints LED names, `--off`, `--pulse`, `--all-vendors`.
- `cosmic/cosmic_theme.py` builds an importable theme from a template COSMIC itself ships, so it matches your installed version.

## Troubleshooting
- No devices found: `openrgb --list-devices`; check udev rules; stop `openrazer-daemon` (it contends with OpenRGB).
- A key is the wrong colour: run `mechanicus_rgb.py --list` and add its name to the sets at the top of the script.
- Lights reset after suspend: `systemctl --user restart mechanicus-rgb`, or use `--pulse` (it keeps re-sending).
- Prefer an OpenRGB profile: once the lights look right, click *Save Profile* in the OpenRGB GUI and load it with `openrgb --profile <name>`.
- Undo: `*.pre-mechanicus` backups sit beside replaced files; `cosmic_theme.py panel --revert` resets panel tint.
