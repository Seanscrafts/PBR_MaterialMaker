# PBR MaterialMaker

Generate PBR textures from a reference image using ComfyUI (CHORD model) and import them directly into **Rhino 8** or **Unreal Engine 5** as a properly configured material — automatically.

## What's in this repo

| Folder | What it does |
|---|---|
| `rhino/` | Import script for Rhino 8 — creates a true Physically Based material with all 6 maps |
| `unreal/` | Import script for Unreal Engine 5 — creates a material instance from M_BlendMaster_Nanite |
| `ingest/` | Tool for adding external PBR texture packs to your library |

## How the workflow works

1. Drop a reference image into ComfyUI
2. Run the CHORD workflow (in `unreal/workflows/`) — outputs BaseColor, Normal, Roughness, Metalness, Displacement, AO
3. Run `rhino/rhino_import.py` inside Rhino **or** `unreal/unreal_textureimport.py` inside Unreal
4. Pick your texture set from the popup — done

## Texture maps supported

| Map | ComfyUI prefix |
|---|---|
| Base Colour | `BaseColor_` |
| Normal | `Normal_` |
| Roughness | `Roughness_` |
| Metalness | `Metalness_` |
| Displacement | `Displacement_` |
| Ambient Occlusion | `AO_` |

## Requirements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) with CHORD model
- Rhino 8 (for the Rhino importer)
- Unreal Engine 5.7 (for the Unreal importer)
- Python 3

## Setup

Each tool has its own `install.py`. Run it once to configure your paths:

```
cd rhino
python install.py

cd unreal
python install.py
```

Paths are stored in each tool's `config.json` — nothing is hardcoded.

## Adding external texture packs

Use the ingest tool to add downloaded PBR packs to your shared library:

```
cd ingest
python pbr_ingest_gui.py
```

Or double-click `run_pbr_ingest.bat`.

The tool detects which file is which channel, lets you confirm the mapping, then renames and copies everything to the shared texture folder — it immediately appears in the picker for both Rhino and Unreal.

## ComfyUI workflow

Primary workflow: `unreal/workflows/Texturemaker_CHORD_img2pbr_switchable_seamless.json`

## Upgrade plan

See `PBR_UPGRADE_PLAN.md` for the full project history and future plans.
