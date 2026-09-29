#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1] / "screenshots" / "architecture.png"
W, H = 1800, 850
img = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(img)


def font(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)


TITLE = font(42, True)
BODY = font(26)
SMALL = font(21)
BOX_TITLE = font(28, True)


def box(x, y, w, h, title, lines, fill, stroke="#164e63"):
    draw.rounded_rectangle((x, y, x + w, y + h), 22, fill=fill, outline=stroke, width=4)
    draw.text((x + 24, y + 20), title, font=BOX_TITLE, fill="#102a43")
    yy = y + 70
    for line in lines:
        draw.text((x + 24, yy), line, font=SMALL, fill="#243b53")
        yy += 32


def arrow(x1, y1, x2, y2, label=""):
    draw.line((x1, y1, x2, y2), fill="#0f766e", width=6)
    angle = 18
    draw.polygon([(x2, y2), (x2 - angle, y2 - 11), (x2 - angle, y2 + 11)], fill="#0f766e")
    if label:
        tw = draw.textbbox((0, 0), label, font=SMALL)[2]
        draw.text(((x1 + x2 - tw) / 2, y1 - 34), label, font=SMALL, fill="#0f4c5c")


draw.text((W / 2, 35), "Фактическая архитектура CourseProject_V3", font=TITLE, anchor="ma", fill="#102a43")

box(45, 150, 300, 210, "Web UI", ["HTML / CSS / JS", "форма и SVG", "status / results"], "#e6fffa")
box(435, 150, 330, 210, "Node.js server", ["HTTP API", "validation", "spawn + run lock"], "#ecfeff")
box(855, 150, 350, 210, "Python pipeline", ["run_pipeline.py", "последовательные стадии", "контроль return code"], "#eff6ff")

arrow(345, 255, 435, 255)
arrow(765, 255, 855, 255)

box(140, 515, 310, 205, "SALOME 9.16", ["GEOM + SMESH", "HDF + UNV", "mesh_summary.json"], "#fef3c7", "#92400e")
box(560, 515, 310, 205, "OpenFOAM 13", ["import + checkMesh", "SIMPLE → PIMPLE", "foamPostProcess"], "#fee2e2", "#991b1b")
box(980, 515, 310, 205, "ParaView 6.1", ["pvpython", "5 PNG", "point ranges"], "#ede9fe", "#5b21b6")
box(1400, 515, 340, 205, "Persistent run", ["case / logs", "HDF / UNV / PNG", "status + summary"], "#dcfce7", "#166534")

draw.line((1030, 360, 1030, 445), fill="#0f766e", width=6)
draw.line((295, 445, 1570, 445), fill="#0f766e", width=6)
for cx in (295, 715, 1135, 1570):
    draw.line((cx, 445, cx, 515), fill="#0f766e", width=6)
    draw.polygon([(cx, 515), (cx - 11, 497), (cx + 11, 497)], fill="#0f766e")
draw.text((1030, 405), "управление этапами", font=SMALL, anchor="mm", fill="#0f4c5c")

draw.text((W / 2, 790), "Единый settings.json проходит через весь конвейер; каждый запуск сохраняется в отдельном runs/<id>.", font=BODY, anchor="mm", fill="#334e68")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, format="PNG", optimize=True)
print(OUT)
