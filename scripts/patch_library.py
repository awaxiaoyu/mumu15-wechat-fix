#!/usr/bin/env python3
"""Generate the verified one-byte patch without redistributing MuMu libraries."""
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA = "b0132bc4c7c6351d6daecae51c19fb779408f0e34432310f13c48cb75c034f4d"
PATCHED_SHA = "9b0d18c457cb6d874e6fc95871b8e2d5659809de8257e623861e52f9ddaeb29d"
OFFSET = 0x70B99C


def patch(source: Path, destination: Path) -> None:
    if source.resolve() == destination.resolve():
        raise ValueError("Input and output must be different files")
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA:
        raise ValueError("Unsupported MuMu translator SHA256")
    if original[OFFSET] != 0x5F:
        raise ValueError("Unexpected original byte")
    modified = bytearray(original)
    modified[OFFSET] = 0x58
    if hashlib.sha256(modified).hexdigest() != PATCHED_SHA:
        raise ValueError("Patched SHA256 mismatch")
    destination.write_bytes(modified)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        patch(args.source, args.destination)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(f"Generated {args.destination.name}: {PATCHED_SHA}")
