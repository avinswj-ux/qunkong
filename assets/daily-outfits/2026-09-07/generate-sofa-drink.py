from pathlib import Path
import sys, json, base64
ROOT=Path('/Users/apple/Documents/ChatGPT/群控'); sys.path.insert(0,str(ROOT/'iphone-control-mvp'))
from app.video_generation import AutoDLClient,VideoGenerationService
HERE=Path(__file__).parent; OUT=Path('/Users/apple/Desktop/抖音成片/2026-09-07'); OUT.mkdir(parents=True,exist_ok=True)
env={}
for line in (ROOT/'iphone-control-mvp/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
service=VideoGenerationService(HERE/'sofa-drink-tasks.sqlite3',OUT,AutoDLClient(token=env.get('AUTODL_COMFYUI_TOKEN',''),base_url=env.get('AUTODL_BASE_URL','https://autodl.art'),timeout=180))
statefile=HERE/'sofa-drink-task.json'
prompt='''Create a 10-second 9:16 1080p natural smartphone video from the supplied opening frame. Preserve the exact adult woman's face, face shape, facial proportions, skin tone, long straight black hair and body proportions already visible in the frame. Preserve the black fitted short-sleeve crop top, exposed waist skin with black lace skirt trim, opaque black fitted skirt, glass, cream sofa, water garden and architecture. Boyfriend handheld perspective, one continuous seated shot, eye-level slightly off-center, only mild phone micro-jitter. 0-3s she looks down at the drink and gently rotates the glass; 3-6s she lifts it for a small sip while keeping hips and feet anchored; 6-8s she glances briefly toward the boyfriend beside the lens with a small natural smile; 8-10s she lowers the glass and looks back at the water. Keep seated weight, knees, feet and sofa contact fixed; no walking, no sliding, no drifting, no camera travel, no outfit change, no second person, no bag, no white waistband, no new accessories, no text, logo or watermark. Natural skin pores, flyaway hair, fabric folds, realistic hands and shadows, normal speed, subtle room ambience and glass sound only.'''
if '--submit' in sys.argv:
    ref=Path('/Users/apple/.codex/generated_images/01a0478f-f2eb-7203-9d1a-732803ab5f71/exec-10b05bea-c841-479b-990a-c63ba0a0db32.png')
    t=service.submit('minimax_h3_lightx2v_v5',{'prompt':prompt,'duration':10,'resolution':'1080p竖','ref_image_0':'data:image/png;base64,'+base64.b64encode(ref.read_bytes()).decode()})
    statefile.write_text(json.dumps({'task_id':t['task_id'],'status':t['status']},ensure_ascii=False,indent=2)); print(json.dumps(t,ensure_ascii=False))
else:
    s=json.loads(statefile.read_text()); t=service.refresh(s['task_id']); s['status']=t['status']
    if t['status']=='SUCCESS': s['output_path']=t['output_path']
    statefile.write_text(json.dumps(s,ensure_ascii=False,indent=2)); print(json.dumps(s,ensure_ascii=False))
