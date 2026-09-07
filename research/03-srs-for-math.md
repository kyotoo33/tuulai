# SRS for Mathematical Understanding — Research Findings

> Research report compiled for the Tuulai learning-workspace design.

## A. The Matuschak/Nielsen canon (practitioner, but the most sophisticated practice available)

**1. Nielsen's baseline practice: atomic prompts, in service of a project, and the declarative/procedural gap.**
Source: https://augmentingcognition.com/ltm.html — Confidence: practitioner account (highly influential).
Key extractions: break every failed card into more atomic sub-questions; high-level conceptual questions are fine *if* they're atomic conditional on background knowledge; avoid "orphan" cards disconnected from a knowledge network; "Anki works much better when used in service to some personal creative project." Critical limit stated explicitly: "to really internalize a process, it's not enough just to review Anki cards. You need to carry out the process, in context."
Design implication: cards must exist *in service of* the weekly problem-bank grind, not parallel to it; every card should trace back to a quiz-relevant task; card failure should trigger decomposition, not just re-scheduling.

**2. Nielsen's proof-specific method ("seeing through a piece of mathematics").**
Source: https://cognitivemedium.com/srs-mathematics — Confidence: practitioner account, single-n, honest caveats.
Method: Phase I "grazing" — extract individual proof elements as cards, restate the same idea multiple ways (algebraic/geometric/verbal), plus one "aspirational" card ("In one sentence, what is the core reason X holds?") that distills the whole proof. Phase II — variation cards: weaken hypotheses, ask for counterexamples to modified claims, generalize. Cost: 40–80 cards and hours per theorem; he abandoned it for the fundamental theorem of algebra. He stresses the value is mostly in the *process of pulling apart the proof*, Anki only preserves the result; and even then he forgot alternate proofs he didn't record.
Design implication: full Ankification is too expensive for a 7-week course at ~1 theorem granularity — but the *card genres* (multiple restatements, counterexample-to-weakened-hypothesis, one-sentence-essence) are cheap to generate from an AI workspace and are exactly what closed-book proof quizzes test. Reserve deep Ankification for the 3–5 load-bearing proofs per week.

**3. Matuschak's prompt-quality rules and failure modes.**
Source: https://andymatuschak.org/prompts/ — Confidence: practitioner synthesis, grounded in literature.
Five properties: focused, precise, consistent, tractable ("almost always answer correctly"), effortful (no trivial inference). Conceptual knowledge gets systematic "lenses": attributes/tendencies, similarities/differences, parts/wholes, causes/effects, significance. Failure modes: binary yes/no prompts, pattern-matching on long distinctive question text, ambiguous answers. Write 5–10 prompts on first pass, iterate from review failures; delete prompts you stop caring about.
Design implication: if the workspace auto-generates cards, generate against these lenses and lint against the failure modes (no yes/no, one fact per card, answer uniquely determined). Track "sigh" cards and rewrite rather than letting them churn.

**4. SRS *can* carry conceptual understanding — but scheduling and authoring differ from facts.**
Source: https://notes.andymatuschak.org/z9Vi7YVx7NzxU2wawNgsJbk — Confidence: practitioner note citing strong studies (Butler 2010; Karpicke & Blunt 2011 show the testing effect holds for conceptual/inference questions).
Caveats: writing conceptual prompts is much harder than factual ones; conceptual material "may have much slower optimal spaced repetition schedules"; open question whether atomic or integrative tasks serve concepts better.
Design implication: don't let one scheduler treat definition cards and concept cards identically; concept/connection prompts can tolerate longer gaps, definitional fluency needs tighter ones early.

**5. "Why books don't work" + Quantum Country's actual retention data.**
Sources: https://andymatuschak.org/books/ · https://notes.andymatuschak.org/zt1TyUANyt84UkQVBJjWEGZ3JUd2HP92r65 — Confidence: argument essay + observational product data (not RCT).
Mechanism claim: reading fails because comprehension monitoring/metacognition is unsupported; the mnemonic medium interleaves expository text with embedded retrieval at expanding intervals, offloading metacognition onto the medium. Data: after ~30 min total review, readers retain answers to ~112 questions for 2+ weeks; ~1 hr → 5+ weeks; ~1.5 hr → 9+ weeks. Roughly "+50% time on top of reading buys months of retention."
Design implication: embed retrieval directly into the weekly study material (questions inline with notes/lecture digest) rather than a separate deck app; the marginal time cost is small and the metacognitive signal (what you *can't* answer) is the main product.

**6. The known frontier problem: application prompts don't behave like recall prompts.**
Sources: https://notes.andymatuschak.org/The_mnemonic_medium_can_help_readers_apply_what_they%E2%80%99ve_learned_through_simple_application_prompts · https://notes.andymatuschak.org/z3ERHM3aC9jCyTR5KpgxTAyXf7kNSkG57SqrR — Confidence: practitioner working notes.
Readers of pure-recall media feel their knowledge is "parroting"; application prompts (use the idea in a small novel situation) are the fix, but they break the SRS feedback loop: when you fail one, you can't just memorize the shown answer — you must diagnose *which component* you were missing. Execute Program is cited as the existence proof that prompts can be simultaneously application and recall.
Design implication: this is precisely where an AI tutor beats static SRS — on a failed application/problem prompt, the AI can do the failure diagnosis (which prerequisite, which move) and spawn the targeted recall card automatically. That closes the loop static systems can't.

## B. Scheduling problems instead of cards

**7. FSRS: what it actually optimizes, and its scope.**
Sources: https://faqs.ankiweb.net/what-spaced-repetition-algorithm · https://expertium.github.io/Algorithm.html — Confidence: strong (open benchmark, ML on large review corpora).
FSRS fits a 3-component memory model (Difficulty, Stability, Retrievability) to review history and schedules each card to hit a target retention (e.g., 90%). Key insight over SM-2: stability gain depends on how close to forgetting the review lands. Scope limits: it models *binary recall of a fixed item*; a parameterized problem whose surface changes each rep violates the "same item" assumption (arguably a feature — forces generalization, at the cost of noisier grading data).
Design implication: use FSRS-style scheduling for the fact/definition/theorem-statement layer with target retention set high (0.9+, short course). For the problem layer, schedule *skills/topics*, not cards, and grade "can execute the method," not "recalled the string."

**8. Math Academy's FIRe: the most developed practice of spacing problems, not cards.**
Sources: https://www.justinmath.com/individualized-spaced-repetition-in-hierarchical-knowledge-structures/ · https://www.justinmath.com/files/the-math-academy-way.pdf — Confidence: serious practitioner system (proprietary, no independent RCT).
Mechanics: knowledge graph over topics; solving an advanced problem sends *fractional implicit credit* down to encompassed prerequisite skills, postponing their reviews ("repetition compression"); failing a basic skill propagates penalties *up* to dependent topics; per student-topic speed multipliers. Without compression, review load explodes (60+ due questions/day within weeks).
Design implication: the architecture for the workspace: model the course as a small prerequisite graph (~50–100 skills for 7 weeks), schedule *skills*, satisfy due reviews implicitly by choosing problem-bank items that encompass them, and propagate credit/penalty through the graph. The professor's parameterized bank is exactly the item generator Math Academy had to build itself.

**9. Execute Program & SuperMemo culture: corroborating practice.**
Sources: https://www.executeprogram.com/spaced-repetition · https://mike.place/2020/executeprogram/ · https://supermemo.guru/wiki/Neural_networks_in_spaced_repetition — Confidence: practitioner.
Execute Program schedules tiny *interactive tasks* (not flashcards) with daily lesson caps to force distribution; prompts double as recall and application. SuperMemo's "incremental problem solving" is more folklore than documented method.
Design implication: cap daily new-topic intake and make review items executable tasks; a rate limiter is a feature, not a nanny, in a course where the temptation is to binge before each quiz.

**10. The skeptical case: spacing maintains, induction needs contrast.**
Source: https://gwern.net/spaced-repetition — Confidence: literature review by careful practitioner.
Two cautions: Rothkopf's "Spacing is the friend of recall, but the enemy of induction" — isolated spaced items arriving days apart deprive you of the side-by-side contrast that builds category/strategy discrimination; and evidence on motor/complex skills suggests SRS *maintains* skills rather than growing them.
Design implication: don't atomize everything — review sessions should sometimes present *sets* of contrasting items together (e.g., "which counting technique applies?" across 5 juxtaposed problems). Growth comes from the problem sessions; SRS's job is to keep components warm.

## C. The cognitive science floor (strongest evidence)

**11. Testing effect — and its short-horizon twist.**
Source: Roediger & Karpicke 2006, https://pubmed.ncbi.nlm.nih.gov/16507066/ — Confidence: strong (replicated hundreds of times; Adesope et al. 2017 meta g≈0.6).
At a 5-minute delay, restudying *beats* testing; at 2 days and 1 week, testing wins decisively — and repeated restudy inflates confidence while producing worse 1-week retention. The 1-week crossover is exactly the quiz horizon.
Design implication: for weekly quizzes, rereading notes the night before is the confidence-inflating trap; everything between lecture and quiz should be retrieval-formatted. The "feels worse, works better" asymmetry must be surfaced to the student explicitly.

**12. Spacing at short horizons: the optimal gap for a 1-week test is 1–3 days.**
Source: Cepeda, Vul, Rohrer, Wixted & Pashler 2008, https://files.eric.ed.gov/fulltext/ED505660.pdf — Confidence: strong (n>1,350, parametric sweep).
Optimal inter-study gap ≈ 20–40% of the retention interval at 1-week delay (shrinking to 5–10% at 1-year). Performance rises then falls with gap; too-long gaps at short horizons actively hurt.
Design implication: spacing is *not* voided by a 7-week course. For a quiz on day 7: learn day 0–1, first retrieval day 2–3, second day 5–6. The scheduler should target the quiz date, not "lifetime retention" — set retention targets per-quiz, plus a lighter maintenance track for the final.

**13. Successive relearning: the packaging of spacing+testing with classroom-grade evidence.**
Sources: Rawson & Dunlosky 2022 overview, https://journals.sagepub.com/doi/full/10.1177/09637214221100484 · Rawson, Dunlosky & Sciartelli 2013 — Confidence: strong, in authentic courses.
Protocol: retrieve each item to criterion (1 correct) in a session, then *relearn to criterion* in 2–3 more spaced sessions before the exam. Produced roughly a letter-grade improvement on real course exams (tested at 3 and 24 days). Notably: pushing initial-session criterion from 1→3 correct recalls stops mattering once you have 3 spaced sessions — sessions beat within-session reps.
Design implication: the weekly loop should be "3 short sessions to criterion" (e.g., Mon/Wed/Fri), and the system should stop drilling an item within a session once it's been retrieved correctly — banking the reps for the next session instead. The single most directly transplantable protocol for a 7-week course.

**14. Interleaving in math: large, delayed-test effect, and the mechanism matches quiz conditions.**
Source: Rohrer, Dedrick, Hartwig & Cheung 2020 RCT, https://gwern.net/doc/psychology/spaced-repetition/2019-rohrer.pdf (54 classes, 787 students) · practice guide http://uweb.cas.usf.edu/~drohrer/pdfs/Interleaved_Mathematics_Practice_Guide.pdf — Confidence: strong (preregistered RCT).
Interleaved vs blocked homework: 61% vs 38% on an unannounced test one month later, d = 0.83. Mechanism: blocked practice lets students execute a strategy without ever *choosing* it; interleaving forces strategy discrimination — which is what a closed-book quiz mixing proofs/combinatorics/graphs demands.
Design implication: after the first day on a new topic, practice sets should always be mixed across the week's (and prior weeks') topics, with problems unlabeled by technique. "Which tool is this?" is itself the skill to schedule.

**15. Worked examples first, then fade (and the expertise reversal).**
Sources: https://www.tandfonline.com/doi/full/10.1080/01443410.2023.2273762 · https://mrbartonmaths.com/resourcesnew/8.%20Research/Explicit%20Instruction/The%20Expertise%20Reversal%20Effect.pdf — Confidence: strong (decades of CLT studies).
Novices learn more from studying worked solutions than from struggling (means–ends search swamps working memory); the effect *reverses* with competence — guidance becomes redundant/harmful. Standard remedy: faded examples (full solution → completion problems → full solving).
Design implication: on first contact with each topic, serve worked solutions from the problem bank plus completion problems, and *fade* scaffolding within 1–2 days — because the quiz is unscaffolded. A per-skill "novice → faded → full-solve → interleaved" pipeline operationalizes this.

**16. Self-explanation is the active ingredient when studying examples/proofs.**
Source: Chi, Bassok, Lewis, Reimann & Glaser 1989, https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1302_1 — Confidence: strong (foundational, well replicated; Renkl extensions).
Good solvers (82% vs 46% on subsequent problems) generated ~3x more self-explanations while studying examples, monitored their own comprehension accurately, and referred back to examples *less* during solving.
Design implication: never let the student passively read a bank solution — the AI should demand line-by-line "why is this step licensed / what goal does it serve?" and check the explanations. A proof studied without self-explanation is a rep wasted.

**17. Desirable difficulties — with the success caveat.**
Source: Bjork & Bjork, https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-introducing-desirable-difficulties-into-practice-and-instruction-bjork-and-bjork.pdf — Confidence: strong framework.
Spacing, interleaving, testing, variation all impair *performance during practice* while improving learning — but only when the learner has the background to succeed at the harder task; otherwise the difficulty is undesirable.
Design implication: expect and normalize lower in-session accuracy under interleaving (show learning-vs-performance explicitly), but gate difficulty on prerequisite mastery from the knowledge graph — struggle on a problem whose prerequisites aren't in place is waste, not virtue.

**18. Calibration: confident-wrong is the failure mode SRS quietly fixes — if grading is honest.**
Sources: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8442020/ (persistent miscalibration despite practice-test feedback) · https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6509741/ (retrieval practice improves JOL accuracy) · https://www.improvewithmetacognition.com/hypercorrection-overcoming-overconfidence-metacognition/ (hypercorrection effect) — Confidence: strong for the phenomena.
Poor calibration predicts lower grades; low performers overestimate most and feedback alone doesn't fix it; but retrieval attempts + immediate feedback both improve calibration and preferentially correct high-confidence errors.
Design implication: collect a confidence rating *before* revealing solutions, track a per-skill calibration curve, and prioritize review of confident-wrong items — simultaneously the biggest quiz risk and the most fixable. "I could reproduce this proof" claims should be spot-audited by making the student actually write it out closed-book.

## D. Practitioner accounts

**19. Two university accounts converge on the same division of labor.**
Sources: https://jallmo.substack.com/p/how-i-used-anki-throughout-my-engineering · https://benpomeranz.substack.com/p/anki-for-math — Confidence: practitioner anecdote (n=2, but consistent with everything above).
Pomeranz: "I've never used spaced repetition to *learn* math… I've learned it with pencil and paper… then used Anki to *forget less* of it." Highest-value card genres for math: object classification ("what kind of thing is X"), canonical examples, perverse examples, snappy counterexamples, rare "intuition" cards; whole-proof cards were labor-intensive and mostly not worth it. The engineering account: putting actual tutorial problems into Anki and solving them on a scratchpad during review (not recognizing answers) was the shift that made it work; perfectionist card-crafting was the main waste; 5-minute stuck rule, then move on and revisit.
Design implication: (a) learning happens at the desk with paper — the workspace schedules and audits, it doesn't replace derivation; (b) auto-generate the cheap high-yield genres (definitions, examples, counterexamples, "which technique?") and let the AI eat the card-authoring cost; (c) reviews of problem-type items must be done by *writing on paper*, matching the handwritten quiz modality.

## Cross-cutting synthesis

- **Two-layer system falls straight out of the evidence**: a card layer (definitions, theorem statements, proof skeletons, example/counterexample pairs — FSRS-scheduled, tractable, 90%+ retention target per quiz date) and a problem layer (parameterized bank items scheduled per *skill* via a FIRe-like prerequisite graph, interleaved, paper-solved, AI-graded). The card layer alone produces "memorized cards, can't solve"; the problem layer alone produces forgetting of the component fluency that makes proofs feel obvious.
- **7-week horizon changes parameters, not principles**: spacing still wins within a week (Cepeda: 1–3 day gaps; Roediger & Karpicke: testing beats restudy by day 2); the protocol with real classroom-exam evidence at this horizon is successive relearning (3 spaced to-criterion sessions per item per week).
- **The AI's unique roles per the literature**: generating Matuschak-quality prompts (the known skill bottleneck), diagnosing failed application prompts into targeted recall repairs (the known SRS dead-end), demanding and checking self-explanations, and running the calibration audit (confidence-before-answer, prioritize confident-wrong).
