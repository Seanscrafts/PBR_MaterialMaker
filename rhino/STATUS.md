# STATUS — PBR Material Maker (ComfyUI → Rhino 8)

**Last updated:** 2026-05-27 (session 6 — AO map added and confirmed working in Rhino ✓)

---

## What this project is

Uses ComfyUI (with CHORD model) to generate PBR texture maps from a reference image,
then imports those textures into Rhino 8 as a Physically Based material — automatically.

Same ComfyUI workflow as the Unreal version. New Rhino-specific import script.

---

## Project status

| Component | Status |
|---|---|
| Folder + Git repo | Created ✓ |
| GitHub repo | https://github.com/Esmesrepo/PBR-TORHINO ✓ |
| config.json | Created — texture_output_folder set to `C:\AI\PBR_Textures` ✓ |
| install.py | Created ✓ |
| rhino_import.py | Created ✓ |
| Script in Rhino folder | Manually copied to Rhino 8 scripts folder ✓ |
| workflows/ | Not needed — shared with PBR_TOUNREAL on same machine |

---

## ComfyUI workflows (shared with Unreal project)

Primary workflow: `Texturemaker_CHORD_img2pbr_switchable_seamless.json`

Located in: `C:\ai\PBR_TOUNREAL\workflows\` — no need to copy, both projects share the same ComfyUI install.

---

## Key file locations

| File | Path |
|---|---|
| This project | `C:\ai\PBR_TORHINO\` |
| Unreal version (reference) | `C:\ai\PBR_TOUNREAL\` |
| ComfyUI install | `D:\AI\ComfyUI_windows_portable\ComfyUI\` |
| Texture output folder | `C:\AI\PBR_Textures\` ✓ |

---

## What was done (session 1)

| Item | Detail |
|---|---|
| Repo created | `C:\ai\PBR_TORHINO\` + GitHub https://github.com/Esmesrepo/PBR-TORHINO |
| Shared texture folder | `C:\AI\PBR_Textures\` created |
| Unreal paths fixed | All 5 files in PBR_TOUNREAL updated from old path to `C:\AI\PBR_Textures\` |
| `install.py` | Written — copies scripts to Rhino scripts folder, sets texture path in config |
| `rhino_import.py` | Written — finds latest CHORD textures, creates Rhino 8 PBR material, applies to selection |
| Script deployed | Manually copied to `C:\Users\esmev\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts\` |
| Handoff doc | `HANDOFF_FOR_SEAN.md` on Desktop — for Sean to fix paths on his machine |

## What was done (session 3)

**PBR Set Picker added. Repo moved to Seanscrafts GitHub.**

| File | Change |
|---|---|
| `rhino_import.py` | Replaced auto-latest logic with `pick_texture_set()` — uses `rs.ListBox()` to list all available sets, user picks one. |
| `rhino_import_BACKUP.py` | Backup of previous version — do not delete |

- GitHub repo moved from Esmesrepo/PBR-TORHINO to `Seanscrafts/PBR_TORHINO`
- Git user set locally: Seanscrafts / pretorius.sean@gmail.com
- Live copy deployed to: `C:\Users\esmev\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts\`

## What was done (session 4) — 2026-05-27

**Trying to fix: script creates Custom material instead of Physically Based.**

Approaches tried — none worked:
- `mat.ToPhysicallyBased()` — runs without error but material still shows as Custom
- `mat.RenderPlugInId = Guid("99999999-...")` — no effect on type displayed
- `mat.PhysicallyBased.SetTexture(...)` — textures still not loading
- `rr.RenderContent.Create(sc.doc, PBR_TYPE_ID)` — getting closer, still debugging parameter errors

**RhinoMCP installed (2026-05-27):**
- Rhino plugin: installed via Rhino Package Manager (jingcheng-chen/rhinomcp)
- uv installed, MCP added to Claude Code
- Start server in Rhino with: `StartRhinoMCP`

---

## What was done (session 5) — 2026-05-27

**PBR material type FIXED ✓ — using RhinoMCP to test live inside Rhino.**

Root cause: the old approach used `sc.doc.Materials.Add()` (legacy system) which always creates a "Custom" type.  
Fix: use Rhino's Render Content system properly.

Working approach confirmed by live MCP testing:
- `rr.RenderContent.Create(sc.doc, PBR_TYPE_ID)` — creates a true Physically Based render material
- `rr.SimulatedTexture()` + `rr.RenderTexture.NewBitmapTexture(sim, sc.doc)` — correct way to make textures
- `rm.SetChild(tex, slot_name)` inside `BeginChange/EndChange` — attaches textures to PBR slots
- `attrs.RenderMaterial = rm` + `sc.doc.Objects.ModifyAttributes()` — applies to objects

PBR slot names confirmed working:
- basecolor → `pbr-base-color` + `pbr-base-color-on`
- roughness → `pbr-roughness` + `pbr-roughness-on`
- metallic → `pbr-metallic` + `pbr-metallic-on`
- normal → `pbr-bump` + `pbr-bump-on`
- displacement → `pbr-displacement` + `pbr-displacement-on`

**Second bug found and fixed same session:**
- `SetChild()` connects the texture but leaves the lightbulb (enable toggle) OFF
- Fix: call `rm.SetParameter("pbr-base-color-on", True)` etc. after each `SetChild()`
- Without this, all textures are connected but disabled → material renders white

Files updated:
- `C:\ai\PBR_TORHINO\rhino_import.py` ✓
- `C:\Users\esmev\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts\rhino_import.py` ✓ (live copy)

**Script is now fully working end-to-end. ✓**

---

## Next tasks

1. [x] Test `rhino_import.py` in Rhino 8 — working ✓
2. [x] Generate a test texture set in ComfyUI and test full flow — working ✓
3. [x] Commit everything to GitHub ✓
4. [x] PBR set picker added and working ✓
5. [x] Phase 2 — `pbr_ingest.py` written and tested ✓ — `C:\ai\PBR_Textures\pbr_ingest.py`
6. [x] `pbr_ingest_gui.py` — GUI version written, desktop shortcut created, working ✓ (2026-05-27)
7. [x] **DONE** — Fix `rhino_import.py` material type — now creates true Physically Based ✓
8. [x] **DONE** — Fix lightbulb issue — textures were connected but disabled, now enabled ✓
9. [x] Alpha / Opacity — **DROPPED** — out of scope (checked Unreal master mat, transparency not supported)
10. [x] **DONE** — Add Ambient Occlusion (AO) map to Rhino import script ✓ (slot: pbr-ambient-occlusion)
11. [ ] Test clean install on second machine

---

## Alpha / Opacity — DROPPED (out of scope)

**Decision made 2026-05-27.**

- Checked Unreal master material — transparency is not supported there either
- Opacity/transparency is beyond the scope of this project for both Unreal and Rhino
- Most CHORD outputs are solid materials anyway — not needed

**No action required.**

---

## Ambient Occlusion (AO) — DONE ✓

**Completed 2026-05-27 (session 6).**

ComfyUI is outputting `AO_*.png` files. Rhino import script updated to pick them up.

| Where | Status |
|---|---|
| ComfyUI CHORD workflow | AO map confirmed in output ✓ |
| Rhino import script | `pbr-ambient-occlusion` slot added and tested ✓ |
| Unreal master material | Not yet checked |

**Slot used:** `pbr-ambient-occlusion` + `pbr-ambient-occlusion-on` — confirmed working ✓

---

## Future — Shared texture library (both Unreal + Rhino)

**Goal:** One shared output folder that both tools can read from. Pick an existing texture set instead of always generating new ones.

**How it would work:**
- All generated texture sets saved to a shared folder (e.g. `D:\AI\PBR_Textures\`)
- Each set in its own numbered subfolder: `001_brick\`, `002_concrete\`, etc.
- Both import scripts show a list of existing sets to choose from
- No need to re-generate textures already in the library

**Note:** The folder structure should be consistent from the start so this is easy to add later.
