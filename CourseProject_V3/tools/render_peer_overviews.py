#!/usr/bin/env python3
"""Render four representative pages per peer into compact review sheets."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def select_pages(item):
    headings = item["headings"]
    pages = [1]
    for pattern in (r"СОДЕРЖАНИЕ", r"РАЗРАБОТК.*ПРИЛОЖ|СОЗДАНИ.*ПРИЛОЖ|ПРОЕКТИРОВАНИ.*ПРИЛОЖ", r"СРАВНЕНИ|АНАЛИЗ.*РЕЗУЛЬТ|РЕЗУЛЬТАТ.*РАСЧ"):
        found = next((page for page, title in headings if re.search(pattern, title, re.I)), None)
        if found and found not in pages:
            pages.append(found)
    for fallback in (5, max(1, item["pages"] // 2), max(1, item["pages"] - 2)):
        if len(pages) >= 4:
            break
        if fallback not in pages:
            pages.append(fallback)
    return pages[:4]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("representatives", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    reports = json.loads(args.representatives.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="cpv3_peer_render_"))
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    thumb_w, thumb_h = 300, 424
    gap, label_h = 18, 70
    rendered = []
    for report_index, item in enumerate(reports):
        page_images = []
        for page in select_pages(item):
            prefix = work / f"r{report_index:02d}_p{page:03d}"
            subprocess.run([
                "pdftoppm", "-f", str(page), "-l", str(page), "-singlefile",
                "-jpeg", "-r", "60", item["path"], str(prefix)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            page_images.append((page, Image.open(prefix.with_suffix(".jpg")).convert("RGB")))
        rendered.append((item, page_images))

    for batch in range(0, len(rendered), 2):
        pair = rendered[batch:batch + 2]
        canvas = Image.new("RGB", (4 * (thumb_w + gap) + gap, 2 * (thumb_h + label_h + gap) + gap), "#d0d0d0")
        draw = ImageDraw.Draw(canvas)
        for row, (item, images) in enumerate(pair):
            base_y = gap + row * (thumb_h + label_h + gap)
            draw.text((gap, base_y), item["student_folder"], fill="black", font=font_bold)
            for col, (page, source) in enumerate(images):
                source.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                x = gap + col * (thumb_w + gap) + (thumb_w - source.width) // 2
                y = base_y + label_h + (thumb_h - source.height) // 2
                canvas.paste(source, (x, y))
                draw.text((gap + col * (thumb_w + gap), base_y + 32), f"стр. {page}", fill="black", font=font)
        target = args.output_dir / f"peer_{batch + 1:02d}_{min(batch + 2, len(rendered)):02d}.jpg"
        canvas.save(target, quality=90)
        print(target)


if __name__ == "__main__":
    main()
