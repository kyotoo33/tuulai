"""
main.py — the thin API (Atlas §5). Reads content, reads/writes state, grades. No content
logic here. `_safe_problem()` strips solutions/answers/rubrics at the boundary (invariant 14).
Static SPA is mounted LAST (Atlas invariant 11). One process serves API + SPA.
"""
from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend import coach as coachmod
from backend import content as C
from backend import database as db
from backend import mock as mockmod
from backend import scheduler as sch
from backend import tutor
from backend import vision

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

app = FastAPI(title="Tuulai")
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


@app.middleware("http")
async def _no_cache_assets(request, call_next):
    """Local-first dev: never cache our own JS/CSS so edits show on reload. Vendored KaTeX
    (fonts/js/css) is content-stable and may cache normally."""
    resp = await call_next(request)
    path = request.url.path
    is_doc = path == "/" or path.endswith(".html")
    if is_doc or (path.endswith((".js", ".css")) and "/vendor/" not in path):
        resp.headers["Cache-Control"] = "no-store"
    return resp


# ── answer stripping (invariant 14) ──────────────────────────────────────────

def _safe_problem(p: dict) -> dict:
    """Strip everything that reveals the answer before an attempt is logged."""
    hide = {"solution", "answer"}
    out = {k: v for k, v in p.items() if k not in hide}
    out["parts"] = [
        {k: v for k, v in part.items() if k not in {"answer", "rubric"}}
        for part in p.get("parts", [])
    ]
    return out


def _has_attempt(problem_key: str) -> bool:
    return len(db.attempts_for(problem_key)) > 0


# ── health (content counts = real end-to-end boot assertion, Atlas §8) ───────

@app.get("/api/health")
def health():
    return {"ok": True, "app": "Tuulai", **C.summary()}


# ── course + radar ───────────────────────────────────────────────────────────

@app.get("/api/course")
def course():
    today = date.today()
    return {
        "course": C.COURSE,
        "next_quiz": (lambda q: q["id"] if q else None)(sch.next_quiz(C.COURSE, today)),
        "days_until_quiz": sch.days_until_quiz(C.COURSE, today),
        "streak": db.streak(),
    }


@app.get("/api/radar")
def radar():
    return sch.quiz_radar(C.COURSE, C.SKILLS, db.all_skill_state(), date.today())


# ── today (the enforced session, README §4) ──────────────────────────────────

@app.get("/api/today")
def today():
    cards = db.due_cards()
    plan = sch.build_today(
        C.COURSE, C.SKILLS, C.LIVE_PROBLEMS, cards, db.all_skill_state(), date.today())
    # attach card fronts (backs stay server-side until reviewed)
    plan["cards_due"] = [
        {"key": c["card_key"], **_card_front(c["card_key"])}
        for c in cards if c["card_key"] in C.CARDS_BY_KEY
    ]
    plan["streak"] = db.streak()
    plan["open_errors"] = len(db.open_errors())
    return plan


def _card_front(card_key: str) -> dict:
    card = C.CARDS_BY_KEY.get(card_key, {})
    return {"skill": card.get("skill"), "genre": card.get("genre"), "front": card.get("front")}


# ── problems ─────────────────────────────────────────────────────────────────

@app.get("/api/problems/{key}")
def get_problem(key: str):
    p = C.PROBLEMS_BY_KEY.get(key)
    if not p:
        raise HTTPException(404, "unknown problem")
    safe = _safe_problem(p)
    safe["attempted"] = _has_attempt(key)
    safe["concept"] = _concept_for_problem(key)   # solution panel "shore up" link (#5)
    safe["playbook"] = _playbook_for_problem(key)  # "how do I even start?" link
    return safe


class RevealIn(BaseModel):
    confidence: str               # sure | shaky | guess — the calibration prediction
    mode: str = "paper"           # paper | typed
    hints_used: int = 0
    seconds: int = 0


@app.post("/api/problems/{key}/reveal")
def reveal_solution(key: str, body: RevealIn):
    """Capture the confidence prediction (invariant 16), log a pending attempt, and unlock
    the solution (invariant 14). Grading (self-assessment) happens in a second step."""
    p = C.PROBLEMS_BY_KEY.get(key)
    if not p:
        raise HTTPException(404, "unknown problem")
    if body.confidence not in {"sure", "shaky", "guess"}:
        raise HTTPException(400, "confidence required before reveal (invariant 16)")
    quiz = sch.next_quiz(C.COURSE, date.today())
    aid = db.record_attempt(
        key, body.mode, "pending", body.confidence,
        hints_used=body.hints_used, seconds=body.seconds,
        quiz_target=quiz["id"] if quiz else None)
    return {
        "attempt_id": aid,
        "solution": p.get("solution", ""),
        "answer": p.get("answer"),
        "parts": [{"prompt": pt.get("prompt"), "answer": pt.get("answer"),
                   "rubric": pt.get("rubric", [])} for pt in p.get("parts", [])],
    }


class GradeIn(BaseModel):
    attempt_id: int
    result: str                   # correct | partial | wrong (honest self-grade)
    error_taxonomy: str | None = None  # concept | procedure | misread | slip
    error_note: str = ""


@app.post("/api/problems/{key}/grade")
def grade_attempt(key: str, body: GradeIn):
    p = C.PROBLEMS_BY_KEY.get(key)
    if not p:
        raise HTTPException(404, "unknown problem")
    if body.result not in {"correct", "partial", "wrong"}:
        raise HTTPException(400, "bad result")
    at = db.get_attempt(body.attempt_id)
    if not at or at["problem_key"] != key:
        raise HTTPException(404, "unknown attempt")
    db.grade_attempt(body.attempt_id, body.result)

    cold = at["hints_used"] == 0
    deltas = sch.credit_for_attempt(p, C.SKILLS_BY_KEY, body.result, cold)
    today = date.today()
    for sk, delta in deltas.items():
        st = db.get_skill_state(sk)
        strength = (st["strength"] if st else 0) + delta
        db.upsert_skill_state(
            sk, add_touches=delta, on_day=today.isoformat(),
            due=sch.next_due(body.result, cold, today),
            strength=strength, demote=(delta < 0))

    error_id = None
    if body.result in ("wrong", "partial") and body.error_taxonomy:
        error_id = db.add_error(
            key, body.error_taxonomy, body.error_note, attempt_id=body.attempt_id,
            retest_due=sch.next_due("wrong", cold, today))

    return {"credited": deltas, "error_id": error_id}


# ── hint ladder (server-side gate) ───────────────────────────────────────────

class HintIn(BaseModel):
    rung: int = 1
    note: str = ""


@app.post("/api/problems/{key}/hint")
def get_hint(key: str, body: HintIn):
    p = C.PROBLEMS_BY_KEY.get(key)
    if not p:
        raise HTTPException(404, "unknown problem")
    if body.rung >= tutor.MAX_RUNG and not _has_attempt(key):
        raise HTTPException(
            403, "full solution unlocks only after a logged attempt (invariant 14)")
    db.record_hint(key, body.rung)
    return tutor.hint(p, body.rung, body.note)


# ── cards ────────────────────────────────────────────────────────────────────

@app.get("/api/cards/{key}")
def get_card(key: str):
    card = C.CARDS_BY_KEY.get(key)
    if not card:
        raise HTTPException(404, "unknown card")
    return card  # full card (front+back) — cards are self-graded on reveal


class CardReviewIn(BaseModel):
    grade: str    # again | good | easy


@app.post("/api/cards/{key}/review")
def review_card(key: str, body: CardReviewIn):
    if key not in C.CARDS_BY_KEY:
        raise HTTPException(404, "unknown card")
    if body.grade not in {"again", "good", "easy"}:
        raise HTTPException(400, "bad grade")
    db.review_card(key, body.grade)
    return {"ok": True}


@app.post("/api/skills/{key}/start")
def start_skill(key: str):
    """Activate a skill's cards + mark it seen (moves it out of 'new content')."""
    sk = C.SKILLS_BY_KEY.get(key)
    if not sk:
        raise HTTPException(404, "unknown skill")
    card_keys = [c["key"] for c in C.CARDS if c["skill"] == key]
    db.activate_cards(card_keys)
    st = db.get_skill_state(key)
    if st is None:
        db.upsert_skill_state(key, add_touches=0, on_day=date.today().isoformat(),
                              due=date.today().isoformat(), strength=0)
    concept = C.concept_for_skill(key)
    return {"ok": True, "activated_cards": len(card_keys),
            "first_contact": sk.get("first_contact"),
            "concept": concept["key"] if concept else None}   # first-contact routing (I: worked-first)


# ── error log ────────────────────────────────────────────────────────────────

def _concept_for_problem(problem_key: str) -> str | None:
    p = C.PROBLEMS_BY_KEY.get(problem_key)
    if not p or not p.get("skills"):
        return None
    c = C.concept_for_skill(p["skills"][0])
    return c["key"] if c else None


def _playbook_for_problem(problem_key: str) -> str | None:
    p = C.PROBLEMS_BY_KEY.get(problem_key)
    if not p or not p.get("skills"):
        return None
    for sk in p["skills"]:                     # first skill with a playbook wins
        pb = C.playbook_for_skill(sk)
        if pb:
            return pb["key"]
    return None


@app.get("/api/errors")
def errors():
    # concept-gap rows get a "Review the concept" target (integration #4)
    out = []
    for r in db.open_errors():
        row = dict(r)
        if row.get("taxonomy") == "concept":
            row["concept"] = _concept_for_problem(row.get("problem_key"))
        out.append(row)
    return out


# ── concepts (docs/concepts-plan.md) — read-only; reading logs NOTHING (I23) ──

@app.get("/api/concepts")
def concepts_index():
    """Index grouped by week, each concept carrying its linked skills' readiness (radar dots)."""
    state = db.all_skill_state()
    quiz = sch.next_quiz(C.COURSE, date.today())
    quiz_dt = sch.quiz_date(C.COURSE, quiz) if quiz else None
    out = []
    for c in C.CONCEPTS:
        readiness = [sch.readiness(state.get(sk), quiz_dt, date.today()) for sk in c["skills"]]
        out.append({"key": c["key"], "week": c["week"], "title": c["title"],
                    "summary": c.get("summary", ""), "skills": c["skills"],
                    "module": c.get("module"), "readiness": readiness})
    return out


@app.get("/api/concepts/{key}")
def get_concept(key: str):
    c = C.CONCEPTS_BY_KEY.get(key)
    if not c:
        raise HTTPException(404, "unknown concept")
    hooks = [{"key": pk, "title": C.PROBLEMS_BY_KEY[pk]["title"],
              "kind": C.PROBLEMS_BY_KEY[pk]["kind"]}
             for pk in c["retrieval_problems"] if pk in C.PROBLEMS_BY_KEY]
    cards = [{"key": cd["key"], "genre": cd["genre"]}
             for cd in C.CARDS if cd["skill"] in c["skills"]]
    return {**c, "retrieval_hooks": hooks, "cards": cards}


# ── playbooks (recitation-derived "how to start") — read-only; logs NOTHING ──

@app.get("/api/playbooks")
def playbooks_index():
    """Index grouped by family (proofs / logic / analysis), with linked skills' readiness."""
    state = db.all_skill_state()
    quiz = sch.next_quiz(C.COURSE, date.today())
    quiz_dt = sch.quiz_date(C.COURSE, quiz) if quiz else None
    out = []
    for pb in C.PLAYBOOKS:
        readiness = [sch.readiness(state.get(sk), quiz_dt, date.today()) for sk in pb["skills"]]
        out.append({"key": pb["key"], "title": pb["title"], "family": pb["family"],
                    "one_liner": pb["one_liner"], "skills": pb["skills"],
                    "n_moves": len(pb["moves"]), "n_drills": len(pb["drills"]),
                    "readiness": readiness})
    return out


@app.get("/api/playbooks/{key}")
def get_playbook(key: str):
    pb = C.PLAYBOOKS_BY_KEY.get(key)
    if not pb:
        raise HTTPException(404, "unknown playbook")
    drills = [{"key": pk, "title": C.PROBLEMS_BY_KEY[pk]["title"],
               "kind": C.PROBLEMS_BY_KEY[pk]["kind"],
               "difficulty": C.PROBLEMS_BY_KEY[pk].get("difficulty")}
              for pk in pb["drills"] if pk in C.PROBLEMS_BY_KEY]
    return {**pb, "drill_hooks": drills}


# ── coach (weekly report) + notification summary (README §4 Loop 3, P7) ──────

@app.get("/api/coach")
def coach():
    return coachmod.build_report(
        C.COURSE, C.SKILLS, C.SKILLS_BY_KEY, C.PROBLEMS_BY_KEY, db, date.today())


@app.get("/api/notify")
def notify():
    """Compact, state-bearing summary the desktop notifier turns into a message."""
    today = date.today()
    plan = sch.build_today(C.COURSE, C.SKILLS, C.LIVE_PROBLEMS, db.due_cards(),
                           db.all_skill_state(), today)
    open_errs = db.open_errors()
    due_retests = sum(1 for e in open_errs
                      if not e["retest_due"] or e["retest_due"][:10] <= today.isoformat())
    q = sch.next_quiz(C.COURSE, today)
    active_today = today.isoformat() in db.heatmap(1)
    return {
        "quiz_target": q["id"] if q else None,
        "days_until_quiz": sch.days_until_quiz(C.COURSE, today),
        "cards_due": len(plan["cards_due"]),
        "review_due": len(plan["review_problems"]),
        "new_skills": len(plan["new_skills"]),
        "retests_due": due_retests,
        "streak": db.streak(),
        "active_today": active_today,
        "is_sunday": today.weekday() == 6,
        "is_lecture_day": today.weekday() in (1, 3),   # Tue/Thu — Wooclap point at a random lecture
        "url": "http://127.0.0.1:8642/#/today",
    }


# ── mock quiz pipeline (README §4 Loop 2, P6) ────────────────────────────────

@app.get("/api/mock/capability")
def mock_capability():
    """Whether auto transcription/grading is available, and via which provider."""
    return vision.capability()


@app.get("/api/mock/history")
def mock_history():
    return [dict(r) for r in db.mock_history()]


# Custom exam scopes: a real exam often spans weeks that match no single quiz window.
# Define one here and the Mock page's "Exam sprint" button will assemble against it.
# Example: an exam covering weeks 1-2 plus a later strand in week 8.
EXAM_SCOPES = {
    "exam-sprint": {"weeks": [1, 2], "count": 8,
                    "title": "Exam sprint"},
}


class AssembleIn(BaseModel):
    quiz_target: str | None = None
    scope: str | None = None          # e.g. "exam-sprint" — a custom cross-week exam scope


@app.post("/api/mock/assemble")
def assemble_mock(body: AssembleIn):
    today = date.today()
    if body.scope:                    # custom exam scope (cross-week)
        sc = EXAM_SCOPES.get(body.scope)
        if not sc:
            raise HTTPException(400, f"unknown scope '{body.scope}'")
        plan = mockmod.assemble(C.COURSE, C.LIVE_PROBLEMS, C.SKILLS_BY_KEY, body.scope,
                                random.Random(), weeks=sc["weeks"], n_target=sc["count"])
        if not plan["problem_keys"]:
            raise HTTPException(409, "no problems available for this exam scope")
        mid = db.create_assembled_mock(body.scope, plan["problem_keys"], plan["points"],
                                       plan["duration_min"])
        return _mock_payload(mid)
    target = body.quiz_target
    if not target:
        q = sch.next_quiz(C.COURSE, today)
        target = q["id"] if q else (C.COURSE["quizzes"][0]["id"] if C.COURSE["quizzes"] else None)
    if not target:
        raise HTTPException(400, "no quiz to assemble a mock for")
    plan = mockmod.assemble(
        C.COURSE, C.LIVE_PROBLEMS, C.SKILLS_BY_KEY, target, random.Random())
    if not plan["problem_keys"]:
        raise HTTPException(409, "no problems available for this quiz's coverage window")
    mid = db.create_assembled_mock(target, plan["problem_keys"], plan["points"], plan["duration_min"])
    return _mock_payload(mid)


@app.get("/api/mock/{mock_id}")
def get_mock(mock_id: int):
    return _mock_payload(mock_id)


def _mock_payload(mock_id: int) -> dict:
    row = db.get_assembled_mock(mock_id)
    if not row:
        raise HTTPException(404, "unknown mock")
    keys = json.loads(row["problem_keys"])
    problems = [_safe_problem(C.PROBLEMS_BY_KEY[k]) for k in keys if k in C.PROBLEMS_BY_KEY]
    quiz = next((q for q in C.COURSE["quizzes"] if q["id"] == row["quiz_target"]), None)
    _scope = EXAM_SCOPES.get(row["quiz_target"])
    return {
        "id": mock_id, "quiz_target": row["quiz_target"],
        "quiz_title": quiz["title"] if quiz else (_scope["title"] if _scope else "Mock quiz"),
        "points": row["points"], "duration_min": row["duration_min"],
        "conditions": C.COURSE["conditions"], "problems": problems,
        "transcripts": json.loads(row["transcripts"]) if row["transcripts"] else None,
    }


@app.post("/api/mock/{mock_id}/transcribe")
async def transcribe_mock(mock_id: int, files: list[UploadFile] = File(...)):
    row = db.get_assembled_mock(mock_id)
    if not row:
        raise HTTPException(404, "unknown mock")
    keys = json.loads(row["problem_keys"])
    problems = [C.PROBLEMS_BY_KEY[k] for k in keys if k in C.PROBLEMS_BY_KEY]
    # store photos
    updir = DATA_DIR / "uploads" / f"mock-{mock_id}"
    updir.mkdir(parents=True, exist_ok=True)
    images, paths = [], []
    for i, f in enumerate(files):
        data = await f.read()
        ext = (f.filename or "img.jpg").rsplit(".", 1)[-1][:5]
        path = updir / f"page-{i+1}.{ext}"
        path.write_bytes(data)
        images.append((data, f.filename or path.name))
        paths.append(str(path))
    transcripts = mockmod.transcribe(problems, images)
    db.set_mock_photos_transcripts(mock_id, paths, transcripts or {})
    return {
        "available": vision.capability()["available"],
        "transcriptions": transcripts,   # None => manual entry / self-grade
        "problem_keys": [p["key"] for p in problems],
    }


class GradeMockIn(BaseModel):
    transcriptions: dict[str, str] = {}
    minutes: int | None = None
    # optional manual self-grade fallback when no vision provider: {key: score}
    self_scores: dict[str, float] | None = None


@app.post("/api/mock/{mock_id}/grade")
def grade_mock(mock_id: int, body: GradeMockIn):
    row = db.get_assembled_mock(mock_id)
    if not row:
        raise HTTPException(404, "unknown mock")
    keys = json.loads(row["problem_keys"])
    problems = [C.PROBLEMS_BY_KEY[k] for k in keys if k in C.PROBLEMS_BY_KEY]
    today = date.today()

    if vision.capability()["available"] and body.transcriptions:
        report = mockmod.grade_all(problems, body.transcriptions)
        # error-log entries for misses, with a scheduled re-test
        for r in report["results"]:
            if r.get("graded") and float(r.get("score", 0)) < float(r.get("max", 0)):
                tax = r.get("miss_taxonomy") or "concept"
                if tax == "none":
                    continue
                db.add_error(r["key"], tax, r.get("feedback", "")[:400],
                             retest_due=sch.next_due("wrong", True, today))
        # skill credit: a fully-correct problem gives a cold touch
        for r in report["results"]:
            p = C.PROBLEMS_BY_KEY.get(r["key"])
            if p and r.get("graded") and float(r.get("score", 0)) >= float(r.get("max", 0)):
                deltas = sch.credit_for_attempt(p, C.SKILLS_BY_KEY, "correct", True)
                for sk, d in deltas.items():
                    st = db.get_skill_state(sk)
                    db.upsert_skill_state(sk, add_touches=d, on_day=today.isoformat(),
                                          due=sch.next_due("correct", True, today),
                                          strength=(st["strength"] if st else 0) + d)
    else:
        # manual self-grade fallback (no vision provider or no transcriptions)
        ss = body.self_scores or {}
        results, score, mx = [], 0.0, 0.0
        for p in problems:
            s = float(ss.get(p["key"], 0))
            results.append({"key": p["key"], "title": p["title"], "graded": True,
                            "score": s, "max": p["points"], "feedback": "Self-assessed.",
                            "miss_taxonomy": "none" if s >= p["points"] else "concept"})
            score += s; mx += p["points"]
            if s < p["points"]:
                db.add_error(p["key"], "concept", "Self-graded miss on mock.",
                             retest_due=sch.next_due("wrong", True, today))
        report = {"results": results, "score": round(score, 2), "max": round(mx, 2),
                  "pct": round(100 * score / mx) if mx else 0}

    band = _grade_band(report["pct"])
    rid = db.record_mock(row["quiz_target"], f"mock-{mock_id}", report["score"], report["max"],
                         body.minutes or 0, row["photo_paths"], json.dumps(report))
    return {"report_id": rid, "band": band, **report}


def _grade_band(pct: float) -> str:
    for name, low in sorted(C.COURSE["grade_scale"].items(), key=lambda kv: -kv[1]):
        if pct >= low:
            return name
    return "F"


# ── static SPA (MUST be last — Atlas invariant 11) ───────────────────────────

if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
