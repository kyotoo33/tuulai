"""
mock.py — mock-quiz assembly + photo-grading orchestration (README §4 Loop 2, P6).

Assembly: pick a balanced, interleaved set from the coverage window, mirroring a real quiz
(≈5 problems, ~1 pt each, mixed kinds, closed-book). Grading: transcribe handwritten photos
(student confirms — kills the dominant OCR error), then grade per rubric line against the
reference solution. All LLM work goes through vision.py and degrades to manual self-grading.
"""
from __future__ import annotations

import json

from backend import vision

# Tune to your course: a typical quiz here is ~5-7 one-point problems in ~50 minutes.
TARGET_PROBLEMS = 5
MINUTES_PER_POINT = 10


def coverage_weeks(course: dict, quiz_target: str) -> set[int]:
    q = next((qz for qz in course["quizzes"] if qz["id"] == quiz_target), None)
    return set(q["covers_weeks"]) if q else {w["n"] for w in course["weeks"]}


def assemble(course, live_problems, skills_by_key, quiz_target, rng,
             weeks=None, n_target=None) -> dict:
    """Return {problem_keys, points, duration_min}. `rng` is a random.Random for reproducibility.

    weeks: explicit coverage set (e.g. a custom exam scope); falls back to the quiz's window.
    n_target: how many problems to assemble; defaults to a quiz-sized set.
    """
    weeks = set(weeks) if weeks else coverage_weeks(course, quiz_target)
    target_n = n_target or TARGET_PROBLEMS

    def prob_week(p):
        # a problem's home week is its PRIMARY (first) skill's week — secondaries don't
        # pull an induction problem into a Quiz-1 window, etc.
        for s in p["skills"]:
            if s in skills_by_key:
                return skills_by_key[s]["week"]
        return 99

    pool = [p for p in live_problems if prob_week(p) in weeks]
    if not pool:
        return {"problem_keys": [], "points": 0, "duration_min": 0}

    # group by primary skill; prefer covering distinct skills, then mix kinds
    by_skill: dict[str, list] = {}
    for p in pool:
        key = p["skills"][0] if p["skills"] else "?"
        by_skill.setdefault(key, []).append(p)
    for lst in by_skill.values():
        rng.shuffle(lst)

    chosen, used_skills, want_proof = [], set(), True
    skill_order = list(by_skill.keys())
    rng.shuffle(skill_order)
    # first pass: one problem per distinct skill, biasing toward at least one proof
    for sk in skill_order:
        if len(chosen) >= target_n:
            break
        cand = by_skill[sk]
        pick = None
        if want_proof:
            pick = next((p for p in cand if p["kind"] == "proof"), None)
        pick = pick or cand[0]
        if pick["key"] not in {c["key"] for c in chosen}:
            chosen.append(pick)
            used_skills.add(sk)
            if pick["kind"] == "proof":
                want_proof = False
    # second pass: fill remaining slots from any unused problems
    if len(chosen) < target_n:
        rest = [p for p in pool if p["key"] not in {c["key"] for c in chosen}]
        rng.shuffle(rest)
        chosen.extend(rest[: target_n - len(chosen)])

    # interleave so consecutive problems differ in subtopic where possible
    chosen = _interleave(chosen)
    points = sum(p["points"] for p in chosen)
    duration = max(30, round(points * MINUTES_PER_POINT / 5) * 5)
    return {"problem_keys": [p["key"] for p in chosen], "points": points, "duration_min": duration}


def _interleave(problems):
    if len(problems) < 2:
        return list(problems)
    remaining = list(problems)
    out = [remaining.pop(0)]
    while remaining:
        last = out[-1]["subtopic"]
        i = next((j for j, p in enumerate(remaining) if p["subtopic"] != last), 0)
        out.append(remaining.pop(i))
    return out


# ── transcription (photos -> per-problem text; student confirms) ─────────────

_TRANSCRIBE_SYS = (
    "You transcribe handwritten mathematics exam answers from photos into clean text with "
    "LaTeX for math ($...$). Transcribe faithfully — do NOT correct the student's errors, "
    "do NOT solve anything. Preserve what is written, including mistakes."
)


def transcribe(problems: list[dict], images: list[tuple[bytes, str]]) -> dict | None:
    """Return {problem_key: transcription} or None if no vision provider / failure."""
    if not vision.capability()["available"] or not images:
        return None
    manifest = "\n".join(
        f'- key "{p["key"]}" (problem {i+1}): {p["title"]}'
        for i, p in enumerate(problems))
    prompt = (
        "The attached photo(s) show a student's handwritten answers to these problems:\n"
        f"{manifest}\n\n"
        "The student may have labelled answers by problem number. Return STRICT JSON mapping "
        'each problem key to the transcription of that problem\'s handwritten work:\n'
        '{"transcriptions": {"<key>": "<verbatim transcription, LaTeX for math>", ...}}\n'
        "If a problem has no visible work, use an empty string for it."
    )
    out = vision.ask_json(_TRANSCRIBE_SYS, prompt, images, max_tokens=3000)
    if not isinstance(out, dict):
        return None
    tr = out.get("transcriptions", out)
    return {k: str(v) for k, v in tr.items()} if isinstance(tr, dict) else None


# ── grading (per rubric line, against reference solution) ────────────────────

_GRADE_SYS = (
    "You are a fair, rigorous grader for a discrete-math course. The instructor requires BOTH "
    "correct equations AND descriptive reasoning. Grade ONLY against the provided rubric and "
    "reference solution. Award partial credit per rubric line. Never invent credit not in the "
    "rubric. Be a second grader: flag anything you are unsure about rather than guessing."
)


def _rubric_lines(problem: dict) -> list[dict]:
    lines = []
    for part in problem.get("parts", []):
        for l in part.get("rubric", []):
            lines.append({"points": l["points"], "criterion": l["criterion"]})
    if not lines:
        lines = [{"points": problem["points"], "criterion":
                  "Correct, complete, rigorous solution with both equations and reasoning."}]
    return lines


def grade_one(problem: dict, transcription: str) -> dict | None:
    """Grade one problem's transcribed work. None if no provider / failure."""
    if not vision.capability()["available"]:
        return None
    rubric = _rubric_lines(problem)
    prompt = (
        f"PROBLEM:\n{problem['statement']}\n\n"
        + ("PARTS:\n" + "\n".join(
            f"({chr(65+i)}) [{pt.get('points')} pt] {pt.get('prompt','')}"
            for i, pt in enumerate(problem.get("parts", []))) + "\n\n"
           if problem.get("parts") else "")
        + f"REFERENCE SOLUTION:\n{problem.get('solution','')}\n\n"
        + "RUBRIC (grade against these, award partial credit per line):\n"
        + "\n".join(f"- [{l['points']} pt] {l['criterion']}" for l in rubric) + "\n\n"
        + f"STUDENT'S TRANSCRIBED WORK:\n{transcription or '(blank)'}\n\n"
        + "Return STRICT JSON: {\"score\": <number>, \"max\": " + str(problem["points"]) + ", "
        + "\"lines\": [{\"criterion\": \"...\", \"awarded\": <number>, \"max\": <number>}], "
        + "\"feedback\": \"<2-3 sentences: what earned/lost points>\", "
        + "\"miss_taxonomy\": \"concept|procedure|misread|slip|none\"}"
    )
    out = vision.ask_json(_GRADE_SYS, prompt, images=None, max_tokens=1200)
    if not isinstance(out, dict) or "score" not in out:
        return None
    out["max"] = problem["points"]
    return out


def grade_all(problems: list[dict], transcriptions: dict[str, str]) -> dict:
    """Grade every problem; aggregate. Problems that fail LLM grading are marked ungraded."""
    results = []
    total_score = total_max = 0.0
    for p in problems:
        tr = transcriptions.get(p["key"], "")
        g = grade_one(p, tr)
        if g is None:
            results.append({"key": p["key"], "title": p["title"], "graded": False,
                            "max": p["points"]})
            total_max += p["points"]
            continue
        results.append({"key": p["key"], "title": p["title"], "graded": True, **g})
        total_score += float(g.get("score", 0) or 0)
        total_max += p["points"]
    pct = round(100 * total_score / total_max) if total_max else 0
    return {"results": results, "score": round(total_score, 2), "max": round(total_max, 2),
            "pct": pct}
