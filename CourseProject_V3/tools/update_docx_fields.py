#!/usr/bin/env python3
"""Update document indexes and fields through a private LibreOffice instance."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue


def prop(name, value):
    item = PropertyValue()
    item.Name = name
    item.Value = value
    return item


def update(path: Path):
    profile = tempfile.mkdtemp(prefix="cpv3_soffice_")
    xdg_config = tempfile.mkdtemp(prefix="cpv3_xdg_config_")
    xdg_runtime = tempfile.mkdtemp(prefix="cpv3_xdg_runtime_")
    os.chmod(xdg_runtime, 0o700)
    environment = os.environ.copy()
    environment["XDG_CONFIG_HOME"] = xdg_config
    environment["XDG_RUNTIME_DIR"] = xdg_runtime
    pipe_name = f"cpv3_{os.getpid()}"
    process = subprocess.Popen(
        [
            "/home/pavel/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice",
            f"-env:UserInstallation=file://{profile}",
            "--headless",
            "--nologo",
            "--nodefault",
            "--nofirststartwizard",
            "--norestore",
            f"--accept=pipe,name={pipe_name};urp;StarOffice.ComponentContext",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    try:
        local = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local
        )
        context = None
        for _ in range(80):
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise RuntimeError(
                    f"LibreOffice listener exited with {process.returncode}: {stdout}{stderr}"
                )
            try:
                context = resolver.resolve(
                    f"uno:pipe,name={pipe_name};urp;StarOffice.ComponentContext"
                )
                break
            except Exception:
                time.sleep(0.1)
        if context is None:
            raise RuntimeError("LibreOffice UNO connection was not established")

        desktop = context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", context
        )
        document = desktop.loadComponentFromURL(
            uno.systemPathToFileUrl(str(path.resolve())),
            "_blank",
            0,
            (prop("Hidden", True), prop("ReadOnly", False)),
        )
        indexes = document.getDocumentIndexes()
        print(f"indexes={indexes.getCount()}")
        for number in range(indexes.getCount()):
            indexes.getByIndex(number).update()
        document.calculateAll()
        document.store()
        document.close(True)
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    update(args.document)


if __name__ == "__main__":
    main()
