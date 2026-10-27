import {readFileSync} from 'node:fs';
import {McpSession,gate} from '../bin/fm-t3-mcp.mjs';
const c=JSON.parse(readFileSync(process.argv[2]));
const s=new McpSession(c.origin,c.access_token);
try {
 const g=await gate(s,c);
 console.log(JSON.stringify({serverVersion:g.serverVersion,toolFamilies:g.toolFamilies}));
 try {
  await s.call('t3_thread_configure',{threadId:process.argv[3]});
  throw new Error('old write-only tool unexpectedly accepted a read');
 } catch(e) {
  if(!e.message.includes('modelSelection'))throw e;
  console.log(JSON.stringify({attempt:'t3_thread_configure with only threadId on old T3',expectedRefusal:e.message}));
 }
 console.log(JSON.stringify({dedicatedRead:await s.call('t3_thread_configuration',{threadId:process.argv[3]})}));
} finally {await s.close();}
