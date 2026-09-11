"""Stage 1 — ACL Anthology ingest.

Pulls the Anthology's XML metadata (1,000 volume files, ~77 MB) as a single
tarball from GitHub and flattens it to one row per paper.

Verified 2026-09-10: 2024.acl.xml carries 1,030 papers, 1,021 with DOIs (99%).
DOIs use the 10.18653 prefix from 2015; earlier volumes largely lack them, so
the OpenAlex join in stage 2 falls back to title+year matching for the tail.

    python -m src.ingest_acl              # -> data/interim/acl_papers.parquet|csv
    python -m src.ingest_acl --limit 20   # smoke test on 20 volumes
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
TARBALL_URL = "https://codeload.github.com/acl-org/acl-anthology/tar.gz/refs/heads/master"
TARBALL = RAW / "acl-anthology-master.tar.gz"

# Volume-id prefixes we treat as the core *ACL venues, mirroring how the
# Anthology itself namespaces collections. Everything else is kept but flagged,
# so a later filter is a column select rather than a re-ingest.
CORE_VENUES = {"acl", "emnlp", "naacl", "eacl", "coling", "tacl", "cl", "findings", "conll", "lrec", "semeval", "ws", "anlp", "aacl", "ijcnlp"}


def text_of(el) -> str:
    """Flatten an element's mixed content (titles carry <fixed-case> etc.)."""
    if el is None:
        return ""
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def download(force: bool = False) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    if TARBALL.exists() and not force and TARBALL.stat().st_size > 1_000_000:
        print(f"[cache] {TARBALL.name} ({TARBALL.stat().st_size/1e6:.1f} MB)")
        return TARBALL
    print(f"[get ] {TARBALL_URL}")
    req = urllib.request.Request(TARBALL_URL, headers={"User-Agent": "ai4peace-research/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        blob = r.read()
    TARBALL.write_bytes(blob)
    print(f"[ok  ] {len(blob)/1e6:.1f} MB -> {TARBALL}")
    return TARBALL


def volume_id(name: str) -> str:
    """'2024.acl.xml' -> 'acl'; 'P19.xml' -> 'P19' (old scheme)."""
    stem = Path(name).stem
    parts = stem.split(".")
    return parts[1] if len(parts) > 1 else stem


def parse_volume(raw: bytes, source: str) -> list[dict]:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  ! parse error in {source}: {e}", file=sys.stderr)
        return []

    collection_id = root.attrib.get("id", Path(source).stem)
    out: list[dict] = []

    for vol in root.findall("volume"):
        vol_id = vol.attrib.get("id", "")
        vol_title = text_of(vol.find("meta/booktitle"))
        vol_year = text_of(vol.find("meta/year"))

        for paper in vol.findall("paper"):
            title = text_of(paper.find("title"))
            if not title:
                continue
            year = text_of(paper.find("year")) or vol_year
            authors = [
                " ".join(x for x in (text_of(a.find("first")), text_of(a.find("last"))) if x)
                for a in paper.findall("author")
            ]
            out.append(
                {
                    "acl_id": f"{collection_id}-{vol_id}.{paper.attrib.get('id','')}",
                    "collection_id": collection_id,
                    "volume_id": vol_id,
                    "paper_id": paper.attrib.get("id", ""),
                    "title": title,
                    "year": pd.to_numeric(year, errors="coerce"),
                    "doi": text_of(paper.find("doi")) or None,
                    "url": text_of(paper.find("url")) or None,
                    "abstract": text_of(paper.find("abstract")) or None,
                    "n_authors": len(authors),
                    "authors": "; ".join(authors),
                    "booktitle": vol_title,
                    "venue_key": volume_id(source),
                    "source_file": source,
                }
            )
    return out


def build(limit: int | None = None) -> pd.DataFrame:
    tar_path = download()
    rows: list[dict] = []
    n_files = 0

    with tarfile.open(tar_path, "r:gz") as tf:
        members = [m for m in tf.getmembers() if m.name.endswith(".xml") and "/data/xml/" in m.name]
        members.sort(key=lambda m: m.name)
        if limit:
            members = members[:limit]
        print(f"[xml ] {len(members)} volume files")
        for m in members:
            fh = tf.extractfile(m)
            if fh is None:
                continue
            rows.extend(parse_volume(fh.read(), Path(m.name).name))
            n_files += 1
            if n_files % 200 == 0:
                print(f"       {n_files}/{len(members)} files, {len(rows)} papers")

    df = pd.DataFrame(rows)
    df["is_core_venue"] = df["venue_key"].str.lower().isin(CORE_VENUES)
    df["has_doi"] = df["doi"].notna()

    INTERIM.mkdir(parents=True, exist_ok=True)
    out_csv = INTERIM / "acl_papers.csv"
    df.to_csv(out_csv, index=False)
    try:
        df.to_parquet(INTERIM / "acl_papers.parquet", index=False)
    except Exception:
        pass  # pyarrow optional; CSV is the contract

    print(f"\n[done] {len(df):,} papers from {n_files} volumes -> {out_csv}")
    print(f"       DOIs: {df['has_doi'].sum():,} ({100*df['has_doi'].mean():.1f}%)")
    yr = df["year"].dropna()
    if len(yr):
        print(f"       years: {int(yr.min())}–{int(yr.max())}")
    print(f"       core-venue papers: {df['is_core_venue'].sum():,}")
    print("\n       top venues:")
    for k, v in df["venue_key"].value_counts().head(12).items():
        print(f"         {k:<12} {v:,}")
    print("\n       DOI coverage by era:")
    for lo, hi in [(1979, 1999), (2000, 2009), (2010, 2014), (2015, 2019), (2020, 2026)]:
        sl = df[(df["year"] >= lo) & (df["year"] <= hi)]
        if len(sl):
            print(f"         {lo}–{hi}: {len(sl):>6,} papers, {100*sl['has_doi'].mean():>5.1f}% with DOI")
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only parse the first N volume files")
    build(ap.parse_args().limit)
