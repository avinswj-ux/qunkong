from pathlib import Path
import sys, json, base64, time, subprocess

ROOT = Path('/Users/apple/Documents/ChatGPT/群控')
sys.path.insert(0, str(ROOT / 'iphone-control-mvp'))
from app.video_generation import AutoDLClient, VideoGenerationService

HERE = Path(__file__).parent
OUT = Path('/Users/apple/Desktop/抖音成片/2026-09-06')
OUT.mkdir(parents=True, exist_ok=True)
env = {}
for line in (ROOT/'iphone-control-mvp/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k,v=line.split('=',1); env[k.strip()]=v.strip().strip('\"').strip("'")
client=AutoDLClient(token=env.get('AUTODL_COMFYUI_TOKEN',''),base_url=env.get('AUTODL_BASE_URL','https://autodl.art'),timeout=180)
service=VideoGenerationService(HERE/'tasks.sqlite3',OUT,client)
anchor=ROOT/'assets/model-templates/locked-model-frontal-v2.png'
def uri(p): return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
looks=[
 ('black-jacket','black fitted zip athletic jacket with curved seam panels and thumbhole sleeves, grey taupe fitted opaque athletic shorts','She lifts her open palm toward the lens until it fully occludes the image, then lowers it.','She gently adjusts a cuff, turns 30 degrees to show the jacket side seam, then returns to front.'),
 ('slate-jacket','slate blue fitted zip athletic jacket with curved seam panels and thumbhole sleeves, grey taupe fitted opaque athletic shorts','She brings a plain folded light towel across the lens from left to right, fully occluding the view momentarily.','She lowers the towel out of view, gently rolls her shoulders, takes a small step and rests naturally.'),
 ('pink-dress','modest blush pink short sleeve day dress exactly matching reference 2, opaque fabric, buttoned neckline, no pants','She steps forward and covers the camera with her open palm, then uncovers it.','She takes a small step back, turns gently 30 degrees, lets the skirt fabric settle and smiles subtly.'),
 ('olive-dress','heather grey olive short sleeve polo dress with button placket and small side hem slit exactly matching reference 2, no pants','She sweeps a plain cream scarf fully across the lens, then lowers it out of frame.','She casually brushes a strand of hair behind her ear, takes one small side step and settles facing the camera.'),
]
common='''Create a 10-second vertical 9:16 natural smartphone outfit-change video. Reference 1 shows the opening outfit and the locked adult Chinese woman. Reference 2 shows the exact target outfit, same identity and same room. Preserve her facial structure, age, skin tone, body proportions and long straight black hair. Only one woman. Fixed eye-level full-body camera with head and both bare feet inside the frame, no zoom or low angles. Keep the beige wall, framed artwork, dark door and floor consistent. Ordinary daylight, understated expression, authentic fabric folds, real grounded weight, mild phone compression and natural skin. Barefoot throughout, no shoes or socks. No exaggerated posing or body changes. No text, logos, UI or watermark. No extra fingers, face drift, duplicate people or garment layering. Normal speed, no slow motion. Soft original rhythm and a short swish on the cut, no speech or copied song. Timeline: 0-1.5 seconds in the striped sweater and white shorts of reference 1; 1.5-2.5 seconds perform the occlusion below. Only when the lens is FULLY covered, hard cut to the target outfit of reference 2, maintaining pose and camera alignment. From 2.5 to 9.5 seconds show the target outfit with the small actions below. Final 0.5 seconds hold naturally. Never show physical undressing, dissolving clothes, or see-through fabric. '''
manifest_path=HERE/'manifest.json'
items=json.loads(manifest_path.read_text()) if manifest_path.exists() else []
for i,(name,outfit,transition,action) in enumerate(looks,1):
    if '--olive-only' in sys.argv and name != 'olive-dress': continue
    if '--ready-only' in sys.argv and i > 2: continue
    if any(x['name']==name for x in items): continue
    ref=HERE/f'look-{i:02d}.png'
    if not ref.exists(): raise RuntimeError(f'Missing {ref}')
    prompt=common+' Target outfit: '+outfit+'. Occlusion: '+transition+' After reveal: '+action
    (HERE/f'prompt-{i:02d}-en.txt').write_text(prompt)
    task=service.submit('minimax_h3_lightx2v_v5',{'prompt':prompt,'duration':10,'resolution':'1080p竖','ref_image_0':uri(anchor),'ref_image_1':uri(ref)})
    items.append({'name':name,'task_id':task['task_id'],'status':task.get('status')})
    manifest_path.write_text(json.dumps(items,ensure_ascii=False,indent=2))
    print(json.dumps({'submitted':name,'task_id':task['task_id']},ensure_ascii=False),flush=True)
deadline=time.time()+2400
while time.time()<deadline:
    pending=False
    for item in items:
        if item['status'] in ('SUCCESS','FAILED'): continue
        task=service.refresh(item['task_id']); item['status']=task['status']
        print(json.dumps({'name':item['name'],'status':item['status']},ensure_ascii=False),flush=True)
        if task['status']=='SUCCESS':
            src=Path(task['output_path']); dst=OUT/(item['name']+'-10s-1080p.mp4')
            subprocess.run(['ffmpeg','-y','-i',str(src),'-t','10','-vf','scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2','-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-movflags','+faststart',str(dst)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            item['path']=str(dst)
            item['probe']=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(dst)]))
        elif task['status']=='FAILED': item['error']=task.get('error')
        else: pending=True
        manifest_path.write_text(json.dumps(items,ensure_ascii=False,indent=2))
    if not pending: break
    time.sleep(25)
print(json.dumps(items,ensure_ascii=False),flush=True)
