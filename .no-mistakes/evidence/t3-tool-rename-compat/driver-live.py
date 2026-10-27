import subprocess, pathlib, os, time, json, urllib.request, signal, sqlite3, datetime
root=pathlib.Path.cwd()
scratch=root/'.t3-validation'
evidence=pathlib.Path('/home/hermesadmin/.no-mistakes/evidence/01M5YT7QRSMYMKZZ1FNQEV2W8C')
name,version,port=__import__('sys').argv[1:]
folder=scratch/name/f't3-{version}-linux-x64'
print('bundle files:',[x.name for x in folder.iterdir()],flush=True)
cli=folder/'t3'
home=scratch/(name+'-home'); home.mkdir(exist_ok=True)
base=scratch/(name+'-data')
env={**os.environ,'HOME':str(home),'T3CODE_HOME':str(base),'T3CODE_TELEMETRY_ENABLED':'false','XDG_CONFIG_HOME':str(home/'config'),'XDG_CACHE_HOME':str(home/'cache'),'XDG_DATA_HOME':str(home/'data')}
env['NODE_OPTIONS']='--import='+str(scratch/'trace.mjs')
env['T3_TRACE']=str(evidence/(name+'-tool-calls.jsonl'))
log=open(scratch/(name+'-server.log'),'w')
proc=subprocess.Popen([str(cli),'serve','--base-dir',str(base),'--host','127.0.0.1','--port',port,'--no-browser'],env=env,stdout=log,stderr=log,start_new_session=True)
try:
  for _ in range(150):
    if proc.poll() is not None: raise RuntimeError('server exited '+str(proc.returncode))
    try:
      urllib.request.urlopen('http://127.0.0.1:'+port,timeout=1);break
    except Exception: time.sleep(.2)
  else: raise RuntimeError('server not ready')
  cred=scratch/(name+'-token')
  def run(args):
    p=subprocess.run(['node',str(root/'bin/fm-t3-mcp.mjs'),*args,'--token-file',str(cred)],env=env,text=True,capture_output=True,timeout=80)
    print(json.dumps({'command':args,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}),flush=True)
    return p
  run(['login','--access','full-access','--url','http://127.0.0.1:'+port,'--t3',str(cli),'--base-dir',str(base)])
  run(['status'])
  p=subprocess.run(['node',str(scratch/'inspect.mjs'),str(cred),str(scratch/(name+'-inspect.json'))],env=env,text=True,capture_output=True,timeout=80)
  print(p.stdout,p.stderr,flush=True)
  project=scratch/(name+'-project');project.mkdir(exist_ok=True)
  subprocess.run(['git','init',str(project)],capture_output=True,check=True)
  result=run(['project-ensure','--root',str(project)])
  pid=json.loads(result.stdout).get('projectId')
  selection=json.dumps({'instanceId':'codex','model':'gpt-5.4','options':[]})
  result=run(['launch','--project',pid,'--title','rename compatibility validation','--model-selection',selection])
  obj=json.loads(result.stdout)
  if obj.get('threadId'):
    thread=obj['threadId']
    run(['requests','--thread',thread])
    c=sqlite3.connect(base/'userdata/statev2.sqlite')
    now=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
    request='validation-question-'+thread;node='validation-question-node-'+thread;item='validation-question-item-'+thread
    req={'id':request,'nodeId':node,'providerTurnId':None,'nativeRequestRef':None,'kind':'user_input','status':'pending','responseCapability':{'type':'message'},'createdAt':now,'resolvedAt':None}
    n={'id':node,'threadId':thread,'runId':None,'parentNodeId':None,'rootNodeId':node,'kind':'user_input_request','status':'waiting','countsForRun':False,'providerThreadId':None,'providerTurnId':None,'nativeItemRef':None,'runtimeRequestId':request,'checkpointScopeId':None,'startedAt':now,'completedAt':None}
    ti={'id':item,'threadId':thread,'runId':None,'nodeId':node,'providerThreadId':None,'providerTurnId':None,'nativeItemRef':None,'parentItemId':None,'ordinal':1,'status':'pending','title':None,'startedAt':now,'completedAt':None,'updatedAt':now,'type':'user_input_request','requestId':request,'questions':[{'id':'q1','header':'Pick','question':'Which compatibility path?','options':[{'label':'both','description':'Keep old and new servers working'}]}]}
    c.execute('INSERT INTO orchestration_v2_projection_runtime_requests VALUES (?,?,?,?,?,?,?,?,?)',(request,thread,node,None,'user_input','pending',now,None,json.dumps(req)))
    c.execute('INSERT INTO orchestration_v2_projection_nodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(node,thread,None,None,node,'user_input_request','waiting',None,None,request,None,now,None,json.dumps(n)))
    c.execute('INSERT INTO orchestration_v2_projection_turn_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(item,thread,None,node,None,None,None,1,'user_input_request','pending',now,json.dumps(ti)))
    c.commit()
    print('Seeded disposable T3 persisted request and turn-item dataset from published OrchestrationV2RuntimeRequest contract; no provider session or model was run.',flush=True)
    run(['requests','--thread',thread])
    answers=scratch/(name+'-answers.json');answers.write_text('{"q1":"both"}')
    run(['respond','--thread',thread,'--request',request,'--answers-file',str(answers)])
    print('Persisted request after respond: '+str(c.execute('SELECT status,payload_json FROM orchestration_v2_projection_runtime_requests WHERE runtime_request_id=?',(request,)).fetchone()),flush=True)
    run(['requests','--thread',thread])
    c.close()
    run(['archive','--thread',thread])
finally:
  os.killpg(proc.pid,signal.SIGTERM)
  try: proc.wait(timeout=10)
  except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  log.close()
