"""Coach analysis tests — calibration, hint velocity, modality."""
from backend import coach


def _a(confidence, result, mode="paper", hints_used=0, problem_key="p"):
    return {"confidence": confidence, "result": result, "mode": mode,
            "hints_used": hints_used, "problem_key": problem_key}


def test_calibration_flags_confident_wrong():
    attempts = [
        _a("sure", "correct", problem_key="a"),
        _a("sure", "wrong", problem_key="b"),      # confident-wrong
        _a("sure", "partial", problem_key="c"),    # confident-wrong (not fully correct)
        _a("guess", "correct", problem_key="d"),   # underconfident
    ]
    cal = coach.calibration(attempts)
    assert set(cal["confident_wrong"]) == {"b", "c"}
    assert cal["underconfident"] == ["d"]
    assert cal["buckets"]["sure"]["accuracy"] == 33   # 1 of 3


def test_hint_velocity():
    attempts = [_a("sure", "correct", hints_used=0), _a("shaky", "partial", hints_used=3),
                _a("shaky", "wrong", hints_used=2)]
    hv = coach.hint_velocity(attempts)
    assert hv["hint_heavy"] == 2
    assert hv["cold_rate"] == 33


def test_modality():
    attempts = [_a("sure", "correct", mode="paper"), _a("sure", "correct", mode="typed"),
                _a("sure", "correct", mode="paper")]
    m = coach.modality(attempts)
    assert m["paper"] == 2 and m["typed"] == 1 and m["paper_rate"] == 67


def test_templated_narrative_mentions_confident_wrong():
    r = {"quiz": {"target": "quiz-1", "days_until": 10, "solid": 2, "total": 14},
         "calibration": {"confident_wrong": ["x", "y"]}, "at_risk": [],
         "week_active_days": 3, "modality": {"paper_rate": 90}, "errors": {"due_now": 1}}
    note = coach._templated_narrative(r)
    assert "confident" in note.lower() and "quiz-1" in note
