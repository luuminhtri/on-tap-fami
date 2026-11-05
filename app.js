'use strict';
const $=id=>document.getElementById(id), KEY='xstk-study-v1';
let saved={};try{saved=JSON.parse(localStorage.getItem(KEY))||{}}catch{}
let scope=String(saved.scope||'all'), sessions=saved.sessions||{};
if(!['all','1','2','3','4'].includes(scope))scope='all';
let questions=[],session,lastTick=Date.now();
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
for(const c of CHAPTERS){const o=document.createElement('option');o.value=c.number;o.textContent=`Chương ${c.number} · ${c.title} (${c.questions.length} câu)`;$('chapter').append(o)}
function save(){try{localStorage.setItem(KEY,JSON.stringify({scope,sessions}))}catch{$('save-note').textContent='Không thể lưu tiến độ trên trình duyệt này'}}
function loadScope(){questions=CHAPTERS.filter(c=>scope==='all'||String(c.number)===scope).flatMap(c=>c.questions.map(q=>({...q,chapter:c.number,chapterTitle:c.title})));session=sessions[scope]||{index:0,answers:{},elapsed:0,paused:false};sessions[scope]=session;session.index=Math.max(0,Math.min(questions.length-1,session.index||0));lastTick=Date.now();$('chapter').value=scope;render();updateTimer();save()}
function isCorrect(q,selected){return q.answers.length===selected.length&&q.answers.every(id=>selected.includes(id))}
function answer(q){return session.answers[q.id]||{selected:[],confirmed:false}}
function render(){const q=questions[session.index],a=answer(q),multi=q.type==='multi'||q.answers.length>1;
$('question').innerHTML=`<div class="question-head"><div class="question-meta"><span class="question-number">Câu ${session.index+1} <span style="color:#99a49b;font-weight:400">/ ${questions.length}</span></span><span class="badge ${multi?'multi':''}">${multi?'▢ Chọn nhiều đáp án':'◯ Chọn 1 đáp án'}</span></div><div class="chapter-title">CHƯƠNG ${q.chapter} · ${esc(q.chapterTitle)}</div><div class="question-text" id="question-text">${esc(q.text)}</div></div><div class="options" role="group" aria-labelledby="question-text">${q.options.map((o,i)=>{const selected=a.selected.includes(o.id),correct=a.confirmed&&q.answers.includes(o.id),wrong=a.confirmed&&selected&&!correct;return `<label class="option ${correct?'correct':wrong?'incorrect':selected?'selected':''}"><input type="${multi?'checkbox':'radio'}" name="answer" value="${esc(o.id)}" ${selected?'checked':''} ${a.confirmed?'disabled':''}><span class="letter">${String.fromCharCode(65+i)}.</span><span class="content">${esc(o.text)}</span>${correct?'<span class="mark">✓ Đáp án đúng</span>':wrong?'<span class="mark">✕ Bạn chọn</span>':''}</label>`}).join('')}</div><div class="result ${a.confirmed?(isCorrect(q,a.selected)?'good':'bad'):''}" role="status">${a.confirmed?(isCorrect(q,a.selected)?'✓ Chính xác! Bạn đã chọn đầy đủ đáp án đúng.':'Chưa chính xác. Tất cả đáp án đúng đã được tô xanh lá cây.'):(multi?'Chọn tất cả đáp án bạn cho là đúng, rồi bấm xác nhận.':'Chọn một đáp án, rồi bấm xác nhận để kiểm tra.')}</div>`;
if(window.renderMathInElement)renderMathInElement($('question'),{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false},{left:'\\(',right:'\\)',display:false},{left:'\\[',right:'\\]',display:true}],throwOnError:false,trust:false});
$('question').querySelectorAll('input').forEach(input=>input.addEventListener('change',()=>{let selected=multi?[...$('question').querySelectorAll('input:checked')].map(el=>el.value):[input.value];session.answers[q.id]={selected,confirmed:false};save();$('question').querySelectorAll('.option').forEach(el=>el.classList.toggle('selected',el.querySelector('input').checked));$('confirm').disabled=!selected.length}));
$('confirm').disabled=a.confirmed||!a.selected.length;$('confirm').textContent=a.confirmed?'Đã xác nhận ✓':'Xác nhận đáp án';$('prev').disabled=session.index===0;$('next').disabled=session.index===questions.length-1;
const done=questions.filter(q=>answer(q).confirmed),right=done.filter(q=>isCorrect(q,answer(q).selected)).length,pct=Math.round(done.length/questions.length*100);
$('done').textContent=`${done.length}/${questions.length}`;$('right').textContent=right;$('wrong').textContent=done.length-right;$('percent').textContent=pct+'%';$('progress').style.width=pct+'%';
$('grid').innerHTML=questions.map((q,i)=>`<button class="qnav ${answer(q).confirmed?'done':''} ${i===session.index?'current':''}" ${i===session.index?'aria-current="step"':''} aria-label="Câu ${i+1}, ${answer(q).confirmed?'đã làm':'chưa xác nhận'}" data-index="${i}">${i+1}</button>`).join('');
$('grid').querySelectorAll('button').forEach(b=>b.onclick=()=>go(Number(b.dataset.index)));
$('complete').textContent=done.length===questions.length?`Bạn đã hoàn thành bộ câu hỏi! Đúng ${right}/${questions.length} câu. Có thể chọn lại từng câu để xem đáp án.`:'';
}
function go(index){session.index=index;save();render()}
function tick(){const now=Date.now();if(!session.paused&&questions.some(q=>!answer(q).confirmed))session.elapsed+=Math.max(0,now-lastTick);lastTick=now;updateTimer()}
function updateTimer(){const t=Math.floor(session.elapsed/1000);$('timer').textContent=[Math.floor(t/3600),Math.floor(t/60)%60,t%60].map(n=>String(n).padStart(2,'0')).join(':');$('pause').textContent=session.paused?'▶':'Ⅱ';$('pause').setAttribute('aria-label',session.paused?'Tiếp tục thời gian':'Tạm dừng thời gian');$('pause').title=session.paused?'Tiếp tục thời gian':'Tạm dừng thời gian'}
$('confirm').onclick=()=>{const q=questions[session.index],a=answer(q);if(!a.selected.length||a.confirmed)return;tick();a.confirmed=true;session.answers[q.id]=a;save();render()};
$('prev').onclick=()=>go(Math.max(0,session.index-1));$('next').onclick=()=>go(Math.min(questions.length-1,session.index+1));
$('chapter').onchange=()=>{tick();scope=$('chapter').value;loadScope()};$('pause').onclick=()=>{tick();session.paused=!session.paused;updateTimer();save()};
$('reset').onclick=()=>$('reset-dialog').showModal();$('cancel-reset').onclick=()=>$('reset-dialog').close();$('accept-reset').onclick=()=>{delete sessions[scope];$('reset-dialog').close();loadScope()};
loadScope();setInterval(()=>{tick();save()},1000);window.addEventListener('pagehide',()=>{tick();save()});
