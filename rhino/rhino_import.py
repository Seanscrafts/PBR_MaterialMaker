# -*- coding: utf-8 -*-
import os
import json
import glob
import System

import Rhino
import Rhino.Render as rr
import rhinoscriptsyntax as rs
import scriptcontext as sc


# --- Config loading ---

def find_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for name in ("pbr_config.json", "config.json"):
        p = os.path.join(script_dir, name)
        if os.path.exists(p):
            return p
    raise IOError("pbr_config.json not found. Run install.py first.")


def load_config():
    config_path = find_config()
    with open(config_path, "r") as f:
        return json.load(f)


# --- Texture discovery ---

CHANNEL_PREFIXES = {
    "basecolor":    "BaseColor",
    "normal":       "Normal",
    "roughness":    "Roughness",
    "metallic":     "Metalness",
    "displacement": "Displacement",
    "ao":           "AO",
}

# Child slot names and their enable-parameter for Rhino 8 Physically Based material
# slot = connects the texture,  on_param = turns the lightbulb ON so it actually renders
PBR_CHANNEL_SLOTS = {
    "basecolor":    ("pbr-base-color",          "pbr-base-color-on"),
    "roughness":    ("pbr-roughness",            "pbr-roughness-on"),
    "metallic":     ("pbr-metallic",             "pbr-metallic-on"),
    "normal":       ("pbr-bump",                 "pbr-bump-on"),
    "displacement": ("pbr-displacement",         "pbr-displacement-on"),
    "ao":           ("pbr-ambient-occlusion",    "pbr-ambient-occlusion-on"),
}

# TypeId for Rhino's built-in Physically Based material
PBR_TYPE_ID = System.Guid("5a8d7b9b-cdc9-49de-8c16-2ef64fb097ab")


def find_all_sets(texture_folder):
    sets = {}
    for channel, prefix in CHANNEL_PREFIXES.items():
        pattern = os.path.join(texture_folder, prefix + "_*.png")
        for filepath in glob.glob(pattern):
            name = os.path.splitext(os.path.basename(filepath))[0]
            parts = name.split("_")
            if len(parts) >= 2 and parts[-2].isdigit():
                num = parts[-2]
                if num not in sets:
                    sets[num] = {}
                sets[num][channel] = filepath
    return sets


def pick_texture_set(texture_folder):
    if not os.path.exists(texture_folder):
        raise IOError("Texture folder not found:\n" + texture_folder)

    sets = find_all_sets(texture_folder)

    if not sets:
        return {}

    sorted_nums = sorted(sets.keys(), key=lambda x: int(x))

    if len(sorted_nums) == 1:
        return sets[sorted_nums[0]]

    labels = ["Set {}  —  {} maps".format(n, len(sets[n])) for n in sorted_nums]

    choice = rs.ListBox(labels, "Choose a PBR set to import", "Select PBR Set")

    if choice is None:
        return None

    chosen_num = sorted_nums[labels.index(choice)]
    return sets[chosen_num]


# --- Material creation ---

def make_render_texture(path):
    """Create a Rhino render texture from a file path."""
    sim = rr.SimulatedTexture()
    sim.Filename = path
    return rr.RenderTexture.NewBitmapTexture(sim, sc.doc)


def create_pbr_material(name, channels):
    """
    Create a true Physically Based material in Rhino 8.
    Uses RenderContent.Create so it appears as 'Physically Based'
    in the Materials panel — not 'Custom'.
    """
    rm = rr.RenderContent.Create(sc.doc, PBR_TYPE_ID)

    if rm is None:
        raise Exception("Failed to create Physically Based render material.")

    rm.BeginChange(rr.RenderContent.ChangeContexts.Program)
    rm.Name = name

    # Attach each texture as a child in the correct PBR slot
    # SetChild connects the texture; SetParameter turns the lightbulb ON
    for ch, (slot, on_param) in PBR_CHANNEL_SLOTS.items():
        if ch in channels:
            tex = make_render_texture(channels[ch])
            rm.SetChild(tex, slot)
            rm.SetParameter(on_param, True)
            print("  " + ch + ":  " + os.path.basename(channels[ch]))

    rm.EndChange()
    return rm


# --- Apply to objects ---

def apply_to_objects(rm):
    """Apply the render material to user-selected objects."""
    obj_ids = rs.GetObjects(
        "Select objects to apply material (Enter to skip)",
        preselect=True
    )
    if not obj_ids:
        print("No objects selected - material added to document, not applied.")
        return 0

    for obj_id in obj_ids:
        rhino_obj = sc.doc.Objects.Find(obj_id)
        if rhino_obj:
            attrs = rhino_obj.Attributes.Duplicate()
            attrs.MaterialSource = Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject
            attrs.RenderMaterial = rm
            sc.doc.Objects.ModifyAttributes(rhino_obj, attrs, True)

    return len(obj_ids)


# --- Main ---

def main():
    try:
        config = load_config()
        texture_folder = config.get("texture_output_folder", "")
        prefix = config.get("rhino_material_name_prefix", "PBR_")

        if not texture_folder:
            rs.MessageBox(
                "Texture folder is not configured.\nRun install.py first.",
                title="PBR Import"
            )
            return

        print("\nScanning: " + texture_folder)
        channels = pick_texture_set(texture_folder)

        if channels is None:
            return

        if not channels:
            rs.MessageBox(
                "No texture files found in:\n" + texture_folder +
                "\n\nGenerate textures in ComfyUI first.",
                title="PBR Import"
            )
            return

        # Name the material based on how many PBR materials already exist
        mat_count = sc.doc.RenderMaterials.Count + 1
        mat_name = prefix + "{:02d}".format(mat_count)

        print("\nCreating material: " + mat_name)
        rm = create_pbr_material(mat_name, channels)

        applied = apply_to_objects(rm)
        sc.doc.Views.Redraw()

        msg = "Material '" + mat_name + "' created."
        if applied:
            msg += "\nApplied to " + str(applied) + " object(s)."
        else:
            msg += "\nFind it in the Materials panel."

        print("\n" + msg)
        rs.MessageBox(msg, title="PBR Import")

    except Exception as e:
        rs.MessageBox("Error:\n" + str(e), title="PBR Import Error")
        raise


main()
