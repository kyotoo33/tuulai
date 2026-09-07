# Architecture

A small, deliberately boring system. The interesting decisions are about *where things live*,
not about frameworks.

```
   content (validated Python)          state (SQLite)
            │                                │
            ▼                                ▼
      backend/content  ──►  backend/main.py (thin FastAPI)  ◄── scheduler · tutor · coach · mock
                                    │
                                    ▼
                       frontend/ (vanilla JS SPA, no build)
```

## The five layers

| Layer | File(s) | Responsibility |
|---|---|---|
| **Validation gate** | `schema.py` | Every content model + a structural LaTeX linter. Nothing enters the system without passing here. |
| **Content** | `content/` | Your course, as importable Python. Assembled and cross-checked once, at boot. |
| **State** | `database.py` | SQLite. Attempts, reviews, errors, mocks. **Never** course material. |
| **Logic** | `scheduler.py`, `tutor.py`, `coach.py`, `mock.py`, `vision.py` | Pure-ish modules with no HTTP knowledge. |
| **Transport** | `main.py`, `frontend/` | A thin API and a build-free SPA. |

## Why content is code, not rows

A database of course material would let you save something broken. Python won't:
`backend/content/__init__.py` assembles everything at import and cross-validates it — a
problem referencing a skill that doesn't exist, a quiz referencing a missing problem, an
unbalanced `$` in a formula, a rubric whose points don't sum. **The app cannot start with
invalid content.**

The payoff: your curriculum is diffable, reviewable and revertible in git, and `make check`
is a compiler for it.

The cost: authoring is editing files, not filling in a web form. For a single learner building
one course, that's the right trade.

## Separation of content and state

Content is immutable input; the database only records *what happened*. Delete
`data/tuulai.db` and you lose your progress but never your course. This is also why keys are
permanent — they're the join between the two halves.

## The invariants

These are the rules the system holds itself to. Several are enforced in code; the rest are
design commitments worth preserving if you fork this.

**Enforced by the schema**

1. Every content object validates at import, or the app doesn't boot.
2. Every LaTeX string is structurally balanced (`$`, `$$`, `\(`, `\[`, braces, `\begin/\end`).
3. Cross-references resolve: problems → skills, quizzes → problems, concepts → skills and live
   problems, playbooks → skills and live problems.
4. `weights` sum to 1.0; part points sum to the problem's points.
5. `mcq` requires options; a resolved auto-gradable problem requires an answer.
6. A concept page needs ≥1 visualization and ≥1 live retrieval problem.
7. Visualization payloads are typed and checked per kind.
8. Only `status: "resolved"` content is served to the learner.

**Enforced by the API**

9. Solutions, answers and rubrics are stripped from every payload until an attempt is logged.
10. A solution unlocks only after a confidence call is recorded.
11. Reading a concept page or a cheatsheet awards **zero** progress. Progress is only ever
    derived from cold retrieval events.

**Design commitments**

12. The tutor hints, never answers.
13. Practice mirrors exam conditions by default (paper, closed-book, timed).
14. No build step, no bundler, no npm. Vendored KaTeX for offline math.
15. Local-first: no accounts, no telemetry, no network required.
16. Every AI feature degrades to a working offline path.

## Request flow

`GET /api/today` → scheduler picks due cards + problems (interleaved, prereq-aware) →
`_safe_problem()` strips solutions → SPA renders.

`POST /api/problems/{key}/reveal` → records the confidence call and opens an attempt → *now*
the solution is returned.

`POST /api/mock/assemble` → `mock.assemble()` picks a balanced set from a coverage window (a
quiz's `covers_weeks`, or a custom `EXAM_SCOPES` entry) → the SPA renders a printable paper.

## The frontend

Three files and no toolchain: `api.js` (fetch wrappers), `viz.js` (the visualization engine),
`app.js` (hash router + views). KaTeX is vendored so math renders offline.

**Cache gotcha:** assets are versioned with a `?v=N` query in `index.html`. Bump it whenever you
edit JS or CSS, or browsers will serve you a stale file and you'll debug a bug you already fixed.

## Extending it

- **New visualization** → `docs/VIZ.md`, "Adding your own primitive".
- **New content type** → add a model + `validate_*()` in `schema.py`, assemble it in
  `content/__init__.py`, expose it in `main.py`, render it in `app.js`. `playbooks` is a
  small, complete worked example of exactly this.
- **New exam scope** → add an entry to `EXAM_SCOPES` in `main.py` for exams that span weeks no
  single quiz window covers.

## Deployment

It's a local app. `make run` serves API and SPA from one process on `127.0.0.1:8642`.

On macOS, `make install-agents` installs two LaunchAgents: a keep-alive for the server and a
daily notification. One hard-won detail baked into `tools/notify/install.sh`: **launchd cannot
write logs into `~/Desktop`, `~/Documents` or `~/Downloads`** (TCC blocks it, and the agent
fails silently with `EX_CONFIG`). Logs go to `~/Library/Logs/`. If you relocate the repo, keep
them there.
