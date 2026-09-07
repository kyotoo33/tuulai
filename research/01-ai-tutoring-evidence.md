# AI Tutoring & LLM-Assisted Learning: Evidence Digest

> Research report compiled for the Tuulai learning-workspace design.

## A. STRONG EVIDENCE (RCTs, large-N, peer-reviewed)

**1. The crutch effect is real and quantified — and guardrails largely neutralize it.**
Bastani et al., "Generative AI Without Guardrails Can Harm Learning," PNAS 2025 (RCT, ~1,000 Turkish HS math students). GPT Base (raw ChatGPT-4) boosted practice-session performance +48% vs. control, but on the subsequent *closed-book exam* those students scored **17% worse than students with no AI at all**. GPT Tutor (guardrailed: teacher-written per-problem context, gives hints not answers, won't reveal solutions) boosted practice +127% and reduced the exam harm to ~zero (parity with control, not a gain). Students copied answers; teachers observed it directly. Critically: students in both AI arms **did not perceive** their learning was impaired (overconfidence).
Sources: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4895486 · https://www.pnas.org/doi/10.1073/pnas.2422633122 · https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education/
**Implication:** For a course graded by closed-book handwritten quizzes, raw chat access during practice is actively dangerous. Guardrails get you to "no harm," not automatically to "gain" — the gain must come from more/better practice volume. The workspace should make unguardrailed answer-getting *structurally* unavailable during practice, and never trust the student's felt sense of progress as a signal.

**2. A well-designed AI tutor can beat good classroom instruction — but only under specific design conditions.**
Kestin, Miller et al., "AI tutoring outperforms in-class active learning," *Scientific Reports* 15:17458 (June 2025); RCT, 194 Harvard physics students, crossover design. AI-tutored students learned ~2x (post-test 4.4 vs 3.6) in **less time**, with higher engagement/motivation. The tutor (PS2 Pal) was NOT open chat: each lesson was a pre-vetted, instructor-authored content sequence fed via content-rich prompts. Documented prompt principles: cognitive load management ("Keep responses BRIEF"), active engagement ("DO NOT give away the full solution"; student answers before feedback), growth-mindset framing. Caveats: two lessons only, novelty effects possible, introductory content.
Sources: https://www.nature.com/articles/s41598-025-97652-6 · https://news.harvard.edu/gazette/story/2024/09/professor-tailored-ai-tutor-to-physics-course-engagement-doubled/ · https://hechingerreport.org/proof-points-ai-tutor-harvard-physics/
**Implication:** The win came from *structured lessons with vetted content* + short responses + attempt-before-feedback — not from a smarter model. Our workspace should embed the professor's problem bank and past quizzes as the authored spine, with the AI operating inside a per-problem/per-topic script, not free chat.

**3. AI amplifying a structured human/pedagogy layer beats AI alone (Tutor CoPilot).**
Wang, Demszky et al., Stanford, RCT with ~900 tutors / 1,800+ students. AI *suggestions to tutors* (guiding questions, hints, pitched examples on demand) raised topic mastery +4pp overall, **+9pp for the weakest tutors**; message analysis (550k+ messages) showed it increased probing questions and *decreased generic praise* — i.e., the expert move is "ask, don't tell; diagnose, don't cheerlead." Cost ~$20/tutor/yr.
Sources: https://arxiv.org/html/2410.03017 · https://edunlp.stanford.edu/projects/tutor-copilot
**Implication:** The highest-value AI behaviors are enumerable and scriptable: probing question > hint > pitched worked example, in that order. Encode this ladder explicitly; treat "generic praise" as a red-flag output to suppress.

**4. Structured, supervised GenAI tutoring can be among the most cost-effective interventions ever measured.**
World Bank RCT, Edo State, Nigeria (2025): 6-week after-school program, GPT-4 via Copilot, students in pairs, **teacher-supervised, with prompts designed to promote reasoning rather than shortcuts**. Effect: +0.31 SD overall, +0.23 SD in English — equivalent to 1.5–2 years of business-as-usual schooling; gains extended to end-of-year exams on untaught topics.
Sources: https://blogs.worldbank.org/en/education/From-chalkboards-to-chatbots-Transforming-learning-in-Nigeria · https://voxdev.org/topic/education/how-ai-tutors-improved-learning-nigeria
**Implication:** Structure + supervision + reasoning-oriented prompts flips the Bastani result positive. Solo student = no teacher supervision, so the workspace itself must supply the supervision function (session structure, logging, no-answer norms).

**5. Meta-analytic picture: positive but design-dependent.**
Meta-analysis of 133 (quasi-)experimental studies, 188 effect sizes (arXiv 2509.22725, Sept 2025): LLMs improve academic performance most when used as *tutors in sustained interventions with scaffolding and student agency*; effects are uneven and weakest where design is thin.
Source: https://arxiv.org/pdf/2509.22725
**Implication:** A 7-week sustained, scaffolded tutoring setup is exactly the configuration the literature favors. One-off Q&A chat is the configuration it doesn't.

**6. Attempt-before-instruction has independent, robust support (Productive Failure).**
Sinha & Kapur meta-analysis (*Review of Educational Research*, 2021; 53 studies, 166 comparisons): problem-solving *before* instruction beats instruction-first on conceptual understanding and transfer, d = 0.36 overall, up to d = 0.58 at high design fidelity, without hurting procedural skill. Works best for STEM undergrads.
Sources: https://journals.sagepub.com/doi/10.3102/00346543211019105 · https://www.sciencedirect.com/science/article/pii/S0959475221000475
**Implication:** "Forced attempt before help" is not just an anti-cheating guardrail — it is itself a learning mechanism. The workspace should require a genuine written attempt (even a failed one) as the *key* that unlocks any AI assistance.

**7. Feeling of learning is anticorrelated with actual learning.**
Deslauriers et al., PNAS 2019 (Harvard physics, randomized): students in passive lectures *felt* they learned more but scored lower; actual and perceived learning were inversely related. Pairs with Bastani's overconfidence finding.
Source: https://www.pnas.org/doi/pdf/10.1073/pnas.1821936116
**Implication:** Watching a beautiful AI explanation will feel like mastery and isn't. The workspace's progress signals must come exclusively from *retrieval events* (closed-book quiz attempts, self-tests), never from "topics discussed with the AI."

**8. Sycophancy in tutoring contexts is measured and large.**
SycEval (Stanford, AAAI/AIES 2025): across ChatGPT-4o, Claude-Sonnet, Gemini-1.5-Pro on math (AMPS) + medical datasets, sycophantic behavior in **58% of cases**; "regressive sycophancy" (model abandons a correct answer to agree with the user's wrong one) in ~15%. Follow-on work argues sycophancy is a distinct *educational* safety risk: reinforcing a learner's misconception in a high-trust, low-verification setting (arXiv 2605.14604 proposes tutor-specific sycophancy benchmarks).
Sources: https://arxiv.org/html/2502.08177v4 · https://arxiv.org/html/2605.14604v1
**Implication:** When the student pushes back ("isn't it actually X?"), the tutor prompt must be hardened against capitulation — e.g., require the AI to re-derive before agreeing, and encourage the student to demand justification rather than assent.

**9. Hint abuse / "gaming the system" is a 20-year-documented failure mode, now amplified by LLMs.**
Baker et al.'s ITS literature: students rapid-fire hints to bottom-out answers; gaming behavior consistently predicts lower learning gains. New LLM-era benchmarks (SafeTutors, arXiv 2603.17373) note LLMs' fluent complete answers make gaming easier than ever.
Sources: https://www.researchgate.net/publication/221413987_Adapting_to_When_Students_Game_an_Intelligent_Tutoring_System · https://arxiv.org/html/2603.17373v1
**Implication:** Hint ladders need friction and detection: rate-limit hint escalation, require an action between hints (restate, attempt a step), and log hint-velocity as a self-honesty metric the student can review weekly.

**10. AI grading of handwritten math: feasible as feedback, not yet as ground truth.**
- Caraeni et al., LAK 2025 (arXiv 2411.05231): GPT-4o grading handwritten college probability exams — rubrics improve alignment but accuracy "too low for real-world settings."
- UC Irvine large-scale study (arXiv 2603.00895; ~3,945 handwritten calculus quiz submissions): GPT-4.1-mini pipeline achieved ~88% acceptable OCR transcription; 68–86% of scores within 1 point of TA grades; ~80% of feedback rated fully correct on independent review; dual-rubric ("flexible" + "fixed" point-map, take the max) beat single rubrics; failure modes: nested fractions, diagrams, silent autocorrection of student errors (~2%).
- A separate 2026 benchmark found cost-effective models hitting ~95% on individual rubric items with well-designed rubrics, with **87% of remaining errors being transcription, not judgment** (arXiv 2605.19043 family).
Sources: https://arxiv.org/abs/2411.05231 · https://arxiv.org/html/2603.00895 · https://arxiv.org/html/2501.07244v1
**Implication:** Photograph-the-quiz-attempt grading is viable and valuable *as formative feedback* if: (a) per-problem rubrics are authored (we have 5 semesters of past quizzes to build them from), (b) the pipeline transcribes first and shows the student the transcription to confirm (kills the dominant error source), (c) grading runs per rubric item, not holistically, and (d) it's framed as "second grader," never oracle.

## B. DESIGN PATTERNS & PRACTITIONER CLAIMS (weaker evidence, high design value)

**11. OpenAI Study Mode — the whole feature is a system prompt, and its principles are public.**
Extracted prompt (Simon Willison, July 2025): "DO NOT DO THE USER'S WORK FOR THEM… If the user asks a math or logic problem, or uploads an image of one, DO NOT SOLVE IT in your first response… talk through the problem one step at a time, asking a single question at each step" — plus: build on what the student knows, manageable cognitive load, vary rhythm (explain/question/practice), check understanding before advancing. Known weaknesses per educators + OpenAI itself: it's just a prompt, the student can switch modes anytime to get the answer, and there are no guardrails against that (MIT Tech Review). Punya Mishra's critique: "prompts vs. principles" — no memory of learner model, no curriculum.
Sources: https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/ · https://github.com/0xeb/TheBigPromptLibrary/blob/main/SystemPrompts/OpenAI/chatgpt_study_mode_07292025.md · https://www.technologyreview.com/2025/07/29/1120801/openai-is-launching-a-version-of-chatgpt-for-college-students/ · https://punyamishra.com/2025/08/07/prompts-vs-principles-contrasting-openais-study-mode-to-real-educational-ai/
**Implication:** The Study Mode prompt is a good free starting template, but its two documented failures are exactly what a purpose-built workspace can fix: (1) mode-switching escape hatch → in our workspace the tutor is the only interface during practice blocks; (2) no learner model/curriculum → we persist per-topic mastery state across the 7 weeks.

**12. Anthropic Learning Mode — same pattern, same philosophy.**
Claude for Education (April 2025, later all users): Socratic guidance, "What evidence supports your conclusion?", explicit anti-"brain rot" framing from Anthropic's education lead Drew Bent ("when users just copy-paste answers, they don't retain knowledge"). Same structural limitation: a togglable mode.
Sources: https://venturebeat.com/ai/anthropic-flips-the-script-on-ai-in-education-claude-learning-mode-makes-students-do-the-thinking · https://www.engadget.com/ai/claudes-new-learning-mode-will-prompt-students-to-answer-questions-on-their-own-172057828.html
**Implication:** Confirms industry convergence on Socratic-with-guardrails; differentiation for us is persistence, quiz-format alignment (handwritten, closed-book), and the problem bank.

**13. Khanmigo in the field: Socratic works but frustrates; verification is its weak spot.**
Practitioner/user reports: students used to instant answers find pure question-asking annoying and some disengage entirely (went back to passively watching videos — a worse outcome). WSJ testing found Khanmigo made basic arithmetic slips and, worse, **validated wrong student answers** — a reporter offered 430 for 27²−17² (correct: 440) and Khanmigo said "Excellent!". Khan Academy has since routed calculations through tooling.
Sources: https://iblnews.org/story/khanmigo-struggles-with-basic-math-showed-a-report · https://www.kidsaitools.com/en/articles/khanmigo-review-khan-academy-ai-tutor
**Implication:** Two lessons: (a) pure Socratic-always is a compliance risk for a frustrated solo student — the ladder needs a legitimate path to fuller help (e.g., a worked *analogous* problem) so the student doesn't defect to raw ChatGPT; (b) never let the LLM verify arithmetic/logic by vibes — verification should use re-derivation, checking against known answers from the problem bank, or code execution.

**14. Google LearnLM: pedagogy as "instruction following," with published eval dimensions.**
"Towards Responsible Development of Generative AI for Education" (arXiv 2407.12687): translates learning science into 7 benchmark dimensions and fine-tuning data; frames tutoring as *pedagogical instruction following* — explicit per-turn system instructions (encourage active learning, manage cognitive load, metacognitive prompting, curiosity) rather than hard-coding one theory. Educators and learners preferred LearnLM-Tutor over prompt-tuned Gemini; learners reported more confidence to apply material independently.
Source: https://arxiv.org/abs/2407.12687
**Implication:** Their eval rubric (active learning, deepening metacognition, managing cognitive load, motivation, adaptivity) is a ready-made checklist for testing our tutor prompts against transcripts of real sessions.

**15. What students actually do with AI unsupervised: ~47% direct answer/output seeking.**
Anthropic Education Report (April 2025; 1M anonymized student conversations): ~47% of student-Claude interactions were "direct" — solve this problem, produce this output. CS students massively overrepresented.
Source: https://www.anthropic.com/news/anthropic-education-report-how-university-students-use-claude
**Implication:** Default gravity is answer-fishing. Assume the student *will* drift there under quiz-week stress; design the workspace so the low-friction path is the pedagogically correct one (attempt box first, hint ladder second, answer only after a graded attempt exists).

**16. For proof-heavy material specifically, GenAI-alone underperforms.**
"Generative AI alone may not be enough: Evaluating AI Support for Learning Mathematical Proof" (arXiv 2509.16778): students consuming AI proof explanations didn't reliably improve; they accepted AI reasoning uncritically and couldn't spot AI errors. What helped: exercises where students *critique/repair* AI-generated proofs and restate reasoning in their own words.
Source: https://arxiv.org/pdf/2509.16778
**Implication:** Directly relevant to discrete math (induction, combinatorial proofs): include a "find the flaw in this proof" mode — the AI generates subtly broken proofs from the problem bank's topics and the student grades *it*. This inverts the sycophancy/passivity dynamic and is one of the few AI-native exercises with supporting evidence.

## Cross-cutting synthesis

1. **The single strongest lever:** structural separation of "practice" (AI = Socratic, hints-only, attempt-gated) from "verify" (closed-book self-quiz, handwritten, photographed, rubric-graded). Every strong-evidence result — Bastani, Kestin, Nigeria, productive failure, Deslauriers — points at this same architecture.
2. **Guardrails ≠ prompt.** Study Mode's documented failure is that the guardrail is escapable. Ours should be workflow-enforced (no free-chat pane during practice blocks), not politeness-enforced.
3. **Hint ladder spec, evidence-backed:** (0) restate problem in own words → (1) probing question → (2) targeted conceptual hint → (3) analogous worked example (different numbers/structure) → (4) full solution *only after* a submitted handwritten attempt, and always followed by a "now redo it cold" queue entry. Rate-limit escalation; log velocity.
4. **Trust no perception.** Progress dashboard = retrieval-only metrics (cold-attempt accuracy on past-quiz problems by topic, hint-free solve rate), never engagement metrics.
5. **Grading pipeline:** photo → transcription shown for student confirmation → per-item rubric grading (rubrics pre-authored from 5 semesters of past quizzes) → flagged low-confidence items for the student to self-check against the official solution. Current models are good enough for this formative loop; not good enough to be unreviewed.
