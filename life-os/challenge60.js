/* MONTBLANC 14 — earned-day challenge. Private records remain in the existing vault.
   One actual lesson, one real exercise session, deliberate social practice, practical
   learning, commercial action and one compact journal. No external requests. */
(function(global){
'use strict';
const TRACKS=[
 {id:'focus',name:'Доход · реальное действие',icon:'💼'},
 {id:'english',name:'Английский · полноценный урок',icon:'🗣️'},
 {id:'sport',name:'Спорт · полноценное занятие',icon:'🏃'},
 {id:'presence',name:'Харизма · тренировка в жизни',icon:'✨'},
 {id:'learning',name:'Развитие · применить новое',icon:'🧠'},
 {id:'diary',name:'Дневник · честный итог',icon:'✍️'}
];
const TOPICS=[
 ['Знакомство и семья','I am, I have, I live','Расскажи о себе и задай 5 вопросов'],
 ['Мой день','get up, usually, sometimes','Расскажи о распорядке с примерами'],
 ['Работа','I work with, I can help','Опиши свою работу и пользу'],
 ['Мой район','There is, there are','Объясни, что есть рядом с домом'],
 ['Покупки','How much is it?','Сыграй диалог с продавцом'],
 ['Ресторан','I would like, Could I have','Сделай заказ и уточни стоимость'],
 ['Теннис','I can, I play, I need','Забронируй корт на английском'],
 ['Звонок клиенту','May I speak with...?','Начни деловой разговор'],
 ['Вчерашний день','Yesterday I went, I did','Расскажи 6 событий в прошлом'],
 ['Планы на выходные','I am going to','Расскажи о планах и условиях'],
 ['Путешествие','Where can I find...?','Реши вопрос в аэропорту'],
 ['Письмо клиенту','Thank you for, I suggest','Составь короткое письмо'],
 ['Услуга и её результат','We help businesses','Объясни проблему и решение'],
 ['Переговоры о встрече','Are you available?','Согласуй день и время'],
 ['Возражения','I understand, however','Спокойно ответь на сомнение']
];
const PRESENCE=[
 ['Спокойный голос','Запиши 60 секунд рассказа. Повтори медленнее, с паузами, сравни звучание.'],
 ['Инициатива','Начни два коротких доброжелательных разговора; запомни, как собеседники ответили.'],
 ['Контакт глазами','Потренируй естественный зрительный контакт и открытую позу в живом разговоре, без пристальности.'],
 ['Активное слушание','Задай три открытых вопроса, не перебивай и перескажи одну услышанную мысль.'],
 ['Искренняя улыбка','Перед разговором расслабь лицо; улыбнись естественно и отметь реакцию без ожидания похвалы.'],
 ['История за минуту','Расскажи короткую историю: начало, неожиданный момент, вывод. Запиши видео или аудио.'],
 ['Юмор без сарказма','Придумай две мягкие смешные реплики по обычной ситуации; проверь, понятны ли они.'],
 ['Уверенная просьба','Сформулируй конкретную просьбу без извинений и давления, выслушай ответ.'],
 ['Спокойные паузы','Перед ответом делай паузу 1–2 секунды; говори без спешки и слов-паразитов.'],
 ['Тёплый контакт','Проведи разговор с близким без телефона, проявив интерес, а не советы.'],
 ['Собственное мнение','Выскажи точку зрения в 2–3 предложениях, сохраняя уважение к другой позиции.'],
 ['Комплимент по делу','Отметь конкретное хорошее действие другого человека, без неискренней лести.'],
 ['Общение с новым человеком','Найди уместный повод познакомиться без навязывания; после — запиши ощущения.'],
 ['Вопросы и уточнения','Сформулируй два уточняющих вопроса вместо поспешного ответа.'],
 ['Обратная связь','Спроси доверенного человека о ясности голоса, улыбке или умении слушать.']
];
const WORKOUT=['Силовая тренировка по самочувствию','Бег или другая аэробная тренировка','Теннис или другой игровой спорт','Силовая или круговая тренировка','Кардио, велосипед или плавание','Теннис, зал или любимый вид спорта','День восстановления: мягкая мобильность и растяжка без боли'];
const KNOWLEDGE=['Переговоры и вопросы клиенту','Как проверять спрос до создания продукта','Как работает воронка продаж','Контроль внимания и привычек','Финансовая грамотность: выручка и прибыль','Критическое мышление и проверка источников','Повторение и применение знаний'];
const PHASES=[
 ['Основа','Построить ритм и измерить исходную точку.'],
 ['Действие','От подготовки — к реальным разговорам и занятиям.'],
 ['Практика','Закреплять речь, физическую активность и выход к клиентам.'],
 ['Результаты','Повторять то, что работает; убирать шум.'],
 ['Автономность','Создать свой устойчивый маршрут после вызова.']
];
const numeric=v=>{const n=Number(v);return Number.isFinite(n)?n:0};
function create(ctx){
 const S=()=>ctx.state(),safe=ctx.e,today=ctx.today,plus=ctx.plusDays,delta=ctx.deltaDays,ru=ctx.ruDate;
 const pget=()=>S().profile?.montblanc60;
 const get=()=>{const c=pget()?.challenge;if(!c||c.version!==2||!Array.isArray(c.days))return null;return c};
 const has=()=>!!get();
 const entry=(i,c=get())=>c?.days?.[i]||{};
 const complete=(i,c=get())=>TRACKS.every(t=>!!entry(i,c).proofs?.[t.id]);
 const frontier=(c=get())=>{if(!c)return 0;let i=0;while(i<60&&complete(i,c))i++;return i};
 const completedOn=(i,c=get())=>entry(i,c)?.finishedOn||'';
 const milestones=[[7,'Первый ритм'],[14,'Две недели'],[21,'Новый навык'],[30,'Экватор'],[45,'Проверка силы'],[60,'Вершина']];
 const ready=(c=get())=>!!c&&frontier(c)<60&&(frontier(c)===0||completedOn(frontier(c)-1,c)<today());
 const viewIndex=(c=get())=>{
  if(!c)return 0;
  const edge=frontier(c),requested=S().mission60DayIndex;
  return Number.isInteger(requested)&&requested>=0&&requested<60&&requested<=edge?requested:Math.min(59,edge);
 };
 const canView=i=>!!get()&&Number.isInteger(i)&&i>=0&&i<60&&i<=frontier()&&(i<frontier()||ready());
 const phase=i=>Math.floor(i/12);
 const minutes=(id,i)=>id==='english'?90:id==='focus'?45+phase(i)*5:id==='sport'?(i%7===6?20:40):id==='presence'?15+phase(i)*2:id==='learning'?20:id==='diary'?5:0;
 const minimum=(id,i)=>id==='english'?60:id==='sport'?(i%7===6?20:30):id==='focus'?40:id==='presence'?12:id==='learning'?15:1;
 const lesson=i=>{
  const topic=TOPICS[i%TOPICS.length],stage=phase(i);
  const grammar=['be, have, present simple, вопросы','Present Simple vs Continuous, can/could','Past Simple, рассказ и связки','Future forms, сравнения и аргументация','Уточнения, обсуждение условий и переговоры'][stage];
  return {topic:topic[0],phrase:topic[1],task:topic[2],grammar,
   review:i===0?'Скажи вслух пять известных фраз о себе.':'Повтори 10 фраз из прошлого занятия без подсказки.'};
 };
 const work=i=>{
  const starter=ctx.legacy.INCOME_STEPS[i]||'Сделай один коммерческий шаг с проверяемым результатом.';
  const stage=phase(i),outcome=stage===0?'Сохрани конкретный артефакт: список, текст, проверку спроса или первое обращение.':stage===1?'Свяжись с реальным потенциальным клиентом, подготовь предложение или проведи разговор.':stage===2?'Проведи следующий контакт с клиентом, разбери возражение или заверши пилот.':stage===3?'Улучши повторяемую продажу, цену, процесс или выполненное обещание по фактам.':'Закрепи результат: повтори работающие действия и составь следующий финансовый шаг.';
  return starter+' '+outcome;
 };
 const drill=i=>{
  const d=PRESENCE[i%PRESENCE.length],level=phase(i);
  return {title:d[0],instruction:d[1],stretch:level===0?'В конце запиши, что получилось и что было трудно.':level===1?'Повтори практику два раза или с двумя собеседниками.':level===2?'Сделай это в менее привычной, но безопасной ситуации.':level===3?'Получай обратную связь и исправляй одну конкретную деталь.':'Выполни спокойно, без заученного образа, и сравни с началом программы.'};
 };
 const tasks=i=>{
  const en=lesson(i),pres=drill(i);
  return [
   {id:'focus',title:'Доход: конкретный коммерческий результат',minutes:minutes('focus',i),minimum:minimum('focus',i),detail:work(i),proof:'Что ты создал, отправил, проверил или с кем поговорил? Укажи результат.'},
   {id:'english',title:'Английский: урок '+(i+1)+' / 60',minutes:90,minimum:60,detail:'Тема: '+en.topic+'. Грамматика: '+en.grammar+'. Цель: '+en.task+'. Один полноценный урок, а не пара фраз.',proof:'Какой урок прошёл? Что смог сказать? Какая ошибка исправлена?',en},
   {id:'sport',title:i%7===6?'Восстановительная тренировка':'Спорт: полноценная сессия',minutes:minutes('sport',i),minimum:minimum('sport',i),detail:WORKOUT[i%7]+'. Выбирай подходящий вид нагрузки. Не выполняй интенсивные тренировки через боль или болезнь.',proof:'Вид активности, длительность, самочувствие после.'},
   {id:'presence',title:'Харизма: '+pres.title,minutes:minutes('presence',i),minimum:minimum('presence',i),detail:pres.instruction+' '+pres.stretch,proof:'Что практиковал в реальности, как прошёл разговор или запись, какой сделал вывод?'},
   {id:'learning',title:'Развитие: знание с применением',minutes:20,minimum:15,detail:'Изучи «'+KNOWLEDGE[i%KNOWLEDGE.length]+'». 15–20 минут разбора, затем объясни одну идею своими словами и где применишь её завтра.',proof:'Один полезный вывод и его практическое применение.'},
   {id:'diary',title:'Дневник: 5 минут честного итога',minutes:5,minimum:1,detail:'Одним рассказом опиши чувства и мысли, результат дня и следующий шаг. Отметь энергию и уверенность.',proof:'Заполни короткий дневник.'}
  ];
 };
 const earned=()=>get()?frontier():0;
 const recordDay=async(c,i,next)=>{
  const days=c.days.slice();
  const prev=days[i]||{},merged={...prev,...next,proofs:{...(prev.proofs||{}),...(next.proofs||{})}};
  if(TRACKS.every(t=>!!merged.proofs[t.id])&&!merged.finishedOn)merged.finishedOn=today();
  days[i]=merged;
  const updated={...c,days};
  await ctx.saveProfile({...S().profile,montblanc60:{...pget(),challenge:updated}});
  return updated;
 };
 async function start(){
  if(has())return;
  if(!S().local&&!S().demo)throw Error('Вызов доступен после входа в личный режим.');
  await ctx.saveProfile({...S().profile,montblanc60:{...(pget()||{version:1,started:today(),pace:'steady',days:{}}),challenge:{version:2,started:today(),days:[]}}});
  S().mission60DayIndex=null;
 }
 function selectedAction(){
  const x=S().c60Proof;
  return x&&Number.isInteger(x.day)&&x.day===frontier()&&ready()?tasks(x.day).find(t=>t.id===x.id&&t.id!=='diary'):null;
 }
 async function recordProof(form){
  const c=get(),i=frontier(c),id=String(form.track||''),task=tasks(i).find(x=>x.id===id&&id!=='diary');
  if(!c||!ready(c)||form.day!==String(i)||!task)throw Error('Этот этап ещё не открыт.');
  const note=String(form.evidence||'').trim(),mins=Number(form.minutes);
  if(note.length<20)throw Error('Добавь конкретный результат или вывод (не менее 20 символов).');
  if(!Number.isFinite(mins)||mins<task.minimum||mins>480)throw Error('Для этого задания нужна реальная практика от '+task.minimum+' минут.');
  let type='';
  if(id==='sport'){
   type=String(form.workout_type||'');
   if(!['зал','бег','теннис','домашняя тренировка','плавание/велосипед','другой спорт','восстановление'].includes(type))throw Error('Укажи вид тренировки.');
   if(i%7===6&&type!=='восстановление')throw Error('Каждый седьмой день — восстановительная практика без интенсивного спорта.');
   if(i%7!==6&&type==='восстановление')throw Error('Для этого дня выбери тренировку; восстановление предусмотрено на седьмой день.');
  }
  // Mirror actual session time into existing daily logs without counting it twice.
  const logKey={focus:'focus_min',english:'english_min',sport:'exercise_min',presence:'m60_presence_min',learning:'learning_min'}[id];
  if(logKey){
   const oldLog=S().data.daily_logs.find(x=>x.log_date===today())||{};
   await ctx.saveRecord('daily_logs',{...oldLog,log_date:today(),[logKey]:Math.max(numeric(oldLog[logKey]),mins)});
  }
  await recordDay(c,i,{date:entry(i,c).date||today(),proofs:{[id]:{at:new Date().toISOString(),date:today(),minutes:mins,note:note.slice(0,2000),type}}});
 }
 async function completeDiary(date){
  const c=get();if(!c||!ready(c)||date!==today())return;
  const i=frontier(c);if(entry(i,c).proofs?.diary)return;
  const log=S().data.daily_logs.find(x=>x.log_date===date);
  if(!log?.reflection_done||!String(log.thoughts||'').trim()||!String(log.win_of_day||'').trim())return;
  await recordDay(c,i,{date:entry(i,c).date||today(),proofs:{diary:{at:new Date().toISOString(),date:today(),minutes:5,note:'Итог дня записан в дневнике'}}});
 }
 function currentStreak(c=get()){
  if(!c)return 0;let count=0,prev='';
  for(let i=0;i<frontier(c);i++){
   const date=completedOn(i,c);
   if(i===0){count=1;prev=date;continue}
   count=date===plus(prev,1)?count+1:1;prev=date;
  }
  if(!prev||delta(prev,today())>1)return 0;
  return count;
 }
 function recordCounts(c=get()){
  const arr=[];
  for(let i=0;i<frontier(c);i++)arr.push(...TRACKS.map(t=>({id:t.id,...entry(i,c).proofs[t.id]})));
  const sum=id=>arr.filter(x=>x.id===id).reduce((n,x)=>n+numeric(x.minutes),0);
  return {days:frontier(c),english:sum('english'),sport:sum('sport'),focus:sum('focus'),presence:sum('presence'),learning:sum('learning'),sportTypes:Object.fromEntries([...new Set(arr.filter(x=>x.id==='sport').map(x=>x.type))].map(t=>[t,arr.filter(x=>x.id==='sport'&&x.type===t).length]))};
 }
 function dailyLessonPrompt(i){
  const x=lesson(i);
  return 'Ты мой интерактивный преподаватель английского. Проведи со мной полноценный урок №'+(i+1)+' программы MONTBLANC (целевой формат 90 минут; минимум 60 минут активной практики). Мой текущий уровень примерно A1, цель — устойчивый B1, без обещания срока. Тема: '+x.topic+'. Полезные конструкции: '+x.phrase+'. Грамматика: '+x.grammar+'. Результат: '+x.task+'. Структура: 10 минут повторение и диагностика, 15 минут новые выражения, 20 минут грамматика с 8 упражнениями, 15 минут чтение/аудирование с вопросами, 20 минут диалог и разговор, 10 минут исправление ошибок и повторение. '+x.review+' Задавай по одному вопросу, жди ответ, исправляй ошибки понятно на русском и проверяй понимание. Не выдавай сразу весь урок текстом. Составь в конце 5 фраз на повторение завтра.';
 }
 const top=()=>{const c=get(),n=frontier(c);return {c,n,i:viewIndex(c),waiting:!ready(c)&&n<60,finished:n===60}};
 function cell(i,c,n){
  const done=i<n,open=i===n&&ready(c),locked=i>n||(!open&&!done);
  return '<button class="c60-day '+(done?'done':open?'open':'locked')+'" data-action="c60-day" data-index="'+i+'" '+(locked?'disabled':'')+' aria-label="'+(locked?'Закрытый ':done?'Завершённый ':'Текущий ')+'день '+(i+1)+'"><strong>'+(i+1)+'</strong><small>'+(done?'✓':open?'●':'🔒')+'</small></button>';
 }
 function proofDialog(){
  const task=selectedAction();if(!task)return '';
  const x=S().c60Proof,i=x.day;
  const extra=task.id==='sport'?'<label>Тип занятия<select name="workout_type" required><option value="">Выбери вид спорта</option>'+['зал','бег','теннис','домашняя тренировка','плавание/велосипед','другой спорт','восстановление'].map(t=>'<option value="'+t+'">'+t+'</option>').join('')+'</select></label>':'';
  return '<div class="c60-overlay" role="presentation"><form data-form="c60-proof" class="c60-modal" role="dialog" aria-modal="true" aria-label="Подтверждение практики"><input type="hidden" name="day" value="'+i+'"><input type="hidden" name="track" value="'+task.id+'"><div class="c60-modal-header"><h2>'+safe(task.title)+'</h2><button type="button" data-action="c60-proof-close" aria-label="Закрыть">✕</button></div><p>'+safe(task.detail)+'</p><p class="c60-proof-rule">Для зачёта: от '+task.minimum+' минут реальной практики и конкретный результат.</p>'+extra+'<label>Сколько минут реально занимался?<input name="minutes" type="number" min="'+task.minimum+'" max="480" placeholder="Например, '+task.minutes+'" required inputmode="numeric"/></label><label>Факт и твой вывод<textarea name="evidence" rows="4" minlength="20" maxlength="2000" placeholder="'+safe(task.proof)+'" required></textarea></label><button class="m60-primary" type="submit">Подтвердить выполненную практику</button><button type="button" data-action="c60-proof-close" class="c60-secondary">Вернуться без отметки</button></form></div>';
 }
 function itemCard(task,i,c,n){
  const saved=entry(i,c).proofs?.[task.id],past=i<n,available=i===n&&ready(c);
  const area=TRACKS.find(t=>t.id===task.id);
  return '<article class="c60-practice '+(saved?'done':'')+'"><div class="c60-practice-head"><span class="c60-emoji">'+area.icon+'</span><div><small>'+task.minutes+' мин · '+(task.id==='english'?'цель 90 мин':'практика')+'</small><h3>'+safe(task.title)+'</h3></div><span class="c60-state">'+(saved?'✓':past?'—':'○')+'</span></div><p>'+safe(task.detail)+'</p>'+
   (task.en?'<details class="c60-lesson"><summary>Программа полноценного урока · 90 минут</summary><ol><li>10 мин — повторение предыдущего материала</li><li>15 мин — слова и полезные фразы по теме</li><li>20 мин — грамматика и упражнения</li><li>15 мин — чтение, понимание на слух и ответы</li><li>20 мин — живой диалог и речь</li><li>10 мин — разбор ошибок и повторение</li></ol><p>Полезная конструкция: '+safe(task.en.phrase)+'. '+safe(task.en.review)+'</p><button type="button" data-action="c60-lesson-copy" data-index="'+i+'" class="c60-secondary">Скопировать полноценный урок для ChatGPT</button></details>':'')+
   (saved?'<div class="c60-evidence"><strong>✓ Засчитано · '+saved.minutes+' мин</strong><p>'+safe(saved.note||'Практика подтверждена')+'</p></div>':available?(task.id==='diary'?'<button data-page="reflection" class="c60-action">Заполнить итог дня →</button>':'<button data-action="c60-proof-open" data-index="'+i+'" data-id="'+task.id+'" class="c60-action">Выполнено — записать результат →</button>'):'')+
   '</article>';
 }
 function program(){
  const {c,n,waiting,finished}=top();if(!c)return '<div class="m60-page c60-root"><div class="m60-title"><span>MONTBLANC · CHALLENGE</span><h1>60 дней полной прокачки</h1><p>Шесть обязательных действий ежедневно. Следующий день открывается только после завершения всех пунктов и наступления следующего дня.</p></div>'+onboard()+'</div>';
  const i=viewIndex(c),open=i===n&&!waiting,done=i<n,ts=tasks(i),saved=entry(i,c).proofs||{},numDone=TRACKS.filter(t=>saved[t.id]).length,total=ts.reduce((sum,t)=>sum+t.minutes,0);
  return '<div class="m60-page c60-root"><div class="m60-title"><span>🏔️ CHALLENGE · 60 ЗАСЛУЖЕННЫХ ДНЕЙ</span><h1>'+ (finished?'Вершина достигнута':waiting?'День завершён': 'День '+(n+1)+' / 60')+'</h1><p>Задания раскрываются последовательно. Нет зачёта за галочку без практики. Пропуск не стирает проделанную работу.</p></div>'+
    '<section class="m60-card c60-hero"><div class="c60-hero-row"><div><small>ТВОЙ МАРШРУТ</small><h2>'+n+' <span>/ 60 дней</span></h2><p>Серия подряд: '+currentStreak(c)+' · выполнено '+(n*6)+' основных практик</p></div><div class="c60-hero-num">'+Math.round(n/60*100)+'%</div></div><div class="m60-track"><i style="width:'+(n/60*100)+'%"></i></div>'+(waiting?'<p class="c60-status-message">Все шесть заданий выполнены. Следующий день станет доступен завтра. Сегодня можно отдохнуть, выполненное не пропадёт.</p>':'')+(finished?'<p class="c60-status-message">Все 60 дней завершены! Открой итоговый разбор роста по своим записям.</p><button data-page="progress" class="m60-primary">Мой итог за 60 дней →</button>':'')+'</section>'+
    '<section class="m60-card c60-daycard"><div class="c60-day-title"><div><small>ЭТАП '+(phase(i)+1)+' · '+PHASES[phase(i)][0]+'</small><h2>День '+(i+1)+' · '+(done?'завершён':open?'в работе':'пока закрыт')+'</h2></div><strong>'+numDone+' / 6</strong></div><p>'+PHASES[phase(i)][1]+' · план ≈ '+Math.floor(total/60)+' ч '+(total%60)+' мин</p><div class="c60-checks">'+TRACKS.map(t=>'<span class="'+(saved[t.id]?'passed':'')+'">'+(saved[t.id]?'✓':'○')+' '+t.name.split(' · ')[0]+'</span>').join('')+'</div>'+((open||done)?ts.map(t=>itemCard(t,i,c,n)).join(''):'<div class="c60-status-message">Следующий день ещё закрыт.</div>')+'</section>'+
    '<section class="m60-card c60-milestones"><h2>Контрольные вершины</h2><div class="c60-milestone-grid">'+milestones.map(([day,label])=>'<div class="'+(n>=day?'unlocked':'')+'"><strong>'+(n>=day?'✓ ': '🔒 ')+day+'</strong><small>'+safe(label)+'</small></div>').join('')+'</div><p class="m60-hint">Контрольные вершины открываются за завершённые дни, без повторного начисления очков за те же действия.</p></section>'+
    '<section class="m60-card"><div class="c60-day-title"><div><small>ТВОЯ ЭКСПЕДИЦИЯ</small><h2>Карта 60 дней</h2></div><button data-action="c60-day" data-index="'+(waiting?Math.max(0,n-1):Math.min(n,59))+'" class="c60-secondary">'+(waiting?'Последний завершённый':'Текущий день')+'</button></div><div class="c60-calendar">'+Array.from({length:60},(_,j)=>cell(j,c,n)).join('')+'</div><p class="m60-hint">Закрытые дни не открываются досрочно; прошлые отчёты доступны для просмотра. Выполнение невозможно задним числом.</p></section>'+proofDialog()+'</div>';
 }
 function onboard(){
  return '<section class="m60-card c60-onboard"><h2>Не просто привычки. Настоящие занятия.</h2><p>Один полноценный урок английского (цель 90 минут), тренировка (или восстановительная практика раз в неделю), коммерческий блок, работа над харизмой, прикладное обучение и короткий дневник. План — около 3,5–4 часов в обычный день.</p><p>Каждый день нужно подтвердить шесть практик. Следующий откроется завтра, если все выполнены. День отдыха или болезни можно пропустить без потери уже завершённых этапов, но серия подряд прервётся.</p><p>Прежние записи и старый маршрут останутся в защищённом хранилище. Новый вызов начнётся с дня 1.</p><button class="m60-primary" data-action="c60-start">Начать новый 60-дневный вызов →</button></section>';
 }
 function home(){
  const {c,n,waiting,finished}=top(),task=tasks(Math.min(59,n)),remaining=finished?0:6-TRACKS.filter(t=>entry(n,c).proofs?.[t.id]).length;
  return '<div class="m60-page c60-root"><div class="m60-title"><span>'+safe(ru(today()))+' · MONTBLANC</span><h1>Сегодня</h1><p>Не идеальный образ. Шесть реальных действий, которые двигают тебя к вершине.</p></div><section class="m60-card c60-hero"><small>60-ДНЕВНЫЙ ВЫЗОВ</small><h2>'+(finished?'60 / 60 · завершено':waiting?'Сегодня всё сделано':'День '+(n+1)+' из 60')+'</h2><p>'+n+' завершённых дней · серия '+currentStreak(c)+' · '+(waiting?'Новый этап завтра':finished?'Пора подвести итоги':remaining+' пунктов осталось')+'</p><div class="m60-track"><i style="width:'+(n/60*100)+'%"></i></div><button class="m60-primary" data-page="'+(finished?'progress':'mission60')+'">'+(finished?'Посмотреть результаты →':waiting?'Посмотреть выполненный день →':'Открыть мои задания →')+'</button></section>'+
   (!finished&&!waiting?'<section class="m60-card"><h2>Сегодняшний маршрут</h2><div class="c60-mini-list">'+task.map(t=>'<button data-page="mission60"><span>'+TRACKS.find(a=>a.id===t.id).icon+'</span><b>'+safe(t.title)+'</b><small>'+t.minutes+' мин</small><span>'+ (entry(n,c).proofs?.[t.id]?'✓':'›')+'</span></button>').join('')+'</div></section>':'')+
   '<section class="m60-card"><h2>Осознанное развитие</h2><p>Главная цель — не количество нажатий, а устойчивые навыки, живые разговоры, тренировки, коммерческие действия и честная оценка изменений.</p><div class="m60-summary"><div><b>'+recordCounts(c).english/60+' ч</b><small>Уроки английского</small></div><div><b>'+recordCounts(c).sport/60+' ч</b><small>Спорт</small></div><div><b>'+recordCounts(c).focus/60+' ч</b><small>Работа к доходу</small></div></div><button data-page="progress" class="m60-textbutton">Аналитика изменений →</button></section>'+
   '<section class="m60-card"><h2>Важное вне вызова</h2><p>Семья, отдых, питание и путешествия не превращены в обязательные галочки. Записывай важное в дневник, а финансовые поступления — в отдельный учёт.</p><button data-page="finance" class="m60-textbutton">Финансы →</button><button data-page="reflection" class="m60-textbutton">Короткий дневник →</button></section></div>';
 }
 function diary(){
  const date=S().reflectionDate||today(),r=S().data.daily_logs.find(x=>x.log_date===date)||{},all=S().data.daily_logs.filter(x=>x.reflection_done).length;
  return '<div class="m60-page c60-root"><div class="m60-title"><span>ЛИЧНЫЙ ДНЕВНИК · '+all+' ЗАПИСЕЙ</span><h1>Мой день</h1><p>Без десятков форм. Пиши своими словами, как прошёл день и что почувствовал.</p></div>'+
   '<div class="m60-diarydate"><button data-action="reflection-date" data-value="'+plus(date,-1)+'">‹</button><div><b>'+safe(ru(date))+'</b><small>'+(r.reflection_done?'✓ Итог сохранён':'Сегодняшняя запись')+'</small></div><button data-action="reflection-date" data-value="'+plus(date,1)+'" '+(date>=today()?'disabled':'')+'>›</button><button data-action="reflection-date" data-value="'+today()+'">Сегодня</button></div>'+
   '<form data-form="mission-journal"><input type="hidden" name="log_date" value="'+date+'"><section class="m60-card c60-journal"><label>Как прошёл день? Мысли, ощущения, что было важным<textarea name="thoughts" rows="7" minlength="10" maxlength="2500" required placeholder="Сегодня я чувствовал… Что меня порадовало, удивило, напрягло? Что изменилось в моём отношении к себе?">'+safe(r.thoughts||'')+'</textarea></label><label>Один конкретный результат дня<input name="win_of_day" maxlength="500" required minlength="8" value="'+safe(r.win_of_day||'')+'" placeholder="Например: прошёл урок и написал двум клиентам"></label><div class="c60-diary-selects"><label>Энергия 1–10<select name="evening_energy"><option value="">Не оценивать</option>'+Array.from({length:10},(_,i)=>'<option value="'+(i+1)+'" '+(Number(r.evening_energy)===(i+1)?'selected':'')+'>'+(i+1)+'</option>').join('')+'</select></label><label>Уверенность 1–10<select name="m60_confidence"><option value="">Не оценивать</option>'+Array.from({length:10},(_,i)=>'<option value="'+(i+1)+'" '+(Number(r.m60_confidence)===(i+1)?'selected':'')+'>'+(i+1)+'</option>').join('')+'</select></label></div><label>Что важно сделать или изменить завтра?<input name="tomorrow_one" maxlength="450" value="'+safe(r.tomorrow_one||'')+'" placeholder="Один следующий шаг"></label></section><button class="m60-primary m60-submit" type="submit">Сохранить итог дня</button><p class="m60-hint">'+(S().demo?'Демо: записи не сохраняются после закрытия вкладки.':S().local?'Черновик шифруется локально; итог засчитывается после нажатия «Сохранить».':'Итог засчитывается после подтверждения сохранения.')+'</p></form>'+
   '<div class="m60-linklist"><button data-page="feed"><span>📖</span><div><b>Моя история</b><small>Все прошлые записи без потери подробных полей</small></div><em>›</em></button><button data-page="progress"><span>📊</span><div><b>Что изменилось</b><small>Тренды и итоги вызова</small></div><em>›</em></button></div></div>';
 }
 function analysis(){
  const c=get(),metrics=recordCounts(c),days=frontier(c),completionDates=Array.from({length:days},(_,i)=>entry(i,c).date);
  const logs=S().data.daily_logs.filter(x=>completionDates.includes(x.log_date)).sort((a,b)=>String(a.log_date).localeCompare(String(b.log_date)));
  const recent=logs.slice(-7),baseline=logs.slice(0,7);
  const avg=(arr,key)=>{const z=arr.map(x=>Number(x[key])).filter(n=>n>=1&&n<=10);return z.length?{value:Math.round(z.reduce((a,b)=>a+b,0)/z.length*10)/10,n:z.length}:null};
  const compare=(key)=>{const a=avg(baseline,key),b=avg(recent,key);return {a,b,diff:a&&b&&a.n>=3&&b.n>=3&&days>=14?Math.round(10*(b.value-a.value))/10:null}};
  const finance=ctx.monthIncome(),baseIncome=numeric(S().profile?.income_baseline);
  const sales=logs.reduce((n,x)=>n+numeric(x.sales_contacts),0),replies=logs.reduce((n,x)=>n+numeric(x.sales_replies),0),payments=logs.reduce((n,x)=>n+numeric(x.sales_paid),0);
  return {days,metrics,energy:compare('evening_energy'),confidence:compare('m60_confidence'),baseIncome,finance,sales,replies,payments,logs};
 }
 function reportPrompt(includeNotes=false){
  const a=analysis(),c=get();
  const data={completed_days:a.days,total_required_days:60,streak:currentStreak(c),minutes_by_area:a.metrics,energy_week1_vs_latest:a.energy,confidence_week1_vs_latest:a.confidence,starting_income_recorded:a.baseIncome,current_month_income:a.finance,customer_contacts:a.sales,replies:a.replies,paid_events_by_diary:a.payments,remarks:'Self-reported evidence, not verified independently. Incomplete days not counted.'};
  if(includeNotes){
   data.journal=S().data.daily_logs.filter(x=>x.log_date>=c.started&&x.log_date<=today()&&x.reflection_done).sort((a,b)=>String(a.log_date).localeCompare(String(b.log_date))).map(x=>({date:x.log_date,thoughts:String(x.thoughts||'').slice(0,1500),win:String(x.win_of_day||'').slice(0,500)}));
   data.practice_evidence=Array.from({length:a.days},(_,i)=>({day:i+1,proofs:Object.fromEntries(TRACKS.filter(t=>t.id!=='diary').map(t=>[t.id,entry(i,c).proofs?.[t.id]?.note||'']))}));
  }
  return 'Подготовь развернутый, аккуратный разбор моего прогресса за 60-дневный вызов MONTBLANC. Данные — самоотчёты, не считай их независимым подтверждением. Сравни исходный и последний доступный период, отдели действия от результатов, укажи пробелы и неопределённость, оцени отдельно английский, спорт, коммуникацию, коммерческие результаты, дисциплину, самочувствие. Баллы 0–10 обоснуй только доступными фактами, не придумывай рост уровня английского. Сформулируй 5 доказанных изменений, 5 остающихся препятствий и персональный план на следующие 30 дней. Не давай медицинских диагнозов.\n'+JSON.stringify(data,null,2);
 }
 function progress(){
  const c=get(),a=analysis(),days=a.days;
  const fmt=x=>x.diff===null?'Мало записей для сравнения':(x.diff>0?'+':'')+x.diff+' / 10';
  const chart=x=>'<div><strong>'+(x.b?x.b.value+'/10':'—')+'</strong><small>'+fmt(x)+'</small></div>';
  return '<div class="m60-page c60-root"><div class="m60-title"><span>ТВОЙ РОСТ · ПО ДЕЛАМ И ЗАПИСЯМ</span><h1>Результаты вызова</h1><p>Отличаем выполненную практику от настоящих изменений. Глубокий вывод возможен после накопления наблюдений.</p></div>'+
  '<section class="m60-card c60-hero"><small>ПУТЬ К ВЕРШИНЕ</small><h2>'+days+' из 60 дней</h2><div class="m60-track"><i style="width:'+(days/60*100)+'%"></i></div><div class="c60-score-grid"><div><b>'+Math.round(a.metrics.english/60*10)/10+' ч</b><small>Английский</small></div><div><b>'+Math.round(a.metrics.sport/60*10)/10+' ч</b><small>Спорт</small></div><div><b>'+Math.round(a.metrics.focus/60*10)/10+' ч</b><small>Дела к доходу</small></div><div><b>'+Math.round(a.metrics.presence/60*10)/10+' ч</b><small>Харизма</small></div><div><b>'+Math.round(a.metrics.learning/60*10)/10+' ч</b><small>Развитие</small></div><div><b>'+currentStreak(c)+'</b><small>Серия дней</small></div></div></section>'+
  '<section class="m60-card"><h2>Изменения по дневнику</h2><p>Сравнение первых семи и последних семи сохранённых итогов. Требуется не менее трёх оценок в каждом периоде и 14 завершённых дней.</p><div class="c60-trends"><div><span>Энергия</span>'+chart(a.energy)+'</div><div><span>Уверенность</span>'+chart(a.confidence)+'</div></div><p class="m60-hint">Самооценки отражают ощущения, а не медицинский или психологический диагноз.</p></section>'+
  '<section class="m60-card"><h2>Доход: действия и результаты отдельно</h2><div class="c60-score-grid"><div><b>'+a.sales+'</b><small>Обращений</small></div><div><b>'+a.replies+'</b><small>Ответов</small></div><div><b>'+a.payments+'</b><small>Оплат в дневнике</small></div><div><b>'+ctx.money(a.finance)+'</b><small>Доход месяца из финансов</small></div></div><p class="m60-hint">Стартовый доход из настроек: '+ctx.money(a.baseIncome)+'. Это разные временные периоды; рост дохода нельзя подтвердить только выполненными заданиями.</p><button data-page="finance" class="m60-textbutton">Открыть учёт доходов →</button></section>'+
  '<section class="m60-card"><h2>'+(days===60?'Большой итог за 60 дней':'Разбор по мере продвижения')+'</h2><p>Локально подсчитываются занятия, отклики и изменения самооценки. Для подробного смыслового анализа можно вручную передать факты в ChatGPT; без твоего действия дневник никуда не отправляется.</p><button data-action="c60-copy-report" data-mode="numbers" class="c60-action">Подготовить анализ без личных записей</button><button data-action="c60-copy-report" data-mode="journal" class="c60-secondary c60-wide">Подготовить полный анализ с текстом дневника</button><p class="m60-hint">Второй вариант включает приватные заметки и подтверждения действий — только после отдельного согласия.</p></section>'+
  '<section class="m60-card"><h2>Твой путь по дням</h2><div class="c60-calendar">'+Array.from({length:60},(_,i)=>cell(i,c,days)).join('')+'</div></section></div>';
 }
 return {TRACKS,PHASES,get,has,frontier,ready,canView,earned,tasks,minimum,minutes,lesson,dailyLessonPrompt,start,recordProof,completeDiary,selectedAction,proofDialog,program,home,diary,progress,analysis,reportPrompt,currentStreak,recordCounts,onboard};
}
global.MONTBLANCCHALLENGE={create};
})(window);
