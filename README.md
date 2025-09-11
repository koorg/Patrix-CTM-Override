# Patrix-CTM-Compatibility-Override

**A tiny utility that builds a mini resource-pack to replace Patrix’s CTM “placeholder” textures (the ones that say _“ENABLE CONNECT TEXTURE”_) with real textures — so other mods that bypass CTM stop showing that error image.**

- **SPDX-License-Identifier:** MIT  
- **Copyright (c) 2025 Koorg**

---

## Why this exists (the short version)

Patrix relies heavily on **CTM (Connected Textures)** rules (via **Continuity** on Fabric or OptiFine-style CTM). To encourage you to enable CTM, some **vanilla texture slots** in Patrix are intentionally populated with a visible **placeholder** that reads **“ENABLE CONNECT TEXTURE”**.  

When Minecraft renders blocks **through the CTM pipeline**, those placeholders are never used: CTM swaps in the correct, beautiful Patrix tiles.

However, **some mods** (e.g., physics/particle/mini-map/inventory preview mods) **don’t use the CTM pipeline** for certain renders. Instead, they **directly fetch the vanilla texture** at paths like `assets/minecraft/textures/block/stone.png`. If that slot contains the Patrix placeholder, you’ll literally see **“ENABLE CONNECT TEXTURE”** on broken pieces, particles, debris, thumbnails, etc.

This project **builds a tiny override pack** that replaces a few critical vanilla slots (e.g., `stone.png`, `grass_block_top.png`) **with actual Patrix art** (copied from Patrix’s CTM directories). Result:  
- CTM users keep all CTM goodness as before.  
- **Non-CTM renderers** (like some physics/particle systems) **stop showing the placeholder** and use a reasonable base texture instead.

> **Important:** This is not limited to any single mod. **PhysicsMod** is a common example (broken bits/particles), but **any mod that bypasses CTM** can surface the placeholder. If you see that image, it means **that rendering path is not CTM-aware**.

---

## What the tool does

Given a Patrix `.zip` (basic archive only), the scripts:

1. **Detect the resolution** (`32x`, `64x`, `128x`, or `256x`) from the filename.
2. **Extract specific Patrix CTM tiles** (e.g.,  
   - `assets/minecraft/optifine/ctm/patrix/grass/block/top/1.png` → `assets/minecraft/textures/block/grass_block_top.png`  
   - `assets/minecraft/optifine/ctm/patrix/stone/1.png` → `assets/minecraft/textures/block/stone.png`)
3. **Assemble a minimal override pack**:
   ```
   Patrix_32x_CTMOverride/
   ├── assets/
   │   └── minecraft/
   │       └── textures/
   │           └── block/
   │               ├── grass_block_top.png
   │               └── stone.png
   └── pack.mcmeta
   ```
4. **Zip it** into `Patrix_<RES>_CTMOverride.zip`.

You then **load this override pack at the very top** of your resource packs list (above Patrix).

> By default, the override currently targets **grass top** and **stone** — the most commonly visible placeholders in physics/particle scenarios. You can extend it (see “Extending to more blocks”).

---

## The “ENABLE CONNECT TEXTURE” error — deep dive

### What it actually means
- It is **not** a generic Minecraft error; it is a **Patrix placeholder texture** deliberately placed in **vanilla texture slots** to nudge players to **enable CTM**.
- When **Continuity/CTM is active**, CTM **replaces** those placeholders at render time with the correct tiles.
- If you **still see the text**, that specific **render path is not CTM-aware** (or CTM is disabled/misconfigured). Typical culprits:
  - **Physics/Particles**: breakage debris, ragdoll chunks, dust clouds, etc.
  - **Thumbnails/Icons**: inventory previews, JEI-like widgets, UI list renders.
  - **Map/Minimap/Scanner**: tools that sample base textures directly.
  - **Custom Model Renderers**: mods that build their own sprite fetch logic.

### Why PhysicsMod often triggers it
- Many physics/particle engines **read the base atlas** (vanilla texture path) to spawn debris/particles.
- If the base slot contains the Patrix **“ENABLE CONNECT TEXTURE”** placeholder, that’s what the particles will show.
- That **doesn’t mean Patrix or CTM is broken**. It means that **this particular renderer** didn’t hand off to **CTM** for its texture lookup.

### Not just PhysicsMod
- Any mod that **calls vanilla texture paths directly**, **samples atlases before CTM substitution**, or **renders off-thread/off-pipeline** may exhibit the same behavior.
- Seeing the text is a **compatibility signal**: “This render path does **not** support CTM substitution.”

### What this override fixes — and what it doesn’t
- ✅ **Fixes** non-CTM renderers **for the blocks we override** by putting **actual Patrix art** back into those vanilla slots.
- ✅ **Leaves CTM visuals intact** for normal world rendering (CTM continues to apply).
- ❌ Doesn’t “teach” the mod to use CTM; it **sidesteps** the placeholder by restoring sane base textures.
- ❌ Doesn’t overhaul every block; it’s a **selective patch**. You can add more (see below).

---

## Installation & load order

1. Install Patrix and your CTM solution (**Continuity** on Fabric or an OptiFine-style CTM setup).
2. Build the override zip (see Usage).
3. **Load order in Minecraft (top → bottom):**
   1. `Patrix_<RES>_CTMOverride.zip`  ← **this project**
   2. Patrix (matching resolution)
   3. Any other packs you use
   4. Default

> The override must be **above** Patrix so the vanilla slots we restore take precedence when mods read them directly.  
> After changing packs, press **F3+T** to reload textures (Java).

---

## Usage

You have **two equivalent implementations**: **Python** and **PowerShell**.

### Python
```bash
python create_patrix_overrid.py Patrix_1.21.8_32x_basic.zip
# Produces: Patrix_32x_CTMOverride.zip
```

### PowerShell (Windows)
```powershell
.\Create-PatrixOverride.ps1 -InputZip "Patrix_1.21.8_32x_basic.zip"
# Produces: Patrix_32x_CTMOverride.zip
```

**Notes**
- The scripts currently support **32x, 64x, 128x, 256x**.
- The Patrix input filename should include the resolution (e.g., `..._32x_...`) so detection works.
- The resulting pack includes a `pack.mcmeta` with:
  ```json
  {
    "pack": {
      "pack_format": 64,
      "description": "Override CTM placeholders (stone/grass top) using Patrix CTM tiles for non-CTM renderers."
    }
  }
  ```

---

## Extending to more blocks

If you encounter the placeholder on other blocks (e.g., gravel, sand, ores):

1. Find the **relevant CTM tile** inside the Patrix zip under `assets/minecraft/optifine/ctm/patrix/...`.
2. Copy (or script) a representative tile (often `1.png` or an appropriate base tile from the CTM set).
3. Place it into the **vanilla slot** in the override pack, e.g.:
   - `assets/minecraft/textures/block/gravel.png`
   - `assets/minecraft/textures/block/sand.png`
4. Re-zip the override and put it **above** Patrix.

> Tip: Prefer a **neutral, generic** tile from the CTM set so it looks consistent when used for particles/thumbnails.

---

## Troubleshooting

- **I still see “ENABLE CONNECT TEXTURE”.**
  - Ensure the override zip is **above** Patrix in the pack list.
  - Confirm the **resolution** matches the Patrix pack you’re using.
  - Reload textures (**F3+T**) and/or **restart** the game after changing packs.
  - Verify the **paths inside the zip** match the structure shown above.
  - Some mods cache textures; look for a **“reload resources”** option in the mod or restart the game.
  - The block you’re seeing may **not yet be overridden**. Add it (see “Extending…”).

- **CTM visuals changed in world rendering.**
  - The override only drops base textures into vanilla slots. If world CTM looks wrong:
    - Check that **Continuity/CTM is enabled** and compatible with your version.
    - Make sure **other packs** above Patrix are not interfering.

- **Particles still look odd.**
  - Many mods downscale or stylize particles. The override ensures they’re not the placeholder; it doesn’t control the particle style.

---

## What about proper CTM support in mods?

The ideal fix is for mods to **query the post-CTM sprite** (or expose hooks/APIs that do). Until then, this override is a **pragmatic compatibility shim**:
- Keeps CTM for normal world rendering.
- Provides respectable **fallbacks** for **non-CTM renderers**.

---

## Security, licensing & ethics

- **You must own a legitimate copy** of the Patrix pack you’re targeting.
- The override **extracts a few tiles from your local Patrix zip** purely to repair non-CTM render paths **on your machine**.
- **Do not redistribute** Patrix assets if you got them via the Patreon subscription.

This repository (scripts and docs) is licensed under **MIT** (see `LICENSE`).

---

## FAQ

**Q: Does this enable CTM?**  
**A:** No. It just **stops the placeholder** from appearing in **non-CTM** renderers by restoring sensible base textures.

**Q: Is this only for PhysicsMod?**  
**A:** No. PhysicsMod is a **common case**, but **any mod** that bypasses CTM may show the placeholder. This override helps across the board.

**Q: Will this hurt performance?**  
**A:** It’s a minimal pack with 2–N textures. Overhead is negligible.

**Q: Can I use it on Forge / Fabric / Quilt?**  
**A:** The pack is **just a resource pack**; it’s loader-agnostic. For **CTM features**, use **Continuity** (Fabric) or an equivalent CTM solution for your mod loader.

**Q: Which Minecraft versions?**  
**A:** The override targets the **filesystem layout** used by Patrix and modern Minecraft. If Mojang bumps `pack_format`, update `pack.mcmeta` accordingly. The default here (`64`) targets recent 1.21.x-style packs.

---

## Contributing

- PRs welcome for **extra block overrides**, **auto-detection improvements**, and **robust filename parsing**.
- Please do **not** include Patrix assets in PRs.

---

## Example session

```bash
# Build an override for a 32x Patrix pack:
python create_patrix_overrid.py Patrix_1.21.8_32x_basic.zip

# Result:
#   Patrix_32x_CTMOverride.zip

# Load order (top → bottom) in Minecraft:
#   1) Patrix_32x_CTMOverride.zip
#   2) Default Connected Textures (provided by Continuity)
#   3) Patrix_1.21.8_32x_addon.zip
#   4) Patrix_1.21.8_32x_basic.zip
#   5) Default resource pack
```

You should now find that **broken stone/grass particles and debris** no longer shout **“ENABLE CONNECT TEXTURE”** — even when rendered by mods that don’t speak CTM — while your **world** continues to benefit from **full Patrix + CTM** visuals.

BTW, you should try PhysicsMod Pro and Patrix 128x textures, definitely.
