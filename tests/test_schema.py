"""Schema gate tests — the LaTeX linter and cross-field validators must reject bad content."""
import pytest

from backend import schema as S


def test_latex_lint_balanced_ok():
    S.lint_latex(r"For $p \implies q$, the contrapositive is $\lnot q \implies \lnot p$.", "ok")
    S.lint_latex(r"$$\binom{n}{k} = \frac{n!}{k!(n-k)!}$$", "ok")
    S.lint_latex(r"\begin{cases} 1 & x>0 \\ 0 & x\le 0 \end{cases}", "ok")


def test_latex_lint_unbalanced_dollars():
    with pytest.raises(S.ContentError):
        S.lint_latex(r"this $x + 1 has no close", "bad")


def test_latex_lint_unbalanced_braces():
    with pytest.raises(S.ContentError):
        S.lint_latex(r"$\frac{1}{2$", "bad")


def test_latex_lint_env_mismatch():
    with pytest.raises(S.ContentError):
        S.lint_latex(r"\begin{align} x=1 \end{cases}", "bad")


def test_latex_lint_linebreak_spacing_ok():
    # `\\[4pt]` is a line-break spacing directive, NOT a `\[` display-math opener.
    S.lint_latex(r"$\begin{cases} a, & n\ge 2 \\[4pt] 0, & \text{else} \end{cases}$", "ok")


def test_problem_auto_needs_answer():
    with pytest.raises(S.ContentError):
        S.validate_problem({
            "key": "t.1", "origin": "bank", "status": "resolved", "kind": "mcq",
            "topic": "logic", "title": "t", "statement": "pick one",
            "options": ["a", "b"],  # mcq but no answer
        })


def test_problem_points_mismatch():
    with pytest.raises(S.ContentError):
        S.validate_problem({
            "key": "t.2", "origin": "bank", "status": "resolved", "kind": "short",
            "topic": "logic", "title": "t", "statement": "x", "points": 1.0,
            "parts": [
                {"prompt": "a", "points": 0.3, "answer": "1"},
                {"prompt": "b", "points": 0.3, "answer": "2"},  # sums to 0.6 != 1.0
            ],
        })


def test_course_weights_must_sum_to_one():
    with pytest.raises(S.ContentError):
        S.validate_course({
            "code": "X", "title": "t", "term": "t", "start_date": "2026-08-24",
            "n_weeks": 7, "final_week": 8, "weeks": [{"n": 1, "start": "2026-08-24"}],
            "quizzes": [], "weights": {"quizzes": 0.5, "final": 0.3},  # 0.8
            "conditions": [], "grade_scale": {"F": 0}, "miss_rule": "x",
        })


def test_real_content_imports():
    from backend import content as C
    assert C.summary()["skills"] > 0
    assert all(p["status"] == "resolved" for p in C.LIVE_PROBLEMS)


def test_concept_requires_viz_and_retrieval():
    skills = {"w1.x"}; probs = {"bank.p1"}; live = {"bank.p1"}
    base = {"key": "concept.x", "week": 1, "title": "T", "skills": ["w1.x"],
            "blocks": [{"type": "viz", "viz": "venn", "data": {"sets": ["A", "B"], "shaded": ["AB"]}}],
            "retrieval_problems": ["bank.p1"]}
    S.validate_concept(dict(base), skills, probs, live)  # ok
    # no viz -> fails I24
    with pytest.raises(S.ContentError):
        S.validate_concept({**base, "blocks": [{"type": "text", "body": "hi"}]}, skills, probs, live)
    # retrieval problem not live -> fails
    with pytest.raises(S.ContentError):
        S.validate_concept(base, skills, probs, set())
    # unknown skill -> fails
    with pytest.raises(S.ContentError):
        S.validate_concept({**base, "skills": ["w9.nope"]}, skills, probs, live)


def test_viz_payload_validation():
    with pytest.raises(S.ContentError):   # venn wrong set count
        S._check_viz("venn", {"sets": ["A"], "shaded": []}, "ctx")
    with pytest.raises(S.ContentError):   # truthtable ragged row
        S._check_viz("truthtable", {"columns": ["p", "q"], "rows": [["T"]]}, "ctx")
    with pytest.raises(S.ContentError):   # flow edge to unknown node
        S._check_viz("flow", {"nodes": [{"id": "a"}], "edges": [{"from": "a", "to": "z"}]}, "ctx")
    S._check_viz("mapping", {"domain": ["1"], "codomain": ["a"], "maps": [[0, 0]]}, "ctx")  # ok


def test_viz_v2_payloads():
    S._check_viz("pascal", {"rows": 7}, "ctx")                       # ok
    with pytest.raises(S.ContentError):
        S._check_viz("pascal", {"rows": 99}, "ctx")                  # too many rows
    S._check_viz("gridpaths", {"width": 2, "height": 1,
                 "paths": [{"steps": "RRU"}]}, "ctx")                # ok: 2R,1U
    with pytest.raises(S.ContentError):
        S._check_viz("gridpaths", {"width": 2, "height": 1,
                     "paths": [{"steps": "RUU"}]}, "ctx")            # 1R != width 2
    with pytest.raises(S.ContentError):
        S._check_viz("venn", {"sets": ["A", "B", "C"], "shaded": ["XY"]}, "ctx")  # bad region
    S._check_viz("venn", {"sets": ["A", "B", "C"], "shaded": ["ABC", "AB"]}, "ctx")  # ok compound


def test_playbook_validation():
    skills = {"w1.x"}; probs = {"p.1"}; live = {"p.1"}
    base = {
        "key": "play.x", "title": "T", "family": "proofs", "skills": ["w1.x"],
        "one_liner": "start with the definition",
        "cues": ["you see 'injective'"],
        "moves": [{"situation": "goal is injective", "first_line": "Suppose $f(x_1)=f(x_2)$.", "why": "it's a conditional"}],
        "template": "Let $x_1,x_2$.\n[...]",
        "worked": {"anchor": "p.1", "trace": "we open with the definition"},
        "pitfall": "assuming what you want",
        "drills": ["p.1"],
    }
    S.validate_playbook(dict(base), skills, probs, live)               # ok
    with pytest.raises(S.ContentError):                               # unknown skill
        S.validate_playbook({**base, "skills": ["w9.nope"]}, skills, probs, live)
    with pytest.raises(S.ContentError):                               # drill not live
        S.validate_playbook(base, skills, probs, set())
    with pytest.raises(S.ContentError):                               # no moves
        S.validate_playbook({**base, "moves": []}, skills, probs, live)
    with pytest.raises(S.ContentError):                               # bad family
        S.validate_playbook({**base, "family": "misc"}, skills, probs, live)
    with pytest.raises(S.ContentError):                               # unbalanced LaTeX in a first_line
        S.validate_playbook({**base, "moves": [{"situation": "s", "first_line": "$x_1", "why": "w"}]},
                            skills, probs, live)


def test_viz_v4_payloads():
    # plot: single-view shorthand + multi-view with asymptote both ok
    S._check_viz("plot", {"series": [{"kind": "line", "points": [[0, 0], [1, 1]]}]}, "ctx")
    S._check_viz("plot", {"views": [
        {"asymptote": {"y": 0}, "series": [{"points": [[1, 1], [2, 0.5]]}]}]}, "ctx")
    with pytest.raises(S.ContentError):          # a point that isn't an [x,y] pair
        S._check_viz("plot", {"series": [{"points": [[1, 1], [2]]}]}, "ctx")
    with pytest.raises(S.ContentError):          # a view with no series
        S._check_viz("plot", {"views": [{"series": []}]}, "ctx")
    with pytest.raises(S.ContentError):          # non-numeric asymptote
        S._check_viz("plot", {"series": [{"points": [[0, 0]]}], "asymptote": {"y": "x"}}, "ctx")
    # numberline: interval with endpoints, ∞ arrows, and single-point (R=0)
    S._check_viz("numberline", {"min": -2, "max": 2, "views": [
        {"intervals": [{"lo": -1, "hi": 1, "loOpen": True, "hiOpen": True}]},
        {"points": [{"x": 0, "label": "0"}]}]}, "ctx")
    with pytest.raises(S.ContentError):          # min not < max
        S._check_viz("numberline", {"min": 2, "max": 2, "intervals": [{"lo": 0, "hi": 1}]}, "ctx")
    with pytest.raises(S.ContentError):          # a view with neither interval nor point
        S._check_viz("numberline", {"min": -2, "max": 2, "views": [{}]}, "ctx")
    with pytest.raises(S.ContentError):          # non-numeric interval bound
        S._check_viz("numberline", {"min": -2, "max": 2, "intervals": [{"lo": "a", "hi": 1}]}, "ctx")


def test_viz_proofsteps_payloads():
    S._check_viz("proofsteps", {"claim": "$x=1$", "steps": [
        {"line": r"Let $a_n=\sin n$.", "tag": "name it", "mark": "0.2"}]}, "ctx")   # ok
    with pytest.raises(S.ContentError):          # no steps
        S._check_viz("proofsteps", {"steps": []}, "ctx")
    with pytest.raises(S.ContentError):          # step without a line
        S._check_viz("proofsteps", {"steps": [{"tag": "x"}]}, "ctx")
    with pytest.raises(S.ContentError):          # unbalanced LaTeX inside a line
        S._check_viz("proofsteps", {"steps": [{"line": "$x_1"}]}, "ctx")


def test_concept_accepts_module_key():
    skills = {"w1.x"}; probs = {"p.1"}; live = {"p.1"}
    base = {"key": "concept.x", "week": 1, "title": "T", "skills": ["w1.x"],
            "module": "Quiz 1 — proof writing",
            "blocks": [{"type": "viz", "viz": "proofsteps",
                        "data": {"steps": [{"line": r"Let $x=1$.", "tag": "name"}]}}],
            "retrieval_problems": ["p.1"]}
    S.validate_concept(dict(base), skills, probs, live)                 # module allowed
    with pytest.raises(S.ContentError):                                 # unknown key still rejected
        S.validate_concept({**base, "bogus": 1}, skills, probs, live)


def test_viz_reftable_payloads():
    S._check_viz("reftable", {"columns": ["Test", "Converges", "Diverges"],
                 "hide": [1, 2], "rows": [["ratio", "$\\rho<1$", "$\\rho>1$"]]}, "ctx")  # ok
    with pytest.raises(S.ContentError):          # ragged row
        S._check_viz("reftable", {"columns": ["a", "b"], "rows": [["x"]]}, "ctx")
    with pytest.raises(S.ContentError):          # hide index out of range
        S._check_viz("reftable", {"columns": ["a", "b"], "hide": [5], "rows": [["x", "y"]]}, "ctx")
