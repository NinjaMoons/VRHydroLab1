#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "screenshots"


def open_rgb(name):
    return Image.open(SRC / name).convert("RGB")


def save_crop(source, target, bottom):
    image = open_rgb(source)
    crop = image.crop((0, 0, image.width, min(bottom, image.height)))
    crop.save(SRC / target, "PNG", optimize=True)


def compact_paraview(source, target, plot_box, scale_box, canvas_size, plot_target, scale_target):
    """Recompose existing plot and scalar bar without altering their contents."""
    image = open_rgb(source)
    plot = image.crop(plot_box)
    scale = image.crop(scale_box)
    plot.thumbnail((plot_target[2], plot_target[3]), Image.Resampling.LANCZOS)
    scale.thumbnail((scale_target[2], scale_target[3]), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", canvas_size, "white")
    canvas.paste(plot, (plot_target[0], plot_target[1]))
    canvas.paste(scale, (scale_target[0], scale_target[1]))
    canvas.save(SRC / target, "PNG", optimize=True)


save_crop("app_default_acceptance.jpg", "app_default_report.png", 1580)
save_crop("app_changed_acceptance.jpg", "app_changed_report.png", 1580)
save_crop("app_running_acceptance.jpg", "app_running_report.png", 1680)

source = open_rgb("app_complete_u0p15_acceptance.jpg")
top = source.crop((0, 0, source.width, 1260))
bottom = source.crop((0, 1210, source.width, source.height))
target_height = max(top.height, bottom.height)


def pad(image, height):
    canvas = Image.new("RGB", (image.width, height), "white")
    canvas.paste(image, (0, 0))
    return canvas


gap = 34
header = 66
top = pad(top, target_height)
bottom = pad(bottom, target_height)
canvas = Image.new("RGB", (top.width + bottom.width + gap, target_height + header), "white")
canvas.paste(top, (0, header))
canvas.paste(bottom, (top.width + gap, header))
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
draw.text((top.width / 2, 30), "Входные параметры Uin = 0,15 м/с", font=font,
          fill="#12343b", anchor="mm")
draw.text((top.width + gap + bottom.width / 2, 30), "Завершение и сохранённые результаты", font=font,
          fill="#12343b", anchor="mm")
draw.rectangle((top.width + gap // 2 - 1, 0, top.width + gap // 2 + 1, canvas.height),
               fill="#9fb3b8")
canvas.save(SRC / "app_complete_u0p15_report.png", "PNG", optimize=True)

mesh = open_rgb("openfoam_mesh.png").crop((475, 250, 1125, 350))
mesh = mesh.resize((1300, 200), Image.Resampling.LANCZOS)
mesh_canvas = Image.new("RGB", (1380, 260), "white")
mesh_canvas.paste(mesh, (40, 30))
mesh_canvas.save(SRC / "openfoam_mesh_report.png", "PNG", optimize=True)

compact_paraview(
    "velocity.png", "velocity_report.png",
    (470, 245, 1140, 360), (1460, 0, 1600, 235),
    (1380, 320), (35, 80, 1160, 200), (1220, 25, 135, 250),
)
compact_paraview(
    "pressure.png", "pressure_report.png",
    (470, 245, 1140, 360), (1460, 0, 1600, 235),
    (1380, 320), (35, 80, 1160, 200), (1220, 25, 135, 250),
)
compact_paraview(
    "streamlines.png", "streamlines_report.png",
    (45, 190, 1545, 390), (1460, 0, 1600, 235),
    (1500, 300), (25, 80, 1280, 190), (1340, 15, 135, 250),
)
compact_paraview(
    "obstacles_zoom.png", "obstacles_zoom_report.png",
    (0, 190, 1460, 590), (1460, 0, 1600, 235),
    (1500, 470), (20, 75, 1300, 380), (1340, 15, 135, 250),
)

for name in (
    "app_default_report.png",
    "app_changed_report.png",
    "app_running_report.png",
    "app_complete_u0p15_report.png",
    "openfoam_mesh_report.png",
    "velocity_report.png",
    "pressure_report.png",
    "streamlines_report.png",
    "obstacles_zoom_report.png",
):
    image = Image.open(SRC / name)
    print(name, image.size)
