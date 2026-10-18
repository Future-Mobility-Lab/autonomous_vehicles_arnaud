"""Calibration agreement and the cost break-even (on the PC): Krippendorff's alpha of the 30-item calibration round
(R2), the annotation time estimated from the calibration sheets, the cost break-even of design decision D17 and the
project's spend, from the files of record, so that no figure in them is typed by hand.

From the repository folder, with the virtual environment active (no GPU, no internet):
    python analysis_05_calibration_cost.py --preflight
        Before the commit. Checks every input against the record, then builds every figure, table and file in memory
        and discards them. It writes no output (matplotlib may refresh its cache).
    python analysis_05_calibration_cost.py --confirm-committed
        After this file is committed and its SHA-256 recorded. The run of record. It runs once: it refuses to start
        if this file's outputs already exist (the SHA-256 is that of the file with LF line endings, as the register
        records script hashes).

Inputs, each checked against its SHA-256 of record before it is read: the data files as their bytes stand, as the
register fingerprints data files, and the repository text files with LF line endings (a checkout that turned them
into CRLF changes nothing that is read). Nothing else is read and no repository module is imported.
  data/annotation/calibration_annotator_A_filled.xlsx   the calibration sheets as A, B and C completed them
  data/annotation/calibration_annotator_B_filled.csv    (September 2026), fingerprinted on 17 October 2026, when
  data/annotation/calibration_annotator_C_filled.csv    they were copied into the repository folder (B's sheet as
                                                         it stood on 19 October: other bytes, the same content;
                                                         see the register)
  data/annotation/calibration_review_sheet_filled.csv   the review sheet (R2): the three labels, the disagreement, its
                                                         cause, the agreed label
  results/sample_results.json                            the sample analyses of record (14 October 2026): the ratings
                                                         of each tranche
  data/models/evaluation/evaluation_results.json         the evaluation of record (11 October 2026): the deployed
                                                         Stage 2 configuration, its cost per 1,000 comments, macro-F1
                                                         (read with LF line endings, as analysis_04_tables.py reads
                                                         it, although it is under data/)
  data/models/deploy/stage2_manifest.json                the Stage 2 corpus run of record (15 October 2026): its
                                                         comments and its cost
  docs/cost_inputs.json                                  committed with this file: the card charges in Australian
                                                         dollars, the Anthropic credit, the Colab position and the
                                                         hourly rate with its source

Rules fixed with this file
  1. The calibration sheets. Each has the twelve columns of draw_calibration.py (empty cells after the twelfth are
     ignored) and 30 rows; the four sheets hold the same 30 ids, whose membership SHA-256 (the ids sorted and joined
     by a newline, no newline at the end) is the one in data/frozen/calibration_manifest.txt. A skip cell is blank,
     or Y, YES, X, SKIP, SKIPPED, TRUE or 1, which make the rating missing: nothing else on a missing rating is
     read. On every other rating, relevance is Y or N and a class CONCERN, ENDORSEMENT or OTHER (case and
     surrounding spaces ignored); a time is a finite number of seconds, at least zero, or blank. Anything else stops
     the script. The missing ratings are counted for each annotator and reported.
  2. Agreement. Krippendorff's alpha, nominal, computed exactly as the evaluation of record computes it (the
     function alpha_exact of models_05_evaluate.py, copied unchanged): Stage 1 on the relevance ratings of the 30
     items; Stage 2 on the classes of the ratings marked relevant (a class given with N is not a value, and a Y
     without a class gives none); each class against the rest on the Stage 2 values. Only items with at least two
     values count (the units). R2's branch follows mechanically: alpha at least 0.7 at both stages means "proceed
     context-free, unchanged"; otherwise the branch of the plurality cause among the disagreements is named.
  3. Disagreements, from the three sheets: at Stage 1 where the relevance ratings differ; at Stage 2 where the
     relevance ratings are all Y and the classes given differ. The review sheet holds the same 30 ids; its
     disagreement is none, stage1 or stage2, its cause blank, a, b or c, and its codebook flag Y or N (or blank
     where the disagreement is none); anything else stops the script. Its disagreements, causes and agreed labels are
     counted as recorded and compared with the sheets; every difference is reported as a count, and no comment
     identifier is written in any output.
  4. Times. For each annotator and stage, the seconds recorded on the ratings made at that stage: Stage 1 every
     rating that is not missing, Stage 2 the ratings marked Y with a class, the subsystem the ratings marked Y with a
     subsystem label. Seconds recorded where that stage has no rating are counted and not used. The seconds per
     rating of a stage is the mean over the annotators of each annotator's mean; an annotator with no times at that
     stage is left out of it.
  5. Annotation time. The ratings of each tranche, from the sample analyses of record: relevance ratings are the
     sheet items rated (tranche 1) and the single-rated items plus the 100 reliability items each annotator rated
     (tranche 2); stance and subsystem ratings are the ratings with a primary subsystem label in each tranche, which
     in tranche 1 are every rating coded relevant and in tranche 2 leave out the few relevant ratings without a
     subsystem label. Hours = ratings x seconds per rating / 3,600. The calibration round's own time is the seconds
     recorded on its sheets, with a missing time filled with the seconds per rating of its stage. The estimate
     counts time on the items only, so it is a floor: no reading of the codebook, no set-up, no breaks.
  6. Cost (D17). The deployed Stage 2 configuration's cost per comment is the corpus run's cost divided by its
     comments, with the evaluation's cost per 1,000 comments beside it. Australian dollars per US dollar of credit
     are the Anthropic card charges in Australian dollars divided by the credit bought in US dollars, so they
     include what the card was charged above the credit. Incremental accounting: the annotated set is needed to
     evaluate any classifier, so it is not charged to fine-tuning, which then costs A$0 per comment (its GPU time
     carried no separate charge and it makes no API call). Full accounting: all relevance and stance labelling,
     calibration included, is charged to fine-tuning at the hourly rate; subsystem labelling serves RQ2, not the
     Stage 2 comparison, and is reported, not charged. The break-even is the number of Stage 2 comments at which
     the zero-shot cost equals that labelling cost; it is proportional to the rate, so it is also given per A$10 an
     hour. No on-cost is added to the rate. Beside the cost, the accuracy of record: the pooled macro-F1 of the
     deployed configuration and of the better of the two fine-tuned configurations (DistilBERT, RoBERTa), which must
     have been evaluated on the same number of items.
  7. Budget: the card charges by line in Australian dollars as charged, the Colab line at A$0, and their total; with
     the Anthropic credit bought, used and unused as recorded in docs/cost_inputs.json.
  8. Formats, in the tables, the report and the figure: Australian dollars to the cent; costs per 1,000 comments to
     three decimals; seconds and hours to one decimal (the calibration round's hours, in the report, to two); alpha
     to three decimals, or to as many as it takes to tell it from 0.7 when three would show 0.700; rates of exchange
     to four decimals; the break-even to the nearest 1,000 comments. Rounding is half to even, from exact fractions.
     The results file gives every figure as an exact fraction beside a decimal (six places; alpha four).
  9. The figure (matplotlib, Agg backend, with matplotlib's default settings restored first): the cost of each
     approach against the number of Stage 2 comments on linear axes, from zero to twice the break-even (or to 1.15
     times the corpus run, if that is larger), with the break-even marked and an arrow to the corpus run. No
     smoothing and no fitted line; the PDF carries no creation date and the PNG no software stamp.

Writes, in data/analysis/calibration_cost/run_<first 12 hex digits of this file's SHA-256>/ (data/ is not committed):
  calibration_cost_results.json    every figure, exact fractions beside the decimals
  calibration_cost_report.md       the same, readable
  tables/calibration.tex           calibration agreement, disagreements, causes and R2's branch
  tables/cost.tex                  the cost break-even and its inputs
  tables/budget.tex                the spend by line
  figures/cost_breakeven.pdf, .png the cost of each approach against the number of Stage 2 comments
  calibration_cost_manifest.json   time, versions, the SHA-256 of every input and output
  PASTE_calibration_cost_block.txt the register lines (hashes only)
After the run, the results file and the report are copied to results/, the tables to results/report_tables/ and the
figures to results/report_figures/, and committed with the register lines.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import platform
import shutil
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation, localcontext
from fractions import Fraction
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

# =============================================================================
# THE RECORD
# =============================================================================
SCRIPT = "analysis_05_calibration_cost.py"
REPORT = "Report this message before going further."


def _find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for folder in (here, *here.parents):
        if (folder / "docs" / "analysis_preregistration.md").exists():
            return folder
    return here


REPO = _find_repo_root()
ANN = REPO / "data" / "annotation"
INPUTS = {   # name: (path, SHA-256 of record, "bytes" for a data file as it stands or "lf" for repository text)
    "calibration_annotator_A_filled.xlsx": (
        ANN / "calibration_annotator_A_filled.xlsx",
        "dbfef978c3d89fd00093cac22a4b92e65fecf81b9a0c9673f86e71a5cd9effbb", "bytes"),
    "calibration_annotator_B_filled.csv": (
        ANN / "calibration_annotator_B_filled.csv",
        "bc4a04e9d1f14eaf30efe9a515737c09ce511963f79f93c906f6f3ab100b3a16", "bytes"),
    "calibration_annotator_C_filled.csv": (
        ANN / "calibration_annotator_C_filled.csv",
        "af9f66c22cdb5b58f57720b6951eed2de0623944b07ceab21887d2f3f11b7f6e", "bytes"),
    "calibration_review_sheet_filled.csv": (
        ANN / "calibration_review_sheet_filled.csv",
        "acecb0ba873d9a3cc033f97d9dbc586ad7e15679a8875a5625b0863dd08a6134", "bytes"),
    "sample_results.json": (
        REPO / "results" / "sample_results.json",
        "be9db9a168e6d432d5f7b6190a7a204a624e1aa4992cd399cbb90288a383c5d7", "lf"),
    "evaluation_results.json": (
        REPO / "data" / "models" / "evaluation" / "evaluation_results.json",
        "411f6c23ef6525b077c74fec15b8e5a06c59c550a8f3f2d15e99eb7d354d32e4", "lf"),
    "stage2_manifest.json": (
        REPO / "data" / "models" / "deploy" / "stage2_manifest.json",
        "eafaefada3c07b02ebe14b5afa9c0e075585e7b86640184fe30e28f9d72462ef", "bytes"),
    "cost_inputs.json": (
        REPO / "docs" / "cost_inputs.json",
        "8c433df56a128ce522259c37fda3ac825071473b20e99c9f7ceb7096af03fac3", "lf"),
}
SHEETS = {"A": "calibration_annotator_A_filled.xlsx", "B": "calibration_annotator_B_filled.csv",
          "C": "calibration_annotator_C_filled.csv"}
REVIEW = "calibration_review_sheet_filled.csv"
CALIBRATION_MEMBERSHIP = "1302336e8ba478d4004fc9bd1d505d68f2d603706084bc36941d4f8c7f6ecbc2"
CALIBRATION_ITEMS = 30
SHEET_COLUMNS = ["row", "id", "subreddit", "comment", "stage1_relevant", "stage1_seconds", "stage2_class",
                 "stage2_seconds", "subsystem", "subsystem_seconds", "skip", "notes"]
REVIEW_COLUMNS = ["id", "label_A", "label_B", "label_C", "disagreement", "cause", "agreed_label",
                  "codebook_change_needed", "review_notes"]
ANNOTATORS = ["A", "B", "C"]
CLASSES = ["CONCERN", "ENDORSEMENT", "OTHER"]
STAGES = ["stage1", "stage2", "subsystem"]
SKIP_MARKS = ("Y", "YES", "X", "SKIP", "SKIPPED", "TRUE", "1")
STAGE_NAMES = {"stage1": "Relevance (Stage 1)", "stage2": "Stance (Stage 2)", "subsystem": "Subsystem"}
CAUSES = {"a": "missing context", "b": "codebook ambiguity", "c": "misapplication"}
R2_BRANCHES = {   # R2, docs/analysis_preregistration.md, word for word
    "pass": "proceed context-free, unchanged",
    "a": "the post title is added to the Stage 2 presentation for annotators, and the Stage 2 model comparison is "
         "run on title-plus-comment for all five models. Stage 1 remains blind in all cases, because comment-level "
         "topicality is the estimand",
    "b": "revise the codebook, re-run calibration on 30 fresh items, discard both rounds",
    "c": "retrain on the existing codebook, re-run calibration on 30 fresh items. No codebook change",
}
ALPHA_BAR = Fraction(7, 10)
RELIABILITY_ITEMS_PER_TRANCHE = 100        # R1; Deviation 11: each annotator rates the tranche's 100 reliability items
FINE_TUNED = ["distilbert", "roberta"]     # the fine-tuned Stage 2 configurations of the evaluation of record
API_LINE = "Model API (Anthropic credit)"
DEPLOYED_RUN = ("sonnet-domain", "claude-sonnet-4-6")   # Deviation 12's deployed configuration; Deviation 13's run
LIBRARIES = {"numpy": "2.5.1", "matplotlib": "3.11.2"}
RECORDED_ONLY = ["openpyxl"]               # its version is recorded, not pinned: it only reads the cell values
OUT_ROOT = REPO / "data" / "analysis" / "calibration_cost"
FIGURE_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
INK, GRID = "#333333", "#dddddd"


def col(width: str) -> str:
    """A ragged-right paragraph column of the given share of the line width (no column type of the report needed)."""
    return rf">{{\raggedright\arraybackslash}}p{{{width}\linewidth}}"


def rcol(width: str) -> str:
    return rf">{{\raggedleft\arraybackslash}}p{{{width}\linewidth}}"


# =============================================================================
# helpers
# =============================================================================
def setup_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:                                   # noqa: BLE001 - best effort only
            pass


def stop(message: str) -> None:
    print("\nSTOPPED: " + message, flush=True)
    sys.exit(1)


def lf_text(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError:
        stop(f"{path.name} is not UTF-8 text. {REPORT}")


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def own_sha256() -> str:
    return text_sha256(lf_text(Path(__file__).resolve()))


def run_folder(me: str) -> Path:
    return OUT_ROOT / f"run_{me[:12]}"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def replace_patiently(tmp: Path, path: Path) -> None:
    """On Windows a virus scanner or a sync client can hold a file for a moment: a refused move is tried again."""
    for attempt in range(20):
        try:
            tmp.replace(path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.5)


def json_text(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def show_register_block(path: Path, lines: list[str]) -> None:
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


def check_libraries() -> dict:
    found = {}
    for name in [*LIBRARIES, *RECORDED_ONLY]:
        try:
            found[name] = package_version(name)
        except PackageNotFoundError:
            found[name] = "not installed"
    pinned = {n: found[n] for n in LIBRARIES}
    if pinned != LIBRARIES:
        pins = " ".join(f"{n}=={v}" for n, v in LIBRARIES.items())
        stop(f"this file uses {', '.join(f'{n} {v}' for n, v in LIBRARIES.items())}; found "
             f"{', '.join(f'{n} {v}' for n, v in pinned.items())}.\n  Install them with:  python -m pip install {pins}")
    for n in RECORDED_ONLY:
        if found[n] == "not installed":
            stop(f"{n} is not installed; it reads calibration_annotator_A_filled.xlsx. {REPORT}")
    return found


class Input:
    """A JSON input with its name, so that a missing key stops the script with the key's full path."""

    def __init__(self, name: str, data):
        self.name, self.data = name, data

    def get(self, *path):
        x = self.data
        for k in path:
            if isinstance(x, dict) and k in x:
                x = x[k]
            elif isinstance(x, list) and isinstance(k, int) and -len(x) <= k < len(x):
                x = x[k]
            else:
                stop(f"{self.name} has no entry {'.'.join(str(p) for p in path)} (it stops at {k!r}). {REPORT}")
        return x


def load_inputs() -> tuple[dict, dict]:
    """Every input checked against its SHA-256 of record, then parsed; nothing is read before its check."""
    shas, raw = {}, {}
    for name, (path, want, kind) in INPUTS.items():
        if not path.exists():
            stop(f"{name} not found at {path}. {REPORT}")
        data = path.read_bytes()
        if kind == "bytes":
            got = hashlib.sha256(data).hexdigest()
        else:
            try:
                got = text_sha256(data.decode("utf-8").replace("\r\n", "\n"))
            except UnicodeDecodeError:
                stop(f"{name} is not UTF-8 text. {REPORT}")
        if got != want:
            stop(f"{name} is not the file of record (SHA-256 {got[:16]}..., recorded {want[:16]}...). {REPORT}")
        shas[name] = got
        raw[name] = data
    loaded = {}
    for name in ("sample_results.json", "evaluation_results.json", "stage2_manifest.json", "cost_inputs.json"):
        try:
            loaded[name] = Input(name, json.loads(raw[name].decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            stop(f"{name} could not be read as JSON ({e}). {REPORT}")
    loaded["sheets"] = {a: read_sheet(SHEETS[a], raw[SHEETS[a]]) for a in ANNOTATORS}
    loaded["review"] = read_table(REVIEW, raw[REVIEW], REVIEW_COLUMNS)
    return loaded, shas


# =============================================================================
# numbers
# =============================================================================
def num(x, what: str) -> Fraction:
    """An exact number from a JSON or a cell value: a decimal string, an int or a float as written."""
    if isinstance(x, bool):
        stop(f"{what}: a yes/no value where a number was expected. {REPORT}")
    if isinstance(x, int):
        return Fraction(x)
    d = None
    if isinstance(x, float):
        d = Decimal(repr(x))
    elif isinstance(x, str):
        try:
            d = Decimal(x.strip())
        except (InvalidOperation, ValueError):
            d = None
    if d is not None and d.is_finite():
        return Fraction(d)
    stop(f"{what}: {x!r} is not a number. {REPORT}")


def fixed(x: Fraction, places: int, sign: bool = False) -> str:
    """An exact fraction with the given decimals, half to even."""
    with localcontext() as ctx:
        ctx.prec = 60
        d = Decimal(x.numerator) / Decimal(x.denominator)
        out = d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_EVEN)
    s = f"{out:,.{places}f}"
    if out == 0:
        return s.lstrip("-")
    return ("+" + s) if sign and not s.startswith("-") else s


def nearest(x: Fraction, step: int) -> int:
    """x rounded to the nearest multiple of step, half to even."""
    q = x / step
    f = q.numerator // q.denominator
    rest = q - f
    if rest > Fraction(1, 2) or (rest == Fraction(1, 2) and f % 2 == 1):
        f += 1
    return int(f * step)


def fr(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def dec(x: Fraction, places: int = 6) -> float:
    return float(fixed(x, places).replace(",", ""))


def median(values: list[Fraction]) -> Fraction:
    v = sorted(values)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def mean(values: list[Fraction]) -> Fraction:
    return sum(values, Fraction(0)) / len(values)


# =============================================================================
# the calibration sheets (rule 1)
# =============================================================================
def cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def read_table(name: str, data: bytes, columns: list[str]) -> list[dict]:
    """A CSV file of record as a list of rows (dicts of stripped strings); its header must be exactly columns."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        stop(f"{name} is not UTF-8 text. {REPORT}")
    rows = [r for r in csv.reader(io.StringIO(text, newline="")) if any(c.strip() for c in r)]
    return table_rows(name, rows, columns)


def table_rows(name: str, rows: list[list], columns: list[str]) -> list[dict]:
    header = [cell(c) for c in rows[0]] if rows else []
    while header and header[-1] == "":
        header.pop()
    if header != columns:
        stop(f"{name}: the columns are not {', '.join(columns)}. {REPORT}")
    out = []
    for i, r in enumerate(rows[1:], start=2):
        r = [cell(c) for c in r]
        if len(r) > len(columns) and any(r[len(columns):]):
            stop(f"{name}, row {i}: more cells than columns. {REPORT}")
        r = (r + [""] * len(columns))[:len(columns)]
        out.append(dict(zip(columns, r)))
    return out


def read_sheet(name: str, data: bytes) -> list[dict]:
    if name.endswith(".xlsx"):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        try:
            rows = [list(r) for r in wb.worksheets[0].iter_rows(values_only=True)]
        finally:
            wb.close()
        rows = [r for r in rows if any(cell(c) for c in r)]
        return table_rows(name, rows, SHEET_COLUMNS)
    return read_table(name, data, SHEET_COLUMNS)


def membership(ids) -> str:
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def seconds(value: str, where: str) -> Fraction | None:
    if value == "":
        return None
    try:
        d = Decimal(value)
    except (InvalidOperation, ValueError):
        d = None
    if d is None or not d.is_finite():
        stop(f"{where}: {value!r} is not a number of seconds. {REPORT}")
    s = Fraction(d)
    if s < 0:
        stop(f"{where}: a negative time. {REPORT}")
    return s


def parse_sheets(sheets: dict) -> dict:
    """Each annotator's ratings by id: relevance, class, subsystem label, the three times, missing (rule 1)."""
    out = {}
    for a in ANNOTATORS:
        name = SHEETS[a]
        rows = sheets[a]
        if len(rows) != CALIBRATION_ITEMS:
            stop(f"{name} has {len(rows)} rows, not {CALIBRATION_ITEMS}. {REPORT}")
        ids = [r["id"] for r in rows]
        if len(set(ids)) != len(ids) or "" in ids:
            stop(f"{name}: an id is blank or repeated. {REPORT}")
        if membership(ids) != CALIBRATION_MEMBERSHIP:
            stop(f"{name} does not hold the 30 calibration items of record (membership SHA-256). {REPORT}")
        by = {}
        for i, r in enumerate(rows, start=2):
            where = f"{name}, row {i}"
            skip = r["skip"].upper()
            if skip not in ("", *SKIP_MARKS):
                stop(f"{where}: skip {r['skip']!r} is not blank or one of {', '.join(SKIP_MARKS)}. {REPORT}")
            if skip:
                by[r["id"]] = {"missing": True, "stage1": "", "class": "", "subsystem": "",
                               "t": {k: None for k in STAGES}}
                continue
            s1 = r["stage1_relevant"].upper()
            if s1 not in ("Y", "N"):
                stop(f"{where}: relevance {r['stage1_relevant']!r} is not Y or N. {REPORT}")
            c = r["stage2_class"].upper()
            if c and c not in CLASSES:
                stop(f"{where}: class {r['stage2_class']!r} is not one of {', '.join(CLASSES)}. {REPORT}")
            by[r["id"]] = {"missing": False, "stage1": s1, "class": c, "subsystem": r["subsystem"],
                           "t": {k: seconds(r[f"{k}_seconds"], f"{where}, {k}_seconds") for k in STAGES}}
        out[a] = by
    return out


def label_text(x: dict) -> str:
    """A rating as the review sheet writes it: N, or Y / CLASS (Y alone where no class was given); blank if missing."""
    if x["missing"]:
        return ""
    if x["stage1"] == "N":
        return "N"
    return "Y/" + x["class"] if x["class"] else "Y"


def norm_label(s: str) -> str:
    return "".join(s.upper().split())


# =============================================================================
# Krippendorff's alpha (nominal): models_05_evaluate.py, alpha_exact, copied unchanged (rule 2)
# =============================================================================
def alpha_exact(units: list[list[str]], cats: list[str]):
    """Nominal alpha from the coincidence matrix, exactly; None if there is no variation."""
    o = {(a, b): Fraction(0) for a in cats for b in cats}
    for vals in units:
        m = len(vals)
        if m < 2:
            continue
        cnt = Counter(vals)
        for a in cnt:
            for b in cnt:
                o[(a, b)] += Fraction(cnt[a] * (cnt[b] - (a == b)), m - 1)
    n_c = {a: sum(o[(a, b)] for b in cats) for a in cats}
    n = sum(n_c.values())
    disagree = sum(o[(a, b)] for a in cats for b in cats if a != b)
    expected = n * n - sum(x * x for x in n_c.values())
    if n == 0 or expected == 0:
        return None
    return 1 - (n - 1) * disagree / expected


def alpha_text(a) -> str:
    """Alpha to three decimals, or to as many as it takes to tell it from 0.7 when three would show 0.700 (rule 8)."""
    if a is None:
        return "undefined"
    places = 3
    while a != ALPHA_BAR and fixed(a, places) == fixed(ALPHA_BAR, places) and places < 12:
        places += 1
    return fixed(a, places)


def calibration(P: dict, review: list[dict]) -> dict:
    ids = sorted(P["A"])
    s1 = [[P[a][i]["stage1"] for a in ANNOTATORS if not P[a][i]["missing"]] for i in ids]
    s2 = [[P[a][i]["class"] for a in ANNOTATORS
           if not P[a][i]["missing"] and P[a][i]["stage1"] == "Y" and P[a][i]["class"]] for i in ids]
    measures = [("Stage 1", s1, ["N", "Y"]), ("Stage 2", s2, CLASSES)] + \
               [(f"{c} against the rest", [["1" if x == c else "0" for x in v] for v in s2], ["0", "1"])
                for c in CLASSES]
    alphas = {}
    for name, units, cats in measures:
        a = alpha_exact(units, cats)
        pairable = [u for u in units if len(u) >= 2]
        alphas[name] = {"alpha": dec(a, 4) if a is not None else None, "alpha_exact": fr(a) if a is not None else None,
                        "units": len(pairable), "pairable_values": sum(len(u) for u in pairable), "_a": a}
    # disagreements from the sheets (rule 3)
    derived = {}
    for i, v1, v2 in zip(ids, s1, s2):
        if len(set(v1)) > 1:
            derived[i] = "stage1"
        elif v1 and set(v1) == {"Y"} and len(set(v2)) > 1:
            derived[i] = "stage2"
        else:
            derived[i] = "none"
    classes_also_differ = sum(1 for i, v2 in zip(ids, s2) if derived[i] == "stage1" and len(set(v2)) > 1)
    # the review sheet, as recorded
    if len(review) != CALIBRATION_ITEMS or membership(r["id"] for r in review) != CALIBRATION_MEMBERSHIP \
            or len({r["id"] for r in review}) != CALIBRATION_ITEMS:
        stop(f"{REVIEW} does not hold the 30 calibration items of record. {REPORT}")
    rec, cause, label_diff = {}, {}, {a: 0 for a in ANNOTATORS}
    agreed_diff = agreed_checked = change_needed = 0
    for row_no, r in enumerate(review, start=2):
        where = f"{REVIEW}, row {row_no}"
        d = r["disagreement"].lower()
        if d not in ("none", "stage1", "stage2"):
            stop(f"{where}: disagreement {r['disagreement']!r} is not none, stage1 or stage2. {REPORT}")
        c = r["cause"].lower()
        if c not in ("", *CAUSES):
            stop(f"{where}: cause {r['cause']!r} is not a, b or c. {REPORT}")
        flag = r["codebook_change_needed"].upper()
        if flag not in ("Y", "N") and not (flag == "" and d == "none"):
            stop(f"{where}: codebook_change_needed {r['codebook_change_needed']!r} is not Y or N. {REPORT}")
        i = r["id"]
        rec[i], cause[i] = d, c
        change_needed += flag == "Y"
        for a in ANNOTATORS:
            if norm_label(r[f"label_{a}"]) != norm_label(label_text(P[a][i])):
                label_diff[a] += 1
        labels = {norm_label(label_text(P[a][i])) for a in ANNOTATORS if not P[a][i]["missing"]}
        if derived[i] == "none" and len(labels) == 1:
            agreed_checked += 1
            agreed_diff += norm_label(r["agreed_label"]) != labels.pop()
    recorded_dis = [i for i in ids if rec[i] != "none"]
    derived_dis = [i for i in ids if derived[i] != "none"]
    stage_pairs = Counter((rec[i], derived[i]) for i in ids if rec[i] != derived[i])
    causes = Counter(cause[i] for i in recorded_dis if cause[i])
    branch_key = "pass" if all(alphas[s]["_a"] is not None and alphas[s]["_a"] >= ALPHA_BAR
                               for s in ("Stage 1", "Stage 2")) else None
    plurality = None
    if branch_key is None:
        top = causes.most_common()
        if top and (len(top) == 1 or top[0][1] > top[1][1]):
            plurality = top[0][0]
            branch_key = plurality
    return {
        "alphas": alphas,
        "missing_ratings": {a: sum(1 for x in P[a].values() if x["missing"]) for a in ANNOTATORS},
        "disagreements_from_the_sheets": {"total": len(derived_dis),
                                          "stage1": sum(1 for i in ids if derived[i] == "stage1"),
                                          "stage2": sum(1 for i in ids if derived[i] == "stage2"),
                                          "stage1_items_whose_relevant_ratings_also_differ_in_class":
                                              classes_also_differ},
        "review_sheet": {
            "disagreements_recorded": {"total": len(recorded_dis),
                                       "stage1": sum(1 for i in ids if rec[i] == "stage1"),
                                       "stage2": sum(1 for i in ids if rec[i] == "stage2")},
            "causes_recorded": {k: causes.get(k, 0) for k in CAUSES},
            "items_recorded_otherwise_than_the_sheets": [
                {"recorded": a, "from_the_sheets": b, "items": n} for (a, b), n in sorted(stage_pairs.items())],
            "disagreements_from_the_sheets_without_a_cause": sum(1 for i in derived_dis if not cause[i]),
            "causes_on_items_without_a_disagreement_in_the_sheets": sum(1 for i in ids
                                                                        if cause[i] and derived[i] == "none"),
            "labels_differing_from_the_sheets": label_diff,
            "agreed_labels_checked_on_unanimous_items": agreed_checked,
            "agreed_labels_differing_from_the_unanimous_label": agreed_diff,
            "codebook_change_needed": change_needed},
        "r2_branch": {"key": branch_key, "plurality_cause": plurality,
                      "text": R2_BRANCHES.get(branch_key) if branch_key else
                      "no single plurality cause: R2 does not name a branch"},
    }


# =============================================================================
# times and annotation hours (rules 4 and 5)
# =============================================================================
def timings(P: dict) -> dict:
    per = {}
    for a in ANNOTATORS:
        per[a] = {}
        for k in STAGES:
            made_ids = {i for i, x in P[a].items() if not x["missing"] and (
                k == "stage1" or (k == "stage2" and x["stage1"] == "Y" and x["class"])
                or (k == "subsystem" and x["stage1"] == "Y" and x["subsystem"]))}
            made = [P[a][i] for i in sorted(made_ids)]
            vals = [x["t"][k] for x in made if x["t"][k] is not None]
            unused = sum(1 for i, x in P[a].items() if x["t"][k] is not None and i not in made_ids)
            per[a][k] = {"ratings": len(made), "with_a_time": len(vals), "without_a_time": len(made) - len(vals),
                         "times_without_a_label_not_used": unused,
                         "mean": mean(vals) if vals else None, "median": median(vals) if vals else None,
                         "total": sum(vals, Fraction(0))}
    spr = {}
    for k in STAGES:
        means = [per[a][k]["mean"] for a in ANNOTATORS if per[a][k]["mean"] is not None]
        if not means:
            stop(f"no annotator recorded a time at the {k} stage. {REPORT}")
        spr[k] = mean(means)
    return {"per_annotator": per, "seconds_per_rating": spr}


def tranche_ratings(S: Input) -> dict:
    t1_rel = sum(int(S.get("tranche1_checks", "annotator_sensitivity", a, "sheet_items_rated")) for a in ANNOTATORS)
    t2_single = sum(int(S.get("counts_required_by_the_record", "tranche2_single_rated_items_by_annotator", a,
                              "items")) for a in ANNOTATORS)
    t2_rel = t2_single + len(ANNOTATORS) * RELIABILITY_ITEMS_PER_TRANCHE
    lab = {t: int(S.get("subsystem", "secondary_labels", t, "all_ratings_with_a_primary", "ratings_with_a_primary"))
           for t in ("tranche 1", "tranche 2")}
    t1_coded = sum(int(S.get("tranche1_checks", "annotator_sensitivity", a, "coded_relevant")) for a in ANNOTATORS)
    if t1_coded != lab["tranche 1"]:
        stop(f"sample_results.json: tranche 1 ratings coded relevant ({t1_coded}) differ from its ratings with a "
             f"primary subsystem label ({lab['tranche 1']}). {REPORT}")
    return {"tranche 1": {"stage1": t1_rel, "stage2": lab["tranche 1"], "subsystem": lab["tranche 1"]},
            "tranche 2": {"stage1": t2_rel, "stage2": lab["tranche 2"], "subsystem": lab["tranche 2"]},
            "tranche_2_single_rated_items": t2_single}


def hours(T: dict, R: dict, P: dict) -> dict:
    spr = T["seconds_per_rating"]
    tr = {t: {k: Fraction(R[t][k]) * spr[k] / 3600 for k in STAGES} for t in ("tranche 1", "tranche 2")}
    cal = {}
    for k in STAGES:
        recorded = sum((T["per_annotator"][a][k]["total"] for a in ANNOTATORS), Fraction(0))
        filled = sum(T["per_annotator"][a][k]["without_a_time"] for a in ANNOTATORS)
        cal[k] = {"recorded_seconds": recorded, "ratings_without_a_time": filled,
                  "hours": (recorded + filled * spr[k]) / 3600}
    charged = sum((cal[k]["hours"] for k in ("stage1", "stage2")), Fraction(0)) + \
        sum((tr[t][k] for t in tr for k in ("stage1", "stage2")), Fraction(0))
    subsystem = cal["subsystem"]["hours"] + tr["tranche 1"]["subsystem"] + tr["tranche 2"]["subsystem"]
    return {"tranches": tr, "calibration": cal, "charged_relevance_and_stance": charged,
            "subsystem_not_charged": subsystem}


# =============================================================================
# cost and budget (rules 6 and 7)
# =============================================================================
def cost(E: Input, M: Input, K: Input, H: dict) -> dict:
    deployed = E.get("stage2", "deployment", "deployed")
    if M.get("run") != "stage2":
        stop(f"stage2_manifest.json is not the Stage 2 run. {REPORT}")
    if (deployed, M.get("model")) != DEPLOYED_RUN:
        stop(f"the corpus run ({M.get('model')}) is not the deployed configuration of the evaluation ({deployed}). "
             f"{REPORT}")
    comments = int(M.get("comments"))
    if comments <= 0:
        stop(f"stage2_manifest.json records no comment. {REPORT}")
    run_usd = num(M.get("cost_usd"), "stage2_manifest.json cost_usd")
    per_usd = run_usd / comments
    eval_per_1000 = num(E.get("stage2", "configurations", deployed, "cost_usd_per_1000_comments"),
                        "evaluation cost per 1,000")
    charges = K.get("card_charges")
    api = [c for c in charges if c.get("line") == API_LINE]
    if not api or any("usd" not in c for c in api):
        stop(f"cost_inputs.json: every {API_LINE} charge needs its US dollar amount. {REPORT}")
    api_aud = sum((num(c["aud"], "charge aud") for c in api), Fraction(0))
    api_usd = sum((num(c["usd"], "charge usd") for c in api), Fraction(0))
    bought = num(K.get("anthropic_credit", "bought_usd"), "credit bought")
    aud_per_usd_credit = api_aud / bought
    per_aud = per_usd * aud_per_usd_credit
    rate = num(K.get("hourly_rate", "aud"), "hourly rate")
    step = num(K.get("rate_step_aud_per_hour"), "rate step")
    h = H["charged_relevance_and_stance"]
    labelling = h * rate
    breakeven = labelling / per_aud
    per_step = h * step / per_aud
    best_ft = max(FINE_TUNED, key=lambda c: Fraction(E.get("stage2", "configurations", c, "pooled", "macro_f1_exact")))
    items = {c: int(E.get("stage2", "configurations", c, "pooled", "items")) for c in (deployed, best_ft)}
    if len(set(items.values())) != 1:
        stop(f"evaluation_results.json: the deployed and the best fine-tuned configurations were not evaluated on the "
             f"same number of items ({items}). {REPORT}")
    return {
        "deployed": deployed, "deployed_name": E.get("stage2", "configurations", deployed, "name"),
        "corpus_run": {"comments": comments, "cost_usd": run_usd, "model": M.get("model")},
        "per_1000_usd_corpus_run": per_usd * 1000, "per_1000_usd_evaluation": eval_per_1000,
        "per_1000_aud_corpus_run": per_aud * 1000, "per_1000_aud_evaluation": eval_per_1000 * aud_per_usd_credit,
        "api_charges_aud": api_aud, "api_charges_usd": api_usd, "credit_bought_usd": bought,
        "aud_per_usd_of_credit": aud_per_usd_credit, "aud_per_usd_on_the_card": api_aud / api_usd,
        "charged_above_the_credit": api_usd / bought - 1,
        "hourly_rate_aud": rate, "rate_step_aud": step,
        "labelling_hours_charged": h, "labelling_cost_aud": labelling,
        "breakeven_stage2_comments": breakeven, "breakeven_per_rate_step": per_step,
        "corpus_run_cost_aud": run_usd * aud_per_usd_credit,
        "incremental_fine_tuning_aud_per_comment": Fraction(0),
        "macro_f1": {deployed: Fraction(E.get("stage2", "configurations", deployed, "pooled", "macro_f1_exact")),
                     best_ft: Fraction(E.get("stage2", "configurations", best_ft, "pooled", "macro_f1_exact"))},
        "best_fine_tuned": best_ft, "best_fine_tuned_name": E.get("stage2", "configurations", best_ft, "name"),
        "evaluation_items": items[deployed],
        "rate_classification": K.get("hourly_rate", "classification"),
    }


def budget(K: Input) -> dict:
    lines = {}
    for c in K.get("card_charges"):
        for key in ("date", "line", "statement", "aud"):
            if key not in c:
                stop(f"cost_inputs.json: a card charge has no {key}. {REPORT}")
        lines.setdefault(c["line"], []).append(c)
    colab = num(K.get("colab", "aud"), "colab aud")
    totals = {k: sum((num(c["aud"], "charge aud") for c in v), Fraction(0)) for k, v in lines.items()}
    return {"lines": lines, "totals": totals, "colab": colab, "colab_basis": K.get("colab", "basis"),
            "total": sum(totals.values(), Fraction(0)) + colab, "credit": K.get("anthropic_credit")}


# =============================================================================
# outputs
# =============================================================================
def tex(s: str) -> str:
    out = []
    for ch in str(s):
        out.append({"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
                    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
                    "<": "$<$", ">": "$>$", "|": "$|$"}.get(ch, ch))
    s = "".join(out)
    if any(ord(c) > 127 for c in s):
        stop(f"non-ASCII text in a table cell ({s!r}). {REPORT}")
    return s


def tabular(spec: str, header: list[str], rows: list[list[str]], groups: dict | None = None,
            size: str = r"\small") -> str:
    L = [size, rf"\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(header) + r" \\", r"\midrule"]
    ncol = len(header)
    for i, r in enumerate(rows):
        if len(r) != ncol:
            stop(f"a table row has {len(r)} cells for {ncol} columns. {REPORT}")
        if groups and i in groups:
            if i:
                L.append(r"\addlinespace")
            L.append(rf"\multicolumn{{{ncol}}}{{@{{}}l}}{{\textit{{{groups[i]}}}}} \\")
        L.append(" & ".join(r) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(L) + "\n"


def money(x: Fraction, places: int = 2) -> str:
    return r"A\$" + fixed(x, places)


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def long_date(iso: str) -> str:
    """2026-08-03 as 3 August 2026."""
    try:
        y, mo, d = (int(x) for x in iso.split("-"))
        return f"{d} {MONTHS[mo - 1]} {y}"
    except (ValueError, IndexError):
        stop(f"cost_inputs.json: {iso!r} is not a date written YYYY-MM-DD. {REPORT}")


def table_calibration(C: dict) -> str:
    A = C["alphas"]
    rows, groups = [], {0: f"Krippendorff's alpha, nominal ({CALIBRATION_ITEMS} items, {len(ANNOTATORS)} annotators)"}
    for name, label in (("Stage 1", "Stage 1 (relevance)"), ("Stage 2", "Stage 2 (three classes)"),
                        ("CONCERN against the rest", "CONCERN against the rest"),
                        ("ENDORSEMENT against the rest", "ENDORSEMENT against the rest"),
                        ("OTHER against the rest", "OTHER against the rest")):
        rows.append([label, alpha_text(A[name]["_a"]),
                     f"{A[name]['units']} items, {A[name]['pairable_values']} values"])
    miss = C["missing_ratings"]
    rows.append(["Ratings missing (skip cell marked)", str(sum(miss.values())),
                 "; ".join(f"{a}: {miss[a]}" for a in ANNOTATORS)])
    D, Rv = C["disagreements_from_the_sheets"], C["review_sheet"]
    groups[len(rows)] = "Disagreements and their causes (R2)"
    rows.append(["Disagreements, from the three sheets",
                 str(D["total"]), f"Stage 1: {D['stage1']}; Stage 2: {D['stage2']}"])
    rec = Rv["disagreements_recorded"]
    rows.append(["Disagreements, as recorded on the review sheet",
                 str(rec["total"]), f"Stage 1: {rec['stage1']}; Stage 2: {rec['stage2']}"])
    for k, label in CAUSES.items():
        rows.append([f"Cause ({k}): {label}", str(Rv["causes_recorded"][k]), "as recorded on the review sheet"])
    rows.append(["Codebook change needed", str(Rv["codebook_change_needed"]), "items, as recorded"])
    groups[len(rows)] = "R2's branch"
    rows.append(["Branch", "", tex(C["r2_branch"]["text"][:1].upper() + C["r2_branch"]["text"][1:])])
    return tabular("@{}" + col("0.44") + rcol("0.12") + col("0.38") + "@{}",
                   ["Measure", "Value", "Basis"], rows, groups)


def table_cost(X: dict, H: dict, T: dict, R: dict, K: Input) -> str:
    spr = T["seconds_per_rating"]
    rows, groups = [], {0: "Zero-shot classification: the deployed configuration"}
    rows.append([tex(f"Cost per 1,000 Stage 2 comments, corpus run ({X['corpus_run']['comments']:,} comments)"),
                 money(X["per_1000_aud_corpus_run"], 3), r"US\$" + fixed(X["per_1000_usd_corpus_run"], 3)])
    rows.append([tex("Cost per 1,000 comments, evaluation run"), money(X["per_1000_aud_evaluation"], 3),
                 r"US\$" + fixed(X["per_1000_usd_evaluation"], 3)])
    rows.append([tex("Australian dollars per US dollar of credit (card charges / credit bought)"),
                 fixed(X["aud_per_usd_of_credit"], 4),
                 tex(f"card rate {fixed(X['aud_per_usd_on_the_card'], 4)}; charged "
                     f"{fixed(X['charged_above_the_credit'] * 100, 1)}% above the credit")])
    groups[len(rows)] = "Labelling time, estimated from the calibration sheets (time on the items only)"
    for k in STAGES:
        rows.append([tex(f"{STAGE_NAMES[k]}: seconds per rating"), fixed(spr[k], 1),
                     tex(f"ratings: tranche 1 {R['tranche 1'][k]:,}, tranche 2 {R['tranche 2'][k]:,}")])
    rows.append([tex("Relevance and stance labelling, calibration included (charged)"),
                 fixed(H["charged_relevance_and_stance"], 1) + " h", ""])
    rows.append([tex("Subsystem labelling (RQ2; not charged)"), fixed(H["subsystem_not_charged"], 1) + " h", ""])
    groups[len(rows)] = "Break-even (design decision D17)"
    rows.append([tex("Incremental accounting: fine-tuned classifier, per comment"),
                 money(X["incremental_fine_tuning_aud_per_comment"]),
                 tex("cheaper at every corpus size; the annotated set is needed to evaluate any classifier")])
    rows.append([tex(f"Zero-shot cost of the corpus run ({X['corpus_run']['comments']:,} comments)"),
                 money(X["corpus_run_cost_aud"]), ""])
    rows.append([tex("Full accounting: labelling charged to fine-tuning"), money(X["labelling_cost_aud"]),
                 tex(f"{fixed(X['labelling_hours_charged'], 1)} h at A${fixed(X['hourly_rate_aud'], 2)} an hour "
                     f"(UTS {X['rate_classification']}; no on-costs)")])
    rows.append([tex("Break-even, Stage 2 comments"),
                 tex(f"{nearest(X['breakeven_stage2_comments'], 1000):,}"),
                 tex(f"{fixed(X['breakeven_stage2_comments'] / X['corpus_run']['comments'], 0)} times the corpus "
                     f"run; zero-shot is cheaper below it")])
    rows.append([tex(f"Break-even per A${fixed(X['rate_step_aud'], 0)} an hour of the rate"),
                 tex(f"{nearest(X['breakeven_per_rate_step'], 1000):,}"),
                 tex("Stage 2 comments; proportional to the rate")])
    groups[len(rows)] = f"Accuracy (evaluation of record, macro-F1 on {X['evaluation_items']:,} items)"
    for c, name, role in ((X["deployed"], X["deployed_name"], "Deployed"),
                          (X["best_fine_tuned"], X["best_fine_tuned_name"], "Best fine-tuned")):
        rows.append([tex(f"{role}: {name}"), fixed(X["macro_f1"][c], 3), ""])
    return tabular("@{}" + col("0.47") + rcol("0.14") + col("0.33") + "@{}",
                   ["Quantity", "Value", "Basis"], rows, groups)


def table_budget(B: dict) -> str:
    rows = []
    for line, charges in B["lines"].items():
        detail = "; ".join(f"{long_date(c['date'])}: A${fixed(num(c['aud'], 'aud'), 2)}" +
                           (f" (US${fixed(num(c['usd'], 'usd'), 2)})" if "usd" in c else "") for c in charges)
        if line == API_LINE:
            cr = B["credit"]
            detail += (f"; credit bought US${fixed(num(cr['bought_usd'], 'b'), 2)}, used US$"
                       f"{fixed(num(cr['used_usd'], 'u'), 2)} to {long_date(cr['as_of'])}, US$"
                       f"{fixed(num(cr['remaining_usd'], 'r'), 2)} unused")
        rows.append([tex(line), money(B["totals"][line]), tex(detail)])
    rows.append([tex("GPU (Google Colab)"), money(B["colab"]), tex(B["colab_basis"])])
    rows.append([r"\textbf{Total paid}", r"\textbf{" + money(B["total"]) + "}", ""])
    return tabular("@{}" + col("0.26") + rcol("0.13") + col("0.55") + "@{}",
                   ["Line", "Paid", "Charges (date: amount)"], rows)


def make_figure(X: dict) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcdefaults()
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
                         "legend.fontsize": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "savefig.dpi": 200, "axes.edgecolor": INK, "xtick.color": INK,
                         "ytick.color": INK, "axes.labelcolor": INK, "text.color": INK})
    per = float(X["per_1000_aud_corpus_run"]) / 1000
    lab = float(X["labelling_cost_aud"])
    be = float(X["breakeven_stage2_comments"])
    n_run = X["corpus_run"]["comments"]
    xmax = max(2 * be, 1.15 * n_run)
    ytop = max(2 * lab, per * xmax)
    fig, ax = plt.subplots(figsize=(170 / 25.4, 6.5 / 2.54 - 0.01), layout="constrained")
    ax.plot([0, xmax], [0, per * xmax], color=FIGURE_COLOURS[0], lw=1.4,
            label="Zero-shot (deployed configuration): cost per comment of the corpus run")
    ax.plot([0, xmax], [lab, lab], color=FIGURE_COLOURS[1], lw=1.4,
            label="Fine-tuned, full accounting: relevance and stance labelling charged")
    ax.plot([0, xmax], [0, 0], color=FIGURE_COLOURS[2], lw=1.4, ls=(0, (4, 2)),
            label="Fine-tuned, incremental accounting: A\\$0 per comment")
    ax.annotate(f"corpus run: {n_run:,} comments, A\\${fixed(X['corpus_run_cost_aud'], 2)}",
                xy=(n_run, per * n_run), xytext=(0.06 * xmax, 0.78 * ytop), fontsize=7, va="center", ha="left",
                arrowprops={"arrowstyle": "->", "color": INK, "lw": 0.7})
    ax.axvline(be, color=INK, lw=0.7, ls=":")
    ax.text(be, ytop * 0.06, f"  break-even: about {nearest(X['breakeven_stage2_comments'], 1000):,}",
            fontsize=7, va="bottom", ha="left")
    ax.set_xlim(0, xmax)
    ax.set_ylim(-ytop * 0.015, ytop)
    ax.set_xlabel("Stage 2 comments classified")
    ax.set_ylabel("Cost (A\\$)")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.legend(loc="outside lower center", ncol=1)
    files = {}
    for fmt in ("pdf", "png"):
        buf = io.BytesIO()
        fig.savefig(buf, format=fmt, metadata={"CreationDate": None} if fmt == "pdf" else {"Software": None})
        files[f"cost_breakeven.{fmt}"] = buf.getvalue()
    plt.close(fig)
    return files


def jsonable(x):
    if isinstance(x, Fraction):
        return {"value": dec(x, 6), "exact": fr(x)}
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, list):
        return [jsonable(v) for v in x]
    return x


def results_payload(C, T, R, H, X, B, shas, me) -> dict:
    return jsonable({
        "specification": ("analysis_05_calibration_cost.py, rules 1-9 of its docstring; R2 of "
                          "docs/analysis_preregistration.md; design decision D17"),
        "script_sha256_lf": me, "inputs_sha256": shas,
        "calibration": C, "timings": T, "ratings_by_tranche": R, "annotation_hours": H, "cost": X,
        "budget": {"totals_by_line": B["totals"], "colab": B["colab"], "total_paid": B["total"],
                   "card_charges": B["lines"], "anthropic_credit": B["credit"]},
    })


def report_text(C, T, R, H, X, B) -> str:
    A = C["alphas"]
    L = ["# Calibration agreement and the cost break-even", "",
         f"Written by `{SCRIPT}` from the files of record (rules 1-9 of its docstring). No comment identifier is "
         "written here.", "", "## 1. Calibration round (R2)", "",
         "| Measure | Alpha | Items | Values |", "|---|---|---|---|"]
    for name in A:
        L.append(f"| {name} | {alpha_text(A[name]['_a'])} | {A[name]['units']} | {A[name]['pairable_values']} |")
    D, Rv = C["disagreements_from_the_sheets"], C["review_sheet"]
    rec = Rv["disagreements_recorded"]
    L += ["", "Ratings missing (skip cell marked): "
          + ", ".join(f"{a} {C['missing_ratings'][a]}" for a in ANNOTATORS) + ".",
          f"Disagreements from the three sheets: {D['total']} (Stage 1 {D['stage1']}, Stage 2 {D['stage2']}); "
              f"Stage 1 disagreements whose relevant ratings also differ in class: "
              f"{D['stage1_items_whose_relevant_ratings_also_differ_in_class']}.",
          f"Recorded on the review sheet: {rec['total']} (Stage 1 {rec['stage1']}, Stage 2 {rec['stage2']}); causes "
          + ", ".join(f"({k}) {CAUSES[k]} {Rv['causes_recorded'][k]}" for k in CAUSES) + ".",
          "Items whose recorded stage differs from the sheets: "
          + ("; ".join(f"{p['items']} recorded {p['recorded']}, {p['from_the_sheets']} from the sheets"
                       for p in Rv["items_recorded_otherwise_than_the_sheets"]) or "none") + ".",
          f"Disagreements in the sheets without a recorded cause: "
          f"{Rv['disagreements_from_the_sheets_without_a_cause']}; causes on items the sheets agree on: "
          f"{Rv['causes_on_items_without_a_disagreement_in_the_sheets']}.",
          "Review-sheet labels differing from the annotators' sheets: "
          + ", ".join(f"{a} {Rv['labels_differing_from_the_sheets'][a]}" for a in ANNOTATORS) + ".",
          f"Agreed labels on the {Rv['agreed_labels_checked_on_unanimous_items']} unanimous items that differ from "
          f"the unanimous label: {Rv['agreed_labels_differing_from_the_unanimous_label']}.",
          f"Codebook change needed: {Rv['codebook_change_needed']} items.",
          f"R2's branch: {C['r2_branch']['text']}.", "",
          "## 2. Times on the calibration sheets (seconds per rating)", "",
          "| Annotator | Stage | Ratings | With a time | Mean | Median | Times without a label (not used) |",
          "|---|---|---|---|---|---|---|"]
    for a in ANNOTATORS:
        for k in STAGES:
            p = T["per_annotator"][a][k]
            L.append(f"| {a} | {STAGE_NAMES[k]} | {p['ratings']} | {p['with_a_time']} | "
                     f"{fixed(p['mean'], 1) if p['mean'] is not None else 'none'} | "
                     f"{fixed(p['median'], 1) if p['median'] is not None else 'none'} | "
                     f"{p['times_without_a_label_not_used']} |")
    L += ["", "Seconds per rating (mean of the annotators' means): "
          + "; ".join(f"{STAGE_NAMES[k]} {fixed(T['seconds_per_rating'][k], 1)}" for k in STAGES) + ".", "",
          "## 3. Annotation hours (estimate; time on the items only)", "",
          "| | Relevance | Stance | Subsystem |", "|---|---|---|---|"]
    for t in ("tranche 1", "tranche 2"):
        L.append(f"| {t.capitalize()}: ratings | {R[t]['stage1']:,} | {R[t]['stage2']:,} | {R[t]['subsystem']:,} |")
        L.append(f"| {t.capitalize()}: hours | " + " | ".join(fixed(H['tranches'][t][k], 1) for k in STAGES) + " |")
    L.append("| Calibration round: hours | " + " | ".join(fixed(H['calibration'][k]['hours'], 2) for k in STAGES)
             + " |")
    L += ["", f"Charged under full accounting (relevance and stance, calibration included): "
              f"{fixed(H['charged_relevance_and_stance'], 1)} hours. Subsystem labelling, not charged: "
              f"{fixed(H['subsystem_not_charged'], 1)} hours.", "",
          "## 4. Cost break-even (D17)", "",
          f"- Deployed Stage 2 configuration: {X['deployed_name']}. Corpus run: {X['corpus_run']['comments']:,} "
          f"comments, US${fixed(X['corpus_run']['cost_usd'], 4)}; US${fixed(X['per_1000_usd_corpus_run'], 3)} per "
          f"1,000 comments (evaluation run: US${fixed(X['per_1000_usd_evaluation'], 3)}).",
          f"- Australian dollars per US dollar of credit: {fixed(X['aud_per_usd_of_credit'], 4)} "
          f"(A${fixed(X['api_charges_aud'], 2)} charged for US${fixed(X['credit_bought_usd'], 2)} of credit; the card "
          f"was charged US${fixed(X['api_charges_usd'], 2)}, {fixed(X['charged_above_the_credit'] * 100, 1)}% above "
          f"the credit; card rate {fixed(X['aud_per_usd_on_the_card'], 4)}). Zero-shot cost: "
          f"A${fixed(X['per_1000_aud_corpus_run'], 3)} per 1,000 Stage 2 comments; the corpus run cost "
          f"A${fixed(X['corpus_run_cost_aud'], 2)}.",
          f"- Incremental accounting: the fine-tuned classifier costs A$0 per comment, so it is cheaper at every "
          f"corpus size.",
          f"- Full accounting: {fixed(X['labelling_hours_charged'], 1)} hours at A${fixed(X['hourly_rate_aud'], 2)} an "
          f"hour = A${fixed(X['labelling_cost_aud'], 2)}. Break-even: "
          f"{fixed(X['breakeven_stage2_comments'], 0)} Stage 2 comments (about "
          f"{nearest(X['breakeven_stage2_comments'], 1000):,}, "
          f"{fixed(X['breakeven_stage2_comments'] / X['corpus_run']['comments'], 1)} times the corpus run); "
          f"{fixed(X['breakeven_per_rate_step'], 0)} comments for each A${fixed(X['rate_step_aud'], 0)} an hour of "
          f"the rate. Zero-shot is cheaper below the break-even.",
          f"- Macro-F1 (evaluation of record): {X['deployed_name']} {fixed(X['macro_f1'][X['deployed']], 3)}; "
          f"{X['best_fine_tuned_name']} {fixed(X['macro_f1'][X['best_fine_tuned']], 3)} (best fine-tuned).", "",
          "## 5. Spend", "", "| Line | Paid |", "|---|---|"]
    for line in B["lines"]:
        L.append(f"| {line} | A${fixed(B['totals'][line], 2)} |")
    L += [f"| GPU (Google Colab) | A${fixed(B['colab'], 2)} |", f"| Total paid | A${fixed(B['total'], 2)} |", ""]
    return "\n".join(L)


# =============================================================================
# building and writing
# =============================================================================
def build(loaded: dict, shas: dict, me: str) -> tuple[dict, dict, dict]:
    S, E, M, K = (loaded[k] for k in ("sample_results.json", "evaluation_results.json", "stage2_manifest.json",
                                      "cost_inputs.json"))
    P = parse_sheets(loaded["sheets"])
    for a in ANNOTATORS:
        if set(P[a]) != set(P["A"]):
            stop(f"{SHEETS[a]} does not hold the same ids as {SHEETS['A']}. {REPORT}")
    C = calibration(P, loaded["review"])
    T = timings(P)
    R = tranche_ratings(S)
    H = hours(T, R, P)
    X = cost(E, M, K, H)
    B = budget(K)
    tables = {}
    for name, text in (("calibration.tex", table_calibration(C)), ("cost.tex", table_cost(X, H, T, R, K)),
                       ("budget.tex", table_budget(B))):
        tables[name] = f"% {name}: written by {SCRIPT} from the files of record; do not edit by hand.\n" + text
    texts = {"calibration_cost_results.json": json_text(results_payload(C, T, R, H, X, B, shas, me)),
             "calibration_cost_report.md": report_text(C, T, R, H, X, B)}
    return texts, tables, make_figure(X)


def write_outputs(texts: dict, tables: dict, figures: dict, me: str, out_dir: Path, shas: dict, libs: dict) -> None:
    """Written to a fresh work folder, then moved into place with the manifest last: a run that fails part-way leaves
    no manifest, so it can simply be run again (it gives the same bytes)."""
    work = OUT_ROOT / f"in_progress_{os.getpid()}_{time.time_ns()}"
    (work / "tables").mkdir(parents=True)
    (work / "figures").mkdir()
    try:
        outputs = {}
        for name, text in sorted(texts.items()):
            with open(work / name, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            outputs[name] = text_sha256(text)
        for name, text in sorted(tables.items()):
            with open(work / "tables" / name, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            outputs[f"tables/{name}"] = text_sha256(text)
        for name, blob in sorted(figures.items()):
            with open(work / "figures" / name, "wb") as f:
                f.write(blob)
            outputs[f"figures/{name}"] = hashlib.sha256(blob).hexdigest()
        created = now_iso()
        versions = {"python": platform.python_version(), **libs}
        with open(work / "calibration_cost_manifest.json", "w", encoding="utf-8", newline="\n") as f:
            f.write(json_text({"created": created, "script": {"file": SCRIPT, "sha256_lf": me},
                               "inputs_sha256": shas, "outputs_sha256": outputs, "versions": versions}))
        out_dir.mkdir(parents=True, exist_ok=True)
        for sub in ("tables", "figures"):
            (out_dir / sub).mkdir(exist_ok=True)
            for name in sorted(os.listdir(work / sub)):
                replace_patiently(work / sub / name, out_dir / sub / name)
        for name in sorted(texts):
            replace_patiently(work / name, out_dir / name)
        replace_patiently(work / "calibration_cost_manifest.json", out_dir / "calibration_cost_manifest.json")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rel = out_dir.relative_to(REPO).as_posix()
    man_sha = hashlib.sha256((out_dir / "calibration_cost_manifest.json").read_bytes()).hexdigest()
    show_register_block(out_dir / "PASTE_calibration_cost_block.txt", [
        f"- `{SCRIPT}` (SHA-256 `{me}`) run {created} with `--confirm-committed`: every input matched its SHA-256 of "
        f"record (the four calibration sheets, `results/sample_results.json`, `evaluation_results.json`, "
        f"`stage2_manifest.json`, `docs/cost_inputs.json`).",
        f"- Outputs, in `{rel}/` (not committed; the results file and report copied to `results/`, the tables to "
        f"`results/report_tables/`, the figures to `results/report_figures/`): "
        f"`calibration_cost_results.json` `{outputs['calibration_cost_results.json']}`; "
        f"`calibration_cost_report.md` `{outputs['calibration_cost_report.md']}`; {len(tables)} table files and "
        f"{len(figures)} figure files, with their SHA-256 in `calibration_cost_manifest.json` `{man_sha}`. Python "
        f"{versions['python']}, NumPy {versions['numpy']}, matplotlib {versions['matplotlib']}, openpyxl "
        f"{versions['openpyxl']}.",
    ])
    print(f"\nwritten: {out_dir}")
    print("Next: copy the results file and the report to results/, the tables folder to results/report_tables/ and "
          "the figures folder to results/report_figures/.")


def summary_lines(texts: dict) -> list[str]:
    r = json.loads(texts["calibration_cost_results.json"])
    a = r["calibration"]["alphas"]
    x = r["cost"]
    miss = sum(r["calibration"]["missing_ratings"].values())
    return [f"calibration alpha: Stage 1 {a['Stage 1']['alpha']}, Stage 2 {a['Stage 2']['alpha']} ({miss} ratings "
            f"missing); R2: {r['calibration']['r2_branch']['text']}",
            f"labelling charged: {x['labelling_hours_charged']['value']:.1f} h; break-even "
            f"{x['breakeven_stage2_comments']['value']:,.0f} Stage 2 comments; total paid A$"
            f"{r['budget']['total_paid']['value']:.2f}"]


# =============================================================================
# main
# =============================================================================
def main() -> None:
    setup_console()
    ap = argparse.ArgumentParser(description="Calibration agreement and the cost break-even, from the files of record.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks and a build; writes nothing")
    mode.add_argument("--confirm-committed", action="store_true", help="the run of record (after the commit)")
    args = ap.parse_args()
    if not (args.preflight or args.confirm_committed):
        stop("choose one: --preflight (before the commit) or --confirm-committed (after the commit: the run of record)")
    started = time.time()
    print("Calibration agreement and cost break-even: "
          + ("preflight, before the commit\n" if args.preflight else "the run of record\n"))
    me = own_sha256()
    out_dir = run_folder(me)
    print(f"this script: {SCRIPT} SHA-256 {me}")
    if (out_dir / "calibration_cost_manifest.json").exists():
        stop(f"this script's outputs have already been written: they are in {out_dir}. They are written once.")
    libs = check_libraries()
    print(f"libraries: {', '.join(f'{n} {v}' for n, v in libs.items())}")
    loaded, shas = load_inputs()
    print(f"inputs: all {len(INPUTS)} match their SHA-256 of record")
    texts, tables, figures = build(loaded, shas, me)
    print(f"built: the results file, the report, {len(tables)} tables and {len(figures) // 2} figure (PDF and PNG)")
    if args.preflight:
        print(f"\nPREFLIGHT PASSED: every input matches the record and every output can be built. No output was "
              f"written ({time.time() - started:.0f} seconds).")
        return
    for line in summary_lines(texts):
        print(line)
    write_outputs(texts, tables, figures, me, out_dir, shas, libs)
    print(f"({time.time() - started:.0f} seconds)")


if __name__ == "__main__":
    main()
