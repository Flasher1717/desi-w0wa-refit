"""Download and verify all external data files (the project's only network step).

Reads data_manifest.json, downloads each file to data/ atomically
(temp file + rename), and verifies its SHA256. Idempotent: files already
present with a matching hash are skipped. A hash mismatch is a hard error
and leaves no partial file behind.

Usage: uv run python scripts/download_data.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "data_manifest.json"
DATA_DIR = PROJECT_ROOT / "data"
CHUNK_SIZE = 1 << 20


@dataclass(frozen=True)
class ManifestEntry:
    name: str
    url: str
    sha256: str


def load_manifest(path: Path) -> list[ManifestEntry]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    files: list[dict[str, str]] = raw["files"]
    return [ManifestEntry(name=f["name"], url=f["url"], sha256=f["sha256"].lower()) for f in files]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def download_atomic(entry: ManifestEntry, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    try:
        with urllib.request.urlopen(entry.url) as response, tmp.open("wb") as out:
            while chunk := response.read(CHUNK_SIZE):
                out.write(chunk)
        actual = sha256_of(tmp)
        if actual != entry.sha256:
            raise RuntimeError(
                f"{entry.name}: SHA256 mismatch after download "
                f"(expected {entry.sha256}, got {actual}). "
                "The pinned upstream content changed or the transfer was corrupted."
            )
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    entries = load_manifest(MANIFEST_PATH)
    DATA_DIR.mkdir(exist_ok=True)
    for entry in entries:
        dest = DATA_DIR / entry.name
        if dest.is_file() and sha256_of(dest) == entry.sha256:
            print(f"ok       {entry.name} (already present, hash verified)")
            continue
        print(f"download {entry.name}")
        download_atomic(entry, dest)
        print(f"verified {entry.name}")
    print(f"All {len(entries)} files present and verified in {DATA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
