"""Tranche 2 pipeline: configuration and shared helpers.

Governed by R1 and Deviations 2, 5 and 10 of docs/analysis_preregistration.md.

Run order:
    1. python tranche2_01_export_prefilter_input.py     (laptop; checks every input)
    2. python tranche2_02_score_prefilter.py ...        (GPU, e.g. Colab; BART-MNLI)
    3. python tranche2_03_allocate.py                   (laptop; hit rates and allocation)
    4. python tranche2_04_draw.py                       (laptop; draw, key, workbooks)
Optional, at any time: python tranche2_gate_null_simulation.py   (where the gate's bar comes from)

Paths are set ONCE, in the CONFIGURATION block below. Nothing else needs editing.
Frozen values further down come from R1, R5, Deviation 10 and the tranche 1 files;
they are checked, never recomputed.
"""
from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def _find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for folder in (here, *here.parents):
        if (folder / "docs" / "analysis_preregistration.md").exists():
            return folder
    return here


REPO = _find_repo_root()

# =============================================================================
# CONFIGURATION - edit this block only
# =============================================================================
# Corpus v2.2 (R5: data/clean_v2_2/). Parquet or CSV.
CORPUS_PATH = REPO / "data" / "clean_v2_2" / "corpus.parquet"

# Frozen draw frame, one comment id per line (R5).
FRAME_IDS_PATH = REPO / "data" / "frozen" / "draw_frame_ids.txt"

# Completed tranche 1 sheets (.xlsx or .csv) and the tranche 1 master key.
TRANCHE1_SHEETS = {
    "A": REPO / "data" / "annotation" / "tranche1_annotator_A.csv",
    "B": REPO / "data" / "annotation" / "tranche1_annotator_B.csv",
    "C": REPO / "data" / "annotation" / "tranche1_annotator_C.csv",
}
TRANCHE1_KEY = REPO / "data" / "annotation" / "tranche1_master_key.csv"

# File(s) holding the 30 calibration ids: .txt (one id per line), or .csv/.xlsx
# with an id column. The three annotators have seen and discussed these items,
# so they are excluded from the tranche 2 draw. Every id must be found in the corpus.
CALIBRATION_ID_FILES = [
    REPO / "data" / "annotation" / "calibration_annotator_A.csv",
]
CALIBRATION_N = 30          # set to None only if the calibration round was not 30 items

# Where tranche 2 files are written. Contains comment text and the researcher-only
# key: keep it out of the public repository.
OUT_DIR = REPO / "data" / "tranche2"

# Corpus column names. None = detect automatically; set a name to force it.
COL_ID = None               # detected as the column that contains every frame id
COL_TEXT = "clean_body"     # R5: the text annotators and models see
COL_SUBREDDIT = None
COL_CREATED = None

# Subsystem columns in the tranche 2 workbooks (Deviation 10): two columns beside the
# Stage 2 class, hidden until the annotator has finished Stage 1 and Stage 2.
# False would give the same sheet as tranche 1, with subsystem labels collected later.
INCLUDE_SUBSYSTEM_COLUMNS = True

# Safety overrides. Leave False unless a check stops you and you have recorded why.
ALLOW_TEXT_MISMATCH = False
ALLOW_TRANCHE1_LABEL_MISMATCH = False
ALLOW_OTHER_PREFILTER_SPEC = False      # scores made with a different model or wording than the committed script
ALLOW_CALIBRATION_IDS_NOT_IN_CORPUS = False   # only if a calibration item was later removed from the corpus
# =============================================================================

# ---- frozen values (R1, R5, Deviation 10, tranche 1 files). Do not edit. -------
SEED = 24916660
TRANCHE = 2
FRAME_N = 12166
FRAME_SHA256 = "ce85a3b046fedf3648861d446832a364ab89e7b60a0e58f10272b33b1997d7b3"
CORPUS_N = 12776
CORPUS_SHA256 = "d187adac10d98ccda1f0145713139f008705349ea6e0b4921092b1ad099559d4"
TRANCHE1_N = 500
# Membership hash of the 500 tranche 1 ids (recorded in the brief as 8b214a96...4eb15c).
TRANCHE1_SHA256 = "8b214a961f3419fb14b2fb246b4a8e1cf91d94a05ef0f8d55404ee61594eb15c"
# One label per tranche 1 item: gold (Deviation 2) for the 100 reliability items,
# the single rating otherwise.
TRANCHE1_EXPECTED_COUNTS = {"N": 203, "CONCERN": 120, "ENDORSEMENT": 95, "OTHER": 82}
# SHA-256 of the lines "id:label", sorted by id, newline-joined, no trailing newline.
TRANCHE1_LABELS_SHA256 = "d6f4eeeaf756831c3ba2a3165a7a548505d75a315b4f06069b9cf8ce580cd8d7"
# File hashes recorded in docs/decision_register.md on 26 September 2026 (reported, not
# enforced: a re-saved workbook has a different hash, but its labels must still match).
TRANCHE1_RECORDED_FILE_SHA256 = {
    "A": "2fe9b29ff2fb3298c4581e2bb79de711b4713abc40cdd065f2070ca0be39e50e",
    "B": "e80439ae671a21c69ffe5307cdebcf96b16bb33599015361304bff3dc71b4c04",
    "C": "4ec6a12a215edb3c4a0c2ac86d92c7871de0fa88ea84fc50d25cdf2f239ba6f6",
    "key": "ce50173525fd7ac74a3d720bf5f1a395b131066383f5c121002eb7dfc357755f",
}

TRANCHE2_N = 500
RELIABILITY_N = 100
RANDOM_POOL_N = 500
# Deviation 10: the draw goes ahead only if the rule's expected smallest final class
# count is at least this. A second natural tranche would be expected to leave the
# smallest class near 164 (twice its tranche 1 count). With predicted labels unrelated
# to the tranche 1 labels the figure averages about 178 and rarely reaches 200; see
# tranche2_gate_null_simulation.py.
GATE_MIN_EXPECTED_SMALLEST = 200
ANNOTATORS = ["A", "B", "C"]
CLASSES = ["CONCERN", "ENDORSEMENT", "OTHER"]
LABELS = ["N"] + CLASSES
SUBSYSTEMS = ["sensing", "in_vehicle_networks", "v2x", "cybersecurity", "privacy", "data_governance"]

TIER_OF = {
    "teslamotors": "Tier 1", "selfdrivingcars": "Tier 1", "realtesla": "Tier 1", "waymo": "Tier 1",
    "electricvehicles": "Tier 2", "cars": "Tier 2", "futurology": "Tier 2", "technology": "Tier 2",
    "privacy": "Tier 3", "cybersecurity": "Tier 3",
}

# Sub-streams of the frozen seed, so that each random step is independent of the others.
# Generator = numpy.random.default_rng([SEED, TRANCHE, component]).
RNG_COMPONENT = {
    "draw_CONCERN": 0, "draw_ENDORSEMENT": 1, "draw_OTHER": 2,
    "reliability": 3, "assignment": 4,
    "order_A": 5, "order_B": 6, "order_C": 7,
    "random_pool": 8,
}

# ---- output file names ---------------------------------------------------------
PREFILTER_INPUT = OUT_DIR / "prefilter_input.csv"
PREFILTER_INPUT_MANIFEST = OUT_DIR / "prefilter_input_manifest.json"
CALIBRATION_RESOLVED = OUT_DIR / "calibration_ids_resolved.txt"
PREFILTER_SCORES = OUT_DIR / "prefilter_scores.csv"
PREFILTER_SCORES_MANIFEST = OUT_DIR / "prefilter_scores_manifest.json"
ALLOCATION_JSON = OUT_DIR / "tranche2_allocation.json"
HIT_RATES_CSV = OUT_DIR / "tranche2_hit_rates.csv"
MASTER_KEY = OUT_DIR / "tranche2_master_key.csv"
RANDOM_POOL_IDS = OUT_DIR / "tranche2_random_pool_ids.txt"
DRAW_MANIFEST = OUT_DIR / "tranche2_manifest.json"
# Register text holding the measured figures.
SEALED_ALLOCATION_TEXT = OUT_DIR / "SEALED_step3_register_figures.txt"
SEALED_DRAW_TEXT = OUT_DIR / "SEALED_step4_register_figures.txt"
# The lines to paste into docs/decision_register.md after steps 3 and 4. They hold
# file hashes and the gate result only, so these two files are safe to open.
PASTE_STEP3 = OUT_DIR / "PASTE_step3_register_block.txt"
PASTE_STEP4 = OUT_DIR / "PASTE_step4_register_block.txt"

SEALED_NOTICE = (
    "SEALED until all three sheets are returned, their hashes are recorded and any Deviation 2\n"
    "adjudication is entered. Do not open: prefilter_scores.csv, prefilter_scores_manifest.json,\n"
    "tranche2_allocation.json, tranche2_hit_rates.csv, tranche2_master_key.csv, tranche2_manifest.json,\n"
    "the two SEALED_*.txt files, or another annotator's workbook.")


def workbook_path(annotator: str) -> Path:
    return OUT_DIR / f"tranche2_annotator_{annotator}.xlsx"


# =============================================================================
# small utilities
# =============================================================================
def setup_console() -> None:
    """Windows consoles default to cp1252; never let a stray character stop a run."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def stop(message: str) -> None:
    print("\nSTOPPED: " + message)
    sys.exit(1)


def rng(component: str) -> np.random.Generator:
    return np.random.default_rng([SEED, TRANCHE, RNG_COMPONENT[component]])


def ids_sha256(ids) -> str:
    """Membership hash used throughout the project: sorted ids, newline-joined, no trailing newline."""
    return hashlib.sha256("\n".join(sorted(str(i) for i in ids)).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def versions() -> dict:
    out = {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__}
    try:
        import openpyxl
        out["openpyxl"] = openpyxl.__version__
    except Exception:
        pass
    return out


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")


def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def show_register_block(path: Path, lines: list[str]) -> None:
    """Print the lines that go into the decision register, and write the same lines to a
    small text file so that they can be copied from an editor instead of the terminal."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        where = f"The same lines are in {path.name} (safe to open): copy them from that file."
    except OSError as e:                    # the results above are complete; only this convenience copy failed
        where = f"Could not write {path.name} ({e}). Copy the lines below from this window instead."
    bar = "=" * 78
    print("\n" + bar)
    print("PASTE NOW into docs/decision_register.md (hashes only; nothing here reveals the class mix).")
    print(where)
    print(bar)
    print("\n".join(lines))
    print(bar)


def norm_ws(text: str) -> str:
    return " ".join(str(text).split())


# Characters that cannot be stored in a workbook (XML 1.0) or survive a CSV round trip.
_UNSHOWABLE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]")


def shown_text(text: str) -> str:
    """The text the model scores and the annotators read: the corpus text with unshowable
    control characters removed. Identical for both, so what is annotated is what was scored."""
    return _UNSHOWABLE.sub("", str(text))


EXCEL_CELL_LIMIT = 32767


def excel_len(text: str) -> int:
    """Length as Excel counts it (UTF-16 code units), for the workbook cell limit."""
    return len(str(text).encode("utf-16-le", errors="surrogatepass")) // 2


def _cell(value) -> str:
    """Spreadsheet cell -> clean string. Empty cells become ''."""
    if value is None:
        return ""
    if isinstance(value, float):
        if np.isnan(value):
            return ""
        if value.is_integer():
            return str(int(value))
    return str(value).strip()


def read_table(path: Path) -> pd.DataFrame:
    """Read .xlsx / .csv / .parquet."""
    path = Path(path)
    if not path.exists():
        stop(f"file not found: {path}\n  Set the path in the CONFIGURATION block of tranche2_common.py.")
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm"):
        df = pd.read_excel(path, dtype=object, keep_default_na=False)
    elif suffix == ".csv":
        df = pd.read_csv(path, dtype=object, keep_default_na=False, encoding="utf-8-sig")
    elif suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        stop(f"unsupported file type: {path}")
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
    df.columns = [str(c).strip() for c in df.columns]
    return df


def read_string_table(path: Path) -> pd.DataFrame:
    df = read_table(path)
    return pd.DataFrame({c: [_cell(v) for v in df[c].tolist()] for c in df.columns})


def read_lines(path: Path) -> list[str]:
    path = Path(path)
    if not path.exists():
        stop(f"file not found: {path}\n  Set the path in the CONFIGURATION block of tranche2_common.py.")
    with open(path, "r", encoding="utf-8-sig") as f:
        return [line.strip() for line in f if line.strip()]


# =============================================================================
# frame, corpus, calibration
# =============================================================================
def load_frame() -> list[str]:
    ids = read_lines(FRAME_IDS_PATH)
    if len(ids) != len(set(ids)):
        stop("the frame id list contains duplicate ids")
    if len(ids) != FRAME_N:
        stop(f"frame has {len(ids):,} ids; R5 fixes {FRAME_N:,}")
    digest = ids_sha256(ids)
    if digest != FRAME_SHA256:
        stop(f"frame membership SHA-256 is {digest}\n  R5 fixes {FRAME_SHA256}")
    print(f"frame: {len(ids):,} ids, membership SHA-256 matches R5")
    return sorted(ids)


def era_of(year: int) -> str:
    if 2016 <= year <= 2018:
        return "2016-2018"
    if 2019 <= year <= 2021:
        return "2019-2021"
    if 2022 <= year <= 2025:
        return "2022-2025"
    return "outside window"


def parse_created(col: pd.Series) -> pd.Series:
    """Creation time as UTC datetimes, from datetimes, ISO strings or epoch seconds/milliseconds."""
    if pd.api.types.is_datetime64_any_dtype(col):
        return pd.to_datetime(col, utc=True)
    numeric = pd.to_numeric(col, errors="coerce")
    if numeric.notna().all():
        unit = "ms" if float(numeric.median()) > 1e11 else "s"
        return pd.to_datetime(numeric, unit=unit, utc=True)
    try:
        return pd.to_datetime(col.astype(str), utc=True, format="ISO8601")
    except Exception:
        return pd.to_datetime(col.astype(str), utc=True, format="mixed")


def _pick(df: pd.DataFrame, forced, candidates, what: str) -> str:
    if forced is not None:
        if forced not in df.columns:
            stop(f"corpus has no column `{forced}` for {what}. Columns: {list(df.columns)}\n"
                 f"  Set the right name in the CONFIGURATION block of tranche2_common.py.")
        return forced
    for c in candidates:
        if c in df.columns:
            return c
    stop(f"could not find the corpus column for {what}. Columns: {list(df.columns)}\n"
         f"  Set it in the CONFIGURATION block of tranche2_common.py.")


def load_corpus(frame_ids: list[str]):
    """Return (frame items as a table with id, text, subreddit, year, era, tier; set of all corpus ids)."""
    raw = read_table(CORPUS_PATH)
    frame = set(frame_ids)

    # id column: the one that contains every frame id
    if COL_ID is not None:
        id_col = _pick(raw, COL_ID, [], "the comment id")
    else:
        id_col = None
        preferred = ["id", "comment_id", "parsedId", "parsed_id", "commentId"]
        others = [c for c in raw.columns if c not in preferred]
        for c in [c for c in preferred if c in raw.columns] + others:
            try:
                values = set(raw[c].astype(str))
            except Exception:
                continue
            if frame <= values:
                id_col = c
                break
        if id_col is None:
            stop(f"no corpus column contains all {FRAME_N:,} frame ids. Columns: {list(raw.columns)}\n"
                 f"  Check CORPUS_PATH points at corpus v2.2, or set COL_ID.")
    text_col = _pick(raw, COL_TEXT, [], "the comment text")
    sub_col = _pick(raw, COL_SUBREDDIT, ["subreddit", "parsedCommunityName", "communityName", "community"], "the subreddit")
    created_col = _pick(raw, COL_CREATED, ["created", "createdAt", "created_at", "created_utc", "timestamp"], "the creation time")
    print(f"corpus: {len(raw):,} rows | id=`{id_col}` text=`{text_col}` subreddit=`{sub_col}` created=`{created_col}`")

    ids_all = raw[id_col].astype(str)
    if ids_all.duplicated().any():
        stop("the corpus id column contains duplicate ids")
    if len(raw) == CORPUS_N:
        digest = ids_sha256(ids_all)
        if digest != CORPUS_SHA256:
            stop(f"corpus membership SHA-256 is {digest}\n  R5 fixes {CORPUS_SHA256} for v2.2")
        print(f"corpus: {CORPUS_N:,} rows, membership SHA-256 matches R5 (v2.2)")
    else:
        print(f"NOTE: corpus file has {len(raw):,} rows, not the {CORPUS_N:,} of v2.2; membership hash not checked. "
              f"Every frame id is present.")

    df = raw.loc[ids_all.isin(frame)].copy()
    if df[text_col].isna().any():
        stop("some frame items have no text in the corpus")
    created = parse_created(df[created_col])
    if created.isna().any():
        stop(f"{int(created.isna().sum())} frame items have no usable creation time in column `{created_col}`. "
             f"Set COL_CREATED in the CONFIGURATION block.")
    sub = df[sub_col].astype(str).str.strip().str.replace(r"^/?r/", "", regex=True)
    raw_text = df[text_col].astype(str)
    out = pd.DataFrame({
        "id": df[id_col].astype(str).to_numpy(),
        "text": raw_text.map(shown_text).to_numpy(),
        "text_altered": (raw_text.map(shown_text) != raw_text).to_numpy(),
        "subreddit": sub.to_numpy(),
        "year": created.dt.year.astype(int).to_numpy(),
    })
    out["era"] = out["year"].map(era_of)
    out["tier"] = out["subreddit"].str.lower().map(TIER_OF).fillna("unknown")
    out = out.sort_values("id").reset_index(drop=True)
    if len(out) != FRAME_N:
        stop(f"{len(out):,} frame items found in the corpus; expected {FRAME_N:,}")
    if (out["text"].str.strip() == "").any():
        stop("some frame items have empty text in the corpus")
    return out, set(ids_all)


def resolve_calibration(frame_ids: list[str], corpus_ids: set) -> list[str]:
    """Read the calibration ids and fail closed: every id must exist in the corpus id column.

    A file whose ids are in another format (a prefix, different case) would otherwise exclude
    nothing and let calibration items into the draw."""
    if not CALIBRATION_ID_FILES:
        stop("CALIBRATION_ID_FILES is empty. The calibration items were seen and discussed by all three "
             "annotators and must be excluded from the tranche 2 draw. Point it at the file holding their ids.")
    ids: set[str] = set()
    for path in CALIBRATION_ID_FILES:
        path = Path(path)
        if path.suffix.lower() == ".txt":
            found = read_lines(path)
        else:
            df = read_string_table(path)
            candidates = [c for c in ("id", "comment_id", "parsedId", "parsed_id", "commentId") if c in df.columns]
            if not candidates:
                stop(f"{path} has no id column (columns: {list(df.columns)})")
            found = None
            for col in candidates:
                values = [v for v in df[col].tolist() if v]
                if values and set(values) <= corpus_ids:
                    found = values
                    break
            if found is None and ALLOW_CALIBRATION_IDS_NOT_IN_CORPUS:
                found = [v for v in df[candidates[0]].tolist() if v]
            if found is None:
                stop(f"no id column in {path} holds ids that are all in the corpus (tried {candidates}).\n"
                     f"  The calibration ids must be in the same form as the corpus ids.")
        missing = sorted(set(found) - corpus_ids)
        if missing and not ALLOW_CALIBRATION_IDS_NOT_IN_CORPUS:
            stop(f"{len(missing)} calibration id(s) in {path} are not in the corpus, e.g. {missing[:5]}.\n"
                 f"  They must be in the same form as the corpus ids, or they would not be excluded.")
        if missing:
            print(f"NOTE: {len(missing)} calibration id(s) are not in the corpus (override in force): {missing}")
        ids |= set(found)
    if CALIBRATION_N is not None and len(ids) != CALIBRATION_N:
        stop(f"{len(ids)} distinct calibration ids found; expected {CALIBRATION_N}. Check CALIBRATION_ID_FILES.")
    in_frame = ids & set(frame_ids)
    print(f"calibration: {len(ids)} ids, all found in the corpus; {len(in_frame)} are in the frame and are excluded")
    return sorted(ids)


def step1_manifest() -> dict:
    if not PREFILTER_INPUT_MANIFEST.exists() or not CALIBRATION_RESOLVED.exists():
        stop("run step 1 first (tranche2_01_export_prefilter_input.py).")
    return read_json(PREFILTER_INPUT_MANIFEST)


def load_resolved_calibration(manifest: dict) -> list[str]:
    """The calibration ids as validated and frozen by step 1."""
    ids = read_lines(CALIBRATION_RESOLVED)
    if ids_sha256(ids) != manifest["calibration_ids_sha256"]:
        stop("calibration_ids_resolved.txt does not match the hash step 1 recorded. Run step 1 again.")
    return sorted(ids)


def eligible_ids(frame_ids: list[str], tranche1_ids, calibration_ids, manifest: dict | None = None) -> list[str]:
    excluded = set(tranche1_ids) | set(calibration_ids)
    out = sorted(i for i in frame_ids if i not in excluded)
    if manifest is not None and ids_sha256(out) != manifest["eligible_ids_sha256"]:
        stop("the eligible items differ from those step 1 recorded. Run step 1 again and record why they changed.")
    return out


# =============================================================================
# tranche 1: ratings, key and one label per item
# =============================================================================
SHEET_COLUMNS = ["row", "id", "subreddit", "comment", "stage1_relevant", "stage2_class", "skip", "notes"]


def load_tranche1(verbose: bool = True):
    """Return (key, ratings_long, item_labels).

    item_labels: one label in {N, CONCERN, ENDORSEMENT, OTHER} per tranche 1 item:
    the gold label (Deviation 2: majority of three) for reliability items, and the
    assigned annotator's rating otherwise.
    """
    key = read_string_table(TRANCHE1_KEY)
    need = {"id", "era", "subreddit", "weight", "is_reliability", "assigned_to"}
    if not need <= set(key.columns):
        stop(f"tranche 1 master key lacks columns {sorted(need - set(key.columns))}")
    if len(key) != TRANCHE1_N or key["id"].duplicated().any():
        stop(f"tranche 1 master key has {len(key)} rows / duplicate ids; expected {TRANCHE1_N} distinct ids")
    digest = ids_sha256(key["id"])
    if digest != TRANCHE1_SHA256:
        stop(f"tranche 1 membership SHA-256 is {digest}\n  expected {TRANCHE1_SHA256}")
    key["weight"] = key["weight"].astype(float)
    key["is_reliability"] = key["is_reliability"].str.lower().map({"true": True, "false": False})
    if key["is_reliability"].isna().any():
        stop("tranche 1 master key: is_reliability must be True/False")
    key = key.set_index("id")
    rel_ids = set(key.index[key["is_reliability"]])

    frames = []
    for a, path in TRANCHE1_SHEETS.items():
        df = read_string_table(path)
        missing = [c for c in SHEET_COLUMNS if c not in df.columns]
        if missing:
            stop(f"tranche 1 sheet {a} lacks columns {missing}")
        df = df[SHEET_COLUMNS].copy()
        df = df[df["id"] != ""]
        df["annotator"] = a
        frames.append(df)
    long = pd.concat(frames, ignore_index=True)

    # vocabulary and structure
    problems = []
    for r in long.itertuples():
        if r.skip != "":
            problems.append(f"{r.annotator}/{r.id}: skip is set (none are recorded for tranche 1)")
        if r.stage1_relevant not in ("Y", "N"):
            problems.append(f"{r.annotator}/{r.id}: stage1_relevant={r.stage1_relevant!r}")
        elif r.stage1_relevant == "N" and r.stage2_class != "":
            problems.append(f"{r.annotator}/{r.id}: stage2_class present where stage1 is N")
        elif r.stage1_relevant == "Y" and r.stage2_class not in CLASSES:
            problems.append(f"{r.annotator}/{r.id}: stage2_class={r.stage2_class!r}")
    if problems:
        stop("tranche 1 sheets fail validation:\n  " + "\n  ".join(problems[:20]))
    per_item = long.groupby("id")["annotator"].agg(lambda s: "".join(sorted(s)))
    if set(per_item.index) != set(key.index):
        stop("the ids in the tranche 1 sheets are not the 500 ids in the master key")
    if long.duplicated(["id", "annotator"]).any():
        stop("an id appears twice in one tranche 1 sheet")
    for i, who in per_item.items():
        if i in rel_ids and who != "ABC":
            stop(f"reliability item {i} is not in all three sheets")
        if i not in rel_ids and who != key.at[i, "assigned_to"]:
            stop(f"item {i} is assigned to {key.at[i, 'assigned_to']!r} but appears in sheet(s) {who}")
    if len(long) != 700 or len(rel_ids) != 100:
        stop(f"expected 700 ratings and 100 reliability items; found {len(long)} and {len(rel_ids)}")

    long["label"] = np.where(long["stage1_relevant"] == "N", "N", long["stage2_class"])
    labels = {}
    unresolved = []
    for i, g in long.groupby("id"):
        if i not in rel_ids:
            labels[i] = g["label"].iloc[0]
            continue
        votes = g["label"].tolist()
        yes = [v for v in votes if v != "N"]
        if len(yes) < 2:                       # Stage 1 majority: not relevant
            labels[i] = "N"
            continue
        top, n = Counter(yes).most_common(1)[0]
        if n >= 2:                             # Stage 2 majority among those who rated it relevant
            labels[i] = top
        else:                                  # Deviation 2: resolved by the author, never by code
            unresolved.append(f"{i}: {votes}")
    if unresolved:
        stop("these reliability items have no majority and need adjudication under Deviation 2:\n  "
             + "\n  ".join(unresolved))
    item_labels = pd.Series(labels).reindex(key.index)
    counts = {k: int((item_labels == k).sum()) for k in LABELS}
    digest = hashlib.sha256("\n".join(f"{i}:{item_labels[i]}" for i in sorted(item_labels.index)).encode("utf-8")).hexdigest()
    if verbose:
        print(f"tranche 1: 500 items, 700 ratings, 100 reliability items | labels {counts}")
    if (counts != TRANCHE1_EXPECTED_COUNTS or digest != TRANCHE1_LABELS_SHA256) and not ALLOW_TRANCHE1_LABEL_MISMATCH:
        stop(f"the tranche 1 labels on disk are not the labels the register describes "
             f"(counts {counts}; expected {TRANCHE1_EXPECTED_COUNTS}; per-item fingerprint "
             f"{'matches' if digest == TRANCHE1_LABELS_SHA256 else 'differs'}).\n"
             f"  Restore the completed sheets recorded on 26 September 2026.")
    if verbose:
        print("tranche 1: every item's label matches the recorded fingerprint")
    return key, long, item_labels


def tranche1_file_hashes(verbose: bool = True) -> dict:
    found = {a: file_sha256(p) for a, p in TRANCHE1_SHEETS.items()}
    found["key"] = file_sha256(TRANCHE1_KEY)
    same = {k: found[k] == TRANCHE1_RECORDED_FILE_SHA256[k] for k in found}
    if verbose:
        if all(same.values()):
            print("tranche 1 files: all four match the SHA-256 values recorded in the register")
        else:
            differ = [k for k, v in same.items() if not v]
            print(f"NOTE: tranche 1 file(s) {differ} differ byte-for-byte from the files recorded in the register "
                  f"(for example a re-save). Every label still matches the recorded fingerprint.")
    return {"sha256": found, "matches_register": same}


def check_text_against_tranche1(corpus: pd.DataFrame, long: pd.DataFrame) -> dict:
    """The corpus text for the 500 tranche 1 items should be the text the annotators were shown."""
    text = dict(zip(corpus["id"], corpus["text"]))
    exact = repaired = different = 0
    for i, g in long.groupby("id"):
        target = norm_ws(text[i])
        shown = [norm_ws(t) for t in g["comment"]]
        if target in shown:
            exact += 1
            continue
        fixed = []
        for s in shown:                        # annotator C's sheet: Mac Roman mis-decoding (see register)
            try:
                fixed.append(norm_ws(s.encode("mac_roman").decode("utf-8")))
            except Exception:
                pass
        if target in fixed:
            repaired += 1
        else:
            different += 1
    result = {"identical": exact, "identical_after_encoding_repair": repaired, "different": different}
    print(f"text check against the tranche 1 sheets: {result}")
    if different > 50 and not ALLOW_TEXT_MISMATCH:
        stop(f"the corpus text differs from what annotators saw for {different} of 500 tranche 1 items.\n"
             f"  COL_TEXT (`{COL_TEXT}`) is probably not the column tranche 1 was built from.")
    return result
