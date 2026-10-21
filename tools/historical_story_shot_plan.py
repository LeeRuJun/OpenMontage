"""Official shot-prompt planning stage for historical-story."""
from __future__ import annotations
import argparse,json
from pathlib import Path
STYLE={'map':('overhead parchment cartography','river systems, borders, and deterministic route overlays','top-down push'),'diagram':('top-down evidence table','ledgers, seals, map fragments, and institutional relationships','document reveal'),'evidence_card':('editorial archival evidence composition','one dominant artifact and citation-safe negative space','focus pull'),'reconstruction':('single coherent cinematic environmental reconstruction','subject embedded in a specific historical location','lateral parallax'),'typography':('single symbolic historical still life','one decisive object with strong negative space','object reveal'),'timeline':('single horizontal historical timeline built from documents and route markers','sequence and transition evidence','left-to-right draw'),'split_screen':('single editorial diptych with two distinct historical situations','contrasting outcomes in separate spatial zones','two-panel reveal'),'balance_scale':('single symbolic still life of two unequal historical costs','objects representing sovereign power, family, people, and war','opposing sides settle'),'modern_context':('single museum-like editorial collage','historical maps, books, landscape, and modern reception kept separate','layered assembly'),'closing_typography':('single wide contemplative Jiangnan river landscape','quiet sky, distant boat, and emotional landing','slow pull back')}

def pick_character(title,act):
    if '钱俶' in title or act in {'act_05','act_08','epilogue'} or '入朝' in title or '王还在' in title:return 'qianchu'
    if '军' in title:return 'song_soldier'
    if '宋朝' in title or '朝廷' in title:return 'song_taizong'
    if '官员' in title or '行政' in title:return 'wuyue_official'
    return None

def pick_scene(title,kind):
    if any(x in title for x in ['水网','水乡','城市','社会']):return 'wuyue_waterways'
    if any(x in title for x in ['宫','制度','王还在']):return 'wuyue_palace'
    if any(x in title for x in ['军','压力']):return 'song_riverbank'
    if '入朝' in title:return 'song_court'
    if kind in {'map','diagram','evidence_card','timeline'}:return 'archive_table'
    return 'wuyue_waterways'

def main(project):
    plan=json.load(open(project/'artifacts/scene_plan.json')); shots=[]
    for i,scene in enumerate(plan['scenes'],1):
        bid=scene.get('visual_board_id',scene['id']); title=scene['description']; kind=scene.get('type','reconstruction'); visual,evidence,motion=STYLE.get(kind,STYLE['reconstruction']); character=pick_character(title,scene.get('id','')); location=pick_scene(title,kind); refs=[location]+([character] if character else [])
        prompt=(f"Create ONE coherent cinematic documentary shot for the specific historical claim: {title}. "
          f"Use the supplied reference assets only for visual continuity of the historical person and location; integrate them into one continuous camera view. "
          f"Do not create a collage, split-screen, contact sheet, reference-board layout, side-by-side panels, pasted portraits, or visible source-image frames. "
          f"Visual grammar: {visual}. Subject/action must occur inside the fixed scene {location}. Evidence layer: {evidence}; if evidence needs text or labels, leave clean space for deterministic post-production overlays rather than generating text. "
          f"Motion cue reserved for edit: {motion}. Deep ink charcoal, rice-paper warmth, restrained vermilion, historically grounded late-tenth-century material detail. "
          "No readable text, no letters, no digits, no board IDs, no logos, no modern objects, no unsupported insignia, no generic floating portrait. Leave lower third safe for captions. Illustrative reconstruction, not archival footage.")
        shots.append({'shot_id':f'shot-{i:02d}','scene_id':scene['id'],'visual_board_id':bid,'board_duration_seconds':max(20,scene['end_seconds']-scene['start_seconds']),'microbeat_ids':[f'{bid}-m1',f'{bid}-m2',f'{bid}-m3'],'internal_motion_plan':[motion,'deterministic evidence reveal','caption overlay'],'prompt_spec':{'script_section_id':scene['id'],'visual_claim':title,'subject_action':f"Specific action for {title}, embedded in one continuous scene.",'location_context':f"Fixed scene plate: {location}.",'evidence_layer':evidence,'historical_boundary':'illustrative reconstruction; no invented dialogue or readable AI text','dynamic_layers':[motion,'evidence reveal','caption label'],'caption_safe_area':'lower third reserved for deterministic captions','positive_prompt':prompt,'constraints':['single coherent shot','no collage or split-screen','no readable text or digits','no modern objects','no generic floating portrait']},'narration_beat':title,'visual_function':'evidence_insert' if kind in {'diagram','evidence_card','timeline'} else 'show_event','generation_mode':'composite_references','required_core_assets':refs,'prompt':prompt,'camera':visual,'composition':f'{visual}; one coherent camera view for {title}; no repeated centered portrait template','prompt_constraints':['single coherent shot','no collage','no readable text','no digits or board IDs','no modern objects','no unsupported insignia'],'reuse_policy':'primary image unique to this board; references only for continuity','reused_by_shots':[],'status':'approved'})
    out={'version':'1.0','mode':'full_longform','shots':shots,'metadata':{'board_count':len(shots),'provider':'openai:gpt-image-2','unique_primary_image_required':True,'prompt_stage':'shot-prompt-director','coherent_single_shot_required':True}}
    (project/'artifacts/shot_asset_plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'shots':len(shots),'stage':'shot_prompt_director'},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',required=True); a=p.parse_args(); main(Path(a.project_dir).resolve())
