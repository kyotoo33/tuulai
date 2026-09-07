# The pedagogy

Why the system nags you the way it does. Each principle below is implemented somewhere
concrete — the point of this file is that you can see *where*, and preserve it if you fork.

Longer evidence write-ups are in [`../research/`](../research/).

---

## 1. Retrieval, not review

Re-reading notes and highlighting produce a strong feeling of fluency and weak retention.
Pulling an answer out of your head — effortfully, without cues — is what builds durable memory.

**Implemented as:** every concept page is *required* to end in live problems; reading awards
zero progress; readiness is computed only from cold retrieval events.

**What this rules out:** a "study streak" you can satisfy by scrolling. If you only read, the
system will correctly report that you know nothing.

## 2. Match the conditions of the test

Memory is cued by context. Practising typed, with notes open, at your own pace trains a
different skill from a closed-book handwritten exam under time.

**Implemented as:** mocks print a real paper with the real conditions from `course.py`; you do
it on paper and photograph it. The system tracks paper-vs-typed performance separately, because
the gap between them is diagnostic.

## 3. Spacing and successive relearning

Cramming works for tomorrow and fails in three weeks. Re-testing at expanding intervals —
*successive relearning* — is one of the most reliably effective techniques in the literature.

**Implemented as:** `scheduler.py`. Items return at widening intervals; a miss shortens the
interval sharply. Urgency rises as an assessment approaches, so the queue reshapes itself
toward what's actually about to be examined.

## 4. Interleaving

Blocked practice (twenty of the same problem type) inflates confidence and teaches you to apply
a method you were *told* to apply. Real exams don't announce the method. Interleaving forces
the discrimination step — choosing the technique — which is where marks are actually lost.

**Implemented as:** the daily queue mixes skills; mock assembly deliberately interleaves
subtopics so consecutive problems differ.

## 5. Calibration

The most expensive exam failure is being **confidently wrong**: you don't check it, and you
don't study it. Calibration is trainable, but only if it's measured.

**Implemented as:** you must commit a confidence call (*sure / shaky / guessing*) before any
solution unlocks. The weekly coach reports your confident-wrong rate specifically.

## 6. Guide, never answer

A model that hands over solutions produces the illusion of understanding and trains
dependence. Help should raise the floor, not remove the problem.

**Implemented as:** a hint ladder that escalates from "what kind of problem is this?" toward a
next step but never a final answer; solutions gated behind a logged attempt; and every AI path
degrading to a working offline one.

## 7. Worked examples before problem-solving

For genuinely new material, studying a worked example first beats floundering. The advantage
reverses once you have some competence — hence *first contact* only.

**Implemented as:** `first_contact` on each skill routes your first exposure to a worked
example or concept page; afterwards you go straight to cold problems.

## 8. Error logs beat re-reading

Your own mistakes, categorised, are the highest-yield study material you will ever have.

**Implemented as:** every miss is logged with a taxonomy — *concept gap · procedure slip ·
misread · arithmetic slip*. The distinction matters: a concept gap sends you back to the idea,
a slip sends you to more reps under time.

## 9. Strategy is teachable — teach it explicitly

Students who freeze at a blank page usually don't lack knowledge; they lack a *first move*.
That knowledge is normally left implicit and picked up by osmosis.

**Implemented as:** `playbooks` — recognition cue → the literal first line to write → template
→ annotated worked trace → the wrong turn. And the `proofsteps` visualization, which pairs each
line of a model proof with the mark it earns.

---

## The trap to avoid

**Engagement is not learning.** Polished study apps optimise for streaks, XP and time-on-task —
metrics that go up when you do easy, pleasant, low-retrieval work. A tool can make you feel
excellent and teach you nothing.

The guard rails here are deliberate:

- reading awards **zero** progress
- there is no streak you can satisfy without retrieval
- the only number that counts is cold recall under exam conditions
- the coach reports uncomfortable things (confident-wrong rate, hint dependence) rather than
  congratulating you

If you fork this and find yourself adding a mechanic that feels motivating, check whether it
rewards retrieval or merely rewards *presence*. Optimise for the exam you'll sit, not the
dashboard you'll look at.
