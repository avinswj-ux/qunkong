"""Submit/query four locked-model MiniMax H3 clips with durable per-look ledgers."""
from pathlib import Path
import base64, hashlib, json, shutil, sys

ROOT = Path('/Users/apple/Documents/ChatGPT/群控')
HERE = Path(__file__).parent
OUT = Path('/Users/apple/Desktop/抖音成片/2026-09-08')
sys.path.insert(0, str(ROOT / 'iphone-control-mvp'))
from app.video_generation import AutoDLClient, VideoGenerationService

COMMON = '''Create one continuous 10-second natural real-time smartphone fashion clip, vertical 9:16, native 1080p. [identity] Reference image 0 is the accepted opening keyframe and the sole visual identity, body, outfit, pose and location source—not loose inspiration. Preserve this exact adult woman's facial geometry in every frame: face outline, eye shape and spacing, eyebrows, nose bridge and tip, lip proportions, skin tone, age, center-part long straight black hair, hairline, shoulder-waist-hip proportions and leg length. Never recast, beautify, change ethnicity, change hairstyle, slim, enlarge curves or lengthen limbs. [user] Preserve the exact garment color, neckline, seams, waistband, length and fit already embedded in the keyframe. No outfit transformation. [skill] Same corridor geometry, window, sculptures, floor, lighting direction, exposure and camera position throughout. Boyfriend-viewpoint candid phone shot at eye level, nearly fixed with only subtle human micro-jitter; no zoom, orbit, pan, tracking, low angle, cuts or transitions. Both feet must keep credible ground contact and contact shadows; no gliding, floating, foot sliding or continuous walking. Each time segment has one main action. Natural blinks, breathing, fine hair and cloth response only. She does not stare at the lens throughout. No second person or hand entering frame. No captions, watermark, brand text, dialogue or music; quiet corridor ambience and only action-related cloth/foot sounds. Avoid identity drift at head turns, anatomical distortion, extra/fused fingers, broken joints, garment mutation, background warping, sudden pose resets, plastic skin or glossy CGI.'''

LOOKS = {
    '01': {
        'ref': 'look-01-gray-vest-black-biker-keyframe.png',
        'file': 'look-01-gray-vest-black-biker-10s-1080p.mp4',
        'action': '''[user] Outfit remains the exact grey sleeveless high-neck full-zip fitted athletic vest with curved chest and waist seam lines, black high-waist mid-thigh biker shorts, and white low-top sneakers. 0-1.5s: the forward foot finishes one short natural step and plants firmly; hips and torso settle over the new support leg, both shoe shadows lock to the floor. 1.5-4s: standing in place, right fingers smooth the vest hem once by two or three centimeters; zipper and seam lines stay fixed. 4-6.5s: right hand releases and rests naturally, head turns slightly toward the window while eyes follow. 6.5-8.5s: brief glance toward the companion just beside the lens with a restrained relaxed expression. 8.5-10s: gaze returns down the corridor and body settles. No additional step, runway sway, hem lifting, zipper opening or shorts deformation.'''
    },
    '02': {
        'ref': 'look-02-gray-flare-flipflops-keyframe.png',
        'file': 'look-02-gray-flare-flipflops-10s-1080p.mp4',
        'action': '''[user] Outfit remains the ivory fitted short-sleeve crop athletic top, charcoal high-waist fitted flared yoga trousers with smooth clean front, and black thin-strap flat flip-flops. 0-2s: maintain the original supported pose with right palm lightly touching the window frame and both flip-flops fully planted; breathe and blink. 2-4s: right fingertips slide downward only a few centimeters along the frame, then stop; elbow relaxes without changing foot placement. 4-6.5s: head and eyes turn a few degrees from the window toward the companion beside camera; no torso rotation. 6.5-8s: a tiny natural closed-mouth smile, then neutral. 8-10s: gaze returns outside and fingers rest. Keep trouser flare, inseam, waistband and hem stable; no pants shortening, shoe change, leg crossing, foot dragging or flip-flop detachment.'''
    },
    '03': {
        'ref': 'look-03-brown-leggings-oatmeal-top-keyframe.png',
        'file': 'look-03-brown-leggings-oatmeal-top-10s-1080p.mp4',
        'action': '''[user] Outfit remains the oatmeal fitted long-sleeve half-zip athletic top, deep cocoa-grey high-waist ankle-length fitted leggings, and dark-brown thin-strap flat flip-flops. 0-2s: left palm remains supported on the wall and feet remain at the same crossed standing marks; natural blink and breath. 2-4.5s: right fingers complete one small hair-tuck behind the ear, following a short arc; hair strands bend and settle without changing hairstyle. 4.5-6.5s: right hand lowers to rest beside the torso, while the supported hand stays fixed. 6.5-8s: eyes lift briefly toward the companion just to the side of lens, restrained expression. 8-10s: gaze lowers toward the floor and holds. No walking, pelvic drift, leg uncrossing, wall penetration, zipper motion, waistband movement or front-seam distortion.'''
    },
    '04': {
        'ref': 'look-04-gray-openback-black-biker-keyframe.png',
        'file': 'look-04-gray-openback-black-biker-10s-1080p.mp4',
        'action': '''[user] Outfit remains the exact light-grey long-sleeve cropped yoga top with open back, two thin straps crossing in a clean X and a twisted fabric knot at the lower back, black high-waist mid-thigh biker shorts, and black flat flip-flops. 0-2s: hold the original back three-quarter pose; right palm keeps light contact with the window frame and both feet remain planted. 2-4s: fingertips flex once against the frame and relax; shoulder blade motion is subtle and anatomically linked. 4-6.5s: head turns only a few degrees toward the window, eyes follow, hair shifts softly but must not cover or alter the X straps. 6.5-8.5s: left hand smooths the side waistband once by a few centimeters, then stops. 8.5-10s: settle and look outside. The X straps and lower-back twist must remain continuously visible, connected and unchanged; no extreme neck twist, no turn to front, no shorts shortening, no thong appearance, no strap duplication or disappearance.'''
    }
}

def env_values():
    values = {}
    for line in (ROOT / 'iphone-control-mvp/.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values

def main():
    look, mode = sys.argv[1:3]
    item = LOOKS[look]
    ref = HERE / item['ref']
    statefile = HERE / f'look-{look}-task.json'
    env = env_values()
    client = AutoDLClient(token=env.get('AUTODL_COMFYUI_TOKEN', ''), base_url=env.get('AUTODL_BASE_URL', 'https://autodl.art'), timeout=180)
    service = VideoGenerationService(HERE / 'tasks.sqlite3', HERE / 'clips', client)
    if mode == 'submit':
        if statefile.exists():
            print('Existing ledger; refusing duplicate submission:', statefile)
            return
        data = ref.read_bytes()
        state = {
            'status': 'SUBMITTING', 'reference': str(ref),
            'sha256': hashlib.sha256(data).hexdigest(),
            'prompt': COMMON + '\n' + item['action'],
            'sources': {'identity': 'accepted keyframe carrying locked model', 'user': '2026-09-08 garment screenshots and current request', 'skill': 'female-outfit-director + VIDEO_WORKFLOW_RULES'},
            'conflict_check': 'passed', 'workflow': 'minimax_h3_lightx2v_v5',
            'duration': 10, 'resolution': '1080p竖', 'review': 'pending video review'
        }
        statefile.write_text(json.dumps(state, ensure_ascii=False, indent=2))
        try:
            task = service.submit(state['workflow'], {'prompt': state['prompt'], 'duration': 10, 'resolution': '1080p竖', 'ref_image_0': 'data:image/png;base64,' + base64.b64encode(data).decode()})
        except Exception:
            state['status'] = 'SUBMISSION_UNCERTAIN'
            statefile.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            raise
        state.update(task_id=task['task_id'], status=task['status'])
    elif mode == 'query':
        state = json.loads(statefile.read_text())
        if not state.get('task_id'):
            raise RuntimeError('Uncertain submission requires reconciliation; refusing blind resubmit')
        task = service.refresh(state['task_id'])
        state.update(status=task['status'], output_path=task.get('output_path'), error=task.get('error'))
        if task['status'] == 'SUCCESS' and task.get('output_path'):
            OUT.mkdir(parents=True, exist_ok=True)
            dest = OUT / item['file']
            if not dest.exists():
                shutil.copy2(task['output_path'], dest)
            state['delivery_path'] = str(dest)
    else:
        raise ValueError('submit or query')
    statefile.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(json.dumps({k: state.get(k) for k in ('task_id', 'status', 'reference', 'sha256', 'output_path', 'delivery_path', 'error')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
