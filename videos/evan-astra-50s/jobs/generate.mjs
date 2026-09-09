import fs from 'node:fs';
const key=process.env.EVAN_DONA_KEY;
if(!key) throw new Error('EVAN_DONA_KEY required');
const n=process.argv[2]||'01';
const specs={
 '01':{image:'01-study.png',duration:8,prompt:'0–1秒，第三人称侧面中景，Evan坐在皮椅看右侧屏幕，自然呼吸。1–6秒他说中文：“Astra，看看今天女装什么款在爆，整理份报告。”6–8秒平静温柔女性助手画外音：“好，开始分析。”Evan轻微点头，镜头保持缓慢推近。'},
 '02':{image:'04-grinder.png',duration:6,prompt:'0–2秒第三人称侧面中远景，Evan把小杯中咖啡豆倒进磨豆机，豆子自然落下。2–4秒他放下小杯，按下磨豆按钮。4–6秒机器磨豆，他安静等待。固定镜头，背景屏幕仍然运行暗蓝界面，真实磨豆机声，无对白。'},
 '03':{image:'01-study.png',duration:8,prompt:'0–4秒第三人称侧面中景，Evan坐在椅子看屏幕，温柔女性助手画外音说：“报告好了，要从商品库里挑款吗？”4–8秒Evan轻轻点头说：“好，搭配、生成视频，再剪好。”镜头缓慢推近，口型自然。'},
 '04':{image:'02-coffee.png',duration:9,prompt:'0–3秒第三人称侧面中景，Evan手持细嘴壶缓慢画圈注水，细水流落入滤杯。3–6秒保持注水，水汽轻升，背景屏幕暗蓝色任务界面持续工作。6–9秒他停止注水，将水壶稳稳放回台面。固定摄影，水流和咖啡滴落声音，无对白。'},
 '05':{image:'02-coffee.png',duration:8,prompt:'0–2秒第三人称侧面中景，Evan停止注水并把水壶放到台面。温柔女性助手画外音说：“视频做好了，要定时发布吗？”2–6秒Evan望向右侧屏幕自然回答：“每隔四小时发一条。”6–8秒女性助手答：“已安排。”Evan放松微笑，固定镜头。'},
 '06':{image:'03-court.png',duration:11,prompt:'0–3秒第三人称侧面中景，Evan在羽毛球场边长椅休息，穿灰色运动T恤黑短裤，左手拿水瓶右手拿手机，真实汗水和轻微喘息。3–6秒手机通知声，他低头看手机，脸上轻微满意的笑容。6–9秒他略抬水瓶喝一口水。9–11秒水瓶放低，镜头缓慢拉远，球场远处击球声继续。不看镜头，无对白。'}
};
const s=specs[n]; if(!s) throw Error('Unknown shot');
const stem=`jobs/${n}-locked-v2`;
if(fs.existsSync(stem+'-attempt.json')) throw Error('Already attempted; recover before retry');
const prompt=`[规格] 图生视频，${s.duration}秒，16:9，真实实拍宣传片。[连续性锚点] 严格使用所附图片作为首帧，保持参考中同一Evan的面部身份、短黑发、肤色、180cm74kg自然体型、服装与整个房间布置、家具位置和暖窗光完全一致，禁止换成其他人或办公室。全程第三人称观察摄影，人物绝不看镜头。[时间轴] ${s.prompt} [约束] 真实皮肤、手部和道具物理，只有一个Evan，不增加人物。无配乐，无字幕无水印，屏幕文字后期合成，不改变场景。`;
const payload={model:'AP Seedance-2.5 标准版',seconds:s.duration,duration:s.duration,size:'1280x720',resolution:'720p',generate_audio:true,content:[{type:'text',text:prompt},{type:'image_url',role:'first_frame',image_url:{url:'data:image/png;base64,'+fs.readFileSync('assets/keyframes/'+s.image).toString('base64')}}]};
fs.writeFileSync(stem+'-attempt.json',JSON.stringify({started:new Date().toISOString(),model:payload.model,...s,prompt,state:'submitted_or_unknown'},null,2));
try {
 const r=await fetch('https://www.donaapi.com/v1/videos',{method:'POST',headers:{Authorization:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(600000)});
 const raw=await r.text(); fs.writeFileSync(stem+'-response.json',raw); console.log(n,r.status,raw);
}catch(e){console.log(n,'UNKNOWN: query task list, do not duplicate',e.message);process.exitCode=1;}
