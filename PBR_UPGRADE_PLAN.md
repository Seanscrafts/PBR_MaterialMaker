# PBR Upgrade Plan
**Created:** 2026-05-26
**Author:** Sean (working on Esme's machine)

---

## What this plan covers

Upgrading the two PBR import tools (Rhino and Unreal) so that:
1. You can choose which PBR set to import, instead of always getting the latest
2. You can bring in PBR textures from external packs (not just ComfyUI-generated ones)

---

## Repos involved

| Repo | GitHub account | Local path |
|---|---|---|
| PBR_TORHINO | Esme (Esmesrepo) | `C:\ai\PBR_TORHINO\` |
| PBR_TOUNREAL | Sean (Seanscrafts) — https://github.com/Seanscrafts/PBR_TOUNREAL | `C:\ai\PBR_TOUNREAL\` |
| Shared texture folder | Not a repo | `C:\ai\PBR_Textures\` |

**Path note:** This machine (Esme's) has C drive only. Sean's machine has C and D drives.
All scripts read paths from `config.json` — never hardcoded.

---

## Phase 1 — PBR Picker

**Goal:** Instead of auto-importing the latest set, show a list of all available sets and let you choose.

### How it works

The `PBR_Textures` folder is scanned. Files are grouped by their number:
- Set 00001 — BaseColor, Normal, Roughness, Metalness, Displacement
- Set 00002 — BaseColor, Normal, Roughness, Metalness, Displacement

A picker is shown. You select the set you want. That set is imported.

### Changes needed

| File | What changes |
|---|---|
| `PBR_TORHINO\rhino_import.py` | Replace "find latest" logic with a `rs.ListBox()` picker showing all available sets |
| `PBR_TOUNREAL\unreal_textureimport.py` | Replace "find latest" logic with a `tkinter` popup picker |

### Status
- [x] Rhino picker — working ✓
- [x] Unreal picker — working ✓

---

## Phase 2 — External PBR Ingest

**Goal:** Take PBR textures from any external source (downloaded pack, etc.), rename and label them to match the standard format, and add them to `PBR_Textures` so they appear in the picker.

### New file: `pbr_ingest.py`

A standalone script you run from the command line (not inside Rhino or Unreal).

**What it does:**
1. You point it at a folder containing an external PBR pack
2. It reads the filenames and identifies which file is which channel (BaseColor, Normal, Roughness, Metalness, Displacement) using common keyword patterns
3. Shows you the detected mapping so you can confirm or correct it
4. Asks: is the normal map DirectX or OpenGL? (Handles the green channel difference between Unreal and Rhino)
5. Assigns the next available number in `PBR_Textures`
6. Copies and renames files to the standard format: `BaseColor_00003_.png` etc.
7. The new set immediately appears in the picker for both Rhino and Unreal

### Common filename keywords to detect

| Channel | Keywords it looks for |
|---|---|
| BaseColor | color, colour, col, basecolor, albedo, diffuse |
| Normal | normal, nrm, nor, nml |
| Roughness | roughness, rough, rgh |
| Metalness | metallic, metalness, metal, met |
| Displacement | displacement, disp, height, depth |

### Where `pbr_ingest.py` lives

Placed in `C:\ai\PBR_Textures\` — neutral ground, not inside either repo.
Can also be copied into whichever repo makes sense later.

### Status
- [x] Write `pbr_ingest.py` — written to `C:\ai\PBR_Textures\pbr_ingest.py` ✓
- [x] Test with a real external pack — tested on `alien-metal1-ue`, set 00005 created ✓

---

## Phase 2b — Ingest GUI (done 2026-05-27)

**Goal:** Make `pbr_ingest.py` runnable by double-click — no terminal.

### What was built

| File | Location |
|---|---|
| `pbr_ingest_gui.py` | `C:\ai\PBR_Textures\` |
| `run_pbr_ingest.bat` | `C:\ai\PBR_Textures\` |
| Desktop shortcut | `PBR Ingest` on Esme's desktop |

Uses Python 3.14 (installed 2026-05-27) + tkinter. Folder picker → auto-detect channels → confirm → copies files.

### Status
- [x] GUI written and working ✓
- [x] Desktop shortcut created ✓
- [ ] Commit to repo — pending repo consolidation (see below)

---

## Rhino material type fix ✅ (2026-05-28)

`create_pbr_material()` in `C:\ai\PBR_TORHINO\rhino_import.py` rewritten to use the `mat.PhysicallyBased` interface. All 5 channels now load correctly. Material shows as Physically Based in the Rhino material editor.

---

## Pending fixes — Ingest + Numbering (next sessions)

### Fix 1 — Ingest GUI normal map wording ✅ (2026-05-28)
- Group label changed to `What is the normal map type?`
- Grey note added below radio buttons: *"OpenGL maps will be converted to DirectX on import. Rhino flips them back automatically."*
- File: `C:\ai\PBR_Textures\pbr_ingest_gui.py`

---

### Fix 2 — AO skipping in ingest ✅ (2026-05-28)
- Removed `"ao"`, `"occlusion"`, and `"ambient"` from SKIP_WORDS in both `pbr_ingest.py` and `pbr_ingest_gui.py`
- SKIP_WORDS now contains only: `"preview"`, `"thumbnail"`, `"thumb"`

---

### Fix 3 — Set numbering: BaseColor anchors the number
**Problem:** Each channel is numbered independently. If a drag-and-drop pack is missing a channel, that channel's counter skips a number while others don't. ComfyUI has its own internal counter and does not know about gaps left by ingest. Result: channels from the same set end up with different numbers and the import scripts cannot pair them.

**Fix — standard to adopt:**
- The set number is always determined by the **BaseColor/Albedo** file
- All other channels in the same set (Normal, Roughness, Metalness, Displacement, AO) use that exact same number
- If a channel is missing from a pack, there is simply no file for it — the number is not used for that channel, and the next pack still increments from the last BaseColor number
- Both `pbr_ingest.py` and the ComfyUI workflow must agree on the next available number by reading the highest existing BaseColor number in `PBR_Textures` and adding 1

**Files to change:**
- `C:\ai\PBR_Textures\pbr_ingest.py` — rewrite numbering logic to anchor on BaseColor
- ComfyUI workflow JSONs in `C:\ai\PBR_TOUNREAL\workflows\` — fix counter to read max BaseColor number from `PBR_Textures` folder, not use an internal per-channel counter

---

## Repo Consolidation (next session — do after Rhino fix)

**Goal:** Merge the two separate repos and the ingest tools into one single repo on Seanscrafts GitHub.

**Why:** All three parts (Rhino importer, Unreal importer, ingest tool) are one project.
They share the same texture folder and workflow. One repo is simpler to manage.

### New repo structure

```
PBR_MaterialMaker/          ← new single repo on Seanscrafts
  rhino/
    rhino_import.py
    rhino_import_BACKUP.py
    install.py
    config.json
    STATUS.md
  unreal/
    unreal_textureimport.py
    unreal_textureimport_BACKUP.py
    install.py
    config.json
    workflows/
  ingest/
    pbr_ingest.py
    pbr_ingest_gui.py
    run_pbr_ingest.bat
  README.md
  PBR_UPGRADE_PLAN.md
```

### Steps (do in one session)

1. Create new GitHub repo: `Seanscrafts/PBR_MaterialMaker`
2. Create the folder structure above locally
3. Copy files from `PBR_TORHINO\`, `PBR_TOUNREAL\`, and `PBR_Textures\` into the right subfolders
4. Check all scripts still reference paths from `config.json` — no hardcoded paths
5. Initial commit and push to new repo
6. Archive or delete old repos (`PBR_TORHINO`, `PBR_TOUNREAL`) on GitHub

### Note on the desktop shortcut

After consolidation, update `run_pbr_ingest.bat` path in the desktop shortcut if the file moves.

---

## Phase 3 — Future (not planned yet)

- Named subfolders: `001_brick\`, `002_marble\` instead of flat files
- A simple preview or thumbnail alongside the picker
- Batch ingest (multiple packs at once)

---

## Git workflow (current — before consolidation)

1. **PBR_TORHINO changes** — push as Seanscrafts
2. **PBR_TOUNREAL changes** — push as Seanscrafts

## Git workflow (after consolidation)

Everything pushes to `Seanscrafts/PBR_MaterialMaker` — one repo, one account.

---
