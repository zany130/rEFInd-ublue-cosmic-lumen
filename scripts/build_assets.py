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

# Gradient glass cards independent of fixed menu state.
CARD=576
SMALL=96
HIGHLIGHT=648
# place card within 576 PNG to preserve soft selection offset.
def glass_card(size=CARD):
    im=Image.new('RGBA',(size,size),(0,0,0,0))
    tile=(20,18,size-20,size-18)
    # Off-screen shadow with gentle Gaussian dropoff, not a giant bright halo.
    shadow=Image.new('RGBA',im.size)
    sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((30,34,size-30,size-10),radius=52,fill=(0,0,28,160))
    shadow=shadow.filter(ImageFilter.GaussianBlur(18))
    im.alpha_composite(shadow)
    # Glass interior: slightly brighter along bottom, violet towards right.
    layer=Image.new('RGBA',(size,size))
    px=np.empty((size,size,4),dtype=np.uint8)
    ya,xa=np.mgrid[0:size,0:size]
    xx=xa/(size-1); yy=ya/(size-1)
    px[:,:,0]=np.clip(11 + 25*xx + 12*yy,0,255).astype(np.uint8)
    px[:,:,1]=np.clip(26 + 15*(1-xx) + 7*(1-yy),0,255).astype(np.uint8)
    px[:,:,2]=np.clip(64 + 57*xx + 11*yy,0,255).astype(np.uint8)
    px[:,:,3]=198
    layer=Image.fromarray(px,'RGBA')
    m=Image.new('L',(size,size),0); ImageDraw.Draw(m).rounded_rectangle(tile,radius=50,fill=255)
    a=np.asarray(m,dtype=np.uint16)*np.asarray(layer.getchannel('A'),dtype=np.uint16)//255
    layer.putalpha(Image.fromarray(np.uint8(a),'L'))
    im.alpha_composite(layer)
    # Waves along bottom – small, subtle, curved and bounded to tile.
    wave=Image.new('RGBA',(size,size),(0,0,0,0)); wd=ImageDraw.Draw(wave)
    wd.ellipse((-120,370,365,700),fill=(43,119,247,80))
    wd.ellipse((235,374,770,740),fill=(115,79,242,73))
    wa=np.asarray(wave.getchannel('A'),dtype=np.uint16)*np.asarray(m,dtype=np.uint16)//255
    wave.putalpha(Image.fromarray(np.uint8(wa),'L')); im.alpha_composite(wave)
    # thin glass border and one soft top highlight
    bd=ImageDraw.Draw(im)
    bd.rounded_rectangle(tile,radius=50,outline=(170,185,247,190),width=3)
    bd.arc((25,22,size-25,size-25),180,286,fill=(232,249,255,185),width=2)
    return im

def art_symbol(filename,scale=330):
    img=Image.open(SOURCE/filename).convert('RGBA')
    a=np.asarray(img.getchannel('A'),dtype=np.uint8).copy()
    # threshold a few stray one-alpha border pixels from diffusion models
    a[a<8]=0
    img.putalpha(Image.fromarray(a,'L'))
    img.thumbnail((scale,scale),Image.Resampling.LANCZOS)
    return img

sources={
  'os_bazzite.png':'glowing_cyan_to_magenta_monogram_icon.png',
  'os_win.png':'neon_glass_windows_logo.png',
  'os_shell.png':'glossy_neon_terminal_icon.png',
  'os_firmware.png':'neon_frosted_six_tooth_gear.png',
  'os_rescue.png':'neon_frosted_six_tooth_gear.png',
}
for filename,src in sources.items():
    card=glass_card()
    symbol=art_symbol(src,342)
    card.alpha_composite(symbol,((CARD-symbol.width)//2,(CARD-symbol.height)//2-5))
    save_png(card,ICONS/filename)
for alt in ('os_windows.png','os_win11.png','os_win10.png'):
    shutil.copyfile(ICONS/'os_win.png',ICONS/alt)

# The small official utility icons are separate round glass chips.
smalls={'func_firmware.png':'neon_frosted_six_tooth_gear.png',
  'func_reset.png':'glowing_glass_reboot_icon.png',
  'func_shutdown.png':'glowing_cyan_purple_power_icon.png',
  'tool_shell.png':'glossy_neon_terminal_icon.png'}
for filename,src in smalls.items():
    tile=Image.new('RGBA',(SMALL,SMALL),(0,0,0,0))
    t=Image.new('RGBA',tile.size)
    dt=ImageDraw.Draw(t)
    dt.rounded_rectangle((7,12,SMALL-7,SMALL-10),radius=17,fill=(17,24,69,216),outline=(111,139,244,181),width=2)
    tile.alpha_composite(t)
    symbol=art_symbol(src,65)
    tile.alpha_composite(symbol,((SMALL-symbol.width)//2,(SMALL-symbol.height)//2))
    save_png(tile,ICONS/filename)
# Selection big: transparent center, glow on the outer border of chosen OS glass tile.
select=Image.new('RGBA',(HIGHLIGHT,HIGHLIGHT),(0,0,0,0))
offset=(HIGHLIGHT-CARD)//2
box=(offset+15,offset+13,HIGHLIGHT-offset-15,HIGHLIGHT-offset-13)
for width,blur,alpha in [(32,33,230),(20,18,220),(8,6,235)]:
    glow=Image.new('RGBA',(HIGHLIGHT,HIGHLIGHT),(0,0,0,0));gd=ImageDraw.Draw(glow)
    gd.rounded_rectangle(box,radius=57,outline=(37,172,255,alpha),width=width)
    if blur: glow=glow.filter(ImageFilter.GaussianBlur(blur))
    select.alpha_composite(glow)
ImageDraw.Draw(select).rounded_rectangle(box,radius=57,outline=(128,244,255,235),width=6)
save_png(select,ROOT/'selection_big.png')
smallsel=Image.new('RGBA',(128,128),(0,0,0,0))
for blur,alpha,width in [(14,190,9),(5,230,5)]:
    g=Image.new('RGBA',(128,128),(0,0,0,0));d=ImageDraw.Draw(g)
    d.rounded_rectangle((20,24,108,103),radius=20,outline=(81,178,255,alpha),width=width)
    smallsel.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))
ImageDraw.Draw(smallsel).rounded_rectangle((20,24,108,103),radius=20,outline=(162,210,255,190),width=3)
save_png(smallsel,ROOT/'selection_small.png')

# Preview not a boot screenshot; rEFInd has different label/row layout depending on discovered entries.
preview=clean.convert('RGBA')
centers=[360,675,990,1305]
# source mockup uses four big tiles. Render approximate only.
for i,name in enumerate(('os_win.png','os_bazzite.png','os_shell.png','os_firmware.png')):
    size=266
    px=centers[i]-size//2;py=292
    if i==1:
        hi=Image.open(ROOT/'selection_big.png').resize((302,302),Image.Resampling.LANCZOS)
        preview.alpha_composite(hi,(px-18,py-18))
    icon=Image.open(ICONS/name).resize((size,size),Image.Resampling.LANCZOS)
    preview.alpha_composite(icon,(px,py))
for i,name in enumerate(('func_reset.png','func_shutdown.png')):
    icon=Image.open(ICONS/name).resize((58,58),Image.Resampling.LANCZOS)
    preview.alpha_composite(icon,(730+i*142,760))
save_png(preview.convert('RGB'),SHOT/'asset-composition-preview.png')

(ROOT/'theme.conf').write_text('''# Universal Blue Cosmic Lumen — VISUAL ONLY.
# Do not alter refind.conf bootloader entries, scanning, or Secure Boot.
icons_dir themes/rEFInd-ublue-cosmic-lumen/icons
banner themes/rEFInd-ublue-cosmic-lumen/background.png
banner_scale fillscreen
big_icon_size 576
small_icon_size 96
selection_big themes/rEFInd-ublue-cosmic-lumen/selection_big.png
selection_small themes/rEFInd-ublue-cosmic-lumen/selection_small.png
''',encoding='utf-8')
(ROOT/'README.md').write_text('''# Universal Blue Cosmic Lumen — rEFInd Theme

An **experimental 4K rEFInd theme** based on the user-approved Universal Blue cosmic / glass-card boot menu concept. Inspired by [rEFInd Lumen](https://github.com/shoxjaxon-atabayev/rEFInd-lumen) (MIT); all cards and glow effects in this package are newly composited artwork rather than a copy of Lumen's assets.

> **Visual installation candidate, not yet boot-tested.** The concept and asset preview are artistic illustrations, not actual screenshots from UEFI firmware. Real stock rEFInd positions and labels can differ; fine-tune after a boot test.

![Approved concept (illustration)](screenshots/approved-concept.png)

## Included files

- `background.png`: **3840×2160 RGB** starfield / galaxy / horizon wallpaper with original Universal Blue title at upper left, **without permanently baked-in menu tiles or reboot/shutdown controls**.
- `icons/os_bazzite.png`, `os_win.png`, `os_windows.png`, `os_win11.png`, `os_win10.png`, `os_shell.png`, `os_firmware.png`, `os_rescue.png`: **576×576 RGBA** translucent glass boot cards with embedded artwork.
- `icons/func_reset.png`, `func_shutdown.png`, `func_firmware.png`, `tool_shell.png`: **96×96 RGBA** utility icons.
- `selection_big.png`: **648×648 RGBA**, blue glow with a transparent center.
- `selection_small.png`: **128×128 RGBA**, small tool-row highlight.
- `theme.conf`: **visual overrides only**; boot logic remains in your existing configuration.
- `screenshots/`: concept and a separate *illustrative* overlay preview.

## Installation (on an existing rEFInd system)

Do **not** replace or overwrite `refind.conf`, Shim, GRUB, or any `.efi` executable. First back up your existing rEFInd configuration outside the EFI System Partition:

```sh
cp /boot/efi/EFI/refind/refind.conf "$HOME/refind.conf.before-cosmic-lumen.bak"
```

Extract the **install ZIP**, open a shell in the directory containing the extracted `rEFInd-ublue-cosmic-lumen` folder, and run:

```sh
sudo cp -a rEFInd-ublue-cosmic-lumen /boot/efi/EFI/refind/themes/
```

Replace only your existing active theme `include` line in the main `/boot/efi/EFI/refind/refind.conf` with:

```conf
include themes/rEFInd-ublue-cosmic-lumen/theme.conf
```

Do not have two active theme `include` lines overriding one another. Keep all existing `scanfor`, loader paths, `volume`, `default_selection`, `dont_scan_files`, and Secure Boot configuration **unchanged**.

If desired, in **your existing working Bazzite manual stanza** set the icon path only:

```conf
icon /EFI/refind/themes/rEFInd-ublue-cosmic-lumen/icons/os_bazzite.png
```

On the user's Bazzite machine the tested loader path must remain `/EFI/fedora/shimx64.efi`. Never change it to `/EFI/fedora/grubx64.efi` to install this theme; doing so can break GRUB with `shim_lock protocol not found`.

## Difference from the design illustration

1. Stock rEFInd does not make UEFI Shell and Firmware Settings main-row boot entries just because their `os_*.png` files exist. Shell and firmware are usually **tool row** entries. Add `shell` or `firmware` to `showtools` in the main configuration if you want them enabled; if you need a custom main-row EFI Shell entry, it requires a separate valid, trusted loader definition. `Rescue Tools` similarly requires an actual EFI loader.
2. rEFInd generally labels the **currently selected** entry, not every boot option simultaneously, so the approved mockup's per-card labels are conceptual. We do not burn false labels onto icons or wallpaper.
3. The glass appearance is baked into **each transparent OS icon**; `selection_big.png` displays only an overlay glow for the selected entry. The real position of those icons is controlled by rEFInd, not exact absolute coordinates in the mockup.
4. At 3840×2160, 576px cards occupy substantial space. If you see clipping with many discovered entries, set `big_icon_size 448` or `384` in the theme file. Stock rEFInd rescales the images.
5. Background is reconstructed from the user-supplied approved concept plus procedural galaxy / planetary horizon rendering. It is designed to be faithful to the concept, **not pixel-identical** to the obscured pixels behind the original drawn menu.

## Restore previous theme

Restore your earlier `include themes/.../theme.conf` line (and previous manual Bazzite icon path, if modified), or copy back your saved config file. No bootloader binaries or firmware boot entries need changing.

## Build from source

Install Python 3, Pillow and NumPy. Run `python3 scripts/build_assets.py` from the repository root; the source package includes the approved concept and icon artwork under `source/`. The build script recreates deterministic assets from those inputs without needing network access.

## Licensing & acknowledgments

Code and original compositing scripts are MIT-licensed; source artwork rights and third-party logos are not automatically transferred by this license. The design draws inspiration from [Lumen](https://github.com/shoxjaxon-atabayev/rEFInd-lumen) (MIT) and the user-supplied Universal Blue concept. Product names and logos are the property of their respective owners. This project is **unofficial** and not affiliated with or endorsed by Universal Blue, Bazzite, Microsoft or the original Lumen author. Consult `ATTRIBUTION.md` before redistribution.
''',encoding='utf-8')
(ROOT/'ATTRIBUTION.md').write_text('''# Attribution and asset provenance

- User-approved Universal Blue Cosmic Lumen concept (`screenshots/approved-concept.png` and `source/approved-concept.png`): provided by the user in a ChatGPT conversation; used for visual direction and static top-left branding. The user should check any rights to redistribute or claim ownership of this image.
- Glass card geometry and color treatment are inspired by [rEFInd Lumen](https://github.com/shoxjaxon-atabayev/rEFInd-lumen) by Shoxjaxon Atabayev (MIT), but the glass and glow graphics here were independently synthesized with Pillow rather than copying Lumen's bundled PNGs or scripts.
- `source/glowing_cyan_to_magenta_monogram_icon.png`, `neon_glass_windows_logo.png`, `glossy_neon_terminal_icon.png`, `neon_frosted_six_tooth_gear.png`, `glowing_glass_reboot_icon.png`, and `glowing_cyan_purple_power_icon.png`: generated earlier in the ChatGPT conversation for another Bazzite rEFInd theme. They are not claimed to be official company logo artwork.
- Names, logos, and marks of Universal Blue, Bazzite and Microsoft remain subject to their owners' rights. Avoid presenting this as an official product.
- MIT in `LICENSE` applies to original project scripts and documentation; it does not grant licenses to trademarks or independent third-party source artwork.
''',encoding='utf-8')
(ROOT/'LICENSE').write_text('''MIT License

Copyright (c) 2026 rEFInd-ublue-cosmic-lumen contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''',encoding='utf-8')
(ROOT/'PUBLISHING.md').write_text('''# GitHub publishing

1. Boot-test the theme and keep it marked beta until the layout is verified at actual rEFInd resolution.
2. Confirm permissions for any user-supplied imagery/trademarks before public redistribution.
3. Create an empty GitHub repository, e.g. `zany130/rEFInd-ublue-cosmic-lumen` (unofficial, not endorsed by Universal Blue).
4. Unzip the **source** ZIP, `cd rEFInd-ublue-cosmic-lumen`, then:

```sh
git init -b main
git add .
git commit -m "Initial Universal Blue Cosmic Lumen theme (beta)"
git remote add origin https://github.com/zany130/rEFInd-ublue-cosmic-lumen.git
git push -u origin main
```

Do not publish the install ZIP as a stable release before actual firmware testing. When ready, add a release with the install ZIP attached.
''',encoding='utf-8')
# add convenient release rebuild script in source package only.

# Compact install ZIP: include only needed rEFInd content and user-facing README and attribution.
base=ROOT.parent
install=base/'rEFInd-ublue-cosmic-lumen-install.zip'
source=base/'rEFInd-ublue-cosmic-lumen-source.zip'
installfiles=[ROOT/'background.png',ROOT/'selection_big.png',ROOT/'selection_small.png',ROOT/'theme.conf',ROOT/'README.md',ROOT/'ATTRIBUTION.md',ROOT/'LICENSE'] + sorted(ICONS.glob('*.png'))
with zipfile.ZipFile(install,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for p in installfiles:
        z.write(p,p.relative_to(base).as_posix())
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(base).as_posix())
print('BUILT',ROOT)
for path in (install,source):
    print(path, path.stat().st_size, 'bytes', 'ZIP okay?',zipfile.ZipFile(path).testzip() is None)
