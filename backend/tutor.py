"""
tutor.py — the hint ladder, grading, and coach. Every function is None-degradable: with no
ANTHROPIC_API_KEY the app falls back to authored/structural help and never fails a core flow
(Atlas invariant 12). The ladder is a server-side gate, not a prompt suggestion (README §9).

Ladder (README §9):
    rung 0  restate the problem in your own words
    rung 1  probing question (Socratic)
    rung 2  targeted concept hint
    rung 3  worked ANALOGOUS problem (same structure, different surface)
    rung 4  full solution — UNLOCKS ONLY after a logged attempt exists, and enqueues a
            cold redo (handled by the API on attempt submit)
"""
from __future__ import annotations

import json
import os
import urllib.request

MODEL = "claude-fable-5"
MAX_RUNG = 4

_SYSTEM = (
    "You are a Socratic mathematics tutor for a hard discrete-math course. NEVER give the "
    "final answer or a full solution. Respond in 1-3 sentences. Ask one probing question or "
    "give one targeted hint appropriate to the requested rung. Do not agree with a student's "
    "assertion unless you have re-derived it yourself. Keep cognitive load low."
)


def _llm(prompt: str, max_tokens: int = 300) -> str | None:
    """Call Claude over plain urllib. Returns None on ANY failure (Atlas §5.2)."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        body = json.dumps({
            "model": MODEL, "max_tokens": max_tokens,
            "system": _SYSTEM,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=body,
            headers={
                "x-api-key": key, "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        return data["content"][0]["text"].strip()
    except Exception:
        return None


def _authored_fallback(problem: dict, rung: int) -> str:
    """Structural help derived from the problem itself when no LLM is available."""
    if rung == 0:
        return ("Restate the problem in your own words — what are you given, and what "
                "exactly must you show? Write it before reading on.")
    if rung == 1:
        skill = problem["skills"][0].split(".")[-1].replace("-", " ") if problem["skills"] else "the core idea"
        return f"What definition or technique does this problem hinge on? (Hint: think about {skill}.)"
    if rung == 2:
        if problem["kind"] == "proof":
            return ("Decide your proof strategy first: direct, contrapositive, or "
                    "contradiction? Write the first line — 'Assume …' — before continuing.")
        return "Name the first quantity you can compute from the givens, and compute it."
    if rung == 3:
        return ("Try the same move on a smaller instance (tiny sets / small n), get it right "
                "there, then scale the argument back up.")
    return "You've earned the full solution — submit your written attempt to reveal it."


def hint(problem: dict, rung: int, student_note: str = "") -> dict:
    """Return {rung, text, is_llm}. rung is clamped to [0, 3] here; rung 4 is the attempt path."""
    rung = max(0, min(rung, MAX_RUNG - 1))
    rung_goal = {
        0: "Ask the student to restate the problem; do not hint yet.",
        1: "Ask ONE probing question that surfaces the key definition/technique.",
        2: "Give ONE targeted conceptual hint — name the strategy, not the steps.",
        3: "Describe an ANALOGOUS simpler problem and its approach, not this one's answer.",
    }[rung]
    prompt = (
        f"Problem: {problem['statement']}\n\n"
        f"Student's note so far: {student_note or '(none)'}\n\n"
        f"Rung {rung} instruction: {rung_goal}"
    )
    text = _llm(prompt)
    if text is None:
        return {"rung": rung, "text": _authored_fallback(problem, rung), "is_llm": False}
    return {"rung": rung, "text": text, "is_llm": True}


# ── grading (typed short answers; the mock photo pipeline is separate) ────────

def grade_open(problem: dict, submission: str) -> dict | None:
    """LLM rubric grade of a free-response submission. None on failure -> UI self-assessment."""
    if not submission.strip():
        return None
    rubric = "\n".join(
        f"- {l['points']} pt: {l['criterion']}"
        for part in problem.get("parts", []) for l in part.get("rubric", [])
    ) or f"- {problem['points']} pt: correct, complete, rigorous solution"
    prompt = (
        f"Grade this student solution against the rubric. Return STRICT JSON "
        f'{{"score": <number>, "max": {problem["points"]}, "feedback": "<2-3 sentences>", '
        f'"rubric_hits": ["..."]}}.\n\n'
        f"Problem: {problem['statement']}\n\nReference solution: {problem.get('solution','')}\n\n"
        f"Rubric:\n{rubric}\n\nStudent solution:\n{submission}"
    )
    raw = _llm(prompt, max_tokens=500)
    if raw is None:
        return None
    try:
        start, end = raw.index("{"), raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return None
