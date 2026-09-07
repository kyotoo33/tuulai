r"""
playbooks/example.py — EXAMPLE playbook.

A concept teaches an IDEA. A playbook teaches the MOVE: how to recognise a problem type
and the literal first line to write. This is the antidote to "I stared at a blank page".

Every `drills` key and `worked.anchor` must be a LIVE problem (status "resolved").
family must be one of: logic | proofs | analysis

Register in backend/content/__init__.py:  for _pn in ("example", ...)
"""

PLAYBOOKS = [
    {
        "key": "play.example.limits",
        "title": "How to start a limit problem",
        "family": "analysis",
        "skills": ["w1.limits-basic"],
        "one_liner": "Substitute first; the form you get names the technique.",
        "cues": [
            "A limit of a quotient where substitution gives $\\tfrac00$.",
            "A square root sitting in a numerator or denominator.",
            "A limit as $x\\to\\infty$ of a ratio of polynomials.",
        ],
        "moves": [
            {"situation": "Substitution gives a finite number.",
             "first_line": "Substituting $x=a$ gives $[\\;\\cdot\\;]$, so the limit is that value.",
             "why": "If $f$ is continuous at $a$ there is nothing to do — say so and stop."},
            {"situation": "Substitution gives $\\tfrac00$ with polynomials.",
             "first_line": "Substitution gives $\\tfrac00$, so factor: $[\\;\\cdot\\;]$.",
             "why": "A $\\tfrac00$ form means numerator and denominator share a root; cancelling it removes the hole."},
            {"situation": "Substitution gives $\\tfrac00$ and a square root appears.",
             "first_line": "Multiply numerator and denominator by the conjugate $[\\;\\cdot\\;]$.",
             "why": "The conjugate turns a difference of roots into a difference of squares, which cancels the offending factor."},
        ],
        "template": "Limit: $\\lim_{x\\to a} f(x)$.\n\n"
                    "Step 1 — substitute $x=a$. Record the form: [finite / $\\tfrac00$ / $\\tfrac{\\infty}{\\infty}$].\n"
                    "Step 2 — pick by form:\n"
                    "   finite            -> that IS the limit; state it.\n"
                    "   $\\tfrac00$, polynomials -> factor and cancel.\n"
                    "   $\\tfrac00$, roots       -> multiply by the conjugate.\n"
                    "   $x\\to\\infty$          -> divide by the highest power.\n"
                    "Step 3 — substitute again into the simplified expression.\n"
                    "Step 4 — state the limit in a sentence.",
        "worked": {
            "anchor": "ex.short-01",
            "trace": "Substituting $x=0$ into $\\tfrac{\\sqrt{x+9}-3}{x}$ gives $\\tfrac00$, so you may not stop. "
                     "A square root in the numerator points at the conjugate, so multiply top and bottom by "
                     "$\\sqrt{x+9}+3$. The numerator becomes $(x+9)-9=x$, which cancels the $x$ below and leaves "
                     "$\\tfrac{1}{\\sqrt{x+9}+3}$ — now continuous at $0$. Substituting again gives $\\tfrac16$. "
                     "Every step was chosen by the FORM, never by inspiration.",
        },
        "pitfall": "Declaring 'the limit does not exist' the moment you see $\\tfrac00$. "
                   "That form carries no information — it only tells you that substitution alone is not enough. "
                   "Simplify first, then substitute again.",
        "drills": ["ex.short-01", "ex.mcq-01"],
    },
]
