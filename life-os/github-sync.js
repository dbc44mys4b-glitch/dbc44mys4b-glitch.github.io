/* MONTBLANC GitHub private encrypted-vault backup client.
   The GitHub credential is supplied at runtime on the owner's iPhone.
   Never embed a token in a static Pages file, URL or a commit.
   GitHub is used as an off-device encrypted backup store, not a public diary. */
const API='https://api.github.com';
const GH_HEADERS={Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2026-03-10'};
export const VAULT_PATH='backups/montblanc-vault.json';
export function parseRepo(input){const repo=String(input||'').trim();if(!/^[\w.-]+\/[\w.-]+$/.test(repo)||repo.length>180||repo.includes('..'))throw new Error('Формат репозитория: владелец/название');return repo}
export function apiUrl(repo,path=''){return `${API}/repos/${parseRepo(repo)}${path}`}
async function request(token,url,method='GET',body){if(!/^github_pat_[\w-]{10,}$|^gh[pousr]_[\w-]{10,}$/.test(String(token||'')))throw new Error('Нужен действующий GitHub token с доступом только к приватному репозиторию');let result;try{result=await fetch(url,{method,headers:{...GH_HEADERS,Authorization:'Bearer '+token,...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{}) ,cache:'no-store',credentials:'omit'})}catch{throw new Error('Нет соединения с GitHub. Данные остались на iPhone.')}
const txt=await result.text();let json;try{json=txt?JSON.parse(txt):{}}catch{json={}};
if(!result.ok&&result.status!==404){if(result.status===401||result.status===403)throw new Error('GitHub отказал в доступе: проверь токен, его срок и права Contents: Read and write.');if(result.status===409||result.status===422)throw new Error('Конфликт версии в GitHub. Данные на iPhone не удалены.');throw new Error('Ошибка GitHub HTTP '+result.status)}
return {status:result.status,data:json}
}
export async function verifyPrivateRepo(repo,token){const r=await request(token,apiUrl(repo));if(r.status===404)throw new Error('Приватный репозиторий не найден или токен не даёт доступ');if(r.data.private!==true)throw new Error('Репозиторий публичный! Создай отдельный PRIVATE репозиторий для записей.');if(r.data.permissions&&r.data.permissions.push===false)throw new Error('У токена нет права записи в репозиторий');return r.data}
const toB64=text=>{const bytes=new TextEncoder().encode(text);let s='';for(let i=0;i<bytes.length;i+=16384)s+=String.fromCharCode(...bytes.subarray(i,i+16384));return btoa(s)};
const fromB64=text=>{let binary=atob(text.replace(/\s/g,''));const bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));return new TextDecoder().decode(bytes)};
export async function readRemoteVault(repo,token){const r=await request(token,apiUrl(repo,'/contents/'+VAULT_PATH));if(r.status===404)return {exists:false,sha:'',value:null};const item=r.data;if(item.type!=='file'||!item.sha||item.encoding!=='base64'||typeof item.content!=='string')throw new Error('GitHub вернул неожиданный формат архива');let value;try{value=JSON.parse(fromB64(item.content))}catch{throw new Error('Удалённый файл повреждён или имеет неизвестный формат')}
if(value?.format!=='life-os-v3-encrypted'||value.version!==3||!value.ciphertext||!value.salt||!value.iv)throw new Error('Удалённый архив не похож на зашифрованный дневник');return {exists:true,sha:item.sha,value}}
export async function writeRemoteVault(repo,token,vault,sha){if(vault?.format!=='life-os-v3-encrypted'||vault.version!==3||typeof vault.ciphertext!=='string')throw new Error('Нельзя загружать незашифрованные данные');const body={message:'MONTBLANC encrypted backup · '+new Date().toISOString(),content:toB64(JSON.stringify(vault)),...(sha?{sha}:{})};const r=await request(token,apiUrl(repo,'/contents/'+VAULT_PATH),'PUT',body);if(r.status!==200&&r.status!==201)throw new Error('GitHub не подтвердил сохранение архива');return r.data.content?.sha||''}
