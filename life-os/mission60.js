/* MONTBLANC 12.0 — 60-day private life-growth module.
   Standalone presentation/logic layer. Existing vault, GH backup, tasks and daily logs
   are owned by app.js, not by this module. No external network requests. */
(function(global){
'use strict';
const AREAS=[
 {id:'focus',name:'Доход и фокус',emoji:'💼',color:'#356dde'},
 {id:'english',name:'Английский',emoji:'🗣️',color:'#9960d9'},
 {id:'sport',name:'Спорт и движение',emoji:'🏃',color:'#f27c4b'},
 {id:'learning',name:'Полезные знания',emoji:'📚',color:'#0f9991'},
 {id:'nutrition',name:'Питание',emoji:'🥗',color:'#34a366'},
 {id:'family',name:'Семья и харизма',emoji:'🤝',color:'#dc6597'},
 {id:'diary',name:'Дневник',emoji:'✍️',color:'#5289c9'}
];
const PHASES=[
 ['Начало пути','От рассеянности — к первому измеримому шагу.'],
 ['Новый ритм','Укрепляем внимание, голос и стабильность.'],
 ['Выход в реальность','Реальные контакты, практика и обратная связь.'],
 ['Фокус и результаты','Выбираем полезное, убираем шум, закрепляем привычки.'],
 ['Новая высота','Подводим итоги и строим следующий маршрут.']
];
const INCOME_STEPS=[
'Запиши реальную точку А: доход, обязательные расходы и долги.',
'Выбери одну B2B-услугу, которую можешь проверить без вложений.',
'Опиши одну проблему клиента, которую реально можешь решить.',
'Составь портрет клиента: должность, отрасль, страна, проблема.',
'Найди пять компаний, которым может быть полезна услуга.',
'Изучи два предложения конкурентов и выпиши слабые стороны.',
'Сформулируй ценность услуги в двух коротких предложениях.',
'Проверь одну гипотезу с реальным человеком, не продавая вслепую.',
'Создай список десяти потенциальных клиентов.',
'Подготовь одно персонализированное сообщение с понятной пользой.',
'Отправь первое обращение реальному потенциальному клиенту.',
'Проверь ответы. Если их нет, запиши факт, а не обвинение себя.',
'Изучи одно частое возражение и подготовь спокойный ответ.',
'Составь простое предложение с понятной ценой и объёмом работ.',
'Отправь предложение или согласуй короткий разговор.',
'Сделай 30 минут сфокусированной работы на одной услуге.',
'Найди ещё пять релевантных компаний без массовой рассылки.',
'Проверь качество своего сообщения на одном живом контакте.',
'Спроси потенциального клиента, какая задача у него болит.',
'Запиши три факта о спросе на твою услугу.',
'Составь мини-план получения первого оплаченного теста.',
'Сократи свой список идей до одной проверяемой гипотезы.',
'Проведи короткий звонок или отправь ценное предложение.',
'Проверь конверсию: обращения, ответы, разговоры, оплаты.',
'Опиши маленький платный пилот на 7 дней.',
'Выбери одного подходящего клиента для пилота.',
'Уточни, какие результаты нужно предоставить клиенту.',
'Отправь конкретное предложение пилота.',
'Сделай один нужный follow-up по предыдущему разговору.',
'Зафиксируй, какие действия в продажах были полезны.',
'Разбери одно «нет»: что можно улучшить, не споря с клиентом?',
'Сверь реальный доход и обещанные платежи — не смешивай их.',
'Проверь, сколько времени занимает выполнение услуги.',
'Рассчитай примерную прибыль после расходов.',
'Составь короткий список реальных повторяемых действий.',
'Заверши одно незакрытое клиентское обещание.',
'Создай одно качественное доказательство своей компетенции.',
'Сделай два персональных обращения за один рабочий блок.',
'Попроси обратную связь у заинтересованного клиента.',
'Сравни результат недели с прошлой по цифрам.',
'Отбрось один неработающий канал или предложение по фактам.',
'Проведи глубокую работу над лучшей гипотезой.',
'Обнови текст предложения по реальным ответам клиентов.',
'Обсуди с клиентом конкретную пользу и условия работы.',
'Подготовь следующий оплачиваемый шаг.',
'Запиши выручку, расходы и денежный остаток.',
'Выдели один главный коммерческий приоритет на неделю.',
'Сделай один реальный шаг к получению оплаты.',
'Сверь фактический доход с годовой финансовой целью.',
'Проверь, не тратишь ли время на проекты без проверки спроса.',
'Назови самую полезную привычку для заработка.',
'Повтори действие, которое действительно принесло ответ.',
'Откажись от одного бесполезного действия.',
'Продумай финансовый резерв и обязательные платежи.',
'Проверь статус своего лучшего коммерческого предложения.',
'Запиши уроки из реальных разговоров с клиентами.',
'Составь список из пяти действий, которые дают результат.',
'Сравни текущие деньги и долг со стартовыми цифрами.',
'Сформулируй один измеримый план на следующие 30 дней.',
'Запланируй завтра один конкретный коммерческий шаг.'
];
const ENGLISH_TOPICS=['О себе и своей семье','Мой обычный день','Работа и клиенты','Город, где я живу','Покупки и цены','Транспорт','Теннис и спорт','Планы на завтра','Еда и ресторан','Деньги и числа','Что было вчера','Мои путешествия','Вежливая просьба','Звонок по телефону','Моя бизнес-идея','Вопросы клиенту','Мой опыт','Договориться о встрече','Услуга и её польза','Объяснить проблему','Сравнить два варианта','Выразить предпочтение','Мои навыки','Что мне удалось сегодня','Короткое письмо','Аргумент «за»','Вывод из ошибки','Почему я учу английский','Планы на год','Мои успехи'];
const LEARNING_TOPICS=['Как формируются привычки','Прокрастинация без самокритики','Один главный приоритет','Активное слушание','Выяснение потребностей клиента','Выручка, прибыль и остаток','Простой домашний бюджет','Быстрая проверка гипотез','Цифровые продажи','Понятное предложение ценности','Как работают отвлечения','Письменная коммуникация','Обратная связь','Основа переговоров','Простой маркетинговый кейс','Сон и восстановление','Безопасная умеренная нагрузка','Повторение и закрепление знаний','Проверка источников информации','Финансовый план поездки'];
const FOOD_STEPS=['Добавь доступный продукт, который тебе подходит, для разнообразия питания.','Поешь один раз без телефона, замечая насыщение.','Обрати внимание на достаточное питьё воды.','Спланируй один удобный домашний приём пищи.','Включи подходящий источник белка в один приём пищи.','Постарайся есть в комфортном регулярном ритме.','Заметь, что тебе подходит и как ты себя чувствуешь.','Подготовь простой перекус, если предстоит насыщенный день.','Составь список продуктов на два дня.','Поешь спокойно, без спешки.','Выбери доступное разнообразие без строгих запретов.','Подумай, как удобно питаться в день движения.','Отметь связь еды и уровня энергии без диагнозов.','Сделай один осознанный комфортный выбор в питании.'];
const SOCIAL_STEPS=['Спроси близкого человека, как прошёл день, и внимательно выслушай.','Начни простой разговор без ожидания выгоды.','Поблагодари человека за конкретное хорошее действие.','Задай открытый вопрос и выслушай полный ответ.','Спокойно вырази своё мнение без длинных оправданий.','Побудь десять минут с близкими без телефона.','Расскажи семье об одном позитивном событии.','Запиши сильную сторону и факт, который её подтверждает.','Говори чуть медленнее, делая небольшие паузы.','Попроси конкретную обратную связь по разговору.','Поддержи другого человека без непрошеного совета.','Договорись о совместном времени с семьёй.','Спокойно попроси о помощи или информации.','Расскажи за минуту о своей идее, не торопясь.','Прояви доброжелательную инициативу в общении.'];
const PRESENCE_STEPS=['Спокойно расправь плечи перед разговором.','Улыбнись естественно и поздоровайся.','Задай открытый вопрос и не перебивай.','Выдержи небольшую паузу перед ответом.','Потренируй спокойный голос без спешки.','Скажи искренний конкретный комплимент.','Начни короткий разговор без ожидания результата.','Пошути доброжелательно, без сарказма.','Сохраняй комфортный зрительный контакт.','Выскажи мнение спокойно, без оправданий.','Перефразируй одну мысль собеседника.','Прояви инициативу в общении.','Заметь, когда чувствовал себя комфортно среди людей.','Попроси доверенного человека об обратной связи.'];
const MOVE_STEPS=['Комфортная прогулка','Мягкая разминка и мобильность','Прогулка или лёгкая пробежка по самочувствию','Небольшая силовая тренировка подходящего уровня','Разминка, растяжка без боли или прогулка','Теннис, зал или другая приятная активность','Восстановительная прогулка или отдых по самочувствию'];
const TRAVEL_STEPS=['Выбери новое место, которое хочешь посетить.','Оцени бюджет будущей короткой поездки.','Найди идею семейного путешествия.','Продумай время поездки и условия для семьи.','Запиши, какие впечатления для тебя важнее всего.','Проверь, какую сумму реально можно откладывать на поездку.','Сохрани одну конкретную идею для отдыха.'];
function create(ctx){
 const S=()=>ctx.state(),e=ctx.e,num=ctx.num,today=ctx.today,plus=ctx.plusDays,delta=ctx.deltaDays,ru=ctx.ruDate,money=ctx.money;
 const log=date=>S().data.daily_logs.find(x=>x.log_date===date)||{};
 function get(){
  const x=S().profile?.montblanc60;
  if(!x||x.version!==1||typeof x.started!=='string'||!(/^\d{4}-\d{2}-\d{2}$/.test(x.started)))return null;
  return {version:1,started:x.started,pace:x.pace==='gentle'?'gentle':'steady',days:x.days&&typeof x.days==='object'&&!Array.isArray(x.days)?x.days:{}};
 }
 const elapsed=(p=get())=>p?Math.max(0,Math.min(60,delta(p.started,today())+1)):0;
 const dateOf=(i,p=get())=>p?plus(p.started,Math.max(0,Math.min(59,i))):today();
 const index=(p=get())=>Math.max(0,Math.min(59,S().mission60DayIndex==null?elapsed(p)-1:S().mission60DayIndex));

 function dayMode(i,p=get()){
  const override=p?.days?.[dateOf(i,p)]?.mode;
  return ['gentle','steady'].includes(override)?override:(p?.pace==='gentle'||i%7===6?'gentle':'steady');
 }
 function tasks(i,p=get()){
  const phase=Math.floor(i/12),day=i%7,week=Math.floor(i/7),gentle=dayMode(i,p)==='gentle';
  const min=gentle?{focus:12,english:7,sport:5,learning:3,diary:3,family:0}:{focus:25,english:15,sport:10,learning:7,diary:5,family:5};
  const grammar=['be / have и простые вопросы','Present Simple / Continuous','Past Simple и связки','Будущее, просьбы и аргументы','Связная речь и обсуждение условий'][phase];
  const speaking=['Скажи 5 фраз о себе вслух','Сформулируй 4 вопроса клиенту','Перескажи вчерашний день','Объясни ценность услуги за минуту','Запиши минутный ответ и исправь 2 ошибки'][phase];
  return [
   {id:'focus',title:'Один проверяемый шаг к доходу',detail:INCOME_STEPS[i]+' Зафиксируй конкретный результат, а не только потраченное время.',minutes:min.focus,core:true},
   {id:'english',title:'Английский · '+min.english+' мин',detail:'Тема: '+ENGLISH_TOPICS[i%ENGLISH_TOPICS.length]+'. '+grammar+'. '+speaking+'. Аудирование и повторение входят в эти минуты; пройденный урок можно засчитать.',minutes:min.english,core:true},
   {id:'sport',title:day===6?'Бережное движение или восстановление':'Движение и энергия',detail:MOVE_STEPS[day]+'. Засчитывай уже проведённую тренировку. Не занимайся через боль.',minutes:min.sport,core:true},
   {id:'learning',title:'Знание → применение',detail:'Тема: «'+LEARNING_TOPICS[i%LEARNING_TOPICS.length]+'». Назови один практический вывод, а каждый седьмой день повтори изученное.',minutes:min.learning,core:true},
   {id:'nutrition',title:'Питание и самочувствие',detail:FOOD_STEPS[i%FOOD_STEPS.length]+' Без отдельного таймера и строгих запретов.',minutes:0,core:false},
   {id:'family',title:'Близкие и уверенное общение',detail:SOCIAL_STEPS[i%SOCIAL_STEPS.length]+' Не стремись понравиться всем — слушай, проявляй инициативу и уважение.',minutes:min.family,core:false},
   {id:'diary',title:'Дневник: факт → вывод → завтра',detail:'Запиши самочувствие, один реальный результат, препятствие и посильный шаг на завтра.',minutes:min.diary,core:true},
   ...(day===6?[{id:'travel',title:'Путешествие и вдохновение',detail:TRAVEL_STEPS[week%7],minutes:0,core:false}]:[])
  ];
 }
 function auto(id,date,p=get()){
  const x=log(date),i=p?delta(p.started,date):-1;
  if(id==='diary')return !!x.reflection_done;
  const task=i>=0&&i<60?tasks(i,p).find(t=>t.id===id):null;
  const legacy=date<'2026-11-21',oldReq={english:15,sport:10,learning:10,focus:15,family:10};
  const req=legacy?oldReq[id]:task?.minutes;
  if(S().data.tasks.some(t=>t.task_date===date&&t.m60_action_id===id&&ctx.taskIsDone(t)))return true;
  if(id==='english')return req>0&&num(x.english_min)>=req;
  if(id==='sport')return (req>0&&num(x.exercise_min)>=req)||(legacy&&S().data.tasks.some(t=>t.task_date===date&&ctx.taskIsDone(t)&&['sport','health'].includes(t.category)));
  if(id==='learning')return req>0&&num(x.learning_min)>=req;
  if(id==='focus')return (req>0&&num(x.focus_min)>=req)||(legacy&&S().data.tasks.some(t=>t.task_date===date&&ctx.taskIsDone(t)&&['finance','focus'].includes(t.category)));
  if(id==='family')return num(x.family_min)>=(req||5)&&num(x.family_min)>0;
  if(id==='nutrition')return x.m60_nutrition_done===true;
  return false;
 }
 function status(id,date,p=get()){
  const recorded=auto(id,date,p),manual=!!p?.days?.[date]?.checked?.[id];
  return {done:recorded||manual,recorded,manual};
 }
 function stats(p=get()){
  if(!p)return null;
  const n=elapsed(p),all=Array.from({length:60},(_,i)=>tasks(i,p).length).reduce((a,b)=>a+b,0),totalCore=300;
  let possible=0,done=0,active=0,core=0,corePossible=0,coreDone=0;
  const areas=Object.fromEntries([...AREAS.map(a=>a.id),'travel'].map(k=>[k,{done:0,possible:0}]));
  const weeks=Array.from({length:9},(_,i)=>({index:i,possible:0,done:0,active:0}));
  for(let i=0;i<n;i++){
   const d=dateOf(i,p),list=tasks(i,p),w=weeks[Math.floor(i/7)];let count=0;
   for(const t of list){
    const yes=status(t.id,d,p).done;
    possible++;w.possible++;areas[t.id].possible++;
    if(t.core)corePossible++;
    if(yes){done++;w.done++;areas[t.id].done++;count++;if(t.core)coreDone++}
   }
   if(count){active++;w.active++}
   if(list.filter(t=>t.core).every(t=>status(t.id,d,p).done))core++;
  }
  const tasksOfPeriod=S().data.tasks.filter(x=>x.task_date>=p.started&&x.task_date<=today()&&!['cancelled','skipped'].includes(x.status));
  const personalDone=tasksOfPeriod.filter(ctx.taskIsDone).length;
  return {elapsed:n,total:all,totalCore,possible,done,active,core,corePossible,coreDone,areas,weeks,
   personalDone,personalTotal:tasksOfPeriod.length,bonusDone:done-coreDone,
   journey:Math.round(coreDone/totalCore*100),actual:corePossible?Math.round(coreDone/corePossible*100):0};
 }
 function recommendations(p=get(),s=stats(p)){
  if(!p||!s)return ['Начни с одного конкретного шага. Реальные наблюдения появятся после первых записей.'];
  const logs=S().data.daily_logs.filter(x=>x.log_date>=plus(today(),-6)&&x.log_date<=today());
  const energy=logs.map(x=>Number(x.evening_energy)).filter(x=>x>=1&&x<=10),avg=energy.length?energy.reduce((a,b)=>a+b,0)/energy.length:null;
  const contacts=logs.reduce((a,x)=>a+num(x.sales_contacts),0),replies=logs.reduce((a,x)=>a+num(x.sales_replies),0),tips=[];
  if(avg!==null&&avg<5)tips.push('Энергия по дневнику низкая. Сегодня выбери 30-минутный режим и удели внимание восстановлению.');
  if(s.elapsed>=4&&s.active/s.elapsed<.5)tips.push('Сейчас мало активных дней. Выбери один короткий шаг без попыток наверстать пропуски.');
  if(s.elapsed>=5&&s.areas.english.done/Math.max(1,s.areas.english.possible)<.4)tips.push('Проверь, внесены ли уже пройденные уроки английского. Не добавляй второе длинное занятие.');
  if(s.elapsed>=5&&s.areas.focus.done/Math.max(1,s.areas.focus.possible)<.4)tips.push('Шаги к доходу пока нерегулярны. Запланируй одно конкретное обращение или предложение.');
  if(s.elapsed>=7&&contacts>0&&replies===0)tips.push('Контакты с клиентами записаны, но ответов нет. Проверь выбор клиента и персонализацию сообщения.');
  if(s.elapsed>=7&&contacts===0&&ctx.monthIncome()===0)tips.push('Нет записанных клиентских контактов и оплат. Следующий шаг — проверить спрос с одним реальным клиентом.');
  if(!tips.length)tips.push('Сохраняй один главный приоритет и фиксируй наблюдаемые результаты. Количество отметок не равно росту дохода.');
  return tips.slice(0,3);
 }
 function coachPrompt(){
  const p=get(),s=stats(p),logs=S().data.daily_logs.filter(x=>x.log_date>=plus(today(),-13)&&x.log_date<=today()),sum=k=>logs.reduce((a,x)=>a+num(x[k]),0);
  const energy=logs.map(x=>Number(x.evening_energy)).filter(v=>v>=1&&v<=10);
  const facts={date:today(),days_with_records:logs.length,program_day:s?.elapsed||0,completed_core:s?.coreDone||0,available_core:s?.corePossible||0,personal_tasks:s?.personalDone||0,english_min:sum('english_min'),sport_min:sum('exercise_min'),learning_min:sum('learning_min'),focus_min:sum('focus_min'),family_min:sum('family_min'),average_energy:energy.length?Math.round(10*energy.reduce((a,b)=>a+b,0)/energy.length)/10:null,client_contacts:sum('sales_contacts'),client_replies:sum('sales_replies'),offers:sum('sales_offers'),payments:sum('sales_paid'),income_this_month:ctx.monthIncome()};
  const confidence=logs.map(x=>Number(x.m60_confidence)).filter(v=>v>=1&&v<=10);facts.average_confidence=confidence.length?Math.round(10*confidence.reduce((a,b)=>a+b,0)/confidence.length)/10:null;facts.confidence_samples=confidence.length;
  return 'Проанализируй факты из моего MONTBLANC за 14 дней как внимательный наставник по поведению, английскому и B2B-продажам. Не придумывай данных, не ставь диагнозы и не гарантируй доход. Дай 3 проверяемых вывода, 2 улучшения на следующую неделю, план на завтра на 30–67 минут и 1 показатель для контроля через 7 дней. Не считай одну активность дважды.\n'+JSON.stringify(facts,null,2);
 }

 function awards(s=stats()){
  if(!s)return [];
  return [
   ['🌱','Начало',s.done>=1],['⚡','10 выполненных практик',s.done>=10],['🏃','7 дней движения',s.areas.sport.done>=7],
   ['🗣️','10 практик английского',s.areas.english.done>=10],['📚','20 уроков знаний',s.areas.learning.done>=20],
   ['🥗','10 дней питания',s.areas.nutrition.done>=10],['🎯','20 задач к доходу',s.areas.focus.done>=20],
   ['🤝','20 шагов для близких',s.areas.family.done>=20],['🏕️','10 активных дней',s.active>=10],
   ['🏔️','30 активных дней',s.active>=30],['🧭','50 активных дней',s.active>=50],
   ['🏆','Финиш 60 дней',s.elapsed===60&&s.active>=40]
  ].map(([emoji,title,earned])=>({emoji,title,earned}));
 }
 async function start(){
  if(!S().local&&!S().demo)throw Error('Для личного сохранения открой защищённый режим MONTBLANC');
  if(get())return;
  await ctx.saveProfile({...S().profile,montblanc60:{version:1,started:today(),pace:'steady',days:{}}});
  S().mission60DayIndex=null;
 }
 async function pace(value){
  const p=get();if(!p||!['steady','gentle'].includes(value))return;
  await ctx.saveProfile({...S().profile,montblanc60:{...p,pace:value}});
 }

 async function dayPace(value,date){
  const p=get();if(!p||!['gentle','steady'].includes(value)||!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(date)||date>today())return;
  const i=delta(p.started,date);if(i<0||i>=60)return;
  const old=p.days[date]||{},preserved={...(old.checked||{})};
  // Keep already credited low-intensity actions even if the day's budget increases.
  for(const item of tasks(i,p))if(status(item.id,date,p).done)preserved[item.id]=true;
  await ctx.saveProfile({...S().profile,montblanc60:{...p,days:{...p.days,[date]:{...old,mode:value,checked:preserved}}}});
 }
 async function toggle(id,date){
  const p=get();if(!p||date>today()||!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(date))return;
  const i=delta(p.started,date);if(i<0||i>=60||!tasks(i,p).some(t=>t.id===id))return;
  if(id==='diary'){S().reflectionDate=date;S().page='reflection';ctx.render();ctx.scrollTop();return}
  if(auto(id,date,p)){ctx.notify('Уже засчитано по дневнику или явно привязанной задаче');return}
  const old=p.days[date]||{},checked={...(old.checked||{})};
  checked[id]=!checked[id];
  await ctx.saveProfile({...S().profile,montblanc60:{...p,days:{...p.days,[date]:{...old,checked}}}});
 }

 function summaryRing(s){
  const p=s?.journey||0;
  return '<div class="m60-ring" role="img" aria-label="Выполнено '+p+' процентов программы" style="--p:'+p+'"><div><strong>'+p+'%</strong><small>к вершине</small></div></div>';
 }
 function section(k,title,link=''){return '<div class="m60-sectionhead"><div><span>'+k+'</span><h2>'+title+'</h2></div>'+link+'</div>'}
 function onboarding(){
  return '<section class="m60-card m60-start"><div class="m60-start-icon">🏔️</div><h2>Твой путь на 60 дней</h2><p>Английский, ежедневное движение, фокус на доходе, обучение, питание, семья и личный дневник. Пять главных практик и дополнительные шаги. Стандартный день — 67 минут, облегчённый — 30 минут. Без штрафов за пропуски.</p><div class="m60-tags"><b>60 дней</b><b>7 сфер</b><b>Свой темп</b></div>'+(S().local||S().demo?'<button class="m60-primary" data-action="m60-start">Начать экспедицию →</button>':'<p>Для сохранения открой приватный режим MONTBLANC на iPhone.</p>')+'</section>';
 }
 function checklist(i,p=get(),limit=12){
  const d=dateOf(i,p),future=d>today();
  return '<div class="m60-checklist">'+tasks(i,p).slice(0,limit).map(t=>{
   const flag=status(t.id,d,p),area=AREAS.find(a=>a.id===t.id),emoji=area?.emoji||'✈️';
   return '<div class="m60-check '+(flag.done?'is-done':'')+'"><button data-action="m60-toggle" data-id="'+t.id+'" data-date="'+d+'" '+(future?'disabled':'')+' aria-label="'+e(flag.done?'Отмечено: '+t.title:'Выполнить: '+t.title)+'" aria-pressed="'+flag.done+'">'+(flag.done?'✓':'')+'</button><div class="m60-checkcopy"><div><span>'+emoji+'</span><b>'+e(t.title)+'</b>'+(t.core?'':'<i>бонус</i>')+'</div><p>'+e(t.detail)+'</p><small>'+(t.minutes?'≈ '+t.minutes+' мин':'Встроено в обычный день')+(flag.recorded?' · из дневника/плана':'')+'</small></div></div>'
  }).join('')+'</div>';
 }
 function home(){
  const p=get(),s=stats(p),date=today(),todayLog=log(date),elapsedDays=p?elapsed(p):0,current=p?Math.max(0,Math.min(59,elapsedDays-1)):0,finished=!!(p&&delta(p.started,date)>=60);
  const currentTasks=p?tasks(current,p):[],hits=p?currentTasks.filter(x=>status(x.id,date,p).done).length:0;
  const personal=S().data.tasks.filter(x=>x.task_date===date&&!['skipped','cancelled'].includes(x.status)),done=personal.filter(ctx.taskIsDone).length;
  const finances=ctx.monthIncome(),debt=ctx.currentDebt(),year=num(S().profile?.annual_income_goal);
  return '<div class="m60-page"><div class="m60-title"><span>'+e(ru(date))+' · MONTBLANC</span><h1>Сегодня</h1><p>Каждый маленький шаг имеет значение.</p></div>'+
   (finished?'<section class="m60-card m60-highlight"><div class="m60-feature"><div><span>🏔️ МАРШРУТ ЗАВЕРШЁН</span><h2>60 дней позади</h2><p>Главных практик: '+s.coreDone+' из '+s.totalCore+'. Выводы важнее идеальной серии.</p></div>'+summaryRing(s)+'</div><button data-page="progress" class="m60-primary">Итоги и следующие шаги →</button></section>':p?'<section class="m60-card m60-highlight"><div class="m60-feature"><div><span>🏔️ ТВОЯ ЭКСПЕДИЦИЯ</span><h2>День '+(current+1)+' <small>из 60</small></h2><p>'+PHASES[Math.floor(current/12)][0]+' · '+hits+' из '+currentTasks.length+' практик сегодня</p></div>'+summaryRing(s)+'</div><div class="m60-track"><i style="width:'+Math.round(hits/currentTasks.length*100)+'%"></i></div><button class="m60-primary" data-page="mission60">Практики на сегодня →</button></section>':onboarding())+
   (p&&!finished?'<section class="m60-card m60-daily-focus"><span class="m60-focus-label">🎯 СЕГОДНЯ · РЕЗУЛЬТАТ ПО ДОХОДУ</span><h2>'+e(INCOME_STEPS[current])+'</h2><p>Цель — один конкретный результат: обращение, ответ, предложение или оплата.</p><button data-page="mission60" class="m60-textbutton">План дня · '+currentTasks.reduce((n,t)=>n+t.minutes,0)+' мин →</button></section><section class="m60-card m60-presence"><span class="m60-focus-label">✨ PRESENCE · УВЕРЕННОСТЬ</span><h2>Естественное обаяние</h2><p>'+e(PRESENCE_STEPS[current%PRESENCE_STEPS.length])+' Это наблюдение, а не дополнительная галочка.</p><button data-page="reflection" class="m60-textbutton">Записать ощущения →</button></section>':'')+
    section('ПЛАН НА ДЕНЬ','Мои дела','<button data-page="tasks">Весь план ›</button>')+
   '<section class="m60-card"><div class="m60-planhead"><span>Задачи: '+done+'/'+personal.length+'</span><button data-action="new-task" data-date="'+date+'">+ Добавить</button></div>'+
   (personal.length?personal.slice(0,6).map(x=>planRow(x)).join(''):'<p class="m60-empty">Поставь один конкретный шаг на сегодня.</p>')+'<button data-page="tasks" class="m60-textbutton">План на неделю →</button></section>'+
   '<div class="m60-quickgrid"><button data-page="reflection" class="m60-quick lavender"><span>✍️</span><b>Дневник</b><small>'+(todayLog.reflection_done?'✓ Запись сохранена':'Мысли, энергия, достижения')+'</small></button><button data-page="progress" class="m60-quick green"><span>📊</span><b>Прогресс</b><small>'+(s?s.coreDone:'0')+' главных практик</small></button></div>'+
   section('ПО ФАКТАМ','Мои показатели','<button data-page="progress">Подробнее ›</button>')+
   '<div class="m60-metrics"><button data-page="finance"><span>💶 Доход за месяц</span><strong>'+money(finances)+'</strong><small>Цель за год: '+(year>0?money(year):'Не задана')+'</small></button><button data-page="finance"><span>💳 Долг</span><strong>'+money(debt)+'</strong><small>Фактический остаток</small></button><button data-page="reflection"><span>💙 Энергия</span><strong>'+(todayLog.evening_energy||'—')+'</strong><small>Оценка сегодня · /10</small></button><button data-page="mission60"><span>🏃 Практики</span><strong>'+(s?.done||0)+'</strong><small>За весь маршрут</small></button></div>'+
   section('ЕДИНАЯ СИСТЕМА','Важные направления')+'<div class="m60-linklist">'+
   [['goals','🎯','Цели и мечты','Финансы, тело, семья, путешествия'],['ideas-hub','💡','Идеи и проекты','Проверки, заметки, решения'],['route','🏔️','Маршрут А → Б','Большой жизненный путь'],['more','▦','Архив и инструменты','Всё сохранённое раньше']].map(([pg,emoji,title,sub])=>'<button data-page="'+pg+'"><span>'+emoji+'</span><div><b>'+title+'</b><small>'+sub+'</small></div><em>›</em></button>').join('')+'</div></div>';
 }
 function program(){
  const p=get();if(!p)return '<div class="m60-page"><div class="m60-title"><span>ТВОЙ ПУТЬ</span><h1>60 дней роста</h1><p>Действия вместо обещаний.</p></div>'+onboarding()+'<section class="m60-card"><h2>Пять этапов</h2>'+PHASES.map((x,i)=>'<div class="m60-phase-row"><strong>0'+(i+1)+'</strong><div><b>'+x[0]+'</b><p>'+x[1]+'</p></div><small>'+(i*12+1)+'–'+(i+1)*12+'</small></div>').join('')+'</section></div>';
  const s=stats(p),i=index(p),d=dateOf(i,p),ts=tasks(i,p),hits=ts.filter(t=>status(t.id,d,p).done).length,phase=Math.floor(i/12);
  const phaseSegments=PHASES.map((x,k)=>'<div class="'+(k===phase?'selected':'')+'"><b>'+(k+1)+'</b><small>'+x[0]+'</small></div>').join('');
  const calendar=Array.from({length:60},(_,k)=>{const date=dateOf(k,p),all=tasks(k,p),n=all.filter(t=>status(t.id,date,p).done).length;
   return '<button class="'+(k===i?'selected ':'')+(date>today()?'future ':'')+(n===all.length?'complete':'')+'" data-action="m60-day" data-index="'+k+'" aria-label="День '+(k+1)+': '+n+' из '+all.length+'"><b>'+(k+1)+'</b><span>'+(date>today()?'·':n===all.length?'✓':n||'·')+'</span></button>'}).join('');
  return '<div class="m60-page"><div class="m60-title"><span>🏔️ ТВОЯ ЭКСПЕДИЦИЯ</span><h1>60 дней роста</h1><p>Пять этапов к более собранной жизни.</p></div><section class="m60-card m60-highlight"><div class="m60-feature"><div><span>ЭТАП '+(phase+1)+' / 5</span><h2>'+PHASES[phase][0]+'</h2><p>'+PHASES[phase][1]+'</p></div>'+summaryRing(s)+'</div><div class="m60-track"><i style="width:'+s.journey+'%"></i></div><div class="m60-track-label"><span>'+s.coreDone+' из '+s.totalCore+' главных практик</span><b>'+s.journey+'% пути</b></div><div class="m60-phase-mini">'+phaseSegments+'</div></section>'+
  '<section class="m60-card"><div class="m60-dayhead"><div><span>ДЕНЬ '+(i+1)+' · '+e(ru(d))+'</span><h2>Мои практики</h2><p>'+(d>today()?'Будущий день: пока без отметок':ts.filter(x=>x.core&&status(x.id,d,p).done).length+' из 5 главных шагов')+'</p></div><strong>'+hits+'/'+ts.length+'</strong></div><div class="m60-daynav"><button data-action="m60-day" data-index="'+Math.max(0,i-1)+'" '+(i===0?'disabled':'')+' aria-label="Предыдущий день">‹</button><span>День '+(i+1)+'</span><button data-action="m60-day" data-index="'+Math.min(59,i+1)+'" '+(i===59?'disabled':'')+' aria-label="Следующий день">›</button><button data-action="m60-today">Сегодня</button></div>'+checklist(i,p)+((i+1)%7===0?'<section class="m60-card m60-week-review"><h2>Обзор недели</h2><p>Что сработало? Какие ответы были от клиентов? Как изменились энергия и уверенность? Что убрать из перегрузки?</p><button data-page="review" class="m60-textbutton">Записать выводы недели →</button></section>':'')+
  '<div class="m60-pace"><div><b>Нагрузка этого дня</b><small>≈ '+ts.reduce((n,t)=>n+t.minutes,0)+' мин · уроки и тренировки не дублируются</small></div><div><button data-action="m60-day-pace" data-date="'+d+'" data-value="gentle" '+(d>today()?'disabled':'')+' class="'+(dayMode(i,p)==='gentle'?'active':'')+'">30 мин</button><button data-action="m60-day-pace" data-date="'+d+'" data-value="steady" '+(d>today()?'disabled':'')+' class="'+(dayMode(i,p)==='steady'?'active':'')+'">67 мин</button></div></div><button data-action="m60-diary-day" data-date="'+d+'" class="m60-primary" '+(d>today()?'disabled':'')+'>Вечерний дневник этого дня →</button></section>'+
  section('НА КАЖДЫЙ ДЕНЬ','Карта 60 дней')+'<section class="m60-card"><div class="m60-daygrid">'+calendar+'</div></section>'+
  '<section class="m60-card"><h2>Факты программы</h2><div class="m60-summary"><div><b>'+s.coreDone+'</b><small>Главных практик завершено</small></div><div><b>'+s.active+'</b><small>Активных дней</small></div><div><b>'+s.actual+'%</b><small>Выполнение на сегодня</small></div></div><button class="m60-textbutton" data-page="progress">Статистика и достижения →</button></section></div>';
 }
 function planRow(t){
  const done=ctx.taskIsDone(t),cat=ctx.taskLabel?.[t.category]||'Личное';
  return '<div class="m60-planrow"><button data-action="toggle-task" data-id="'+e(t.id)+'" aria-label="'+(done?'Вернуть задачу':'Отметить выполненной')+'" class="'+(done?'done':'')+'">'+(done?'✓':'')+'</button><div class="'+(done?'done':'')+'"><b>'+e(t.title)+'</b><small>'+e(cat)+(t.is_main?' · ★ главное':'')+(t.due_time?' · '+e(t.due_time):'')+'</small></div><button class="m60-ellipsis" data-action="edit-task" data-id="'+e(t.id)+'" aria-label="Изменить задачу">•••</button></div>';
 }
 function planner(){
  const scope=S().mission60Range||'week',now=today(),all=S().data.tasks.filter(t=>!['cancelled','skipped'].includes(t.status)),done=all.filter(ctx.taskIsDone).length;
  const overdue=all.filter(t=>t.task_date&&t.task_date<now&&!ctx.taskIsDone(t)).sort((a,b)=>String(a.task_date).localeCompare(String(b.task_date)));
  const dates=Array.from({length:scope==='month'?30:7},(_,i)=>plus(now,i));
  const groups=dates.map((date,i)=>{const list=all.filter(t=>t.task_date===date).sort((a,b)=>Number(ctx.taskIsDone(a))-Number(ctx.taskIsDone(b)));if(!list.length&&i>=7)return '';
    return '<section class="m60-card m60-plangroup"><div class="m60-planhead"><div><h2>'+(i===0?'Сегодня':i===1?'Завтра':e(ru(date)))+'</h2><small>'+list.filter(ctx.taskIsDone).length+' / '+list.length+' сделано</small></div><button data-action="new-task" data-date="'+date+'" aria-label="Добавить на '+date+'">+</button></div>'+(list.length?list.map(planRow).join(''):'<p class="m60-empty">Задач пока нет.</p>')+'</section>'}).join('');
  return '<div class="m60-page"><div class="m60-title"><span>ПЛАНИРОВЩИК</span><h1>Мой план</h1><p>Сегодня, завтра, неделя и месяц.</p></div><div class="m60-planbuttons"><button class="m60-primary" data-action="new-task" data-date="'+now+'">+ Добавить задачу</button><button data-page="mission60">Практики →</button></div><div class="m60-summary"><div><b>'+all.filter(t=>!ctx.taskIsDone(t)).length+'</b><small>Осталось</small></div><div><b>'+done+'</b><small>Выполнено</small></div><div><b>'+overdue.length+'</b><small>Нужны решения</small></div></div>'+
  '<div class="m60-segments"><button data-action="m60-scope" data-value="week" class="'+(scope==='week'?'active':'')+'">7 дней</button><button data-action="m60-scope" data-value="month" class="'+(scope==='month'?'active':'')+'">30 дней</button></div>'+
  (overdue.length?'<section class="m60-card"><h2>Ранее запланировано · '+overdue.length+'</h2>'+overdue.slice(0,15).map(planRow).join('')+'</section>':'')+groups+
  '<section class="m60-card m60-tail"><button data-page="mission60">🏔️ Практики программы →</button><button data-page="ideas-hub">💡 Идеи и проекты →</button></section></div>';
 }
 function diaryRow(formData,old,finished){
  const text=(k,limit=2500)=>String(formData[k]===undefined?(old[k]||''):formData[k]||'').trim().slice(0,limit);
  const integer=(k,min,max)=>{const raw=formData[k];if(raw===undefined)return old[k]??null;if(String(raw).trim()==='')return null;const n=Number(raw);if(!Number.isFinite(n)||n<min||n>max)throw Error('Проверь поле: '+k);return n};
  return {...old,log_date:String(formData.log_date),thoughts:text('thoughts'),win_of_day:text('win_of_day'),blocked_why:text('blocked_why'),
   future_step:text('future_step'),today_learned:text('today_learned'),tomorrow_one:text('tomorrow_one'),
   m60_nutrition_note:text('m60_nutrition_note'),m60_family_note:text('m60_family_note'),m60_travel_note:text('m60_travel_note'),m60_focus_evidence:text('m60_focus_evidence'),m60_english_evidence:text('m60_english_evidence'),m60_social_evidence:text('m60_social_evidence'),m60_presence_evidence:text('m60_presence_evidence'),
   m60_nutrition_done:formData.m60_nutrition_done===undefined?!!old.m60_nutrition_done:formData.m60_nutrition_done==='yes',
   evening_energy:integer('evening_energy',1,10),evening_mood:integer('evening_mood',1,5),m60_confidence:integer('m60_confidence',1,10),
   english_min:integer('english_min',0,720),exercise_min:integer('exercise_min',0,720),focus_min:integer('focus_min',0,720),learning_min:integer('learning_min',0,720),
   family_min:integer('family_min',0,720),social_min:integer('social_min',0,720),sleep_hours:integer('sleep_hours',0,24),
   reflection_done:!!finished||!!old.reflection_done};
 }
 async function saveJournal(input,finished=false){
  const date=String(input.log_date||'');
  if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||date>today())throw Error('Запись возможна только за сегодняшний или прошлый день');
  await ctx.saveRecord('daily_logs',diaryRow(input,log(date),finished));
 }
 async function saveDraft(force=false){
  const f=document.querySelector('form[data-form="mission-journal"]');
  if(!f||!f.isConnected||!S().local||!ctx.localKey())return;
  if(!force&&f.dataset.dirty!=='yes')return;
  const data=Object.fromEntries(new FormData(f).entries());
  await saveJournal(data,force);
  f.dataset.dirty='';
 }
 function field(k,label,value='',attr=''){
  return '<label class="m60-input"><span>'+label+'</span><input name="'+k+'" value="'+e(value??'')+'" '+attr+' /></label>'
 }
 function area(k,label,value='',placeholder=''){
  return '<label class="m60-input"><span>'+label+'</span><textarea name="'+k+'" rows="3" placeholder="'+e(placeholder)+'">'+e(value||'')+'</textarea></label>'
 }
 function diary(){
  const date=S().reflectionDate||today(),r=log(date),saved=!!r.reflection_done,all=S().data.daily_logs.filter(x=>x.reflection_done).length;
  const metrics=[['english_min','Английский, мин',r.english_min],['exercise_min','Движение, мин',r.exercise_min],['learning_min','Обучение, мин',r.learning_min],
   ['focus_min','Фокус, мин',r.focus_min],['family_min','Семья, мин',r.family_min],['social_min','Соцсети, мин',r.social_min],['sleep_hours','Сон, часы',r.sleep_hours]];
  return '<div class="m60-page"><div class="m60-title"><span>ЛИЧНЫЙ ДНЕВНИК · '+all+' ЗАПИСЕЙ</span><h1>Мой день</h1><p>Всё важное — в одной записи.</p></div>'+
   '<div class="m60-diarydate"><button data-action="reflection-date" data-value="'+plus(date,-1)+'" aria-label="Предыдущий день">‹</button><div><b>'+e(ru(date))+'</b><small>'+(saved?'✓ Итог сохранён':'Черновик или новая запись')+'</small></div><button data-action="reflection-date" data-value="'+plus(date,1)+'" '+(date>=today()?'disabled':'')+' aria-label="Следующий день">›</button><button data-action="reflection-date" data-value="'+today()+'">Сегодня</button></div>'+
   '<form data-form="mission-journal"><input type="hidden" name="log_date" value="'+date+'"/>'+
   '<section class="m60-card"><div class="m60-cardtitle"><span>💙</span><div><h2>Как я себя чувствовал?</h2><small>Наблюдение без оценки себя.</small></div></div><div class="m60-two">'+field('evening_energy','Энергия 1–10',r.evening_energy,'type="number" min="1" max="10" inputmode="numeric" placeholder="6"')+field('evening_mood','Настроение 1–5',r.evening_mood,'type="number" min="1" max="5" inputmode="numeric" placeholder="3"')+field('m60_confidence','Уверенность, 1–10',r.m60_confidence,'type="number" min="1" max="10" inputmode="numeric" placeholder="5"')+'</div>'+
   area('thoughts','Мысли и чувства',r.thoughts,'Что сейчас меня волнует?')+area('win_of_day','Маленькая победа',r.win_of_day,'Что сегодня удалось?')+area('blocked_why','Что не сделал и почему?',r.blocked_why,'Факты, а не обвинения.')+'</section>'+
   '<section class="m60-card"><div class="m60-cardtitle"><span>🎯</span><div><h2>Движение к моим целям</h2><small>Даже один реальный шаг.</small></div></div>'+area('future_step','Что сделал для своего будущего?',r.future_step,'Доход, развитие, спорт, семья…')+area('today_learned','Что нового узнал?',r.today_learned,'Одна полезная мысль.')+area('tomorrow_one','Одно важное дело на завтра',r.tomorrow_one,'Конкретный и посильный шаг.')+'</section>'+
   '<section class="m60-card m60-evidence"><div class="m60-cardtitle"><span>🔎</span><div><h2>Доказательства изменений</h2><small>Один факт на сферу, не дополнительные достижения.</small></div></div>'+area('m60_focus_evidence','Результат по доходу',r.m60_focus_evidence,'Клиент, предложение, ответ или оплата')+area('m60_english_evidence','Что уже умею по-английски?',r.m60_english_evidence,'Фраза или разговор, который сегодня получился')+area('m60_social_evidence','Что удалось в общении?',r.m60_social_evidence,'Разговор, инициатива, улыбка, внимание к близким')+area('m60_presence_evidence','Уверенное присутствие',r.m60_presence_evidence,'Где был спокойным, открытым, позитивным?')+'</section>'+'<section class="m60-card"><div class="m60-cardtitle"><span>🥗</span><div><h2>Питание и жизнь</h2><small>Без жёстких ограничений и диет.</small></div></div><label class="m60-checklabel"><input type="hidden" name="m60_nutrition_done" value="no"><input type="checkbox" name="m60_nutrition_done" value="yes" '+(r.m60_nutrition_done?'checked':'')+'/><span>Сделал один подходящий осознанный выбор в питании</span></label>'+
   area('m60_nutrition_note','Питание и самочувствие',r.m60_nutrition_note,'Что подошло?')+area('m60_family_note','Семья и отношения',r.m60_family_note,'Тёплый момент или разговор.')+area('m60_travel_note','Путешествия и впечатления',r.m60_travel_note,'О какой поездке думаю?')+'</section>'+
   '<details class="m60-card m60-details" open><summary>📊 Время и привычки <small>Минуты и сон</small></summary><div class="m60-two">'+metrics.map(([key,label,value])=>field(key,label,value,'type="number" min="0" max="'+(key==='sleep_hours'?24:720)+'" '+(key==='sleep_hours'?'step="any" inputmode="decimal"':'inputmode="numeric"')+' placeholder="0"')).join('')+'</div></details>'+
   '<button class="m60-primary m60-submit" type="submit">✓ Сохранить дневник за '+e(ru(date))+'</button><p class="m60-hint">'+(S().demo?'Демо-режим: запись хранится временно и не шифруется.':S().local?'Черновик шифруется на устройстве. Кнопка завершает итог дня.':'Для сохранения записи нажми кнопку ниже. Не закрывай страницу до подтверждения.')+'</p></form>'+
   '<div class="m60-linklist"><button data-page="feed"><span>📖</span><div><b>История моих дней</b><small>Все прошлые записи</small></div><em>›</em></button><button data-page="ideas-hub"><span>💡</span><div><b>Инкубатор идей</b><small>Записывай и проверяй гипотезы</small></div><em>›</em></button></div></div>';
 }
 function progress(){
  const p=get(),s=stats(p),range=p?p.started:plus(today(),-59),logs=S().data.daily_logs.filter(x=>x.log_date>=range&&x.log_date<=today());
  const sum=k=>logs.reduce((a,x)=>a+num(x[k]),0),sportDays=new Set(logs.filter(x=>num(x.exercise_min)>=10).map(x=>x.log_date));
  const m=ctx.monthIncome(),debt=ctx.currentDebt(),goal=num(S().profile?.annual_income_goal);
  const recent=logs.filter(x=>x.log_date>=plus(today(),-6)),previous=logs.filter(x=>x.log_date>=plus(today(),-13)&&x.log_date<plus(today(),-6));
   const avg=(rows,key)=>{const ns=rows.map(x=>Number(x[key])).filter(n=>n>=1&&n<=10);return ns.length?{v:Math.round(10*ns.reduce((a,b)=>a+b,0)/ns.length)/10,n:ns.length}:null};
   const en=avg(recent,'evening_energy'),ep=avg(previous,'evening_energy'),cn=avg(recent,'m60_confidence'),cp=avg(previous,'m60_confidence');
   const delta=(x,y)=>x&&y&&x.n>=3&&y.n>=3?((x.v-y.v)>0?'↑ +':(x.v-y.v)<0?'↓ ':'→ ')+Math.round(10*(x.v-y.v))/10+'/10':'Недостаточно данных для сравнения';
   const indicators=[
   ['✅','Личные выполненные задачи',S().data.tasks.filter(ctx.taskIsDone).length,'за всё время'],
   ['🗣️','Английский',Math.round(sum('english_min')/6)/10+' ч','в дневнике за маршрут'],
   ['🏃','Дни активности',sportDays.size,'по дневнику'],
   ['📚','Полезные знания',Math.round(sum('learning_min')/6)/10+' ч','за маршрут'],
   ['🎯','Работа в фокусе',Math.round(sum('focus_min')/6)/10+' ч','за маршрут'],
   ['❤️','Время с близкими',Math.round(sum('family_min')/6)/10+' ч','за маршрут'],
   ['✍️','Вечерние итоги',logs.filter(x=>x.reflection_done).length,'сохранено'],
   ['🥗','Питание',logs.filter(x=>x.m60_nutrition_done).length,'осознанных дней']
  ];
  const aw=awards(s),earned=aw.filter(x=>x.earned).length;
  return '<div class="m60-page"><div class="m60-title"><span>МОЙ РОСТ · ПО ФАКТАМ</span><h1>Прогресс</h1><p>Считаем действия отдельно от жизненных результатов.</p></div>'+
   '<section class="m60-card m60-highlight"><div class="m60-feature"><div><span>🏔️ ПУТЬ К ВЕРШИНЕ</span><h2>'+(s?s.coreDone:S().data.tasks.filter(ctx.taskIsDone).length)+' главных практик</h2><p>'+(s?s.coreDone+' главных практик и отдельно '+s.personalDone+' личных задач':'Здесь появятся выполненные шаги программы.')+'</p></div>'+summaryRing(s)+'</div>'+
   (s?'<div class="m60-track"><i style="width:'+s.journey+'%"></i></div><div class="m60-track-label"><span>'+s.coreDone+' из '+s.totalCore+' главных практик</span><b>'+s.journey+'%</b></div><p class="m60-hint">Из доступных за '+s.elapsed+' дней выполнено '+s.actual+'% главных практик. Личные задачи не суммируются с практиками повторно.</p>':'<p>Начни программу на вкладке «60 дней».</p>')+'</section>'+
   section('НАПРАВЛЕНИЯ','По семи сферам')+'<section class="m60-card m60-domains">'+AREAS.map(a=>{const v=s?.areas[a.id]||{done:0,possible:0},pct=v.possible?Math.round(100*v.done/v.possible):0;
    return '<div><div><span>'+a.emoji+' '+a.name+'</span><b>'+v.done+'/'+v.possible+'</b></div><div class="m60-track"><i style="width:'+pct+'%;background:'+a.color+'"></i></div></div>'}).join('')+'</section>'+
   section('РЕАЛЬНЫЕ ИЗМЕНЕНИЯ','Последняя неделя против предыдущей')+'<section class="m60-card"><div class="m60-summary"><div><b>'+(en?en.v+'/10':'—')+'</b><small>Энергия · '+(en?.n||0)+' записей</small></div><div><b>'+(cn?cn.v+'/10':'—')+'</b><small>Уверенность · '+(cn?.n||0)+' записей</small></div></div><p class="m60-hint">Энергия: '+delta(en,ep)+'. Уверенность: '+delta(cn,cp)+'. Для сравнения нужны минимум три оценки за каждую неделю. Это самооценки, а не медицинские показатели.</p></section>'+section('РЕАЛЬНЫЕ ЗАПИСИ','Твои показатели')+'<div class="m60-metrics">'+indicators.map(x=>'<div><span>'+x[0]+' '+x[1]+'</span><strong>'+x[2]+'</strong><small>'+x[3]+'</small></div>').join('')+'</div>'+
   section('ФИНАНСЫ','От нуля к устойчивости')+'<section class="m60-card m60-finances"><div><span>Доход за месяц</span><b>'+money(m)+'</b></div><div><span>Остаток долга</span><b>'+money(debt)+'</b></div><div><span>Годовая цель дохода</span><b>'+(goal>0?money(goal):'Не задана')+'</b></div><button data-page="finance" class="m60-textbutton">Доходы, расходы и резерв →</button><button data-page="goals" class="m60-textbutton">Мои измеримые цели →</button></section>'+
   (s?'<section class="m60-card"><h2>Путь по неделям</h2><div class="m60-weekbars">'+s.weeks.map((w,i)=>{const pct=w.possible?Math.round(w.done/w.possible*100):0;return '<div><div><i style="height:'+pct+'%"></i></div><b>'+(i+1)+'</b><small>'+(w.possible?pct+'%':'—')+'</small></div>'}).join('')+'</div></section>':'')+
   section('КОММЕРЧЕСКИЕ РЕЗУЛЬТАТЫ','Не количество галочек')+'<section class="m60-card"><div class="m60-summary"><div><b>'+logs.reduce((n,x)=>n+num(x.sales_contacts),0)+'</b><small>Обращений</small></div><div><b>'+logs.reduce((n,x)=>n+num(x.sales_replies),0)+'</b><small>Ответов</small></div><div><b>'+logs.reduce((n,x)=>n+num(x.sales_paid),0)+'</b><small>Оплат по журналу</small></div></div><p class="m60-hint">Это этапы воронки, а не разные достижения одного действия. Подтверждённый доход смотри в финансах.</p><button data-page="sales" class="m60-textbutton">Воронка продаж →</button></section>'+section('ПОДСКАЗКИ ПО ТВОИМ ЗАПИСЯМ','Что поможет двигаться дальше')+'<section class="m60-card m60-insights">'+recommendations(p,s).map(x=>'<div><span>✦</span><p>'+e(x)+'</p></div>').join('')+'<p class="m60-hint">Локальные подсказки по записям. Не медицинская диагностика.</p><button data-action="m60-copy-coach" class="m60-coach-button">Подготовить разбор в ChatGPT ↗</button><p class="m60-hint">В буфер копируются только агрегированные показатели за 14 дней, без мыслей из личного дневника. Отправка — вручную.</p></section>'+
   section('НАГРАДЫ','Заслуженные достижения')+'<section class="m60-card"><div class="m60-awards"><div class="m60-award-count"><strong>'+earned+'</strong><small>из '+aw.length+' открыто</small></div>'+aw.map(x=>'<div class="'+(x.earned?'earned':'')+'"><span>'+x.emoji+'</span><b>'+x.title+'</b><small>'+(x.earned?'Открыто':'Впереди')+'</small></div>').join('')+'</div><p class="m60-hint">Пропущенный день не обнуляет ранее сделанное.</p></section>'+
   '<section class="m60-card m60-tail"><button data-page="review">🧠 Недельные выводы →</button><button data-page="route">🏔️ Мой маршрут А → Б →</button><button data-page="more">▦ Все инструменты и архив →</button></section></div>';
 }
 return {AREAS,PHASES,INCOME_STEPS,recommendations,coachPrompt,get,elapsed,dateOf,index,dayMode,tasks,auto,status,stats,awards,start,pace,dayPace,toggle,
  journalRow:diaryRow,saveJournal,saveDraft,home,program,planner,diary,progress};
}
global.MONTBLANC60={create};
})(window);
