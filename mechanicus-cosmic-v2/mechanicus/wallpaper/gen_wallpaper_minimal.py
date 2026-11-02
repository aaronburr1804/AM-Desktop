#!/usr/bin/env python3
"""Minimal near-black wallpaper with faint circuit tracings (no emblem).
The ASCII widget supplies the focal point; this is just a quiet surface."""
import random
import cairosvg

W, H = 3840, 2160
random.seed(40001)
BRASS, RED = "#c9a24a", "#b81c1c"
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#050404"/>']


def trace(x, y, steps, color, op):
    d = f"M{x} {y}"
    for _ in range(steps):
        step = random.choice([80, 120, 180, 260])
        s = random.choice([-1, 1])
        if random.random() < 0.6:
            x = max(60, min(W - 60, x + s * step))
        else:
            y = max(60, min(H - 60, y + s * step))
        d += f" L{x} {y}"
    o.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="2.5" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="2.5"/>')


# sparse, edge-biased traces so the middle stays empty for windows
for _ in range(34):
    side = random.choice(["l", "r", "t", "b"])
    x = random.randint(60, 700) if side == "l" else random.randint(W - 700, W - 60) if side == "r" else random.randint(60, W - 60)
    y = random.randint(60, 500) if side == "t" else random.randint(H - 500, H - 60) if side == "b" else random.randint(60, H - 60)
    trace(x, y, random.randint(3, 7), random.choice([BRASS, BRASS, RED]), round(random.uniform(0.07, 0.13), 3))
o.append("</svg>")
svg = "\n".join(o)
open("mechanicus-minimal.svg", "w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(), write_to="mechanicus-minimal-3840x2160.png", output_width=W, output_height=H)
print("ok")
