"""
coach.py — the weekly coach (README §4 Loop 3). Reads the ledger and produces the report the
research says matters: at-risk skills vs the Quiz Radar, a calibration audit (confident-wrong
first — biggest quiz risk AND most fixable, per hypercorrection), a hint-velocity self-honesty
check, paper-vs-typed modality, and the coming week's plan. Fresh-start framing every time.

Narrative is written by a text LLM when available (via vision.ask, images=None) and degrades
to a templated summary. All analysis is deterministic and testable.
"""
from __future__ import annotations

from datetime import date, timedelta

from backend import scheduler as sch
from backend import vision


def _pct(n, d):
    return round(100 * n / d) if d else 0


def calibration(attempts) -> dict:
    """Confidence-vs-correctness. Confident-wrong ('sure' but not correct) is the danger set."""
    buckets = {c: {"n": 0, "correct": 0} for c in ("sure", "shaky", "guess")}
    confident_wrong, underconfident = [], []
    for a in attempts:
        conf = a["confidence"]
        if conf not in buckets:
            continue
        ok = a["result"] == "correct"
        buckets[conf]["n"] += 1
        buckets[conf]["correct"] += 1 if ok else 0
        if conf == "sure" and not ok:
            confident_wrong.append(a["problem_key"])
        if conf == "guess" and ok:
            underconfident.append(a["problem_key"])
    # a simple calibration read: accuracy should rise sure > shaky > guess
    rates = {c: _pct(b["correct"], b["n"]) for c, b in buckets.items()}
    return {
        "buckets": {c: {"n": b["n"], "accuracy": rates[c]} for c, b in buckets.items()},
        "confident_wrong": confident_wrong,
        "underconfident": underconfident,
        "n_graded": sum(b["n"] for b in buckets.values()),
    }


def hint_velocity(attempts) -> dict:
    """Self-honesty: how often help was leaned on hard (hints_used >= 2 before solving)."""
    n = len(attempts)
    leaned = [a["problem_key"] for a in attempts if a["hints_used"] >= 2]
    cold = sum(1 for a in attempts if a["hints_used"] == 0)
    return {"attempts": n, "hint_heavy": len(leaned), "hint_heavy_keys": leaned,
            "cold_rate": _pct(cold, n)}


def modality(attempts) -> dict:
    paper = sum(1 for a in attempts if a["mode"] == "paper")
    typed = sum(1 for a in attempts if a["mode"] == "typed")
    return {"paper": paper, "typed": typed, "paper_rate": _pct(paper, paper + typed)}


def build_report(course, skills, skills_by_key, problems_by_key, db, today: date) -> dict:
    week_ago = (today - timedelta(days=7)).isoformat()
    week_attempts = db.graded_attempts(since_iso=week_ago)
    all_attempts = db.graded_attempts()
    skill_state = db.all_skill_state()

    radar = sch.quiz_radar(course, skills, skill_state, today)
    at_risk = [s for s in radar.get("skills", []) if s["readiness"] in ("shaky", "untouched")]

    cal = calibration(all_attempts)
    hv = hint_velocity(week_attempts)
    mod = modality(week_attempts)

    open_errs = db.open_errors()
    err_by_tax: dict[str, int] = {}
    for e in open_errs:
        err_by_tax[e["taxonomy"]] = err_by_tax.get(e["taxonomy"], 0) + 1
    due_retests = [dict(e) for e in open_errs
                   if not e["retest_due"] or e["retest_due"][:10] <= today.isoformat()]

    mocks = [dict(m) for m in db.mock_history(limit=5)]

    # coming-week plan: at-risk skills to drill + due re-tests, capped
    plan = {
        "drill_skills": [{"key": s["key"], "name": _skill_name(skills_by_key, s["key"]),
                          "readiness": s["readiness"]} for s in at_risk[:6]],
        "retests_due": len(due_retests),
        "days_until_quiz": radar.get("days_until"),
    }

    report = {
        "generated": today.isoformat(),
        "week_active_days": len({a["at"][:10] for a in week_attempts}),
        "streak": db.streak(),
        "quiz": {"target": radar.get("quiz"), "title": radar.get("title"),
                 "days_until": radar.get("days_until"),
                 "solid": radar.get("solid", 0), "total": radar.get("total", 0)},
        "at_risk": [{"key": s["key"], "name": _skill_name(skills_by_key, s["key"]),
                     "readiness": s["readiness"]} for s in at_risk],
        "calibration": {
            **cal,
            "confident_wrong_titles": [_title(problems_by_key, k) for k in cal["confident_wrong"][:8]],
        },
        "hint_velocity": hv,
        "modality": mod,
        "errors": {"open": len(open_errs), "by_taxonomy": err_by_tax, "due_now": len(due_retests)},
        "mocks": mocks,
        "plan": plan,
    }
    report["narrative"] = _narrative(report) or _templated_narrative(report)
    return report


def _skill_name(skills_by_key, key):
    return skills_by_key.get(key, {}).get("name", key)


def _title(problems_by_key, key):
    return problems_by_key.get(key, {}).get("title", key.split(".")[-1])


def _narrative(r: dict) -> str | None:
    """LLM-written, honest, encouraging coach note. None if no provider."""
    cw = r["calibration"]["confident_wrong"]
    facts = (
        f"Days active this week: {r['week_active_days']}/7. Streak: {r['streak']}. "
        f"Quiz {r['quiz']['target']} in {r['quiz']['days_until']} days; "
        f"{r['quiz']['solid']}/{r['quiz']['total']} skills solid. "
        f"At-risk skills: {[s['name'] for s in r['at_risk'][:5]]}. "
        f"Confident-wrong count: {len(cw)}. "
        f"Cold-solve rate: {r['hint_velocity']['cold_rate']}%. "
        f"Paper practice rate: {r['modality']['paper_rate']}%. "
        f"Open error-log items: {r['errors']['open']} ({r['errors']['due_now']} due now)."
    )
    prompt = (
        "You are a calm, honest study coach for a hard discrete-math course graded by "
        "closed-book handwritten quizzes. Write a SHORT weekly note (4-6 sentences) to the "
        "student. Open with a fresh-start framing for the week ahead. Name the ONE thing "
        "that most needs attention (usually confident-wrong items or an at-risk skill), and "
        "one concrete action. Be direct, not cheerful; never invent facts beyond these:\n\n"
        f"{facts}"
    )
    return vision.ask("You are a study coach. Be concise, honest, specific.", prompt,
                      images=None, max_tokens=400)


def _templated_narrative(r: dict) -> str:
    cw = len(r["calibration"]["confident_wrong"])
    q = r["quiz"]
    lead = f"New week. Quiz {q['target']} is {q['days_until']} days out — {q['solid']}/{q['total']} skills solid."
    if cw:
        focus = (f" Your sharpest risk is {cw} confident-but-wrong item(s): you felt sure and "
                 f"missed. Re-derive those cold first — high-confidence errors are the most fixable.")
    elif r["at_risk"]:
        focus = f" Focus on the at-risk skills: {', '.join(s['name'] for s in r['at_risk'][:3])}."
    else:
        focus = " Coverage looks solid — keep the cold-retrieval reps up and do a timed mock."
    tail = (f" You practiced on {r['week_active_days']} day(s); paper rate {r['modality']['paper_rate']}%. "
            f"{r['errors']['due_now']} error-log re-test(s) are due.")
    return lead + focus + tail
