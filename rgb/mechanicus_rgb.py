#!/usr/bin/env python3
"""Adeptus Mechanicus lighting for OpenRGB (Razer keyboard + mouse by default).

Needs an OpenRGB SDK server running (openrgb --server) and `openrgb-python`.

  mechanicus_rgb.py                apply the static scheme once and exit
  mechanicus_rgb.py --pulse        apply it, then keep a slow "machine spirit" breathing loop
  mechanicus_rgb.py --off          all LEDs off
  mechanicus_rgb.py --list         print detected devices + LED names (use this if a key looks wrong)
  mechanicus_rgb.py --all-vendors  also light non-Razer keyboards/mice
"""
import argparse
import math
import signal
import sys
import time

from openrgb import OpenRGBClient
from openrgb.utils import DeviceType, RGBColor

CRIMSON = (170, 12, 12)      # robes
BRASS = (215, 160, 40)       # cog-work / key accents
BONE = (235, 225, 200)       # skull white (Esc)
OPTIC = (255, 40, 20)        # servo-skull eye (mouse logo / underglow)

# keys that get brass; everything else stays crimson
BRASS_KEYS = (
    {"w", "a", "s", "d"}
    | {f"f{i}" for i in range(1, 13)}
    | {"up arrow", "down arrow", "left arrow", "right arrow", "up", "down", "left", "right"}
)
BONE_KEYS = {"escape", "esc"}
KEY_ACCENT_PREFIXES = ("logo", "razer logo")


def norm(name: str) -> str:
    n = name.lower().strip()
    for p in ("key: ", "keyboard: "):
        if n.startswith(p):
            n = n[len(p):]
    return n


def color_for_keyboard_led(name: str):
    n = norm(name)
    if n in BONE_KEYS:
        return BONE
    if n in BRASS_KEYS:
        return BRASS
    if n.startswith(KEY_ACCENT_PREFIXES) or "underglow" in n or "light bar" in n:
        return OPTIC
    return CRIMSON


def color_for_mouse_led(name: str):
    n = norm(name)
    if "logo" in n:
        return OPTIC
    if "scroll" in n or "wheel" in n:
        return BRASS
    return CRIMSON


def pick_devices(client, all_vendors: bool):
    chosen = []
    for dev in client.devices:
        if dev.type not in (DeviceType.KEYBOARD, DeviceType.MOUSE):
            continue
        if not all_vendors and "razer" not in dev.name.lower():
            continue
        chosen.append(dev)
    return chosen


def set_direct(dev):
    for mode in ("direct", "Direct", "custom", "Custom", "static", "Static"):
        try:
            dev.set_mode(mode)
            return mode
        except Exception:
            continue
    return None


def build_palette(dev):
    fn = color_for_keyboard_led if dev.type == DeviceType.KEYBOARD else color_for_mouse_led
    return [fn(led.name) for led in dev.leds]


def apply(dev, scale=1.0):
    pal = build_palette(dev)
    cols = [RGBColor(int(r * scale), int(g * scale), int(b * scale)) for r, g, b in pal]
    dev.set_colors(cols, fast=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=6742)
    ap.add_argument("--pulse", action="store_true", help="slow breathing loop (runs until stopped)")
    ap.add_argument("--off", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--all-vendors", action="store_true")
    args = ap.parse_args()

    # the server may still be starting at login
    client = None
    for attempt in range(20):
        try:
            client = OpenRGBClient(address=args.host, port=args.port, name="mechanicus-rgb")
            break
        except Exception:
            time.sleep(1.5)
    if client is None:
        sys.exit("Could not reach the OpenRGB server. Start it with: openrgb --server")

    if args.list:
        for i, dev in enumerate(client.devices):
            print(f"[{i}] {dev.name}  type={dev.type.name}  leds={len(dev.leds)}")
            for led in dev.leds:
                print(f"      {led.name}")
        return

    devices = pick_devices(client, args.all_vendors)
    if not devices:
        sys.exit("No matching keyboard/mouse found. Run with --list, check udev rules, "
                 "and make sure openrazer-daemon isn't holding the devices.")

    for dev in devices:
        mode = set_direct(dev)
        if mode is None:
            print(f"warning: {dev.name} has no direct/static mode; skipping", file=sys.stderr)
            continue
        if args.off:
            dev.set_color(RGBColor(0, 0, 0))
        else:
            apply(dev)
        print(f"{dev.name}: {'off' if args.off else 'Mechanicus scheme applied'} ({mode})")

    if args.pulse and not args.off:
        running = True

        def stop(*_):
            nonlocal running
            running = False

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        t0 = time.time()
        while running:
            # 6 s period, between 40% and 100% brightness
            scale = 0.70 + 0.30 * math.sin((time.time() - t0) * 2 * math.pi / 6.0)
            for dev in devices:
                try:
                    apply(dev, scale)
                except Exception:
                    pass
            time.sleep(0.06)
        for dev in devices:
            try:
                apply(dev, 1.0)
            except Exception:
                pass


if __name__ == "__main__":
    main()
