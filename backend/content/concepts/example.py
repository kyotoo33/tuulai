r"""
concepts/example.py — EXAMPLE concept pages.

A concept page is: idea -> picture -> example -> trap -> retrieval. Two hard rules are
enforced at import (see schema.validate_concept):
  1. at least ONE `viz` block   — a page with no picture is just reading
  2. at least ONE live retrieval problem — reading alone must never end a session

Block types: text | viz | example | trap | check
Optional keys: "summary" (shown in the index), "module" (groups pages above the week
sections in the index — e.g. "Cheatsheet" or "Exam 1 — proof writing").

Register modules in backend/content/__init__.py:  for _cn in ("example", ...)

Markdown and math mix freely: `md()` stashes each `$...$` behind an inert token before
applying markdown, so `**Base case ($n=1$).**` renders bold with the math intact.
"""

CONCEPTS = [
    # ── a real teaching page ────────────────────────────────────────────────
    {
        "key": "concept.example.limits",
        "week": 1,
        "title": "What a limit actually says",
        "summary": "The value the function approaches — not the value it takes.",
        "skills": ["w1.limits-basic", "w1.derivative-definition"],
        "blocks": [
            {"type": "text", "body":
                r"$\lim_{x\to a}f(x)=L$ describes the behaviour of $f$ **near** $a$, and says "
                r"nothing about $f(a)$ itself — $f$ need not even be defined there." "\n\n"
                r"$$\frac{x^{2}-4}{x-2}=x+2 \quad (x\ne 2)$$"},

            # `plot` — points/lines on auto-scaled axes with a dashed limit line
            {"type": "viz", "viz": "plot", "data": {
                "xlabel": "x",
                "views": [
                    {"label": r"$f(x)=\tfrac{x^{2}-4}{x-2}$",
                     "asymptote": {"y": 4, "label": "L = 4"},
                     "series": [{"label": r"$f(x)$ near $x=2$", "kind": "points", "cls": "good",
                                 "points": [[1.0, 3.0], [1.5, 3.5], [1.9, 3.9], [1.99, 3.99],
                                            [2.01, 4.01], [2.5, 4.5], [3.0, 5.0]]}]},
                ]},
             "caption": r"The hole at $x=2$ is invisible to the limit: the values approach $4$ from both sides."},

            # `reftable` — a reference table whose answer columns can be hidden for recall
            {"type": "viz", "viz": "reftable", "data": {
                "columns": ["Limit law", "Statement", "Caveat"],
                "hide": [1],
                "rows": [
                    [r"Sum", r"$\lim(f+g)=\lim f+\lim g$", r"both limits must exist"],
                    [r"Product", r"$\lim(fg)=\lim f\cdot\lim g$", r"both limits must exist"],
                    [r"Quotient", r"$\lim\frac{f}{g}=\frac{\lim f}{\lim g}$", r"requires $\lim g\ne0$"],
                    [r"Power", r"$\lim f^{n}=\left(\lim f\right)^{n}$", r"$n$ a positive integer"],
                ]},
             "caption": r"Press **Predict** to hide the middle column and recall each law before revealing."},

            # `proofsteps` — an annotated model proof; each line + why it earns marks
            {"type": "viz", "viz": "proofsteps", "data": {
                "claim": r"If $f(x)=x^{2}$ then $f'(a)=2a$.",
                "steps": [
                    {"line": r"Let $a\in\mathbb{R}$ be arbitrary. By definition $f'(a)=\lim\limits_{h\to0}\dfrac{f(a+h)-f(a)}{h}$.",
                     "tag": "state the definition", "mark": "0.2"},
                    {"line": r"$(a+h)^{2}-a^{2}=2ah+h^{2}=h(2a+h).$",
                     "tag": "equations — expand and factor", "mark": "0.3"},
                    {"line": r"Since $h\ne0$ in the limit, cancel: $\dfrac{h(2a+h)}{h}=2a+h$.",
                     "tag": "justify the cancellation", "mark": "0.3"},
                    {"line": r"Hence $f'(a)=\lim\limits_{h\to0}(2a+h)=2a$, for arbitrary $a$. $\blacksquare$",
                     "tag": "conclude for arbitrary $a$", "mark": "0.2"},
                ]},
             "caption": r"Hit **Hide the lines** and rewrite the proof from the rubric alone."},

            {"type": "example", "body":
                r"Indeterminate $\tfrac00$ is a signal, not an answer: factor "
                r"($\tfrac{x^2-4}{x-2}$), or multiply by the conjugate when a root appears "
                r"($\tfrac{\sqrt{x+9}-3}{x}$)."},
            {"type": "trap", "body":
                r"**The graded mistake:** writing $\lim_{x\to2}f(x)=f(2)$ by reflex. That equality "
                r"is *continuity*, which must be established — it is not the definition of a limit."},
            {"type": "check",
             "prompt": r"Does $\lim_{x\to2}\frac{x^{2}-4}{x-2}$ exist even though $f(2)$ is undefined?",
             "answer": r"Yes — it equals $4$. A limit never looks at the point itself."},
        ],
        "retrieval_problems": ["ex.short-01", "ex.proof-01"],
    },

    # ── a live gallery of the remaining primitives ──────────────────────────
    # Keep this page while you build; delete it once you know the payloads.
    {
        "key": "concept.example.gallery",
        "week": 1,
        "module": "Reference",                 # `module` groups pages in the index
        "title": "Visualization gallery",
        "summary": "Every built-in viz primitive, rendered. Payload docs in docs/VIZ.md.",
        "skills": ["w1.limits-basic"],
        "blocks": [
            {"type": "text", "body":
                r"All ten primitives live in `frontend/static/js/viz.js` and are validated at "
                r"import by `schema._check_viz`. Payload reference: `docs/VIZ.md`."},
            {"type": "viz", "viz": "truthtable", "data": {
                "columns": [r"$p$", r"$q$", r"$p\wedge q$"], "inputs": 2, "match": [2],
                "rows": [["T", "T", "T"], ["T", "F", "F"], ["F", "T", "F"], ["F", "F", "F"]]},
             "caption": r"`truthtable` — boxed matching columns, predict/reveal toggle."},
            {"type": "viz", "viz": "venn", "data": {"sets": ["A", "B"], "shaded": ["AB"]},
             "caption": r"`venn` — 2 or 3 sets; shade any region, including compound ones like `ABC`."},
            {"type": "viz", "viz": "mapping", "data": {
                "domain": ["1", "2", "3"], "codomain": ["a", "b"],
                "variants": [{"label": "surjective", "maps": [[0, 0], [1, 1], [2, 1]]},
                             {"label": "not surjective", "maps": [[0, 0], [1, 0], [2, 0]]}]},
             "caption": r"`mapping` — domain/codomain arrows with a variant switcher."},
            {"type": "viz", "viz": "flow", "data": {
                "nodes": [{"id": "q", "label": "Indeterminate form?", "kind": "decision"},
                          {"id": "s", "label": "Substitute", "kind": "leaf"},
                          {"id": "f", "label": "Factor / conjugate", "kind": "leaf"}],
                "edges": [{"from": "q", "to": "s", "label": "no"},
                          {"from": "q", "to": "f", "label": "yes"}],
                "start": "q"},
             "caption": r"`flow` — a layered decision tree; ideal for “which technique?”."},
            {"type": "viz", "viz": "pascal", "data": {"rows": 6},
             "caption": r"`pascal` — hover a cell to light its two parents; row-sum toggle."},
            {"type": "viz", "viz": "gridpaths", "data": {
                "width": 3, "height": 3, "diagonal": True,
                "paths": [{"label": "stays below", "steps": "RRRUUU", "valid": True},
                          {"label": "crosses", "steps": "URRRUU", "valid": False}]},
             "caption": r"`gridpaths` — lattice paths as R/U words; invalid paths draw red."},
            {"type": "viz", "viz": "numberline", "data": {
                "min": -3, "max": 3, "ticks": [-2, -1, 0, 1, 2],
                "views": [{"label": r"$|x|<1$", "note": r"Open endpoints: the interval $(-1,1)$.",
                           "intervals": [{"lo": -1, "hi": 1, "loOpen": True, "hiOpen": True,
                                          "cls": "good", "label": "converges"}]},
                          {"label": r"all $x$", "note": r"Arrows mean it extends forever.",
                           "intervals": [{"lo": -3, "hi": 3, "arrowLo": True, "arrowHi": True,
                                          "cls": "good", "label": "converges everywhere"}]}]},
             "caption": r"`numberline` — intervals with open/closed ends, ∞-arrows, case switcher."},
            {"type": "check",
             "prompt": r"Which primitive would you use for “pick the right technique”?",
             "answer": r"`flow` — a decision tree beats prose for a branching procedure."},
        ],
        "retrieval_problems": ["ex.mcq-01"],
    },
]
