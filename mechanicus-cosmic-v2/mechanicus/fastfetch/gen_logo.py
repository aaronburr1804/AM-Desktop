#!/usr/bin/env python3
"""Rasterise a cog + skull into a fastfetch logo ($1 = cog colour, $2 = skull colour)."""
import math
import re

W, H = 44, 22            # cells; a terminal cell is ~2x taller than wide
CX, CY = (W - 1) / 2, (H - 1) / 2
R_OUT, R_IN, R_HUB = 21.0, 17.0, 14.5
TEETH = 16


def cell(x, y):
    dx, dy = x - CX, (y - CY) * 2.0       # undo the 2:1 aspect
    r = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)

    # cog ring with teeth
    tooth = math.cos(ang * TEETH) > 0.15
    outer = R_OUT if tooth else R_IN + 1.0
    if 14.5 <= r <= outer:
        return 1
    if r < 14.5 and r > 12.5:
        return 0

    # skull (dy grows downward)
    cran = (dx / 9.5) ** 2 + ((dy + 2.5) / 8.5) ** 2 <= 1
    jaw = abs(dx) <= 5.4 - max(0.0, dy - 7.0) * 0.6 and 3.0 <= dy <= 9.5
    if not (cran or jaw):
        return 0
    eye = ((abs(dx) - 4.0) / 2.8) ** 2 + ((dy + 1.0) / 2.8) ** 2 <= 1
    nose = abs(dx) <= (dy - 2.2) * 0.5 and 2.2 <= dy <= 5.4
    teeth_gap = 7.0 <= dy <= 9.5 and int(round(dx)) % 3 == 0 and abs(dx) <= 4
    if eye or nose or teeth_gap:
        return 0
    return 2


rows = []
for y in range(H):
    line, cur = "", None
    for x in range(W):
        c = cell(x, y)
        ch, col = (" ", None) if c == 0 else ("█", c)
        if col and col != cur:
            line += f"${col}"
            cur = col
        line += ch
    rows.append(line.rstrip())

while rows and not rows[0]:
    rows.pop(0)
while rows and not rows[-1]:
    rows.pop()

with open("logo.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(rows) + "\n")

for r in rows:
    print(re.sub(r"\$\d", "", r))
