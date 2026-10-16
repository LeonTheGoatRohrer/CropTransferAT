"""Download the open multi-crop yield packages (reports/plan_mehrkultur.md, step W1.1).

Each package is stored under ``data/raw/<name>/`` together with ``MANIFEST.json`` (URL, SHA-256,
size, licence note, download date). Raw data never enters the repository (AGENTS.md 4.5).
Archives are unpacked with a path check; the INVITE ``SiriusQyality/`` folder (contains .exe
files) is never extracted.

AUSTRIA RULE: no package here contains Austrian trial data; the Austrian files stay untouched.
Usage:  python -m croptransfer.fetch_open_sets [--only invite briwecs ...] [--include-large]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

from croptransfer.config import load_config, repo_path

USER_AGENT = "CropTransferAT-research/0.1 (student project; private)"
CHUNK = 1 << 20

# name -> files to fetch (url, target file name) and metadata. Sources: reports/plan_mehrkultur.md
# section 2 (package ids A1..A11). ``large`` packages are only fetched with --include-large.
PACKAGES: dict[str, dict[str, Any]] = {
    "invite": {
        "plan_id": "A1",
        "crop": "winter wheat",
        "licence": "CC BY (Zenodo record); file header says Confidential -> local use only (D12)",
        "files": [("https://zenodo.org/api/records/20786880/files/Dataset.zip/content", "Dataset.zip")],
        "unzip": True,
        "skip_prefixes": ["SiriusQyality/"],
    },
    "briwecs": {
        "plan_id": "A2",
        "crop": "winter wheat",
        "licence": "see figshare record 27910269",
        "files": [("https://ndownloader.figshare.com/files/50832927", "briwecs.zip")],
        "unzip": True,
    },
    "peas_fr": {
        "plan_id": "A9",
        "crop": "field pea",
        "licence": "Recherche Data Gouv 10.57745/FW78RE (see record)",
        "files": [
            ("https://entrepot.recherche.data.gouv.fr/api/access/datafile/764684", "pea_764684"),
            ("https://entrepot.recherche.data.gouv.fr/api/access/datafile/764683", "pea_764683"),
            ("https://entrepot.recherche.data.gouv.fr/api/access/datafile/764685", "pea_764685"),
        ],
    },
    "nordic_barley": {
        "plan_id": "A11",
        "crop": "spring barley (BLUP, tier S4)",
        "licence": "DataverseNO 10.18710/IZ3EFE (see record)",
        "files": [("https://dataverse.no/api/access/datafile/268105", "nordic_268105")],
    },
    "nvt_au": {
        "plan_id": "A10",
        "crop": "wheat, barley, canola (Australia)",
        "licence": "CC BY 4.0 (figshare 16610449); GRDC objected to publication",
        "files": [("https://ndownloader.figshare.com/files/30742573", "nvt.zip")],
        "unzip": True,
        "large": True,
    },
}


def sha256_file(path: Path) -> str:
    """SHA-256 hex digest of a file (streamed)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def download(url: str, target: Path) -> int:
    """Stream ``url`` to ``target`` (via a .part file); return the size in bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    part = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(req, timeout=120) as resp, open(part, "wb") as out:
        for block in iter(lambda: resp.read(CHUNK), b""):
            out.write(block)
    part.replace(target)
    return target.stat().st_size


def safe_extract(archive: Path, dest: Path, skip_prefixes: list[str] | None = None) -> list[str]:
    """Unpack a zip below ``dest``; refuse paths that leave ``dest``; skip given prefixes."""
    dest_root = dest.resolve()
    extracted: list[str] = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            name = info.filename
            if any(name.startswith(p) for p in (skip_prefixes or [])):
                continue
            out = (dest / name).resolve()
            if dest_root not in out.parents and out != dest_root:
                raise ValueError(f"unsafe path in archive: {name}")
            zf.extract(info, dest)
            if not info.is_dir():
                extracted.append(name)
    return extracted


def fetch_package(name: str, raw_root: Path, force: bool = False) -> dict[str, Any]:
    """Download one package and write its MANIFEST.json (skipped if present, unless ``force``)."""
    spec = PACKAGES[name]
    folder = raw_root / name
    manifest_path = folder / "MANIFEST.json"
    if manifest_path.exists() and not force:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    for url, fname in spec["files"]:
        target = folder / fname
        size = download(url, target)
        files.append({"url": url, "file": fname, "bytes": size, "sha256": sha256_file(target)})
        if spec.get("unzip") and zipfile.is_zipfile(target):
            members = safe_extract(target, folder / "unpacked", spec.get("skip_prefixes"))
            files[-1]["unpacked_files"] = len(members)
    manifest = {
        "package": name, "plan_id": spec["plan_id"], "crop": spec["crop"], "licence": spec["licence"],
        "downloaded": date.today().isoformat(), "files": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="*", help="package names (default: all non-large)")
    ap.add_argument("--include-large", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    raw = repo_path(load_config()["paths"]["raw"])
    names = args.only or [n for n, s in PACKAGES.items() if args.include_large or not s.get("large")]
    for n in names:
        m = fetch_package(n, raw, force=args.force)
        print(n, [(f["file"], f["bytes"]) for f in m["files"]])


if __name__ == "__main__":
    main()
