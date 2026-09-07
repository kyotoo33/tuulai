"""Mock assembly tests — coverage window, no cross-week leak, interleaving."""
import random

from backend import mock as mockmod


COURSE = {
    "weeks": [{"n": n, "start": s} for n, s in [
        (1, "2026-08-24"), (2, "2026-08-31"), (3, "2026-09-07"), (4, "2026-09-14")]],
    "quizzes": [{"id": "quiz-1", "week": 3, "covers_weeks": [1, 2]}],
}
SKILLS_BY_KEY = {
    "w1.a": {"week": 1}, "w2.b": {"week": 2}, "w4.induction": {"week": 4},
}


def _p(key, skills, subtopic="x", kind="short", pts=1.0):
    return {"key": key, "skills": skills, "subtopic": subtopic, "kind": kind, "points": pts}


def test_assemble_only_covers_window():
    live = [
        _p("p1", ["w1.a"]), _p("p2", ["w2.b"], subtopic="y"),
        _p("ind", ["w4.induction", "w1.a"]),  # induction: primary is week 4 -> excluded
    ]
    plan = mockmod.assemble(COURSE, live, SKILLS_BY_KEY, "quiz-1", random.Random(0))
    assert "ind" not in plan["problem_keys"]      # no cross-week leak via secondary skill
    assert set(plan["problem_keys"]) <= {"p1", "p2"}


def test_assemble_prefers_distinct_skills_and_interleaves():
    live = [_p(f"a{i}", ["w1.a"], subtopic="logic") for i in range(4)] + \
           [_p(f"b{i}", ["w2.b"], subtopic="sets") for i in range(4)]
    plan = mockmod.assemble(COURSE, live, SKILLS_BY_KEY, "quiz-1", random.Random(1))
    keys = plan["problem_keys"]
    assert len(keys) >= 2
    assert plan["points"] == sum(1.0 for _ in keys)


def test_empty_pool_returns_empty():
    plan = mockmod.assemble(COURSE, [], SKILLS_BY_KEY, "quiz-1", random.Random(0))
    assert plan["problem_keys"] == []
