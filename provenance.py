"""
provenance.py
=============
Every hilbertbrane output is fully determined by its resolved parameters + seed,
so each file can carry everything needed to reproduce it. This module builds a
canonical provenance record (full config + git SHA + tool version + the command
that made it), embeds it wherever a format allows arbitrary metadata, always
offers a sidecar ``*.provenance.json``, and can regenerate from one.

Embedding support by format:
    3mf            <metadata> entries                (exporters.py)
    gltf/glb       asset.extras                       (exporters.py)
    ply            header `comment` lines             (here: embed_ply_comments)
    swc / feb      header comments                    (exporters / morphoelastic)
    gii            GiftiMetaData                       (neuro.py)
    graphml/gexf   graph attributes                    (neuro.py)
    stl, nii, msh, inp, vtu  -> no metadata slot; sidecar JSON only.

The sidecar is the universal, canonical source for `--from-provenance`.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from typing import Optional

VERSION = "0.2.0"
TOOL = "hilbertbrane"
SIDECAR_SUFFIX = ".provenance.json"

__all__ = [
    "VERSION", "TOOL", "SIDECAR_SUFFIX",
    "git_sha", "build_record", "to_json", "flatten",
    "write_sidecar", "sidecar_path", "embed_ply_comments",
    "load", "config_from_record",
]


def git_sha(cwd: Optional[str] = None) -> str:
    """Short git SHA of the working tree, '-dirty' suffixed if modified."""
    cwd = cwd or os.path.dirname(os.path.abspath(__file__))
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd, stderr=subprocess.DEVNULL).decode().strip()
        dirty = subprocess.call(
            ["git", "diff", "--quiet"], cwd=cwd,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return (sha + ("-dirty" if dirty else "")) if sha else "unknown"
    except Exception:
        return "unknown"


def build_record(config: dict,
                 command: Optional[str] = None,
                 extra: Optional[dict] = None) -> dict:
    """Assemble the canonical provenance record from a resolved config."""
    record = {
        "tool": TOOL,
        "version": VERSION,
        "git": git_sha(),
        "created": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "config": _jsonable(config),
    }
    if extra:
        record.update(_jsonable(extra))
    return record


def to_json(record: dict, compact: bool = False) -> str:
    if compact:
        return json.dumps(record, separators=(",", ":"), sort_keys=True)
    return json.dumps(record, indent=2, sort_keys=True)


def flatten(record: dict) -> dict:
    """Flat string key/value map for formats that only take simple metadata.

    Includes a 'provenance_json' field holding the *entire* record compactly,
    so any format that can store this one field is fully self-regenerating.
    """
    return {
        "tool": str(record.get("tool", TOOL)),
        "version": str(record.get("version", VERSION)),
        "git": str(record.get("git", "unknown")),
        "created": str(record.get("created", "")),
        "command": str(record.get("command") or ""),
        "provenance_json": to_json(record, compact=True),
    }


# ---------------------------------------------------------------------------
# sidecar
# ---------------------------------------------------------------------------
def sidecar_path(output_path: str) -> str:
    """`brain.stl` -> `brain.stl.provenance.json` (keeps the original ext visible)."""
    return output_path + SIDECAR_SUFFIX


def write_sidecar(output_path: str, record: dict) -> str:
    path = sidecar_path(output_path)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(to_json(record) + "\n")
    return path


# ---------------------------------------------------------------------------
# PLY: splice `comment` lines into the (ASCII) header of an ascii/binary PLY
# ---------------------------------------------------------------------------
def embed_ply_comments(path: str, record: dict) -> None:
    """Insert provenance as PLY header comments without disturbing binary data."""
    with open(path, "rb") as fh:
        data = fh.read()
    fmt = data.find(b"\nformat ")
    if fmt < 0:
        return  # not a PLY we recognise; leave it alone
    eol = data.find(b"\n", fmt + 1)  # end of the 'format ...' line
    if eol < 0:
        return
    flat = flatten(record)
    lines = [f"{k} {v}" for k, v in flat.items() if k != "provenance_json"]
    lines.append("provenance " + flat["provenance_json"])
    blob = b"".join(b"comment " + ln.replace("\n", " ").encode("utf-8", "replace")
                    + b"\n" for ln in lines)
    with open(path, "wb") as fh:
        fh.write(data[:eol + 1] + blob + data[eol + 1:])


# ---------------------------------------------------------------------------
# regeneration
# ---------------------------------------------------------------------------
def load(path: str) -> dict:
    """Load a provenance record from a sidecar/JSON file or an output file's sidecar."""
    if not path.endswith(".json") and not path.endswith(SIDECAR_SUFFIX):
        side = sidecar_path(path)
        if os.path.exists(side):
            path = side
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def config_from_record(record: dict) -> dict:
    """Extract the resolved config needed to regenerate the output."""
    cfg = dict(record.get("config", {}))
    cfg["preview"] = False  # never pop a window when regenerating
    return cfg


# ---------------------------------------------------------------------------
def _jsonable(obj):
    """Make a config JSON-serialisable (tuples -> lists, etc.)."""
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)
