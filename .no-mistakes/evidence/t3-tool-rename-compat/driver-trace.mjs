import {appendFileSync} from 'node:fs';
const original=globalThis.fetch;
globalThis.fetch=async function(url,init){
 if(process.env.T3_TRACE && init?.body){
   try {const p=JSON.parse(init.body);if(p.method==='tools/call')appendFileSync(process.env.T3_TRACE,JSON.stringify(p.params)+'\n');}catch{}
 }
 return original(url,init);
};
