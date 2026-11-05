const fs=require('node:fs'),cp=require('node:child_process');
const home='C:/Users/Akari/AppData/Local/hermes';
const key=fs.readFileSync(home+'/.env','utf8').match(/^AKARI_9ROUTER_API_KEY=(.*)$/m)?.[1].trim();
(async()=>{
 for(const model of ['nvidia/nvidia/nemotron-3-ultra-550b-a55b']){
  const r=await fetch('http://127.0.0.1:20128/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+key},body:JSON.stringify({model,messages:[{role:'user',content:'Reply only OK.'}],max_tokens:128,stream:false}),signal:AbortSignal.timeout(60000)});
  const j=await r.json();const msg=JSON.stringify(j.error||{}).toLowerCase();
  console.log(JSON.stringify({model,status:r.status,reply:!!j.choices?.[0]?.message?.content,categories:['quota','rate','not found','no available','no active','no models','unauthorized','invalid','cooldown','exhausted','connection','api key','provider','combo'].filter(x=>msg.includes(x))}));
 }
 const p=cp.spawnSync(home+'/bin/hermes.cmd',['--version'],{shell:true,encoding:'utf8',windowsHide:true,timeout:30000});console.log('HERMES_CLI_EXIT='+p.status);console.log('HERMES_VERSION='+((p.stdout+p.stderr).match(/\b\d+\.\d+\.\d+\b/)||['unavailable'])[0]);
})().catch(()=>{console.error('Verification incomplete (details suppressed)');process.exitCode=1});
