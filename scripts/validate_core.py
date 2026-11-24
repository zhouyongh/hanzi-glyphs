#!/usr/bin/env python3
"""Self-contained validator for this standalone core-asset folder.

Uses ONLY this folder's own files: glyphs.csv, quality.csv and glyphs/<layer>/*.svg.
The 13 frozen layer keys are embedded below (FROZEN_LAYERS).  No repo, no provenance,
no audit, no build_core import, no external mapping file.

Scope: the layer-1 contract (keys, paths, fields, quality values/counts, note syntax).
Evidence-level re-derivation (sha256==source_sha256, trace_iou>=0.97, JGW source_url
backfill) is out of scope for this folder; here we assert the published results
(counts/sets), not re-derive them.  Failed pieces have been removed from this package
(their rubbing originals stay as repo-side evidence); the note column is retained but
empty, and the failed-note syntax guard is kept defensively (expected split 0/0/0).
Also verifies manifest.json: rows, per-layer counts, quality counts, the two table
sha256, and the asset aggregate sha256 (assets_count / assets_sha256), and asserts
that no asset still carries a near-white corner mark (watermark-stripped pieces).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
GLYPHS = BASE / "glyphs"

CORE_FIELDS = ["layer", "path", "modern_char", "unicode",
               "source", "source_ref", "source_url", "license"]
QUALITY_FIELDS = ["layer", "path", "quality", "note"]
EXPECTED_ROWS = 183_717
EXPECTED_Q = {"byte-verified": 13_006, "metric-passed": 18_387,
              "watermark-stripped": 12_274, "unverified": 140_050, "failed": 0}
FROZEN_LAYERS = ["oracle-bone", "seal", "bronze", "clerical", "chu", "guwen", "qin",
                 "regular", "running", "cursive", "song-hans", "song-hant", "hei-hant-hk"]
UNICODE_RE = re.compile(r"^[0-9A-F]{6}$")
NOTE_RE = re.compile(r"^replacement=(none|rubbing:.+?)(;reason=[^;]+)?(;caution=true)?$")
LICENSES = {"CC0-1.0", "CC-BY-4.0", "OFL-1.1"}
# source codes are dataset identifiers, NOT layer keys.
SOURCES = {
    "zdic-jiaguwen", "zdic-jinwen", "zdic-zhuanshu", "zdic-lishu",
    "zdic-qinwenzi", "zdic-chuwenzi", "zdic-chuanchao",
    "xxt-jiaguwen", "xxt-jinwen", "xxt-xiaozhuan", "xxt-lishu",
    "xxt-chuwenzi", "xxt-chuanchao", "xxt-qinwenzi",
    "jgw-parametric-0.3",
    "font-noto-serif-sc", "font-noto-serif-tc", "font-chiron-hei-hk",
    "font-liujianmaocao", "font-mashanzheng", "font-zhimangxing",
}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def read(path: Path, fields: list[str]) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames != fields:
            fail(f"{path.name}: header {rd.fieldnames} != {fields}")
        return list(rd)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


NEAR_FILL_RE = re.compile(rb"fill\s*(?:=\s*\"?|:\s*\"?)(#[0-9a-fA-F]{3,6})")


def has_near_white(data: bytes) -> bool:
    """True if any element is filled near-white (all channels >= 240)."""
    for m in NEAR_FILL_RE.finditer(data):
        h = m.group(1).decode()
        if len(h) == 4:
            h = "#" + "".join(c * 2 for c in h[1:])
        if all(int(h[i:i + 2], 16) >= 240 for i in (1, 3, 5)):
            return True
    return False


def check_manifest(core: list[dict], layers: Counter, qcount: Counter) -> None:
    mp = BASE / "manifest.json"
    if not mp.exists():
        fail("manifest.json missing"); return
    m = json.loads(mp.read_text(encoding="utf-8"))
    if m.get("rows") != len(core):
        fail(f"manifest rows {m.get('rows')} != {len(core)}")
    if m.get("layers") != {k: layers.get(k, 0) for k in FROZEN_LAYERS}:
        fail("manifest per-layer counts mismatch")
    if m.get("quality") != {k: qcount.get(k, 0) for k in EXPECTED_Q}:
        fail("manifest quality counts mismatch")
    for fn in ("glyphs.csv", "quality.csv"):
        if m.get("sha256", {}).get(fn) != sha256_file(BASE / fn):
            fail(f"manifest sha256 mismatch: {fn}")
    entries = []
    marked = []
    for ly in FROZEN_LAYERS:
        for p in (GLYPHS / ly).glob("*.svg"):
            data = p.read_bytes()
            if has_near_white(data):
                marked.append(f"{ly}/{p.name}")
            entries.append((f"{ly}/{p.name}", hashlib.sha256(data).hexdigest()))
    if marked:
        fail(f"assets still carrying near-white corner marks: {len(marked)} e.g. {marked[:5]}")
    entries.sort()
    agg = hashlib.sha256("\n".join(f"{k}\t{h}" for k, h in entries).encode("utf-8")).hexdigest()
    if m.get("assets_count") != len(entries):
        fail(f"manifest assets_count {m.get('assets_count')} != {len(entries)}")
    if m.get("assets_sha256") != agg:
        fail("manifest assets_sha256 mismatch")


def main() -> int:
    new_order = FROZEN_LAYERS
    core = read(BASE / "glyphs.csv", CORE_FIELDS)
    qual = read(BASE / "quality.csv", QUALITY_FIELDS)

    if len(core) != EXPECTED_ROWS:
        fail(f"core rows {len(core)} != {EXPECTED_ROWS}")
    keys = [(r["layer"], r["path"]) for r in core]
    dup = [k for k, c in Counter(keys).items() if c > 1]
    if dup:
        fail(f"duplicate core keys: {dup[:5]}")

    layers = Counter(k[0] for k in keys)
    if set(layers) != set(new_order):
        fail(f"layer set != frozen 13: {sorted(set(layers) ^ set(new_order))}")

    # assets: every core path resolves; per-layer disk == core; no extra, no subdir
    for r in core:
        if not (GLYPHS / r["layer"] / r["path"]).exists():
            fail(f"core path missing on disk: {r['layer']}/{r['path']}"); break
    for ly in new_order:
        disk = len(list((GLYPHS / ly).glob("*.svg")))
        if disk != layers.get(ly, 0):
            fail(f"{ly}: disk {disk} != core {layers.get(ly, 0)}")
    keyset = set(keys)
    extra = [(ly, e.name) for ly in new_order for e in (GLYPHS / ly).iterdir()
             if e.is_file() and e.name.endswith(".svg") and (ly, e.name) not in keyset]
    if extra:
        fail(f"extra svg not in core: {extra[:5]}")
    subdirs = [str(p.relative_to(GLYPHS)) for p in GLYPHS.rglob("*")
               if p.is_dir() and p.parent != GLYPHS]
    if subdirs:
        fail(f"unexpected subdir under layer: {subdirs[:5]}")

    only_one = bad_fmt = bad_char = bad_path = 0
    for r in core:
        mc, uc = r["modern_char"], r["unicode"]
        if bool(mc) != bool(uc):
            only_one += 1
        elif mc:
            if not UNICODE_RE.match(uc):
                bad_fmt += 1
            elif len(mc) != 1 or ord(mc) != int(uc, 16):
                bad_char += 1
        if r["source"] not in SOURCES:
            fail(f"bad source code {r['source']!r} at {r['layer']}/{r['path']}")
        if r["license"] not in LICENSES:
            fail(f"bad license {r['license']!r} at {r['layer']}/{r['path']}")
        for f in ("source_ref", "source_url", "license"):
            if not r[f]:
                fail(f"empty {f} at {r['layer']}/{r['path']}")
        p = r["path"]
        if (p.startswith("/") or "\\" in p or "%" in p
                or any(s in (".", "..", "") for s in p.split("/"))
                or not p.endswith(".svg")):
            bad_path += 1
            fail(f"illegal path at {r['layer']}/{p}")
    for name, n in (("modern_char/unicode one-sided", only_one),
                    ("bad unicode format", bad_fmt),
                    ("char/codepoint mismatch", bad_char),
                    ("illegal paths", bad_path)):
        if n:
            fail(f"{name}: {n}")
    subdir_path = [r["path"] for r in core if "/" in r["path"]]
    if subdir_path:
        fail(f"core path not a direct child: {subdir_path[:5]}")

    # quality
    if [(r["layer"], r["path"]) for r in qual] != keys:
        fail("quality keys not one-to-one with core keys (order)")
    qcount = Counter(r["quality"] for r in qual)
    if set(qcount) - set(EXPECTED_Q):
        fail(f"unknown quality values: {sorted(set(qcount) - set(EXPECTED_Q))}")
    for k, v in EXPECTED_Q.items():
        if qcount.get(k, 0) != v:
            fail(f"quality {k} {qcount.get(k, 0)} != {v}")

    n_none = n_rub = n_caution = 0
    for r in qual:
        note = r["note"]
        if r["quality"] == "failed":
            m = NOTE_RE.match(note)
            if not m:
                fail(f"illegal failed note at {r['layer']}/{r['path']}: {note!r}")
                continue
            if m.group(1) == "none":
                n_none += 1
            else:
                n_rub += 1
                seg = m.group(1).split(":", 1)[1]
                mm = re.match(r"^glyphs/([^/]+)/rubbing/", seg)
                if not mm or mm.group(1) not in new_order:
                    fail(f"rubbing layer segment not a frozen key: {seg}")
            if ";caution=true" in note:
                n_caution += 1
        elif note:
            fail(f"non-failed note not empty at {r['layer']}/{r['path']}")
    if (n_rub, n_none, n_caution) != (0, 0, 0):
        fail(f"failed split rubbing={n_rub} none={n_none} caution={n_caution} != 0/0/0")

    check_manifest(core, layers, qcount)

    if errors:
        print(f"[FAIL] {len(errors)} issue(s):")
        for e in errors[:40]:
            print("  -", e)
        return 1
    print("[OK] standalone core-folder validation passed (layer-1 contract)")
    print(f"  core rows={len(core)} layers={len(layers)} keys={len(keyset)}")
    print(f"  quality {dict(qcount)}")
    print(f"  failed: rubbing={n_rub} none={n_none} caution={n_caution}")
    print("  manifest: rows/layers/quality/table-sha256/assets verified")
    print("  note: evidence re-derivation & rubbing target existence are out of scope for this folder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())