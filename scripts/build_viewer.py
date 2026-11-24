#!/usr/bin/env python3
"""Generate the self-contained viewer index from this folder's own tables.

Reads glyphs.csv + quality.csv (joined on the natural key (layer, path)) and writes,
per layer, a lean search index and a lazy source-detail file, plus meta.json:

  viewer/data/layer-<layer>.json  search/grid index, rows:
                                  [path, modern_char, unicode, quality, license]
  viewer/data/src-<layer>.json    source detail, loaded only when a detail is opened:
                                  { "<path>": [source, source_ref, source_url] }
  viewer/data/meta.json           version, layer order, counts, totals, and one
                                  probe asset path used to verify the glyph base

The viewer loads indexes lazily and reads SVGs locally from ../glyphs/<layer>/<path>.
No unified_id, no CDN, no pinyin, no provenance: the new-world core only.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "viewer" / "data"

FROZEN_LAYERS = ["oracle-bone", "seal", "bronze", "clerical", "chu", "guwen", "qin",
                 "regular", "running", "cursive", "song-hans", "song-hant", "hei-hant-hk"]


def dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> int:
    with (BASE / "glyphs.csv").open(encoding="utf-8-sig", newline="") as fh:
        core = list(csv.DictReader(fh))
    with (BASE / "quality.csv").open(encoding="utf-8-sig", newline="") as fh:
        qual = {(r["layer"], r["path"]): r["quality"] for r in csv.DictReader(fh)}
    manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))

    index: dict[str, list] = {ly: [] for ly in FROZEN_LAYERS}
    src: dict[str, dict] = {ly: {} for ly in FROZEN_LAYERS}
    chars = set()
    for r in core:
        ly, p = r["layer"], r["path"]
        index[ly].append([p, r["modern_char"], r["unicode"], qual[(ly, p)], r["license"]])
        src[ly][p] = [r["source"], r["source_ref"], r["source_url"]]
        if r["modern_char"]:
            chars.add(r["modern_char"])

    OUT.mkdir(parents=True, exist_ok=True)
    counts = {}
    for ly in FROZEN_LAYERS:
        counts[ly] = len(index[ly])
        dump(OUT / f"layer-{ly}.json", {"layer": ly, "n": len(index[ly]), "rows": index[ly]})
        dump(OUT / f"src-{ly}.json", {"layer": ly, "s": src[ly]})

    meta = {"name": manifest["name"], "version": manifest["version"],
            "layers": FROZEN_LAYERS, "counts": counts,
            "glyphs": len(core), "chars": len(chars), "dataBase": "data/",
            "probe": f"{FROZEN_LAYERS[0]}/{index[FROZEN_LAYERS[0]][0][0]}"}
    dump(OUT / "meta.json", meta)

    idx_bytes = sum((OUT / f"layer-{ly}.json").stat().st_size for ly in FROZEN_LAYERS)
    src_bytes = sum((OUT / f"src-{ly}.json").stat().st_size for ly in FROZEN_LAYERS)
    print(f"[OK] viewer data: {len(FROZEN_LAYERS)} index + {len(FROZEN_LAYERS)} src + meta.json")
    print(f"  glyphs={len(core)} chars={len(chars)}")
    print(f"  index bytes={idx_bytes}  src bytes={src_bytes}")
    print(f"  counts={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())