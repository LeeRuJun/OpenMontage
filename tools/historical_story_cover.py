"""Generate the approved YouTube cover for the historical-story pipeline."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from dotenv import load_dotenv
from tools.graphics.openai_image import OpenAIImage

def main(project: Path) -> None:
    load_dotenv('/Users/fanshu01/rep/github/OpenMontage/.env')
    out=project/'assets/images/cover/youtube_cover.png'; out.parent.mkdir(parents=True,exist_ok=True)
    prompt=("Cinematic YouTube documentary cover background for a Chinese history story about Qian Chu of Wuyue surrendering territory to Northern Song in 978. "
      "Landscape 16:9 composition. Right side: a restrained distant silhouette of a late-tenth-century Jiangnan king standing beside a lacquered wooden table with a jade seal, an unsealed memorial, rolled territorial map and bronze lamp. "
      "Behind him: misty Jiangnan waterways, low ancient city walls and layered parchment map lines fading into the horizon. "
      "Left 42 percent must be quiet dark ink negative space for deterministic Chinese title overlay. "
      "Deep charcoal ink, warm rice-paper, restrained Northern Song vermilion accent, historically grounded material detail, cinematic documentary lighting. "
      "No readable text, no letters, no digits, no logos, no modern objects, no collage, one coherent scene, no split screen.")
    result=OpenAIImage().execute({'model':'gpt-image-2','prompt':prompt,'size':'1536x864','quality':'high','output_format':'png','n':1,'output_path':str(out)})
    if not result.success: raise SystemExit(result.error or 'cover generation failed')
    manifest={'version':'1.0','asset_id':'youtube_cover','path':str(out.relative_to(project)),'provider':'openai','model':'gpt-image-2','prompt':prompt,'status':'approved','historical_treatment':'illustrative','text_overlay':'deterministic post-production overlay','cover_plan_ref':'cover_plan.json'}
    (project/'artifacts/cover_asset.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(out),'provider':'openai','model':'gpt-image-2'},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',required=True); a=p.parse_args(); main(Path(a.project_dir).resolve())
