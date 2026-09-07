# Tuulai

**A solo learning workspace for a hard course.** You point it at one course, author your
syllabus and problems as code, and it runs three loops for you: daily retrieval, full-dress
mock exams, and a weekly coach that tells you where you're actually weak.

It is deliberately *not* a course platform. One learner, one course, local-first, no accounts,
no cloud, no build step. Clone it, fill in your material, run it on your laptop.

> This repository is a **template**. The content you'll find in it (`MATH 101`, limits and
> derivatives) is a worked example so that everything boots and renders on first run. Replace
> it with your own course — see **[Adapting it to your course](#adapting-it-to-your-course)**.

---

## Why it's built the way it is

Most study tools optimise for feeling productive. This one optimises for the thing that
actually moves exam performance, which the evidence is unusually consistent about:

1. **Retrieval beats review.** Reading notes feels like learning and mostly isn't. Every page
   here ends in a problem you must attempt cold — a rule enforced by the schema, not by
   willpower.
2. **Practise under the real conditions.** If the exam is closed-book, handwritten and timed,
   then practice that isn't closed-book, handwritten and timed is training a different skill.
   The mock loop prints a real paper you do on paper.
3. **Spacing and interleaving.** The scheduler mixes topics and re-tests you at widening
   intervals rather than letting you block-practise one chapter into a false sense of mastery.
4. **Calibration.** Before revealing a solution you must commit a confidence call. Being
   *confidently wrong* is the most expensive failure mode in an exam, and it's invisible
   unless you measure it.
5. **The tutor guides, it never answers.** Hints climb a ladder; solutions unlock only after a
   logged attempt. A model that hands you answers trains dependence.

Longer write-ups of the evidence are in [`research/`](research/), and the principles are
distilled in [`docs/PEDAGOGY.md`](docs/PEDAGOGY.md).

## The three loops

| Loop | Cadence | What it does |
|---|---|---|
| **Daily retrieval** | every day | A short queue of due cards and problems, interleaved across topics, scheduled by a successive-relearning model. |
| **Mock exam** | weekly / pre-exam | Assembles a real paper from your problem bank, prints it, times you. You photograph your handwritten work and it's graded against the rubric (or you self-grade). |
| **Weekly coach** | weekly | Reads your attempt history and reports calibration, hint-dependence, paper-vs-typed gaps, and the skills most at risk before the next assessment. |

## Quickstart

```bash
make setup      # create .venv and install dependencies
make check      # validate all content — should print a summary
make test       # run the test suite
make dev        # start the app with auto-reload
```

Then open **http://127.0.0.1:8642**.

`make check` is the important one. All content is validated *at import*: a malformed problem,
a broken LaTeX expression or a reference to a skill that doesn't exist will fail the boot
immediately, not silently corrupt a revision session three weeks later.

## Adapting it to your course

Work in this order — each step boots and validates on its own.

1. **`backend/content/course.py`** — your syllabus: weeks, quiz dates, what each assessment
   covers, weights, and the exam conditions. Everything downstream derives from this.
2. **`backend/content/weeks/w1.py`** — your skills (the schedulable atoms) and cards. Copy the
   file for each week and register it in `backend/content/__init__.py`.
3. **`backend/content/problems/example.py`** — your problems. This is the bulk of the work and
   where the value is. Past papers are worth more than textbook exercises.
4. **`backend/content/concepts/example.py`** — explainer pages with visualizations. Optional,
   but this is what makes an idea click.
5. **`backend/content/playbooks/example.py`** — "how to start" strategies. Optional, and the
   single best cure for staring at a blank page.

Full field-by-field reference: **[`docs/AUTHORING.md`](docs/AUTHORING.md)**.

Delete `concept.example.gallery` once you've seen the visualization primitives render — it
exists only as a live catalogue.

## Project structure

```
backend/
  schema.py        the validation gate — every content model + a LaTeX linter
  content/         YOUR COURSE lives here (validated Python, not a database)
  database.py      SQLite: attempts, reviews, errors — state only, never content
  scheduler.py     spacing, interleaving, readiness, urgency before an assessment
  mock.py          exam assembly + photo transcription/grading orchestration
  tutor.py         the hint ladder (degrades gracefully with no API key)
  coach.py         the weekly report
  vision.py        provider-agnostic multimodal grading (Anthropic or OpenAI-compatible)
  main.py          thin FastAPI layer — serves the API and the SPA
frontend/          no build step: vanilla JS + CSS + vendored KaTeX
  static/js/viz.js the visualization engine (10 primitives)
tools/notify/      macOS LaunchAgents: keep-alive server + a daily nudge
tests/             schema, scheduler, mock and coach tests
docs/              authoring, architecture, visualization and pedagogy references
research/          the evidence base the design is built on
```

## Content as code, state in SQLite

Course material is **validated Python**, not database rows. That means your curriculum is
diffable, reviewable in git, and impossible to half-break: if it imports, it's structurally
sound and every LaTeX string is balanced.

The database holds only *what happened* — attempts, confidence calls, review history, errors.
You can delete `data/tuulai.db` and lose your progress but never your course.

## Optional: AI features

Everything works without an API key; these features simply degrade.

| Feature | Without a key | With a key |
|---|---|---|
| Hints | templated ladder | model-generated, still answer-free |
| Mock grading | you self-grade against the rubric | photo → transcription → rubric grading |
| Weekly coach | templated report | narrative report |

```bash
export ANTHROPIC_API_KEY=...     # or OPENAI_API_KEY / an OpenAI-compatible endpoint
```

Never commit keys. `.env` and `data/` are git-ignored.

## Documentation

- **[docs/AUTHORING.md](docs/AUTHORING.md)** — every content type, field by field, with the gotchas
- **[docs/VIZ.md](docs/VIZ.md)** — all 10 visualization primitives and their payloads
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — the layers and the invariants that hold it together
- **[docs/PEDAGOGY.md](docs/PEDAGOGY.md)** — the learning-science principles, and what to avoid

## A note on other people's material

Your professor's problem bank, past papers and slides are almost certainly **copyrighted**.
Keeping them in a private working copy for your own study is one thing; publishing them in a
public repository is another. This template ships with none of that, and `.gitignore` excludes
`vendor/` and `data/` by default. Keep it that way.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, adapt it to your own course.
