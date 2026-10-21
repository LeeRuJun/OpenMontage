"""Official historical-story edit stage helper."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main(project: Path) -> None:
    plan=json.loads((project/'artifacts/scene_plan.json').read_text())
    manifest=json.loads((project/'artifacts/asset_manifest.json').read_text())
    boards={a['scene_id']:a for a in manifest['assets'] if a.get('subtype')=='final_board'}
    cuts=[]
    for scene in plan['scenes']:
        bid=scene.get('visual_board_id',scene['id'])
        if bid not in boards: raise SystemExit(f'missing approved final board: {bid}')
        cuts.append({'id':f'cut-{bid}','source':boards[bid]['id'],'in_seconds':0,'out_seconds':round(scene['end_seconds']-scene['start_seconds'],3),'layer':'primary','transform':{'scale':1.0,'position':'center','animation':'ken-burns-slow-zoom'},'transition_in':'dissolve','transition_out':'dissolve','transition_duration':0.35,'reason':scene.get('shot_intent','claim-specific historical visual')})
    edit={'version':'1.0','cuts':cuts,'audio':{'narration':{'src':'assets/audio/narration_full.mp3','volume':1.0},'music':{'asset_id':'historical-bgm-catalog','volume':0.1,'ducking':{'enabled':True,'threshold_db':-18,'reduction_db':-10,'attack_seconds':0.2,'release_seconds':0.6}}},'subtitles':{'enabled':True,'style':'sentence','source':'assets/audio/narration_full.mp3','font':'serif','font_size':34,'color':'#f0dfc5','outline_color':'#17151a','background':'#17151a99','position':'bottom-center','max_words_per_line':18},'renderer_family':'documentary-montage','render_runtime':'hyperframes','composition_mode':'templated','metadata':{'pipeline':'historical-story','unique_board_count':len(cuts)}}
    (project/'artifacts/edit_decisions.json').write_text(json.dumps(edit,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cuts':len(cuts),'runtime':'hyperframes'},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',required=True); args=p.parse_args(); main(Path(args.project_dir).resolve())
