#!/usr/bin/env python3

"""Create a numerically ordered contact sheet from rendered page PNGs."""

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw


for raw_dir in sys.argv[1:]:
    directory = Path(raw_dir)
    pages = sorted(
        directory.glob("page-*.png"),
        key=lambda path: int(re.search(r"(\d+)$", path.stem).group(1)),
    )
    if not pages:
        raise SystemExit(f"No rendered pages in {directory}")

    columns = 4
    thumb_width = 250
    label_height = 28
    with Image.open(pages[0]) as first:
        thumb_height = round(first.height * thumb_width / first.width)
    rows = (len(pages) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + label_height)), "white")
    draw = ImageDraw.Draw(sheet)

    for index, page in enumerate(pages):
        with Image.open(page) as source:
            image = source.convert("RGB")
            image.thumbnail((thumb_width, thumb_height))
        x = (index % columns) * thumb_width + (thumb_width - image.width) // 2
        y = (index // columns) * (thumb_height + label_height)
        sheet.paste(image, (x, y))
        draw.text((x + 6, y + thumb_height + 5), f"{directory.name}, page {index + 1}", fill="black")

    output = directory / "contact_sheet.png"
    sheet.save(output, optimize=True)
    print(output)
