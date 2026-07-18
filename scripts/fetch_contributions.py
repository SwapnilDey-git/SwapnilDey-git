"""
fetch_contributions.py
GitHub serves the contribution calendar as public HTML (no auth, no token)
at https://github.com/users/<username>/contributions - the same fragment
the profile page itself uses. Scrape it and write data/contributions.json
with raw days plus derived stats.
"""
import json
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "SwapnilDey-git"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = "data/contributions.json"


def fetch(username=USERNAME):
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


import re

COUNT_RE = re.compile(r"^(No|\d+)\s+contributions?\s+on", re.IGNORECASE)


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # each day is a <td class="ContributionCalendar-day" id="..." data-date
    # data-level>. Its contribution count lives in a sibling <tool-tip for="id">
    # reading "N contributions on <Month> <Day>." (or "No contributions on ...").
    cells = soup.select("td.ContributionCalendar-day")

    tooltip_by_for = {}
    for tt in soup.find_all("tool-tip"):
        for_id = tt.get("for")
        if for_id:
            tooltip_by_for[for_id] = tt.get_text(strip=True)

    for c in cells:
        date = c.get("data-date")
        level = c.get("data-level")
        cell_id = c.get("id")
        if date is None:
            continue
        try:
            level = int(level) if level is not None else 0
        except ValueError:
            level = 0

        count = 0
        tip_text = tooltip_by_for.get(cell_id, "")
        m = COUNT_RE.match(tip_text)
        if m:
            token = m.group(1)
            count = 0 if token.lower() == "no" else int(token)

        days.append({"date": date, "level": level, "count": count})

    return days


def derive_stats(days):
    days_sorted = sorted(days, key=lambda d: d["date"])
    counts = [d["count"] or 0 for d in days_sorted]
    total = sum(counts)

    # current streak: consecutive days with count > 0, ending at most recent day
    current_streak = 0
    for d in reversed(days_sorted):
        if (d["count"] or 0) > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest = cur = 0
    for d in days_sorted:
        if (d["count"] or 0) > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    best_day = max(days_sorted, key=lambda d: d["count"] or 0, default=None)

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest,
        "best_day": best_day,
        "generated_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() ,
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    html = fetch(username)
    days = parse(html)

    if not days:
        print("warning: no contribution cells parsed - GitHub markup may have "
              "changed, writing empty structure", file=sys.stderr)

    stats = derive_stats(days) if days else {
        "total_last_year": 0, "current_streak": 0,
        "longest_streak": 0, "best_day": None,
        "generated_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() ,
    }

    out = {"username": username, "days": days, "stats": stats}
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print(f"wrote {OUT_PATH}  days={len(days)}  total={stats['total_last_year']}")


if __name__ == "__main__":
    main()
