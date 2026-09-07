"""
graph.py — extra edges in the skill graph that aren't implied by a skill's own
`prereqs` / `encompasses` lists (typically links that cross weeks).

Both endpoints must be real skill keys; validated at import.
    kind: "prereq"      — source should be learned before target
          "encompasses" — mastering source implicitly practises target
"""

CROSS_EDGES = [
    # {"source": "w1.limits-basic", "target": "w6.sequences", "kind": "prereq"},
]
