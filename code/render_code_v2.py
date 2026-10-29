#!/usr/bin/env python3
"""Native 4K math v2: 2× supersampled overlays, fat seeds, nature-matched grade."""
from __future__ import annotations
import math, subprocess, sys, json, os, time, errno
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(os.environ.get('GA_ROOT', Path(__file__).resolve().parent.parent))
OUT = Path(os.environ.get('GA_CODE_OUT', str(ROOT/'bank/code_v2'))); OUT.mkdir(parents=True, exist_ok=True)
LOCKDIR = OUT/'_locks'; LOCKDIR.mkdir(parents=True, exist_ok=True)
W, H, FPS = 3840, 2160, 24
SS = 2  # supersample factor for vector/seed core layer
SW, SH = W*SS, H*SS
GOLDEN = 137.5077640500378
# Nature-matched palette (golden-hour, lifted blacks)
MAGMA = np.array([1.,.45,.10], np.float32)
GOLD  = np.array([1.,.84,.32], np.float32)
CYAN  = np.array([.20,.92,.95], np.float32)
TEAL  = np.array([.25,.78,.82], np.float32)
WHITE = np.array([1.,.97,.93], np.float32)
AMBER = np.array([1.,.62,.18], np.float32)
# Background: not pure black — match nature shadow floor
BG = np.array([0.09, 0.075, 0.055], np.float32)  # warm lifted floor ~nature shadows

YY, XX = np.ogrid[:H, :W]
VIG = np.clip(1.18 - np.sqrt((XX-W/2)**2+(YY-H/2)**2)/(min(W,H)*0.95), 0.55, 1.).astype(np.float32)
D2C = ((XX-W/2)**2 + (YY-H/2)**2).astype(np.float32)

def ease(t):
    t=float(np.clip(t,0,1)); return t*t*(3-2*t)

def vogel(n, angle=GOLDEN, scale=None):
    if scale is None: scale=(min(W,H)*0.44)/math.sqrt(max(n,1))
    i=np.arange(n,dtype=np.float32); th=np.deg2rad(angle)*i; r=scale*np.sqrt(i)
    return r*np.cos(th), r*np.sin(th), i

def splat(px, py, st, col):
    """Half-res multi-scale glow + fat cores. 2× SS via oversized stamps downsampled."""
    sw, sh = W//2, H//2
    glow=np.zeros((sh,sw,3),np.float32)
    px=np.asarray(px,np.float32); py=np.asarray(py,np.float32)
    s=np.asarray(st,np.float32)*1.75
    if np.asarray(col).ndim==1: col=np.broadcast_to(col,(len(px),3)).copy()
    else: col=np.asarray(col,np.float32)
    # scatter at half-res with neighborhood for fat seeds (3x3)
    ix=np.clip((px*(sw/W)).astype(np.int32),1,sw-2)
    iy=np.clip((py*(sh/H)).astype(np.int32),1,sh-2)
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            wgt = 1.0 if dx==0 and dy==0 else 0.45
            for c in range(3): np.add.at(glow[:,:,c],(iy+dy,ix+dx),s*col[:,c]*wgt)
    g=(gaussian_filter(glow,(1.2,1.2,0))*2.6
       +gaussian_filter(glow,(3.5,3.5,0))*1.8
       +gaussian_filter(glow,(10,10,0))*1.1)
    # 2× SS: half-res glow (1920×1080) → LANCZOS to 4K (true 2× supersample, no 8K intermediate)
    img=np.asarray(Image.fromarray(np.clip(g*255,0,255).astype(np.uint8),'RGB').resize((W,H),Image.LANCZOS)).astype(np.float32)/255
    # bright fat cores at full res (vectorized neighborhood via padded buffer)
    ix4=np.clip(px.astype(np.int32),0,W-1); iy4=np.clip(py.astype(np.int32),0,H-1)
    s2=np.minimum(s,2.2)
    core=np.zeros((H+2,W+2,3),np.float32)
    for c in range(3):
        np.add.at(core[:,:,c],(iy4+1,ix4+1),s2*col[:,c]*1.15)
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dx==0 and dy==0: continue
                np.add.at(core[:,:,c],(iy4+1+dy,ix4+1+dx),s2*col[:,c]*0.35)
    img = np.clip(img + core[1:-1,1:-1], 0, 1)
    return img

def finish(img, rng, grain=0.04, lift=1.77):
    # Nature-matched grade: brighter fill, warm mids, soft bloom, lifted blacks
    img = img*lift + BG*1.35
    # soft ambient fill so cuts into nature aren't a black punch
    amb = np.exp(-D2C/(2*(min(W,H)*0.55)**2))[:,:,None]
    img = img + amb * np.array([0.10, 0.08, 0.045], np.float32)
    hi = np.clip(img-0.38,0,1)
    img = img + gaussian_filter(hi,(5,5,0))*0.7
    img = img*VIG[:,:,None]
    noise = (rng.random((H,W,1),np.float32)-0.5)*grain
    dither = (rng.integers(0,3,(H,W,1),dtype=np.int16).astype(np.float32)-1)*(1/255.0)
    img = img + noise + dither
    img = img * np.array([1.08, 1.02, 0.90], np.float32)
    img = np.clip(img, 0, 1)
    img = np.power(img, 0.85)  # lift shadows toward nature midtones
    return np.clip(img, 0, 1)


def shot_claimed(sid, path, n):
    """Skip if done, or if another worker (local or remote GPU desk) holds a lock."""
    if probe_ok(path, n/FPS*0.85):
        return 'done'
    # Remote worker: bank/code_v2/<shot>.lock (file or dir); ours: _locks/<shot>.lock
    for lk in (OUT/f'{sid}.lock', LOCKDIR/f'{sid}.lock'):
        if lk.exists():
            # if OUR mkdir lock and we own this process rendering to partial, encode handles it
            meta=lk/('owner') if lk.is_dir() else None
            owner=''
            if lk.is_file():
                try: owner=lk.read_text().strip()
                except: owner='lock'
            elif meta and meta.exists():
                try: owner=meta.read_text().strip()
                except: owner=''
            # Remote-worker claim — always skip
            if 'remote' in owner.lower() or (lk==OUT/f'{sid}.lock' and lk.exists()):
                return f'claimed:{owner or lk.name}'
    return None

def probe_ok(path, min_dur=0.5):
    if not path.exists() or path.stat().st_size<300_000: return False
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)],capture_output=True,text=True)
    try: return float(r.stdout.strip())>=min_dur
    except: return False

def encode(path, gen, n):
    if probe_ok(path, n/FPS*0.85): return 'skip'
    lock = LOCKDIR/f'{path.stem}.lock'
    # mkdir-based exclusive lock (cross-process); skip if another worker holds it
    for _ in range(3):
        try:
            os.mkdir(lock)
            break
        except FileExistsError:
            # stale lock > 45min → steal; else skip (other worker owns it)
            try: age=time.time()-lock.stat().st_mtime
            except FileNotFoundError: continue
            if age>2700:
                try: os.rmdir(lock); continue
                except OSError: pass
            print(f'LOCK-BUSY {path.stem}', flush=True)
            return 'lock-busy'
    else:
        return 'lock-busy'
    try:
        if probe_ok(path, n/FPS*0.85): return 'skip'
        tmp=path.with_suffix('.partial.mp4')
        cmd=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0',
             '-c:v','libx264','-pix_fmt','yuv420p','-crf','14','-preset','veryfast','-movflags','+faststart',str(tmp)]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for fr in gen(n):
                p.stdin.write((np.clip(fr,0,1)*255).astype(np.uint8).tobytes())
            p.stdin.close(); err=p.stderr.read(); rc=p.wait()
        except BrokenPipeError:
            err=p.stderr.read(); rc=p.wait()
            raise RuntimeError(err[-800:].decode('utf-8','ignore'))
        if rc!=0:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(err[-800:].decode('utf-8','ignore'))
        tmp.replace(path)
        return path.stat().st_size
    finally:
        try: os.rmdir(lock)
        except OSError: pass

def g_intro_seed(n):
    rng=np.random.default_rng(201)
    for i in range(n):
        t=i/(n-1); r=18+220*ease(t)
        img=np.broadcast_to(BG,(H,W,3)).copy()*0
        img=img+np.exp(-D2C/(2*r*r))[:,:,None]*(GOLD*1.15+WHITE*0.4)*(0.7+0.4*t)
        img+=np.exp(-D2C/(2*(r*2.2)**2))[:,:,None]*AMBER*0.55*t
        img+=np.exp(-D2C/(2*(r*4.5)**2))[:,:,None]*MAGMA*0.28*t
        a=t*2*math.pi; x=W/2+math.cos(a)*r*0.4; y=H/2+math.sin(a)*r*0.28
        img+=np.exp(-((XX-x)**2+(YY-y)**2)/(2*14**2))[:,:,None]*(CYAN*0.85)*ease(t)
        yield finish(img,rng,lift=1.52)

def g_intro_pair(n):
    rng=np.random.default_rng(202)
    for i in range(n):
        t=i/(n-1); spin=t*0.95; ang=math.radians(-90+GOLDEN)+spin
        dist=140+480*ease(t)
        img=np.exp(-D2C/(2*28**2))[:,:,None]*(GOLD+WHITE*0.35)
        img+=np.exp(-D2C/(2*85**2))[:,:,None]*AMBER*0.45
        x=W/2+math.cos(ang)*dist; y=H/2+math.sin(ang)*dist*0.82
        img+=np.exp(-((XX-x)**2+(YY-y)**2)/(2*26**2))[:,:,None]*(TEAL*0.55+GOLD*0.5)
        img+=np.exp(-((XX-x)**2+(YY-y)**2)/(2*70**2))[:,:,None]*CYAN*0.4
        # SS thick arms
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        d.line([(SW/2,SH/2),(x*SS,y*SS)],fill=(50,235,255),width=14*SS)
        for k in range(18):
            aa=math.radians(-90)+k/17*math.radians(GOLDEN)*ease(t)
            d.line([(SW/2,SH/2),(SW/2+math.cos(aa)*dist*SS*0.55,SH/2+math.sin(aa)*dist*SS*0.55*0.82)],fill=(255,195,70),width=5*SS)
        img+=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255*(0.55+0.45*t)
        yield finish(img,rng,lift=1.5)

def g_fib(n, mode='syll'):
    rng=np.random.default_rng(203 if mode=='syll' else 204)
    mx=180 if mode=='syll' else 560
    for i in range(n):
        t=i/(n-1); ns=max(1,int(1+ease(t)*mx))
        xs,ys,idx=vogel(ns)
        rot=t*(2.6 if mode=='syll' else 0.85); ca,sa=math.cos(rot),math.sin(rot)
        zoom=0.6+1.15*ease(t) if mode=='syll' else 0.9+0.45*t
        cx=W/2+70*math.sin(t*2); cy=H/2+45*math.cos(t*1.6)
        xr,yr=(xs*ca-ys*sa)*zoom,(xs*sa+ys*ca)*zoom
        drop=np.zeros_like(ys)
        if mode=='syll':
            age=(ns-1-idx)/max(ns,1); u=np.clip(age*10,0,1); ee=u*u*(3-2*u)
            drop=-300*(1-ee)*(age<0.25)
        px,py=cx+xr, cy+yr+drop
        st=1.0+0.8*(1-idx/max(ns,1))
        col=np.zeros((ns,3),np.float32)
        u=idx/max(ns-1,1)
        col[:]=GOLD*(1-u)[:,None]+AMBER*u[:,None]*0.75+MAGMA*0.25
        newest=max(1,ns//5); col[-newest:]=CYAN*0.8+WHITE*0.25
        img=splat(px,py,st,col)
        img+=np.exp(-((XX-cx)**2+(YY-cy)**2)/(2*36**2))[:,:,None]*(WHITE*0.55+GOLD*0.35)
        yield finish(img,rng,lift=1.54)

def g_gaps(n):
    rng=np.random.default_rng(205); xs,ys,idx=vogel(1000)
    for i in range(n):
        t=i/(n-1); rot=t*0.75; ca,sa=math.cos(rot),math.sin(rot)
        zoom=1.08+0.22*math.sin(t*math.pi)
        xr,yr=(xs*ca-ys*sa)*zoom,(xs*sa+ys*ca)*zoom
        col=np.broadcast_to(GOLD*0.8+AMBER*0.3,(1000,3)).copy()
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        for k in range(12):
            a=-math.pi/2+k*math.pi/6+t*0.4
            bri=int(200+55*math.sin(t*4+k))
            d.line([(SW/2,SH/2),(SW/2+math.cos(a)*SH*0.55,SH/2+math.sin(a)*SH*0.55)],fill=(bri,int(bri*0.78),50),width=4*SS)
        img=splat(W/2+xr,H/2+yr,0.7+0.6*(1-idx/1000),col)
        img+=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255*(0.3+0.4*abs(math.sin(t*math.pi)))
        yield finish(img,rng,lift=1.52)

def g_voronoi(n):
    rng=np.random.default_rng(206)
    for i in range(n):
        t=i/(n-1); ns=55+int(130*t)
        xs,ys,_=vogel(ns, scale=(min(W,H)*0.42)/math.sqrt(max(ns,1)))
        rot=t*0.45; ca,sa=math.cos(rot),math.sin(rot)
        sx,sy=xs*ca-ys*sa+W/2, xs*sa+ys*ca+H/2
        sw,sh=W//5,H//5; gy,gx=np.mgrid[0:sh,0:sw]; gx=gx*(W/sw); gy=gy*(H/sh)
        dist=np.full((sh,sw),1e12,np.float32); lab=np.zeros((sh,sw),np.int32)
        for k in range(ns):
            d=(gx-sx[k])**2+(gy-sy[k])**2; m=d<dist; dist[m]=d[m]; lab[m]=k
        cols=np.zeros((ns,3),np.float32)
        for k in range(ns):
            u=k/max(ns-1,1)
            cols[k]=GOLD*(0.6+0.35*u)+TEAL*(0.3*((math.sin(u*8+t*4))**2))+AMBER*0.25
        low=cols[lab]*0.85
        edge=(np.abs(np.diff(lab,axis=0,prepend=lab[:1]))+np.abs(np.diff(lab,axis=1,prepend=lab[:,:1])))>0
        low[edge]=WHITE*1.0
        img=np.asarray(Image.fromarray((np.clip(low,0,1)*255).astype(np.uint8),'RGB').resize((W,H),Image.LANCZOS)).astype(np.float32)/255
        yield finish(img,rng,grain=0.028,lift=1.44)

def g_pulse(n):
    rng=np.random.default_rng(207); xs,ys,idx=vogel(1200)
    for i in range(n):
        t=i/(n-1); pulse=1+0.24*math.sin(t*math.pi*5); rot=t*0.9
        ca,sa=math.cos(rot),math.sin(rot)
        xr,yr=(xs*ca-ys*sa)*pulse,(xs*sa+ys*ca)*pulse
        col=np.broadcast_to(GOLD*0.75+AMBER*0.4,(1200,3)).copy()
        col[(idx.astype(int)%34)<2]=CYAN
        img=splat(W/2+xr,H/2+yr,0.8+0.6*(1-idx/1200),col)
        yield finish(img,rng,lift=1.57)

def g_vogel3d(n, mode='plain'):
    rng=np.random.default_rng({'plain':208,'34':209,'55':210,'both':211}[mode])
    N=1400; i=np.arange(N,dtype=np.float64); th=np.deg2rad(GOLDEN)*i; r=0.04*np.sqrt(i)
    X,Y=r*np.cos(th),r*np.sin(th); Z=0.13*(1-(r/(0.04*math.sqrt(N)))**2)
    m34=(i.astype(int)%34)<2; m55=(i.astype(int)%55)<2
    for fi in range(n):
        t=fi/(n-1)
        az=t*2*math.pi*0.5; el=math.radians(52+10*math.sin(t*2*math.pi)); dist=2.5-0.2*math.sin(t*math.pi)
        ca,sa=math.cos(az),math.sin(az); ce,se=math.cos(el),math.sin(el)
        cx,cy,cz=dist*ce*sa,dist*se,dist*ce*ca
        forward=np.array([-cx,-cy,-cz]); forward/=np.linalg.norm(forward)
        up=np.array([0.,1.,0.]); right=np.cross(forward,up); right/=np.linalg.norm(right); up=np.cross(right,forward)
        pts=np.stack([X-cx,Y-cy,Z-cz],1); xc,yc,zc=pts@right,pts@up,pts@forward
        f=0.58*H/math.tan(math.radians(36)/2)
        px=W*0.5+f*(xc/np.maximum(zc,1e-3)); py=H*0.5-f*(yc/np.maximum(zc,1e-3))
        col=np.broadcast_to(GOLD*0.75+AMBER*0.4,(N,3)).copy()
        if mode in ('34','both'): col[m34]=CYAN
        if mode in ('55','both'): col[m55]=GOLD*0.25+AMBER*0.75
        focus=np.median(zc); bri=(0.75+1.0*(1-i/N)**0.5)*np.clip(1.45-(zc-focus)*0.35,0.4,1.7)
        img=splat(px,py,bri.astype(np.float32),col.astype(np.float32))
        yield finish(img,rng,lift=1.52)

def g_spin(n, seed=218, reverse=False):
    rng=np.random.default_rng(seed); xs,ys,idx=vogel(1400)
    for i in range(n):
        t=i/(n-1); rot=t*2*math.pi*(-0.42 if reverse else 0.52)
        ca,sa=math.cos(rot),math.sin(rot); zoom=1.12+0.28*math.sin(t*math.pi*2)
        xr,yr=(xs*ca-ys*sa)*zoom*1.2,(xs*sa+ys*ca)*zoom*0.88
        cx=W/2+70*math.sin(t*3); cy=H/2+50*math.cos(t*2)
        col=np.broadcast_to(GOLD*0.75+AMBER*0.35,(1400,3)).copy()
        if reverse: col[(idx.astype(int)%21)<2]=CYAN
        else: col[(idx.astype(int)%34)<2]=TEAL
        img=splat(cx+xr,cy+yr,0.75+0.6*(1-idx/1400),col)
        yield finish(img,rng,lift=1.54)

def g_dissolve(n):
    rng=np.random.default_rng(216)
    for i in range(n):
        t=i/(n-1); phase=math.sin(t*math.pi); xs,ys,idx=vogel(1200)
        xsj=xs+rng.normal(0,60*phase,xs.shape); ysj=ys+rng.normal(0,45*phase,ys.shape)
        rot=t*1.15; ca,sa=math.cos(rot),math.sin(rot)
        xr,yr=xsj*ca-ysj*sa,xsj*sa+ysj*ca
        img=splat(W/2+xr,H/2+yr,0.7+0.65*(1-idx/1200),np.broadcast_to(GOLD*0.7+MAGMA*0.4,(1200,3)).copy())
        yield finish(img,rng,lift=1.52)

def g_galaxy(n):
    rng=np.random.default_rng(217)
    for i in range(n):
        t=i/(n-1); img=np.zeros((H,W,3),np.float32)
        for arm in range(3):
            a0=arm*(2*math.pi/3)+t*0.75; ts=np.linspace(0.1,5.5,1000)
            r=26*np.exp(0.4*ts); ang=a0+ts
            px=W/2+r*np.cos(ang)*1.0+rng.normal(0,7,ts.shape)
            py=H/2+r*np.sin(ang)*0.6+rng.normal(0,5,ts.shape)
            col=np.broadcast_to(GOLD*0.5+CYAN*0.4+AMBER*0.25,(len(ts),3)).copy()
            img=np.maximum(img,splat(px,py,np.linspace(1.3,0.3,len(ts)),col))
        img+=np.exp(-D2C/(2*50**2))[:,:,None]*(WHITE*1.0+GOLD*0.55)
        stars=rng.random((1400,2)); img=np.maximum(img,splat(stars[:,0]*W,stars[:,1]*H,np.full(1400,0.5),np.broadcast_to(WHITE*0.85,(1400,3))))
        yield finish(img,rng,lift=1.5)

def g_bridge(n):
    rng=np.random.default_rng(212); N=1400
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',110); font_s=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',64)
    except: font=font_s=ImageFont.load_default()
    for i in range(n):
        t=i/(n-1)
        if t<0.22: ang=GOLDEN
        elif t<0.48: ang=GOLDEN+(120-GOLDEN)*ease((t-0.22)/0.26)
        elif t<0.65: ang=120.
        else: ang=120+(GOLDEN-120)*ease((t-0.65)/0.35)
        fit=max(0,min(1,1-abs(ang-GOLDEN)/abs(120-GOLDEN)))
        xs,ys,idx=vogel(N,angle=ang); rot=t*0.75; ca,sa=math.cos(rot),math.sin(rot)
        zoom=1.12+0.18*math.sin(t*math.pi)
        xr,yr=(xs*ca-ys*sa)*zoom,(xs*sa+ys*ca)*zoom
        base=GOLD*(0.55+0.5*fit)+AMBER*(0.45*fit)+CYAN*(0.7*(1-fit))
        img=splat(W/2+xr,H/2+yr,0.8+1.0*(1-idx/N)**0.5,np.broadcast_to(base,(N,3)).copy())
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        L=min(SW,SH)*0.46*zoom; a1=-math.pi/2; a2=a1+math.radians(ang)
        d.line([(SW/2,SH/2),(SW/2+math.cos(a2)*L,SH/2+math.sin(a2)*L)],fill=(50,235,255),width=16*SS)
        d.line([(SW/2,SH/2),(SW/2+math.cos(a1)*L,SH/2+math.sin(a1)*L)],fill=(255,195,70),width=12*SS)
        img+=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255*1.2
        # text at 1x
        arm=Image.new('RGB',(W,H),(0,0,0)); dd=ImageDraw.Draw(arm)
        st='GOLDEN ANGLE' if fit>0.92 else ('COLLAPSE' if fit<0.25 else 'DRIFT')
        tc=(255,225,100) if fit>0.7 else (110,245,255)
        dd.text((120,120),f'{ang:.2f}°',font=font,fill=tc); dd.text((120,260),st,font=font_s,fill=tc)
        img+=np.asarray(arm).astype(np.float32)/255*1.1
        yield finish(img,rng,lift=1.47)

def g_protractor(n):
    rng=np.random.default_rng(223)
    for i in range(n):
        t=i/(n-1)
        ang=30+250*ease(0.5+0.5*math.sin(t*math.pi*2-math.pi/2))
        L=min(W,H)*(0.4+0.14*math.sin(t*math.pi*3))
        img=np.exp(-D2C/(2*32**2))[:,:,None]*(GOLD*1.05)
        img+=np.exp(-D2C/(2*100**2))[:,:,None]*AMBER*0.4
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        a1=-math.pi/2; a2=a1+math.radians(ang); Ls=L*SS
        bbox=[SW/2-Ls,SH/2-Ls,SW/2+Ls,SH/2+Ls]
        d.arc(bbox, start=-90, end=-90+ang, fill=(90,235,255), width=8*SS)
        d.line([(SW/2,SH/2),(SW/2+math.cos(a1)*Ls,SH/2+math.sin(a1)*Ls)],fill=(255,195,70),width=14*SS)
        d.line([(SW/2,SH/2),(SW/2+math.cos(a2)*Ls,SH/2+math.sin(a2)*Ls)],fill=(50,235,255),width=16*SS)
        img+=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255*1.25
        yield finish(img,rng,lift=1.52)

def g_fib_tiling(n):
    rng=np.random.default_rng(213)
    for i in range(n):
        t=i/(n-1); fib=[1,1,2,3,5,8,13,21,34,55,89,144,233]
        scale=min(W,H)/160*(1.0+0.75*t)
        x,y=int(W*0.30),int(H*0.36); dirs=[(1,0),(0,1),(-1,0),(0,-1)]
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        glow=np.zeros((H,W,3),np.float32)
        for k,f in enumerate(fib[:int(6+t*8)]):
            s=max(16,int(f*scale)); dx,dy=dirs[k%4]
            x2=x+(s if dx>=0 else -s); y2=y+(s if dy>=0 else -s)
            box=[min(x,x2)*SS,min(y,y2)*SS,max(x,x2)*SS,max(y,y2)*SS]
            col=tuple(int(255*c) for c in (GOLD*(0.65+0.35*(k%3)/2)+AMBER*0.4*(k%2)+CYAN*0.25*((k%4)==0)))
            d.rectangle(box,outline=col,width=max(6*SS,10*SS-k))
            d.arc(box, start=(k%4)*90, end=(k%4)*90+90, fill=(255,225,110), width=6*SS)
            cx0=(min(x,x2)+max(x,x2))/2; cy0=(min(y,y2)+max(y,y2))/2
            rr=max(abs(x2-x),abs(y2-y))*0.55
            glow+=np.exp(-(((XX-cx0)**2+(YY-cy0)**2)/(2*(rr**2)+1)))[:,:,None]*(GOLD*0.28+AMBER*0.15)
            if dx==1: x+=s
            elif dx==-1: x-=s
            elif dy==1: y+=s
            else: y-=s
        img=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255*1.5 + glow
        yield finish(img,rng,grain=0.028,lift=1.42)

def g_phylo_top(n):
    rng=np.random.default_rng(215); xs,ys,idx=vogel(1500)
    for i in range(n):
        t=i/(n-1); rot=t*2*math.pi*0.38; ca,sa=math.cos(rot),math.sin(rot); zoom=1.1+0.4*t
        xr,yr=(xs*ca-ys*sa)*zoom,(xs*sa+ys*ca)*zoom
        col=np.broadcast_to(GOLD*0.8+AMBER*0.35,(1500,3)).copy()
        ring=np.abs(np.sqrt(xs**2+ys**2)-(t*min(W,H)*0.4)); col[ring<55]=CYAN
        img=splat(W/2+xr*1.15,H/2+yr*1.15-90,0.8+0.6*(1-idx/1500),col)
        yield finish(img,rng,lift=1.54)

def g_rise(n):
    rng=np.random.default_rng(220)
    for i in range(n):
        t=i/(n-1); ns=280+int(1500*ease(t)); xs,ys,idx=vogel(ns)
        rot=t*1.55; ca,sa=math.cos(rot),math.sin(rot)
        xr,yr=xs*ca-ys*sa,xs*sa+ys*ca
        img=splat(W/2+xr,H/2+yr,(0.6+0.9*t)*(0.6+0.5*(1-idx/max(ns,1))),np.broadcast_to(GOLD*(0.6+0.4*t)+AMBER*0.4,(ns,3)).copy())
        yield finish(img,rng,grain=0.04,lift=1.57)

def g_zoom(n):
    rng=np.random.default_rng(221); xs,ys,idx=vogel(1700)
    for i in range(n):
        t=i/(n-1); mul=2.7-2.0*ease(t); rot=t*0.75; ca,sa=math.cos(rot),math.sin(rot)
        xr,yr=(xs*ca-ys*sa)*mul,(xs*sa+ys*ca)*mul
        col=np.broadcast_to(GOLD*0.85+AMBER*0.3,(1700,3)).copy(); col[(idx.astype(int)%55)<2]=CYAN
        img=splat(W/2+xr,H/2+yr,0.7+0.6*(1-idx/1700),col)
        yield finish(img,rng,lift=1.52)

def g_outro(n):
    """LOCKED look: collapse to yellow/gold circle — light/sharpen only."""
    rng=np.random.default_rng(222); xs,ys,idx=vogel(1100)
    for i in range(n):
        t=i/(n-1); mul=1.08-0.96*ease(t); fade=1-0.75*ease(max(0,(t-0.45)/0.55))
        rot=t*0.4; ca,sa=math.cos(rot),math.sin(rot)
        xr,yr=(xs*ca-ys*sa)*mul,(xs*sa+ys*ca)*mul
        img=splat(W/2+xr,H/2+yr,(0.75+0.45*(1-idx/1100))*fade,np.broadcast_to(GOLD*0.95+AMBER*0.3,(1100,3)).copy())
        if t>0.6: img+=np.exp(-D2C/(2*24**2))[:,:,None]*(GOLD*1.1+WHITE*0.35)*ease((t-0.6)/0.4)*fade
        yield finish(img,rng,lift=1.5)

def g_field(n):
    """LOCKED outro companion — light/sharpen only, same multi-head field."""
    rng=np.random.default_rng(224)
    centers=[(rng.uniform(0.1,0.9)*W,rng.uniform(0.1,0.9)*H,rng.uniform(0.22,0.48)) for _ in range(22)]
    for i in range(n):
        t=i/(n-1); img=np.zeros((H,W,3),np.float32)
        for cx,cy,sc in centers:
            ns=100; xs,ys,idx=vogel(ns, scale=(min(W,H)*0.09*sc)/math.sqrt(ns)*8)
            rot=t*0.65+sc*3; ca,sa=math.cos(rot),math.sin(rot)
            xr,yr=xs*ca-ys*sa,xs*sa+ys*ca
            img=np.maximum(img,splat(cx+xr,cy+yr,0.65+0.5*(1-idx/ns),np.broadcast_to(GOLD*0.8+AMBER*0.35,(ns,3)).copy()))
        yield finish(img,rng,lift=1.5)

def g_petal(n):
    rng=np.random.default_rng(229)
    for i in range(n):
        t=i/(n-1); npet=max(5,int(5+34*ease(t)))
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        for k in range(npet):
            a=-math.pi/2+k*2*math.pi/npet+t*0.35
            r1,r2=140*SS,560*SS
            pts=[(SW/2+math.cos(a)*r1,SH/2+math.sin(a)*r1),
                 (SW/2+math.cos(a-0.1)*r2,SH/2+math.sin(a-0.1)*r2),
                 (SW/2+math.cos(a+0.1)*r2,SH/2+math.sin(a+0.1)*r2)]
            d.polygon(pts, outline=(255,215,90))
        xs,ys,idx=vogel(300); rot=t*0.55; ca,sa=math.cos(rot),math.sin(rot)
        xr,yr=(xs*ca-ys*sa)*0.5,(xs*sa+ys*ca)*0.5
        img=splat(W/2+xr,H/2+yr,0.85+0.55*(1-idx/300),np.broadcast_to(GOLD*1.0,(300,3)).copy())
        img+=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255*1.1
        yield finish(img,rng,lift=1.52)

def g_nautilus(n):
    # FIX 2026-10-27: old radius maxed ~46px (rendered as a near-still dot). Full-frame growing golden spiral.
    rng=np.random.default_rng(226)
    for i in range(n):
        t=i/(n-1); a0=t*1.6; tmax=6.5+5.0*ease(t)
        ts=np.linspace(0.0,tmax,2600); r=34*np.exp(0.3*ts)
        ang=a0+ts; px=W/2+r*np.cos(ang)*1.1; py=H/2+r*np.sin(ang)*0.8
        img=splat(px,py,np.linspace(0.45,1.3,len(ts)),np.broadcast_to(GOLD*0.9+AMBER*0.3,(len(ts),3)).copy())
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        k=0.6
        while k<tmax:
            rr=34*math.exp(0.3*k)*SS; aa=a0+k; cr=max(8*SS,0.16*rr)
            cx=SW/2+rr*math.cos(aa)*1.1; cy=SH/2+rr*math.sin(aa)*0.8
            d.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], outline=(70,235,255), width=4*SS)
            k+=0.62
        img+=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255*0.8
        yield finish(img,rng,lift=1.52)

def g_storm(n):
    # FIX 2026-10-27: old arms maxed ~97px (near-still dot). Full-frame 4-arm spiral storm, rotating + tightening.
    rng=np.random.default_rng(227)
    for i in range(n):
        t=i/(n-1); img=np.zeros((H,W,3),np.float32)
        for arm in range(4):
            a0=arm*(math.pi/2)+t*2.2; ts=np.linspace(0.0,8.6,1500); r=55*np.exp((0.30+0.04*ease(t))*ts)
            ang=a0+ts*0.95; px=W/2+r*np.cos(ang)*0.95; py=H/2+r*np.sin(ang)*0.62
            img=np.maximum(img,splat(px,py,np.linspace(1.1,0.3,len(ts)),np.broadcast_to(CYAN*0.6+WHITE*0.35+GOLD*0.2,(len(ts),3)).copy()))
        img+=np.exp(-D2C/(2*(60+30*t)**2))[:,:,None]*(WHITE*0.8)
        yield finish(img,rng,lift=1.52)

def g_water(n):
    rng=np.random.default_rng(228)
    for i in range(n):
        t=i/(n-1)
        ov=Image.new('RGB',(SW,SH),(0,0,0)); d=ImageDraw.Draw(ov)
        def branch(x,y,ang,depth,len0):
            if depth<=0 or len0<6*SS: return
            x2=x+math.cos(ang)*len0; y2=y+math.sin(ang)*len0
            w=max(3*SS,int(depth*2*SS)); col=(40,200+depth*5,235)
            d.line([(x,y),(x2,y2)], fill=col, width=w)
            branch(x2,y2,ang-0.38-0.12*math.sin(t*5),depth-1,len0*0.73)
            branch(x2,y2,ang+0.45+0.1*math.cos(t*4),depth-1,len0*0.7)
        branch(SW*0.08,SH*0.45,0.08+0.12*math.sin(t*2),9,170*SS*(0.75+0.35*t))
        branch(SW*0.12,SH*0.58,-0.3+0.1*math.cos(t*2),8,140*SS*(0.75+0.35*t))
        img=np.asarray(ov.resize((W,H),Image.LANCZOS)).astype(np.float32)/255
        img=gaussian_filter(img,(1.2,1.2,0))*1.7
        img+=np.exp(-D2C/(2*220**2))[:,:,None]*(TEAL*0.15)
        yield finish(img,rng,grain=0.028,lift=1.44)

def g_bridge_return(n):
    rng=np.random.default_rng(225); xs,ys,idx=vogel(1300)
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',100)
    except: font=ImageFont.load_default()
    for i in range(n):
        t=i/(n-1); rot=t*0.5; ca,sa=math.cos(rot),math.sin(rot)
        xr,yr=xs*ca-ys*sa,xs*sa+ys*ca
        img=splat(W/2+xr,H/2+yr,0.8+0.6*(1-idx/1300),np.broadcast_to(GOLD*0.95+AMBER*0.3,(1300,3)).copy())
        arm=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(arm)
        d.text((120,120),'137.51°',font=font,fill=(255,225,100))
        d.text((120,250),'GOLDEN ANGLE',font=font,fill=(255,225,100))
        img+=np.asarray(arm).astype(np.float32)/255*1.0
        yield finish(img,rng,lift=1.5)

CUT=json.loads((Path(__file__).resolve().parent/'cutlist.json').read_text())['cutlist']
POCKET={c['id']:c['dur'] for c in CUT}

def dur_for(sid):
    return max(6, math.ceil(POCKET.get(sid, 8) + 0.4))

SHOTS={
 'c_intro_seed':(g_intro_seed, dur_for('c_intro_seed')),
 'c_intro_pair':(g_intro_pair, dur_for('c_intro_pair')),
 'c_fib_syllables':(lambda n: g_fib(n,'syll'), dur_for('c_fib_syllables')),
 'c_fib_climb':(lambda n: g_fib(n,'climb'), dur_for('c_fib_climb')),
 'c_gaps_light':(g_gaps, dur_for('c_gaps_light')),
 'c_voronoi':(g_voronoi, dur_for('c_voronoi')),
 'c_grow_pulse':(g_pulse, dur_for('c_grow_pulse')),
 'c_vogel_plain':(lambda n: g_vogel3d(n,'plain'), dur_for('c_vogel_plain')),
 'c_vogel_34':(lambda n: g_vogel3d(n,'34'), dur_for('c_vogel_34')),
 'c_vogel_55':(lambda n: g_vogel3d(n,'55'), dur_for('c_vogel_55')),
 'c_vogel_both':(lambda n: g_vogel3d(n,'both'), dur_for('c_vogel_both')),
 'c_bridge':(g_bridge, dur_for('c_bridge')),
 'c_fib_tiling':(g_fib_tiling, dur_for('c_fib_tiling')),
 'c_phyllotaxis_top':(g_phylo_top, dur_for('c_phyllotaxis_top')),
 'c_spiral_dissolve':(g_dissolve, dur_for('c_spiral_dissolve')),
 'c_galaxy_code':(g_galaxy, dur_for('c_galaxy_code')),
 'c_turn_again_a':(lambda n: g_spin(n,218,False), dur_for('c_turn_again_a')),
 'c_turn_again_b':(lambda n: g_spin(n,219,True), dur_for('c_turn_again_b')),
 'c_rise_energy':(g_rise, dur_for('c_rise_energy')),
 'c_final_zoom_code':(g_zoom, dur_for('c_final_zoom_code')),
 'c_outro_seed':(g_outro, dur_for('c_outro_seed')),
 'c_angle_protractor':(g_protractor, dur_for('c_angle_protractor')),
 'c_field_code':(g_field, dur_for('c_field_code')),
 'c_bridge_return':(g_bridge_return, dur_for('c_bridge_return')),
 'c_nautilus_code':(g_nautilus, dur_for('c_nautilus_code')),
 'c_storm_code':(g_storm, dur_for('c_storm_code')),
 'c_water_code':(g_water, dur_for('c_water_code')),
 'c_petal_math':(g_petal, dur_for('c_petal_math')),
}

def main():
    todo=sys.argv[1:] or [c['id'] for c in CUT if c['id'].startswith('c_')]
    for sid in todo:
        if sid not in SHOTS: print('skip',sid, flush=True); continue
        gen,dur=SHOTS[sid]; n=int(dur*FPS); path=OUT/f'{sid}.mp4'
        why=shot_claimed(sid, path, n)
        if why:
            print(f'SKIP {sid} ({why})', flush=True); continue
        print(f'START {sid} {dur}s {n}f SS={SS}', flush=True)
        sz=encode(path, gen, n)
        print(f'DONE {sid} {sz}', flush=True)

if __name__=='__main__':
    main()
