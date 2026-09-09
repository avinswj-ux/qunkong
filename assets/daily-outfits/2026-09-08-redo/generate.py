"""Five-second human-feeling MiniMax H3 retries; durable ledgers prevent duplicate charges."""
from pathlib import Path
import base64, hashlib, json, shutil, sys

ROOT = Path('/Users/apple/Documents/ChatGPT/群控')
HERE = Path(__file__).parent
OUT = Path('/Users/apple/Desktop/抖音成片/2026-09-08-重做')
sys.path.insert(0, str(ROOT / 'iphone-control-mvp'))
from app.video_generation import AutoDLClient, VideoGenerationService

COMMON = '''Create one continuous 5-second real-time candid iPhone clip, vertical 9:16, native 1080p. Reference image 0 is the accepted opening keyframe and the sole visual source for the adult woman's identity, body, clothing and location. Keep her exact face, facial proportions, skin tone, age, center-part long black hair, hairline and natural body proportions throughout. Preserve the exact clothing already visible in the keyframe. The performance must feel like a real person responding to an ordinary moment, not a model following choreography. Use one motivated action sequence with natural cause and effect: eyes notice the target first, the head follows, shoulders and torso respond subtly, the hand completes the task, then the body releases tension. Include irregular natural blinking, breathing, tiny facial asymmetry, loose hair response and believable cloth compression. Boyfriend-perspective phone camera: restrained handheld observation with small human drift that gently follows the action; never perform an automatic push-in, beauty zoom, orbit or sudden reframe. Keep the face and full action visible. Real skin texture, phone noise, modest compression and natural mixed light. No outfit change, second person, captions, watermark, dialogue or music. Avoid puppet motion, isolated head or hand movement, frozen torso, repeated gesture, prolonged posing, exaggerated smile, identity drift, extra fingers, broken joints, floating feet, prop morphing or background warping.'''

LOOKS = {
  '01': {
    'ref': 'look-01-kitchen-gray-sport-keyframe.png',
    'file': 'look-01-kitchen-gray-sport-5s-1080p.mp4',
    'action': '''She is in the lived-in apartment kitchen wearing the grey sleeveless zipped athletic vest, black mid-thigh biker shorts and white sneakers. She has just heard her companion near the camera while her right hand rests on the clear capped water bottle. Over five seconds, her eyes shift toward the voice, her head and upper chest follow by a small natural amount, then she lifts the bottle cleanly off the table to waist height. Her wrist supports the bottle vertically; water moves subtly and the bottle keeps one stable shape. Her weight shifts slightly into the planted rear foot and the free knee relaxes. She gives a brief unplanned half-smile toward the companion, then looks toward the doorway as if ready to leave. The camera makes only a tiny human correction to keep her full body framed. No walking, drinking, repeated bottle lift, garment tugging or large zoom.'''
  },
  '02': {
    'ref': 'look-02-restaurant-black-lace-keyframe.png',
    'file': 'look-02-restaurant-black-lace-5s-1080p.mp4',
    'action': '''She remains seated in the ordinary restaurant booth wearing the fully opaque black knee-above cocktail dress with horizontal lace surface texture. Her hips stay supported by the same cushion and the open menu stays on the table. Over five seconds, she finishes tucking the loose strand behind her right ear, fingers release naturally, and her right hand lowers beside the menu. While the hand descends, her eyes leave the page and lift toward her companion just beside the lens; her head and shoulders follow softly. A small genuine smile appears for less than one second, then she looks back to the menu. The left fingertips continue holding the menu corner and the pages flex slightly from contact. Camera stays seated at table height with tiny breathing-like hand movement only. No hair flip, seductive pose, menu distortion, body slide or push-in.'''
  },
  '03': {
    'ref': 'look-03-hotel-ivory-dress-keyframe.png',
    'file': 'look-03-hotel-ivory-dress-5s-1080p.mp4',
    'action': '''She remains seated on the same hotel bed edge wearing the opaque ivory halter dress with the same small rhinestone neckline details and beige low-heel sandals. Over five seconds, she guides the small earring into her left ear, pauses when it seats, then lowers her left hand to the open jewellery box supported in her right palm. Her eyes stay on the task until the earring is secure; only then she glances toward her companion off camera with a quiet relieved expression. The head tilt, neck, shoulder and elbow move as one connected chain; long hair slides a little over the shoulder and settles. Hips remain supported, knees and feet keep their original positions, mattress compresses consistently. Camera holds a natural full seated view with slight handheld imperfection. No repeated ear touching, jewellery duplication, hand-ear fusion, standing, leg movement or zoom.'''
  },
  '03b': {
    'ref': 'look-03-hotel-ivory-dress-keyframe.png',
    'file': 'look-03-hotel-ivory-dress-5s-1080p-v2.mp4',
    'action': '''She remains seated on the same hotel bed edge wearing the opaque ivory halter dress with the same small rhinestone neckline details and beige low-heel sandals. This is a quiet private preparation moment with no interaction with the camera. Over five seconds, she keeps her gaze lowered, guides the small earring into her left ear, pauses briefly when it seats, then lowers the left hand to the jewellery box in her right palm and gently closes the lid once. The head tilt, neck, shoulder and elbow move as one connected chain; her torso stays upright and never leans toward the camera. Long hair slides minimally over the shoulder and settles. Hips remain supported, knees and both feet keep their original positions, and mattress compression stays constant. The phone remains at the original full seated framing from first to last frame; no push-in, no face close-up, no reframing and no eye contact with lens. No repeated ear touching, jewellery duplication, hand-ear fusion, standing, leg movement or smile performance.'''
  }
}

def env_values():
    out = {}
    for line in (ROOT / 'iphone-control-mvp/.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k, v = line.split('=', 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def main():
    look, mode = sys.argv[1:3]
    item = LOOKS[look]
    ref = HERE / item['ref']
    statefile = HERE / f'look-{look}-task.json'
    env = env_values()
    service = VideoGenerationService(HERE / 'tasks.sqlite3', HERE / 'clips', AutoDLClient(token=env.get('AUTODL_COMFYUI_TOKEN', ''), base_url=env.get('AUTODL_BASE_URL', 'https://autodl.art'), timeout=180))
    if mode == 'submit':
        if statefile.exists():
            print('Existing ledger; refusing duplicate submission:', statefile)
            return
        data = ref.read_bytes()
        state = {'status':'SUBMITTING','reference':str(ref),'sha256':hashlib.sha256(data).hexdigest(),'prompt':COMMON+'\n'+item['action'],'workflow':'minimax_h3_lightx2v_v5','duration':5,'resolution':'1080p竖','sources':['central-rule-thread:01a08135-2b48-7ae0-ba27-7359f6517610','female-outfit-director','user garment references'],'conflict_check':'passed','review':'pending continuous-motion review'}
        statefile.write_text(json.dumps(state, ensure_ascii=False, indent=2))
        try:
            task = service.submit(state['workflow'], {'prompt':state['prompt'],'duration':5,'resolution':'1080p竖','ref_image_0':'data:image/png;base64,'+base64.b64encode(data).decode()})
        except Exception:
            state['status'] = 'SUBMISSION_UNCERTAIN'
            statefile.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            raise
        state.update(task_id=task['task_id'], status=task['status'])
    elif mode == 'query':
        state = json.loads(statefile.read_text())
        if not state.get('task_id'):
            raise RuntimeError('Uncertain submission; refusing blind resubmit')
        task = service.refresh(state['task_id'])
        state.update(status=task['status'], output_path=task.get('output_path'), error=task.get('error'))
        if task['status'] == 'SUCCESS' and task.get('output_path'):
            OUT.mkdir(parents=True, exist_ok=True)
            dest = OUT / item['file']
            if not dest.exists(): shutil.copy2(task['output_path'], dest)
            state['delivery_path'] = str(dest)
    else:
        raise ValueError('submit or query')
    statefile.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(json.dumps({k:state.get(k) for k in ('task_id','status','reference','sha256','output_path','delivery_path','error')}, ensure_ascii=False))

if __name__ == '__main__': main()
