#!/usr/bin/env python3
"""Simplest release means: pack an explicit allowlist into a versioned zip + sha256.

Stdlib only.  Only published files are included (glyphs SVGs, the two CSVs,
manifest.json, README.md, SPEC.md, LICENSES.md, the scripts, and the self-contained
viewer); everything else (.git, hidden files, logs, temp files, archives) is excluded
by construction.  Reads version from manifest.json, writes the archive to the PARENT
directory with a fixed timestamp and sorted entries so the same inputs reproduce
the same bytes.

    python scripts/make_release.py
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT_FILES = ["glyphs.csv", "quality.csv", "manifest.json", "README.md", "SPEC.md", "LICENSES.md"]
SCRIPT_FILES = ["scripts/validate_core.py", "scripts/make_release.py", "scripts/build_viewer.py"]


def main() -> int:
    manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
    name = manifest["name"]
    version = manifest["version"]
    y, m, d = (int(x) for x in manifest["generated"].split("-"))
    stamp = (y, m, d, 0, 0, 0)
    prefix = f"{name}-{version}"

    files = [BASE / f for f in ROOT_FILES + SCRIPT_FILES]
    files += sorted((BASE / "glyphs").glob("*/*.svg"))
    files.append(BASE / "viewer" / "index.html")
    files += sorted((BASE / "viewer" / "data").glob("*.json"))
    for p in files:
        if not p.is_file():
            raise SystemExit(f"missing publishable file: {p}")
    files = sorted(files, key=lambda p: p.relative_to(BASE).as_posix())

    out_dir = BASE.parent
    archive = out_dir / f"{prefix}.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for p in files:
            rel = p.relative_to(BASE).as_posix()
            zi = zipfile.ZipInfo(f"{prefix}/{rel}", date_time=stamp)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zi, p.read_bytes())

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sidecar = out_dir / f"{prefix}.zip.sha256"
    sidecar.write_bytes(f"{digest}  {prefix}.zip\n".encode("utf-8"))

    print(f"[OK] release archive: {archive}")
    print(f"  files={len(files)} bytes={archive.stat().st_size}")
    print(f"  sha256={digest}")
    print(f"  sidecar: {sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())