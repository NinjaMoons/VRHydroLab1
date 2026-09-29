#!/usr/bin/env python3

"""Set OpenFOAM boundary patch types by patch name, never by line number."""

import os
import re
import sys


EXPECTED = {
    "inlet": "patch",
    "outlet": "patch",
    "walls": "wall",
    "obstacles": "wall",
    "frontAndBack": "empty",
}


def replace_patch_type(text, patch_name, patch_type):
    pattern = re.compile(
        r"(?ms)^(\s*)" + re.escape(patch_name) + r"\s*\n\s*\{(?P<body>.*?)^\s*\}"
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError("patch not found: %s" % patch_name)
    body = match.group("body")
    changed, count = re.subn(
        r"(?m)^(\s*)type\s+[^;]+;",
        lambda found: "%stype            %s;" % (found.group(1), patch_type),
        body,
        count=1,
    )
    if count != 1:
        raise RuntimeError("type entry not found for patch: %s" % patch_name)
    start, end = match.span("body")
    return text[:start] + changed + text[end:]


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: set_patch_types.py constant/polyMesh/boundary")
    path = argv[1]
    with open(path, "r", encoding="utf-8") as stream:
        text = stream.read()
    for name, patch_type in EXPECTED.items():
        text = replace_patch_type(text, name, patch_type)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as stream:
        stream.write(text)
    os.replace(temporary, path)
    print("PATCH_TYPES_OK")
    for name, patch_type in EXPECTED.items():
        print("%s=%s" % (name, patch_type))


if __name__ == "__main__":
    main(sys.argv)
