const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'..','challenge60.js'),'utf8');

function make(date='2026-11-21'){
 const window={};
 vm.runInNewContext(source,{window});
 let current=date;
 const state={page:'mission60',demo:true,local:false,mission60DayIndex:null,
   profile:{montblanc60:{version:1,started:date,days:{}}},
   data:{tasks:[],daily_logs:[]}};
 const plusDays=(d,n)=>{const x=new Date(d+'T12:00:00Z');x.setUTCDate(x.getUTCDate()+n);return x.toISOString().slice(0,10)};
 const ctx={
  state:()=>state,e:x=>String(x??'').replace(/[&<>"']/g,a=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[a])),
  num:x=>Number(x)||0,today:()=>current,plusDays,deltaDays:(a,b)=>Math.round((Date.parse(b)-Date.parse(a))/86400000),ruDate:x=>x,
  money:x=>String(x),taskIsDone:x=>!!x.completed,monthIncome:()=>0,currentDebt:()=>0,
  legacy:{INCOME_STEPS:Array.from({length:60},(_,i)=>'Запусти коммерческую проверку №'+(i+1))},
  saveProfile:async p=>(state.profile=p),
  saveRecord:async(table,row)=>{const i=state.data[table].findIndex(x=>x.log_date===row.log_date);if(i>=0)state.data[table][i]={...state.data[table][i],...row};else state.data[table].push(row)}
 };
 const m=window.MONTBLANCCHALLENGE.create(ctx);
 return {m,state,date:d=>current=d,plusDays};
}
const form=(m,i,id)=>({day:String(i),track:id,evidence:'Я полностью выполнил практику и могу указать конкретный результат, который получил.',minutes:String(m.minimum(id,i)),...(id==='sport'?{workout_type:i%7===6?'восстановление':'теннис'}:{})});

test('all 60 days contain the six genuinely substantive required blocks',()=>{
 const {m}=make();
 for(let i=0;i<60;i++){
  const ts=m.tasks(i);
  assert.equal(ts.length,6);
  assert.deepEqual(Array.from(ts,t=>t.id),['focus','english','sport','presence','learning','diary']);
  assert.equal(m.minimum('english',i),60);
  assert.ok(m.minutes('english',i)>=90);
  assert.ok(m.minimum('sport',i)>=20);
  assert.ok(m.minimum('focus',i)>=40);
  assert.ok(m.minimum('presence',i)>=12);
  assert.ok(m.tasks(i).every(t=>t.detail.length>80));
 }
});
test('current day opens, future day locked and old profile preserved on opt-in',async()=>{
 const {m,state}=make();
 assert.equal(m.has(),false);
 await m.start();
 assert.equal(m.has(),true);
 assert.equal(state.profile.montblanc60.started,'2026-11-21');
 assert.equal(m.frontier(),0);
 assert.equal(m.canView(0),true);
 assert.equal(m.canView(1),false);
 assert.match(m.program(),/Закрытый день 2/);
});
test('short false check-ins cannot unlock tasks',async()=>{
 const {m}=make();await m.start();
 await assert.rejects(()=>m.recordProof({...form(m,0,'english'),minutes:'10'}),/от 60 минут/);
 await assert.rejects(()=>m.recordProof({...form(m,0,'focus'),evidence:'готово'}),/20 символов/);
 await assert.rejects(()=>m.recordProof({...form(m,0,'sport'),workout_type:'восстановление'}),/выбери тренировку/);
 assert.equal(m.frontier(),0);
});
test('only all six real tasks unlock tomorrow, not the same calendar day',async()=>{
 const {m,state,date,plusDays}=make();await m.start();
 for(const id of ['focus','english','sport','presence','learning'])await m.recordProof(form(m,0,id));
 assert.equal(m.frontier(),0);
 assert.equal(m.canView(1),false);
 Object.assign(state.data.daily_logs.find(x=>x.log_date==='2026-11-21'),{reflection_done:true,thoughts:'День был насыщенный, но спокойный',win_of_day:'Урок и реальная тренировка'});
 await m.completeDiary('2026-11-21');
 assert.equal(m.frontier(),1);
 assert.equal(m.ready(),false);
 assert.equal(m.canView(1),false);
 date(plusDays('2026-11-21',1));
 assert.equal(m.canView(1),true);
 assert.equal(m.ready(),true);
});
test('diary requires a written story and a real result',async()=>{
 const {m,state}=make();await m.start();
 state.data.daily_logs.push({log_date:'2026-11-21',reflection_done:true,thoughts:'',win_of_day:'result'});
 await m.completeDiary('2026-11-21');
 assert.equal(m.get().days.length,0);
 state.data.daily_logs[0].thoughts='Сегодня чувствовал уверенность после разговоров';
 state.data.daily_logs[0].win_of_day='Выполнил важное действие';
 await m.completeDiary('2026-11-21');
 assert.ok(m.get().days[0].proofs.diary);
});
test('seventh day is recovery practice with a meaningful minimum',async()=>{
 const {m,state,date,plusDays}=make();await m.start();
 for(let i=0;i<6;i++){
  const d=plusDays('2026-11-21',i);date(d);
  for(const t of m.tasks(i).filter(x=>x.id!=='diary'))await m.recordProof(form(m,i,t.id));
  Object.assign(state.data.daily_logs.find(x=>x.log_date===d),{reflection_done:true,thoughts:'Записал мысли и самочувствие после тренировок',win_of_day:'Я завершил важные практики'});
  await m.completeDiary(d);
 }
 date(plusDays('2026-11-21',6));
 assert.equal(m.frontier(),6);
 assert.equal(m.minimum('sport',6),20);
 await assert.rejects(()=>m.recordProof({...form(m,6,'sport'),workout_type:'теннис'}),/восстановительная/);
 await m.recordProof(form(m,6,'sport'));
 assert.equal(m.get().days[6].proofs.sport.type,'восстановление');
});

test('full sixty-day route is completable with one calendar day per stage',async()=>{
 const {m,state,date,plusDays}=make();await m.start();
 for(let i=0;i<60;i++){
  const d=plusDays('2026-11-21',i);date(d);
  for(const t of m.tasks(i).filter(x=>x.id!=='diary'))await m.recordProof(form(m,i,t.id));
  Object.assign(state.data.daily_logs.find(x=>x.log_date===d),{reflection_done:true,thoughts:'Сегодня было сложно и интересно, но я справился',win_of_day:'Практики и тренировка выполнены',evening_energy:Math.min(10,5+i/20),m60_confidence:Math.min(10,5+i/25)});
  await m.completeDiary(d);
  assert.equal(m.frontier(),i+1,'finished day '+(i+1));
  if(i<59)assert.equal(m.ready(),false,'cannot skip same-day gate');
 }
 assert.equal(m.frontier(),60);
 assert.equal(m.currentStreak(),60);
 assert.match(m.program(),/Вершина достигнута/);
 assert.match(m.progress(),/60 из 60 дней/);
});
test('private notes are excluded from aggregate report and opt-in to full version',async()=>{
 const {m,state}=make();await m.start();
 state.data.daily_logs.push({log_date:'2026-11-21',reflection_done:true,thoughts:'VERY_PRIVATE_DAY_STORY',win_of_day:'Completed one specific action'});
 await m.completeDiary('2026-11-21');
 assert.ok(!m.reportPrompt(false).includes('VERY_PRIVATE_DAY_STORY'));
 assert.ok(m.reportPrompt(true).includes('VERY_PRIVATE_DAY_STORY'));
});
