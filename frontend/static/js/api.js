/* api.js — thin fetch wrappers. The API is the only source of truth; the frontend never
   hardcodes content. */
const API = {
  async _get(path) {
    const r = await fetch('/api' + path);
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
    return r.json();
  },
  async _post(path, body) {
    const r = await fetch('/api' + path, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
    return r.json();
  },
  health()            { return this._get('/health'); },
  course()            { return this._get('/course'); },
  today()             { return this._get('/today'); },
  radar()             { return this._get('/radar'); },
  problem(key)        { return this._get('/problems/' + encodeURIComponent(key)); },
  reveal(key, body)   { return this._post('/problems/' + encodeURIComponent(key) + '/reveal', body); },
  grade(key, body)    { return this._post('/problems/' + encodeURIComponent(key) + '/grade', body); },
  hint(key, body)     { return this._post('/problems/' + encodeURIComponent(key) + '/hint', body); },
  card(key)           { return this._get('/cards/' + encodeURIComponent(key)); },
  reviewCard(key, g)  { return this._post('/cards/' + encodeURIComponent(key) + '/review', { grade: g }); },
  startSkill(key)     { return this._post('/skills/' + encodeURIComponent(key) + '/start', {}); },
  errors()            { return this._get('/errors'); },
  coach()             { return this._get('/coach'); },
  concepts()          { return this._get('/concepts'); },
  concept(key)        { return this._get('/concepts/' + encodeURIComponent(key)); },
  playbooks()         { return this._get('/playbooks'); },
  playbook(key)       { return this._get('/playbooks/' + encodeURIComponent(key)); },
  mockCapability()    { return this._get('/mock/capability'); },
  mockHistory()       { return this._get('/mock/history'); },
  assembleMock(t)     { return this._post('/mock/assemble', { quiz_target: t }); },
  assembleExam(scope) { return this._post('/mock/assemble', { scope: scope || 'exam-sprint' }); },
  getMock(id)         { return this._get('/mock/' + id); },
  gradeMock(id, body) { return this._post('/mock/' + id + '/grade', body); },
  async transcribeMock(id, files) {
    const fd = new FormData();
    for (const f of files) fd.append('files', f);
    const r = await fetch('/api/mock/' + id + '/transcribe', { method: 'POST', body: fd });
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
    return r.json();
  },
};
