#!/usr/bin/env python3
"""Rebuild rEFInd Universal Blue Cosmic Lumen theme from source assets.
No EFI, bootloader or external files are modified.
Requires Pillow and NumPy. Deterministic random seed.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import shutil, textwrap, zipfile, math, hashlib

PARENT = Path(__file__).resolve().parent
ROOT = PARENT.parent if PARENT.name == 'scripts' else PARENT / 'rEFInd-ublue-cosmic-lumen'
SOURCE = ROOT / 'source'
ICONS = ROOT / 'icons'
SHOT = ROOT / 'screenshots'
for path in (ROOT, SOURCE, ICONS, SHOT):
    path.mkdir(parents=True, exist_ok=True)

# Include original screenshot in source, not extracted icon artwork.
REF = Image.open(SOURCE / 'approved-concept.png').convert('RGB')
SW,SH = REF.size
assert (SW,SH) == (1672,941), (SW,SH)
W,H = 3840,2160
np.random.seed(20261015)
rng = np.random.default_rng(20261015)

def save_png(im, path):
    im.save(path, format='PNG', optimize=True)

# Clean, atmospheric source wallpaper, without fixed text/buttons/icons.
# Preserve the approved screenshot's unobstructed top-left project branding.
x,y = np.meshgrid(np.arange(SW,dtype=np.float32),np.arange(SH,dtype=np.float32))
xn,yn=x/SW,y/SH
# Smooth cloud fractal noise (4 scales) to give the sky organic detail.
cloud=np.zeros((SH,SW),np.float32)
for cw,ch,amp in [(18,12,1.0),(45,26,0.55),(110,67,0.22)]:
    n=(rng.random((ch,cw))*255).astype('uint8')
    n=Image.fromarray(n).resize((SW,SH),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(4))
    cloud+=(np.asarray(n,dtype=np.float32)/255-.5)*amp
cloud=np.clip(cloud,-.6,.6)
# blue-purple deep-space clouds. right-upper nebula approximates image reference.
neb=np.exp(-(((xn-.84)/.28)**2+((yn-.24)/.25)**2)*1.1)
neb2=np.exp(-(((xn-.60)/.44)**2+((yn-.37)/.24)**2)*1.5)
leftblue=np.exp(-(((xn-.06)/.34)**2+((yn-.43)/.25)**2)*2)
colors=np.zeros((SH,SW,3),np.float32)
colors[:,:,0]=2.8+18*neb+4*neb2+6*leftblue + cloud*19*(.3+.8*neb)
colors[:,:,1]=5.2+9*neb+11*neb2+15*leftblue + cloud*10*(.4+.8*neb)
colors[:,:,2]=23+38*neb+31*neb2+26*leftblue + cloud*57*(.4+.8*neb)
# Deepen the lower sky. Brightness near horizon rises again.
near=np.exp(-((yn-.57)/.10)**2)
colors[:,:,0]+=near*(8+22*xn)
colors[:,:,1]+=near*(18+8*(1-xn))
colors[:,:,2]+=near*35
# surface below curved planet horizon; reflection-rich blue-violet metallic surface.
horizon=0.535 + .075*((xn-.5)/.5)**2
below=yn-horizon
surf=below>0
surfaceDepth=np.clip(below/.40,0,1)
blue_ref=np.exp(-((xn-.36)/.30)**2)
purple_ref=np.exp(-((xn-.80)/.33)**2)
texture=(np.sin(230*yn+22*xn)*0.26 + np.sin(510*xn+370*yn)*.11 + cloud*.72)
tex2=np.sin(75*yn + 120*xn + cloud*15)
reflect=np.exp(-below/.26)
colors[:,:,0]=np.where(surf, 5+23*purple_ref*reflect+10*blue_ref*reflect+9*texture*reflect+5*surfaceDepth, colors[:,:,0])
colors[:,:,1]=np.where(surf, 9+18*blue_ref*reflect+6*purple_ref*reflect+9*texture*reflect+4*surfaceDepth, colors[:,:,1])
colors[:,:,2]=np.where(surf, 29+37*blue_ref*reflect+45*purple_ref*reflect+14*texture*reflect+4*tex2*reflect, colors[:,:,2])
# Strong original cosmic horizon. Sharp bright line, plus wide bloom.
d=np.abs(below)
bloom=np.exp(-(d/.040)**2)
sharp=np.exp(-(d/.0025)**2)
sat=np.clip(1-.18*purple_ref,0,1)
colors[:,:,0]+=bloom*(15+16*purple_ref)+sharp*(42+55*purple_ref)
colors[:,:,1]+=bloom*(23+12*blue_ref)+sharp*(94+17*blue_ref)
colors[:,:,2]+=bloom*68+sharp*122
# Vignette and haze at edges.
vig=1-.27*(np.abs(xn-.52)*.82 + np.abs(yn-.46)*.64)
colors*=np.clip(vig,.60,1)[:,:,None]
base=Image.fromarray(np.uint8(np.clip(colors,0,255)),'RGB')
# stars over sky, with a few larger soft galaxy highlights.
starfield=Image.new('RGBA',(SW,SH),(0,0,0,0))
sd=ImageDraw.Draw(starfield,'RGBA')
for i in range(1600):
    xx=int(rng.integers(0,SW)); yy=int(rng.integers(0,480))
    rr=float(rng.choice([.45,.62,.76,1.0,1.2,1.5],p=[.2,.22,.25,.2,.1,.03]))
    bright=int(rng.integers(70,180))
    hue=(164,191,255,bright) if rng.random()<.85 else (225,171,255,bright)
    sd.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=hue)
for xx,yy in [(1408,145),(1150,83),(870,75),(1560,270),(1050,320),(310,255),(1310,355)]:
    sd.ellipse((xx-2,yy-2,xx+2,yy+2),fill=(211,228,255,220))
starfield=starfield.filter(ImageFilter.GaussianBlur(.18))
base=Image.alpha_composite(base.convert('RGBA'),starfield)
# The top quarter of user-approved art (where header lives) remains fully intact.
# Bottom is fully reconstructed so no frozen reboot/shutdown buttons remain.
orig=np.asarray(REF.convert('RGBA'),dtype=np.uint8)
original=Image.fromarray(orig,'RGBA')
mask=np.uint8(np.clip((278-y)/55,0,1)*255)
# Static original heading unchanged; outside this vertical region, reconstructed space art.
mask_im=Image.fromarray(mask,'L')
base.paste(original,(0,0),mask_im)
# A soft nebula in the right lower sky, but leave logo and heading untouched.
# Source file useful for reviewing future design changes.
# Seamless vertical composites: retain the approved cosmic header at the
# top and the rich reflective original surface below y=700. Reconstruct the
# central boot-card band across *the entire image width* to avoid rectangles
# or permanently baked-in card edges.
clean=base.convert('RGB')
source_arr=np.asarray(REF,dtype=np.float32)
made_arr=np.asarray(clean,dtype=np.float32)
# Restore the detailed original reflected surface only BELOW all four cards,
# with a wide feathered transition; there are no labels in this region.
restore=np.clip((y-635)/95,0,1)[:,:,None]
made_arr=made_arr*(1-restore)+source_arr*restore
clean=Image.fromarray(np.uint8(np.clip(made_arr,0,255)),'RGB')
# The user mockup's two fixed bottom UI buttons are replaced by an
# unobstructed reflection strip borrowed from its lower 840:932 region;
# full-width seam-free blend prevents box-shaped restoration marks.
strip=REF.crop((0,837,SW,934)).resize((SW,167),Image.Resampling.BICUBIC)
stripsurface=Image.new('RGB',(SW,SH),(0,0,0))
stripsurface.paste(strip,(0,695))
stripalpha=np.clip((y-698)/34,0,1)*np.clip((847-y)/37,0,1)
clean_arr=np.asarray(clean,dtype=np.float32)
new_arr=np.asarray(stripsurface,dtype=np.float32)
clean=Image.fromarray(np.uint8(np.clip(clean_arr*(1-stripalpha[:,:,None])+new_arr*stripalpha[:,:,None],0,255)),'RGB')
save_png(clean,SOURCE/'background-clean-1672.png')
background=clean.resize((W,H),Image.Resampling.LANCZOS)
save_png(background,ROOT/'background.png')

# Imported refindTTT PNGs and config are not regenerated here.
# This script deliberately rebuilds only the locally composed background.
# Run scripts/sync_refindttt_icons.py to reproduce pinned upstream icons
# and matching selections without modifying the bootloader or wallpaper.
print("Cosmic background rebuilt; imported refindTTT assets and config preserved")
