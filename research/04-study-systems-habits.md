# Solo Study Systems, Exam Simulation, and System Survival

> Research report compiled for the Tuulai learning-workspace design.
> Confidence tiers: **[STRONG]** = meta-analysis/RCT, **[MODERATE]** = single study or platform data, **[PRACTITIONER]** = first-hand/community practice.

## A. Exam simulation and quiz-condition matching

**1. Practice testing is the single highest-utility study technique known. [STRONG]**
Dunlosky et al. 2013 (*Psychological Science in the Public Interest*, 10-technique monograph) rates practice testing and distributed practice as the only two "high utility" techniques; rereading and highlighting (what students default to) rate low. Source: https://journals.sagepub.com/doi/abs/10.1177/1529100612453266
**Design implication:** The workspace's core loop should be *generating and taking quizzes*, not organizing notes. Every AI feature should push toward retrieval ("try it closed-book first"), never toward re-explaining as the default.

**2. Transfer-appropriate processing / context matching is real but modest — the *format* match matters more than the *room* match. [STRONG]**
Smith & Vela's meta-analysis of environmental context-dependent memory (93 studies): reliable but small effect (d ≈ 0.28). The stronger evidence is processing-match: retrieval works best when practice conditions engage the same cognitive operations as the test. Sources: https://link.springer.com/article/10.3758/BF03196157 · https://www.facultyfocus.com/articles/educational-assessment/practice-exams-for-improved-learning/
**Design implication:** Don't obsess over replicating the classroom; obsess over replicating the *task*: pen on paper, no notes, no calculator, real time limit, questions in quiz format. "Typed answer into a chat box" is a fundamentally different (weaker) practice mode than "wrote it by hand under a timer" — track them separately.

**3. Practice tests measurably reduce test anxiety; easy, low-stakes practice tests reduce it most. [STRONG]**
2023 meta-analysis (24 studies, *Educational Psychology Review*): practice tests reduce test anxiety to a medium extent; mechanism appears to be habituation. Source: https://link.springer.com/article/10.1007/s10648-023-09801-w
**Design implication:** Two tiers of simulation: frequent low-stakes micro-quizzes (anxiety inoculation + retrieval), plus one full-dress weekly mock under exact quiz conditions. Never make the daily quizzes feel like judgment — the mock is the judgment.

**4. Past-paper culture (STEP/A-level/competition math) converges on: timed papers + examiner reports + per-question time caps + overrun logging. [PRACTITIONER, deep tradition]**
Work past papers under timed conditions, cap minutes per question, log overruns, mine examiner reports for recurring mark-losing traps; practice *by topic* first, then full timed papers. Sources: https://www.maths.cam.ac.uk/undergrad/admissions/step · https://nextstepmaths.com/how-to-prepare-for-step/
**Design implication:** Maintain a per-question-type time budget and log blowouts. "You spent 14 min on a 6-min induction proof" is more actionable than a percentage score. Old quizzes from this course are the highest-value asset in the system.

**5. Interleaved math practice roughly doubles delayed test performance vs blocked. [STRONG]**
Rohrer et al. 2020 preregistered cluster RCT (787 students): interleaved 61% vs blocked 38%, d = 0.83, surprise test a month later. Source: https://gwern.net/doc/psychology/spaced-repetition/2019-rohrer.pdf
**Design implication:** Generated practice sets should mix problem types (this week's + past weeks'), because the quiz won't announce which technique each problem needs — strategy *selection* is the graded skill. This also builds spaced review into every session.

## B. Error logs

**6. The mistake notebook is a load-bearing institution in exam-intensive cultures (Chinese 错题本/cuotiben, gaokao, AP/competition coaching). [PRACTITIONER, very widespread; no direct RCT found]**
Standard cycle: mistake → cause analysis → re-test the same item later. Coaching sources classify errors as concept gap vs procedural slip vs misread/interpretation vs transcription, and insist "careless" be decomposed further. Conceptual errors get priority; execution slips get process fixes (checking rituals), not re-study. Sources: https://note.com/manabirador/n/n98a9c308b8de?hl=en · https://sparkl.me/blog/ap/error-logs-that-actually-improve-scores-turn-every-mistake-into-ap-gold/ · https://www.edufirst.com.sg/blog/careless-mistakes-fix-a-5-step-error-log-system-for-psle-math/
**Design implication:** Error log = first-class object with a forced taxonomy (concept / procedure / misread / arithmetic-transcription) and a *scheduled re-test* of every logged item before the next quiz. The AI does the expensive part (classification and re-test generation); the student does the valuable part (attempting and reflecting). Different error types trigger different remedies — concept gap → re-derivation session; slip → pre-quiz checking checklist.

## C. Why personal study systems die

**7. The productivity-tool graveyard is a friction problem: systems die when capture requires decisions. [PRACTITIONER, multiple consistent accounts]**
XDA account: Notion workspace with databases/relations/automations → 4 entries before abandonment; Obsidian daily template → dead in 3 days; the killer was per-capture decisions ("which database? what tag taxonomy?"). What survived: journal-based tools that open directly onto *today* with zero filing decisions. "The pursuit of perfection is procrastination wearing a very convincing disguise." Sources: https://www.xda-developers.com/stop-overengineering-notes/ · https://alltech.medium.com/the-day-i-realised-my-productivity-system-was-just-expensive-procrastination-4c9447831705
**Design implication:** (a) The workspace must open directly onto *today's session* — never a dashboard requiring navigation or filing. (b) Building/tuning the system is itself the primary failure mode for a builder-student: freeze the system design after week 1 and make "tinkering" visibly not count as study time. (c) Everything logged should require ≤1 decision; the AI does the categorizing.

**8. Elaborate tracking dies because maintenance cost exceeds consistent capacity. [PRACTITIONER]**
Recurring phrase: systems "abandoned because they demanded more than I could consistently give."
**Design implication:** Define a "minimum viable day" (one 10-minute retrieval set) that keeps the chain alive and costs less than skipping-plus-guilt. Progress tracking must be a byproduct of doing work (auto-logged), never a separate journaling chore.

## D. Habit/routine mechanics

**9. Implementation intentions ("at TIME in PLACE I will X") — d = 0.65 across 94 tests; confirmed at scale. [STRONG]**
Gollwitzer & Sheeran 2006 meta-analysis; 2024 update across 642 tests (d = 0.27–0.66), strongest with explicit if-then format. Sources: https://www.sciencedirect.com/science/chapter/bookseries/abs/pii/S0065260106380021 · https://www.tandfonline.com/doi/abs/10.1080/10463283.2024.2334563
**Design implication:** Onboarding should extract a concrete if-then plan ("After [anchor event], at [place], I do the daily set") and reminders should *echo that plan verbatim*, not say "time to study!"

**10. Habit formation: ~66 days median to automaticity (range 18–254); missing a single day "did not materially affect" the process. [MODERATE]**
Lally et al. 2010. Source: https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674
**Design implication:** A 7-week course won't reach automaticity — scaffolding must last the whole course. Build "miss one day = non-event" into the language and streak mechanics; frame two consecutive misses as the real alarm (mirroring the course's own miss-two-quizzes-fail rule).

**11. Streaks retain but backfire on break: Duolingo's own data. [MODERATE]**
Streak-protection features produced +14% D7 retention; losing a streak is a major quit trigger (abstinence-violation effect); some users serve the streak instead of the learning; *bingers were much more likely to abandon than pacers*. Sources: https://blog.duolingo.com/how-streaks-keep-duolingo-learners-committed-to-their-language-goals/ · https://thedecisionlab.com/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification
**Design implication:** Ship any streak with built-in forgiveness (1–2 earned "freezes"/week) from day one; the tracked metric is *sessions of real retrieval*, not app-opens. Treat a weekend-binge pattern as a churn warning, not a win.

**12. Spacing beats massing decisively; optimal gap scales with retention interval. [STRONG]**
Cepeda et al. 2006 meta-analysis (317 experiments): for a test ~1 week out, ~1–2 day gaps near-optimal. Source: https://www.yorku.ca/ncepeda/publications/CPVWR2006.html
**Design implication:** For weekly quizzes, daily short sessions are close to theoretically optimal — daily 20–40 min, each week's topics resurfacing in weeks n+1 and n+2. Weekend binges are the pattern to actively prevent, on both retention and adherence grounds.

**13. Fresh-start effect: temporal landmarks boost goal initiation and re-initiation. [STRONG]**
Dai, Milkman & Riis 2014, *Management Science*. Source: https://pubsonline.informs.org/doi/10.1287/mnsc.2014.1901
**Design implication:** Structure the course as 7 explicit "Week N begins" resets. After a bad quiz or lapsed days, the recovery move is a declared fresh start at the next landmark ("new week, clean slate — here's the plan"), not surfacing accumulated debt.

## E. Reminder/nudge design

**14. Reminders work until they habituate; rotation/novelty and context-awareness keep them working. [MODERATE-STRONG]**
Yancey & Settles, KDD 2020 (Duolingo): bandit-optimized notification *content* (rotating templates, novelty decay modeling) lifted DAU +0.5% and new-user retention +2%; identical repeated messages decay. Separate 2025 study: notified group 82% adherence vs 49% control, but compliance collapsed when notifications stopped (extrinsic dependency). Sources: https://research.duolingo.com/papers/yancey.kdd20.pdf · https://journals.kmanpub.com/index.php/aitechbesosci/article/view/4724
**Design implication:** One reminder per day, at the user's own if-then time, with rotating content that references *state* ("3 error-log items due for re-test; quiz in 2 days") rather than "study now." Plan for weaning: by week 4-5 the routine anchor should carry the load, not the ping.

## F. Solo accountability

**15. Commitment devices and social accountability raise follow-through; body doubling and stakes are the proven levers. [MODERATE]**
Giné, Karlan & Zinman 2010 field experiment (basis of Beeminder); body doubling (Focusmate) is practitioner-standard for task *initiation*; "learning in public" is a soft commitment device. Sources: https://learningloop.io/plays/psychology/commitment-devices · https://www.accountablo.com/blog/accountability-partner-app
**Design implication:** The AI can play accountability partner cheaply (check-ins, "you said yesterday you'd re-test these"), but the course supplies a real stake for free: miss-two-quizzes-fail — make the countdown/stakes visible rather than manufacturing artificial ones. A lightweight public ledger (weekly mock scores to a friend) is optional escalation.

**16. Compressed-course precedent: Scott Young's MIT Challenge — its engine was exam simulation. [PRACTITIONER]**
33 MIT courses in 12 months; method = compress passive input hard (sped-up lectures), then spend most time on past exams/problem sets under exam conditions, with the Feynman technique reserved for concepts that failed during practice. Insight ordering: practice reveals the gap → *then* targeted explanation. Source: https://www.scotthyoung.com/blog/myprojects/mit-challenge-2/
**Design implication:** The AI's role inversion: default to "attempt first, explain after failure." Lecture/notes review is the minority activity; the majority is quiz-condition attempts with the AI as grader/explainer of what broke.

## Cross-cutting synthesis

- **Strongest convergence:** retrieval under quiz-matched conditions (1, 2, 4, 5, 16) + spacing via daily sessions (12) + error-log recycling (6). These three loops *are* the system; everything else is adherence scaffolding.
- **Biggest design risk for this specific user (a builder building their own tool):** findings 7-8 — system-building as avoidance. The workspace should be deliberately boring and frozen; novelty budget goes into problem content, not features.
- **Anxiety angle:** closed-book handwritten in-person under a hard attendance rule is a high-anxiety format; finding 3 says the simulation habit is itself the anxiety treatment — the weekly mock does double duty.
- **Evidence-quality caveat:** error logs (6) and learning-in-public (15) rest on practitioner tradition; implementation intentions, spacing, interleaving, practice testing, and anxiety reduction are the meta-analytic bedrock.
