#!/usr/bin/env python3
"""
notify.py — the daily desktop nudge (README §4 Loop 3, P7). Reads /api/notify and posts a
state-bearing macOS notification. Content rotates by day (research: identical repeats decay)
and references what's actually due, not a bare "study now". On Sundays it points at the Coach.

Delivery: terminal-notifier (clickable → opens Today) if installed, else osascript. If the
app isn't running, posts a gentle "open Tuulai" fallback rather than nothing.

Run once to test:  .venv/bin/python tools/notify/notify.py
Scheduled by:      com.tuulai.notify LaunchAgent (afternoons).
"""
from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import sys
import urllib.request

API = "http://127.0.0.1:8642/api/notify"
URL = "http://127.0.0.1:8642/#/today"

# rotating openers — picked deterministically by day-of-year so repeats are rare
OPENERS = [
    "Time for a rep.", "Course check-in.", "A little every day.",
    "Your afternoon session.", "Keep the chain alive.", "Discrete math o'clock.",
    "Small and steady.",
]


def fetch() -> dict | None:
    try:
        with urllib.request.urlopen(API, timeout=4) as r:
            return json.loads(r.read())
    except Exception:
        return None


def compose(s: dict | None) -> tuple[str, str, str]:
    """Return (title, subtitle, message)."""
    day = datetime.date.today().timetuple().tm_yday
    opener = OPENERS[day % len(OPENERS)]
    if s is None:
        return ("Tuulai", opener, "Open Tuulai for today's session.")

    dq = s.get("days_until_quiz")
    quiz = s.get("quiz_target") or "the quiz"
    title = f"Tuulai · {quiz} in {dq}d" if dq is not None else "Tuulai"

    due_bits = []
    if s.get("retests_due"):
        due_bits.append(f"{s['retests_due']} error re-test(s)")
    if s.get("cards_due"):
        due_bits.append(f"{s['cards_due']} card(s)")
    if s.get("review_due"):
        due_bits.append(f"{s['review_due']} review problem(s)")

    lecture = " · Wooclap: answer today's question (random lecture = the point)" \
        if s.get("is_lecture_day") else ""

    if s.get("is_sunday"):
        subtitle = "Weekly review"
        message = "Your Coach report is ready — see how the week actually went and set the plan."
    elif s.get("active_today"):
        subtitle = f"{opener}  🔥 {s.get('streak', 0)}-day streak"
        message = ("Nice — you've practiced today. " +
                   (f"Still due: {', '.join(due_bits)}." if due_bits else "Optional: one more cold rep."))
    elif due_bits:
        subtitle = opener
        message = "Due now: " + ", ".join(due_bits) + "."
    else:
        subtitle = opener
        ns = s.get("new_skills", 0)
        message = (f"New material waiting ({ns} skill(s))." if ns else
                   "Nothing due — a timed mock would keep you sharp.")
    return (title, subtitle, message + lecture)


def post(title: str, subtitle: str, message: str) -> None:
    tn = shutil.which("terminal-notifier")
    if tn:
        subprocess.run([tn, "-title", title, "-subtitle", subtitle, "-message", message,
                        "-open", URL, "-group", "tuulai"], check=False)
        return
    # osascript fallback: pass strings as argv (robust for quotes, dashes, emoji) rather
    # than interpolating them into the script text.
    subprocess.run([
        "osascript",
        "-e", "on run argv",
        "-e", "display notification (item 1 of argv) with title (item 2 of argv) "
              "subtitle (item 3 of argv)",
        "-e", "end run",
        message, title, subtitle,
    ], check=False)


def main() -> int:
    s = fetch()
    title, subtitle, message = compose(s)
    post(title, subtitle, message)
    print(f"posted: [{title}] {subtitle} — {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
