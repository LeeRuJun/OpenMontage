"""Official historical-story narration timing stage."""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone
import json,re,subprocess
from pathlib import Path
from dotenv import load_dotenv
from tools.audio.minimax_tts import MiniMaxTTS

def main(project: Path) -> None:
    load_dotenv('/Users/fanshu01/rep/github/OpenMontage/.env')
    text=(project/'artifacts/script.md').read_text(encoding='utf-8')
    script_revision=hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    parts=re.split(r'^## ',text,flags=re.M)[1:]; segments=[]
    for index,part in enumerate(parts,1):
        lines=part.splitlines(); title=lines[0].split('（',1)[0].strip(); body=[]
        for line in lines[1:]:
            if line.startswith(('证据：','>','-','## Sources','http')): continue
            body.append(line)
        narration=re.sub(r'\s+','', '\n'.join(body)).strip()
        if narration: segments.append((index,title,narration))
    out_dir=project/'assets/audio/narration_segments'; out_dir.mkdir(parents=True,exist_ok=True); tts=MiniMaxTTS(); results=[]
    for index,title,narration in segments:
        out=out_dir/f'{index:02d}.mp3'
        result=tts.execute({'text':narration,'model':'speech-2.8-hd','voice_id':'Chinese (Mandarin)_Gentle_Senior','speed':0.95,'vol':1,'pitch':0,'emotion':'calm','format':'mp3','sample_rate':32000,'bitrate':128000,'language_boost':'Chinese','output_path':str(out),'metadata_path':str(out.with_suffix('.json'))})
        if not result.success: raise SystemExit(result.error or f'TTS failed: {index}')
        probe=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)],text=True)); results.append({'index':index,'title':title,'chars':len(narration),'path':str(out.relative_to(project)),'duration_seconds':probe})
    concat=project/'artifacts/narration_concat.txt'; concat.write_text('\n'.join(f"file \'{(project/x['path']).resolve()}\'" for x in results)+'\n')
    final=project/'assets/audio/narration_full.mp3'; subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(final)],text=True)); start=0; sections=[]
    for item in results: sections.append({'id':f"section-{item['index']}",'start_seconds':round(start,3),'end_seconds':round(start+item['duration_seconds'],3)}); start+=item['duration_seconds']
    timing={'version':'1.0','mode':'full_longform','script_revision':script_revision,'narration_asset_id':'narration-full-minimax','narration_path':'assets/audio/narration_full.mp3','measured_duration_seconds':duration,'character_count':sum(x['chars'] for x in results),'word_timestamps':[],'sections':sections,'acts':[{'id':x['id'],'title':results[i]['title'],'start_seconds':x['start_seconds'],'end_seconds':x['end_seconds']} for i,x in enumerate(sections)],'alignment_confidence':0.9,'timing_locked_at':datetime.now(timezone.utc).isoformat()}
    (project/'artifacts/narration_timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n'); (project/'artifacts/narration_generation.json').write_text(json.dumps({'provider':'minimax_tts','model':'speech-2.8-hd','voice_id':'Chinese (Mandarin)_Gentle_Senior','segments':results,'output':str(final),'duration_seconds':duration,'contract_ok':1320<=duration<=1500},ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'duration_seconds':duration,'segments':len(results)},ensure_ascii=False))

if __name__=='__main__':
    import argparse; p=argparse.ArgumentParser(); p.add_argument('--project-dir',required=True); a=p.parse_args(); main(Path(a.project_dir).resolve())
