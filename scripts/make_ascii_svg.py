"""
make_ascii_svg.py
Downsample source-prepped.png to a character grid, map brightness to a
density ramp, and emit a monochrome self-typing SVG (each row wipes in
left-to-right, staggered top to bottom, freezes at the end - no loop).
"""
import sys
from PIL import Image

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)

COLS = 100
ROWS = 53
FONT_SIZE = 7
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
FILL = "#8b949e"          # single monochrome fill, no rainbow
BG = "transparent"
STAGGER = 0.045            # seconds between each row starting
ROW_DURATION = 0.55        # seconds for a row's wipe

def brightness_to_char(v):
    # v: 0 (black) .. 255 (white). White background -> maps to space (ramp[0]).
    idx = int((255 - v) / 255 * (len(RAMP) - 1))
    return RAMP[max(0, min(idx, len(RAMP) - 1))]

def build_grid(img_path):
    im = Image.open(img_path).convert("L")
    im = im.resize((COLS, ROWS), Image.LANCZOS)
    px = im.load()
    grid = []
    for y in range(ROWS):
        row = "".join(brightness_to_char(px[x, y]) for x in range(COLS))
        grid.append(row)
    return grid

def escape(c):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(c, c)

def make_svg(grid, out_path="avi-ascii.svg"):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H + 10

    rows_svg = []
    total_delay = 0.0
    for i, row in enumerate(grid):
        text = "".join(escape(c) for c in row)
        y = (i + 1) * CHAR_H
        clip_id = f"clip{i}"
        delay = i * STAGGER

        # clip-path rect that wipes from 0 width to full width
        rows_svg.append(f"""
  <clipPath id="{clip_id}">
    <rect x="0" y="{y - CHAR_H}" height="{CHAR_H + 2}" width="0">
      <animate attributeName="width" from="0" to="{width}"
        begin="{delay:.3f}s" dur="{ROW_DURATION}s"
        fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    </rect>
  </clipPath>""")

        rows_svg.append(
            f'  <text x="0" y="{y}" clip-path="url(#{clip_id})" '
            f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}" '
            f'fill="{FILL}" xml:space="preserve">{text}</text>'
        )
        total_delay = delay + ROW_DURATION

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}"
     viewBox="0 0 {width:.0f} {height:.0f}">
  <style>
    text {{ letter-spacing: 0px; }}
  </style>
{''.join(rows_svg)}
</svg>
"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}  ({COLS}x{ROWS} chars, ~{total_delay:.1f}s to fully print)")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "avi-ascii.svg"
    grid = build_grid(src)
    make_svg(grid, out)
