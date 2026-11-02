#!/usr/bin/env python3
"""Build an importable Mechanicus theme for COSMIC, and optionally tint the panel/dock.

  cosmic_theme.py theme            writes mechanicus-dark.ron (import it in Settings)
  cosmic_theme.py panel            tint panel + dock (backs up old files first)
  cosmic_theme.py panel --revert   restore the backups
  cosmic_theme.py colors           print the palette as hex

Why a template? COSMIC's theme schema has changed between releases (builder v1 -> v2).
Instead of hard-coding the whole file, `theme` starts from a theme your installed COSMIC
ships in /usr/share/cosmic-themes/ and only swaps the colour fields, so the structure
always matches your version.
"""
import argparse
import glob
import os
import re
import shutil
import sys
import time

HOME = os.path.expanduser("~")
OUT_DIR = os.path.join(HOME, ".local/share/mechanicus-cosmic")

# readability-first palette: bone text on void-red, brass accent, red kept for "destructive"
PALETTE = {
    "bg_color":    "#150a0a",   # void black with a red cast
    "text_tint":   "#eadfc4",   # parchment / bone  (~14:1 on bg)
    "accent":      "#d4a640",   # brass             (~8:1 on bg)
    "neutral_tint": "#3a2a28",  # warm steel
    "success":     "#5cc96b",   # cogitator phosphor green
    "warning":     "#e0a526",   # amber
    "destructive": "#f0483b",   # alarm red
}

PANEL_BG = "#120808"


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def srgb(h):
    r, g, b = hex_rgb(h)
    return f"(red: {r:.4f}, green: {g:.4f}, blue: {b:.4f})"


def cmd_colors(_):
    for k, v in PALETTE.items():
        print(f"{k:13} {v}")
    print(f"{'panel/dock':13} {PANEL_BG}")


def find_template():
    cands = sorted(glob.glob("/usr/share/cosmic-themes/*dark*.ron"))
    pref = [c for c in cands if "nebula" in c] or cands
    return pref[0] if pref else None


def swap_field(text, field, hexval):
    """Replace `field: None | Some((..)) | (..)` keeping the original wrapper style."""
    pat = re.compile(rf"(\b{field}:\s*)(None|Some\(\s*\([^)]*\)\s*\)|\([^)]*\))")
    m = pat.search(text)
    new = srgb(hexval)
    if not m:
        return text, False
    old = m.group(2)
    if old.startswith("Some") or old == "None":
        rep = f"Some({new})"
    else:
        rep = new
    return text[:m.start(2)] + rep + text[m.end(2):], True


def cmd_theme(_):
    tpl = find_template()
    if not tpl:
        print("No /usr/share/cosmic-themes/*dark*.ron found (is cosmic-initial-setup installed?).")
        print("Set these by hand in Settings > Desktop > Appearance instead:")
        cmd_colors(None)
        return 1
    text = open(tpl, encoding="utf-8").read()
    missed = []
    for field, hx in PALETTE.items():
        text, ok = swap_field(text, field, hx)
        if not ok:
            missed.append(field)
    text = re.sub(r"(\bis_frosted:\s*)(true|false)", r"\1false", text)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "mechanicus-dark.ron")
    open(out, "w", encoding="utf-8").write(text)
    print(f"template : {tpl}")
    print(f"written  : {out}")
    if missed:
        print("not found in template (set by hand): " + ", ".join(missed))
        for k in missed:
            print(f"   {k:13} {PALETTE[k]}")
    print("\nNext: Settings > Desktop > Appearance > (Import) > pick that file.")
    return 0


PANELS = ("com.system76.CosmicPanel.Panel", "com.system76.CosmicPanel.Dock")


def cmd_panel(args):
    base = os.path.join(HOME, ".config/cosmic")
    for p in PANELS:
        d = os.path.join(base, p, "v1")
        bg = os.path.join(d, "background")
        bak = bg + ".mechanicus.bak"
        if args.revert:
            if os.path.exists(bak):
                shutil.move(bak, bg)
                print(f"restored {bg}")
            elif os.path.exists(bg):
                os.remove(bg)
                print(f"removed {bg} (back to default)")
            continue
        os.makedirs(d, exist_ok=True)
        if os.path.exists(bg) and not os.path.exists(bak):
            shutil.copy2(bg, bak)
        r, g, b = hex_rgb(PANEL_BG)
        open(bg, "w").write(f"Color(({r:.4f}, {g:.4f}, {b:.4f}))")
        print(f"wrote {bg}")
    print("COSMIC reloads panel config live. If the panel looks wrong, run: cosmic_theme.py panel --revert")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("theme").set_defaults(fn=cmd_theme)
    sub.add_parser("colors").set_defaults(fn=cmd_colors)
    p = sub.add_parser("panel")
    p.add_argument("--revert", action="store_true")
    p.set_defaults(fn=cmd_panel)
    args = ap.parse_args()
    sys.exit(args.fn(args) or 0)


if __name__ == "__main__":
    main()
