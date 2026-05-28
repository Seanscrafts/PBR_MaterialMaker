# PBR Upgrade — Status
**Last updated:** 2026-05-28 (Fix 1 + Fix 2 + Fix 3 done)
**Plan file:** `C:\ai\PBR_UPGRADE_PLAN.md`

---

## What is done

### Phase 1 — PBR Picker ✅
- Rhino picker — working
- Unreal picker (tkinter popup) — working

### Phase 2 — External PBR Ingest ✅
- `pbr_ingest.py` written and tested on a real pack (`alien-metal1-ue`, set 00005)
- Lives in `C:\ai\PBR_Textures\`

### Phase 2b — Ingest GUI ✅
- `pbr_ingest_gui.py` — double-click GUI, working
- `run_pbr_ingest.bat` — launcher
- Desktop shortcut on Esme's desktop
- Not yet committed to repo (waiting on repo consolidation)

### Rhino — Physically Based material fix ✅ (2026-05-28)
- `create_pbr_material()` in `rhino_import.py` rewritten to use the `mat.PhysicallyBased` interface
- All 5 channels now load: BaseColor, Normal, Roughness, Metalness, Displacement
- Material shows as Physically Based type in the Rhino material editor
- File: `C:\ai\PBR_TORHINO\rhino_import.py`

### Unreal — AO support added ✅ (2026-05-27)
- `Ambient Occlusion A` param added to `TEXTURE_PARAMS` in `unreal_textureimport.py`
- Keywords: `ao`, `ambientocclusion`, `occlusion` — matches ComfyUI filenames like `AO_00008_.png`
- Both copies updated:
  - `C:\ai\PBR_TOUNREAL\unreal_textureimport.py`
  - `C:\Users\esmev\Documents\Unreal Projects\BlendMasterMaterial\Content\Python\unreal_textureimport.py`
- **Note for future:** `install.py` copies the source to the Unreal project — always edit BOTH or run install again after source changes

### Fix 1 — Ingest GUI normal map wording ✅ (2026-05-28)
- Group label changed to `What is the normal map type?`
- Grey note added below radio buttons: *"OpenGL maps will be converted to DirectX on import. Rhino flips them back automatically."*
- File: `C:\ai\PBR_Textures\pbr_ingest_gui.py`

### Fix 2 — AO skipping in ingest ✅ (2026-05-28)
- Removed `"ao"`, `"occlusion"`, and `"ambient"` from SKIP_WORDS — these are valid AO texture keywords, not preview files
- SKIP_WORDS now contains only: `"preview"`, `"thumbnail"`, `"thumb"`
- Fixed in both `pbr_ingest.py` and `pbr_ingest_gui.py`

### Fix 3 — Set numbering mismatch ✅ (2026-05-28)
**Rule:** BaseColor anchors the set number. Every channel in the same set gets that exact number. Next number = highest `BaseColor_XXXXX_` in the folder + 1. Missing channels leave no gap.

- `C:\ai\PBR_Textures\pbr_ingest.py` — `next_set_number()` now scans only `BaseColor_XXXXX_` files
- `C:\ai\ComfyUI_windows_portable\ComfyUI\custom_nodes\pbr_set_saver.py` — new custom ComfyUI node "PBR Set Saver". Replaces the 5–6 separate SaveImageKJ save nodes. All channels saved with one shared number.
- Both ComfyUI workflows updated:
  - `Texturemaker_CHORD_img2pbr_switchable_seamless.json` — 6 old save nodes replaced with 1 PBR Set Saver
  - `Texturemaker_CHORD_img2pbr_seamless.json` — 5 old save nodes replaced with 1 PBR Set Saver. Also fixed wrong output folder path.
- Backups saved to: `...\workflows\backups_pre_fix3\`

---

## What is pending

### Repo consolidation 🟡
- Merge `PBR_TORHINO`, `PBR_TOUNREAL`, and ingest tools into one repo: `Seanscrafts/PBR_MaterialMaker`
- See plan for full folder structure and steps
- After consolidation: update `run_pbr_ingest.bat` path in the desktop shortcut

---

## Known issues / things to watch

| Issue | Detail |
|---|---|
| Two copies of `unreal_textureimport.py` | One in the repo, one in the Unreal project Python folder. Changes must go to both until install.py workflow is improved |
| Displacement_00009_.png timing | Was generated after import ran — slot 07 in Unreal is missing Height. Needs manual fix or re-import |

---

## Installing on a new machine

1. **Copy the custom node:**
   `pbr_set_saver.py` → `<ComfyUI folder>\ComfyUI\custom_nodes\`

2. **Update the output folder in each workflow:**
   Open the workflow in ComfyUI. Click the **"PBR Set Saver"** node and change the folder path to wherever `PBR_Textures` lives on that machine.
   - C drive: `C:\ai\PBR_Textures`
   - D drive: `D:\ai\PBR_Textures`

3. **`pbr_ingest.py` needs no changes** — it always saves to the same folder it lives in.
