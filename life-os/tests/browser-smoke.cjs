/* MONTBLANC — real mobile-browser smoke test, without personal data. */
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');

const root=path.resolve(__dirname,'..','..');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.webmanifest':'application/manifest+json','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp'};
const server=http.createServer((req,res)=>{
 const raw=decodeURIComponent((req.url||'/').split('?')[0]);
 const full=path.resolve(root,'.'+raw,raw.endsWith('/')?'index.html':'');
 if(!full.startsWith(root+path.sep)){res.writeHead(403).end('Denied');return}
 fs.readFile(full,(err,data)=>{if(err){res.writeHead(404).end('Not found');return}res.writeHead(200,{'Content-Type':types[path.extname(full)]||'application/octet-stream','Cache-Control':'no-store'});res.end(data)});
});

(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const url='http://127.0.0.1:'+server.address().port+'/life-os/';
 let browser, page;
 try {
  browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
  const failures=[];
  page.on('pageerror',e=>failures.push(String(e)));
  await page.goto(url,{waitUntil:'domcontentloaded'});
  await page.locator('[data-action="demo"]').waitFor({timeout:20000});
  await page.locator('[data-action="demo"]').click();
  await page.locator('.m60-title h1').getByText('Сегодня').waitFor();
  assert.ok((await page.locator('.c60-upgrade').innerText()).includes('60 дней полной прокачки'),'Upgrade must be visible on home');
  await page.locator('.mb7-dock button[data-page="mission60"]').click();
  await page.locator('[data-action="c60-start"]').click();
  await page.locator('.mb7-dock button[data-page="mission60"]').click();
  await page.locator('.c60-root .c60-practice').first().waitFor();
  assert.equal(await page.locator('.c60-day[data-index="1"]').isDisabled(),true,'Day 2 must start locked');
  const cards=page.locator('.c60-practice');
  assert.equal(await cards.count(),6,'Six actual practices must be displayed');
  assert.ok((await page.locator('.c60-lesson').innerText()).includes('Программа полноценного урока'));
  const work=['focus','english','sport','presence','learning'];
  for(const id of work){
   await page.locator('[data-action="c60-proof-open"][data-id="'+id+'"]').click();
   const form=page.locator('form[data-form="c60-proof"]');
   await form.locator('input[name="minutes"]').fill(id==='english'?'90':id==='sport'?'45':id==='presence'?'20':id==='learning'?'22':'50');
   await form.locator('textarea[name="evidence"]').fill('Сегодня выполнил это полноценное задание и записал конкретный результат практики: '+id);
   if(id==='sport')await form.locator('select[name="workout_type"]').selectOption('теннис');
   await form.locator('button[type="submit"]').click();
   await page.locator('.c60-modal').waitFor({state:'detached'});
  }
  assert.equal(await page.locator('.c60-day[data-index="1"]').isDisabled(),true,'Cannot unlock day 2 without journal');
  await page.locator('.mb7-dock button[data-page="reflection"]').click();
  await page.locator('textarea[name="thoughts"]').fill('Сегодня чувствовал энергию, немного волновался, но тренировку и английский прошёл полностью.');
  await page.locator('input[name="win_of_day"]').fill('Завершил урок, теннис и практику общения');
  await page.locator('select[name="m60_confidence"]').selectOption('7');
  await page.locator('select[name="evening_energy"]').selectOption('6');
  await page.locator('input[name="tomorrow_one"]').fill('Разобрать ошибки вчерашнего урока');
  const invalid=await page.locator('form[data-form="mission-journal"]').evaluate(form=>Array.from(form.elements).filter(x=>typeof x.checkValidity==='function'&&!x.checkValidity()).map(x=>({name:x.name,value:x.value,message:x.validationMessage})));
  assert.deepEqual(invalid,[],'Compact diary must accept reasonable written entries');
  await page.locator('.m60-submit').click();
  await page.locator('.mb7-dock button[data-page="progress"]').click();
  await page.locator('[data-action="c60-copy-report"][data-mode="numbers"]').waitFor();
  assert.ok((await page.locator('.m60-page').innerText()).includes('Изменения по дневнику'),'Progress must show actual observations');
  await page.locator('.mb7-dock button[data-page="reflection"]').click();
  assert.equal(await page.locator('select[name="m60_confidence"]').inputValue(),'7','Saved diary must survive tab navigation');
  assert.ok((await page.locator('textarea[name="thoughts"]').inputValue()).includes('немного волновался'));
  await page.locator('.mb7-dock button[data-page="mission60"]').click();
  assert.equal(await page.locator('.c60-day[data-index="1"]').isDisabled(),true,'Day 2 must wait until next calendar day');
  assert.ok((await page.locator('.c60-root').innerText()).includes('Следующий день станет доступен завтра'));
  await page.locator('.mb7-dock button[data-page="dashboard"]').click();
  assert.ok((await page.locator('.m60-page').innerText()).includes('60-ДНЕВНЫЙ ВЫЗОВ'));
  const size=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
  assert.ok(size.scroll<=size.width+2,'Unexpected horizontal overflow on iPhone width: '+JSON.stringify(size));
  assert.equal(failures.length,0,'Uncaught browser errors: '+failures.join('\n'));
  console.log('PASS browser: full 6-track challenge, proof entry, day gating, compact diary, analytics and mobile viewport');
 } catch(e) {
  if(page)await page.screenshot({path:'/tmp/montblanc-browser-failure.png',fullPage:true}).catch(()=>{});
  throw e;
 } finally {
  if(browser)await browser.close();
  server.close();
 }
})().catch(err=>{console.error(err);process.exitCode=1});
