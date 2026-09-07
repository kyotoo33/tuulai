"""
scheduler.py — the retention engine (README §8). Pure functions over content + state.

Three mechanisms, per the research bible:
  1. Successive relearning (research 03 #13): a skill is quiz-ready at >=3 successful cold
     retrievals on DISTINCT days, the last within 4 days of the quiz. Within a session one
     success banks the rep; no same-day grinding.
  2. FIRe-lite (research 02/03 #8): a hint-free solve gives a full touch to the problem's
     primary skill and 0.5 to each encompassed skill, so hard mixed problems discharge
     review debt. Hints used -> no implicit credit. A miss demotes only the diagnosed skill.
  3. Interleaving (research 03 #14): daily sets mix >=3 topics, unlabeled, current + prior.

Quiz targeting: everything aims at the next open quiz window; the Quiz Radar is coverage
skills x readiness. Dates are injectable so this is unit-testable.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

# Readiness thresholds
CRITERION_DAYS = 3          # distinct-day cold successes to be "solid"
LAST_TOUCH_WINDOW = 4       # last success must be within N days of the quiz
NEW_SKILLS_PER_DAY = 2      # rate limit (Execute Program): cap new intake
DEFAULT_QUIZ_WEEKDAY = 1    # Tuesday (0=Mon) — safe assumption until Ed confirms (README §14)


def _d(iso: str) -> date:
    return date.fromisoformat(iso[:10])


# ── which quiz are we aiming at ──────────────────────────────────────────────

def quiz_date(course: dict, quiz: dict) -> date:
    """Announced date if set, else the assumed weekday of the quiz's academic week."""
    if quiz.get("date"):
        return _d(quiz["date"])
    wk = next((w for w in course["weeks"] if w["n"] == quiz["week"]), None)
    if wk is not None:
        start = _d(wk["start"])
    else:
        # week not explicitly listed: derive from week-1 start + 7 days per week
        w1 = min(course["weeks"], key=lambda w: w["n"])
        start = _d(w1["start"]) + timedelta(days=7 * (quiz["week"] - w1["n"]))
    return start + timedelta(days=DEFAULT_QUIZ_WEEKDAY)


def next_quiz(course: dict, today: date) -> dict | None:
    upcoming = [(quiz_date(course, q), q) for q in course["quizzes"]]
    upcoming = [(d, q) for d, q in upcoming if d >= today]
    if not upcoming:
        return None
    upcoming.sort(key=lambda x: x[0])
    return upcoming[0][1]


def days_until_quiz(course: dict, today: date) -> int | None:
    q = next_quiz(course, today)
    return (quiz_date(course, q) - today).days if q else None


# ── skill readiness (successive relearning) ──────────────────────────────────

def readiness(skill_state_row, quiz_dt: date | None, today: date) -> str:
    """Return one of: untouched | shaky | warming | solid."""
    if skill_state_row is None:
        return "untouched"
    days = skill_state_row["distinct_days"]
    demoted = skill_state_row["demoted_at"] is not None and not _cleared_since_demote(skill_state_row)
    last = skill_state_row["last_touch"]
    if days == 0:
        return "untouched"
    if demoted:
        return "shaky"
    if days >= CRITERION_DAYS:
        # solid only if the last touch is recent enough to still be warm for the quiz
        if quiz_dt and last:
            gap = (quiz_dt - _d(last)).days
            return "solid" if gap <= max(LAST_TOUCH_WINDOW, 7) else "warming"
        return "solid"
    return "warming"


def _cleared_since_demote(row) -> bool:
    # a later successful touch clears the demotion flag conceptually; we treat a demote as
    # sticky until distinct_days advances past the pre-demote count. Simplified: if last_touch
    # is after demoted_at, the demotion has been worked on.
    if not row["demoted_at"] or not row["last_touch"]:
        return False
    return row["last_touch"] > row["demoted_at"]


# ── FIRe-lite: apply an attempt's credit to skills ───────────────────────────

def credit_for_attempt(problem: dict, skills_by_key: dict, result: str, cold: bool) -> dict:
    """
    Return {skill_key: delta_touches}. Positive credit only on a cold correct solve.
    Full credit to primary (first listed) skill, 0.5 to encompassed skills. A wrong/partial
    result yields negative credit (demotion) for the primary skill only.
    """
    if not problem["skills"]:
        return {}
    primary = problem["skills"][0]
    deltas: dict[str, float] = {}
    if result == "correct" and cold:
        deltas[primary] = 1.0
        # secondary listed skills get partial
        for sk in problem["skills"][1:]:
            deltas[sk] = deltas.get(sk, 0) + 0.5
        # encompassed skills (from the graph) get FIRe implicit credit
        enc = skills_by_key.get(primary, {}).get("encompasses", [])
        for sk in enc:
            deltas[sk] = deltas.get(sk, 0) + 0.5
    elif result in ("wrong", "partial"):
        deltas[primary] = -1.0 if result == "wrong" else -0.5
    return deltas


def next_due(result: str, cold: bool, today: date) -> str:
    """Successive-relearning spacing: correct -> 2-day gap; else -> tomorrow."""
    gap = 2 if (result == "correct" and cold) else 1
    return (today + timedelta(days=gap)).isoformat()


# ── interleaving ─────────────────────────────────────────────────────────────

def interleave(problems: list[dict]) -> list[dict]:
    """Reorder so no two consecutive problems share a topic, where possible (research #14)."""
    if len(problems) < 2:
        return list(problems)
    remaining = list(problems)
    out = [remaining.pop(0)]
    while remaining:
        last_topic = out[-1]["topic"]
        pick = next((i for i, p in enumerate(remaining) if p["topic"] != last_topic), 0)
        out.append(remaining.pop(pick))
    return out


# ── the Today plan ───────────────────────────────────────────────────────────

def due_skills(course: dict, skills: list[dict], state: dict, today: date) -> list[dict]:
    """Skills in the current quiz window that are due for a retrieval touch."""
    q = next_quiz(course, today)
    weeks = set(q["covers_weeks"]) if q else {w["n"] for w in course["weeks"]}
    due = []
    for sk in skills:
        if sk["week"] not in weeks:
            continue
        row = state.get(sk["key"])
        if row is None:
            continue  # untouched skills surface via "new content", not review
        d = row["due"]
        if d is None or _d(d) <= today:
            due.append(sk)
    return due


def build_today(course, skills, live_problems, card_rows, skill_state, today: date) -> dict:
    """
    Assemble the day's session (README §4, Loop 1). Order is enforced:
    due cards -> due skill-review problems (interleaved) -> new content.
    """
    skills_by_key = {s["key"]: s for s in skills}
    q = next_quiz(course, today)
    quiz_dt = quiz_date(course, q) if q else None

    # 1. due cards (already filtered by caller)
    cards = [dict(r) for r in card_rows]

    # 2. due skill-review problems, interleaved
    dsk = due_skills(course, skills, skill_state, today)
    due_skill_keys = {s["key"] for s in dsk}
    review_problems = []
    seen = set()
    for p in live_problems:
        if p["key"] in seen:
            continue
        if any(sk in due_skill_keys for sk in p["skills"]):
            review_problems.append(p)
            seen.add(p["key"])
    review_problems = interleave(review_problems)

    # 3. new content: untouched skills in the quiz window, rate-limited
    weeks = set(q["covers_weeks"]) if q else {w["n"] for w in course["weeks"]}
    new_skills = [
        s for s in skills
        if s["week"] in weeks and skill_state.get(s["key"]) is None
    ][:NEW_SKILLS_PER_DAY]

    return {
        "quiz_target": q["id"] if q else None,
        "quiz_title": q["title"] if q else None,
        "days_until_quiz": (quiz_dt - today).days if quiz_dt else None,
        "cards_due": cards,
        "review_problems": [_thin(p) for p in review_problems],
        "new_skills": [{"key": s["key"], "name": s["name"], "first_contact": s.get("first_contact")}
                       for s in new_skills],
        "order": ["cards", "review", "new"],
    }


def _thin(p: dict) -> dict:
    return {"key": p["key"], "title": p["title"], "topic": p["topic"],
            "kind": p["kind"], "est_minutes": p["est_minutes"], "points": p["points"]}


# ── Quiz Radar ───────────────────────────────────────────────────────────────

def quiz_radar(course, skills, skill_state, today: date) -> dict:
    q = next_quiz(course, today)
    if not q:
        return {"quiz": None, "skills": []}
    quiz_dt = quiz_date(course, q)
    weeks = set(q["covers_weeks"])
    rows = []
    for sk in skills:
        if sk["week"] not in weeks:
            continue
        st = readiness(skill_state.get(sk["key"]), quiz_dt, today)
        rows.append({"key": sk["key"], "name": sk["name"], "week": sk["week"], "readiness": st})
    order = {"shaky": 0, "untouched": 1, "warming": 2, "solid": 3}
    rows.sort(key=lambda r: order[r["readiness"]])
    return {
        "quiz": q["id"],
        "title": q["title"],
        "date": quiz_dt.isoformat(),
        "days_until": (quiz_dt - today).days,
        "covers_weeks": sorted(weeks),
        "skills": rows,
        "solid": sum(1 for r in rows if r["readiness"] == "solid"),
        "total": len(rows),
    }
