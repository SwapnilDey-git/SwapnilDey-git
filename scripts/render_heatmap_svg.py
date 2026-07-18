"""
render_heatmap_svg.py
Draw data/contributions.json as the classic 53-week x 7-day grid of
rounded boxes. Reveal once with a diagonal, line-after-line slide-down
(CSS keyframes that play on load, then freeze - no looping "glow").
"""
import json
import os
from datetime import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#           none ->                                        brightest (level 5, neon top end)

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 30
TOP_PAD = 34
BOTTOM_PAD = 46

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

STATIC = os.environ.get("STATIC", "0") == "1"


def load(path="data/contributions.json"):
    with open(path) as f:
        return json.load(f)


def to_weeks(days):
    """days are already in GitHub's column-major order: one entry per
    (week, weekday) cell as it walked the grid top-to-bottom, left-to-right.
    Group every 7 into a week column."""
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    return weeks


def month_labels(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        first_valid = next((d for d in week if d.get("date")), None)
        if not first_valid:
            continue
        month = int(first_valid["date"][5:7])
        if month != last_month:
            labels.append((wi, MONTH_ABBR[month - 1]))
            last_month = month
    return labels


def make_svg(data, out_path="contrib-heatmap.svg"):
    days = data["days"]
    stats = data["stats"]
    weeks = to_weeks(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * CELL + 10
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    boxes = []
    delay_step = 0.012  # per-cell stagger, diagonal via (week+day) index
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if not day.get("date"):
                continue
            level = min(day.get("level", 0), 5)
            color = PALETTE[level]
            x = LEFT_PAD + wi * CELL
            y = TOP_PAD + di * CELL
            diag = wi + di
            delay = diag * delay_step

            if STATIC:
                anim = ""
                y_start = y
                opacity = 1
            else:
                y_start = y - 6
                opacity = 0
                anim = (
                    f'<animate attributeName="y" from="{y_start}" to="{y}" '
                    f'begin="{delay:.3f}s" dur="0.35s" fill="freeze" '
                    f'calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                    f'<animate attributeName="opacity" from="0" to="1" '
                    f'begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
                )

            title = day["date"]
            boxes.append(
                f'<rect x="{x}" y="{y_start}" width="{BOX}" height="{BOX}" rx="2.5" '
                f'fill="{color}" opacity="{opacity}">{anim}'
                f'<title>{title}: {day.get("count", 0)} contributions</title></rect>'
            )

    labels = month_labels(weeks)
    label_svgs = [
        f'<text x="{LEFT_PAD + wi * CELL}" y="{TOP_PAD - 10}" '
        f'font-family="Consolas, Menlo, monospace" font-size="10" fill="#8b949e">{m}</text>'
        for wi, m in labels
    ]

    dow_labels = []
    for di, lab in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = TOP_PAD + di * CELL + BOX - 2
        dow_labels.append(
            f'<text x="0" y="{y}" font-family="Consolas, Menlo, monospace" '
            f'font-size="9" fill="#8b949e">{lab}</text>'
        )

    legend_x = LEFT_PAD
    legend_y = height - 22
    legend_boxes = []
    for i, c in enumerate(PALETTE):
        legend_boxes.append(
            f'<rect x="{legend_x + 32 + i * (BOX + 3)}" y="{legend_y}" '
            f'width="{BOX}" height="{BOX}" rx="2.5" fill="{c}"/>'
        )

    total = stats.get("total_last_year", 0)
    streak = stats.get("current_streak", 0)
    footer = (
        f'<text x="{legend_x}" y="{legend_y + BOX - 1}" '
        f'font-family="Consolas, Menlo, monospace" font-size="10" fill="#8b949e">Less</text>'
        f'<text x="{legend_x + 32 + len(PALETTE) * (BOX + 3) + 6}" y="{legend_y + BOX - 1}" '
        f'font-family="Consolas, Menlo, monospace" font-size="10" fill="#8b949e">More</text>'
        f'<text x="{width - 10}" y="{legend_y + BOX - 1}" text-anchor="end" '
        f'font-family="Consolas, Menlo, monospace" font-size="11" fill="#c9d1d9">'
        f'{total} contributions in the last year &#183; current streak {streak}d</text>'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
{''.join(label_svgs)}
{''.join(dow_labels)}
{''.join(boxes)}
{''.join(legend_boxes)}
{footer}
</svg>
'''
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}  weeks={n_weeks} total={total}")


if __name__ == "__main__":
    data = load()
    make_svg(data)
