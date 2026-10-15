# Universal Blue Cosmic Lumen — rEFInd Theme

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
