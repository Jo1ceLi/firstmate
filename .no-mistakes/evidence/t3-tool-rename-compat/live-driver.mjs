import http from 'node:http';
import fs from 'node:fs';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const exec=promisify(execFile);
const [label,port,tokenfile]=process.argv.slice(2);
const credential=JSON.parse(fs.readFileSync(tokenfile));
let removed=[];const calls=[];
const server=http.createServer(async(req,res)=>{try{
 const chunks=[];for await (const x of req)chunks.push(x);const body=Buffer.concat(chunks);const rpc=JSON.parse(body.toString());
 if(rpc.method==='tools/call')calls.push(rpc.params);
 const headers={...req.headers};delete headers.host;delete headers.connection;
 const upstream=await fetch(`http://127.0.0.1:${port}${req.url}`,{method:req.method,headers,body});
 let result=await upstream.text();
 if(rpc.method==='tools/list'&&removed.length){const d=JSON.parse(result);d.result.tools=d.result.tools.filter(t=>!removed.includes(t.name));result=JSON.stringify(d);}
 res.writeHead(upstream.status,{'content-type':upstream.headers.get('content-type')||'application/json',...(upstream.headers.get('mcp-session-id')?{'mcp-session-id':upstream.headers.get('mcp-session-id')}: {})});res.end(result);
 }catch(e){res.writeHead(500);res.end(e.message);}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const proxyToken=`.test-t3-lab/${label}-proxy-token`;
fs.writeFileSync(proxyToken,JSON.stringify({...credential,origin:`http://127.0.0.1:${server.address().port}`}),{mode:0o600});
async function cli(...args){let out;try{out=await exec('node',['bin/fm-t3-mcp.mjs',...args,'--token-file',proxyToken],{timeout:30000});}catch(e){out=e;}console.log(JSON.stringify({command:args,exitCode:out.code||0,stdout:out.stdout?.trim(),stderr:out.stderr?.trim()}));return JSON.parse(out.stdout);}
try{
 console.log(`REAL T3 ${label}: unmodified forwarding proxy records tool calls; fault scenario removes advertised tools only.`);
 await cli('status');
 const p=await cli('project-ensure','--root',`${process.cwd()}/.test-t3-lab/project`);
 const t=await cli('launch','--project',p.projectId,'--title',`rename-${label}`,'--model-selection','{"instanceId":"codex","model":"gpt-6.1-sol"}');
 if(!t.ok)throw new Error('launch failed');
 await cli('requests','--thread',t.threadId);
 fs.writeFileSync('.test-t3-lab/answers.json','{"q1":"test"}');
 const response=await cli('respond','--thread',t.threadId,'--request','not-a-real-request','--answers-file','.test-t3-lab/answers.json');
 if(response.ok)throw new Error('nonexistent request unexpectedly accepted');
 await cli('archive','--thread',t.threadId);
 removed=['t3_pending_request','t3_pending_request_respond'];
 const before=calls.length;
 const refused=await cli('launch','--project',p.projectId,'--title','must-not-launch','--model-selection','{"instanceId":"codex","model":"gpt-6.1-sol"}');
 if(calls.length!==before)throw new Error('incomplete capability reached a tool call');
 if(refused.error?.code!=='capability_gate')throw new Error('incomplete capability unexpectedly accepted');
 removed=['t3_thread_configuration','t3_thread_configure'];
 const noConfig=await cli('status');
 if(noConfig.error?.code!=='capability_gate')throw new Error('missing configuration capability accepted');
 console.log(JSON.stringify({recordedCalls:calls},null,2));
 const configs=calls.filter(c=>['t3_thread_configuration','t3_thread_configure'].includes(c.name));
 if(configs.length!==1||JSON.stringify(Object.keys(configs[0].arguments).sort())!=='["threadId"]')throw new Error('configuration was not a read-only call');
 console.log('Observed: launch verified binding; configuration read supplied only threadId; absent question refused; archive confirmed; incomplete capability refused.');
}finally{await new Promise(r=>server.close(r));}
