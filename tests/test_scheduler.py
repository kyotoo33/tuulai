"""Scheduler unit tests — the retention policy must behave as specified (README §8)."""
from datetime import date

from backend import scheduler as sch


COURSE = {
    "weeks": [
        {"n": 1, "start": "2026-08-24"}, {"n": 2, "start": "2026-08-31"},
        {"n": 3, "start": "2026-09-07"}, {"n": 4, "start": "2026-09-14"},
    ],
    "quizzes": [
        {"id": "quiz-1", "week": 3, "covers_weeks": [1, 2], "date": None, "title": "Q1"},
        {"id": "quiz-2", "week": 5, "covers_weeks": [3, 4], "date": None, "title": "Q2"},
    ],
}


def test_next_quiz_picks_soonest_upcoming():
    q = sch.next_quiz(COURSE, date(2026, 8, 25))
    assert q["id"] == "quiz-1"


def test_quiz_date_assumes_tuesday_when_unannounced():
    q = COURSE["quizzes"][0]
    # week 3 starts Mon 2026-09-07; Tuesday = 09-08
    assert sch.quiz_date(COURSE, q) == date(2026, 9, 8)


def test_fire_credit_full_and_partial():
    skills_by_key = {"a": {"encompasses": ["b"]}}
    prob = {"skills": ["a", "c"], "topic": "logic"}
    d = sch.credit_for_attempt(prob, skills_by_key, "correct", cold=True)
    assert d["a"] == 1.0          # primary full
    assert d["c"] == 0.5          # secondary listed
    assert d["b"] == 0.5          # encompassed implicit


def test_no_credit_when_hints_used():
    prob = {"skills": ["a"], "topic": "logic"}
    d = sch.credit_for_attempt(prob, {}, "correct", cold=False)
    assert d == {}


def test_wrong_demotes_primary_only():
    prob = {"skills": ["a", "b"], "topic": "logic"}
    d = sch.credit_for_attempt(prob, {}, "wrong", cold=True)
    assert d == {"a": -1.0}


def test_interleave_avoids_consecutive_same_topic():
    probs = [
        {"key": "1", "topic": "logic"}, {"key": "2", "topic": "logic"},
        {"key": "3", "topic": "comb"}, {"key": "4", "topic": "graph"},
    ]
    out = sch.interleave(probs)
    topics = [p["topic"] for p in out]
    consecutive_dupes = sum(1 for i in range(1, len(topics)) if topics[i] == topics[i-1])
    assert consecutive_dupes == 0


def test_readiness_progression():
    quiz_dt = date(2026, 9, 8)
    today = date(2026, 9, 4)
    assert sch.readiness(None, quiz_dt, today) == "untouched"
    warming = {"distinct_days": 1, "demoted_at": None, "last_touch": "2026-09-04"}
    assert sch.readiness(warming, quiz_dt, today) == "warming"
    solid = {"distinct_days": 3, "demoted_at": None, "last_touch": "2026-09-04"}
    assert sch.readiness(solid, quiz_dt, today) == "solid"
    shaky = {"distinct_days": 3, "demoted_at": "2026-09-03", "last_touch": "2026-09-02"}
    assert sch.readiness(shaky, quiz_dt, today) == "shaky"
