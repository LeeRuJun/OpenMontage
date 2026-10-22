"""Generate and compose the approved YouTube cover."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from tools.graphics.openai_image import OpenAIImage

PROMPT=("Cinematic YouTube documentary cover background for a Chinese history story about Qian Chu of Wuyue surrendering territory to Northern Song in 978. "
"Landscape 16:9 composition. Right side: a restrained distant silhouette of a late-tenth-century Jiangnan king standing beside a lacquered wooden table with a jade seal, an unsealed memorial, rolled territorial map and bronze lamp. "
"Behind him: misty Jiangnan waterways, low ancient city walls and layered parchment map lines fading into the horizon. "
"Left 42 percent must be quiet dark ink negative space for deterministic Chinese title overlay. "
"Deep charcoal ink, warm rice-paper, restrained Northern Song vermilion accent, historically grounded material detail, cinematic documentary lighting. "
"No readable text, no letters, no digits, no logos, no modern objects, no collage, one coherent scene, no split screen.")

FONT='/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc'

def main(project: Path) -> None:
    load_dotenv('/Users/fanshu01/rep/github/OpenMontage/.env')
    out=project/'assets/images/cover/youtube_cover.png'; bg=project/'assets/images/cover/youtube_cover_bg.png'; out.parent.mkdir(parents=True,exist_ok=True)
    if not bg.exists():
        if out.exists(): shutil.copyfile(out,bg)
        else:
            result=OpenAIImage().execute({'model':'gpt-image-2','prompt':PROMPT,'size':'1536x864','quality':'high','output_format':'png','n':1,'output_path':str(bg)})
            if not result.success: raise SystemExit(result.error or 'cover generation failed')
    image=Image.open(bg).convert('RGBA'); overlay=Image.new('RGBA',image.size,(0,0,0,0)); draw=ImageDraw.Draw(overlay)
    draw.rectangle((0,0,800,image.height),fill=(20,17,20,135)); draw.rectangle((72,190,132,196),fill=(184,92,56,255))
    small=ImageFont.truetype(FONT,30,index=0); title=ImageFont.truetype(FONT,76,index=0); sub=ImageFont.truetype(FONT,42,index=0); meta=ImageFont.truetype(FONT,25,index=0)
    draw.text((72,95),'读点东西 · 历史故事',font=small,fill=(196,91,61,255),spacing=8)
    draw.text((72,235),'钱俶纳土归宋',font=title,fill=(244,229,201,255),stroke_width=2,stroke_fill=(20,17,20,220))
    draw.text((72,345),'一个吴越国王',font=sub,fill=(244,229,201,255),stroke_width=1,stroke_fill=(20,17,20,220))
    draw.text((72,410),'为什么交出自己的国家？',font=sub,fill=(244,229,201,255),stroke_width=1,stroke_fill=(20,17,20,220))
    draw.text((72,555),'五代十国余波 · 北宋初年 · 978年',font=meta,fill=(206,184,148,255))
    Image.alpha_composite(image,overlay).convert('RGB').save(out,quality=95)
    manifest={'version':'1.0','asset_id':'youtube_cover','path':str(out.relative_to(project)),'background_path':str(bg.relative_to(project)),'provider':'openai','model':'gpt-image-2','prompt':PROMPT,'status':'approved','historical_treatment':'illustrative','text_overlay':'deterministic Pillow overlay','cover_plan_ref':'cover_plan.json'}
    (project/'artifacts/cover_asset.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(out),'background':str(bg),'overlay':'deterministic','provider':'openai'},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',required=True); a=p.parse_args(); main(Path(a.project_dir).resolve())
