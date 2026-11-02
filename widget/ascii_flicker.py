#!/usr/bin/env python3
"""Mechanicus ASCII widget: flickers your ASCII logo in and out on the desktop.

It is a click-through Wayland layer-shell surface on the BOTTOM layer: above the
wallpaper, below every window. Idle cost is a 12 fps timer that only redraws when
something changes (nothing is drawn while the art is hidden).

  ascii_flicker.py                     run on the first monitor
  ascii_flicker.py --monitor all       one widget per monitor
  ascii_flicker.py --x 0.75 --y 0.5 --scale 0.7   position / height as fractions of the screen
  ascii_flicker.py --always-on         never fade out (handy while positioning)
  ascii_flicker.py --render-test out.png          draw sample frames offscreen (no GTK needed)

Needs: gtk4, gtk4-layer-shell, python-gobject, python-cairo.
"""
import argparse
import os
import random
import re
import sys
import time

DEFAULT_ARTS = (
    "~/.local/share/mechanicus-ascii/art.txt",
    "~/.config/fastfetch/mechanicus-logo.txt",
)

RED = (0.80, 0.16, 0.13)
HOT = (0.95, 0.30, 0.22)
BRASS = (0.79, 0.64, 0.29)
BONE = (0.91, 0.86, 0.75)

# character -> (layer name)
CLASS_OF = {".": "dot", ":": "low", "-": "low", "+": "mid", "=": "mid", "*": "mid",
            "#": "high", "%": "high", "@": "max"}
LAYERS = [  # name, colour, base alpha
    ("dot", BRASS, 0.16),
    ("low", RED, 0.45),
    ("mid", RED, 0.65),
    ("high", RED, 0.85),
    ("max", HOT, 1.00),
    ("other", RED, 0.60),
]


def load_art(path=None):
    cands = [path] if path else list(DEFAULT_ARTS)
    for c in cands:
        p = os.path.expanduser(c)
        if os.path.isfile(p):
            raw = open(p, encoding="utf-8").read().splitlines()
            lines = [re.sub(r"\$\d", "", ln).rstrip("\n") for ln in raw]
            while lines and not lines[-1].strip():
                lines.pop()
            width = max(len(ln) for ln in lines)
            return [ln.ljust(width) for ln in lines], p
    sys.exit("No ASCII art found. Pass --art FILE or put it in ~/.local/share/mechanicus-ascii/art.txt")


class Flicker:
    HIDDEN, BOOT, HOLD, OUT = range(4)

    def __init__(self, lines, always_on=False, seed=None):
        self.rng = random.Random(seed)
        self.lines = lines
        self.rows = len(lines)
        self.cols = len(lines[0])
        self.always_on = always_on
        self.layers = []            # (colour, alpha, [row strings])
        for name, colour, alpha in LAYERS:
            rows = []
            for ln in lines:
                s = "".join(ch if (ch != " " and CLASS_OF.get(ch, "other") == name) else " " for ch in ln)
                rows.append(s if s.strip() else "")
            if any(rows):
                self.layers.append((colour, alpha, rows))
        self.row_alpha = [0.0] * self.rows
        self.row_dx = [0] * self.rows
        self.scan = -1
        self.dip = 0
        self.dip_alpha = 1.0
        self.state = self.HIDDEN
        self.t0 = time.monotonic()
        self.dur = self.rng.uniform(2.0, 4.0)
        if always_on:
            self._enter(self.HOLD, self.t0)

    # ---- state machine -------------------------------------------------
    def _enter(self, state, now):
        self.state = state
        self.t0 = now
        self.dur = {
            self.HIDDEN: self.rng.uniform(6.0, 16.0),
            self.BOOT: self.rng.uniform(1.2, 2.0),
            self.HOLD: self.rng.uniform(4.0, 10.0),
            self.OUT: self.rng.uniform(0.7, 1.3),
        }[state]
        if state == self.HOLD and self.always_on:
            self.dur = 1e9

    def tick(self, now):
        """Advance one frame. Returns True if the picture changed."""
        r = self.rng
        p = (now - self.t0) / self.dur
        if p >= 1.0:
            nxt = {self.HIDDEN: self.BOOT, self.BOOT: self.HOLD, self.HOLD: self.OUT, self.OUT: self.HIDDEN}[self.state]
            self._enter(nxt, now)
            p = 0.0
        n = self.rows
        if self.state == self.HIDDEN:
            changed = any(self.row_alpha) or self.scan != -1
            self.row_alpha = [0.0] * n
            self.row_dx = [0] * n
            self.scan = -1
            return changed
        if self.state == self.BOOT:
            self.scan = -1
            for i in range(n):
                thr = (i / n) * 0.75
                if p < thr:
                    self.row_alpha[i] = 0.0
                    continue
                stable = min(1.0, (p - thr) / 0.25)
                on = r.random() < 0.45 + 0.55 * stable
                self.row_alpha[i] = 0.85 if on else 0.2
                self.row_dx[i] = 0 if stable > 0.6 else r.choice((-1, 0, 0, 1))
                if abs(p / 0.75 * n - i) < 1.0 and p < 0.75:
                    self.scan = i
            return True
        if self.state == self.HOLD:
            self.scan = -1
            if self.dip > 0:
                self.dip -= 1
            elif r.random() < 0.035:
                self.dip = r.randint(1, 4)
                self.dip_alpha = r.uniform(0.15, 0.55)
            level = self.dip_alpha if self.dip > 0 else 0.85 - r.uniform(0.0, 0.08)
            self.row_alpha = [level] * n
            self.row_dx = [0] * n
            if r.random() < 0.05:                       # horizontal tear
                start = r.randrange(n)
                shift = r.choice((-2, -1, 1, 2))
                for k in range(start, min(n, start + r.randint(1, 3))):
                    self.row_dx[k] = shift
            return True
        # OUT: stutter and collapse
        self.scan = -1
        p_on = (1.0 - p) ** 1.5
        blink_off = r.random() < 0.25
        for i in range(n):
            self.row_alpha[i] = 0.0 if blink_off or r.random() > p_on else 0.8
            self.row_dx[i] = r.choice((-3, -1, 0, 0, 0, 1, 3)) if r.random() < 0.15 else 0
        return True

    # ---- drawing -------------------------------------------------------
    def draw(self, cr, w, h, cx=0.76, cy=0.5, scale=0.72):
        if not any(self.row_alpha):
            return
        cr.select_font_face("monospace")
        cr.set_font_size(100)
        adv100 = cr.text_extents("M").x_advance
        fs = (scale * h) / (self.rows * 1.2)
        fs = min(fs, (0.46 * w) / (self.cols * adv100 / 100.0))
        cr.set_font_size(fs)
        adv = adv100 * fs / 100.0
        cell_h = fs * 1.2
        x0 = cx * w - self.cols * adv / 2.0
        y0 = cy * h - self.rows * cell_h / 2.0 + fs
        for i in range(self.rows):
            ra = self.row_alpha[i]
            if ra <= 0.01:
                continue
            x = x0 + self.row_dx[i] * adv
            y = y0 + i * cell_h
            if i == self.scan:
                cr.set_source_rgba(*BONE, 0.95)
                cr.move_to(x, y)
                cr.show_text(self.lines[i].replace(".", " "))
                continue
            for colour, alpha, rows in self.layers:
                s = rows[i]
                if not s:
                    continue
                cr.set_source_rgba(*colour, alpha * ra)
                cr.move_to(x, y)
                cr.show_text(s)


# ---- offscreen test ----------------------------------------------------
def render_test(lines, out, args):
    import cairo
    f = Flicker(lines, seed=7)
    t = f.t0
    shots, want = [], {}
    dt = 1 / 12
    names = {Flicker.BOOT: "boot", Flicker.HOLD: "hold", Flicker.OUT: "glitch-out"}
    for _ in range(2000):
        t += dt
        f.tick(t)
        prog = (t - f.t0) / f.dur
        for st, pr in ((Flicker.BOOT, 0.45), (Flicker.HOLD, 0.5), (Flicker.OUT, 0.35)):
            if f.state == st and prog >= pr and st not in want:
                want[st] = True
                W, H = 960, 540
                surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
                cr = cairo.Context(surf)
                cr.set_source_rgb(0.02, 0.016, 0.016)
                cr.paint()
                f.draw(cr, W, H, args.x, args.y, args.scale)
                cr.set_source_rgba(1, 1, 1, 0.5)
                cr.set_font_size(18)
                cr.move_to(14, 28)
                cr.show_text(names[st])
                shots.append(surf)
        if len(shots) == 3:
            break
    W, H = 960, 540
    sheet = cairo.ImageSurface(cairo.FORMAT_ARGB32, W * 2, H * 2)
    cr = cairo.Context(sheet)
    cr.set_source_rgb(0, 0, 0)
    cr.paint()
    for k, s in enumerate(shots):
        cr.set_source_surface(s, (k % 2) * W, (k // 2) * H)
        cr.paint()
    sheet.write_to_png(out)
    print("wrote", out)


# ---- GTK front end -----------------------------------------------------
def run_gtk(lines, args):
    # gtk4-layer-shell must be loaded before libwayland-client: preload it and re-exec once.
    if not os.environ.get("MECH_ASCII_PRELOADED"):
        for cand in ("/usr/lib/libgtk4-layer-shell.so", "/usr/lib64/libgtk4-layer-shell.so",
                     "/usr/lib/x86_64-linux-gnu/libgtk4-layer-shell.so"):
            if os.path.exists(cand):
                env = dict(os.environ)
                env["LD_PRELOAD"] = cand + (":" + env["LD_PRELOAD"] if env.get("LD_PRELOAD") else "")
                env["MECH_ASCII_PRELOADED"] = "1"
                os.execve(sys.executable, [sys.executable] + sys.argv, env)

    import gi
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gdk", "4.0")
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gdk, GLib, Gtk
    from gi.repository import Gtk4LayerShell as LS
    try:
        import cairo
    except ImportError:
        cairo = None

    flicker = Flicker(lines, always_on=args.always_on)

    class App(Gtk.Application):
        def __init__(self):
            super().__init__(application_id="local.mechanicus.ascii")
            self.areas = []

        def do_activate(self):
            css = Gtk.CssProvider()
            css.load_from_string("window.mech-ascii, window.mech-ascii > * { background: transparent; }")
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            mons = Gdk.Display.get_default().get_monitors()
            if args.monitor == "all":
                targets = [mons.get_item(i) for i in range(mons.get_n_items())]
            else:
                idx = min(int(args.monitor), mons.get_n_items() - 1)
                targets = [mons.get_item(idx)]
            for m in targets:
                self.make_window(m)
            GLib.timeout_add(int(1000 / args.fps), self.on_tick)

        def make_window(self, monitor):
            win = Gtk.ApplicationWindow(application=self)
            win.add_css_class("mech-ascii")
            win.set_decorated(False)
            LS.init_for_window(win)
            LS.set_namespace(win, "mechanicus-ascii")
            LS.set_layer(win, LS.Layer.BOTTOM)          # above wallpaper, below windows
            for edge in (LS.Edge.TOP, LS.Edge.BOTTOM, LS.Edge.LEFT, LS.Edge.RIGHT):
                LS.set_anchor(win, edge, True)
            LS.set_exclusive_zone(win, -1)
            LS.set_keyboard_mode(win, LS.KeyboardMode.NONE)
            LS.set_monitor(win, monitor)
            area = Gtk.DrawingArea()
            area.set_draw_func(lambda a, cr, w, h: flicker.draw(cr, w, h, args.x, args.y, args.scale))
            win.set_child(area)

            def make_click_through(w):
                if cairo is not None:
                    try:
                        w.get_surface().set_input_region(cairo.Region())
                    except Exception as e:      # still works, just not click-through
                        print("click-through unavailable:", e, file=sys.stderr)
            win.connect("realize", make_click_through)
            win.present()
            self.areas.append(area)

        def on_tick(self):
            if flicker.tick(time.monotonic()):
                for a in self.areas:
                    a.queue_draw()
            return True

    sys.exit(App().run([sys.argv[0]]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--art")
    ap.add_argument("--monitor", default="0", help="monitor index or 'all'")
    ap.add_argument("--x", type=float, default=0.35, help="art centre, fraction of width")
    ap.add_argument("--y", type=float, default=0.50, help="art centre, fraction of height")
    ap.add_argument("--scale", type=float, default=0.72, help="art height, fraction of screen height")
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--always-on", action="store_true")
    ap.add_argument("--render-test", metavar="PNG")
    args = ap.parse_args()
    lines, path = load_art(args.art)
    if args.render_test:
        render_test(lines, args.render_test, args)
    else:
        print(f"art: {path} ({len(lines[0])}x{len(lines)})", file=sys.stderr)
        run_gtk(lines, args)


if __name__ == "__main__":
    main()
