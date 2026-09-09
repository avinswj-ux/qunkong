"""Durable one-shot submission; ambiguous submissions never auto-retry."""
from pathlib import Path
import base64, hashlib, json, sys

ROOT = Path('/Users/apple/Documents/ChatGPT/群控')
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'iphone-control-mvp'))
from app.video_generation import AutoDLClient, VideoGenerationService

COMMON = '''Generate a single continuous 10-second natural real-time smartphone shot, vertical 9:16, native 1080p. Reference image 0 is the accepted opening keyframe and SOLE visual identity and outfit source, not loose inspiration. Preserve this exact adult woman's facial geometry: oval jaw contour, eye shape and spacing, nose bridge and tip, lip proportions, age, skin tone, center-part long straight black hair and slender skeletal proportions throughout EVERY frame. Do not recast, beautify, slim, lengthen legs or change face at head turns. Preserve exact oversized T-shirt silhouette, neckline, sleeve width, chest print and hem length from the frame. Opaque fitted shorts are underneath and fully covered by the long shirt; maintain complete hip/crotch coverage throughout, bare legs, no hem lifting or underwear visibility. Same room geometry, window light direction, warm lamp, exposure, furniture and camera position throughout. Candid boyfriend viewpoint from a seated companion: nearly fixed eye-level phone, tiny natural hand tremor only, no zoom, orbit, travel, low angle, cuts or transition. Pelvis remains supported at the same seat point, both feet keep their original floor contact points with stable shadows; no walking, standing, leg crossing, foot sliding or levitation. Allow breathing and natural blinks. No second person or hand entering frame. Natural skin texture, hair strands and cotton wrinkles, no plastic skin. No outfit transformation, captions, watermark, dialogue or music. Quiet room ambience and only action-related soft sounds. Do not exaggerate smiles or stare at the lens throughout. Avoid anatomical distortions, extra fingers, fused hands, prop morphing, background warping, print mutation and sudden pose resets.'''
LOOKS = {
 '01': ('look01-white-keyframe.png', '''White loose T-shirt with centered black STARRYTONLION lettering. Seated in blue armchair; left forearm remains on armrest. 0-1s: gaze lowers gently toward ceramic cup in right hand near lap. 1-3s: right elbow flexes smoothly, cup stays upright and rises to lips for one small sip; fingers maintain the same grip, cup has fixed shape. 3-5s: lower cup along the same path back above lap, pause. 5-7s: glance briefly toward companion just beside lens with a tiny relaxed smile. 7-10s: look toward window and settle, cup and left hand remain still. No spilling, cup duplication, armrest penetration or torso travel. Preserve relaxed knee position.'''),
 '02': ('look02-grey-keyframe.png', '''Light heather grey loose raglan T-shirt, exactly three black parallel bands along each shoulder/sleeve, small B-star SOUL BACK chest emblem. Seated on white bed edge. 0-1s: look at left sleeve; right fingers lightly contact left sleeve edge as in first frame. 1-3s: right fingers smooth the sleeve once by only a few centimeters, cotton folds compress then release; do not pull shirt hem or expose shorts. 3-5s: release sleeve and rest right hand naturally on lap; left arm remains relaxed by bed, pelvis and feet unchanged. 5-7s: lift eyes slightly toward companion beside camera, restrained amused expression. 7-10s: gaze returns to hands, soft breath, no new action. Sleeve stripes and chest emblem remain fixed on cloth and never slide independently.'''),
 '03': ('look03-jeep-keyframe.png', '''Warm oatmeal heather oversized T-shirt, three black shoulder/sleeve stripes, small Jeep chest wordmark and hem label. Seated at bed edge with open paperback supported in both hands. 0-1s: look down at book, left hand supports spine. 1-3s: right fingertips lift ONE page corner, move it over spine, page bends and settles on other side; no second page or book distortion. 3-5s: right fingertips release and rest on new page; book remains above lap without covering face or lifting shirt. 5-7s: raise eyes toward companion just beside lens with small warm smile, head only slight tilt. 7-10s: eyes lower to book and hold. Knees together and foot contacts anchored, no torso shift, no new props. Soft single page rustle.''')
}

def main():
    look, mode = sys.argv[1:3]
    filename, action = LOOKS[look]
    ref = HERE / filename
    statefile = HERE / f'look{look}-task.json'
    env = {}
    for line in (ROOT/'iphone-control-mvp/.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
    client=AutoDLClient(token=env.get('AUTODL_COMFYUI_TOKEN',''), base_url=env.get('AUTODL_BASE_URL','https://autodl.art'),timeout=120)
    service=VideoGenerationService(HERE/'tasks.sqlite3', HERE/'clips', client)
    if mode == 'submit':
        if statefile.exists():
            print('Existing ledger; refusing duplicate submission:', statefile); return
        data=ref.read_bytes()
        state={'status':'SUBMITTING','reference':str(ref),'sha256':hashlib.sha256(data).hexdigest(),'prompt':COMMON+'\n'+action,'workflow':'minimax_h3_lightx2v_v5','duration':10,'resolution':'1080p竖','review':'pending video review'}
        with statefile.open('x') as f: json.dump(state,f,ensure_ascii=False,indent=2)
        try:
            task=service.submit(state['workflow'],{'prompt':state['prompt'],'duration':10,'resolution':'1080p竖','ref_image_0':'data:image/png;base64,'+base64.b64encode(data).decode()})
        except Exception:
            state['status']='SUBMISSION_UNCERTAIN'
            statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)); raise
        state.update(task_id=task['task_id'],status=task['status'])
    elif mode == 'query':
        state=json.loads(statefile.read_text())
        if not state.get('task_id'): raise RuntimeError('Uncertain submission requires reconciliation, never blind resubmit')
        task=service.refresh(state['task_id'])
        state.update(status=task['status'],output_path=task.get('output_path'),error=task.get('error'))
    else: raise ValueError('submit or query')
    statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2))
    print(json.dumps({k:state.get(k) for k in ('task_id','status','reference','sha256','output_path','error')},ensure_ascii=False))

if __name__ == '__main__': main()
