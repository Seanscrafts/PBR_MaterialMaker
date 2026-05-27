# -*- coding: utf-8 -*-
import os
import json
import glob

import Rhino
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
}


def find_latest_textures(texture_folder):
    if not os.path.exists(texture_folder):
        raise IOError("Texture folder not found:\n" + texture_folder)

    channels = {}
    for channel, prefix in CHANNEL_PREFIXES.items():
        pattern = os.path.join(texture_folder, prefix + "_*.png")
        matches = sorted(
            glob.glob(pattern),
            key=lambda p: os.path.getmtime(p),
            reverse=True
        )
        if matches:
            channels[channel] = matches[0]

    return channels


# --- Material creation ---

def make_texture(path):
    tex = Rhino.DocObjects.Texture()
    tex.FileName = path
    return tex


def create_pbr_material(name, channels):
    mat = Rhino.DocObjects.Material()
    mat.Name = name
    TT = Rhino.DocObjects.TextureType

    if "basecolor" in channels:
        try:
            mat.SetTexture(make_texture(channels["basecolor"]), TT.PBR_BaseColor)
        except Exception:
            mat.SetBitmapTexture(channels["basecolor"])
        print("  BaseColor:     " + os.path.basename(channels["basecolor"]))

    if "roughness" in channels:
        try:
            mat.SetTexture(make_texture(channels["roughness"]), TT.PBR_Roughness)
            print("  Roughness:     " + os.path.basename(channels["roughness"]))
        except Exception:
            pass

    if "metallic" in channels:
        try:
            mat.SetTexture(make_texture(channels["metallic"]), TT.PBR_Metallic)
            print("  Metallic:      " + os.path.basename(channels["metallic"]))
        except Exception:
            pass

    if "normal" in channels:
        mat.SetTexture(make_texture(channels["normal"]), TT.Bump)
        print("  Normal (bump): " + os.path.basename(channels["normal"]))

    if "displacement" in channels:
        try:
            mat.SetTexture(make_texture(channels["displacement"]), TT.PBR_Displacement)
            print("  Displacement:  " + os.path.basename(channels["displacement"]))
        except Exception:
            pass

    mat_index = sc.doc.Materials.Add(mat)
    return mat_index


# --- Apply to objects ---

def apply_to_objects(mat_index):
    obj_ids = rs.GetObjects(
        "Select objects to apply material (Enter to skip)",
        preselect=True
    )
    if not obj_ids:
        print("No objects selected - material added to document, not applied.")
        return 0

    for obj_id in obj_ids:
        rs.ObjectMaterialIndex(obj_id, mat_index)
        rs.ObjectMaterialSource(obj_id, 1)

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
        channels = find_latest_textures(texture_folder)

        if not channels:
            rs.MessageBox(
                "No texture files found in:\n" + texture_folder + "\n\nGenerate textures in ComfyUI first.",
                title="PBR Import"
            )
            return

        mat_count = sc.doc.Materials.Count + 1
        mat_name = prefix + "{:02d}".format(mat_count)

        print("\nCreating material: " + mat_name)
        mat_index = create_pbr_material(mat_name, channels)

        applied = apply_to_objects(mat_index)
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
