import fs from 'node:fs';
const key=process.env.EVAN_DONA_KEY;
if(!key)throw Error('EVAN_DONA_KEY required');
const stem=process.argv[2]||'fictional-01';
if(!/^fictional-\d{2}(?:-v\d+)?$/.test(stem))throw Error('Invalid shot name');
const task=JSON.parse(fs.readFileSync('jobs/'+stem+'-response.json','utf8'));
const id=task.id||task.task_id;
if(!id)throw Error('No task ID; inspect response before proceeding');
const r=await fetch('https://www.donaapi.com/v1/videos/'+encodeURIComponent(id),{headers:{Authorization:'Bearer '+key},signal:AbortSignal.timeout(30000)});
const raw=await r.text();console.log(r.status,raw);
if(!r.ok)process.exit(1);
fs.writeFileSync('jobs/'+stem+'-status.json',raw);
const status=JSON.parse(raw);
if(status.status==='completed'){
const file='assets/video/'+stem+'.mp4';
if(fs.existsSync(file)){console.log('Already downloaded',file);process.exit(0);}
const media=await fetch('https://www.donaapi.com/v1/videos/'+encodeURIComponent(id)+'/content',{headers:{Authorization:'Bearer '+key},signal:AbortSignal.timeout(90000)});
if(!media.ok)throw Error('Download failed '+media.status);
const bytes=Buffer.from(await media.arrayBuffer());fs.writeFileSync(file,bytes);console.log('Downloaded',file,bytes.length);
}
