#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Koorg
# 
# This script creates a package to override texture placeholders from Patrix resource packs
# that show the error message "ENABLE CONNECT TEXTURE".
# 
# PLEASE NOTE : If you can see this error message, it means that ANOTHER package is not 
# using the correct method to display the textures... 
# (e.g. PhysicsMod, when the grass block or the stone block is broken into pieces)
# 
# Usage : create_patrix_overrid.py Patrix_1.21.8_32x_basic.zip
# => creates Patrix_32x_CTMOverride.zip that must be loaded on top of your resource packs.

import zipfile, os, re, sys, tempfile, shutil, json

PACK_FORMAT = 64  # selon ton instruction
DESC = "Overrides for mods breaking CTM with Patrix \nBy Koorg"

TAILS = {
    "grass": "assets/minecraft/optifine/ctm/patrix/grass/block/top/1.png",
    "stone": "assets/minecraft/optifine/ctm/patrix/stone/1.png",
}

def detect_res(filename: str):
    m = re.search(r'(?i)(^|[_\W-])(32|64|128|256)x($|[_\W-])', filename)
    return (m.group(2) + "x") if m else None

def find_entry(zf: zipfile.ZipFile, tail: str):
    tail = tail.replace("\\", "/").lower()
    for name in zf.namelist():
        p = name.replace("\\", "/").lower()
        if p.endswith(tail):
            return name
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_patrix_override.py <resourcepack.zip>")
        sys.exit(1)

    in_zip = os.path.abspath(sys.argv[1])
    if not zipfile.is_zipfile(in_zip):
        print(f"Error: not a zip file: {in_zip}")
        sys.exit(1)

    base = os.path.basename(in_zip)
    res = detect_res(base)
    dir_name = f"Patrix_{res}_CTMOverride" if res else "Patrix_CTMOverride"
    out_zip = os.path.join(os.path.dirname(in_zip), f"{dir_name}.zip")

    tmp = tempfile.mkdtemp(prefix="patrix_override_")
    build_dir = os.path.join(tmp, dir_name)
    block_dir = os.path.join(build_dir, "assets", "minecraft", "textures", "block")
    os.makedirs(block_dir, exist_ok=True)

    # pack.mcmeta
    mcmeta = {"pack": {"pack_format": PACK_FORMAT, "description": DESC}}
    with open(os.path.join(build_dir, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump(mcmeta, f, ensure_ascii=False, indent=2)

    # extractions ciblées
    with zipfile.ZipFile(in_zip, "r") as zf:
        mapping = {}
        for key, tail in TAILS.items():
            entry = find_entry(zf, tail)
            if not entry:
                print(f"ERROR: missing '{tail}' in {in_zip}")
                shutil.rmtree(tmp, ignore_errors=True)
                sys.exit(2)
            mapping[key] = entry

        for key, entry in mapping.items():
            target_name = "grass_block_top.png" if key == "grass" else "stone.png"
            target_path = os.path.join(block_dir, target_name)
            with zf.open(entry) as src, open(target_path, "wb") as dst:
                shutil.copyfileobj(src, dst)

    # zippage (contenu à la racine du zip : pack.mcmeta + assets/)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as outz:
        for root, _, files in os.walk(build_dir):
            for fn in files:
                full = os.path.join(root, fn)
                arcname = os.path.relpath(full, build_dir).replace("\\", "/")
                outz.write(full, arcname)

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Created: {out_zip}")


if __name__ == "__main__":
    main()
