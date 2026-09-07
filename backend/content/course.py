"""
course.py — your syllabus, as data. START HERE when adapting Tuulai to your course.

Everything downstream (the countdown, the quiz radar, mock assembly, the scheduler's
urgency model) is derived from this one dict. Get it right and the rest follows.

Validated at import by schema.validate_course():
  - every `covers_weeks` entry must be a real week
  - `weights` must sum to exactly 1.0
"""

COURSE = {
    # ── identity ────────────────────────────────────────────────────────────
    "code": "MATH 101",
    "title": "Example Course — replace this with yours",
    "term": "Spring 2026",

    # ── calendar ────────────────────────────────────────────────────────────
    # start_date is the Monday of week 1. Weeks drive the whole scheduler.
    "start_date": "2026-01-12",
    "n_weeks": 7,
    "final_week": 8,
    "weeks": [
        {"n": 1, "start": "2026-01-12", "label": "Limits & continuity"},
        {"n": 2, "start": "2026-01-19", "label": "Derivatives"},
        {"n": 3, "start": "2026-01-26", "label": "Applications of derivatives"},
        {"n": 4, "start": "2026-02-02", "label": "Integration"},
        {"n": 5, "start": "2026-02-09", "label": "Techniques of integration"},
        {"n": 6, "start": "2026-02-16", "label": "Sequences"},
        {"n": 7, "start": "2026-02-23", "label": "Series"},
        {"n": 8, "start": "2026-03-02", "label": "Final exam week"},
    ],

    # ── assessments ─────────────────────────────────────────────────────────
    # `week` = the week the quiz happens; `covers_weeks` = what it examines.
    # Leave `date` as None and the scheduler assumes the Tuesday of that week.
    "quizzes": [
        {"id": "quiz-1", "week": 3, "covers_weeks": [1, 2], "date": None,
         "duration_min": 50, "title": "Quiz 1 — limits & derivatives"},
        {"id": "quiz-2", "week": 5, "covers_weeks": [3, 4], "date": None,
         "duration_min": 50, "title": "Quiz 2 — applications & integration"},
        {"id": "quiz-3", "week": 7, "covers_weeks": [5, 6], "date": None,
         "duration_min": 50, "title": "Quiz 3 — techniques & sequences"},
        {"id": "final", "week": 8, "covers_weeks": [1, 2, 3, 4, 5, 6, 7, 8], "date": None,
         "duration_min": 120, "title": "Final exam (cumulative)"},
    ],

    # ── grading ─────────────────────────────────────────────────────────────
    "weights": {"quizzes": 0.60, "final": 0.35, "participation": 0.05},  # must sum to 1.0
    "grade_scale": {"A": 93, "A-": 90, "B+": 87, "B": 83, "B-": 80,
                    "C+": 77, "C": 73, "D": 60, "F": 0},                 # lower bounds

    # ── exam conditions — these are printed on every mock paper ─────────────
    # Make them match reality. Rehearsing under the real constraints is the
    # single highest-leverage thing this whole system does.
    "conditions": [
        "Closed book — no notes, no textbook",
        "No calculator, phone or computer",
        "Pen only, handwritten",
        "Show all work; answers without justification score zero",
    ],
    "miss_rule": "Missing two or more quizzes results in failing the course.",

    # ── links surfaced in the Library view ──────────────────────────────────
    "links": {
        "syllabus": "https://example.edu/your-course/syllabus",
        "textbook": "https://example.edu/your-course/textbook",
        "lms": "https://example.edu/your-course",
    },
}
