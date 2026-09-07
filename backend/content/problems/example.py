r"""
problems/example.py — EXAMPLE problem module showing every problem shape.

Register new modules in backend/content/__init__.py:
    for _modname in ("example", "week1_problems", ...):

Two behavioural families (see backend/schema.py):
  AUTO  — mcq · numeric · truefalse · match   (machine-checkable; `answer` REQUIRED if resolved)
  OPEN  — proof · short · design              (rubric-graded; answer optional)

`status` is the publication gate:
  "resolved"     -> live, reaches the practice queue
  "needs_review" -> parked; validated but never served
  "templated"    -> a parameterised stub you have not instantiated yet
Only `resolved` problems appear to the learner. That gate is the whole point: it keeps
half-checked content out of your revision without deleting it.

`difficulty`: intro | core | stretch  (stretch = real exam bar)
`rubric` lines are what the grader pays for. Write them the way your professor marks:
if hypotheses must be verified, make that its own line worth its own points.
"""

PROBLEMS = [
    # ── AUTO: multiple choice — `options` and `answer` are both required ─────
    {
        "key": "ex.mcq-01",
        "origin": "textbook",          # bank | past-quiz | ai-variant | slide | textbook | recitation
        "status": "resolved",
        "difficulty": "intro",
        "kind": "mcq",
        "topic": "calculus", "subtopic": "limits",
        "title": "A limit at an indeterminate form",
        "statement": r"Evaluate $\displaystyle\lim_{x\to 2}\frac{x^{2}-4}{x-2}$.",
        "options": ["0", "2", "4", "The limit does not exist"],
        "answer": "4",
        "solution": r"Direct substitution gives $\tfrac00$, so factor: "
                    r"$\dfrac{x^{2}-4}{x-2}=\dfrac{(x-2)(x+2)}{x-2}=x+2$ for $x\ne2$. "
                    r"Hence the limit is $2+2=4$.",
        "skills": ["w1.limits-basic"],
        "points": 1.0, "est_minutes": 3,
        "source": "Example textbook §2.2",
    },

    # ── OPEN: short answer ──────────────────────────────────────────────────
    {
        "key": "ex.short-01",
        "origin": "textbook",
        "status": "resolved",
        "difficulty": "core",
        "kind": "short",
        "topic": "calculus", "subtopic": "limits",
        "title": "A limit with a square root",
        "statement": r"Evaluate $\displaystyle\lim_{x\to 0}\frac{\sqrt{x+9}-3}{x}$.",
        "answer": r"$\dfrac16$",
        "solution": r"Multiply by the conjugate:"
                    "\n$$\\frac{\\sqrt{x+9}-3}{x}\\cdot\\frac{\\sqrt{x+9}+3}{\\sqrt{x+9}+3}"
                    r"=\frac{(x+9)-9}{x\left(\sqrt{x+9}+3\right)}=\frac{1}{\sqrt{x+9}+3}."
                    "$$\n"
                    r"Letting $x\to0$ gives $\dfrac{1}{3+3}=\dfrac16$.",
        "skills": ["w1.limits-basic"],
        "points": 1.0, "est_minutes": 5,
        "source": "Example textbook §2.3",
    },

    # ── OPEN: proof, with parts and a rubric ────────────────────────────────
    # If part points are non-zero they MUST sum to the problem's `points`.
    {
        "key": "ex.proof-01",
        "origin": "textbook",
        "status": "resolved",
        "difficulty": "stretch",
        "kind": "proof",
        "topic": "calculus", "subtopic": "derivatives",
        "title": "Derivative of $x^{2}$ from the definition",
        "statement": r"Using only the limit definition of the derivative, prove that if "
                     r"$f(x)=x^{2}$ then $f'(a)=2a$ for every real $a$.",
        "parts": [
            {
                "prompt": r"Write the full proof.",
                "points": 1.0,
                "answer": None,
                "rubric": [
                    {"points": 0.2, "criterion": "States the definition being used, with the correct limit"},
                    {"points": 0.3, "criterion": "Expands $(a+h)^2$ and simplifies the difference quotient"},
                    {"points": 0.3, "criterion": "Cancels $h$ with the justification that $h \\ne 0$ in the limit"},
                    {"points": 0.2, "criterion": "Evaluates the limit and states the conclusion for arbitrary $a$"},
                ],
            },
        ],
        "solution": r"Let $a\in\mathbb{R}$ be arbitrary. By definition,"
                    "\n$$f'(a)=\\lim_{h\\to0}\\frac{f(a+h)-f(a)}{h}"
                    r"=\lim_{h\to0}\frac{(a+h)^{2}-a^{2}}{h}."
                    "$$\n"
                    r"Expanding, $(a+h)^{2}-a^{2}=2ah+h^{2}=h(2a+h)$. Since $h\ne0$ in the limit we "
                    r"may cancel:"
                    "\n$$f'(a)=\\lim_{h\\to0}\\frac{h(2a+h)}{h}=\\lim_{h\\to0}(2a+h)=2a."
                    "$$\n"
                    r"As $a$ was arbitrary, $f'(a)=2a$ for every real $a$. $\blacksquare$",
        "skills": ["w1.derivative-definition", "w1.limits-basic"],
        "points": 1.0, "est_minutes": 10,
        "source": "Example textbook §3.1",
    },

    # ── the gate in action: validated, but never served to the learner ──────
    {
        "key": "ex.needs-review-01",
        "origin": "ai-variant",
        "status": "needs_review",      # <- excluded from LIVE_PROBLEMS
        "difficulty": "core",
        "kind": "numeric",
        "topic": "calculus", "subtopic": "limits",
        "title": "Draft problem awaiting a human check",
        "statement": r"Evaluate $\displaystyle\lim_{x\to\infty}\frac{3x^{2}+1}{x^{2}-x}$.",
        "answer": "3",
        "solution": r"Divide numerator and denominator by $x^{2}$: "
                    r"$\dfrac{3+1/x^{2}}{1-1/x}\to 3$.",
        "skills": ["w1.limits-basic"],
        "points": 1.0, "est_minutes": 3,
        "source": "generated draft",
        "notes": "Generated, not yet verified by a human. Flip status to 'resolved' to publish it.",
    },
]
