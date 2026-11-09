#!/usr/bin/env python3
"""Build the x86_64 Zygisk module with the Android NDK and package a module ZIP."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def check_elf(binary: bytes) -> None:
    if binary[:6] != b"\x7fELF\x02\x01" or struct.unpack_from("<H", binary, 18)[0] != 62:
        raise ValueError("Expected an x86_64 ELF64 little-endian shared library")


def package(library: Path) -> Path:
    binary = library.read_bytes()
    check_elf(binary)
    properties = dict(line.split("=", 1) for line in (ROOT / "module/module.prop").read_text().splitlines() if "=" in line)
    output = ROOT / "dist" / f"mumu15-wechat-fix-{properties['version']}.zip"
    output.parent.mkdir(exist_ok=True)
    files = {path.relative_to(ROOT / "module").as_posix(): path.read_bytes() for path in (ROOT / "module").rglob("*") if path.is_file()}
    files["zygisk/x86_64.so"] = binary
    files["LICENSE"] = (ROOT / "LICENSE").read_bytes()
    files["THIRD_PARTY_NOTICES.md"] = (ROOT / "THIRD_PARTY_NOTICES.md").read_bytes()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 11, 10, 0, 0, 0))
            entry.create_system = 3
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            archive.writestr(entry, data)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    print(output)
    print(digest)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ndk", type=Path, default=os.environ.get("ANDROID_NDK_HOME"))
    parser.add_argument("--library", type=Path, help="Package an already-built x86_64 module")
    args = parser.parse_args()
    if args.library:
        package(args.library)
        return
    if not args.ndk:
        parser.error("Set ANDROID_NDK_HOME or pass --ndk")
    toolchain = args.ndk.resolve() / "build/cmake/android.toolchain.cmake"
    if not toolchain.is_file():
        parser.error("Android NDK toolchain not found")
    build_dir = ROOT / "build"
    configure = ["cmake", "-S", str(ROOT), "-B", str(build_dir),
                 f"-DCMAKE_TOOLCHAIN_FILE={toolchain}", "-DANDROID_ABI=x86_64",
                 "-DANDROID_PLATFORM=android-26", "-DANDROID_STL=none", "-DCMAKE_BUILD_TYPE=Release"]
    if os.name == "nt":
        if not shutil.which("ninja"):
            parser.error("On Windows, install Ninja and add it to PATH")
        configure += ["-G", "Ninja"]
    subprocess.run(configure, check=True)
    subprocess.run(["cmake", "--build", str(build_dir), "--parallel"], check=True)
    package(build_dir / "libwechat_media_fix.so")


if __name__ == "__main__":
    main()
