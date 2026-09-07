# Authoring content

Everything in `backend/content/` is **validated Python**. If it imports, it's structurally
sound. `make check` is your compiler.

```bash
make check    # validates everything, prints a summary
```

A validation error always names the offending key, e.g.
`problem 'ex.mcq-01': kind 'mcq' requires options[]`.

---

## The golden rules

1. **Keys are permanent.** Every skill/problem/card key is the join key to your progress
   database. Renaming one orphans its history. Pick names you can live with.
2. **Only `status: "resolved"` content reaches you.** Park anything unverified as
   `needs_review`. It still validates; it just never appears in a session.
3. **Every concept page must end in retrieval.** Enforced: a page needs ≥1 visualization and
   ≥1 live problem. Reading alone must never count as studying.
4. **LaTeX is linted at import.** Unbalanced `$`, braces or `\begin/\end` fail the boot.

## The bold-and-math gotcha (read this one)

The renderer splits text on `$...$` before applying markdown, so **a bold span cannot contain
inline math**:

```python
r"**the claim $P \to Q$**"        # BROKEN — renders literal asterisks
r"**the claim:** $P \to Q$"       # correct — math outside the bold
```

This is the single most common authoring mistake. Same applies to `*italics*`.

---

## Course

`backend/content/course.py` — one dict. Start here.

| Field | Notes |
|---|---|
| `start_date` | Monday of week 1; the whole scheduler derives from it |
| `weeks[]` | `{n, start, label}` — every week you'll reference |
| `quizzes[]` | `{id, week, covers_weeks, date, duration_min, title}`; `date: None` ⇒ assume Tuesday of that week |
| `weights` | **must sum to exactly 1.0** |
| `conditions[]` | printed on every mock paper — make them match reality |

## Skills and cards

`backend/content/weeks/wN.py` exports `SKILLS` and `CARDS`.

A **skill** is one thing you can be tested on — the unit the scheduler tracks.

```python
{
  "key": "w1.limits-basic",     # permanent
  "week": 1,
  "name": "Evaluating limits",
  "guide_line": "...",          # the syllabus/study-guide phrasing
  "prereqs": [],                # soft gate: scheduler prefers these first
  "encompasses": [],            # mastering this implicitly practises these
  "first_contact": "ex.short-01",   # worked example on first exposure
}
```

A **card** is an open-recall prompt. Genres: `definition`, `theorem`, `technique-choice`,
`example`, `counterexample`, `essence`, `intuition`.

> **Rejected by the validator:** yes/no fronts with a binary back. "Is $f$ continuous?" → "Yes"
> trains recognition, not recall. Ask "State what it means for $f$ to be continuous at $a$."

## Problems

`backend/content/problems/*.py` exports `PROBLEMS`. Register the module in
`backend/content/__init__.py`.

Two behavioural families:

| Family | Kinds | Rule |
|---|---|---|
| **AUTO** | `mcq`, `numeric`, `truefalse`, `match` | machine-checkable; if `status: "resolved"` an `answer` is **required** |
| **OPEN** | `proof`, `short`, `design` | rubric-graded; `answer` optional |

Key fields:

- `origin`: `bank` · `past-quiz` · `ai-variant` · `slide` · `textbook` · `recitation`
- `status`: `resolved` (live) · `needs_review` (parked) · `templated` (stub)
- `difficulty`: `intro` · `core` · `stretch` — mark real exam-bar problems `stretch`
- `parts[]`: `{prompt, points, answer, rubric[]}` — if part points are non-zero they **must
  sum to** the problem's `points`
- `rubric[]`: `{points, criterion}` — write these the way your professor actually marks. If
  hypotheses must be verified before a theorem is applied, make that its own line with its own
  points.
- `mcq` requires `options[]`.

Solutions and answers are stripped by the API until an attempt is logged — that's an
invariant, not a setting.

## Concepts

`backend/content/concepts/*.py` exports `CONCEPTS`. A page is: idea → picture → example →
trap → check → retrieval.

```python
{
  "key": "concept.example.limits",
  "week": 1,
  "module": "Cheatsheet",        # optional: groups pages above the week sections
  "title": "...", "summary": "...",
  "skills": ["w1.limits-basic"],
  "blocks": [ ... ],
  "retrieval_problems": ["ex.short-01"],   # must be LIVE
}
```

Block types:

| Type | Fields | Use |
|---|---|---|
| `text` | `body` | the idea, in as few words as possible |
| `viz` | `viz`, `data`, `caption` | the picture — see [VIZ.md](VIZ.md) |
| `example` | `body` | a concrete instance |
| `trap` | `body` | the specific mistake that loses marks |
| `check` | `prompt`, `answer` | a one-line self-test with a reveal |

**Enforced:** ≥1 `viz` block and ≥1 live `retrieval_problems` entry.

Use `module` to build things like a "Cheatsheet" or an "Exam 1" section — they render above
the week groupings in the index.

## Playbooks

`backend/content/playbooks/*.py` exports `PLAYBOOKS`. Where a concept teaches an *idea*, a
playbook teaches the *move*: recognise the problem type, then write the first line.

```python
{
  "key": "play.example.limits",
  "family": "logic" | "proofs" | "analysis",
  "one_liner": "...",                 # the thing to remember under pressure
  "cues": ["a concrete signal that selects this playbook", ...],
  "moves": [{"situation": "...", "first_line": "...", "why": "..."}],
  "template": "a reusable skeleton with [blanks], \n for line breaks",
  "worked": {"anchor": "<live problem key>", "trace": "narrate the THINKING"},
  "pitfall": "the wrong turn and how to avoid it",
  "drills": ["<live problem keys>"],
}
```

`first_line` is the heart of it: a literal sentence the learner can copy to get unstuck. All
`drills` and `worked.anchor` must be live problems.

## Past papers

`backend/content/quizzes/past.py` exports `QUIZZES`. Transcribe real papers — they show the
exact phrasing, weighting and rigour your course expects, which is worth more than any
textbook exercise. Every key in `problems` must exist.

---

## A sane workflow

1. Author the syllabus. `make check`.
2. Add one week of skills and cards. `make check`.
3. Add problems for that week, newest-exam-style first. `make check`.
4. Add a concept page only where an idea genuinely needs a picture.
5. `make dev` and use it.

Add content in small batches and run `make check` constantly — the validator is fast and its
errors are precise. Fixing one bad problem at authoring time costs seconds; discovering it
mid-revision costs a session.
