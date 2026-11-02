#!/usr/bin/env python3
"""Generate the Mechanicus wallpaper as SVG, then render a 4K PNG.

Readability first: emblem is dim and pushed to the right, the left two thirds
stay dark and low-contrast so windows, icons and text sit on a calm surface.
"""
import math
import random
import sys

W, H = 3840, 2160
random.seed(40000)  # deterministic

VOID = "#0b0707"
VOID2 = "#170a0a"
RED = "#b81c1c"
RED_DIM = "#5a1010"
BRASS = "#c9a24a"
BRASS_DIM = "#6b5524"
BONE = "#e8dcc0"

out = []
a = out.append

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a(f"""<defs>
  <radialGradient id="bg" cx="72%" cy="50%" r="75%">
    <stop offset="0" stop-color="{VOID2}"/>
    <stop offset="0.55" stop-color="{VOID}"/>
    <stop offset="1" stop-color="#050303"/>
  </radialGradient>
  <radialGradient id="glow" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="{RED}" stop-opacity="0.28"/>
    <stop offset="1" stop-color="{RED}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="plate" width="120" height="120" patternUnits="userSpaceOnUse">
    <path d="M0 0H120V120" fill="none" stroke="{BRASS}" stroke-opacity="0.045" stroke-width="2"/>
    <circle cx="10" cy="10" r="3" fill="{BRASS}" fill-opacity="0.08"/>
  </pattern>
</defs>""")
a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
a(f'<rect width="{W}" height="{H}" fill="url(#plate)"/>')

# ---------- circuit traces (left side, very faint) ----------
def trace(x, y, steps, color, op, sw=3):
    d = f"M{x} {y}"
    for _ in range(steps):
        horiz = random.random() < 0.6
        step = random.choice([60, 90, 120, 180, 240])
        sign = random.choice([-1, 1])
        if horiz:
            x = max(40, min(W - 40, x + sign * step))
        else:
            y = max(40, min(H - 40, y + sign * step))
        d += f" L{x} {y}"
        if random.random() < 0.25:
            a(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="3"/>')
    a(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linejoin="round"/>')
    a(f'<circle cx="{x}" cy="{y}" r="9" fill="{color}" fill-opacity="{op}"/>')

for _ in range(70):
    trace(random.randint(80, 2600), random.randint(80, H - 80), random.randint(4, 9),
          random.choice([BRASS, RED]), round(random.uniform(0.07, 0.16), 3))

# ---------- binary cant columns ----------
def cant(x, y, n, op):
    bits = "".join(random.choice("01") for _ in range(n))
    for i, ch in enumerate(bits):
        a(f'<text x="{x}" y="{y + i * 30}" font-family="monospace" font-size="22" '
          f'fill="{BRASS}" fill-opacity="{op}">{ch}</text>')

for i in range(26):
    cant(60 + i * 100 + random.randint(-20, 20), random.randint(-200, 400), random.randint(30, 60),
         round(random.uniform(0.04, 0.10), 3))

# ---------- emblem ----------
CX, CY = 2780, 1060


def cog_path(cx, cy, r_root, r_tip, teeth, tooth_frac=0.5, taper=0.12):
    pts = []
    for i in range(teeth):
        base = 2 * math.pi * i / teeth
        span = 2 * math.pi / teeth
        t0 = base + span * (0.5 - tooth_frac / 2)
        t1 = base + span * (0.5 + tooth_frac / 2)
        for ang, r in ((base, r_root), (t0 - span * taper, r_root), (t0, r_tip), (t1, r_tip),
                       (t1 + span * taper, r_root)):
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


a(f'<circle cx="{CX}" cy="{CY}" r="980" fill="url(#glow)"/>')

# outer toothed ring (half red / half dim steel via two clipped copies)
a(f'<path d="{cog_path(CX, CY, 800, 880, 32)}" fill="{RED}" fill-opacity="0.50" stroke="{BRASS}" stroke-opacity="0.55" stroke-width="5"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="700" fill="{VOID}" stroke="{BRASS}" stroke-opacity="0.5" stroke-width="6"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="660" fill="none" stroke="{RED}" stroke-opacity="0.55" stroke-width="3" stroke-dasharray="6 14"/>')

# ring of notches
for i in range(72):
    ang = 2 * math.pi * i / 72
    r1, r2 = 590, 640 if i % 3 else 660
    a(f'<line x1="{CX + r1 * math.cos(ang):.1f}" y1="{CY + r1 * math.sin(ang):.1f}" '
      f'x2="{CX + r2 * math.cos(ang):.1f}" y2="{CY + r2 * math.sin(ang):.1f}" '
      f'stroke="{BRASS}" stroke-opacity="0.45" stroke-width="4"/>')

# inner cog
a(f'<path d="{cog_path(CX, CY, 520, 570, 20, 0.45)}" fill="{RED_DIM}" fill-opacity="0.65" stroke="{BRASS}" stroke-opacity="0.45" stroke-width="4"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="470" fill="{VOID2}" stroke="{BRASS}" stroke-opacity="0.35" stroke-width="3"/>')

# skull (centered on CX, CY)
sk = []
s = sk.append
s(f'<g fill="{BONE}" fill-opacity="0.78">')
s(f'<ellipse cx="{CX}" cy="{CY - 50}" rx="300" ry="290"/>')                  # cranium
s(f'<path d="M{CX - 190} {CY + 150} L{CX - 150} {CY + 330} Q{CX} {CY + 380} {CX + 150} {CY + 330} L{CX + 190} {CY + 150} Z"/>')  # jaw
s('</g>')
s(f'<g fill="{VOID}">')
s(f'<ellipse cx="{CX - 118}" cy="{CY - 20}" rx="82" ry="88"/>')                # eyes
s(f'<ellipse cx="{CX + 118}" cy="{CY - 20}" rx="82" ry="88"/>')
s(f'<path d="M{CX} {CY + 60} L{CX - 38} {CY + 150} L{CX + 38} {CY + 150} Z"/>')  # nose
for i in range(-3, 4):                                                          # teeth gaps
    s(f'<rect x="{CX + i * 44 - 3}" y="{CY + 230}" width="6" height="110"/>')
s(f'<rect x="{CX - 160}" y="{CY + 226}" width="320" height="6"/>')
s('</g>')
# Mechanicus half-face: red optic + brass plate on the right side
s(f'<circle cx="{CX + 118}" cy="{CY - 20}" r="34" fill="{RED}"/>')
s(f'<circle cx="{CX + 118}" cy="{CY - 20}" r="14" fill="#ff5a4a"/>')
s(f'<path d="M{CX + 20} {CY - 330} Q{CX + 300} {CY - 280} {CX + 300} {CY - 40} L{CX + 20} {CY - 40} Z" '
  f'fill="{BRASS_DIM}" fill-opacity="0.55" stroke="{BRASS}" stroke-opacity="0.6" stroke-width="3"/>')
for i in range(5):
    s(f'<line x1="{CX + 50 + i * 45}" y1="{CY - 300 + i * 18}" x2="{CX + 50 + i * 45}" y2="{CY - 70}" '
      f'stroke="{BRASS}" stroke-opacity="0.35" stroke-width="3"/>')
out.extend(sk)

# bolts around outer ring
for i in range(16):
    ang = 2 * math.pi * (i + 0.5) / 16
    bx, by = CX + 750 * math.cos(ang), CY + 750 * math.sin(ang)
    a(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="14" fill="{VOID}" stroke="{BRASS}" stroke-opacity="0.6" stroke-width="3"/>')
    a(f'<line x1="{bx - 8:.1f}" y1="{by:.1f}" x2="{bx + 8:.1f}" y2="{by:.1f}" stroke="{BRASS}" stroke-opacity="0.6" stroke-width="3"/>')

# ---------- inscription (bottom right, small, low-contrast) ----------
a(f'<text x="{CX}" y="{H - 150}" text-anchor="middle" font-family="serif" font-size="46" letter-spacing="14" '
  f'fill="{BRASS}" fill-opacity="0.45">OMNISSIAH · MACHINA · VIVIT</text>')
a(f'<text x="{CX}" y="{H - 95}" text-anchor="middle" font-family="monospace" font-size="24" letter-spacing="6" '
  f'fill="{BRASS}" fill-opacity="0.30">01001111 01001101 01001110 01001001</text>')

# vignette frame
a(f'<rect x="30" y="30" width="{W - 60}" height="{H - 60}" fill="none" stroke="{BRASS}" stroke-opacity="0.12" stroke-width="3"/>')
for (x, y) in [(30, 30), (W - 30, 30), (30, H - 30), (W - 30, H - 30)]:
    a(f'<circle cx="{x}" cy="{y}" r="16" fill="{VOID}" stroke="{BRASS}" stroke-opacity="0.35" stroke-width="3"/>')

a("</svg>")

svg = "\n".join(out)
open("mechanicus.svg", "w", encoding="utf-8").write(svg)
print("wrote mechanicus.svg", len(svg) // 1024, "KB")

if "--no-png" not in sys.argv:
    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode(), write_to="mechanicus-3840x2160.png",
                     output_width=W, output_height=H)
    print("wrote mechanicus-3840x2160.png")
