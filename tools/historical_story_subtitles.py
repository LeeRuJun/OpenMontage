"""Generate and burn canonical Chinese subtitles for historical-story output."""
from __future__ import annotations
import argparse, re, shutil, subprocess
from pathlib import Path

def ts(seconds: float) -> str:
    ms = int(round(seconds * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def make_srt(project: Path, duration: float) -> Path:
    text=(project/'artifacts/script.md').read_text(encoding='utf-8')
    sections=re.split(r'^## ',text,flags=re.M)[1:]
    chunks=[]
    for section in sections:
        lines=section.splitlines(); body=[]
        for line in lines[1:]:
            if line.startswith(('证据：','>','-','## Sources','http')): continue
            body.append(line.strip())
        clean=re.sub(r'\s+','', ''.join(body))
        for part in re.split(r'(?<=[。！？；])',clean):
            part=part.strip()
            while len(part)>24:
                cut=part[:24].rfind('，')
                if cut<12: cut=24
                chunks.append(part[:cut+1]); part=part[cut+1:]
            if part: chunks.append(part)
    total_chars=sum(len(x) for x in chunks) or 1
    cursor=0.0; rows=[]
    for i,part in enumerate(chunks,1):
        d=duration*len(part)/total_chars
        rows.append(f"{i}\n{ts(cursor)} --> {ts(cursor+d)}\n{part}\n")
        cursor+=d
    out=project/'assets/audio/narration.zh-CN.srt'; out.write_text('\n'.join(rows),encoding='utf-8'); return out

def main(project: Path) -> None:
    source=project/'renders/historical_story_final.mp4'; final=project/'renders/historical_story_final_subtitled.mp4'
    if not source.is_file(): raise SystemExit(f'missing render: {source}')
    ffprobe='/opt/homebrew/opt/ffmpeg-full/bin/ffprobe'
    duration=float(subprocess.check_output([ffprobe,'-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(source)],text=True))
    srt=make_srt(project,duration)
    ffmpeg='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
    subtitle_filter=rf"subtitles=filename='{srt}':force_style='FontName=PingFang SC\,FontSize=20\,PrimaryColour=&H00F0DFC5\,OutlineColour=&H0017151A\,BorderStyle=1\,Outline=2\,Shadow=0\,Alignment=2\,MarginV=55'"
    subprocess.run([ffmpeg,'-y','-i',str(source),'-vf',subtitle_filter,'-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','medium','-crf','18','-c:a','copy','-movflags','+faststart',str(final)],check=True)
    print({'output':str(final),'subtitle_path':str(srt),'duration_seconds':duration})

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',required=True); a=p.parse_args(); main(Path(a.project_dir).resolve())
