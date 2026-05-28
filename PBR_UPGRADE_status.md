# PBR Upgrade — Status
**Last updated:** 2026-05-28 (Fix 1 + Fix 2 + Fix 3 done, repo consolidated, folders reorganised)
**Plan file:** `C:\ai\PBR_UPGRADE_PLAN.md`
**All PBR folders now live under:** `C:\ai\PBR\`

---

## What is done

### Phase 1 — PBR Picker ✅
- Rhino picker — working
- Unreal picker (tkinter popup) — working

### Phase 2 — External PBR Ingest ✅
- `pbr_ingest.py` written and tested on a real pack (`alien-metal1-ue`, set 00005)
- Lives in `C:\ai\PBR\PBR_Textures\`

### Phase 2b — Ingest GUI ✅
- `pbr_ingest_gui.py` — double-click GUI, working
- `run_pbr_ingest.bat` — launcher
- Desktop shortcut on Esme's desktop

### Rhino — Physically Based material fix ✅ (2026-05-28)
- `create_pbr_material()` in `rhino_import.py` rewritten to use the `mat.PhysicallyBased` interface
- All 5 channels now load: BaseColor, Normal, Roughness, Metalness, Displacement
- Material shows as Physically Based type in the Rhino material editor
- File: `C:\ai\PBR\PBR_TORHINO\rhino_import.py`

### Unreal — AO support added ✅ (2026-05-27)
- `Ambient Occlusion A` param added to `TEXTURE_PARAMS` in `unreal_textureimport.py`
- Keywords: `ao`, `ambientocclusion`, `occlusion` — matches ComfyUI filenames like `AO_00008_.png`
- Both copies updated:
  - `C:\ai\PBR\PBR_TOUNREAL\unreal_textureimport.py`
  - `C:\Users\esmev\Documents\Unreal Projects\BlendMasterMaterial\Content\Python\unreal_textureimport.py`
- **Note for future:** `install.py` copies the source to the Unreal project — always edit BOTH or run install again after source changes

### Fix 1 — Ingest GUI normal map wording ✅ (2026-05-28)
- Group label changed to `What is the normal map type?`
- Grey note added below radio buttons: *"OpenGL maps will be converted to DirectX on import. Rhino flips them back automatically."*
- File: `C:\ai\PBR\PBR_Textures\pbr_ingest_gui.py`

### Fix 2 — AO skipping in ingest ✅ (2026-05-28)
- Removed `"ao"`, `"occlusion"`, and `"ambient"` from SKIP_WORDS — these are valid AO texture keywords, not preview files
- SKIP_WORDS now contains only: `"preview"`, `"thumbnail"`, `"thumb"`
- Fixed in both `pbr_ingest.py` and `pbr_ingest_gui.py`

### Fix 3 — Set numbering mismatch ✅ (2026-05-28)
**Rule:** BaseColor anchors the set number. Every channel in the same set gets that exact number. Next number = highest `BaseColor_XXXXX_` in the folder + 1. Missing channels leave no gap.

- `C:\ai\PBR\PBR_Textures\pbr_ingest.py` — `next_set_number()` now scans only `BaseColor_XXXXX_` files
- `C:\ai\ComfyUI_windows_portable\ComfyUI\custom_nodes\pbr_set_saver.py` — new custom ComfyUI node "PBR Set Saver". Replaces the 5–6 separate SaveImageKJ save nodes. All channels saved with one shared number.
- Both ComfyUI workflows updated:
  - `Texturemaker_CHORD_img2pbr_switchable_seamless.json` — 6 old save nodes replaced with 1 PBR Set Saver
  - `Texturemaker_CHORD_img2pbr_seamless.json` — 5 old save nodes replaced with 1 PBR Set Saver. Also fixed wrong output folder path.
- Backups saved to: `...\workflows\backups_pre_fix3\`

---

## What is pending

### Repo consolidation ✅ (2026-05-28)
- Consolidated into `Seanscrafts/PBR_MaterialMaker` — 2 commits pushed
- All folders moved under `C:\ai\PBR\`
- Config paths updated on this machine

---

## Known issues / things to watch

| Issue | Detail |
|---|---|
| Two copies of `unreal_textureimport.py` | One in the repo, one in the Unreal project Python folder. Changes must go to both until install.py workflow is improved |
| Displacement_00009_.png timing | Was generated after import ran — slot 07 in Unreal is missing Height. Needs manual fix or re-import |

---

## Next session — to do

### Issue 1 — Rhino normal map conversion
- `rhino_import.py` currently loads normal maps as-is
- Needs to detect OpenGL vs DirectX and flip the green channel on import if OpenGL
- The ingest GUI already asks about normal map type — the Rhino script needs to do the same or read that info

### Issue 2 — Unreal missing channels on import
- Metalness, Height/Displacement slots not being assigned when importing
- Material is created but those slots appear empty (no error thrown)
- Needs investigation: check parameter names in `unreal_textureimport.py` match what the master material expects

---

## Installing on a new machine

1. **Clone the repo:**
   `git clone https://github.com/Seanscrafts/PBR_MaterialMaker`
   Recommended location: somewhere like `C:\ai\PBR\PBR_MaterialMaker\`

2. **Run Rhino installer:**
   Run `rhino\install.py`. It will ask for the path to your `PBR_Textures` folder.
   Enter the full path — e.g. `C:\ai\PBR\PBR_Textures` or `D:\ai\PBR\PBR_Textures`.
   This copies `rhino_import.py` and a `pbr_config.json` into the Rhino AppData scripts folder.
   **Important:** if you ever move the PBR_Textures folder later, run install.py again — or manually update `pbr_config.json` at:
   `C:\Users\<username>\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts\pbr_config.json`

3. **Run Unreal installer:**
   Run `unreal\install.py` and enter the path to your `PBR_Textures` folder when prompted.

4. **Copy the custom ComfyUI node:**
   `pbr_set_saver.py` → `<ComfyUI folder>\ComfyUI\custom_nodes\`

5. **Update the output folder in each ComfyUI workflow:**
   Open the workflow in ComfyUI. Click the **"PBR Set Saver"** node and set the folder path to wherever `PBR_Textures` lives on that machine.

6. **`pbr_ingest.py` needs no changes** — it always saves to the same folder it lives in.
