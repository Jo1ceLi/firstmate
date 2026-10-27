import {readFileSync, writeFileSync} from 'node:fs';
import {McpSession, gate} from '../bin/fm-t3-mcp.mjs';
const c=JSON.parse(readFileSync(process.argv[2]));
const s=new McpSession(c.origin,c.access_token);
try {
  const g=await gate(s,c);
  const tools=await s.rpc('tools/list',{});
  const cap=await s.call('orchestrator_capabilities',{});
  writeFileSync(process.argv[3],JSON.stringify({gate:g,tools,cap},null,2));
  console.log(JSON.stringify({gate:g,cap}));
} finally {await s.close();}
