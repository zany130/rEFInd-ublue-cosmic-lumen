# Credits, asset provenance and license scope

This repository is an **unofficial rEFInd theme**, not an official or endorsed release of Bazzite, Universal Blue, Microsoft, rEFInd, or the other projects cited below. Names, artwork and trademarks belong to their respective rights holders.

## Shadow-rEFInd graphics (GNU AGPL-3.0)

The rEFInd icon collection is sourced from [chris1111/Shadow-rEFInd](https://github.com/chris1111/Shadow-rEFInd) at pinned Git revision `fe639d2869f59d291489c0c416c17577bd166046`.

- Imported original PNGs in `icons/` cover the upstream OS icon family (`os_*`), functional icons (`func_*`), utility icons (`tool_*`), volume badges (`vol_*`), boot labels (`boot_*`), and navigation/decorative icons. The two selection images are shipped as `selection_big.png` and `selection_small.png`; equivalent copies also appear under `icons/`.
- **Upstream asset bytes are unmodified** for their corresponding filenames. Extra aliases such as `icons/os_win11.png` (and `os_win10.png` where present) reuse the corresponding Shadow Windows icon image to support common rEFInd icon names. The custom `icons/os_bazzite.png` was made for this theme collection and is **not** a Shadow-rEFInd original.
- Imported assets remain under Shadow-rEFInd's **GNU AGPL-3.0** license. Preserve the source attribution and the complete license notice in [third_party/Shadow-rEFInd-AGPL-3.0.txt](third_party/Shadow-rEFInd-AGPL-3.0.txt) when redistributing.
- The repository's root `LICENSE` applies **MIT only to independently originated project material**, not to imported AGPL-3.0 graphics; the MIT license does not supersede AGPL-3.0 terms.

## Cosmic Lumen design and user-provided materials

- **Approved concept:** `screenshots/approved-concept.png` / `source/approved-concept.png` is the user-approved, AI-assisted design mockup. This is **not** a photograph of a UEFI display or official Universal Blue artwork.
- **Derived wallpaper:** `background.png` is the final 4K starfield/horizon composition, including the “Lumen Companion” heading. It is independently composed for this unofficial theme, not a copied upstream Lumen PNG.
- **Other source files:** the `source/` images (neon Bazzite/Windows-style icons, glow elements and clean backgrounds) are prior user-provided/generated theme components kept for design history. Their inclusion does not grant ownership of any independently held trademark or source image rights.
- **Screenshots:** `screenshots/asset-composition-preview.png` is a prior static design visualization; `screenshots/preview.png` is the actual rEFInd menu under **QEMU/OVMF**, not real physical firmware. `preview.png` is a duplicate of the latter.
- **Inspiration:** [rEFInd Lumen](https://github.com/shoxjaxon-atabayev/rEFInd-lumen) by Shoxjaxon Atabayev (MIT), for overall glass-card and cosmic styling. No bundled upstream Lumen PNGs, source scripts or bootloader code are claimed as copied.

## Logo and permission caveats

Bazzite, Universal Blue, Microsoft, Windows, and other third-party identifiers are the property of their respective owners. The custom Bazzite icon is not an official branding-license grant. This documentation records known sources and license terms; it does not imply consent from rightsholders or resolve any specifically unverified wallpaper permissions.

See the project [README](README.md) for safe installation and QEMU-versus-hardware testing distinctions.
