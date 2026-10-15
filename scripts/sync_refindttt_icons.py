#!/usr/bin/env python3
"""Import pinned refindTTT originals with verified Git hashes.

Writes only icons and matching selection PNGs; leaves original wallpaper,
theme.conf, EFI bootloader and system settings untouched.
"""
import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
COMMIT="427f62a44a701bc75e2fbe973424a2a601238c37"
ASSETS={
 "icons/os_bazzite.png": ("cf4acbd678878938a916dc87b45f87cfcd23e100", ["icons/os_bazzite.png"]),
 "icons/os_win.png": ("9c3317f66e0b6b0a2d811cf144c4bd6a9700805f", ["icons/os_win.png","icons/os_win10.png","icons/os_win11.png","icons/os_windows.png"]),
 "icons/func_firmware.png": ("dc884890707f09be82f745020f998e452c76439e", ["icons/func_firmware.png"]),
 "icons/func_reset.png": ("482778799b428cc35d478102845d7e15d630c8fc", ["icons/func_reset.png"]),
 "icons/func_shutdown.png": ("04deda6da9e288172e7e88bfa485ceca24c7f318", ["icons/func_shutdown.png"]),
 "icons/tool_shell.png": ("101a2365ad8f6f8986ed69fab52fa446a696bdaa", ["icons/tool_shell.png"]),
 "icons/tool_rescue.png": ("3e9b15c2cebc3fd6ae9e2623bbd95fc0bf00edc9", ["icons/tool_rescue.png"]),
 "backgrounds/selection_big_blue.png": ("10fa170dafc284bea31db14bb503cf1e15d1ae94", ["selection_big.png"]),
 "backgrounds/selection_small_blue.png": ("e4d9517c52181d73deddd753eee6c0d50f488cbb", ["selection_small.png"])
}
for src,(sha_expected,destinations) in ASSETS.items():
    url=f"https://raw.githubusercontent.com/gutlessCGH/refindTTT/{COMMIT}/{src}"
    with urlopen(url,timeout=30) as res:
        data=res.read()
    real_sha=hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
    if real_sha!=sha_expected: raise RuntimeError(f"SHA mismatch for {src}: {real_sha}")
    for destination in destinations:
        path=ROOT/destination
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        print(f"Imported {destination}")
