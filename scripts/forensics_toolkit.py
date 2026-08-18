"""
Digital Forensics Toolkit
==========================

Evidence collection and analysis toolkit for compromised systems.
Demonstrates a defensible forensic workflow:
  1. Evidence handling & chain of custody
  2. Disk imaging helpers (dd / FTK Imager)
  3. Hashing for integrity (SHA-256)
  4. Metadata / artifact collection (timestamps, file listing)
  5. Memory analysis hooks (Volatility)
  6. Reporting (structured JSON output)

The functions that invoke external tools (dd, fls, volatility) print the exact
command to run so the operator keeps full control of a live forensic chain.

Dependencies: none beyond the Python standard library.
"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Evidence & chain of custody
# ---------------------------------------------------------------------------
EVIDENCE_DIR = "evidence"
CHAIN_FILE = "chain_of_custody.json"


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_evidence_id() -> str:
    return f"EVID-{uuid.uuid4().hex[:8].upper()}"


def log_chain_of_custody(evidence_id: str, action: str, handler: str, details: str = "") -> None:
    """Append an entry to the chain-of-custody log (evidence/chain_of_custody.json)."""
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    path = os.path.join(EVIDENCE_DIR, CHAIN_FILE)
    entry = {
        "evidence_id": evidence_id,
        "timestamp_utc": timestamp(),
        "action": action,
        "handler": handler,
        "details": details,
    }
    records = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                records = json.load(fh)
        except (json.JSONDecodeError, OSError):
            records = []
    records.append(entry)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2)
    print(f"[chain-of-custody] {entry['timestamp_utc']} | {evidence_id} | {action} | {handler}")


# ---------------------------------------------------------------------------
# Hashing & integrity
# ---------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    """Compute the SHA-256 hash of a file (for evidence integrity)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Disk imaging helpers (conceptual)
# ---------------------------------------------------------------------------
def disk_image_command(source: str, dest: str) -> str:
    """Return the dd command to create a raw bit-stream image (Linux)."""
    return f"sudo dd if={source} of={dest} bs=4M conv=noerror,sync status=progress"


def tsk_commands(image: str) -> list[str]:
    """Return common Sleuth Kit commands to run against an image."""
    return [
        f"fls -r -p {image}",          # list files and directories
        f"fsstat {image}",             # file system statistics
        f"mmls {image}",               # partition layout
        f"istat {image} <inode>",      # inode details
        f"icat {image} <inode>",       # export file contents by inode
    ]


# ---------------------------------------------------------------------------
# Artifact collection (host)
# ---------------------------------------------------------------------------
def collect_metadata(path: str) -> dict:
    """Collect forensic metadata for a file (MAC times, size)."""
    st = os.stat(path)
    def utc(ts):
        return datetime.fromtimestamp(ts, timezone.utc).isoformat()

    return {
        "path": os.path.abspath(path),
        "size_bytes": st.st_size,
        "mtime_utc": utc(st.st_mtime),
        "atime_utc": utc(st.st_atime),
        "ctime_utc": utc(st.st_ctime),
        "sha256": sha256_file(path),
    }


def collect_artifact(path: str, handler: str) -> str:
    """Collect an artifact with chain-of-custody + metadata + hash."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    evidence_id = new_evidence_id()
    log_chain_of_custody(evidence_id, "acquired", handler, f"artifact: {path}")

    meta = collect_metadata(path)
    report_path = os.path.join(EVIDENCE_DIR, f"{evidence_id}_report.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(
            {"evidence_id": evidence_id, "source": path, "metadata": meta},
            fh, indent=2,
        )
    print(f"[collect] evidence {evidence_id} -> {report_path}")
    return evidence_id


# ---------------------------------------------------------------------------
# Memory analysis hook (Volatility)
# ---------------------------------------------------------------------------
def volatility_commands(memfile: str) -> list[str]:
    """Common Volatility 3 plugins for memory forensics."""
    return [
        f"vol3 -f {memfile} windows.pslist",          # process list
        f"vol3 -f {memfile} windows.cmdline",         # process command lines
        f"vol3 -f {memfile} windows.netscan",         # network connections
        f"vol3 -f {memfile} windows.malfind",         # find injected / hidden code
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Digital Forensics Toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("collect", help="Collect an artifact with chain of custody")
    a.add_argument("--path", required=True)
    a.add_argument("--handler", required=True, help="name of the evidence handler")
    a.set_defaults(fn=lambda args: collect_artifact(args.path, args.handler))

    d = sub.add_parser("image", help="Show disk imaging command (dd)")
    d.add_argument("--source", required=True)
    d.add_argument("--dest", required=True)
    d.set_defaults(fn=lambda args: print(disk_image_command(args.source, args.dest)))

    t = sub.add_parser("tsk", help="Show Sleuth Kit commands for an image")
    t.add_argument("--image", required=True)
    t.set_defaults(fn=lambda args: print("\n".join(tsk_commands(args.image))))

    m = sub.add_parser("memory", help="Show Volatility commands for a memory image")
    m.add_argument("--file", required=True)
    m.set_defaults(fn=lambda args: print("\n".join(volatility_commands(args.file))))

    c = sub.add_parser("chain", help="Print chain-of-custody log")
    c.set_defaults(fn=lambda args: _print_chain())

    args = p.parse_args(argv)
    return args.fn(args)


def _print_chain() -> int:
    path = os.path.join(EVIDENCE_DIR, CHAIN_FILE)
    if not os.path.exists(path):
        print("No chain-of-custody log yet.")
        return 0
    with open(path, "r", encoding="utf-8") as fh:
        print(json.dumps(json.load(fh), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
