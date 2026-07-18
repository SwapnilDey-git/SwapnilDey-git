"""
make_info_card.py
Hand-authored neofetch-style SVG panel: a title bar, then colored
key/value rows that fade + slide in with a short stagger.
STATIC=1 env var emits a frozen (fully-visible) frame for local previews.
"""
import os

WIDTH = 490
ROW_H = 30
PAD_TOP = 58
FIELD_COL = "#79c0ff"     # neofetch-blue keys
VALUE_COL = "#c9d1d9"     # light gray values
ACCENT = "#39d353"        # green accent (matches the heatmap's brightest tone)
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"

STATIC = os.environ.get("STATIC", "0") == "1"

FIELDS = [
    ("OS", "SwapnilOS 27.0 (KIIT edition)"),
    ("Now", "AI Engineer @ Metaborong"),
    ("Prev", "Web Dev Intern @ Creative Creature"),
    ("Stack", "Python / Flutter / Django / Firebase / TF"),
    ("Highlights", "Pragati \u00b7 LeetCode 250+ \u00b7 Top 2% CTF"),
]

def escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def make_svg(out_path="info-card.svg"):
    height = PAD_TOP + ROW_H * len(FIELDS) + 24

    rows = []
    for i, (key, val) in enumerate(FIELDS):
        y = PAD_TOP + i * ROW_H
        delay = 0.15 + i * 0.18
        dur = 0.5
        if STATIC:
            key_attrs = 'opacity="1"'
            val_attrs = 'opacity="1"'
            key_anim = ""
            val_anim = ""
        else:
            key_attrs = 'opacity="0"'
            val_attrs = 'opacity="0"'
            key_anim = (
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="{dur}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="-14 0" '
                f'to="0 0" begin="{delay:.2f}s" dur="{dur}s" fill="freeze" '
                f'calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
            )
            v_delay = delay + 0.05
            val_anim = (
                f'<animate attributeName="opacity" from="0" to="1" begin="{v_delay:.2f}s" '
                f'dur="{dur}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="-14 0" '
                f'to="0 0" begin="{v_delay:.2f}s" dur="{dur}s" fill="freeze" '
                f'calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
            )

        rows.append(f'''
  <g>
    <text x="28" y="{y}" font-family="Consolas, Menlo, monospace" font-size="14"
      font-weight="700" fill="{FIELD_COL}" {key_attrs}>{escape(key)}{key_anim}</text>
    <text x="130" y="{y}" font-family="Consolas, Menlo, monospace" font-size="14"
      fill="{VALUE_COL}" {val_attrs}>{escape(val)}{val_anim}</text>
  </g>''')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}"
     viewBox="0 0 {WIDTH} {height}">
  <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0" y="0" width="{WIDTH}" height="34" rx="8" fill="{TITLEBAR}"/>
  <rect x="0" y="24" width="{WIDTH}" height="10" fill="{TITLEBAR}"/>
  <circle cx="20" cy="17" r="5" fill="#ff5f56"/>
  <circle cx="38" cy="17" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="17" r="5" fill="#27c93f"/>
  <text x="{WIDTH/2}" y="21" text-anchor="middle" font-family="Consolas, Menlo, monospace"
    font-size="12" fill="#8b949e">swapnil@github: neofetch</text>

  <text x="28" y="{PAD_TOP - 20}" font-family="Consolas, Menlo, monospace" font-size="16"
    font-weight="700" fill="{ACCENT}">swapnil@github</text>
  <line x1="28" y1="{PAD_TOP - 12}" x2="{WIDTH - 28}" y2="{PAD_TOP - 12}" stroke="{BORDER}"/>
{''.join(rows)}
</svg>
'''
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}  static={STATIC}")

if __name__ == "__main__":
    make_svg()
