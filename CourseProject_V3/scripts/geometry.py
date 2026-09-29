#!/usr/bin/env python3

"""Shared parameter validation and derived values for Course Project V3."""

import json
import math
import os
import sys


REQUIRED_GEOMETRY = ("L", "H", "a", "P", "S", "Y", "R")


class GeometryValidationError(ValueError):
    """Raised when a parameter set cannot define a valid fluid domain."""


def load_settings(path):
    with open(path, "r", encoding="utf-8") as stream:
        return json.load(stream)


def obstacle_centres(geometry):
    """Return named obstacle centres computed only from L, R, P, S and Y."""
    L = float(geometry["L"])
    H = float(geometry["H"])
    P = float(geometry["P"])
    S = float(geometry["S"])
    R = float(geometry["R"])
    Y = float(geometry["Y"])
    last_upper = L - R
    upper_x = [last_upper - multiplier * P for multiplier in (3, 2, 1, 0)]
    lower_x = [value + S for value in upper_x[:3]]
    centres = []
    for index, x_value in enumerate(upper_x, 1):
        centres.append({"name": "upper%d" % index, "x": x_value, "y": H - Y})
    for index, x_value in enumerate(lower_x, 1):
        centres.append({"name": "lower%d" % index, "x": x_value, "y": Y})
    return centres


def validate_settings(settings):
    errors = []
    geometry = settings.get("geometryMm", {})
    flow = settings.get("flow", {})
    mesh = settings.get("mesh", {})

    for key in REQUIRED_GEOMETRY:
        try:
            value = float(geometry[key])
        except (KeyError, TypeError, ValueError):
            errors.append("geometryMm.%s must be a finite number" % key)
            continue
        if not math.isfinite(value) or value <= 0:
            errors.append("geometryMm.%s must be > 0" % key)

    try:
        Uin = float(flow["Uin"])
        if not math.isfinite(Uin) or Uin <= 0:
            errors.append("flow.Uin must be > 0")
    except (KeyError, TypeError, ValueError):
        errors.append("flow.Uin must be a finite number")

    for path, value in (
        ("flow.nu", flow.get("nu")),
        ("flow.rho", flow.get("rho")),
        ("mesh.maxSizeMm", mesh.get("maxSizeMm")),
        ("mesh.minSizeMm", mesh.get("minSizeMm")),
        ("mesh.obstacleSizeMm", mesh.get("obstacleSizeMm")),
    ):
        try:
            numeric = float(value)
            if not math.isfinite(numeric) or numeric <= 0:
                errors.append("%s must be > 0" % path)
        except (TypeError, ValueError):
            errors.append("%s must be a finite number" % path)

    try:
        thickness = float(mesh.get("thicknessMm"))
        if abs(thickness - 1.0) > 1.0e-12:
            errors.append("mesh.thicknessMm is technological and must remain 1.0 mm")
    except (TypeError, ValueError):
        errors.append("mesh.thicknessMm must be 1.0 mm")

    if errors:
        raise GeometryValidationError("; ".join(errors))

    L = float(geometry["L"])
    H = float(geometry["H"])
    a = float(geometry["a"])
    P = float(geometry["P"])
    S = float(geometry["S"])
    Y = float(geometry["Y"])

    checks = (
        (S >= a, "S must be >= a because staggered rows overlap vertically"),
        (P - S >= a, "P - S must be >= a because staggered rows overlap vertically"),
        (P >= a, "P must be >= a"),
        (Y - a / 2.0 > 0, "lower obstacles must not touch the lower wall"),
        (H - Y - a / 2.0 > 0, "upper obstacles must not touch the upper wall"),
    )
    errors.extend(message for condition, message in checks if not condition)

    centres = obstacle_centres(geometry)
    for obstacle in centres:
        if obstacle["x"] - a / 2.0 <= 0:
            errors.append("%s crosses or touches inlet" % obstacle["name"])
        if obstacle["x"] + a / 2.0 >= L:
            errors.append("%s crosses or touches outlet" % obstacle["name"])

    for first_index, first in enumerate(centres):
        for second in centres[first_index + 1:]:
            overlap_x = abs(first["x"] - second["x"]) < a
            overlap_y = abs(first["y"] - second["y"]) < a
            if overlap_x and overlap_y:
                errors.append("%s intersects %s" % (first["name"], second["name"]))

    if errors:
        raise GeometryValidationError("; ".join(errors))
    return centres


def derived_values(settings):
    centres = validate_settings(settings)
    geometry = settings["geometryMm"]
    flow = settings["flow"]
    Uin = float(flow["Uin"])
    nu = float(flow["nu"])
    a_m = float(geometry["a"]) * 1.0e-3
    H_m = float(geometry["H"]) * 1.0e-3
    Re_a = Uin * a_m / nu
    Re_H = Uin * H_m / nu

    # Engineering inlet estimate: I=0.16*Re_H^(-1/8), l=0.07*H.
    intensity = 0.16 * Re_H ** (-1.0 / 8.0)
    length_scale = 0.07 * H_m
    Cmu = 0.09
    k_value = 1.5 * (Uin * intensity) ** 2
    omega_value = math.sqrt(k_value) / (Cmu ** 0.25 * length_scale)
    return {
        "obstacles": centres,
        "Re_a": Re_a,
        "Re_H": Re_H,
        "turbulenceIntensity": intensity,
        "turbulenceLengthScaleM": length_scale,
        "kInlet": k_value,
        "omegaInlet": omega_value,
    }


def main(argv):
    default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
    path = argv[1] if len(argv) > 1 else default_path
    settings = load_settings(path)
    values = derived_values(settings)
    print(json.dumps(values, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
