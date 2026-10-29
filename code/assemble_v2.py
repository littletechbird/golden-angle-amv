#!/usr/bin/env python3
"""Assemble v2 with HARD guard.
Sources: code_v2 > code; nature: hf_esrgan (Real-ESRGAN) > hf_4k (lanczos PROVISIONAL) > hf.
Re-runnable: drop ESRGAN plates into bank/hf_esrgan/ and re-run — cutlist unchanged.
"""
from __future__ import annotations
import json, subprocess, sys, re
from pathlib import Path
import numpy as np
from PIL import Image

import os
ROOT=Path(os.environ.get('GA_ROOT', Path(__file__).resolve().parent.parent))
CUT=json.loads((Path(__file__).resolve().parent/'cutlist.json').read_text())['cutlist']
AUDIO=Path(os.environ.get('GA_AUDIO', ROOT/'golden-angle-v1.mp3'))  # song not in repo
SEG=ROOT/'exports/v2/segments'; SEG.mkdir(parents=True, exist_ok=True)
OUT=ROOT/'exports/v2'
W,H,FPS=3840,2160,24
AUDIO_DUR=318.672
FORBIDDEN=re.compile(r'(still_pad|kenburns|zoompan|tpad\s*=\s*stop_mode\s*=\s*clone|loop=-1|freeze\s*=)', re.I)

def fatal(m):
    print('FATAL GUARD:', m, file=sys.stderr); sys.exit(2)

def probe(path):
    r=subprocess.run(['ffprobe','-v','error','-select_streams','v:0',
                      '-show_entries','stream=width,height,duration:format=duration','-of','json',str(path)],
                     capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr)
    j=json.loads(r.stdout); st=j['streams'][0]
    return int(st['width']), int(st['height']), float(st.get('duration') or j['format']['duration'])

def find_src(sid):
    """Resolve plate. Nature prefers Real-ESRGAN bank when present (GPU-desk swap).
    Drop finished plates into bank/hf_esrgan/{id}.mp4 and re-run this script — no cutlist edit.
    """
    if sid.startswith('h_'):
        for p in [ROOT/'bank/hf_esrgan'/f'{sid}.mp4',  # Real-ESRGAN from the GPU desk (preferred)
                  ROOT/'bank/hf_4k'/f'{sid}.mp4',       # provisional lanczos
                  ROOT/'bank/hf'/f'{sid}.mp4']:
            if p.exists(): return p
    else:
        for p in [ROOT/'bank/code_v2'/f'{sid}.mp4', ROOT/'bank/code'/f'{sid}.mp4']:
            if p.exists(): return p
    fatal(f'missing {sid}')

def motion_score(path):
    w,h,dur=probe(path)
    if dur<0.4: fatal(f'{path.name} too short')
    diffs=[]
    for ta,tb in [(dur*0.12,dur*0.5),(dur*0.5,dur*0.88),(dur*0.12,dur*0.88)]:
        a=SEG/f'_a_{path.stem}.png'; b=SEG/f'_b_{path.stem}.png'
        subprocess.run(['ffmpeg','-y','-ss',str(ta),'-i',str(path),'-frames:v','1',str(a)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(['ffmpeg','-y','-ss',str(tb),'-i',str(path),'-frames:v','1',str(b)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        A=np.asarray(Image.open(a).convert('L').resize((320,180)),np.float32)
        B=np.asarray(Image.open(b).convert('L').resize((320,180)),np.float32)
        mask=(A>12)|(B>12)
        diffs.append(float(np.mean(np.abs(A-B)[mask])) if mask.sum()>=30 else float(np.mean(np.abs(A-B))))
        a.unlink(missing_ok=True); b.unlink(missing_ok=True)
    return sum(diffs)/len(diffs)

def make_seg(sid, need, idx):
    src=find_src(sid); w,h,sd=probe(src)
    stretch=need/sd
    if stretch>1.45: fatal(f'{sid}: pocket {need:.2f} > 1.45× src {sd:.2f}')
    vf=[]
    if w!=W or h!=H: vf.append(f'scale={W}:{H}:flags=lanczos')
    if abs(stretch-1)>0.02: vf.append(f'setpts={stretch:.6f}*PTS')
    vf += [f'fps={FPS}', f'trim=duration={need:.6f}', 'setpts=PTS-STARTPTS']
    vf=','.join(vf)
    if FORBIDDEN.search(vf): fatal(f'forbidden in vf {vf}')
    out=SEG/f'{idx:03d}_{sid}.mp4'
    if out.exists():
        try:
            _,_,od=probe(out)
            if od+0.1>=need*0.96 and out.stat().st_size>100000:
                print(f'  RESUME {idx:03d} {sid}', flush=True); return out, vf
        except: pass
    r=subprocess.run(['ffmpeg','-y','-i',str(src),'-vf',vf,'-an','-c:v','libx264','-pix_fmt','yuv420p',
                      '-crf','16','-preset','veryfast','-t',f'{need:.6f}',str(out)], capture_output=True, text=True)
    if r.returncode: fatal(f'{sid} ffmpeg: {r.stderr[-400:]}')
    return out, vf

def main():
    print('=== GUARD PREFLIGHT v2 ===', flush=True)
    used={}; paths=[]; flog=[]
    for i,c in enumerate(CUT):
        sid=c['id']; need=float(c['dur'])
        used[sid]=used.get(sid,0)+1
        if used[sid]>1: fatal(f'reuse {sid}')
        src=find_src(sid)
        ms=motion_score(src)
        print(f'  motion {sid}: {ms:.2f}', flush=True)
        if ms<1.5: fatal(f'{sid}: near-still {ms:.2f}')
        seg,vf=make_seg(sid, need, i)
        paths.append(seg); flog.append((sid,vf))
        print(f'  SEG {i:02d} {sid} need={need:.2f}', flush=True)
    print(f'UNIQUE OK {len(used)}; NO STILL/KB/TPAD', flush=True)
    cl=OUT/'concat.txt'; cl.write_text(''.join(f"file '{p}'\n" for p in paths))
    vo=OUT/'master_video_only.mp4'
    r=subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(cl),'-c','copy','-movflags','+faststart',str(vo)],capture_output=True,text=True)
    if r.returncode: fatal(r.stderr[-500:])
    # Prefer ESRGAN; drop PROVISIONAL only when EVERY nature plate is from hf_esrgan
    hf_ids=[c['id'] for c in CUT if c['id'].startswith('h_')]
    esrgan_all=all((ROOT/'bank/hf_esrgan'/f'{hid}.mp4').exists() for hid in hf_ids)
    if esrgan_all:
        master=OUT/'golden_angle_master_4k_v2.mp4'
        print(f'ESRGAN complete ({len(hf_ids)} plates) — master NON-PROVISIONAL', flush=True)
    else:
        master=OUT/'golden_angle_master_4k_v2_PROVISIONAL_lanczosHF.mp4'
        missing=[hid for hid in hf_ids if not (ROOT/'bank/hf_esrgan'/f'{hid}.mp4').exists()]
        print(f'ESRGAN incomplete missing={missing[:5]}... → PROVISIONAL lanczos', flush=True)
    r=subprocess.run(['ffmpeg','-y','-i',str(vo),'-i',str(AUDIO),'-map','0:v:0','-map','1:a:0',
                      '-c:v','copy','-c:a','aac','-b:a','320k','-shortest','-movflags','+faststart',str(master)],
                     capture_output=True,text=True)
    if r.returncode: fatal(r.stderr[-500:])
    print('MASTER', master, master.stat().st_size, probe(master)[2], flush=True)
    review=OUT/'golden_angle_review_1080p_v2.mp4'
    for crf in (16,18,20):
        subprocess.run(['ffmpeg','-y','-i',str(master),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264',
                        '-pix_fmt','yuv420p','-crf',str(crf),'-preset','veryfast','-c:a','aac','-b:a','160k',
                        '-movflags','+faststart',str(review)], check=True)
        if review.stat().st_size<100_000_000: break
    teaser=OUT/'golden_angle_teaser_40s_1080p_v2.mp4'
    # final chorus ~257.4
    subprocess.run(['ffmpeg','-y','-ss','257.4','-t','40','-i',str(master),'-vf','scale=1920:1080:flags=lanczos',
                    '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','veryfast','-c:a','aac','-b:a','192k',
                    '-movflags','+faststart',str(teaser)], check=True)
    # Contact sheet v2: mid-frame from each segment
    contact_dir=OUT/'contact_frames'; contact_dir.mkdir(exist_ok=True)
    thumbs=[]
    for i,c in enumerate(CUT):
        sid=c['id']; seg=paths[i]
        thumb=contact_dir/f'{i:03d}_{sid}.jpg'
        subprocess.run(['ffmpeg','-y','-ss',str(float(c['dur'])*0.45),'-i',str(seg),'-frames:v','1',
                        '-vf','scale=320:180:flags=lanczos',str(thumb)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if thumb.exists(): thumbs.append(thumb)
    cols=5; rows=(len(thumbs)+cols-1)//cols
    sheet=Image.new('RGB',(cols*320, rows*180),(12,12,12))
    for i,t in enumerate(thumbs):
        sheet.paste(Image.open(t).convert('RGB'), ((i%cols)*320,(i//cols)*180))
    contact=OUT/'golden_angle_contact_v2.jpg'
    sheet.save(contact, quality=90)
    # Source map for ESRGAN swap re-runs
    src_map={}
    for citem in CUT:
        sid=citem['id']; src=find_src(sid)
        kind='esrgan' if 'hf_esrgan' in str(src) else ('hf_4k' if 'hf_4k' in str(src) else ('hf' if sid.startswith('h_') else 'code_v2'))
        src_map[sid]={'path':str(src),'kind':kind}
    (OUT/'source_map_v2.json').write_text(json.dumps(src_map, indent=2))
    (ROOT/'bank/hf_esrgan').mkdir(parents=True, exist_ok=True)
    (ROOT/'bank/hf_esrgan/README.txt').write_text(
        "Drop Real-ESRGAN 4K plates here as h_<name>.mp4 (same ids as cutlist).\n"
        "Then re-run: python3 scripts/assemble_v2.py\n"
        "find_src prefers hf_esrgan > hf_4k > hf. Cutlist unchanged.\n")
    (OUT/'guard_report_v2.json').write_text(json.dumps({'status':'PASSED','unique':list(used),'filters':flog,
        'master':str(master),'review':str(review),'teaser':str(teaser),'contact':str(contact),
        'source_map':str(OUT/'source_map_v2.json'),
        'hf_swap':'Place Real-ESRGAN plates in bank/hf_esrgan/ then re-run assemble_v2.py'}, indent=2))
    print('GUARD PASSED v2', flush=True)
    print('REVIEW', review.stat().st_size, 'TEASER', teaser.stat().st_size, 'CONTACT', contact, flush=True)

if __name__=='__main__':
    main()
