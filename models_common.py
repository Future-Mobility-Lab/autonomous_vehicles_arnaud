"""Small helpers shared by the model scripts (standard library only)."""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def setup_console() -> None:
    """Never let a stray character stop a run on a Windows console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:                                   # noqa: BLE001 - best effort only
            pass


def stop(message: str) -> None:
    print("\nSTOPPED: " + message, flush=True)
    sys.exit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def ids_sha256(ids) -> str:
    """Membership SHA-256: ids sorted, joined by a newline, no trailing newline."""
    return hashlib.sha256("\n".join(sorted(str(i) for i in ids)).encode("utf-8")).hexdigest()


def pairs_sha256(mapping: dict) -> str:
    """SHA-256 of the lines "id:value", sorted by id, joined by a newline, no trailing newline."""
    return hashlib.sha256("\n".join(f"{k}:{mapping[k]}" for k in sorted(mapping)).encode("utf-8")).hexdigest()


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def replace_patiently(tmp: Path, path: Path) -> None:
    """Move a finished temporary file into place. On Windows a virus scanner or a sync client can
    hold a file for a moment, so a refused move is tried again for up to about ten seconds."""
    for attempt in range(20):
        try:
            tmp.replace(path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.5)


def check_run_libraries(names) -> None:
    """Stop unless the libraries named have the versions models_config.RUN_LIBRARY_VERSIONS fixes."""
    import models_config as cfg
    found = {}
    for name in names:
        module = {"scikit-learn": "sklearn"}.get(name, name)
        try:
            found[name] = __import__(module).__version__
        except ImportError:
            found[name] = "not installed"
    wrong = {n: v for n, v in found.items() if v != cfg.RUN_LIBRARY_VERSIONS[n]}
    if wrong:
        pins = " ".join(f"{n}=={cfg.RUN_LIBRARY_VERSIONS[n]}" for n in names)
        stop(f"these runs use {', '.join(f'{n} {cfg.RUN_LIBRARY_VERSIONS[n]}' for n in names)}; found "
             f"{', '.join(f'{n} {v}' for n, v in found.items())}.\n  Install them with:  pip install {pins}\n"
             f"  then restart the runtime (Colab: Runtime > Restart session) and run this again.")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    replace_patiently(tmp, path)


def read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_rows_csv(path: Path, header: list[str], rows: list[list]) -> str:
    """Write a CSV with UTF-8, LF line endings and minimal quoting; return its SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    replace_patiently(tmp, path)
    return sha256_file(path)


def versions(*modules: str) -> dict:
    out = {"python": platform.python_version()}
    for name in modules:
        try:
            mod = __import__(name)
            out[name] = getattr(mod, "__version__", "unknown")
        except Exception:                                   # noqa: BLE001 - recorded, not fatal
            out[name] = "not installed"
    return out


def show_register_block(path: Path, lines: list[str]) -> None:
    """Print the lines to paste into docs/decision_register.md, and keep a copy in a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        where = f"The same lines are in {path.name} (hashes only, safe to open): copy them from that file."
    except OSError as e:
        where = f"Could not write {path.name} ({e}). Copy the lines below from this window instead."
    bar = "=" * 78
    print("\n" + bar)
    print("REGISTER BLOCK. " + where)
    print(bar)
    for line in lines:
        print(line)
    print(bar)
