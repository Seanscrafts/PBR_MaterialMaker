from pathlib import Path
import json
import os
import shutil
import sys


REPO_DIR = Path(__file__).parent
CONFIG_PATH = REPO_DIR / "config.json"
RHINO_IMPORT_SCRIPT = REPO_DIR / "rhino_import.py"

RHINO_SCRIPTS_DIR = Path(os.environ["APPDATA"]) / "McNeel" / "Rhinoceros" / "8.0" / "scripts"


def ask_texture_output_folder():
    default = r"C:\AI\PBR_Textures"
    answer = input(f"Enter the full path where ComfyUI saves textures (press Enter for default: {default}): ").strip().strip('"')
    texture_path = Path(answer) if answer else Path(default)

    if not texture_path.exists():
        confirm = input(f"Folder does not exist: {texture_path}\nCreate it? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("ERROR: Texture output folder does not exist.")
            sys.exit(1)
        texture_path.mkdir(parents=True, exist_ok=True)
        print(f"Created: {texture_path}")

    return texture_path


def write_config(texture_output_folder):
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = json.load(f)

    config["texture_output_folder"] = str(texture_output_folder)

    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print(f"config.json updated with texture folder: {texture_output_folder}")


def copy_files_to_rhino():
    RHINO_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    if not RHINO_IMPORT_SCRIPT.exists():
        print(f"WARNING: rhino_import.py not found yet — skipping copy to Rhino scripts folder.")
        print(f"         Run install.py again once rhino_import.py has been created.")
        return

    shutil.copy2(RHINO_IMPORT_SCRIPT, RHINO_SCRIPTS_DIR / "rhino_import.py")
    shutil.copy2(CONFIG_PATH, RHINO_SCRIPTS_DIR / "pbr_config.json")
    print(f"Scripts copied to: {RHINO_SCRIPTS_DIR}")


def main():
    print("=== PBR to Rhino 8 — Installer ===\n")

    texture_output_folder = ask_texture_output_folder()
    write_config(texture_output_folder)
    copy_files_to_rhino()

    print("""
Install complete.

Next steps:
1. Open Rhino 8.
2. Type: RunPythonScript
3. Browse to and select the rhino_import.py file that was copied to:
""" + f"   {RHINO_SCRIPTS_DIR}" + """

Or create a toolbar button in Rhino with this command:
   _-RunPythonScript "rhino_import.py"
""")


if __name__ == "__main__":
    main()
