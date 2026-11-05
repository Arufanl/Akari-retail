// Local integration. Never prints credentials or upstream response bodies.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const home='C:/Users/Akari/AppData/Local/hermes';
const data='C:/Users/Akari/AppData/Roaming/9router';
const api=require('C:/Users/Akari/AppData/Roaming/npm/node_modules/9router/src/cli/api/client.js');
api.configure({host:'127.0.0.1',port:20128});
const models=['nvidia/nvidia/nemotron-3-ultra-550b-a55b','oc/mimo-v2.6-flash-free'];
const token=()=>crypto.createHash('sha256').update(fs.readFileSync(path.join(data,'machine-id'),'utf8').trim()+'9r-cli-auth'+fs.readFileSync(path.join(data,'auth/cli-secret'),'utf8').trim()).digest('hex').slice(0,16);
async function admin(route,method,body){const r=await fetch('http://127.0.0.1:20128'+route,{method,headers:{'Content-Type':'application/json','x-9r-cli-token':token()},body:JSON.stringify(body),signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error('Local admin HTTP '+r.status);return r.json();}
(async()=>{
 const combos=await api.getCombos();if(!combos.success)throw Error('Router unavailable');
 const stamp=new Date().toISOString().replace(/[:.]/g,'-');
 const backup=path.join(home,'backups','pre-9router-connect-'+stamp);fs.mkdirSync(backup,{recursive:true});
 for(const name of ['config.yaml','.env','auth.json'])if(fs.existsSync(path.join(home,name)))fs.copyFileSync(path.join(home,name),path.join(backup,name));
 const routerBackup=path.join(data+'-backups','pre-hermes-connect-'+stamp);fs.mkdirSync(routerBackup,{recursive:true});fs.cpSync(data,path.join(routerBackup,'9router'),{recursive:true});
 const py='import sqlite3,sys; a=sqlite3.connect("file:"+sys.argv[1]+"?mode=ro",uri=True); b=sqlite3.connect(sys.argv[2]); a.backup(b); assert b.execute("PRAGMA integrity_check").fetchone()[0]=="ok"; b.close(); a.close()';
 const b=cp.spawnSync('C:/Python314/python.exe',['-',path.join(data,'db/data.sqlite'),path.join(routerBackup,'consistent-data.sqlite')],{input:py,encoding:'utf8',windowsHide:true});if(b.status!==0)throw Error('Backup failed; no configuration changed');
 console.log('HERMES_BACKUP='+backup);console.log('ROUTER_BACKUP='+routerBackup);
 let combo=combos.data.combos.find(c=>c.name==='akari');
 if(!combo){const r=await api.createCombo({name:'akari',models});if(!r.success)throw Error('Combo creation failed');combo=r.data;}
 else {const r=await api.updateCombo(combo.id,{models});if(!r.success)throw Error('Combo update failed');}
 const keys=await api.getApiKeys();if(!keys.success)throw Error('Key lookup failed');
 let key=keys.data.keys.find(k=>k.name==='Hermes Akari'&&k.isActive!==false);
 if(!key){const r=await api.createApiKey('Hermes Akari');if(!r.success)throw Error('Key creation failed');key=r.data.key && typeof r.data.key==='object'?r.data.key:r.data;}
 if(!key.key||!key.id)throw Error('Unexpected key metadata; credentials suppressed');
 await admin('/api/keys/'+key.id,'PUT',{access:{restricted:true,allow:['akari',...models]}});
 const envPath=path.join(home,'.env');let env=fs.readFileSync(envPath,'utf8');const line='AKARI_9ROUTER_API_KEY='+key.key;
 env=/^AKARI_9ROUTER_API_KEY=.*$/m.test(env)?env.replace(/^AKARI_9ROUTER_API_KEY=.*$/m,line):env.replace(/\s*$/,'')+'\n'+line+'\n';
 fs.writeFileSync(envPath,env);
 const cfgPath=path.join(home,'config.yaml');let cfg=fs.readFileSync(cfgPath,'utf8');
 const block='model:\n  default: "akari"\n  provider: "custom"\n  base_url: "http://127.0.0.1:20128/v1"\n  api_mode: "chat_completions"\n  key_env: "AKARI_9ROUTER_API_KEY"\n';
 if(!/^model:\r?\n/m.test(cfg))throw Error('Model block not found');
 cfg=cfg.replace(/^model:\r?\n(?:[ \t].*\r?\n|\r?\n)*/m,block);fs.writeFileSync(cfgPath,cfg);
 console.log('CONFIGURED=custom/akari/chat_completions');
 const r=await fetch('http://127.0.0.1:20128/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+key.key},body:JSON.stringify({model:'akari',messages:[{role:'user',content:'Reply only OK.'}],max_tokens:128,stream:false}),signal:AbortSignal.timeout(120000)});
 const result=await r.json();console.log('MODEL_TEST_HTTP='+r.status);console.log('MODEL_TEST_HAS_REPLY='+Boolean(result.choices?.[0]?.message?.content));
 if(!r.ok)process.exitCode=2;
})().catch(e=>{console.error('INTEGRATION_ERROR='+((e.message||'').match(/^[A-Za-z0-9 /;_=.-]+$/)?e.message:'Details suppressed'));process.exitCode=1});
