'use strict';
const $ = id => document.getElementById(id), KEY = window.COURSE_CODE === 'MI2021' ? 'xstk-study-v1' : `xstk-study-v1:${window.COURSE_CODE}`;
const progressKey = ['midterm', 'google'].includes(window.STUDY_MODE) ? KEY + ':' + window.STUDY_MODE : KEY;
let saved = {}; try { saved = JSON.parse(localStorage.getItem(progressKey)) || {} } catch { }
let scope = String(saved.scope || 'all'), sessions = saved.sessions || {};
if (scope !== 'all' && !CHAPTERS.some(chapter => String(chapter.number) === scope)) scope = 'all';
let questions = [], session, lastTick = Date.now(), running = false;
let shuffled = !!saved.shuffled;
const sessionKey = () => scope + (shuffled ? ':random' : '');
function shuffle(items) { const result = [...items]; for (let i = result.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[result[i], result[j]] = [result[j], result[i]] } return result }
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
// Allow basic formatting without accepting HTML attributes or executable markup.
function renderText(text) {
    return esc(text)
        .replace(/&lt;\s*\/?\s*br\s*[/\\]?\s*&gt;/gi, '<br>')
        .replace(/&lt;(\/?)\s*(b|strong|i|em|u|sub|sup)\s*&gt;/gi,
            (_, closing, tag) => '<' + closing + tag.toLowerCase() + '>');
}
for (const c of CHAPTERS) { const o = document.createElement('option'); o.value = c.number; o.textContent = `${window.COURSE_CODE === "IT4785E" ? "" : `Chương ${c.number} · `}${c.title} (${c.questions.length} câu)`; $('chapter').append(o) }
function save() { try { localStorage.setItem(progressKey, JSON.stringify({ scope, shuffled, sessions })) } catch { $('save-note').textContent = 'Không thể lưu tiến độ trên trình duyệt này' } }
function pool() { return CHAPTERS.filter(c => scope === 'all' || String(c.number) === scope).flatMap(c => c.questions) }
function newSession() { const list = pool(); return { index: 0, answers: {}, elapsed: 0, paused: false, order: (shuffled ? shuffle(list) : list).map(q => q.id), options: Object.fromEntries(list.map(q => [q.id, (shuffled ? shuffle(q.options) : q.options).map(o => o.id)])) } }
function loadScope() {
    session = sessions[sessionKey()];
    const list = pool();
    const byId = new Map(list.map(q => [q.id, q]));
    session.order = (session.order || []).filter(id => byId.has(id));
    const existing = new Set(session.order);
    const added = list.filter(q => !existing.has(q.id));
    session.order.push(...(shuffled ? shuffle(added) : added).map(q => q.id));
    session.options ||= {};
    for (const q of list) {
        const current = session.options[q.id] || (shuffled ? shuffle(q.options) : q.options).map(option => option.id);
        const ids = new Set(q.options.map(option => option.id));
        session.options[q.id] = [
            ...current.filter(id => ids.has(id)),
            ...q.options.filter(option => !current.includes(option.id)).map(option => option.id),
        ];
    }
    questions = session.order.map(id => {
        const q = byId.get(id);
        return { ...q, options: session.options[id].map(id => q.options.find(option => option.id === id)) };
    });
    session.index = Math.max(0, Math.min(questions.length - 1, session.index || 0));
    lastTick = Date.now();
    running = true;
    $('setup').hidden = true;
    $('exam').hidden = false;
    $('back').hidden = false;
    render();
    updateTimer();
    save();
}
function setup() { running = false; $('exam').hidden = true; $('setup').hidden = false; $('back').hidden = true; $('chapter').value = scope; $('shuffle').checked = shuffled; updateResume() }
function updateResume() { $('resume').hidden = !sessions[sessionKey()]; save() }
function canGrade(q) {
    return Boolean(q.fields?.length || q.answers.length);
}
function isCorrect(q, selected) {
    if (!canGrade(q)) return false;
    if (q.fields) {
        return q.fields.length === selected.length &&
            q.fields.every((accepted, i) => accepted.includes(selected[i].trim()));
    }
    return q.answers.length === selected.length && q.answers.every(id => selected.includes(id));
}
function renderSource(source) {
    if (!source) return '';
    if (source.url) {
        const url = new URL(source.url);
        if (url.protocol !== 'https:' || url.hostname !== 'developer.android.com') return '';
        return `<p class="source-ref"><a href="${esc(url.href)}" target="_blank" rel="noopener">${esc(source.title || 'Google quiz')}</a></p>`;
    }
    const links = source.pages.map(page => {
        const file = String(Number(page)).padStart(2, '0');
        return `<a href="scans/${encodeURIComponent(source.term)}-${file}.jpg" target="_blank" rel="noopener">${Number(page)}</a>`;
    });
    const id = source.code ? `#${esc(source.code)}` : `mục ${Number(source.number)}`;
    return `<p class="source-ref">Nguồn ${esc(source.term)} · ${id} · Trang ${links.join(', ')}</p>`;
}
function answer(q) { return session.answers[q.id] || { selected: [], confirmed: false } }
function render() {
    const q = questions[session.index], a = answer(q);
    const multi = q.type === 'multi' || q.answers.length > 1;
    const fill = q.type === 'fill';
    const review = q.type === 'review' || (!fill && !q.options.length);
    const graded = canGrade(q);
    const result = !a.confirmed ? '' : !graded ? 'Đã lưu · Không tính điểm' :
        isCorrect(q, a.selected) ? '✓ Chính xác' : '✕ Chưa chính xác';
    const resultStyle = a.confirmed && graded ? (isCorrect(q, a.selected) ? 'good' : 'bad') : '';
    const format = q.plain ? esc : renderText;
    const badge = review ? 'Đối chiếu đề' : fill ? 'Điền khuyết' :
        multi ? '▢ Chọn nhiều đáp án' : '◯ Chọn 1 đáp án';
    const options = review ? '' : fill ? q.fields.map((accepted, i) =>
        `<label class="fill-field">Ô ${i + 1}
            <input type="text" data-blank="${i}" autocomplete="off" spellcheck="false"
                value="${esc(a.selected[i] || '')}" ${a.confirmed ? 'disabled' : ''}>
            ${a.confirmed ? `<span>Đáp án: <code>${esc(accepted[0])}</code></span>` : ''}
        </label>`
    ).join('') : q.options.map((option, i) => {
        const selected = a.selected.includes(option.id);
        const correct = a.confirmed && q.answers.includes(option.id);
        const wrong = a.confirmed && graded && selected && !correct;
        const state = correct ? 'correct' : wrong ? 'incorrect' : selected ? 'selected' : '';
        const mark = correct ? '✓ Đáp án đúng' : wrong ? '✕ Bạn chọn' : '';
        return `<label class="option ${state}">
            <input type="${multi ? 'checkbox' : 'radio'}" name="answer" value="${esc(option.id)}"
                ${selected ? 'checked' : ''} ${a.confirmed ? 'disabled' : ''}>
            <span class="letter">${String.fromCharCode(65 + i)}.</span>
            <span class="content ${q.plain ? 'preserve-lines' : ''}">${format(option.text)}</span>
            ${mark ? `<span class="mark">${mark}</span>` : ''}
        </label>`;
    }).join('');
    $('question').innerHTML = `<div class="question-head">
        <div class="question-meta"><span class="question-number">Câu ${session.index + 1} / ${questions.length}</span>
            <span class="badge ${multi ? 'multi' : ''}">${badge}</span></div>
        ${renderSource(q.source)}
        ${q.otherSources?.length ? `<details class="source-ref"><summary>Nguồn trùng (${q.otherSources.length})</summary>
            ${q.otherSources.map(renderSource).join('')}</details>` : ''}
        <div class="question-text ${q.plain ? 'preserve-lines' : ''}" id="question-text">${format(q.text)}</div>
        ${q.note ? `<p class="source-ref">${esc(q.note)}</p>` : ''}
    </div>
    ${options ? `<div class="options" role="group" aria-labelledby="question-text">${options}</div>` : ''}
    <div class="result ${resultStyle}" role="status">${result}</div>
    ${a.confirmed && q.explanation ? `<p class="result">${esc(q.explanation)}</p>` : ''}`;
    if (!q.plain && window.renderMathInElement) renderMathInElement($('question'), {
        delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }, { left: '\\\\(', right: '\\\\)', display: false }, { left: '\\\\[', right: '\\\\]', display: true }],
        throwOnError: false, trust: false
    });
    const ready = selected => fill ? selected.length === q.fields.length && selected.every(value => value.trim()) : selected.length > 0;
    $('question').querySelectorAll('input').forEach(input => {
        input.addEventListener(fill ? 'input' : 'change', () => {
            const selected = fill
                ? [...$('question').querySelectorAll('[data-blank]')].map(el => el.value)
                : [...$('question').querySelectorAll('input:checked')].map(el => el.value);
            session.answers[q.id] = { selected, confirmed: false };
            save();
            if (!fill) $('question').querySelectorAll('.option').forEach(el => el.classList.toggle('selected', el.querySelector('input').checked));
            $('confirm').disabled = !ready(selected);
        });
    });
    $('confirm').disabled = a.confirmed || (!review && !ready(a.selected));
    $('confirm').textContent = a.confirmed ? 'Đã xác nhận ✓' : review ? 'Đã xem' : 'Xác nhận';
    $('prev').disabled = session.index === 0;
    $('next').disabled = session.index === questions.length - 1;
    const done = questions.filter(q => answer(q).confirmed);
    const gradedDone = done.filter(canGrade);
    const right = gradedDone.filter(q => isCorrect(q, answer(q).selected)).length;
    const pct = Math.round(done.length / questions.length * 100);
    $('done').textContent = `${done.length}/${questions.length}`; $('right').textContent = right; $('wrong').textContent = gradedDone.length - right; $('percent').textContent = pct + '%'; $('progress').style.width = pct + '%';
    $('grid').innerHTML = questions.map((q, i) => `<button class="qnav ${answer(q).confirmed ? 'done' : ''} ${i === session.index ? 'current' : ''}" ${i === session.index ? 'aria-current="step"' : ''} aria-label="Câu ${i + 1}, ${answer(q).confirmed ? 'đã làm' : 'chưa xác nhận'}" data-index="${i}">${i + 1}</button>`).join('');
    $('grid').querySelectorAll('button').forEach(b => b.onclick = () => go(Number(b.dataset.index)));
    $('complete').textContent = done.length === questions.length ? `Hoàn thành · Đúng ${right}/${gradedDone.length} câu có chấm điểm` : '';
}
function go(index) { session.index = index; save(); render() }
function tick() { if (!running) return; const now = Date.now(); if (!session.paused && questions.some(q => !answer(q).confirmed)) session.elapsed += Math.max(0, now - lastTick); lastTick = now; updateTimer() }
function updateTimer() { const t = Math.floor(session.elapsed / 1000); $('timer').textContent = [Math.floor(t / 3600), Math.floor(t / 60) % 60, t % 60].map(n => String(n).padStart(2, '0')).join(':'); $('pause').textContent = session.paused ? '▶' : 'Ⅱ'; $('pause').setAttribute('aria-label', session.paused ? 'Tiếp tục thời gian' : 'Tạm dừng thời gian'); $('pause').title = session.paused ? 'Tiếp tục thời gian' : 'Tạm dừng thời gian' }
$('confirm').onclick = () => { const q = questions[session.index], a = answer(q); if ($('confirm').disabled || a.confirmed) return; tick(); a.confirmed = true; session.answers[q.id] = a; save(); render() };
$('prev').onclick = () => go(Math.max(0, session.index - 1)); $('next').onclick = () => go(Math.min(questions.length - 1, session.index + 1));
$('chapter').onchange = () => { scope = $('chapter').value; updateResume() }; $('shuffle').onchange = () => { shuffled = $('shuffle').checked; updateResume() };
$('start').onclick = () => { if (sessions[sessionKey()]) { $('reset-dialog').showModal(); return } sessions[sessionKey()] = newSession(); loadScope() };
$('resume').onclick = loadScope;
$('back').onclick = () => { tick(); save(); setup() };
$('pause').onclick = () => { tick(); session.paused = !session.paused; updateTimer(); save() };
$('reset').onclick = () => $('reset-dialog').showModal(); $('cancel-reset').onclick = () => $('reset-dialog').close(); $('accept-reset').onclick = () => { sessions[sessionKey()] = newSession(); $('reset-dialog').close(); loadScope() };
function updateTheme() { const dark = document.documentElement.dataset.theme === 'dark'; $('theme').textContent = dark ? '☀ Chế độ sáng' : '☾ Chế độ tối'; $('theme').setAttribute('aria-pressed', String(dark)) }
$('theme').onclick = () => { document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; try { localStorage.setItem('xstk-theme', document.documentElement.dataset.theme) } catch { } updateTheme() };
setup(); updateTheme(); setInterval(() => { if (running) { tick(); save() } }, 1000); window.addEventListener('pagehide', () => { tick(); save() });
