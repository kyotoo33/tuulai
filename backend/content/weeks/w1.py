r"""
weeks/w1.py — EXAMPLE week module. Copy this file to w2.py, w3.py, ... for your course.

A week module exports two lists:
  SKILLS — the schedulable atoms. One skill = one thing you can be tested on.
  CARDS  — retrieval prompts attached to a skill (flashcards, but open-recall).

Register each new week in backend/content/__init__.py:
    from backend.content.weeks import w1, w2      <- add it here
    _WEEK_MODULES = [w1, w2]                      <- and here

Skill keys are permanent: they are the join key to your progress database. Renaming a
skill key orphans its history, so pick names you can live with.
"""

WEEK = 1

SKILLS = [
    {
        "key": "w1.limits-basic",              # stable id — never rename casually
        "week": 1,
        "name": "Evaluating limits",
        "guide_line": "Evaluate limits of rational functions; recognise indeterminate forms.",
        "prereqs": [],                          # skill keys that should come first
        "encompasses": [],                      # mastering this implicitly practises these
        "first_contact": "ex.short-01",         # worked example shown on first exposure
        "textbook": ["Ch. 2.1–2.3"],
        "slides": [],
    },
    {
        "key": "w1.derivative-definition",
        "week": 1,
        "name": "The derivative from first principles",
        "guide_line": "Compute $f'(a)$ from the limit definition of the derivative.",
        "prereqs": ["w1.limits-basic"],         # soft gate: scheduler prefers prereqs first
        "encompasses": [],
        "first_contact": "ex.proof-01",
        "textbook": ["Ch. 3.1"],
        "slides": [],
    },
]

# Card genres (pick the one that matches the recall you want):
#   definition · theorem · technique-choice · example · counterexample · essence · intuition
#
# RULE: never write a yes/no question. The validator rejects fronts like
# "Is f continuous?" with a back of "Yes" — those train recognition, not recall.
CARDS = [
    {
        "key": "w1.limits-basic#def-0",
        "skill": "w1.limits-basic",
        "genre": "definition",
        "front": r"State what $\lim_{x\to a} f(x) = L$ means, informally.",
        "back": r"$f(x)$ can be made arbitrarily close to $L$ by taking $x$ sufficiently close to "
                r"(but not equal to) $a$.",
    },
    {
        "key": "w1.limits-basic#technique-0",
        "skill": "w1.limits-basic",
        "genre": "technique-choice",
        "front": r"You hit the indeterminate form $\tfrac00$ in a rational limit. What are your two "
                 r"first moves?",
        "back": r"Factor and cancel the common root; or multiply by the conjugate when a square "
                r"root is present. Only then substitute.",
    },
    {
        "key": "w1.derivative-definition#def-0",
        "skill": "w1.derivative-definition",
        "genre": "definition",
        "front": r"Write the limit definition of $f'(a)$.",
        "back": r"$f'(a) = \displaystyle\lim_{h\to 0}\frac{f(a+h)-f(a)}{h}$ "
                r"(equivalently $\lim_{x\to a}\frac{f(x)-f(a)}{x-a}$).",
    },
]
