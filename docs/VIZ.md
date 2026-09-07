# Visualization primitives

Ten data-driven primitives, implemented in `frontend/static/js/viz.js` and validated at import
by `schema._check_viz`. You author a payload; the engine renders it. No drawing code in content.

See them all rendered live at **Concepts → Reference → Visualization gallery**
(`concept.example.gallery`) — delete that page once you know the payloads.

Authored strings in a payload (table cells, `proofsteps` claims/lines/tags, column headers)
go through the same markdown+math renderer as concept prose, so `**bold**` and `$math$` both
work — and may be combined.

A viz block inside a concept page looks like:

```python
{"type": "viz", "viz": "<kind>", "data": { ... }, "caption": r"optional, LaTeX ok"}
```

Cell/label strings may contain LaTeX (`$...$`); it's rendered with KaTeX.

---

## `truthtable`

Logic tables with a predict/reveal toggle.

```python
{"columns": [r"$p$", r"$q$", r"$p \wedge q$"],
 "inputs": 2,          # first N columns are inputs (shaded)
 "match": [2],         # column indices to box (e.g. the two that agree)
 "rows": [["T","T","T"], ["T","F","F"], ["F","T","F"], ["F","F","F"]]}
```
Every row must have exactly `len(columns)` cells.

## `venn`

Two or three sets; shade any region, including compound ones.

```python
{"sets": ["A", "B"], "shaded": ["AB"]}
{"sets": ["A", "B", "C"], "shaded": ["ABC", "AB"]}
```
Valid region ids — 2 sets: `A`, `B`, `AB`, `U` · 3 sets: `A`, `B`, `C`, `AB`, `AC`, `BC`,
`ABC`, `U`. (`U` = outside everything.)

## `mapping`

Domain → codomain arrows, with an optional variant switcher. Ideal for
injective/surjective/bijective.

```python
{"domain": ["1","2","3"], "codomain": ["a","b"],
 "variants": [{"label": "surjective", "maps": [[0,0],[1,1],[2,1]]},
              {"label": "not surjective", "maps": [[0,0],[1,0],[2,0]]}]}
```
`maps` are `[domain_index, codomain_index]` pairs; indices must be in range. A single-variant
payload may use `"maps"` at the top level instead.

## `flow`

A layered decision tree (longest-path layout). The best primitive for "which technique?".

```python
{"nodes": [{"id": "q", "label": "Indeterminate?", "kind": "decision"},
           {"id": "f", "label": "Factor", "kind": "leaf"}],
 "edges": [{"from": "q", "to": "f", "label": "yes"}],
 "start": "q"}
```
`kind`: `decision` (neutral) or `leaf` (highlighted endpoint). Every edge endpoint must be a
declared node id.

## `pascal`

Pascal's triangle. Hovering a cell lights its two parents; a toggle overlays row sums $2^n$.

```python
{"rows": 7}      # integer, 1..14
```

## `gridpaths`

Lattice paths as R/U words — combinatorics, Catalan, stars-and-bars.

```python
{"width": 4, "height": 4, "diagonal": True,
 "paths": [{"label": "stays below", "steps": "RRUURRUU", "valid": True},
           {"label": "crosses",     "steps": "URRUURRU", "valid": False}]}
```
`steps` must contain exactly `width` R's and `height` U's (validated). `valid: False` draws the
path in the warning colour.

## `plot`

Points/lines on auto-scaled axes with an optional dashed limit line and a view switcher. Each
view reframes to its own data.

```python
{"xlabel": "n",
 "views": [
   {"label": r"$a_n = 1/n$",
    "asymptote": {"y": 0, "label": "L = 0"},        # plain text label
    "series": [{"label": r"$a_n$", "kind": "points", "cls": "good",
                "points": [[1,1],[2,0.5],[3,0.333]]}]},
 ]}
```
- `kind`: `points` or `line`
- `cls`: `good` (accent) · `bad` (warning) · `alt` · `warm` · `target` (heavy neutral)
- points are `[x, y]` numeric pairs
- a single-view payload may use top-level `series` / `asymptote`

Author the sample points yourself — the renderer does no maths, which keeps content verifiable.

## `numberline`

Intervals with open/closed endpoints and ∞-arrows. Built for radius/interval of convergence.

```python
{"min": -4, "max": 4, "ticks": [-3,-2,-1,0,1,2,3],
 "views": [
   {"label": r"$R=1$", "note": r"Endpoints must be tested separately.",
    "intervals": [{"lo": -1, "hi": 1, "loOpen": True, "hiOpen": True,
                   "cls": "good", "label": "converges"}]},
   {"label": r"$R=\infty$",
    "intervals": [{"lo": -4, "hi": 4, "arrowLo": True, "arrowHi": True, "cls": "good"}]},
   {"label": r"$R=0$", "points": [{"x": 0, "label": "only x = 0", "cls": "center"}]},
 ]}
```
Each view needs at least one interval or point. `arrowLo/arrowHi` replace the endpoint dot with
an arrow (extends forever).

## `reftable`

A reference table whose answer columns can be hidden — turns a cheatsheet into a recall drill.

```python
{"columns": ["Test", "Hypotheses", "Verdict"],
 "hide": [1, 2],          # column indices blanked in Predict mode
 "rows": [[r"Ratio", r"$a_n \ne 0$", r"$\rho<1$ converges"], ...]}
```
Rows must match the column count; `hide` indices must be in range. This is the workhorse for
formula sheets, identity tables and test handbooks.

## `proofsteps`

An annotated model proof: each line paired with the rubric reason it earns marks. A toggle
hides the lines so the learner rewrites the proof from the reasons alone.

```python
{"claim": r"There are infinitely many primes.",
 "steps": [
   {"line": r"Suppose, for contradiction, there are finitely many $p_1,\dots,p_n$.",
    "tag": "the exact negation", "mark": "0.25"},
   {"line": r"$N = p_1p_2\cdots p_n + 1.$",
    "tag": "construct the witness", "mark": "0.25"},
 ]}
```
`tag` and `mark` are optional. This is the primitive to reach for when a course grades *proof
rigour* rather than final answers.

---

## Reserved kinds

`graph` and `tiling` are accepted by the validator but have **no renderer yet** — a page using
them shows a "not available" placeholder. Implement them in `viz.js` and add them to the `VIZ`
map if you need them.

## Adding your own primitive

1. **Validate** — add a branch to `_check_viz` in `backend/schema.py` and register the name in
   `VIZ_KINDS`.
2. **Render** — write `vizYourKind(el, data)` in `frontend/static/js/viz.js` and add it to the
   `VIZ` map at the bottom.
3. **Style** — add CSS in `frontend/static/css/app.css` using the existing theme variables
   (`--accent`, `--ink`, `--paper`, …) so it works in light and dark automatically.
4. **Bump the asset version** — the `?v=N` query on the script/style tags in
   `frontend/index.html`. Browsers cache these aggressively.

Keep primitives *data-driven and pure*: no animation loops, no computation the content author
can't verify by reading the payload.
