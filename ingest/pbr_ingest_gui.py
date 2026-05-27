# -*- coding: utf-8 -*-
"""
PBR Ingest GUI
--------------
Browse to an external PBR pack folder, confirm the channel mapping,
and click Import — the files are copied and renamed into PBR_Textures
so they appear in both the Rhino and Unreal pickers.

Launch with: run_pbr_ingest.bat  (double-click)
"""

import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ── Constants ──────────────────────────────────────────────────────────────────

CHANNEL_KEYWORDS = {
    "BaseColor":    ["basecolor", "albedo", "alb", "diffuse", "color", "colour", "col"],
    "Normal":       ["normal", "nrm", "nor", "nml"],
    "Roughness":    ["roughness", "rough", "rgh"],
    "Metalness":    ["metallic", "metalness", "metal", "met"],
    "Displacement": ["displacement", "disp", "height", "depth"],
}

SKIP_WORDS   = {"preview", "ao", "occlusion", "ambient", "thumbnail", "thumb"}
IMAGE_EXTS   = {".png", ".jpg", ".jpeg", ".tga", ".exr", ".tiff", ".tif"}
NOT_FOUND    = "(not found)"

# Output folder = same folder this script lives in (PBR_Textures)
TEXTURE_FOLDER = os.path.dirname(os.path.abspath(__file__))


# ── Detection helpers ──────────────────────────────────────────────────────────

def get_segments(filename):
    """Split filename into lowercase parts on - _ . and spaces."""
    name = os.path.splitext(filename)[0].lower()
    return re.split(r"[-_.\s]", name)


def is_skip_file(filename):
    return any(seg in SKIP_WORDS for seg in get_segments(filename))


def identify_channel(filename):
    """Return channel name or None."""
    if is_skip_file(filename):
        return None
    segments = get_segments(filename)
    # Walk from end — channel keyword is usually the last segment
    for seg in reversed(segments):
        for channel, keywords in CHANNEL_KEYWORDS.items():
            for kw in keywords:
                if seg == kw or (seg.startswith(kw) and seg[len(kw):].isdigit()):
                    return channel
    return None


def detect_normal_type(filename):
    """Try to detect DirectX or OpenGL from filename. Returns string or None."""
    segs = get_segments(filename)
    if "dx" in segs:
        return "DirectX"
    if any(s in segs for s in ("ogl", "opengl", "gl")):
        return "OpenGL"
    return None


def next_set_number(folder):
    """Find the next unused 5-digit set number."""
    existing = set()
    for fname in os.listdir(folder):
        parts = fname.split("_")
        if len(parts) >= 2 and parts[1].isdigit():
            existing.add(int(parts[1]))
    return max(existing, default=0) + 1


# ── GUI ────────────────────────────────────────────────────────────────────────

class PBRIngestApp:

    def __init__(self, root):
        self.root = root
        self.root.title("PBR Ingest")
        self.root.resizable(False, False)

        self.source_folder  = tk.StringVar()
        self.normal_type    = tk.StringVar(value="DirectX")
        self.channel_vars   = {}   # channel name  ->  StringVar (selected filename)
        self.dropdown_menus = {}   # channel name  ->  OptionMenu widget

        self._build_ui()

    # ── Layout ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        PX = 14   # horizontal padding for outer frames

        # ── Folder picker ──────────────────────────────────────────────────────
        row = tk.Frame(self.root)
        row.pack(fill=tk.X, padx=PX, pady=(14, 6))

        tk.Label(row, text="Source folder:", width=14, anchor="w").pack(side=tk.LEFT)

        tk.Entry(row, textvariable=self.source_folder,
                 state="readonly", relief=tk.SUNKEN,
                 bg="#f4f4f4", width=40).pack(side=tk.LEFT, padx=(4, 8), fill=tk.X, expand=True)

        tk.Button(row, text="Browse…", width=9,
                  command=self._browse).pack(side=tk.LEFT)

        # ── Channel mapping table ──────────────────────────────────────────────
        map_frame = tk.LabelFrame(self.root, text="  Channel Mapping  ", padx=12, pady=8)
        map_frame.pack(fill=tk.X, padx=PX, pady=4)

        for i, channel in enumerate(CHANNEL_KEYWORDS):
            var = tk.StringVar(value=NOT_FOUND)
            self.channel_vars[channel] = var

            tk.Label(map_frame, text=channel, width=13, anchor="w").grid(
                row=i, column=0, sticky="w", pady=3)
            tk.Label(map_frame, text="→", fg="#999").grid(
                row=i, column=1, padx=(6, 10))

            menu = tk.OptionMenu(map_frame, var, NOT_FOUND)
            menu.config(width=40, anchor="w", relief=tk.GROOVE)
            menu.grid(row=i, column=2, sticky="w", pady=3)

            self.dropdown_menus[channel] = menu

        # ── Normal map type ────────────────────────────────────────────────────
        nrm_frame = tk.LabelFrame(self.root, text="  Normal Map Type  ", padx=12, pady=8)
        nrm_frame.pack(fill=tk.X, padx=PX, pady=4)

        tk.Radiobutton(nrm_frame,
                       text="DirectX   (Unreal Engine — most downloaded packs)",
                       variable=self.normal_type, value="DirectX").pack(anchor="w")
        tk.Radiobutton(nrm_frame,
                       text="OpenGL    (Rhino / Blender)",
                       variable=self.normal_type, value="OpenGL").pack(anchor="w")

        # ── Import button ──────────────────────────────────────────────────────
        ttk.Separator(self.root, orient="horizontal").pack(
            fill=tk.X, padx=PX, pady=(8, 0))

        btn_row = tk.Frame(self.root)
        btn_row.pack(pady=10)

        tk.Button(
            btn_row, text="  Import  ",
            command=self._do_import,
            bg="#2a7ae2", fg="white",
            activebackground="#1a5ec0", activeforeground="white",
            font=("TkDefaultFont", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=12, pady=5
        ).pack()

        # ── Status label ───────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Browse to a PBR pack folder to begin.")
        tk.Label(self.root, textvariable=self.status_var,
                 fg="#666", anchor="w",
                 font=("TkDefaultFont", 8)).pack(
            fill=tk.X, padx=PX, pady=(0, 8))

    # ── Browsing + scanning ─────────────────────────────────────────────────────

    def _browse(self):
        folder = filedialog.askdirectory(title="Select PBR Pack Folder")
        if folder:
            self.source_folder.set(folder)
            self._scan_folder(folder)

    def _scan_folder(self, folder):
        image_files = sorted(
            f for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS
            and not f.startswith(".")
        )

        if not image_files:
            self.status_var.set("No image files found in that folder.")
            return

        # Auto-detect channels — first match per channel wins
        auto_map = {}
        for fname in image_files:
            if is_skip_file(fname):
                continue
            ch = identify_channel(fname)
            if ch and ch not in auto_map:
                auto_map[ch] = fname

        # Auto-detect normal map type
        if "Normal" in auto_map:
            detected = detect_normal_type(auto_map["Normal"])
            if detected:
                self.normal_type.set(detected)

        # Rebuild all dropdown menus with the new file list
        options = [NOT_FOUND] + image_files
        for channel, menu in self.dropdown_menus.items():
            menu["menu"].delete(0, "end")
            var = self.channel_vars[channel]
            for opt in options:
                menu["menu"].add_command(
                    label=opt,
                    command=lambda v=var, o=opt: v.set(o)
                )
            var.set(auto_map.get(channel, NOT_FOUND))

        n_found   = sum(1 for ch in CHANNEL_KEYWORDS if ch in auto_map)
        n_skipped = sum(1 for f in image_files if is_skip_file(f))
        msg = f"{len(image_files)} image(s) found  —  {n_found} of 5 channels detected."
        if n_skipped:
            msg += f"  ({n_skipped} skipped)"
        msg += "  Check the mapping, then click Import."
        self.status_var.set(msg)

    # ── Import ──────────────────────────────────────────────────────────────────

    def _do_import(self):
        folder = self.source_folder.get()
        if not folder:
            messagebox.showwarning("No folder selected",
                                   "Please browse to a PBR pack folder first.")
            return

        mapping = {
            ch: var.get()
            for ch, var in self.channel_vars.items()
            if var.get() != NOT_FOUND
        }

        if not mapping:
            messagebox.showwarning("Nothing to import",
                                   "No channels are assigned.\n"
                                   "Please select files from the dropdowns.")
            return

        missing = [ch for ch in CHANNEL_KEYWORDS if ch not in mapping]
        if missing:
            if not messagebox.askyesno(
                "Missing channels",
                f"These channels are not assigned:\n\n"
                f"  {', '.join(missing)}\n\n"
                f"Continue anyway?"
            ):
                return

        set_num = next_set_number(TEXTURE_FOLDER)

        # Confirmation summary
        lines = [
            f"Set number:    {set_num:05d}",
            f"Normal type:   {self.normal_type.get()}",
            f"Destination:   {TEXTURE_FOLDER}",
            "",
            "Files to copy:",
        ]
        for ch, fname in mapping.items():
            lines.append(f"  {ch:<14}  ←  {fname}")

        if not messagebox.askyesno("Confirm Import", "\n".join(lines)):
            return

        # Copy and rename
        try:
            for channel, fname in mapping.items():
                ext = os.path.splitext(fname)[1]
                dst_name = f"{channel}_{set_num:05d}_{ext}"
                shutil.copy2(
                    os.path.join(folder, fname),
                    os.path.join(TEXTURE_FOLDER, dst_name)
                )

            # Save info file
            with open(os.path.join(TEXTURE_FOLDER, f"info_{set_num:05d}.txt"), "w") as fh:
                fh.write(f"Set: {set_num:05d}\n")
                fh.write(f"Source: {folder}\n")
                fh.write(f"Normal map type: {self.normal_type.get()}\n")

            self.status_var.set(
                f"Done! Set {set_num:05d} added. "
                f"It will now appear in the Rhino and Unreal pickers.")
            messagebox.showinfo(
                "Import complete",
                f"Set {set_num:05d} is ready.\n\n"
                f"It will now appear in the picker\n"
                f"for both Rhino and Unreal.")

            # Reset for next use
            self.source_folder.set("")
            for var in self.channel_vars.values():
                var.set(NOT_FOUND)

        except Exception as exc:
            messagebox.showerror("Import failed",
                                 f"Something went wrong:\n\n{exc}")
            self.status_var.set("Error — see the message for details.")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    app = PBRIngestApp(root)
    root.after(200, lambda: root.attributes("-topmost", False))
    root.mainloop()
