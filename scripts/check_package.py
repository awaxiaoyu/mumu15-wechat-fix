#!/usr/bin/env python3
"""Check the installable ZIP boundary and its architecture."""
import sys
import zipfile
from pathlib import Path

from build import check_elf

REQUIRED = {"module.prop", "customize.sh", "post-fs-data.sh", "uninstall.sh", "skip_mount",
            "zygisk/x86_64.so", "LICENSE", "THIRD_PARTY_NOTICES.md"}

with zipfile.ZipFile(Path(sys.argv[1])) as archive:
    if set(archive.namelist()) != REQUIRED:
        raise SystemExit(f"Unexpected module contents: {archive.namelist()}")
    check_elf(archive.read("zygisk/x86_64.so"))
    for name in ("customize.sh", "post-fs-data.sh", "uninstall.sh"):
        data = archive.read(name)
        if b"\r" in data or not data.startswith(b"#!/system/bin/sh\n"):
            raise SystemExit(f"Invalid Android shell script: {name}")
    if archive.testzip() is not None:
        raise SystemExit("Corrupt ZIP")
print("Package verified: x86_64 module, installer, licenses; no MuMu system library")
