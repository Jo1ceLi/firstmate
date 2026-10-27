import pathlib,subprocess,os,time,urllib.request,signal,json
r=pathlib.Path.cwd();s=r/'.t3-validation'
env={**os.environ,'HOME':str(s/'stable-home'),'T3CODE_HOME':str(s/'stable-data'),'T3CODE_TELEMETRY_ENABLED':'false','XDG_CONFIG_HOME':str(s/'stable-home/config'),'XDG_CACHE_HOME':str(s/'stable-home/cache'),'XDG_DATA_HOME':str(s/'stable-home/data')}
with open(s/'regression-server.log','w') as log:
 p=subprocess.Popen([str(s/'stable/t3-0.1.3-linux-x64/t3'),'serve','--base-dir',str(s/'stable-data'),'--host','127.0.0.1','--port','47233','--no-browser'],env=env,stdout=log,stderr=log,start_new_session=True)
 try:
  for _ in range(150):
   try:urllib.request.urlopen('http://127.0.0.1:47233',timeout=1);break
   except Exception:time.sleep(.2)
  for label,helper,expected in [('base 7da4c362',s/'base-helper.mjs',4),('target 753f5992',r/'bin/fm-t3-mcp.mjs',0)]:
   q=subprocess.run(['node',str(helper),'status','--token-file',str(s/'stable-token')],env=env,text=True,capture_output=True,timeout=60)
   print(json.dumps({'revision':label,'command':'status against real T3 0.1.3 stable','exit':q.returncode,'stdout':q.stdout,'stderr':q.stderr}),flush=True)
   assert q.returncode==expected
 finally:
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
