/* app.js — state, hash router, views. Framework-free. Every view re-renders #view from
   scratch; every innerHTML interpolation of content goes through esc(). */

const view = document.getElementById('view');
const KATEX_MACROS = {
  '\\abs': '\\left|#1\\right|',
  '\\N': '\\mathbb{N}', '\\Z': '\\mathbb{Z}', '\\Q': '\\mathbb{Q}', '\\R': '\\mathbb{R}',
};
window.KATEX_MACROS = KATEX_MACROS;   // shared with viz.js

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
/* Content prose may carry **bold**, *italic*, and inline math. Escape first, then reintroduce
   a tiny safe subset, then KaTeX renders the math delimiters. */
function md(s) {
  // Math is STASHED behind placeholders (not merely skipped) so prose substitutions never
  // touch LaTeX — e.g. derivatives f'' — while markdown spans may still cross a formula.
  // `**Base case ($n=1$).**` must render bold, so the bold regex needs one continuous prose
  // string with each formula standing in as an inert token. NUL delimits the token because it
  // cannot occur in authored content (a bare " 3 " placeholder would eat real prose digits).
  const math = [];
  const NUL = '\u0000';
  const buf = String(s == null ? '' : s)
    .split(/(\$\$[^$]*\$\$|\$[^$]*\$)/g)
    .map(seg => seg.startsWith('$') ? NUL + (math.push(seg) - 1) + NUL : esc(seg))
    .join('')
    .replace(/``/g, '\u201c').replace(/''/g, '\u201d')
    .replace(/\\emoji\{[^}]*\}/g, '')
    .replace(/---/g, '\u2014')
    .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
    .replace(/(^|[^*])\*([^*]+)\*/g, '$1<i>$2</i>')
    .replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
  return buf.replace(/\u0000(\d+)\u0000/g, (_, i) => esc(math[+i]));  // KaTeX renders these
}

function renderMath(el) {
  if (!window.renderMathInElement) return;
  try {
    renderMathInElement(el, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false },
        { left: '\\[', right: '\\]', display: true },
      ],
      macros: KATEX_MACROS, throwOnError: false, ignoredClasses: ['no-math'],
    });
  } catch (e) { /* KaTeX best-effort */ }
}
function mount(html) { view.innerHTML = html; renderMath(view); }
function toast(msg) {
  const t = document.createElement('div');
  t.className = 'toast'; t.textContent = msg; document.body.appendChild(t);
  setTimeout(() => t.remove(), 2600);
}

/* ── router ───────────────────────────────────────────────────────────── */
const routes = {};
function route(name, fn) { routes[name] = fn; }

async function router() {
  const raw = (location.hash.replace(/^#\//, '') || 'today');
  const [name, ...rest] = raw.split('/');
  const arg = rest.length ? decodeURIComponent(rest.join('/')) : null;
  document.querySelectorAll('.navlink').forEach(a =>
    a.classList.toggle('active', a.getAttribute('href') === '#/' + name));
  view.innerHTML = '<div class="spinner"></div>';
  const fn = routes[name] || routes.today;
  try { await fn(arg); }
  catch (e) { mount(`<div class="empty"><b>Something broke.</b><br>${esc(e.message)}</div>`); }
}
window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', () => {
  if (!location.hash) location.hash = '#/today';
  router();
});

document.getElementById('themebtn').onclick = () => {
  const cur = document.documentElement.dataset.theme;
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('tuulai-theme', next);
};

/* ── Today ────────────────────────────────────────────────────────────── */
route('today', async () => {
  const t = await API.today();
  const days = t.days_until_quiz;
  const countdown = days == null ? '' : `
    <div class="countdown"><span class="n">${days}</span><span class="l">days to ${esc(t.quiz_target || 'quiz')}</span></div>`;
  const streak = `<div class="streakline">
     <span class="chip">🔥 <b>${t.streak}</b>-day streak</span>
     <span class="chip">✦ <b>${t.open_errors}</b> error-log items</span>
     ${t.quiz_title ? `<span class="chip">◈ aiming at <b>${esc(t.quiz_title)}</b></span>` : ''}
   </div>`;

  const cardSec = section(1, 'Warm-up cards', t.cards_due.length,
    t.cards_due.length
      ? `<button class="btn primary" onclick="location.hash='#/cards'">Review ${t.cards_due.length} due card${t.cards_due.length > 1 ? 's' : ''} →</button>`
      : `<div class="empty">No cards due. They activate as you start new skills below.</div>`);

  const revItems = t.review_problems.map(p => itemRow(p)).join('');
  const reviewSec = section(2, 'Interleaved practice', t.review_problems.length,
    t.review_problems.length ? revItems
      : `<div class="empty">Nothing due for review yet — start a new skill to seed the queue.</div>`);

  const newItems = t.new_skills.map(s => `
    <button class="item" onclick="location.hash='#/skill/${encodeURIComponent(s.key)}'">
      <span class="tag">new</span>
      <span class="body"><span class="t">${esc(s.name)}</span>
        <span class="m">first contact — worked example, then you try</span></span>
      <span class="go">→</span></button>`).join('');
  const newSec = section(3, 'New material', t.new_skills.length,
    t.new_skills.length ? newItems
      : `<div class="empty"><b>All caught up on new material</b> for this quiz window.</div>`);

  mount(`
    <div class="pagehead"><div>
       <h1>Today</h1><div class="sub">Reviews first, then new material — the order is the method.</div>
     </div>${countdown}</div>
    ${streak}${cardSec}${reviewSec}${newSec}`);
});

function section(step, title, count, inner) {
  return `<section class="section">
    <div class="section-h"><span class="step">${step}</span><h2>${esc(title)}</h2>
      <span class="count">${count}</span></div>${inner}</section>`;
}
function itemRow(p) {
  const tagcls = p.topic === 'logic' ? 'logic' : '';
  const kind = p.kind === 'proof' ? 'proof' : p.topic;
  return `<button class="item" onclick="location.hash='#/problem/${encodeURIComponent(p.key)}'">
    <span class="tag ${p.kind === 'proof' ? 'proof' : tagcls}">${esc(kind)}</span>
    <span class="body"><span class="t">${esc(p.title)}</span>
      <span class="m">${p.points} pt · ~${p.est_minutes} min</span></span>
    <span class="go">→</span></button>`;
}

/* ── Problem player (the core loop) ───────────────────────────────────── */
const player = { key: null, confidence: null, attemptId: null, hints: 0, result: null, taxonomy: null, t0: 0 };

route('problem', async (key) => {
  const p = await API.problem(key);
  Object.assign(player, { key, confidence: null, attemptId: null, hints: 0, result: null, taxonomy: null, t0: Date.now() });

  const parts = (p.parts || []).map((pt, i) => pt.prompt ? `
    <div class="part"><span class="pt">PART ${String.fromCharCode(65 + i)} · ${pt.points} pt</span>
      <div>${md(pt.prompt)}</div></div>` : '').join('');

  mount(`
    <div class="pagehead"><div>
      <h1>${esc(p.title)}</h1>
      <div class="sub">${esc(p.topic)}${p.subtopic ? ' · ' + esc(p.subtopic) : ''} · ${p.points} pt · closed-book, on paper${p.difficulty === 'stretch' ? ' · <span class="diff-badge">exam bar</span>' : ''}</div>
    </div><button class="btn ghost sm" onclick="history.back()">← back</button></div>

    <div class="problem-statement">${md(p.statement)}${parts}</div>
    ${p.playbook ? `<div class="play-nudge">Don't know how to start? <a href="#/playbooks/${encodeURIComponent(p.playbook)}">Open the playbook — recognise the type and get the first line →</a></div>` : ''}

    <div class="panel" id="ladder">
      <h3>Stuck? Climb one rung at a time.</h3>
      <div class="ladder" id="hintlist"></div>
      <button class="btn ghost sm" id="hintbtn" style="margin-top:12px">Ask for a nudge</button>
    </div>

    <div class="panel">
      <h3>Before you check — how sure are you?</h3>
      <div class="confidence" id="conf">
        ${confBtn('sure', '🎯', 'Sure', 'I can defend every step')}
        ${confBtn('shaky', '🤔', 'Shaky', 'Got an answer, not certain')}
        ${confBtn('guess', '🎲', 'Guessing', 'Mostly a shot in the dark')}
      </div>
      <button class="btn primary" id="revealbtn" disabled style="margin-top:14px;width:100%">
        Show the worked solution</button>
      <div class="sub" style="margin-top:8px;font-size:.82rem;color:var(--ink-3)">
        The solution unlocks only after you commit a confidence call — that gap is where calibration is trained.</div>
    </div>

    <div id="afterreveal"></div>`);

  // hint ladder
  const hintlist = document.getElementById('hintlist');
  document.getElementById('hintbtn').onclick = async (e) => {
    player.hints += 1;
    try {
      const h = await API.hint(key, { rung: player.hints, note: '' });
      const div = document.createElement('div');
      div.className = 'hint-line';
      div.innerHTML = `<div class="hint-bubble"><div class="who">Nudge ${h.rung + 1}${h.is_llm ? '' : ' · offline'}</div>${md(h.text)}</div>`;
      hintlist.appendChild(div); renderMath(div);
      if (player.hints >= 3) e.target.style.display = 'none';
    } catch (err) { toast(err.message); }
  };

  // confidence
  document.querySelectorAll('#conf .conf').forEach(b => b.onclick = () => {
    player.confidence = b.dataset.v;
    document.querySelectorAll('#conf .conf').forEach(x => x.classList.toggle('sel', x === b));
    document.getElementById('revealbtn').disabled = false;
  });

  // reveal
  document.getElementById('revealbtn').onclick = async (e) => {
    e.target.disabled = true; e.target.textContent = 'Revealing…';
    const seconds = Math.round((Date.now() - player.t0) / 1000);
    try {
      const r = await API.reveal(key, { confidence: player.confidence, mode: 'paper', hints_used: player.hints, seconds });
      player.attemptId = r.attempt_id;
      renderSolution(p, r);
    } catch (err) { toast(err.message); e.target.disabled = false; e.target.textContent = 'Show the worked solution'; }
  };
});

function confBtn(v, e, l, d) {
  return `<button class="conf" data-v="${v}"><div class="e">${e}</div><div class="l">${l}</div><div class="d">${esc(d)}</div></button>`;
}

function renderSolution(p, r) {
  const ans = (r.parts || []).filter(pt => pt.answer).map((pt, i) =>
    `<div class="answer-key"><b>Part ${String.fromCharCode(65 + i)}:</b> ${md(pt.answer)}</div>`).join('')
    || (r.answer ? `<div class="answer-key"><b>Answer:</b> ${md(r.answer)}</div>` : '');

  const el = document.getElementById('afterreveal');
  const shore = p.concept
    ? `<div class="sub" style="margin-top:12px;font-size:.86rem">Shore up the idea: <a href="#/concepts/${encodeURIComponent(p.concept)}">review the concept →</a></div>`
    : '';
  el.innerHTML = `
    <div class="panel solution worked">
      <h3>Worked solution</h3>
      ${ans}
      <div class="ref">${md(r.solution)}</div>
      ${shore}
    </div>
    <div class="panel">
      <h3>Grade yourself honestly — this is the only number that counts.</h3>
      <div class="grade-row" id="grade">
        <button class="grade correct" data-v="correct">Got it</button>
        <button class="grade partial" data-v="partial">Partly</button>
        <button class="grade wrong" data-v="wrong">Missed it</button>
      </div>
      <div id="taxwrap" style="display:none">
        <div class="sub" style="margin:14px 0 4px;font-size:.86rem">What kind of miss? (each has a different fix)</div>
        <div class="taxonomy" id="tax">
          ${taxBtn('concept', 'Concept gap', "didn't know the idea/technique")}
          ${taxBtn('procedure', 'Procedure', 'right idea, execution broke')}
          ${taxBtn('misread', 'Misread', 'solved the wrong question')}
          ${taxBtn('slip', 'Slip', 'careless arithmetic/sign')}
        </div>
      </div>
      <button class="btn primary" id="donebtn" disabled style="margin-top:16px;width:100%">Log it &amp; continue</button>
    </div>`;
  renderMath(el);

  document.querySelectorAll('#grade .grade').forEach(b => b.onclick = () => {
    player.result = b.dataset.v;
    document.querySelectorAll('#grade .grade').forEach(x => x.classList.toggle('sel', x === b));
    document.getElementById('taxwrap').style.display = player.result === 'correct' ? 'none' : 'block';
    document.getElementById('donebtn').disabled = player.result !== 'correct' && !player.taxonomy;
  });
  document.querySelectorAll('#tax .tax').forEach(b => b.onclick = () => {
    player.taxonomy = b.dataset.v;
    document.querySelectorAll('#tax .tax').forEach(x => x.classList.toggle('sel', x === b));
    document.getElementById('donebtn').disabled = false;
  });
  document.getElementById('donebtn').onclick = async (e) => {
    e.target.disabled = true;
    try {
      const g = await API.grade(player.key, {
        attempt_id: player.attemptId, result: player.result,
        error_taxonomy: player.result === 'correct' ? null : player.taxonomy, error_note: '',
      });
      const credited = Object.keys(g.credited || {}).length;
      toast(player.result === 'correct'
        ? `Logged. ${credited} skill${credited !== 1 ? 's' : ''} advanced.`
        : 'Logged to your error log — a re-test is scheduled.');
      setTimeout(() => location.hash = '#/today', 700);
    } catch (err) { toast(err.message); e.target.disabled = false; }
  };
}
function taxBtn(v, t, d) {
  return `<button class="tax" data-v="${v}"><div class="tt">${esc(t)}</div><div class="td">${esc(d)}</div></button>`;
}

/* ── new-skill first contact ──────────────────────────────────────────── */
route('skill', async (key) => {
  const res = await API.startSkill(key);
  // worked-examples-first: send novices to the concept page before the exercise (if one exists)
  if (res.concept) {
    toast('Cards activated — start with the concept.');
    location.hash = '#/concepts/' + encodeURIComponent(res.concept);
  } else if (res.first_contact) {
    toast('Cards activated — here is your worked example.');
    location.hash = '#/problem/' + encodeURIComponent(res.first_contact);
  } else {
    toast(`${res.activated_cards} cards activated.`);
    location.hash = '#/cards';
  }
});

/* ── Quiz Radar ───────────────────────────────────────────────────────── */
route('radar', async () => {
  const r = await API.radar();
  if (!r.quiz) return mount(`<div class="empty">No upcoming quiz.</div>`);
  const pct = r.total ? Math.round(100 * r.solid / r.total) : 0;
  const rows = r.skills.map(s => `
    <div class="radar-row"><span class="dot ${s.readiness}"></span>
      <span class="nm">${esc(s.name)}</span>
      <span class="st ${s.readiness}">${s.readiness}</span></div>`).join('');
  mount(`
    <div class="pagehead"><div>
      <h1>Quiz Radar</h1>
      <div class="sub">${esc(r.title)} · ${r.days_until} days out · covers weeks ${r.covers_weeks.join(' & ')}</div>
    </div><div class="countdown"><span class="n">${r.solid}/${r.total}</span><span class="l">skills solid</span></div></div>
    <div class="readybar"><i style="--p:${pct / 100}"></i></div>
    <div class="radar-grid">${rows}</div>`);
});

/* ── Cards ────────────────────────────────────────────────────────────── */
route('cards', async () => {
  const t = await API.today();
  const queue = t.cards_due.map(c => c.key);
  if (!queue.length) return mount(`
    <div class="pagehead"><div><h1>Cards</h1><div class="sub">Spaced retrieval of definitions & techniques.</div></div></div>
    <div class="empty"><b>No cards due right now.</b> They activate as you start new skills, and return on schedule.</div>`);
  runCard(queue, 0, { done: 0 });
});

async function runCard(queue, i, stats) {
  if (i >= queue.length) return mount(`
    <div class="pagehead"><div><h1>Cards</h1></div></div>
    <div class="empty"><b>Done — ${stats.done} card${stats.done !== 1 ? 's' : ''} reviewed.</b><br>
      <button class="btn primary" style="margin-top:12px" onclick="location.hash='#/today'">Back to Today</button></div>`);
  const card = await API.card(queue[i]);
  mount(`
    <div class="pagehead"><div><h1>Cards</h1><div class="sub">${i + 1} of ${queue.length}</div></div></div>
    <div class="card-wrap">
      <div class="flashcard"><span class="genre">${esc(card.genre)}</span><div>${md(card.front)}</div></div>
    </div>
    <button class="btn primary" id="flip" style="margin-top:14px;width:100%">Show answer</button>
    <div id="back"></div>`);
  document.getElementById('flip').onclick = () => {
    document.getElementById('flip').style.display = 'none';
    const b = document.getElementById('back');
    b.innerHTML = `
      <div class="panel solution"><h3>Answer</h3><div>${md(card.back)}</div></div>
      <div class="grade-row">
        <button class="grade wrong" data-g="again">Again</button>
        <button class="grade partial" data-g="good">Good</button>
        <button class="grade correct" data-g="easy">Easy</button>
      </div>`;
    renderMath(b);
    b.querySelectorAll('.grade').forEach(btn => btn.onclick = async () => {
      await API.reviewCard(card.key, btn.dataset.g);
      runCard(queue, i + 1, { done: stats.done + 1 });
    });
  };
}

/* ── Error log ────────────────────────────────────────────────────────── */
route('errors', async () => {
  const errs = await API.errors();
  const body = errs.length ? errs.map(e => `
    <div class="radar-row"><span class="dot shaky"></span>
      <span class="nm">${esc(e.problem_key.split('.').slice(-1)[0])} · <i>${esc(e.taxonomy)}</i>${
        e.taxonomy === 'concept' && e.concept ? ` · <a href="#/concepts/${encodeURIComponent(e.concept)}">review concept →</a>` : ''}</span>
      <span class="st shaky">re-test due ${esc((e.retest_due || '').slice(0, 10) || 'soon')}</span></div>`).join('')
    : `<div class="empty"><b>Empty error log.</b> Misses land here, each classified, each with a scheduled re-test variant.</div>`;
  mount(`<div class="pagehead"><div><h1>Error log</h1>
    <div class="sub">Every miss, classified and queued for a fresh re-test before the quiz.</div></div></div>${body}`);
});

/* ── Mock quiz (Loop 2: assemble → print → photograph → grade) ─────────── */
route('mock', async (arg) => {
  if (arg) return mockTake(arg);
  const [cap, hist, course] = await Promise.all([API.mockCapability(), API.mockHistory(), API.course()]);
  const nq = course.next_quiz;
  const histHtml = hist.length ? hist.map(h => {
    const rep = h.graded_json ? JSON.parse(h.graded_json) : {};
    return `<div class="rprob"><div class="rt"><span>${esc(h.quiz_target || 'mock')} · ${esc((h.at||'').slice(0,10))}</span>
      <span>${h.score}/${h.total} · ${rep.pct != null ? rep.pct + '%' : ''}</span></div></div>`;
  }).join('') : `<div class="empty">No mocks yet. Your first full dress rehearsal is the best test-anxiety treatment there is.</div>`;
  mount(`
    <div class="pagehead"><div><h1>Mock quiz</h1>
      <div class="sub">A full, timed, pen-and-paper rehearsal under real quiz rules — then photographed and graded.</div></div></div>
    <div class="mock-actions">
      <button class="btn primary" id="genexam">🎯 Exam sprint — full timed rehearsal →</button>
      <button class="btn ghost" id="gen">Or a short mock for ${esc(nq || 'the next quiz')} →</button>
    </div>
    <div class="provider-note">Exam sprint = a longer, mixed set drawn from logic, proofs, sets &amp; functions, and sequences &amp; series — one sitting, on paper, under the clock. The real test of readiness.</div>
    <div class="provider-note">${cap.available
      ? `Auto-grading on via <b>${esc(cap.provider)}</b>${cap.model ? ' (' + esc(cap.model) + ')' : ''}: photograph your work and it transcribes + grades against the rubric.`
      : `No vision model configured — you'll self-grade against the reference solutions (still a real rehearsal). Set <code>ANTHROPIC_API_KEY</code> (or <code>OPENAI_API_KEY</code>) to enable photo auto-grading.`}</div>
    <h3 style="margin-top:30px">Past mocks</h3>${histHtml}`);
  document.getElementById('gen').onclick = async (e) => {
    e.target.disabled = true; e.target.textContent = 'Assembling…';
    try { const m = await API.assembleMock(nq); location.hash = '#/mock/' + m.id; }
    catch (err) { toast(err.message); e.target.disabled = false; e.target.textContent = 'Generate a mock →'; }
  };
  document.getElementById('genexam').onclick = async (e) => {
    e.target.disabled = true; e.target.textContent = 'Assembling your exam…';
    try { const m = await API.assembleExam('exam-sprint'); location.hash = '#/mock/' + m.id; }
    catch (err) { toast(err.message); e.target.disabled = false; e.target.textContent = '🎯 Exam sprint — full timed rehearsal →'; }
  };
});

const mockState = { id: null, mock: null, files: [], t0: 0, timerH: null };

async function mockTake(id) {
  const m = await API.getMock(id);
  mockState.id = id; mockState.mock = m; mockState.files = []; mockState.t0 = Date.now();
  const problems = m.problems.map((p, i) => {
    const parts = (p.parts || []).map((pt, j) => pt.prompt
      ? `<div style="margin-top:8px">(${String.fromCharCode(97 + j)}) [${pt.points} pt] ${md(pt.prompt)}</div>` : '').join('');
    return `<div class="qproblem">
      <span class="qpts">${p.points} pt</span>
      <span class="qnum">Problem ${i + 1}.</span>
      <div class="qbody">${md(p.statement)}${parts}</div>
      <div class="writespace ${p.kind === 'proof' ? 'proof' : ''}"></div></div>`;
  }).join('');
  const rules = m.conditions.map(c => `<li>${esc(c)}</li>`).join('');
  mount(`
    <div class="pagehead"><div><h1>${esc(m.quiz_title)}</h1>
      <div class="sub">${m.points} pt · ${m.duration_min} min · print it, do it by hand under the timer</div></div>
      <button class="btn ghost sm no-print" onclick="location.hash='#/mock'">← mocks</button></div>
    <div class="mock-actions no-print">
      <button class="btn primary" onclick="window.print()">Print / save PDF</button>
      <span class="timer" id="timer">${String(m.duration_min).padStart(2,'0')}:00</span>
      <button class="btn ghost" id="tograde">I've finished — grade my answers →</button>
    </div>
    <div class="paper" id="paper">
      <div class="qhead"><div class="code">${esc(course_code())}</div>
        <h2>${esc(m.quiz_title)}</h2>
        <div class="meta">${m.points} points · ${m.duration_min} minutes · closed book</div></div>
      <div class="rules"><div class="rh">⚡ Rules</div><ul>${rules}</ul></div>
      <div class="namebar"><div class="field">Name:</div><div class="field">Student ID:</div></div>
      ${problems}</div>
    <div id="mockgrade"></div>`);
  startTimer(m.duration_min);
  document.getElementById('tograde').onclick = async () => {
    const minutes = Math.round((Date.now() - mockState.t0) / 60000);
    const cap = await API.mockCapability();
    if (mockState.timerH) clearInterval(mockState.timerH);
    if (cap.available) renderGradeUI(m, minutes);
    else renderSelfGrade(m, minutes);   // no vision → self-grade against solutions directly
  };
}

let _course_code = 'COURSE';
function course_code() { return _course_code; }

function startTimer(minutes) {
  if (mockState.timerH) clearInterval(mockState.timerH);
  let remaining = minutes * 60;
  const el = () => document.getElementById('timer');
  mockState.timerH = setInterval(() => {
    remaining -= 1;
    const e = el(); if (!e) { clearInterval(mockState.timerH); return; }
    if (remaining <= 0) { e.textContent = 'TIME'; e.style.color = 'var(--shaky)'; clearInterval(mockState.timerH); return; }
    const mm = String(Math.floor(remaining / 60)).padStart(2, '0');
    const ss = String(remaining % 60).padStart(2, '0');
    e.textContent = `${mm}:${ss}`;
  }, 1000);
}

function renderGradeUI(m, minutes) {
  const el = document.getElementById('mockgrade');
  el.scrollIntoView({ behavior: 'smooth' });
  el.innerHTML = `
    <div class="panel">
      <h3>Grade your attempt</h3>
      <p class="sub" style="font-size:.88rem">Photograph each page of your handwritten work (or drag files in). We transcribe it, you confirm, then it's graded per rubric.</p>
      <label class="filedrop" id="drop">
        <input type="file" accept="image/*" multiple id="fileinput">
        📷 Tap to add photos of your work
      </label>
      <div class="thumbs" id="thumbs"></div>
      <button class="btn primary" id="process" disabled style="margin-top:16px;width:100%">Transcribe &amp; grade</button>
      <div class="provider-note" id="capnote"></div>
    </div>`;
  const fi = document.getElementById('fileinput');
  document.getElementById('drop').onclick = () => fi.click();
  fi.onchange = () => {
    mockState.files = [...fi.files];
    const t = document.getElementById('thumbs'); t.innerHTML = '';
    mockState.files.forEach(f => { const img = document.createElement('img'); img.src = URL.createObjectURL(f); t.appendChild(img); });
    document.getElementById('process').disabled = mockState.files.length === 0;
  };
  document.getElementById('process').onclick = () => processMock(m, minutes);
  API.mockCapability().then(c => {
    document.getElementById('capnote').innerHTML = c.available
      ? `Grading via ${esc(c.provider)}.` : `No vision model — after upload you'll self-grade against the solutions.`;
  });
}

async function processMock(m, minutes) {
  const btn = document.getElementById('process');
  btn.disabled = true; btn.textContent = 'Reading your handwriting…';
  let tr = null;
  try {
    const res = await API.transcribeMock(m.id, mockState.files);
    tr = res.transcriptions;
  } catch (err) { toast('Upload failed: ' + err.message); }
  const cap = await API.mockCapability();
  if (cap.available && tr) {
    renderConfirm(m, tr, minutes);
  } else {
    renderSelfGrade(m, minutes);   // no vision or transcription failed
  }
}

function renderConfirm(m, tr, minutes) {
  const el = document.getElementById('mockgrade');
  const blocks = m.problems.map((p, i) => `
    <div class="trans-block"><label>Problem ${i + 1} — ${esc(p.title)} (edit if the transcription is off)</label>
      <textarea data-key="${esc(p.key)}">${esc(tr[p.key] || '')}</textarea></div>`).join('');
  el.innerHTML = `
    <div class="panel">
      <h3>Confirm the transcription</h3>
      <p class="sub" style="font-size:.86rem">This is what we read from your photos. Fix anything misread — then grade. (Transcription errors are the #1 source of bad auto-grades.)</p>
      ${blocks}
      <button class="btn primary" id="dograde" style="margin-top:12px;width:100%">Grade against the rubric</button>
    </div>`;
  renderMath(el);
  document.getElementById('dograde').onclick = async (e) => {
    e.target.disabled = true; e.target.textContent = 'Grading…';
    const transcriptions = {};
    el.querySelectorAll('textarea[data-key]').forEach(t => transcriptions[t.dataset.key] = t.value);
    try {
      const rep = await API.gradeMock(m.id, { transcriptions, minutes });
      renderReport(rep, minutes);
    } catch (err) { toast(err.message); e.target.disabled = false; e.target.textContent = 'Grade against the rubric'; }
  };
}

function renderSelfGrade(m, minutes) {
  const el = document.getElementById('mockgrade');
  const blocks = m.problems.map((p, i) => `
    <div class="rprob"><div class="rt"><span>Problem ${i + 1} — ${esc(p.title)}</span><span>${p.points} pt</span></div>
      <div style="margin:8px 0"><a href="#" class="revealsol" data-key="${esc(p.key)}">▸ show reference solution</a><div class="solbox" id="sol-${i}"></div></div>
      <label style="font-size:.84rem">Your score (0–${p.points}):
        <input type="number" min="0" max="${p.points}" step="0.1" data-key="${esc(p.key)}" style="width:70px;margin-left:6px;padding:4px" value="0"></label>
    </div>`).join('');
  el.innerHTML = `
    <div class="panel"><h3>Self-grade against the solutions</h3>
      <p class="sub" style="font-size:.86rem">No auto-grader configured. Compare your handwritten work to each reference solution and score honestly.</p>
      ${blocks}
      <button class="btn primary" id="selfsubmit" style="margin-top:12px;width:100%">Record scores</button></div>`;
  el.querySelectorAll('.revealsol').forEach(a => a.onclick = async (ev) => {
    ev.preventDefault();
    const key = a.dataset.key; const box = a.nextElementSibling;
    // reveal via a logged attempt-free path: fetch solution through reveal (records a mock reveal)
    const r = await API.reveal(key, { confidence: 'guess', mode: 'paper' });
    box.innerHTML = `<div class="ref" style="margin-top:8px">${md(r.solution)}</div>`; renderMath(box); a.style.display = 'none';
  });
  document.getElementById('selfsubmit').onclick = async (e) => {
    e.target.disabled = true;
    const self_scores = {};
    el.querySelectorAll('input[type=number][data-key]').forEach(inp => self_scores[inp.dataset.key] = parseFloat(inp.value) || 0);
    try { const rep = await API.gradeMock(m.id, { self_scores, minutes }); renderReport(rep, minutes); }
    catch (err) { toast(err.message); e.target.disabled = false; }
  };
}

function renderReport(rep, minutes) {
  const el = document.getElementById('mockgrade');
  const rows = rep.results.map((r, i) => `
    <div class="rprob"><div class="rt"><span>Problem ${i + 1} — ${esc(r.title)}</span>
      <span>${r.graded ? (r.score + '/' + r.max) : 'ungraded'}</span></div>
      ${r.feedback ? `<div class="rf">${esc(r.feedback)}</div>` : ''}
      ${r.miss_taxonomy && r.miss_taxonomy !== 'none' ? `<div class="rf">→ logged as a <b>${esc(r.miss_taxonomy)}</b> miss; re-test scheduled.</div>` : ''}
    </div>`).join('');
  el.innerHTML = `
    <div class="panel solution">
      <div class="report-tile"><span class="big">${rep.pct}%</span><span class="band">${esc(rep.band)}</span>
        <span class="sub">${rep.score}/${rep.max} pts · ${minutes} min</span></div>
      ${rows}
      <div class="provider-note" style="margin-top:12px">Misses were added to your Error log with a scheduled re-test. On the real quiz this is ${gradeMeaning(rep.pct)}.</div>
      <button class="btn ghost" style="margin-top:14px" onclick="location.hash='#/mock'">Back to mocks</button>
    </div>`;
  renderMath(el);
  el.scrollIntoView({ behavior: 'smooth' });
}
function gradeMeaning(pct) {
  if (pct >= 90) return 'an A-range result — solid';
  if (pct >= 80) return 'a B-range result';
  if (pct >= 70) return 'a C-range result — worth tightening';
  if (pct >= 60) return 'a passing-but-fragile result';
  return 'below passing — this is exactly what the rehearsal is for';
}

/* ── Coach (weekly report) ────────────────────────────────────────────── */
route('coach', async () => {
  const r = await API.coach();
  const cw = r.calibration.confident_wrong_titles || [];
  const atRisk = r.at_risk.map(s => `<span class="dot ${s.readiness}"></span> ${esc(s.name)}`).join('<br>');
  const cal = r.calibration.buckets;
  const calBar = ['sure', 'shaky', 'guess'].map(c =>
    `<div class="cal-row"><span class="cal-l">${c}</span>
       <div class="cal-track"><i style="--w:${cal[c].accuracy / 100}"></i></div>
       <span class="cal-n">${cal[c].accuracy}% <small>(${cal[c].n})</small></span></div>`).join('');

  mount(`
    <div class="pagehead"><div><h1>Coach</h1>
      <div class="sub">Your week, read from the ledger — not from how it felt.</div></div>
      <div class="countdown"><span class="n">${r.quiz.solid}/${r.quiz.total}</span><span class="l">solid · ${r.quiz.days_until}d to quiz</span></div></div>

    <div class="panel solution"><h3>This week</h3><div class="ref">${md(r.narrative)}</div></div>

    <div class="coach-grid">
      <div class="panel"><h3>Calibration</h3>
        <p class="sub" style="font-size:.82rem">Accuracy at each confidence level. Healthy = sure &gt; shaky &gt; guess.</p>
        ${calBar}
        ${cw.length ? `<div class="danger-box"><b>${cw.length} confident-but-wrong</b> — your biggest risk, and the most fixable. Re-derive cold:<ul>${cw.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>` : `<div class="ok-box">No confident-wrong items — well calibrated.</div>`}
      </div>

      <div class="panel"><h3>At-risk skills for ${esc(r.quiz.target || 'the quiz')}</h3>
        ${atRisk ? `<div style="line-height:2">${atRisk}</div>` : `<div class="ok-box">Nothing at risk — coverage is solid.</div>`}
      </div>

      <div class="panel"><h3>Habits</h3>
        <div class="stat-line"><span>Active days this week</span><b>${r.week_active_days}/7</b></div>
        <div class="stat-line"><span>Streak</span><b>${r.streak}</b></div>
        <div class="stat-line"><span>Cold-solve rate</span><b>${r.hint_velocity.cold_rate}%</b></div>
        <div class="stat-line"><span>On paper (vs typed)</span><b>${r.modality.paper_rate}%</b></div>
        ${r.hint_velocity.hint_heavy ? `<div class="sub" style="font-size:.82rem;margin-top:8px">${r.hint_velocity.hint_heavy} attempt(s) leaned hard on hints this week — try to bank more cold solves.</div>` : ''}
      </div>

      <div class="panel"><h3>Error log</h3>
        <div class="stat-line"><span>Open items</span><b>${r.errors.open}</b></div>
        <div class="stat-line"><span>Re-tests due now</span><b>${r.errors.due_now}</b></div>
        ${Object.entries(r.errors.by_taxonomy).map(([k, v]) => `<div class="stat-line"><span>${esc(k)}</span><b>${v}</b></div>`).join('')}
        <button class="btn ghost sm" style="margin-top:10px" onclick="location.hash='#/errors'">Open error log →</button>
      </div>
    </div>

    <div class="panel"><h3>The plan for this week</h3>
      ${r.plan.drill_skills.length ? `<p>Drill these to solid before the quiz:</p><ul>${r.plan.drill_skills.map(s => `<li>${esc(s.name)} <small>(${s.readiness})</small></li>`).join('')}</ul>` : `<p>Coverage is solid — hold it with cold retrieval and a timed mock.</p>`}
      <div class="mock-actions" style="margin-top:8px">
        <button class="btn primary" onclick="location.hash='#/today'">Start today's session →</button>
        <button class="btn ghost" onclick="location.hash='#/mock'">Run a mock</button>
      </div>
    </div>`);
});

/* ── Concepts (visual homes for the load-bearing ideas) ────────────────── */
route('concepts', async (arg) => {
  if (arg) return conceptPage(arg);
  const list = await API.concepts();
  const dots = r => r.map(x => `<span class="dot ${x}" title="${esc(x)}"></span>`).join('');
  const row = c => `
      <button class="concept-row" onclick="location.hash='#/concepts/${encodeURIComponent(c.key)}'">
        <span class="body"><span class="t">${esc(c.title)}</span><span class="m">${esc(c.summary)}</span></span>
        <span class="dots">${dots(c.readiness)}</span><span class="go">→</span>
      </button>`;
  // modules (e.g. "Quiz 1 — proof writing") lead; the rest group by week
  const byModule = {}, byWeek = {};
  list.forEach(c => c.module
    ? (byModule[c.module] = byModule[c.module] || []).push(c)
    : (byWeek[c.week] = byWeek[c.week] || []).push(c));
  const modSections = Object.keys(byModule).map(m => `
    <div class="wk-head mod">${esc(m)}</div>
    ${byModule[m].map(row).join('')}`).join('');
  const sections = modSections + Object.keys(byWeek).sort((a, b) => a - b).map(wk => `
    <div class="wk-head">Week ${wk}</div>
    ${byWeek[wk].map(row).join('')}`).join('');
  mount(`
    <div class="pagehead"><div><h1>Concepts</h1>
      <div class="sub">The idea, the picture, the trap — then straight into retrieval. Reading alone moves nothing.</div></div></div>
    ${sections || '<div class="empty">No concept pages yet.</div>'}`);
});

async function conceptPage(key) {
  const c = await API.concept(key);
  const blocks = c.blocks.map((b, i) => {
    if (b.type === 'text') return `<div class="concept-block">${md(b.body)}</div>`;
    if (b.type === 'example') return `<div class="concept-block example"><span class="lbl">Example</span>${md(b.body)}</div>`;
    if (b.type === 'trap') return `<div class="concept-block trap"><span class="lbl">⚠ The trap</span>${md(b.body)}</div>`;
    if (b.type === 'viz') return `<div class="viz-block" data-viz="${i}"><div class="viz-mount" id="viz-${i}"></div>${b.caption ? `<div class="cap">${md(b.caption)}</div>` : ''}</div>`;
    if (b.type === 'check') return `
      <div class="check-block"><div class="q">${md(b.prompt)}</div>
        <button class="btn ghost sm" data-check="${i}">Reveal</button>
        <div class="a" id="chk-${i}" style="display:none">${md(b.answer)}</div></div>`;
    return '';
  }).join('');

  const hooks = c.retrieval_hooks.map(h => itemRow(
    { key: h.key, title: h.title, topic: 'concept', kind: h.kind, points: 1, est_minutes: 6 })).join('');
  mount(`
    <div class="pagehead"><div><h1>${esc(c.title)}</h1>
      <div class="sub">week ${c.week} · ${c.skills.map(esc).join(' · ')}</div></div>
      <button class="btn ghost sm" onclick="location.hash='#/concepts'">← concepts</button></div>
    ${blocks}
    <section class="section" style="margin-top:30px">
      <div class="section-h"><span class="step">▸</span><h2>Now retrieve — this is the part that counts</h2></div>
      ${hooks || '<div class="empty">No linked problems.</div>'}
      ${c.cards.length ? `<button class="btn primary" style="margin-top:8px" onclick="location.hash='#/cards'">Review ${c.cards.length} linked card${c.cards.length > 1 ? 's' : ''} →</button>` : ''}
    </section>`);
  // mount visualizations + wire checks
  c.blocks.forEach((b, i) => {
    if (b.type === 'viz') { const el = document.getElementById('viz-' + i); if (el && window.renderViz) renderViz(el, b.viz, b.data); }
    if (b.type === 'check') {
      const btn = view.querySelector(`[data-check="${i}"]`);
      if (btn) btn.onclick = () => { document.getElementById('chk-' + i).style.display = 'block'; btn.style.display = 'none'; };
    }
  });
}

/* ── Playbooks: the "how to start" strategy layer ─────────────────────── */
const FAMILY_LABEL = { proofs: 'Proof moves', logic: 'Logic & modelling', analysis: 'Sequences & series' };
const FAMILY_ORDER = ['logic', 'proofs', 'analysis'];

route('playbooks', async (arg) => {
  if (arg) return playbookPage(arg);
  const list = await API.playbooks();
  const byFam = {};
  list.forEach(pb => (byFam[pb.family] = byFam[pb.family] || []).push(pb));
  const dots = r => r.map(x => `<span class="dot ${x}" title="${esc(x)}"></span>`).join('');
  const sections = FAMILY_ORDER.filter(f => byFam[f]).map(f => `
    <div class="wk-head">${esc(FAMILY_LABEL[f] || f)}</div>
    ${byFam[f].map(pb => `
      <button class="concept-row" onclick="location.hash='#/playbooks/${encodeURIComponent(pb.key)}'">
        <span class="body"><span class="t">${esc(pb.title)}</span><span class="m">${md(pb.one_liner)}</span></span>
        <span class="play-meta">${pb.n_moves} moves · ${pb.n_drills} drills</span>
        <span class="dots">${dots(pb.readiness)}</span><span class="go">→</span>
      </button>`).join('')}`).join('');
  mount(`
    <div class="pagehead"><div><h1>Playbooks</h1>
      <div class="sub">Not what a thing <em>is</em> — how to <em>start</em>. Recognise the type, then write the first line. Built from the recitation problems.</div></div></div>
    ${sections || '<div class="empty">No playbooks yet.</div>'}`);
  renderMath(view);
});

async function playbookPage(key) {
  const pb = await API.playbook(key);
  const cues = pb.cues.map(c => `<li>${md(c)}</li>`).join('');
  const moves = pb.moves.map((m, i) => `
    <div class="play-move">
      <div class="sit"><span class="mv-n">${i + 1}</span>${md(m.situation)}</div>
      <div class="play-first"><span class="lbl">Write this first</span>${md(m.first_line)}</div>
      <div class="play-why">${md(m.why)}</div>
    </div>`).join('');
  const drills = (pb.drill_hooks || []).map(h => itemRow(
    { key: h.key, title: h.title, topic: 'drill', kind: h.kind, points: 1, est_minutes: 10 })).join('');
  mount(`
    <div class="pagehead"><div>
      <h1>${esc(pb.title)}</h1>
      <div class="sub"><span class="fam-badge">${esc(FAMILY_LABEL[pb.family] || pb.family)}</span> · ${pb.skills.map(esc).join(' · ')}</div></div>
      <button class="btn ghost sm" onclick="location.hash='#/playbooks'">← playbooks</button></div>

    <div class="play-lead">${md(pb.one_liner)}</div>

    <section class="section"><div class="section-h"><span class="step">▸</span><h2>Reach for this when you see…</h2></div>
      <ul class="play-cues">${cues}</ul></section>

    <section class="section"><div class="section-h"><span class="step">▸</span><h2>The opening moves</h2></div>
      <div class="sub" style="margin:-6px 0 14px">The blank page is the enemy. Match your goal to a row, then copy its first line to unfreeze.</div>
      ${moves}</section>

    <section class="section"><div class="section-h"><span class="step">▸</span><h2>The template</h2></div>
      <div class="play-template">${md(pb.template)}</div></section>

    <section class="section"><div class="section-h"><span class="step">▸</span><h2>Watch it work</h2></div>
      <div class="sub" style="margin:-6px 0 12px">Try the anchor problem yourself first; then reveal the thinking, narrated.</div>
      <button class="btn ghost sm" id="worked-btn">Reveal the worked thinking</button>
      <div class="play-worked" id="worked" style="display:none">${md(pb.worked.trace)}</div></section>

    <section class="section"><div class="section-h"><span class="step">▸</span><h2>The wrong turn</h2></div>
      <div class="concept-block trap"><span class="lbl">⚠ Where students slip</span>${md(pb.pitfall)}</div></section>

    <section class="section" style="margin-top:24px"><div class="section-h"><span class="step">▸</span><h2>Now drill it — cold, on paper</h2></div>
      ${drills || '<div class="empty">No linked drills.</div>'}</section>`);
  const wb = document.getElementById('worked-btn');
  if (wb) wb.onclick = () => { const w = document.getElementById('worked'); w.style.display = 'block'; wb.style.display = 'none'; renderMath(w); };
  renderMath(view);
}

/* ── Library ──────────────────────────────────────────────────────────── */
route('library', async () => {
  const c = await API.course();
  const links = c.course.links;
  mount(`<div class="pagehead"><div><h1>Library</h1>
    <div class="sub">Read in the book; retrieve in Tuulai. Everything the course points to, in one place.</div></div></div>
    <div class="panel"><h3>Textbooks</h3><div class="linklist">
      <a href="${esc(links.textbook_levin)}" target="_blank">Levin — Discrete Mathematics (DMOI 4e)</a>
      <a href="${esc(links.textbook_ac)}" target="_blank">Keller &amp; Trotter — Applied Combinatorics</a>
    </div></div>
    <div class="panel"><h3>Course</h3><div class="linklist">
      <a href="${esc(links.ed)}" target="_blank">Ed — ask questions here (email is unanswered)</a>
      <a href="${esc(links.gitlab)}" target="_blank">Course repository (GitLab)</a>
      <a href="${esc(links.wooclap)}" target="_blank">Wooclap — participation (random lecture each week)</a>
    </div></div>`);
});
