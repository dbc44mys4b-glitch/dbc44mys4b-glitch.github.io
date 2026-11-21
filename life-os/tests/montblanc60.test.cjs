'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'..','mission60.js'),'utf8');
function harness(start='2026-11-21',current='2026-11-21'){
 const window={};vm.runInNewContext(source,{window});
 const state={page:'dashboard',profile:{montblanc60:{version:1,started:start,pace:'steady',days:{}}},data:{daily_logs:[],tasks:[]}};
 const plusDays=(date,n)=>{const d=new Date(date+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10)};
 const ctx={state:()=>state,e:x=>String(x).replace(/[&<>"]/g,y=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[y])),
  num:x=>Number(x)||0,today:()=>current,plusDays,deltaDays:(a,b)=>Math.round((Date.parse(b)-Date.parse(a))/86400000),
  ruDate:x=>x,money:x=>String(x),taskIsDone:x=>x.status==='done'||!!x.completed,taskLabel:{},monthIncome:()=>0,currentDebt:()=>0,
  saveProfile:async p=>(state.profile=p),saveRecord:async(table,row)=>{const j=state.data[table].findIndex(x=>x.log_date===row.log_date);if(j>=0)state.data[table][j]=row;else state.data[table].push(row)},
  notify:()=>{},render:()=>{},scrollTop:()=>{},localKey:()=>true};
 return {module:window.MONTBLANC60.create(ctx),state,ctx};
}
test('60-day schedule contains exactly five core practices and sustainable budgets',()=>{
 const {module:m}=harness();
 for(let i=0;i<60;i++){
  const list=m.tasks(i),core=list.filter(x=>x.core);
  assert.equal(core.length,5,'day '+(i+1));
  const budget=list.reduce((n,x)=>n+x.minutes,0);
  assert.ok(budget<=67,'day '+(i+1)+' '+budget);
  assert.ok(budget>=30,'day '+(i+1)+' '+budget);
  assert.ok(list.every(x=>x.detail&&x.title));
 }
 assert.equal(m.stats().totalCore,300);
 assert.equal(m.tasks(0).reduce((n,x)=>n+x.minutes,0),67);
 assert.equal(m.tasks(6).reduce((n,x)=>n+x.minutes,0),30);
});
test('generic completed tasks do not automatically become a commercial practice',()=>{
 const {module:m,state}=harness();
 state.data.tasks.push({id:'task-1',task_date:'2026-11-21',category:'finance',completed:true});
 assert.equal(m.status('focus','2026-11-21').done,false);
 assert.equal(m.stats().personalDone,1);
 assert.equal(m.stats().coreDone,0);
});
test('one logged activity counts as one core practice, even with a manual check',()=>{
 const {module:m,state}=harness();
 state.data.daily_logs.push({log_date:'2026-11-21',focus_min:25,english_min:15,reflection_done:true});
 state.profile.montblanc60.days['2026-11-21']={checked:{focus:true,english:true}};
 const s=m.stats();
 assert.equal(s.coreDone,3);
 assert.equal(s.done,3);
 assert.equal(s.personalDone,0);
 assert.equal(s.journey,1);
});
test('a linked task counts as exactly one practice and remains a separate task metric',()=>{
 const {module:m,state}=harness();
 state.data.tasks.push({id:'linked',task_date:'2026-11-21',category:'finance',m60_action_id:'focus',status:'done'});
 assert.equal(m.status('focus','2026-11-21').done,true);
 assert.equal(m.stats().coreDone,1);
 assert.equal(m.stats().personalDone,1);
 assert.ok(!('combinedDone' in m.stats()));
});
test('changing just one day does not reset completed actions or all other days',async()=>{
 const {module:m,state}=harness();
 state.profile.montblanc60.days['2026-11-21']={checked:{focus:true}};
 await m.dayPace('gentle','2026-11-21');
 assert.equal(m.tasks(0).reduce((n,x)=>n+x.minutes,0),30);
 assert.equal(m.status('focus','2026-11-21').done,true);
 assert.equal(state.profile.montblanc60.days['2026-11-21'].checked.focus,true);
 assert.equal(m.tasks(1).reduce((n,x)=>n+x.minutes,0),67);
});
test('past days keep legacy task auto-credit after the upgrade',()=>{
 const {module:m,state}=harness('2026-11-18','2026-11-21');
 state.data.tasks.push({task_date:'2026-11-18',category:'finance',completed:true});
 assert.equal(m.status('focus','2026-11-18').done,true);
});
test('diary keeps evidence and confidence within the existing daily record',()=>{
 const {module:m}=harness();
 const row=m.journalRow({log_date:'2026-11-21',m60_confidence:'7',m60_presence_evidence:'I started a friendly conversation',m60_focus_evidence:'One real client replied'},{existing_legacy_key:'keep'},true);
 assert.equal(row.m60_confidence,7);
 assert.equal(row.m60_presence_evidence,'I started a friendly conversation');
 assert.equal(row.existing_legacy_key,'keep');
 assert.equal(row.reflection_done,true);
});
test('screens render and the AI handoff does not disclose free-text journal',()=>{
 const {module:m,state}=harness();
 state.data.daily_logs.push({log_date:'2026-11-21',thoughts:'HIGHLY_PRIVATE_PHRASE',evening_energy:6,m60_confidence:7});
 assert.ok(m.home().includes('PRESENCE'));
 assert.ok(m.program().includes('60 дней роста'));
 assert.ok(m.planner().includes('Мой план'));
 assert.ok(m.diary().includes('m60_presence_evidence'));
 assert.ok(m.progress().includes('РЕАЛЬНЫЕ ИЗМЕНЕНИЯ'));
 const prompt=m.coachPrompt();
 assert.ok(prompt.includes('average_confidence'));
 assert.ok(!prompt.includes('HIGHLY_PRIVATE_PHRASE'));
});
test('program finishes and future completion is not accepted',async()=>{
 const {module:m,state}=harness('2026-11-21','2027-01-25');
 assert.ok(m.home().includes('МАРШРУТ ЗАВЕРШЁН'));
 assert.ok(!m.home().includes('PRESENCE'));
 await m.dayPace('gentle','2027-01-26');
 assert.equal(Object.keys(state.profile.montblanc60.days).length,0);
});

test('gentle completed practices remain credited when the daily budget increases',async()=>{
 const {module:m,state}=harness();
 state.data.daily_logs.push({log_date:'2026-11-21',english_min:7,focus_min:12});
 await m.dayPace('gentle','2026-11-21');
 assert.equal(m.status('english','2026-11-21').done,true);
 assert.equal(m.status('focus','2026-11-21').done,true);
 await m.dayPace('steady','2026-11-21');
 assert.equal(m.status('english','2026-11-21').done,true);
 assert.equal(m.status('focus','2026-11-21').done,true);
 assert.equal(state.profile.montblanc60.days['2026-11-21'].checked.english,true);
});
