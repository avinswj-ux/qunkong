from pathlib import Path
import sys, json, base64, shutil

ROOT = Path('/Users/apple/Documents/ChatGPT/群控')
sys.path.insert(0, str(ROOT/'iphone-control-mvp'))
from app.video_generation import AutoDLClient, VideoGenerationService

HERE = Path(__file__).parent
OUT = Path('/Users/apple/Desktop/抖音成片/2026-09-07')
OUT.mkdir(parents=True, exist_ok=True)
env = {}
for line in (ROOT/'iphone-control-mvp/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k,v = line.split('=',1)
        env[k.strip()] = v.strip().strip('\"').strip("'")
client = AutoDLClient(token=env.get('AUTODL_COMFYUI_TOKEN',''), base_url=env.get('AUTODL_BASE_URL','https://autodl.art'),timeout=180)
service = VideoGenerationService(HERE/'bed-reading-tasks.sqlite3', OUT, client)
statefile = HERE/'bed-reading-task.json'
prompt = '''Create a 10-second 9:16 1080p natural smartphone video using the supplied image as the opening frame and sole visual reference. Preserve this exact adult woman's facial features, face shape, body proportions, long black hair, navy sleeveless high-neck top, grey-blue ruched skirt, bare feet, bed and hotel room. A quiet boyfriend-perspective candid moment. Single continuous nearly stationary eye-level shot, subtle hand-held micro-jitter only, no camera travel or zoom. She remains seated in exactly the same place with hips supported by the mattress and feet resting on the carpet throughout. 0-4s: she reads and gently turns ONE page using her right hand, left hand supports the book; page bends and settles realistically. 4-7s: she briefly raises her eyes toward the person just beside the lens, gives a small relaxed smile, without turning her torso. 7-10s: she lowers her gaze back to the book and continues reading. Natural blinking and breathing, tiny finger movement. Keep pelvis, legs, feet, furniture and background anchored; no sliding, drifting, walking, standing, leg repositioning, limb distortion or extra fingers. Maintain opaque clothing, exact garment fit and skin texture. No outfit change, no second person, no bag, no text overlays or watermark. Real-time speed, soft room ambience and page rustle, no speech or music. Natural window and bedside lighting consistent with reference.'''
if '--submit' in sys.argv and not statefile.exists():
    ref = Path('/Users/apple/.codex/generated_images/01a0478f-f2eb-7203-9d1a-732803ab5f71/exec-b0cef0fb-c583-492b-b04b-91aa78bdcbbf.png')
    task = service.submit('minimax_h3_lightx2v_v5', {'prompt':prompt,'duration':10,'resolution':'1080p竖','ref_image_0':'data:image/png;base64,'+base64.b64encode(ref.read_bytes()).decode()})
    statefile.write_text(json.dumps({'task_id':task['task_id'],'status':task['status'],'prompt':prompt},ensure_ascii=False,indent=2))
    print(json.dumps({'task_id':task['task_id'],'status':task['status']},ensure_ascii=False))
else:
    state=json.loads(statefile.read_text())
    task=service.refresh(state['task_id'])
    state['status']=task['status']
    if task['status']=='SUCCESS':
        dest=OUT/'bed-reading-navy-grey-10s-1080p.mp4'
        if not dest.exists(): shutil.copy2(task['output_path'],dest)
        state['output_path']=str(dest)
    statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2))
    print(json.dumps({k:state.get(k) for k in ['task_id','status','output_path']},ensure_ascii=False))
