r"""
schema.py — the validation gate. Content is validated source code; this file is the gate.

Inherits the Atlas playbook (docs/learning-workspace-playbook.md §3):
  - Every model forbids extra keys (`extra="forbid"`) so a misspelled key crashes the boot.
  - validate_*() returns the *authored dict unchanged* — the model is a gate, not a
    representation. The API serves the plain dict; there is no model->dict->JSON round-trip.
  - Two-stage validation: pydantic checks shape, hand-written code checks cross-field truth.
  - Every error names the offending id/field, actionable at 1am.

Plus a math-course gate the playbook does not have: every LaTeX string is structurally
lint-checked at import (balanced math delimiters, braces, and \begin/\end environments).
A broken formula fails the boot, not a review session three weeks later.

Pedagogy invariants live in the app, not here; this file only guarantees shape + LaTeX
sanity. See README §10.
"""
from __future__ import annotations

import re
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError


class ContentError(Exception):
    """Raised when authored content is invalid. Message always names the offending id."""


# ─────────────────────────────────────────────────────────────────────────────
# LaTeX structural linter (README §5: an honest lint, not a full KaTeX compile)
# ─────────────────────────────────────────────────────────────────────────────

# Math is authored inline in prose. We accept $...$, $$...$$, \(...\), \[...\].
# The linter checks that delimiters and structure are balanced — the errors that
# actually bite an author. It does NOT check that commands exist or that the math
# is meaningful (that is KaTeX's job at render time in the browser).

_ENV_RE = re.compile(r"\\(begin|end)\s*\{([^}]*)\}")


def _check_braces(s: str, ctx: str) -> None:
    depth = 0
    for i, ch in enumerate(s):
        if ch == "{" and (i == 0 or s[i - 1] != "\\"):
            depth += 1
        elif ch == "}" and (i == 0 or s[i - 1] != "\\"):
            depth -= 1
            if depth < 0:
                raise ContentError(f"{ctx}: unbalanced '}}' (extra closing brace)")
    if depth != 0:
        raise ContentError(f"{ctx}: unbalanced braces ({depth} unclosed '{{')")


def _check_environments(s: str, ctx: str) -> None:
    stack: list[str] = []
    for m in _ENV_RE.finditer(s):
        kind, name = m.group(1), m.group(2)
        if kind == "begin":
            stack.append(name)
        else:  # end
            if not stack:
                raise ContentError(f"{ctx}: \\end{{{name}}} with no matching \\begin")
            top = stack.pop()
            if top != name:
                raise ContentError(
                    f"{ctx}: \\begin{{{top}}} closed by \\end{{{name}}}"
                )
    if stack:
        raise ContentError(f"{ctx}: unclosed environment(s) {stack}")


def _check_math_delimiters(s: str, ctx: str) -> None:
    # Strip escaped dollars so they don't count, and neutralize LaTeX line-breaks `\\`
    # (and their optional spacing arg, e.g. `\\[4pt]`) so the `\[` inside them is not
    # mistaken for a `\[` display-math opener.
    tmp = s.replace("\\$", "\x00").replace("\\\\", "\x01")
    # $$ ... $$ must pair; then remaining single $ must pair.
    if tmp.count("$$") % 2 != 0:
        raise ContentError(f"{ctx}: unbalanced '$$' display-math delimiters")
    without_display = tmp.replace("$$", "")
    if without_display.count("$") % 2 != 0:
        raise ContentError(f"{ctx}: unbalanced '$' inline-math delimiters")
    # \( \) and \[ \] must pair.
    for op, cl, label in ((r"\(", r"\)", r"\(\)"), (r"\[", r"\]", r"\[\]")):
        if tmp.count(op) != tmp.count(cl):
            raise ContentError(f"{ctx}: unbalanced '{label}' math delimiters")


def lint_latex(s: str, ctx: str) -> None:
    """Structural sanity check of a string that may contain LaTeX math. Raises ContentError."""
    if s is None:
        return
    _check_math_delimiters(s, ctx)
    _check_braces(s, ctx)
    _check_environments(s, ctx)


# ─────────────────────────────────────────────────────────────────────────────
# Strict base
# ─────────────────────────────────────────────────────────────────────────────

class _Strict(BaseModel):
    # extra='forbid' is the whole point — it catches misspelled keys at boot.
    model_config = ConfigDict(extra="forbid")


# ─────────────────────────────────────────────────────────────────────────────
# Course (singleton) — the syllabus rules, as data. See README §2.
# ─────────────────────────────────────────────────────────────────────────────

class QuizWindow(_Strict):
    id: str                       # "quiz-1"
    week: int                     # academic week it is held in (3, 5, 7)
    covers_weeks: list[int]       # [1, 2]
    date: str | None = None       # ISO date once announced on Ed; None => assume Tuesday
    duration_min: int | None = None
    title: str = ""


class WeekMeta(_Strict):
    n: int
    start: str                    # ISO Monday
    label: str = ""


class CourseModel(_Strict):
    code: str
    title: str
    term: str
    start_date: str               # ISO Monday of week 1
    n_weeks: int
    weeks: list[WeekMeta]
    quizzes: list[QuizWindow]
    final_week: int
    weights: dict[str, float]     # {"quizzes":0.60,"final":0.35,"participation":0.05}
    conditions: list[str]         # closed-book, pen-only, ...
    grade_scale: dict[str, float] # {"A+":98,"A":93,...} lower bounds
    miss_rule: str
    links: dict[str, str] = {}    # ed, gitlab, textbooks...


def validate_course(d: dict) -> dict:
    ctx = f"course '{d.get('code','?')}'"
    try:
        CourseModel.model_validate(d)
    except ValidationError as e:
        raise ContentError(f"{ctx} invalid — {e}") from None
    weeks = {w["n"] for w in d["weeks"]}
    for q in d["quizzes"]:
        for cw in q["covers_weeks"]:
            if cw not in weeks:
                raise ContentError(f"{ctx}: {q['id']} covers unknown week {cw}")
    if abs(sum(d["weights"].values()) - 1.0) > 1e-6:
        raise ContentError(f"{ctx}: weights sum to {sum(d['weights'].values())}, not 1.0")
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Skill — the schedulable atom. See README §6.
# ─────────────────────────────────────────────────────────────────────────────

class SkillModel(_Strict):
    key: str                      # "w1.converse-contrapositive"
    week: int
    name: str
    guide_line: str = ""          # the study-guide phrasing this skill comes from
    prereqs: list[str] = []       # skill keys that should come first (soft gate)
    encompasses: list[str] = []   # skill keys implicitly practiced by mastering this (FIRe)
    first_contact: str | None = None   # problem key to use as the worked example
    textbook: list[str] = []      # deep links to book sections
    slides: list[str] = []        # lecture pdf refs


def validate_skill(d: dict) -> dict:
    ctx = f"skill '{d.get('key','?')}'"
    try:
        SkillModel.model_validate(d)
    except ValidationError as e:
        raise ContentError(f"{ctx} invalid — {e}") from None
    lint_latex(d.get("name", ""), f"{ctx}.name")
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Card — retrieval prompt. Genres from the Nielsen/Pomeranz high-yield list (research 03).
# ─────────────────────────────────────────────────────────────────────────────

CARD_GENRES = {
    "definition", "theorem", "technique-choice", "example",
    "counterexample", "essence", "intuition",
}


class CardModel(_Strict):
    key: str                      # "w1.converse-contrapositive#def-0"
    skill: str
    genre: Literal[
        "definition", "theorem", "technique-choice", "example",
        "counterexample", "essence", "intuition",
    ]
    front: str                    # may contain LaTeX
    back: str                     # may contain LaTeX


def validate_card(d: dict) -> dict:
    ctx = f"card '{d.get('key','?')}'"
    try:
        CardModel.model_validate(d)
    except ValidationError as e:
        raise ContentError(f"{ctx} invalid — {e}") from None
    # Matuschak lint: reject yes/no fronts (research 03 failure mode).
    front = d["front"].strip().lower()
    if re.match(r"^(is|are|does|do|can|will|has|have|should)\b", front) and "?" in front:
        # crude yes/no heuristic; only fire if the back looks binary
        back = d["back"].strip().lower()
        if back in {"yes", "no", "true", "false"}:
            raise ContentError(
                f"{ctx}: yes/no prompt (Matuschak failure mode) — rewrite as open recall"
            )
    lint_latex(d["front"], f"{ctx}.front")
    lint_latex(d["back"], f"{ctx}.back")
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Problem — the practice/quiz unit. See README §5, §6.
# ─────────────────────────────────────────────────────────────────────────────

# Behavioural families the API keys off (Atlas OPEN/AUTO split).
OPEN_TYPES = {"proof", "short", "design"}      # free response, rubric-graded, never auto
AUTO_TYPES = {"mcq", "numeric", "truefalse", "match"}  # machine-checkable
PROBLEM_KINDS = OPEN_TYPES | AUTO_TYPES

ORIGINS = {"bank", "past-quiz", "ai-variant", "slide", "textbook", "recitation"}
STATUSES = {"resolved", "needs_review", "templated"}
DIFFICULTIES = {"intro", "core", "stretch"}   # stretch = exam/recitation bar


class RubricLine(_Strict):
    points: float
    criterion: str                # what earns these points, in the professor's terms


class ProblemPart(_Strict):
    prompt: str = ""              # sub-question text (may be empty for single-part)
    points: float = 0.0
    answer: str | None = None     # reference answer (LaTeX); None for pure-proof parts
    rubric: list[RubricLine] = []


class ProblemModel(_Strict):
    key: str                      # stable: the bank path, or "quiz.2025-08.03#2"
    origin: Literal["bank", "past-quiz", "ai-variant", "slide", "textbook", "recitation"]
    status: Literal["resolved", "needs_review", "templated"]
    difficulty: Literal["intro", "core", "stretch"] | None = None  # exam bar = 'stretch'
    kind: Literal["proof", "short", "design", "mcq", "numeric", "truefalse", "match"]
    topic: str                    # top-level bank topic: logic/comb/graph/analysis
    subtopic: str = ""
    title: str
    statement: str                # concrete, resolved statement (LaTeX ok)
    parts: list[ProblemPart] = []
    solution: str = ""            # worked solution (LaTeX ok)
    skills: list[str] = []        # skill keys this problem exercises
    points: float = 1.0
    est_minutes: int = 6
    source: str = ""              # provenance: original .qmd path / quiz / slide
    variant_of: str | None = None
    options: list[str] | None = None   # for mcq
    answer: str | None = None     # top-level answer for single-part auto problems
    notes: str = ""               # resolver/provenance notes (why needs_review, chosen instance)


def validate_problem(d: dict) -> dict:
    ctx = f"problem '{d.get('key','?')}'"
    try:
        ProblemModel.model_validate(d)
    except ValidationError as e:
        raise ContentError(f"{ctx} invalid — {e}") from None
    # Stage two: cross-field truth.
    if d["kind"] == "mcq" and not d.get("options"):
        raise ContentError(f"{ctx}: kind 'mcq' requires options[]")
    if d["kind"] in AUTO_TYPES and d["status"] == "resolved":
        has_answer = d.get("answer") is not None or any(
            p.get("answer") is not None for p in d.get("parts", [])
        )
        if not has_answer:
            raise ContentError(
                f"{ctx}: resolved auto-gradable problem has no answer (answer or parts[].answer)"
            )
    # Points consistency (allow single-part problems to omit part points).
    if d.get("parts"):
        psum = sum(p.get("points", 0) for p in d["parts"])
        if psum > 0 and abs(psum - d.get("points", 1.0)) > 1e-6:
            raise ContentError(
                f"{ctx}: parts points sum to {psum} but problem points={d.get('points')}"
            )
    lint_latex(d["statement"], f"{ctx}.statement")
    lint_latex(d.get("solution", ""), f"{ctx}.solution")
    for i, p in enumerate(d.get("parts", [])):
        lint_latex(p.get("prompt", ""), f"{ctx}.parts[{i}].prompt")
        if p.get("answer"):
            lint_latex(p["answer"], f"{ctx}.parts[{i}].answer")
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Quiz — a past paper or an assembled mock. See README §6.
# ─────────────────────────────────────────────────────────────────────────────

class QuizModel(_Strict):
    key: str                      # "quiz.2025-08.03"
    semester: str = ""            # "2025-08"
    week: int | None = None       # which academic week it was given
    kind: Literal["past", "mock", "final"] = "past"
    title: str = ""
    problems: list[str] = []      # problem keys
    duration_min: int = 50
    conditions: list[str] = []


def validate_quiz(d: dict) -> dict:
    ctx = f"quiz '{d.get('key','?')}'"
    try:
        QuizModel.model_validate(d)
    except ValidationError as e:
        raise ContentError(f"{ctx} invalid — {e}") from None
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Graph — prerequisite + encompassing edges across weeks. See README §6, §8.
# ─────────────────────────────────────────────────────────────────────────────

class GraphEdge(_Strict):
    source: str                   # skill key
    target: str                   # skill key
    kind: Literal["prereq", "encompasses"] = "prereq"


def validate_graph(d: dict, skill_keys: set[str]) -> dict:
    ctx = "graph"
    nodes = d.get("nodes", [])
    edges = d.get("edges", [])
    for e in edges:
        try:
            GraphEdge.model_validate(e)
        except ValidationError as ex:
            raise ContentError(f"{ctx}: bad edge {e} — {ex}") from None
        for x in (e["source"], e["target"]):
            if x not in skill_keys:
                raise ContentError(f"{ctx}: edge references unknown skill '{x}'")
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Concept pages + visualizations (docs/concepts-plan.md). Typed viz data checked
# at import (invariant I25); every page must end in retrieval (invariant I24).
# ─────────────────────────────────────────────────────────────────────────────

VIZ_KINDS = {"truthtable", "venn", "mapping", "flow", "pascal",
             "gridpaths", "graph", "tiling", "plot", "numberline", "reftable", "proofsteps"}
BLOCK_KINDS = {"text", "viz", "example", "trap", "check"}
_VENN_REGIONS = {2: {"A", "B", "AB", "U"},
                 3: {"A", "B", "C", "AB", "AC", "BC", "ABC", "U"}}


def _check_viz(kind: str, data: dict, ctx: str) -> None:
    """Validate a visualization payload by kind (I25). Only V1 kinds are strict so far;
    later kinds validate their own required keys and cross-references."""
    if kind not in VIZ_KINDS:
        raise ContentError(f"{ctx}: unknown viz kind '{kind}'")
    if not isinstance(data, dict):
        raise ContentError(f"{ctx}: viz data must be an object")

    if kind == "truthtable":
        cols = data.get("columns")
        rows = data.get("rows")
        if not cols or not isinstance(rows, list) or not rows:
            raise ContentError(f"{ctx}: truthtable needs non-empty 'columns' and 'rows'")
        for i, r in enumerate(rows):
            if len(r) != len(cols):
                raise ContentError(
                    f"{ctx}: truthtable row {i} has {len(r)} cells, expected {len(cols)}")

    elif kind == "venn":
        sets = data.get("sets", [])
        if len(sets) not in (2, 3):
            raise ContentError(f"{ctx}: venn needs 2 or 3 sets, got {len(sets)}")
        valid = _VENN_REGIONS[len(sets)]
        for rid in data.get("shaded", []):
            if rid not in valid:
                raise ContentError(f"{ctx}: venn shaded region '{rid}' invalid for {len(sets)} sets")

    elif kind == "mapping":
        dom, cod = data.get("domain", []), data.get("codomain", [])
        if not dom or not cod:
            raise ContentError(f"{ctx}: mapping needs non-empty 'domain' and 'codomain'")
        variants = data.get("variants") or [{"label": "", "maps": data.get("maps", [])}]
        for v in variants:
            for m in v.get("maps", []):
                if not (0 <= m[0] < len(dom) and 0 <= m[1] < len(cod)):
                    raise ContentError(f"{ctx}: mapping edge {m} out of range")

    elif kind in ("flow", "graph"):
        nodes = data.get("nodes", [])
        ids = {n["id"] for n in nodes}
        if not nodes:
            raise ContentError(f"{ctx}: {kind} needs 'nodes'")
        for e in data.get("edges", []):
            for endpoint in ("from", "to"):
                if e.get(endpoint) not in ids:
                    raise ContentError(f"{ctx}: {kind} edge {endpoint} '{e.get(endpoint)}' is not a node")

    elif kind == "pascal":
        r = data.get("rows")
        if not isinstance(r, int) or not (1 <= r <= 14):
            raise ContentError(f"{ctx}: pascal 'rows' must be an int in 1..14")

    elif kind == "gridpaths":
        w, h = data.get("width"), data.get("height")
        if not isinstance(w, int) or not isinstance(h, int) or w < 1 or h < 1:
            raise ContentError(f"{ctx}: gridpaths needs positive int 'width' and 'height'")
        for p in data.get("paths", []):
            steps = p.get("steps", "")
            if set(steps) - {"R", "U"}:
                raise ContentError(f"{ctx}: gridpaths steps must be R/U only")
            if steps.count("R") != w or steps.count("U") != h:
                raise ContentError(
                    f"{ctx}: gridpaths path '{p.get('label','')}' has {steps.count('R')}R/{steps.count('U')}U, "
                    f"expected {w}R/{h}U")

    elif kind == "plot":
        # A plot is one or more views; each view overlays series of (x,y) points.
        views = data.get("views") or [{"series": data.get("series", []),
                                       "asymptote": data.get("asymptote")}]
        if not views:
            raise ContentError(f"{ctx}: plot needs 'views' or 'series'")
        for vi, v in enumerate(views):
            series = v.get("series", [])
            if not series:
                raise ContentError(f"{ctx}: plot view {vi} has no series")
            for se in series:
                pts = se.get("points")
                if not isinstance(pts, list) or not pts:
                    raise ContentError(f"{ctx}: plot series '{se.get('label','')}' needs non-empty 'points'")
                for pt in pts:
                    if (not isinstance(pt, (list, tuple)) or len(pt) != 2
                            or not all(isinstance(z, (int, float)) for z in pt)):
                        raise ContentError(f"{ctx}: plot point {pt!r} must be a [x, y] number pair")
                if se.get("kind", "points") not in ("points", "line"):
                    raise ContentError(f"{ctx}: plot series kind must be 'points' or 'line'")
            asy = v.get("asymptote")
            if asy is not None and not isinstance(asy.get("y"), (int, float)):
                raise ContentError(f"{ctx}: plot asymptote needs numeric 'y'")

    elif kind == "proofsteps":
        # An annotated model proof: each step pairs the LINE you write with the rubric
        # reason it earns marks. Hiding the lines turns it into a write-it-yourself drill.
        steps = data.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ContentError(f"{ctx}: proofsteps needs a non-empty 'steps' list")
        for i, s in enumerate(steps):
            if not isinstance(s, dict) or not s.get("line"):
                raise ContentError(f"{ctx}: proofsteps step {i} needs a non-empty 'line'")
            lint_latex(s["line"], f"{ctx}.steps[{i}].line")
            lint_latex(s.get("tag", ""), f"{ctx}.steps[{i}].tag")
        lint_latex(data.get("claim", ""), f"{ctx}.claim")

    elif kind == "reftable":
        cols = data.get("columns")
        rows = data.get("rows")
        if not cols or not isinstance(rows, list) or not rows:
            raise ContentError(f"{ctx}: reftable needs non-empty 'columns' and 'rows'")
        for i, r in enumerate(rows):
            if not isinstance(r, list) or len(r) != len(cols):
                raise ContentError(
                    f"{ctx}: reftable row {i} has {len(r) if isinstance(r, list) else '?'} cells, "
                    f"expected {len(cols)}")
        for h in data.get("hide", []):
            if not isinstance(h, int) or not (0 <= h < len(cols)):
                raise ContentError(f"{ctx}: reftable hide index {h!r} out of range")

    elif kind == "numberline":
        lo, hi = data.get("min"), data.get("max")
        if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)) or lo >= hi:
            raise ContentError(f"{ctx}: numberline needs numeric 'min' < 'max'")
        views = data.get("views") or [{"intervals": data.get("intervals", []),
                                       "points": data.get("points", [])}]
        for vi, v in enumerate(views):
            ivs, pts = v.get("intervals", []), v.get("points", [])
            if not ivs and not pts:
                raise ContentError(f"{ctx}: numberline view {vi} needs an interval or a point")
            for iv in ivs:
                if not isinstance(iv.get("lo"), (int, float)) or not isinstance(iv.get("hi"), (int, float)):
                    raise ContentError(f"{ctx}: numberline interval needs numeric 'lo' and 'hi'")
            for pt in pts:
                if not isinstance(pt.get("x"), (int, float)):
                    raise ContentError(f"{ctx}: numberline point needs numeric 'x'")
    # tiling/graph: lenient until their primitives ship (V3).


def validate_concept(d: dict, skill_keys: set[str], problem_keys: set[str],
                     resolved_problem_keys: set[str]) -> dict:
    ctx = f"concept '{d.get('key','?')}'"
    # shape
    required = {"key", "week", "title", "skills", "blocks", "retrieval_problems"}
    missing = required - set(d)
    if missing:
        raise ContentError(f"{ctx}: missing keys {sorted(missing)}")
    for extra in set(d) - (required | {"summary", "module"}):
        raise ContentError(f"{ctx}: unexpected key '{extra}'")

    for sk in d["skills"]:
        if sk not in skill_keys:
            raise ContentError(f"{ctx}: references unknown skill '{sk}'")
    lint_latex(d["title"], f"{ctx}.title")

    n_viz = 0
    for i, b in enumerate(d["blocks"]):
        bctx = f"{ctx}.blocks[{i}]"
        kind = b.get("type")
        if kind not in BLOCK_KINDS:
            raise ContentError(f"{bctx}: unknown block type '{kind}'")
        if kind == "viz":
            n_viz += 1
            _check_viz(b.get("viz"), b.get("data", {}), bctx)
            lint_latex(b.get("caption", ""), f"{bctx}.caption")
        elif kind == "check":
            lint_latex(b.get("prompt", ""), f"{bctx}.prompt")
            lint_latex(b.get("answer", ""), f"{bctx}.answer")
        else:  # text | example | trap
            lint_latex(b.get("body", ""), f"{bctx}.body")

    # invariant I24: every page ends in retrieval — ≥1 viz and ≥1 resolved problem
    if n_viz < 1:
        raise ContentError(f"{ctx}: needs ≥1 viz block (I25/I24)")
    if not d["retrieval_problems"]:
        raise ContentError(f"{ctx}: needs ≥1 retrieval problem (I24)")
    for pk in d["retrieval_problems"]:
        if pk not in problem_keys:
            raise ContentError(f"{ctx}: retrieval problem '{pk}' unknown")
        if pk not in resolved_problem_keys:
            raise ContentError(f"{ctx}: retrieval problem '{pk}' is not resolved/live")
    return d


# ─────────────────────────────────────────────────────────────────────────────
# Playbook — the "how to start" strategy layer (recitation-derived). A concept
# teaches an idea; a playbook teaches the MOVE: recognition cue → first line to
# write → template → annotated trace → the wrong turn. See README §5.
# ─────────────────────────────────────────────────────────────────────────────

class PlayMove(_Strict):
    situation: str                # "when the goal looks like X"
    first_line: str               # the literal first sentence to write on the page
    why: str                      # the reasoning that licenses that move


class PlayWorked(_Strict):
    anchor: str                   # problem key the trace walks through
    trace: str                    # the reasoning narrated, step by step


class PlaybookModel(_Strict):
    key: str                      # "play.function-proofs"
    title: str
    family: Literal["logic", "proofs", "analysis"]
    skills: list[str]
    one_liner: str
    cues: list[str]               # signals in a problem that select this playbook
    moves: list[PlayMove]
    template: str                 # reusable skeleton with [blanks]
    worked: PlayWorked
    pitfall: str
    drills: list[str]             # problem keys to practise on


def validate_playbook(d: dict, skill_keys: set[str], problem_keys: set[str],
                      resolved_problem_keys: set[str]) -> dict:
    ctx = f"playbook '{d.get('key','?')}'"
    try:
        PlaybookModel.model_validate(d)
    except ValidationError as e:
        raise ContentError(f"{ctx} invalid — {e}") from None
    if not d["moves"]:
        raise ContentError(f"{ctx}: needs ≥1 move (the whole point is the opening move)")
    if not d["cues"]:
        raise ContentError(f"{ctx}: needs ≥1 recognition cue")
    for sk in d["skills"]:
        if sk not in skill_keys:
            raise ContentError(f"{ctx}: references unknown skill '{sk}'")
    # every referenced problem must exist AND be live (drills must be practisable)
    refs = list(d["drills"]) + [d["worked"]["anchor"]]
    for pk in refs:
        if pk not in problem_keys:
            raise ContentError(f"{ctx}: references unknown problem '{pk}'")
        if pk not in resolved_problem_keys:
            raise ContentError(f"{ctx}: problem '{pk}' is not resolved/live")
    # LaTeX sanity across every authored string
    lint_latex(d["title"], f"{ctx}.title")
    lint_latex(d["one_liner"], f"{ctx}.one_liner")
    lint_latex(d["template"], f"{ctx}.template")
    lint_latex(d["pitfall"], f"{ctx}.pitfall")
    lint_latex(d["worked"]["trace"], f"{ctx}.worked.trace")
    for i, c in enumerate(d["cues"]):
        lint_latex(c, f"{ctx}.cues[{i}]")
    for i, m in enumerate(d["moves"]):
        lint_latex(m["situation"], f"{ctx}.moves[{i}].situation")
        lint_latex(m["first_line"], f"{ctx}.moves[{i}].first_line")
        lint_latex(m["why"], f"{ctx}.moves[{i}].why")
    return d
