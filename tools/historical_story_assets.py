"""Official historical-story asset stage helpers.

This module is called by the native pipeline stage, not by a project-local
throwaway script. It owns core character/scene assets and the canonical manifest.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from dotenv import load_dotenv
from tools.graphics.image_batch import ImageBatchRunner

SCENES = [
    ("wuyue_waterways", "scene_plate", "Late tenth-century Wuyue Jiangnan waterways and Hangzhou surroundings, canals, rice fields, low ancient city walls, mist, boats and distant hills, historically grounded, wide documentary scene plate, no readable text, no modern objects."),
    ("wuyue_palace", "scene_plate", "Late tenth-century Wuyue palace courtyard and administrative hall, timber architecture, tiled roofs, lacquered desks, official seals and lamps, quiet court atmosphere, wide scene plate, no readable text."),
    ("song_riverbank", "scene_plate", "Jiangnan riverbank under Northern Song military pressure, misty shore, boats, distant banners and supply carts, no battle spectacle, historically restrained wide scene plate, no readable text."),
    ("song_court", "scene_plate", "Northern Song court interior, towering timber hall, formal steps, officials arranged in distance, restrained imperial atmosphere, no identifiable faces, no readable text."),
    ("archive_table", "diagram", "Editorial historical evidence table with bamboo slips, paper memorials, seals, map fragments and chronicle pages, warm rice-paper and ink texture, top-down documentary plate, no readable text."),
    ("wuyue_map", "map", "Historically grounded editorial map plate of Wuyue and Jiangnan waterways in the late tenth century, parchment, rivers, borders and route space, no labels or readable text because labels are deterministic overlays."),
]

def core(project: Path) -> None:
    load_dotenv('/Users/fanshu01/rep/github/OpenMontage/.env')
    scene_dir=project/'assets/images/core/scenes'; scene_dir.mkdir(parents=True,exist_ok=True)
    requests=[{'prompt':p,'preferred_provider':'openai','allowed_providers':['openai'],'model':'gpt-image-2','size':'1280x720','quality':'medium','output_format':'png','n':1,'output_path':str(scene_dir/f'{s}.png'),'task_context':{'pipeline':'historical-story','stage':'core_assets','asset_group_id':g}} for s,g,p in SCENES]
    result=ImageBatchRunner().run(requests,max_workers=3,max_retries=2)
    failed=[x for x in result['results'] if x['status']=='failed']
    if failed: raise SystemExit(f'core_assets failed: {failed}')
    assets=[]
    for path in sorted((project/'assets/images/core/characters').glob('*.png')):
        assets.append({'id':path.stem,'type':'image','path':str(path.relative_to(project)),'source_tool':'image_selector','scene_id':f'core-{path.stem}','model':'gpt-image-2','provider':'openai','generation_mode':'image','status':'approved','origin_type':'generated','historical_treatment':'dramatic_reconstruction','asset_group_id':'character_reference','reused_by_scene_ids':[],'rights_note':'project_generated'})
    for slug,group,_ in SCENES:
        path=scene_dir/f'{slug}.png'
        assets.append({'id':slug,'type':'image' if group!='map' else 'diagram','path':str(path.relative_to(project)),'source_tool':'image_selector','scene_id':f'core-{slug}','model':'gpt-image-2','provider':'openai','generation_mode':'image','status':'approved','origin_type':'generated','historical_treatment':'documentary' if group in {'map','diagram'} else 'dramatic_reconstruction','asset_group_id':group,'reused_by_scene_ids':[],'rights_note':'project_generated'})
    manifest={'version':'1.0','assets':assets,'total_cost_usd':result['totals']['cost'],'metadata':{'pipeline':'historical-story','stage':'core_assets','provider_policy':'openai:gpt-image-2'}}
    (project/'artifacts/asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'core_assets':len(assets),'characters':sum(x['asset_group_id']=='character_reference' for x in assets),'scene_assets':len(assets)-sum(x['asset_group_id']=='character_reference' for x in assets)},ensure_ascii=False))

def shot_assets(project: Path) -> None:
    load_dotenv('/Users/fanshu01/rep/github/OpenMontage/.env')
    manifest_path = project / 'artifacts/asset_manifest.json'
    plan = json.loads((project / 'artifacts/shot_asset_plan.json').read_text())
    manifest = json.loads(manifest_path.read_text())
    by_group = {}
    for item in manifest.get('assets', []):
        by_group.setdefault(item.get('asset_group_id'), []).append(str(project / item['path']))
    refs = (by_group.get('character_reference', [])[:1]
            + by_group.get('scene_plate', [])[:1]
            + by_group.get('map', [])[:1]
            + by_group.get('diagram', [])[:1])
    out_dir = project / 'assets/images/boards'
    out_dir.mkdir(parents=True, exist_ok=True)
    requests=[]
    for shot in plan.get('shots', []):
        board_id = shot.get('visual_board_id') or shot['shot_id']
        requests.append({
            'prompt': shot['prompt'],
            'generation_mode': 'edit',
            'image_paths': refs,
            'preferred_provider': 'openai',
            'allowed_providers': ['openai'],
            'model': 'gpt-image-2',
            'size': '1280x720',
            'quality': 'medium',
            'output_format': 'png',
            'n': 1,
            'output_path': str(out_dir / f'{board_id.lower()}.png'),
            'task_context': {'pipeline':'historical-story','stage':'shot_assets','visual_board_id':board_id},
        })
    result = ImageBatchRunner().run(requests, max_workers=3, max_retries=2)
    failed=[x for x in result['results'] if x['status']=='failed']
    if failed: raise SystemExit(f'shot_assets failed: {failed}')
    core_assets=[x for x in manifest.get('assets', []) if x.get('subtype') != 'final_board']
    for shot in plan.get('shots', []):
        board_id=shot.get('visual_board_id') or shot['shot_id']
        path=out_dir/f'{board_id.lower()}.png'
        core_assets.append({
            'id': board_id, 'type':'image', 'path':str(path.relative_to(project)),
            'source_tool':'image_selector', 'scene_id':board_id, 'model':'gpt-image-2',
            'provider':'openai', 'prompt':shot['prompt'], 'generation_mode':'image',
            'status':'approved', 'origin_type':'generated',
            'historical_treatment':'dramatic_reconstruction', 'asset_group_id':'final_board',
            'reused_by_scene_ids':[board_id], 'rights_note':'project_generated',
        })
    manifest['assets']=core_assets
    manifest['total_cost_usd']=round(float(manifest.get('total_cost_usd',0))+float(result['totals']['cost']),6)
    manifest['metadata'].update({'stage':'shot_assets','unique_final_boards':len(plan.get('shots',[]))})
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'shot_assets':len(plan.get('shots',[])),'cost':result['totals']['cost']},ensure_ascii=False))

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('stage',choices=['core_assets','shot_assets']); p.add_argument('--project-dir',required=True); a=p.parse_args()
    (core if a.stage=='core_assets' else shot_assets)(Path(a.project_dir).resolve())
