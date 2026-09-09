import fs from 'node:fs';
const key=process.env.EVAN_DONA_KEY;if(!key)throw Error('EVAN_DONA_KEY required');
const version=process.env.EVAN_ATTEMPT_VERSION||'v14';
if(!/^v\d+$/.test(version))throw Error('Invalid attempt version');
const stem='jobs/fictional-02-'+version;
if(fs.existsSync(stem+'-attempt.json'))throw Error('Already attempted; inspect before retrying.');
const imageMode=process.env.EVAN_REFERENCE_MODE==='image';
const prompt=(imageMode?'@Image1':'@Video1')+' 的虚构男主是本镜头唯一的人物身份与场景参考。保持其面部结构、发型、体型和服装一致。\n'+fs.readFileSync('jobs/fictional-02.txt','utf8').replaceAll('参考视频',imageMode?'参考图片':'参考视频');
const reference=imageMode?{type:'image_url',role:'reference_image',image_url:{url:'data:image/jpeg;base64,'+fs.readFileSync('jobs/fictional-01-reference.jpg').toString('base64')}}:{type:'video_url',role:'reference_video',video_url:{url:'data:video/mp4;base64,'+fs.readFileSync('assets/video/fictional-01.mp4').toString('base64')}};
const body={model:process.env.EVAN_DONA_MODEL||'seedance-test2',seconds:'6',size:'1280x720',resolution:'720p',generate_audio:true,watermark:false,prompt,content:[{type:'text',text:prompt},reference]};
const dedicated=process.env.EVAN_API_FORMAT==='dedicated';
const endpoint=dedicated?'https://www.donaapi.com/v1/video/generations':'https://www.donaapi.com/v1/videos';
const payload=dedicated?{model:body.model,prompt,duration:6,width:1280,height:720,image:reference.image_url?.url}:body;
fs.writeFileSync(stem+'-attempt.json',JSON.stringify({started:new Date().toISOString(),state:'submitted_or_unknown',endpoint,reference:imageMode?'jobs/fictional-01-reference.jpg':'assets/video/fictional-01.mp4',model:body.model,seconds:6,size:body.size,resolution:body.resolution,prompt},null,2));
try{const r=await fetch(endpoint,{method:'POST',headers:{Authorization:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(600000)});const raw=await r.text();fs.writeFileSync(stem+'-response.json',raw);console.log(r.status,raw)}catch(e){console.log('UNKNOWN; query task list before retrying',e.message);process.exitCode=1}
