import os
import sys
import shutil
import re

# ── Channel keyword map ────────────────────────────────────────────────────────
# Checked from the END of the filename so material names (e.g. "alien-metal")
# don't accidentally match before the actual channel keyword.
CHANNEL_KEYWORDS = {
    "BaseColor":    ["basecolor", "albedo", "alb", "diffuse"],
    "Normal":       ["normal", "nrm", "nor", "nml"],
    "Roughness":    ["roughness", "rough", "rgh"],
    "Metalness":    ["metallic", "metalness", "metal"],
    "Displacement": ["displacement", "disp", "height", "depth"],
}

# Segments that mean "skip this file entirely"
SKIP_WORDS = {"preview", "thumbnail", "thumb"}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tga", ".exr", ".tiff", ".tif"}

# Script lives inside PBR_Textures — output goes to the same folder
TEXTURE_FOLDER = os.path.dirname(os.path.abspath(__file__))


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_segments(filename):
    """Split filename (no extension) into lowercase parts on - _ . characters."""
    name = os.path.splitext(filename)[0].lower()
    return re.split(r"[-_.]", name)


def is_skip_file(filename):
    return any(seg in SKIP_WORDS for seg in get_segments(filename))


def identify_channel(filename):
    """Return channel name, 'SKIP', or None if unrecognised."""
    if is_skip_file(filename):
        return "SKIP"
    segments = get_segments(filename)
    # Walk from the end — channel keyword is usually the last segment
    for seg in reversed(segments):
        for channel, keywords in CHANNEL_KEYWORDS.items():
            for kw in keywords:
                # exact match, or keyword + trailing digit (e.g. "rough2")
                if seg == kw or (seg.startswith(kw) and seg[len(kw):].isdigit()):
                    return channel
    return None


def detect_normal_type(filename):
    """Auto-detect DirectX or OpenGL from filename. Returns string or None."""
    segments = get_segments(filename)
    if "dx" in segments:
        return "DirectX"
    if "ogl" in segments or "opengl" in segments or "gl" in segments:
        return "OpenGL"
    return None


def next_set_number(folder):
    """Anchor to the highest BaseColor set number already in the folder."""
    highest = 0
    for fname in os.listdir(folder):
        m = re.match(r"^BaseColor_(\d+)_", fname)
        if m:
            highest = max(highest, int(m.group(1)))
    return highest + 1


# ── Interactive prompts ────────────────────────────────────────────────────────

def ask_channel(filename):
    options = list(CHANNEL_KEYWORDS.keys()) + ["SKIP"]
    print(f"\n  Cannot identify: {filename}")
    for i, ch in enumerate(options, 1):
        print(f"    {i}. {ch}")
    while True:
        val = input("  Assign to (enter number): ").strip()
        if val.isdigit() and 1 <= int(val) <= len(options):
            return options[int(val) - 1]
        print("  Please enter a number from the list.")


def ask_which_duplicate(channel, file_a, file_b):
    print(f"\n  Two files both match {channel}:")
    print(f"    1. {file_a}")
    print(f"    2. {file_b}")
    while True:
        val = input("  Which one to use? (1 or 2): ").strip()
        if val == "1":
            return file_a
        if val == "2":
            return file_b
        print("  Please enter 1 or 2.")


def ask_normal_type():
    print("\n  Could not detect normal map type from the filename.")
    print("  Which type is it?")
    print("    1. DirectX  (used by Unreal Engine — most UE packs are this)")
    print("    2. OpenGL   (used by Rhino and Blender)")
    while True:
        val = input("  Enter 1 or 2: ").strip()
        if val == "1":
            return "DirectX"
        if val == "2":
            return "OpenGL"
        print("  Please enter 1 or 2.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n-- PBR Ingest --------------------------------------------------")

    # Get source folder from argument or prompt
    if len(sys.argv) > 1:
        source_folder = sys.argv[1].strip().strip('"')
    else:
        source_folder = input("\nPath to PBR pack folder: ").strip().strip('"')

    if not os.path.isdir(source_folder):
        print(f"\nERROR: Folder not found:\n  {source_folder}")
        sys.exit(1)

    print(f"\nScanning: {source_folder}\n")

    image_files = sorted(
        f for f in os.listdir(source_folder)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        and not f.startswith(".")
    )

    if not image_files:
        print("No image files found in that folder.")
        sys.exit(1)

    # ── Identify channels ──────────────────────────────────────────────────────
    mapping = {}
    skipped = []
    unrecognised = []

    for fname in image_files:
        channel = identify_channel(fname)
        if channel == "SKIP":
            skipped.append(fname)
        elif channel is None:
            unrecognised.append(fname)
        elif channel in mapping:
            mapping[channel] = ask_which_duplicate(channel, mapping[channel], fname)
        else:
            mapping[channel] = fname

    # Ask the user to assign any files that couldn't be identified
    for fname in unrecognised:
        channel = ask_channel(fname)
        if channel == "SKIP":
            skipped.append(fname)
        elif channel in mapping:
            mapping[channel] = ask_which_duplicate(channel, mapping[channel], fname)
        else:
            mapping[channel] = fname

    # ── Normal map type ────────────────────────────────────────────────────────
    normal_type = None
    if "Normal" in mapping:
        normal_type = detect_normal_type(mapping["Normal"])

    # ── Show mapping table ─────────────────────────────────────────────────────
    print("\n" + "-" * 60)
    print("  Detected mapping")
    print("-" * 60)
    for ch in CHANNEL_KEYWORDS:
        if ch in mapping:
            note = f"  [{normal_type} detected]" if ch == "Normal" and normal_type else ""
            print(f"  {ch:<14}  ->  {mapping[ch]}{note}")
        else:
            print(f"  {ch:<14}  ->  (not found)")
    if skipped:
        print(f"\n  Skipped ({len(skipped)}):  {', '.join(skipped)}")
    print("-" * 60)

    # Ask for normal type if not detected from filename
    if "Normal" in mapping and normal_type is None:
        normal_type = ask_normal_type()

    # Warn if any channel is missing
    missing = [ch for ch in CHANNEL_KEYWORDS if ch not in mapping]
    if missing:
        print(f"\n  WARNING — these channels were not found: {', '.join(missing)}")
        if input("  Continue anyway? (y/n): ").strip().lower() != "y":
            print("  Cancelled.")
            sys.exit(0)

    # ── Confirm before copying ─────────────────────────────────────────────────
    set_num = next_set_number(TEXTURE_FOLDER)
    print(f"\n  This set will be saved as number {set_num:05d}")
    print(f"  Destination: {TEXTURE_FOLDER}")
    if input("\n  Type YES to copy the files: ").strip() != "YES":
        print("  Cancelled.")
        sys.exit(0)

    # ── Copy and rename ────────────────────────────────────────────────────────
    print()
    for channel, fname in mapping.items():
        ext = os.path.splitext(fname)[1]
        dst_name = f"{channel}_{set_num:05d}_{ext}"
        shutil.copy2(
            os.path.join(source_folder, fname),
            os.path.join(TEXTURE_FOLDER, dst_name)
        )
        print(f"  Copied:  {dst_name}")

    # Save a small note recording the normal map type and where the set came from
    info_path = os.path.join(TEXTURE_FOLDER, f"info_{set_num:05d}.txt")
    with open(info_path, "w") as f:
        f.write(f"Set: {set_num:05d}\n")
        f.write(f"Source: {source_folder}\n")
        if normal_type:
            f.write(f"Normal map type: {normal_type}\n")
    print(f"  Saved:   info_{set_num:05d}.txt")

    print(f"\nDone. Set {set_num:05d} is ready. It will appear in the picker for both Rhino and Unreal.\n")


if __name__ == "__main__":
    main()
