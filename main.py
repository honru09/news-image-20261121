#!/usr/bin/env python3
"""Copy the pre-rendered front-page news infographic to MAKEFUN_OUTPUT_DIR."""

import hashlib
import os
import shutil
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_image = os.path.join(base_dir, "entry.png")

    if not os.path.isfile(source_image):
        sys.stderr.write(f"Error: missing source image at {source_image}\n")
        return 1

    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output").strip() or "output"
    os.makedirs(target_dir, exist_ok=True)

    destination_image = os.path.join(target_dir, "entry.png")
    shutil.copyfile(source_image, destination_image)

    with open(destination_image, "rb") as fh:
        magic = fh.read(8)

    if magic != PNG_SIGNATURE:
        expected_hex = " ".join(f"{b:02X}" for b in PNG_SIGNATURE)
        actual_hex = " ".join(f"{b:02X}" for b in magic)
        sys.stderr.write(
            f"Error: {destination_image} failed PNG magic bytes check "
            f"(expected {expected_hex}, got {actual_hex})\n"
        )
        return 1

    if sha256_file(source_image) != sha256_file(destination_image):
        sys.stderr.write(
            f"Error: SHA-256 mismatch after copying to {destination_image}\n"
        )
        return 1

    os.chmod(destination_image, 0o644)
    size_bytes = os.path.getsize(destination_image)
    print(f"{destination_image} ({size_bytes} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
