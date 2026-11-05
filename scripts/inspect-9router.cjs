const api = require('C:/Users/Akari/AppData/Roaming/npm/node_modules/9router/src/cli/api/client.js');
api.configure({host:'127.0.0.1',port:20128});
(async()=>{
 for (const name of ['getCombos','getAvailableModels']) {
  const r=await api[name]();
  if (!r.success) {console.log(name+': unavailable'); continue;}
  console.log(name+': '+JSON.stringify(r.data));
 }
})().catch(()=>{console.error('Inspection failed (details suppressed)');process.exitCode=1});
