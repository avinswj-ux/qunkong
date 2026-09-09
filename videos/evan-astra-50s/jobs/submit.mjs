import fs from 'node:fs';
const key=process.env.EVAN_DONA_KEY;
if(!key) throw new Error('EVAN_DONA_KEY required');
const payload={model:'AP Seedance-2.5 标准版',seconds:8,size:'1280x720',resolution:'720p',mode:'frames',generate_audio:true,watermark:false,first_frame:'data:image/png;base64,'+fs.readFileSync('assets/keyframes/01-study.png').toString('base64'),prompt:'16:9真人实拍宣传片，8秒。参考首帧锁定同一Evan脸、短黑发、肤色、180cm74kg体型、深灰衬衫和室内布局。第三人称侧面观察摄影，人物不看镜头。0-1秒呼吸，1-6秒Evan看右侧屏幕说中文：Astra，看看今天女装什么款在爆，整理份报告。6-8秒平静女性助手画外音：好，开始分析。Evan点头。镜头轻缓推，真实口型和环境声，无字幕，无新增人物，不变脸，不改变背景。屏幕保持暗蓝稳定框架，文字由后期合成。'};
fs.writeFileSync('jobs/01-request-summary.json',JSON.stringify({...payload,first_frame:'assets/keyframes/01-study.png'},null,2));
const response=await fetch('https://www.donaapi.com/v1/videos',{method:'POST',headers:{Authorization:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(120000)});
const raw=await response.text();fs.writeFileSync('jobs/01-response.json',raw);console.log(response.status,raw);
