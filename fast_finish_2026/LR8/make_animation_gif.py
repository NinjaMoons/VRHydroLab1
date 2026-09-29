#!/usr/bin/env python3

"""Combine LR8 ParaView frames into a looping GIF."""

import glob
import os
import sys

from PIL import Image

frame_dir = os.path.abspath(sys.argv[1])
output_file = os.path.abspath(sys.argv[2])
paths = sorted(glob.glob(os.path.join(frame_dir, "frame_*.png")))
if not paths:
    raise RuntimeError("No animation frames")

frames = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in paths]
frames[0].save(output_file, save_all=True, append_images=frames[1:], duration=180,
               loop=0, optimize=True)
print("LR8_ANIMATION_GIF_OK")
print("frames=", len(frames))
print("output=", output_file)

