# Mastery-Platform Mechanics: Research Report

> Research report compiled for the Tuulai learning-workspace design.

## 1. Math Academy

**Core mechanisms:**
- **Knowledge graph with two link types.** A prerequisite graph (learn-before ordering) plus a separate *encompassing graph* (which advanced topics implicitly practice which simpler ones, with fractional weights for partial coverage). "Thousands of linked topics"; content is ~10x more finely scaffolded than textbooks (~1000 steps for calculus vs ~100).
- **FIRe (Fractional Implicit Repetition) + spaced repetition compression.** Passing a review on an advanced topic trickles credit *down* to encompassed prerequisites (multiple layers deep); failing propagates penalties *up* to dependent topics. The scheduler deliberately picks reviews that "knock out other due reviews like dominoes" — this is why doing new lessons counts as review ("layering") and why students aren't buried in ~60 explicit review questions/day the way flat Anki-style scheduling would produce. Memory decays as (0.5)^(days/interval); per student-per-topic speed ratios scale credit (2x learner gets double credit; below 1x, implicit credit is *discarded* and explicit review forced — struggling students don't get to coast on implicit practice).
- **Adaptive diagnostic** (30–45 min) measuring both mastery and automaticity, producing placement + per-topic mastery estimates + foundational gap list.
- **Lessons = worked example → up to 5 practice problems; advance on 2 consecutive correct.** Pure explicit instruction; they explicitly reject discovery learning citing the expertise-reversal effect and worked-example effect ("minimal instructional guidance leads to minimal learning").
- **XP economy + timed closed-book quizzes.** 1 XP ≈ 1 minute of focused work; adjustable daily XP goal (reviewers settle around 50–90 XP/day); a timed, no-reference quiz fires **every 150 XP** covering recent topics; missed quiz topics immediately become assigned reviews; retake available after review for bonus XP.

**What works (user reports):** procedural fluency genuinely builds; the diagnostic + forced review loop rebuilds rusty skills; daily-quota + leaderboard loop sustains consistency; claimed outcomes (pre-algebra→BC Calc in one year) are impressive but self-reported.

**What fails (credible critiques — Oz Nova, nor's blog, Frank Hecker):**
- **Proof-writing is the weak spot**: proof lessons are "rote templates," too few and insufficiently rigorous — directly relevant to discrete math.
- **Grind fatigue**: "feels like test prep," excessive near-identical variations; Hecker deliberately throttled to 50 XP/day to avoid burnout.
- **No connective tissue**: no motivation, no thematic narrative, "doesn't connect the dots."
- **Rigid dependency enforcement**: one bad diagnostic answer can trigger "years of unnecessary remedial prerequisites"; no skip button; alternative valid topic orderings are disallowed.
- **Speed emphasis**: per-question timing punishes slow-but-correct reasoning.

**Design implications:** FIRe's key insight is directly stealable — with a prerequisite/encompassing graph over the 388-problem bank's topics, *new hard problems can count as implicit review of everything they encompass*, keeping daily review load tiny in a 7-week window. Copy: the 150-XP-style cadence of timed closed-book quizzes (matches the actual grading instrument!), missed-quiz-topic → forced review, per-topic mastery decay. Avoid: rigid no-skip remediation (7 weeks can't afford false-positive gap detection), and don't rely on it for proof-writing — that needs a separate mechanism (self-explanation, graded written proofs).

Sources: https://www.mathacademy.com/pedagogy · https://www.mathacademy.com/how-it-works · https://www.justinmath.com/individualized-spaced-repetition-in-hierarchical-knowledge-structures/ · https://www.justinmath.com/the-tip-of-math-academys-technical-iceberg/ · https://newsletter.ozwrites.com/p/a-balanced-review-of-math-academy · https://nor-blog.pages.dev/posts/2025-04-16-mathacademy/ · https://frankhecker.com/2025/02/18/math-academy-part-11/

## 2. ALEKS / Knowledge Space Theory

**Core mechanisms:**
- **Knowledge states, not topic scores**: KST (Doignon & Falmagne) models the feasible subsets of topics a student can know; the actionable outputs are the **outer fringe** ("ready to learn next") and inner fringe.
- **Markovian adaptive assessment**: pins down one state among millions in ~25–30 questions; open-response (no multiple choice), no partial credit.
- **Periodic re-assessment ("Knowledge Checks")** that can *remove* previously mastered topics from the student's state.

**Works:** the "ready to learn" frontier concept is the cleanest formalism for "what should I attempt next"; placement accuracy is well validated; millions of users across math/chem/stats.

**Fails:** Knowledge Checks are the #1 hated feature — forgetting 2–3 topics can wipe out 50+ topics of credited progress (the state model assumes correlated gaps), which students experience as punitive progress erasure; 5-minute lessons are shallow; only final answers assessed, no metacognition; research shows the core BLIM independence assumptions are questionably calibrated (careless-error/lucky-guess rates).

**Design implications:** steal the *fringe* concept — always surface the small set of problem-bank topics whose prerequisites are all mastered. But make re-assessment *granular*: demote only the topic actually failed (plus flagged dependents for cheap spot-checks), never bulk-erase progress — in a 7-week course, morale-destroying resets are fatal.

Sources: https://www.aleks.com/about_aleks/knowledge_space_theory · https://www.sciencedirect.com/science/article/abs/pii/S0022249621000134 · https://finishmymathclass.com/complete-guide-to-aleks-knowledge-checks/ · https://arxiv.org/pdf/1607.07284

## 3. Brilliant.org

**Core mechanisms:** problem-first interactive lessons (question before explanation); heavy visual/manipulative interactivity; bite-sized incremental sequences; streak gamification. Notably absent: spaced review, mastery gating, retrieval practice of old material.

**Works:** genuinely good at *first-contact intuition* and motivation; lowers activation energy.

**Fails:** consensus across reviews: shallow introductions, "enjoyed it but don't feel they got results," no mechanism forcing recall after a lesson ends → engagement without retention; one-way learning with no feedback on your reasoning. Best understood as an intuition-priming layer, not a mastery system.

**Design implication:** the interactive "try it before being told" moment is fine as a *lesson opener* for a new discrete-math topic, but the workspace's spine must be retrieval + spacing, not interaction. Brilliant is the cautionary tale: polished interaction that never demands closed-book reproduction produces exactly the failure mode a handwritten quiz punishes.

Sources: https://learnopoly.com/brilliant-org-review/ · https://news.ycombinator.com/item?id=29881011 · https://brighterly.com/blog/is-brilliant-org-worth-it/

## 4. Execute Program (Gary Bernhardt)

**Core mechanisms:**
- **Hard gating: reviews come before new content**, and the platform rate-limits progress — you *cannot* binge a course; ~20 min/day over weeks by design.
- Hundreds of tiny interactive code examples of slowly increasing complexity (answers are executed, not multiple-choice).
- Simple expanding intervals; a failed item restarts its interval ladder; items retire after mastery at day 64; missed answers don't punish unless you give up; progression rewards *completing new lessons* over stretching recall intervals.

**Works:** users report durable "I just know it" fluency after months; forcing distribution-over-time is the entire product thesis and it demonstrably prevents the binge-and-forget pattern.

**Fails:** scheduler is "crude relative to Anki" (no per-item difficulty grading); same-day clustering of related reviews makes them artificially easy (cueing); permanent retirement at day 64 assumes usage in real life continues the practice.

**Design implication:** the single most transferable *policy*: **the day's session opens with due reviews; new content unlocks only after they're cleared.** Also steal the calendar realism — a 7-week plan should be laid out as forced daily distribution, front-loading new topics in weeks 1–5 so weeks 6–7 are mostly review at long intervals. Avoid same-day clustering of same-topic reviews (interleave instead).

Sources: https://www.executeprogram.com/why-ep · https://mike.place/2020/executeprogram/ · https://notes.andymatuschak.org/z2LGZ8cXBcQMP7YuAHbeVyCSLZoiMXvQNKCok

## 5. Khan Academy mastery + Duolingo learning science

**Khan:** per-skill ladder Attempted→Familiar (50 pts)→Proficient (80)→Mastered (100); you can only reach Mastered via *mixed-skill assessments* (mastery challenges/unit tests), not by re-grinding the same exercise — a clean anti-gaming device. Their research: skills-brought-to-*proficient* correlates with external test growth (MAP); their explicit finding — **fewer skills to proficient beats many skills to familiar**. Weakness: mastery decay/review is weak, gamification is skippable, so most learners never close loops.

**Duolingo:** Half-Life Regression — a trainable model of per-item memory half-life (practice history + item features), 45% error reduction in recall prediction, +12% engagement in A/B test — the serious science. Streaks work via loss aversion and do build the daily habit; but the documented failure mode is **streak-preserving speedruns of easy content**: engagement metrics diverge from learning at the edges, and gamification demonstrably drives usage, not proficiency. Streak freezes exist because brittle streaks cause quit-on-break.

**Design implications:** (a) score the student's week in "skills brought to proficient," verified only by *mixed, closed-book* checks, never by same-context repetition; (b) a light streak/daily-quota is worth having for a 7-week sprint, but make the unit of credit *quiz-condition performance*, so the streak can't be fed with junk work; forgive single missed days.

Sources: https://blog.khanacademy.org/why-khan-academy-will-be-using-skills-to-proficient-to-measure-learning-outcomes/ · https://support.khanacademy.org/hc/en-us/articles/5548760867853 · https://research.duolingo.com/papers/settles.acl16.pdf · https://github.com/duolingo/halflife-regression · https://thedecisionlab.com/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification

## 6. Olympiad training culture

**Core practices worth stealing:**
- **Error log / mistake notebook as the central artifact**: every miss recorded with *the specific lesson it taught*, reviewed weekly — "a diagnostic database of preparation gaps," not a list of failures.
- **Full past papers under strict exam conditions** (exact time limit, no references, handwritten) — pacing and pressure tolerance are trained skills untimed practice cannot build; ramping to 3–4 timed simulations/week in the final stretch.
- **Quality over volume**: 30 problems/week with full post-mortem beats 100 without reflection.
- **Blocked-then-mixed drilling**: topic-focused runs to build problem-type recognition, then mixed sets.

**Design implication:** this maps one-to-one onto the situation — 5 semesters of past quizzes = past papers; weekly quiz = the competition. The workspace should treat **weekly timed handwritten mock quizzes from past papers + a structured error log (miss → classified cause → regenerated variant from the 388-problem parameterized bank)** as its capstone loop, with the spaced-repetition engine feeding it. The parameterized bank is ideal for regenerating fresh variants of exactly the problems previously missed.

Sources: https://gonit.app/how-to-prepare-for-the-junior-math-olympiad/ · https://descartes-learningcentre.com/how-to-prepare-for-the-math-olympiad-15-expert-tricks/ · https://store.pw.live/blogs/olympiad-exams/time-management-tips-for-olympiad-exams

## Cross-cutting synthesis

1. **The consensus core** (Math Academy + Execute Program + ALEKS agree): prerequisite graph → diagnostic → reviews-gate-new-content → mastery thresholds verified under retrieval conditions. Every platform that skips retrieval-under-test-conditions (Brilliant, most Khan usage) produces the engagement-without-retention failure.
2. **The 7-week twist**: standard SRS intervals (weeks→months) don't fit; the target memory horizon is "next quiz plus finals." FIRe's implicit-credit idea matters more than long intervals: harder multi-concept problems from the bank should discharge review debt on their components.
3. **The quiz *is* the format**: because grading is closed-book handwritten, all mastery checks should be handwritten, timed, no-reference — Math Academy's every-150-XP quiz cadence, olympiad exam-condition simulation, and the error-log loop are the three mechanisms most aligned with the grade.
4. **Known failure modes to engineer against**: grind fatigue (cap daily quota, Hecker-style), false-gap remediation spirals (make demotion granular and appealable, anti-ALEKS), template-proof weakness (proofs need human/AI grading of written arguments, not answer-matching), and streak theater (credit only quiz-condition work).
