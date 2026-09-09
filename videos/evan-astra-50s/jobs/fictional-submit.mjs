import fs from 'node:fs';
const key=process.env.EVAN_DONA_KEY;
if(!key) throw Error('EVAN_DONA_KEY required');
const stem='jobs/fictional-01';
if(fs.existsSync(stem+'-attempt.json')) throw Error('Already attempted. Inspect response/list before retrying.');
const prompt=fs.readFileSync(stem+'.txt','utf8');
const body={model:'AP Seedance-2.5 标准版',seconds:8,size:'1280x720',resolution:'720p',generate_audio:true,watermark:false,prompt};
fs.writeFileSync(stem+'-attempt.json',JSON.stringify({started:new Date().toISOString(),state:'submitted_or_unknown',...body},null,2));
try {
const r=await fetch('https://www.donaapi.com/v1/videos',{method:'POST',headers:{Authorization:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(600000)});
const raw=await r.text();fs.writeFileSync(stem+'-response.json',raw);console.log(r.status,raw);
}catch(e){console.log('UNKNOWN; recover by listing tasks, do not duplicate:',e.message);process.exitCode=1;}
