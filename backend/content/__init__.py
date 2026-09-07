"""
content/__init__.py — assembly + validation (Atlas playbook §4).

Import this module and the entire curriculum is validated. A typo anywhere fails the boot,
not a review session three weeks later. Everything below is derived at assembly time, never
at request time. Deterministic keys are the join to the state DB.

Exports:
    COURSE                         validated syllabus dict
    SKILLS      list[dict]         all skills, week-ordered
    SKILLS_BY_KEY dict             key -> skill
    CARDS       list[dict]         all cards
    CARDS_BY_KEY dict              key -> card
    PROBLEMS    list[dict]         all resolved problems (needs_review excluded from LIVE)
    PROBLEMS_BY_KEY dict           key -> problem
    LIVE_PROBLEMS list[dict]       status == 'resolved' only
    QUIZZES     list[dict]         past papers + assembled mocks
    QUIZZES_BY_KEY dict
    GRAPH       dict               {nodes, edges} unified skill graph
    problems_for_skill(key)        -> list[problem]
    skills_for_week(n)             -> list[skill]
"""
from __future__ import annotations

from backend import schema as S
from backend.content import graph as _graph
from backend.content.course import COURSE as _COURSE_RAW
from backend.content.quizzes import past as _past
from backend.content.weeks import w1

# ── course ───────────────────────────────────────────────────────────────────
COURSE = S.validate_course(_COURSE_RAW)

# ── skills ───────────────────────────────────────────────────────────────────
_WEEK_MODULES = [w1]          # add w2, w3, ... as you author them
SKILLS = [S.validate_skill(sk) for m in _WEEK_MODULES for sk in m.SKILLS]
SKILLS_BY_KEY = {sk["key"]: sk for sk in SKILLS}
if len(SKILLS_BY_KEY) != len(SKILLS):
    raise S.ContentError("duplicate skill key detected")

# ── cards ────────────────────────────────────────────────────────────────────
CARDS = [S.validate_card(c) for m in _WEEK_MODULES for c in m.CARDS]
CARDS_BY_KEY = {c["key"]: c for c in CARDS}
if len(CARDS_BY_KEY) != len(CARDS):
    raise S.ContentError("duplicate card key detected")
for c in CARDS:
    if c["skill"] not in SKILLS_BY_KEY:
        raise S.ContentError(f"card '{c['key']}' references unknown skill '{c['skill']}'")

# ── problems ─────────────────────────────────────────────────────────────────
_PROBLEM_MODULES = []
for _modname in ("example",):          # add each problems module you author
    try:  # AI-resolved batches — present once each resolver workflow has run
        _m = __import__(f"backend.content.problems.{_modname}", fromlist=["PROBLEMS"])
        _PROBLEM_MODULES.append(_m)
    except ImportError:
        pass
PROBLEMS = [S.validate_problem(p) for m in _PROBLEM_MODULES for p in m.PROBLEMS]
PROBLEMS_BY_KEY = {p["key"]: p for p in PROBLEMS}
if len(PROBLEMS_BY_KEY) != len(PROBLEMS):
    raise S.ContentError("duplicate problem key detected")
for p in PROBLEMS:
    for sk in p["skills"]:
        if sk not in SKILLS_BY_KEY:
            raise S.ContentError(f"problem '{p['key']}' references unknown skill '{sk}'")
# LIVE = only human-cleared problems reach the queue (README §5).
LIVE_PROBLEMS = [p for p in PROBLEMS if p["status"] == "resolved"]

# first_contact refs must resolve
for sk in SKILLS:
    fc = sk.get("first_contact")
    if fc and fc not in PROBLEMS_BY_KEY:
        raise S.ContentError(
            f"skill '{sk['key']}' first_contact '{fc}' is not a known problem"
        )

# ── quizzes ──────────────────────────────────────────────────────────────────
QUIZZES = [S.validate_quiz(q) for q in _past.QUIZZES]
QUIZZES_BY_KEY = {q["key"]: q for q in QUIZZES}
for q in QUIZZES:
    for pk in q["problems"]:
        if pk not in PROBLEMS_BY_KEY:
            raise S.ContentError(f"quiz '{q['key']}' references unknown problem '{pk}'")

# ── unified graph ────────────────────────────────────────────────────────────
_nodes = [{"id": sk["key"], "week": sk["week"], "name": sk["name"]} for sk in SKILLS]
_edges = []
for sk in SKILLS:
    for pr in sk.get("prereqs", []):
        _edges.append({"source": pr, "target": sk["key"], "kind": "prereq"})
    for en in sk.get("encompasses", []):
        _edges.append({"source": sk["key"], "target": en, "kind": "encompasses"})
_edges.extend(_graph.CROSS_EDGES)
GRAPH = S.validate_graph({"nodes": _nodes, "edges": _edges}, set(SKILLS_BY_KEY))

# ── concepts (docs/concepts-plan.md) ─────────────────────────────────────────
_CONCEPT_MODULES = []
for _cn in ("example",):               # add each concepts module you author
    try:
        _cm = __import__(f"backend.content.concepts.{_cn}", fromlist=["CONCEPTS"])
        _CONCEPT_MODULES.append(_cm)
    except ImportError:
        pass
_live_keys = {p["key"] for p in LIVE_PROBLEMS}
CONCEPTS = [
    S.validate_concept(c, set(SKILLS_BY_KEY), set(PROBLEMS_BY_KEY), _live_keys)
    for m in _CONCEPT_MODULES for c in m.CONCEPTS
]
CONCEPTS_BY_KEY = {c["key"]: c for c in CONCEPTS}
if len(CONCEPTS_BY_KEY) != len(CONCEPTS):
    raise S.ContentError("duplicate concept key detected")
# skill -> its concept (first concept listing that skill), for first-contact routing
CONCEPT_FOR_SKILL = {}
for c in CONCEPTS:
    for sk in c["skills"]:
        CONCEPT_FOR_SKILL.setdefault(sk, c["key"])


# ── playbooks (recitation-derived "how to start" strategies) ─────────────────
_PLAYBOOK_MODULES = []
for _pn in ("example",):               # add each playbooks module you author
    try:
        _pm = __import__(f"backend.content.playbooks.{_pn}", fromlist=["PLAYBOOKS"])
        _PLAYBOOK_MODULES.append(_pm)
    except ImportError:
        pass
PLAYBOOKS = [
    S.validate_playbook(pb, set(SKILLS_BY_KEY), set(PROBLEMS_BY_KEY), _live_keys)
    for m in _PLAYBOOK_MODULES for pb in m.PLAYBOOKS
]
PLAYBOOKS_BY_KEY = {pb["key"]: pb for pb in PLAYBOOKS}
if len(PLAYBOOKS_BY_KEY) != len(PLAYBOOKS):
    raise S.ContentError("duplicate playbook key detected")
# skill -> its playbook (first listing that names the skill), for problem→playbook routing
PLAYBOOK_FOR_SKILL = {}
for pb in PLAYBOOKS:
    for sk in pb["skills"]:
        PLAYBOOK_FOR_SKILL.setdefault(sk, pb["key"])


# ── derived accessors (assembly-time helpers, cheap at request time) ─────────
def playbook_for_skill(skill_key: str) -> dict | None:
    pk = PLAYBOOK_FOR_SKILL.get(skill_key)
    return PLAYBOOKS_BY_KEY.get(pk) if pk else None


def playbooks_for_family(family: str) -> list[dict]:
    return [pb for pb in PLAYBOOKS if pb["family"] == family]


def concept_for_skill(skill_key: str) -> dict | None:
    ck = CONCEPT_FOR_SKILL.get(skill_key)
    return CONCEPTS_BY_KEY.get(ck) if ck else None


def concepts_for_week(n: int) -> list[dict]:
    return [c for c in CONCEPTS if c["week"] == n]
def problems_for_skill(skill_key: str, live_only: bool = True) -> list[dict]:
    pool = LIVE_PROBLEMS if live_only else PROBLEMS
    return [p for p in pool if skill_key in p["skills"]]


def skills_for_week(n: int) -> list[dict]:
    return [sk for sk in SKILLS if sk["week"] == n]


def skills_for_quiz(quiz_id: str) -> list[dict]:
    q = next((qz for qz in COURSE["quizzes"] if qz["id"] == quiz_id), None)
    if not q:
        return []
    weeks = set(q["covers_weeks"])
    return [sk for sk in SKILLS if sk["week"] in weeks]


def summary() -> dict:
    return {
        "skills": len(SKILLS),
        "cards": len(CARDS),
        "problems": len(PROBLEMS),
        "live_problems": len(LIVE_PROBLEMS),
        "quizzes": len(QUIZZES),
        "concepts": len(CONCEPTS),
        "playbooks": len(PLAYBOOKS),
        "graph_nodes": len(GRAPH["nodes"]),
        "graph_edges": len(GRAPH["edges"]),
    }
