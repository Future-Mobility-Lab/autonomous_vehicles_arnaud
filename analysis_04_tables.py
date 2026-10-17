"""Report tables and data figures (on the PC): the report's data tables, as LaTeX tabulars, and the data figures that
the series analyses do not draw, formatted from the results files of record, so that no number in them is typed by
hand.

From the repository folder, with the virtual environment active (no GPU, no internet):
    python analysis_04_tables.py --preflight
        Before the commit. Checks every input against the record, then builds every table and figure in memory and
        discards them. It writes no output (matplotlib may refresh its cache).
    python analysis_04_tables.py --confirm-committed
        After this file is committed and its SHA-256 recorded. The run of record. It runs once: it refuses to start
        if this file's outputs already exist (the SHA-256 is that of the file with LF line endings, as the register
        records script hashes).

Inputs, each checked against its SHA-256 of record, the text with LF line endings (a checkout that turned them into
CRLF changes nothing that is read). Nothing else is read and no repository module is imported.
  data/models/evaluation/evaluation_results.json   the evaluation of record (register, 11 October 2026)
  results/sample_results.json                       the sample analyses of record (register, 14 October 2026)
  results/corpus_results.json                       the corpus description of record (register, 17 October 2026)
  results/series_results.json                       the series analyses of record (register, 17 October 2026)
  models_config.py                                  the model configuration of record (bb3fbfe), read as text with
                                                    the Python parser for its checkpoints and model identifiers

What it writes (every figure formatted from the inputs; it computes nothing that the inputs do not hold, apart from a
share of two counts the inputs give and the per cent of a preprocessing stage)
  Tables, for the report's \\tabslot and table placeholders (each file holds the tabular only, and the caption,
  label and float stay in the report; the appendix longtable is whole, with its caption and label). They use the
  packages booktabs, array, longtable, url and xurl (for the identifiers in \\path), which the report loads, and no
  column type or macro of the report's own:
    funnel.tex            the preprocessing funnel of corpus v2.2: stage, items retained, items removed, per cent of
                          the previous stage
    models.tex            the classifiers compared and their roles
    reliability.tex       Krippendorff's alpha by stage, class and tranche, with the intervals recorded
    stage2.tex            macro-F1 and per-class F1 of the eight Stage 2 configurations
    trends.tex            the trend statistics of the concern series
    family_a.tex          Family A: the subsystem trend tests, with Holm-adjusted p-values
    sensitivity.tex       the sensitivity table, a complete longtable with its caption and label, which replaces
                          the report's appendix table
    criteria.tex          the success criteria of Deviation 12 and their outcomes
  Figures (PDF and PNG), each drawn at the size of its slot in the report, 17 cm wide (7 cm high for the first,
  6.5 cm for the others), so that it prints at a scale of about 1 (text 8 pt, value labels 7 pt):
    stage2_per_class_f1   per-class F1 by configuration
    composition_by_year   the subreddit composition of the Tier 1+2 comments by year
    relevance_by_era      the relevance rate by era with and without the subreddit rule

Rules fixed with this file
  1. Every number is formatted from the most exact value its input holds: an exact fraction where the input gives
     one (the keys ending in _exact, and shares formed from counts); otherwise the value as written. A value written
     rounded to six decimals whose digits beyond the place shown are exactly 5 followed by zeros could have been
     either side of that 5 before it was rounded, so it is shown with one more decimal. Rounding is half to even.
  2. Formats: per cent with one decimal (in the funnel, as many more as it takes not to show 100 per cent for a stage
     that removed comments); F1, alpha and other rates with three decimals; the ratios C/T and C_m/T with four;
     slopes and differences of shares in percentage points (per year for slopes) with two decimals and a sign;
     p-values with four decimals, as "< 0.0001" below 0.00005, and with eight significant digits, trailing zeros
     kept, where four decimals would show 0.0500; costs in US dollars per 1,000 items with three decimals; counts in
     full with thousands separators. Every bracket says what it holds, in the cell or in its column's header.
  3. The tables report what the inputs record and decide nothing. Where Deviation 12 or 13 fixes the consequence of
     an outcome, the outcome is given as the series analyses of record state it (their statement, or their outcome
     mapped word for word below) or in the words of the deviation; where no rule applies, the cell says so. Deviation
     12's criteria are given word for word, and its domain-specific schema is labelled exploratory (Family C).
  4. Figures (matplotlib, Agg backend, with matplotlib's default settings restored first, so that no matplotlibrc
     changes them): values as recorded, intervals as recorded, no smoothing and no fitted line. They show figures
     that the inputs hold and decide nothing. The PDFs carry no creation date. Their Creator and Producer are fixed
     strings that name the matplotlib version ("Matplotlib v3.11.2, https://matplotlib.org" and "Matplotlib pdf
     backend v3.11.2" in the pinned environment); the manifest records the version.

Writes, in data/analysis/tables/run_<first 12 hex digits of this file's SHA-256>/ (data/ is not committed):
  tables/*.tex                    the tables above
  figures/*.pdf, figures/*.png    the figures above
  tables_manifest.json            time, versions, the SHA-256 of every input and output, and each output's sources
  PASTE_tables_block.txt          the register lines (hashes only)
After the run, tables/ is copied to results/report_tables/ and figures/ to results/report_figures/ and committed
with the register lines.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import platform
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from fractions import Fraction
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

# =============================================================================
# THE RECORD
# =============================================================================
SCRIPT = "analysis_04_tables.py"
REPORT = "Report this message before going further."


def _find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for folder in (here, *here.parents):
        if (folder / "docs" / "analysis_preregistration.md").exists():
            return folder
    return here


REPO = _find_repo_root()
INPUTS = {                                        # name: (path, SHA-256 of the text with LF line endings)
    "evaluation_results.json": (REPO / "data" / "models" / "evaluation" / "evaluation_results.json",
                                "411f6c23ef6525b077c74fec15b8e5a06c59c550a8f3f2d15e99eb7d354d32e4"),
    "sample_results.json": (REPO / "results" / "sample_results.json",
                            "be9db9a168e6d432d5f7b6190a7a204a624e1aa4992cd399cbb90288a383c5d7"),
    "corpus_results.json": (REPO / "results" / "corpus_results.json",
                            "a1a59cda8498d503255fa5e47ce7c9630fb45c9163fec1d0a25e8e0792524a83"),
    "series_results.json": (REPO / "results" / "series_results.json",
                            "d955027383c7c1e55800a629c5a67f1c850389e25bea7fa483c97fb6a9465de8"),
    "models_config.py": (REPO / "models_config.py",
                         "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a"),
}
LIBRARIES = {"numpy": "2.5.1", "matplotlib": "3.11.2"}
OUT_ROOT = REPO / "data" / "analysis" / "tables"

CLASSES = ["CONCERN", "ENDORSEMENT", "OTHER"]
STAGE2_CONFIGS = ["distilbert", "roberta", "bart-universal", "bart-domain", "haiku-universal", "haiku-domain",
                  "sonnet-universal", "sonnet-domain"]                    # the evaluation of record's order
STAGE1_CONFIGS = ["stage1-distilbert", "stage1-roberta", "stage1-roberta-textonly"]
RELIABILITY_SETS = [("tranche 1 (100 items)", "Tranche 1"), ("tranche 2 (100 items)", "Tranche 2"),
                    ("both tranches (200 items)", "Both tranches")]
RELIABILITY_MEASURES = [("Stage 1", "Stage 1 (relevance)"), ("Stage 2", "Stage 2 (three classes)"),
                        ("CONCERN against the rest", "CONCERN against the rest"),
                        ("ENDORSEMENT against the rest", "ENDORSEMENT against the rest"),
                        ("OTHER against the rest", "OTHER against the rest")]
SUBSYSTEM_ALPHAS = [("two_or_more_labels", "Primary subsystem, items with two or more labels"),
                    ("all_three_annotators", "Primary subsystem, items all three annotators labelled")]
ERAS = ["2016-2018", "2019-2021", "2022-2025"]
YEARS = [str(y) for y in range(2016, 2026)]
SUBREDDITS8 = ["teslamotors", "selfdrivingcars", "realtesla", "waymo", "electricvehicles", "cars", "futurology",
               "technology"]                                             # Tier 1, then Tier 2 (R5's order)
FAMILY_A = ["sensing", "in_vehicle_networks", "cybersecurity", "privacy", "data_governance"]   # Deviation 9
SUBSYSTEM_NAMES = {"sensing": "Sensing", "in_vehicle_networks": "In-vehicle networks", "v2x": "V2X",
                   "cybersecurity": "Cybersecurity", "privacy": "Privacy", "data_governance": "Data governance",
                   "none": "None"}

# The classifiers compared (Deviation 12) and what the report says about each beside the record's figures. The
# paradigm, the developer and the access are facts of the design, stated here; the identifiers, commits, costs and
# roles are read from the inputs.
MODEL_ROWS = [
    {"name": "DistilBERT", "paradigm": "Fine-tuned encoder", "kind": "hf", "key": "distilbert",
     "stage2": ["distilbert"], "stage1": ["stage1-distilbert"]},
    {"name": "RoBERTa", "paradigm": "Fine-tuned encoder", "kind": "hf", "key": "roberta",
     "stage2": ["roberta"], "stage1": ["stage1-roberta", "stage1-roberta-textonly"]},
    {"name": "BART-MNLI", "paradigm": "Zero-shot, natural language inference", "kind": "hf", "key": "bart_mnli",
     "stage2": ["bart-universal", "bart-domain"], "stage1": []},
    {"name": "Claude Haiku 4.5", "paradigm": "Zero-shot, prompted language model", "kind": "api", "key": "haiku",
     "stage2": ["haiku-universal", "haiku-domain"], "stage1": []},
    {"name": "Claude Sonnet 4.6", "paradigm": "Zero-shot, prompted language model", "kind": "api", "key": "sonnet",
     "stage2": ["sonnet-universal", "sonnet-domain"], "stage1": [],
     "also": "subsystem classifier (Deviation 13)"},
]
HF_DEVELOPERS = {"distilbert": "Hugging Face", "FacebookAI": "Facebook AI", "facebook": "Facebook AI"}
API_DEVELOPER = "Anthropic"
ACCESS = {"hf": "Open weights, run on a GPU (Google Colab)", "api": "Anthropic API (paid)"}

# Deviation 12's six success criteria, word for word (docs/analysis_preregistration.md), set for LaTeX: alpha and the
# minus sign in math mode.
CRITERIA = {
    "1": r"Krippendorff's $\alpha$ is at least 0.7 at Stage 1 and at Stage 2 on the 200 reliability items. Any "
         r"per-class $\alpha$ below 0.7 is reported beside it.",
    "2": "The model comparison is completed under R5 and this deviation, with a measured cost and refusal rate for "
         "every configuration.",
    "3": "The concern share is reported with the prevalence correction and intervals, and the subsystem measures are "
         "reported as Deviation 9 specifies.",
    "4": "The temporal calibration check is reported on both tranches, and on each alone, before the corrected series "
         "(Deviation 11).",
    "5": "The relevance rate is reported with a design-weighted interval, beside the composition check of Deviation 8 "
         "and the text-only sensitivity.",
    "6": r"The deployed Stage 2 classifier has a TPR $-$ FPR for CONCERN of at least 0.25 on the primary item set. The "
         "bar is a judgement call; its value is that it is fixed before the author has seen any classifier scored. If "
         "it is not met, the uncorrected series is reported beside the corrected one and the instability is stated.",
}
# Deviation 13, "Sensitivity analyses": the three analyses planned in the project's design that are not run, with
# what the deviation says of each.
NOT_RUN = [
    ("Word floor at 15 words", "Not run (Deviation 13): the frozen corpus has no comment below 20 words."),
    ("Relevance classification with the post title added", "Not run (Deviation 13): no title was shown to the "
     "annotators, so labels assigned with the title in view do not exist."),
    ("The re-annotation held open as O17(c) in the governing document", "Not run (Deviation 13). It would show how "
     "the subreddit rule of Deviation 1 bears on the relevance labels; that question is answered only in part, by the "
     "era rates on the six subreddits and the text-only variant reported under RQ4."),
]


def col(width: str) -> str:
    """A ragged-right paragraph column of the given share of the line width (no column type of the report needed)."""
    return rf">{{\raggedright\arraybackslash}}p{{{width}\linewidth}}"


def rcol(width: str) -> str:
    """The same, ragged left (numbers)."""
    return rf">{{\raggedleft\arraybackslash}}p{{{width}\linewidth}}"


SENSITIVITY_SPEC = "@{}" + col("0.04") + col("0.24") + col("0.36") + col("0.28") + "@{}"
SENSITIVITY_HEADER = r"\textbf{No.} & \textbf{Analysis} & \textbf{Result} & \textbf{Outcome under the rules} \\"
FIGURE_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, GRID = "#333333", "#dddddd"


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


def write_json(path: Path, payload: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


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
    for name in LIBRARIES:
        try:
            found[name] = package_version(name)
        except PackageNotFoundError:
            found[name] = "not installed"
    if found != LIBRARIES:
        pins = " ".join(f"{n}=={v}" for n, v in LIBRARIES.items())
        stop(f"the tables use {', '.join(f'{n} {v}' for n, v in LIBRARIES.items())}; found "
             f"{', '.join(f'{n} {v}' for n, v in found.items())}.\n  Install them with:  python -m pip install {pins}")
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

    def has(self, *path) -> bool:
        x = self.data
        for k in path:
            if isinstance(x, dict) and k in x:
                x = x[k]
            else:
                return False
        return True


def load_inputs() -> tuple[dict, dict]:
    """Every input checked against its SHA-256 of record; the JSON files parsed, models_config.py parsed as text."""
    shas, loaded = {}, {}
    for name, (path, want) in INPUTS.items():
        if not path.exists():
            stop(f"{name} not found at {path}. {REPORT}")
        text = lf_text(path)
        got = text_sha256(text)
        if got != want:
            stop(f"{name} is not the file of record (SHA-256 {got[:16]}..., recorded {want[:16]}...). {REPORT}")
        shas[name] = got
        if name.endswith(".json"):
            try:
                loaded[name] = Input(name, json.loads(text))
            except json.JSONDecodeError as e:
                stop(f"{name} could not be read as JSON ({e}). {REPORT}")
        else:
            loaded[name] = models_config_constants(text)
    return loaded, shas


def models_config_constants(text: str) -> dict:
    """CHECKPOINTS and CLAUDE_MODELS of models_config.py, read with the Python parser: the file is not run."""
    want = {"CHECKPOINTS", "CLAUDE_MODELS"}
    out = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in want:
            out[node.targets[0].id] = ast.literal_eval(node.value)
    if set(out) != want:
        stop(f"models_config.py does not define {', '.join(sorted(want - set(out)))} as literals. {REPORT}")
    return out


# =============================================================================
# numbers (rule 1 and rule 2)
# =============================================================================
def exact(x) -> tuple[Decimal, bool]:
    """The value as a Decimal, and whether it may have been rounded to its written digits before it was written.

    A Fraction or an int is exact. A float with at most six decimals in its shortest form is a value written rounded
    (the results files round to six decimals; alpha to four); a longer float is an unrounded value, taken at its exact
    binary value, as Python's formatting takes it."""
    if isinstance(x, bool):
        stop(f"a yes/no value where a number was expected. {REPORT}")
    if isinstance(x, (int, Fraction)):
        f = Fraction(x)
        with localcontext() as ctx:
            ctx.prec = 60
            return Decimal(f.numerator) / Decimal(f.denominator), False
    if isinstance(x, float):
        r = repr(x)
        if "e" in r or "E" in r:
            return Decimal(x), False
        decimals = len(r.split(".")[1]) if "." in r else 0
        if decimals <= 6:
            return Decimal(r), True
        return Decimal(x), False
    if isinstance(x, str) and re.fullmatch(r"-?\d+/\d+", x):
        return exact(Fraction(x))
    stop(f"{x!r} is not a number. {REPORT}")


def fixed(x, places: int, scale: int = 1, sign: bool = False) -> str:
    """x * scale with the given decimals (rule 1: one more where a written value sits exactly on a half)."""
    d, written = exact(x)
    with localcontext() as ctx:
        ctx.prec = 60
        d = d * scale
        q = Decimal(1).scaleb(-places)
        if written:
            stored = -d.as_tuple().exponent if d.as_tuple().exponent < 0 else 0
            if stored > places:
                rest = abs(d) - abs(d).quantize(q, rounding="ROUND_DOWN")
                if rest == q / 2:
                    places += 1
                    q = Decimal(1).scaleb(-places)
        out = d.quantize(q, rounding=ROUND_HALF_EVEN)
    s = f"{out:.{places}f}"
    if out == 0:                                   # a value that rounds to zero carries no sign
        return s.lstrip("-")
    if sign and not s.startswith("-"):
        s = "+" + s
    return s


def grouped(n) -> str:
    if isinstance(n, bool) or not isinstance(n, int):
        stop(f"{n!r} is not a count. {REPORT}")
    return f"{n:,}"


def tex(s: str) -> str:
    """Plain text for LaTeX: the special characters escaped, and <, >, | (which the default font encoding prints as
    other characters) set in math mode."""
    out = []
    for ch in str(s):
        out.append({"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
                    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
                    "<": "$<$", ">": "$>$", "|": "$|$"}.get(ch, ch))
    s = "".join(out)
    if any(ord(c) > 127 for c in s):
        stop(f"non-ASCII text in a table cell ({s!r}). {REPORT}")
    return s


def m(s: str) -> str:
    """A signed number in math mode, so that the minus is a minus sign."""
    return f"${s}$"


def pct(x, places: int = 1) -> str:
    return fixed(x, places, scale=100)


def pts(x, places: int = 2) -> str:
    """A difference of shares or a slope, in percentage points, signed."""
    return m(fixed(x, places, scale=100, sign=True))


def pval(p) -> str:
    """Rule 2: four decimals; below 0.00005 as < 0.0001; eight significant digits where four decimals show 0.0500."""
    d, _ = exact(p)
    if d < Decimal("0.00005"):
        return "$<$0.0001"
    s = fixed(p, 4)
    if s == "0.0500":                              # eight significant digits, trailing zeros kept
        with localcontext() as ctx:
            ctx.prec = 60
            q = Decimal(1).scaleb(d.adjusted() - 7)
            out = d.quantize(q, rounding=ROUND_HALF_EVEN)
            if out.adjusted() != d.adjusted():         # rounding carried into the next power of ten
                out = d.quantize(q * 10, rounding=ROUND_HALF_EVEN)
        return f"{out:f}"
    return s


def count_g(x) -> str:
    """A count or a median of counts: whole numbers without decimals, halves with one."""
    f = Fraction(exact(x)[0])
    return grouped(int(f)) if f.denominator == 1 else fixed(x, 1)


def ratio(k: int, n: int) -> Fraction:
    if not n:
        stop(f"a share with no denominator. {REPORT}")
    return Fraction(k, n)


def interval_text(low, high, places: int = 3, scale: int = 1, signed: bool = False) -> str:
    if signed:
        return f"[{m(fixed(low, places, scale, True))}, {m(fixed(high, places, scale, True))}]"
    return f"[{fixed(low, places, scale)}, {fixed(high, places, scale)}]"


def tabular(spec: str, header: list[str], rows: list[list[str]], size: str = r"\small",
            colsep: str | None = None, groups: dict | None = None) -> str:
    """A booktabs tabular. groups maps a row index to a heading row placed before it."""
    L = [size] if size else []
    if colsep:
        L.append(rf"\setlength{{\tabcolsep}}{{{colsep}}}")
    L += [rf"\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(header) + r" \\", r"\midrule"]
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


# =============================================================================
# the tables
# =============================================================================
def table_funnel(C: Input) -> tuple[str, list]:
    stages = C.get("funnel", "stages")
    if not isinstance(stages, list) or len(stages) < 3:
        stop(f"corpus_results.json funnel.stages is not the list of stages. {REPORT}")
    rows = []
    for k, st in enumerate(stages):
        label = str(C.get("funnel", "stages", k, "stage"))
        items = C.get("funnel", "stages", k, "items")
        text = tex(label[:1].upper() + label[1:]).replace("$>$=", r"$\geq$")
        if k < 2:                                  # as corpus_report.md: the first row counts every raw item (posts
            removed, share = "--", "--"            # included), the rows after it count comments
        else:
            before = C.get("funnel", "stages", k - 1, "items")
            removed = C.get("funnel", "stages", k, "removed")
            if removed != before - items:
                stop(f"corpus_results.json: funnel stage {k} does not remove what its counts say. {REPORT}")
            share, places = pct(ratio(items, before)), 1
            while removed and share.startswith("100.") and places < 4:
                places += 1                        # comments were removed: never show 100 per cent
                share = pct(ratio(items, before), places)
            removed = grouped(removed)
        rows.append([text, grouped(items), removed, share])
    if C.get("funnel", "stages", len(stages) - 1, "items") != C.get("corpus", "rows"):
        stop(f"corpus_results.json: the last funnel stage is not the corpus rows. {REPORT}")
    spec = "@{}" + col("0.52") + rcol("0.12") + rcol("0.12") + rcol("0.16") + "@{}"
    return tabular(spec, ["Stage", "Retained", "Removed", r"Per cent of the previous stage"], rows), \
        ["corpus_results.json: funnel.stages[].{stage, items, removed}; corpus.rows"]


def table_models(E: Input, M: dict) -> tuple[str, list]:
    s2 = E.get("stage2", "configurations")
    s1 = E.get("stage1", "configurations")
    if list(s2) != STAGE2_CONFIGS or list(s1) != STAGE1_CONFIGS:
        stop(f"evaluation_results.json does not hold the configurations of record in their order. {REPORT}")
    dep2 = E.get("stage2", "deployment", "deployed")
    dep1 = E.get("stage1", "deployment", "deployed")
    text_only = E.get("stage1", "deployment", "text_only_variant")
    rows = []
    for r in MODEL_ROWS:
        if r["kind"] == "hf":
            ck = M["CHECKPOINTS"].get(r["key"])
            if not ck or "repo" not in ck or "commit" not in ck:
                stop(f"models_config.py CHECKPOINTS has no repo and commit for {r['key']}. {REPORT}")
            org, _, repo_name = ck["repo"].partition("/")
            if org not in HF_DEVELOPERS:
                stop(f"models_config.py: no developer is listed here for {ck['repo']}. {REPORT}")
            size = [w for w in repo_name.split("-") if w in ("base", "large", "uncased")]
            vendor = ", ".join(size).capitalize() + "; " + HF_DEVELOPERS[org]
            ident = rf"\path{{{ck['repo']}}}, commit \path{{{ck['commit'][:7]}}}"
            costs = {E.get("stage2", "configurations", c, "cost_usd_per_1000_comments") for c in r["stage2"]}
            if costs != {0.0}:
                stop(f"evaluation_results.json gives an API cost for {r['name']}, which runs on a GPU. {REPORT}")
            cost = r"US\$0 (no API charge)"
        else:
            ident_value = M["CLAUDE_MODELS"].get(r["key"])
            if not ident_value:
                stop(f"models_config.py CLAUDE_MODELS has no identifier for {r['key']}. {REPORT}")
            vendor = API_DEVELOPER
            ident = rf"\path{{{ident_value}}}"
            parts = []
            for c in r["stage2"]:
                schema = "universal" if c.endswith("-universal") else "domain-specific"
                parts.append(r"US\$" + fixed(E.get("stage2", "configurations", c, "cost_usd_per_1000_comments"), 3)
                             + f" ({schema})")
            cost = "; ".join(parts)
        roles = []
        if dep1 in r["stage1"]:
            roles.append("Stage 1 deployed (subreddit and comment)"
                         + (", its text-only variant as a sensitivity" if text_only in r["stage1"] else ""))
        elif r["stage1"]:
            roles.append("Stage 1 candidate")
        d2 = [c for c in r["stage2"] if c == dep2]
        if d2:
            other = [c for c in r["stage2"] if c != dep2]
            roles.append("Stage 2 deployed (" + ("domain-specific" if d2[0].endswith("-domain") else "universal")
                         + " schema" + ("; " + ("universal" if other[0].endswith("-universal") else "domain-specific")
                                        + " schema compared" if other else "") + ")")
        else:
            roles.append("Stage 2 compared" + (" (both schemas)" if len(r["stage2"]) == 2 else ""))
        if r.get("also"):
            roles.append(r["also"])
        rows.append([tex(r["name"]), tex(r["paradigm"]), tex(vendor), tex(ACCESS[r["kind"]]), ident, cost,
                     tex("; ".join(roles)).replace("deployed", r"\textbf{deployed}")])
    spec = "@{}" + "".join(col(w) for w in ("0.11", "0.11", "0.09", "0.10", "0.21", "0.13", "0.17")) + "@{}"
    header = ["Model", "Paradigm", "Size or developer", "Access", "Identifier", "Cost per 1,000 items", "Role"]
    return tabular(spec, header, rows, size=r"\footnotesize", colsep="3pt"), \
        ["models_config.py: CHECKPOINTS (repo, commit), CLAUDE_MODELS",
         "evaluation_results.json: stage2.configurations.*.cost_usd_per_1000_comments, stage2.deployment.deployed, "
         "stage1.deployment.deployed, stage1.deployment.text_only_variant"]


def alpha_cell(E: Input, key: str, measure: str) -> str:
    a = E.get("reliability", key, measure, "alpha_exact")
    iv = E.get("reliability", key, measure, "interval95")
    lo, hi = iv.get("low") if isinstance(iv, dict) else None, iv.get("high") if isinstance(iv, dict) else None
    if lo is None or hi is None:
        return fixed(a, 3)
    return rf"{fixed(a, 3)}\newline {interval_text(lo, hi)}"


def table_reliability(E: Input, S: Input) -> tuple[str, list]:
    rows = []
    for measure, label in RELIABILITY_MEASURES:
        units = "/".join(grouped(E.get("reliability", k, measure, "units")) for k, _ in RELIABILITY_SETS)
        rows.append([tex(label)] + [alpha_cell(E, k, measure) for k, _ in RELIABILITY_SETS] + [units])
    for key, label in SUBSYSTEM_ALPHAS:
        cells, units = [], []
        for k, _ in RELIABILITY_SETS:
            cells.append(fixed(S.get("subsystem", "alpha", k, key, "alpha_exact"), 3))
            units.append(grouped(S.get("subsystem", "alpha", k, key, "units")))
        rows.append([tex(label)] + cells + ["/".join(units)])
    spec = "@{}" + col("0.30") + col("0.15") + col("0.15") + col("0.15") + rcol("0.15") + "@{}"
    header = ["Measure"] + [h for _, h in RELIABILITY_SETS] + [r"Units (tranche 1/\allowbreak tranche 2/\allowbreak both)"]
    groups = {0: "Relevance and stance: Krippendorff's alpha [95\\% interval]",
              5: "Primary subsystem: Krippendorff's alpha (no interval recorded)"}
    return tabular(spec, header, rows, size=r"\footnotesize", colsep="4pt", groups=groups), \
        ["evaluation_results.json: reliability.{tranche 1 (100 items), tranche 2 (100 items), both tranches "
         "(200 items)}.{Stage 1, Stage 2, CONCERN/ENDORSEMENT/OTHER against the rest}.{alpha_exact, interval95.low, "
         "interval95.high, units}",
         "sample_results.json: subsystem.alpha.*.{two_or_more_labels, all_three_annotators}.{alpha_exact, units}"]


def split_name(c: str, name: str) -> tuple[str, str]:
    for suffix, schema in ((" (universal)", "Universal"), (" (domain-specific)", "Domain-specific")):
        if name.endswith(suffix):
            return name[: -len(suffix)], schema
    if c in ("distilbert", "roberta"):
        return name, "--"
    stop(f"evaluation_results.json: the name {name!r} of {c} names no schema. {REPORT}")


def f1_cell(E: Input, c: str, measure: str) -> str:
    if measure == "macro":
        value = E.get("stage2", "configurations", c, "pooled", "macro_f1_exact")
        sd = E.get("stage2", "configurations", c, "folds", "macro_f1", "sd")
    else:
        value = E.get("stage2", "configurations", c, "pooled", "per_class", measure, "f1_exact")
        sd = E.get("stage2", "configurations", c, "folds", measure, "sd")
    return f"{fixed(value, 3)} ({fixed(sd, 3)})"


def table_stage2(E: Input) -> tuple[str, list]:
    s2 = E.get("stage2", "configurations")
    if list(s2) != STAGE2_CONFIGS:
        stop(f"evaluation_results.json does not hold the eight configurations of record in their order. {REPORT}")
    deployed = E.get("stage2", "deployment", "deployed")
    items = E.get("item_sets", "stage2_primary", "items")
    rows = []
    for c in STAGE2_CONFIGS:
        if E.get("stage2", "configurations", c, "pooled", "items") != items:
            stop(f"evaluation_results.json: {c} is not scored on the {items} primary items. {REPORT}")
        model, schema = split_name(c, E.get("stage2", "configurations", c, "name"))
        notes = (["exploratory"] if schema == "Domain-specific" else []) + ([r"\textbf{deployed}"] if c == deployed else [])
        if notes:                                  # Deviation 12: the domain-specific schema is Family C, exploratory
            schema += " (" + "; ".join(notes) + ")"
        rows.append([tex(model), schema] + [f1_cell(E, c, "macro")] + [f1_cell(E, c, k) for k in CLASSES])
    spec = "@{}" + "".join(col(w) for w in ("0.15", "0.17", "0.13", "0.13", "0.18", "0.13")) + "@{}"
    header = ["Model", "Schema", "Macro-F1 (fold SD)", "F1 CONCERN (fold SD)", "F1 ENDORSEMENT (fold SD)",
              "F1 OTHER (fold SD)"]
    return tabular(spec, header, rows, size=r"\footnotesize", colsep="4pt"), \
        [f"evaluation_results.json: stage2.configurations.*.pooled.macro_f1_exact, "
         f"stage2.configurations.*.pooled.per_class.*.f1_exact (the {items} primary items), "
         "stage2.configurations.*.folds.{macro_f1, CONCERN, ENDORSEMENT, OTHER}.sd (in brackets), "
         "stage2.configurations.*.name, stage2.deployment.deployed"]


TREND_ROWS = [  # label, path to the trend, unit of the values, what is shown
    ("Primary series (reweighted, corrected)", ("rq1", "primary_series", "trend"), "quarters", "full+hr"),
    ("Block-specific series (temporal check)", ("rq1", "block_specific_series", "trend"), "quarters", "full"),
    ("Companion series (subreddits retained every year)", ("rq1", "companion_series", "trend"), "quarters", "full"),
    ("Pooled series (R3)", ("rq1", "pooled_series", "trend"), "quarters", "full"),
    ("Tier-level series (R3)", ("rq1", "tier_level_series", "trend"), "quarters", "full"),
    ("Three-class correction, CONCERN (exploratory)", ("rq1", "three_class_correction", "trend"), "quarters", "full"),
    ("Word floor of 25 (exploratory)", ("sensitivities", "word_floor_25", "trend"), "quarters", "full"),
    ("Tier 1 only (exploratory)", ("sensitivities", "tier_strata", "tier1", "trend"), "quarters", "full"),
    ("Tier 2 only (exploratory)", ("sensitivities", "tier_strata", "tier2", "trend"), "quarters", "full"),
    ("Size-stratified series (R4)", ("thread_size_R4", "size_stratified_series", "trend"), "years", "full"),
    ("Relevance error, low series", ("relevance_error_series", "low_sen_slope"), "quarters", "slope"),
    ("Relevance error, high series", ("relevance_error_series", "high_sen_slope"), "quarters", "slope"),
]


def slope_cell(S: Input, path: tuple, with_interval: bool = True) -> str:
    t = S.get(*path)
    if t.get("sen_slope_per_year") is None:
        return "n/a"
    s = pts(S.get(*path, "sen_slope_per_year"))
    if with_interval:
        lo, hi = t.get("gilbert95_low_per_year"), t.get("gilbert95_high_per_year")
        s += " " + (interval_text(lo, hi, 2, 100, True) if lo is not None and hi is not None else "[n/a]")
    return s


def p_cell(S: Input, path: tuple) -> str:
    t = S.get(*path)
    if t.get("p") is None:
        return "n/a"
    test = str(S.get(*path, "test"))
    return pval(t["p"]) + (" (exact)" if test.startswith("exact") else "")


def table_trends(S: Input) -> tuple[str, list]:
    rows = []
    for label, path, unit, shown in TREND_ROWS:
        values = S.get(*path, "values")
        if shown == "slope":
            rows.append([tex(label), "--", "--", "--",
                         slope_cell(S, path, False) + " (no interval; not a bound on the slope)", f"{values} {unit}"])
            continue
        t = S.get(*path)
        mk = t.get("mann_kendall") or {}
        stat = "n/a" if mk.get("s") is None else m(str(int(S.get(*path, "mann_kendall", "s"))))
        hr = "--"
        if shown == "full+hr":
            h = S.get(*path, "hamed_rao")
            if h.get("computed") and h.get("computable") and h.get("p") is not None:
                hr = pval(h["p"]) + (" (variance unchanged)" if h.get("variance_changed") is False else "")
            else:
                hr = tex(str(h.get("note") or "not computable"))
        rows.append([tex(label), stat, p_cell(S, path), hr, slope_cell(S, path), f"{values} {unit}"])
    spec = "@{}" + col("0.25") + rcol("0.06") + col("0.13") + col("0.11") + col("0.27") + col("0.11") + "@{}"
    header = ["Series", r"$S$", r"Mann--Kendall $p$", r"Hamed--Rao $p$",
              r"Sen's slope, points per year [Gilbert 95\% interval]", "Values"]
    return tabular(spec, header, rows, size=r"\footnotesize", colsep="3pt"), \
        ["series_results.json: " + "; ".join(".".join(p) + ".{values, mann_kendall.s, p, test, sen_slope_per_year, "
                                             "gilbert95_low_per_year, gilbert95_high_per_year}" for _, p, _, _ in TREND_ROWS)
         + "; rq1.primary_series.trend.hamed_rao.{computed, computable, p, variance_changed}"]


def table_family_a(S: Input) -> tuple[str, list]:
    tests = list(S.get("rq2", "family_A", "tests"))
    holm = S.get("rq2", "family_A", "holm_adjusted_p")
    if S.get("rq2", "family_A", "size") != len(tests) or set(holm) != set(tests) or not set(tests) <= set(FAMILY_A):
        stop(f"series_results.json rq2.family_A is not consistent with its tests. {REPORT}")
    rows = []
    for s in FAMILY_A:
        v = S.get("rq2", "values", s)
        sp = S.get("rq2", "values", s, "sparsity")
        fa = v.get("family_A_test")
        if (fa is not None) != (s in tests):
            stop(f"series_results.json: {s} is {'not ' if s in tests else ''}in Family A but has "
                 f"{'no ' if fa is None else 'a '}test. {REPORT}")
        medians = (f"{count_g(S.get('rq2', 'values', s, 'sparsity', 'median_quarterly_count'))} a quarter; "
                   f"{count_g(S.get('rq2', 'values', s, 'sparsity', 'median_annual_count'))} a year")
        if fa is None:
            rows.append([tex(SUBSYSTEM_NAMES[s]), tex(f"not tested: {sp.get('reported_as')}"), "--", "--", "--",
                         "--", tex(medians)])
            continue
        path = ("rq2", "values", s, "family_A_test")
        if abs(float(S.get(*path, "holm_adjusted_p")) - float(holm[s])) > 5e-7:
            stop(f"series_results.json: the Holm-adjusted p of {s} differs between family_A and the test. {REPORT}")
        rows.append([tex(SUBSYSTEM_NAMES[s]), tex(f"{sp.get('reported_as')}, {S.get(*path, 'values')} values"),
                     m(str(int(S.get(*path, "mann_kendall", "s")))), p_cell(S, path),
                     pval(S.get(*path, "holm_adjusted_p")), slope_cell(S, path), tex(medians)])
    spec = "@{}" + col("0.15") + col("0.16") + rcol("0.05") + col("0.10") + col("0.08") + col("0.23") + col("0.15") + "@{}"
    header = ["Subsystem", "Resolution", r"$S$", r"$p$", r"$p$ (Holm)",
              r"Sen's slope of $\pi_s$, points per year [Gilbert 95\% interval]", "Median count (sparsity rule)"]
    return tabular(spec, header, rows, size=r"\footnotesize", colsep="3pt"), \
        ["series_results.json: rq2.family_A.{tests, size, holm_adjusted_p}; rq2.values.<subsystem>.sparsity."
         "{reported_as, median_quarterly_count, median_annual_count}; rq2.values.<subsystem>.family_A_test."
         "{values, mann_kendall.s, p, test, holm_adjusted_p, sen_slope_per_year, gilbert95_low_per_year, "
         "gilbert95_high_per_year}"]


def statement_body(statement: str) -> str:
    """A statement of the series analyses without its leading name ("Pooled series (R3): ...")."""
    head, sep, rest = statement.partition(": ")
    body = rest if sep and len(head) < 60 else statement
    return body[:1].upper() + body[1:]


def r4_outcome(t4: Input) -> str:
    o = str(t4.get("thread_size_R4", "outcome"))
    if o.startswith("not applied: the primary series' Mann-Kendall test is not significant"):
        return ("Outcome not applied: the primary series' Mann--Kendall test is not significant, so $T$ cannot be told "
                r"from zero (Deviation 13); $|C|/(\mathrm{TPR}-\mathrm{FPR})$ = "
                + fixed(t4.get("thread_size_R4", "abs_C_corrected_scale"), 2, 100) + " points of corrected share.")
    if o == "non-consequential: |C| < 0.20 x |T|":
        return r"Non-consequential: $|C| < 0.20 \times |T|$ (R4)."
    if o.startswith("material limitation"):
        return (r"Material limitation (R4): $C$ is reported and the trend is stated net of it, $T - C$ = "
                + pts(t4.get("thread_size_R4", "T_minus_C")) + " points ("
                + pts(t4.get("thread_size_R4", "T_minus_C_corrected_scale")) + " on the corrected scale).")
    if o.startswith("|C| >= 0.50 x |T|"):
        return (r"$|C| \geq 0.50 \times |T|$: the size-stratified series is reported first as the result for RQ1, "
                "with the primary series beside it (R4 as Deviation 13 reads it).")
    if o == "not computed":
        return "Not computed."
    stop(f"series_results.json thread_size_R4.outcome is not one this script knows ({o!r}). {REPORT}")


def cm_outcome(S: Input) -> str:
    base = ("sensitivities", "seasonality", "month_of_year_decomposition")
    o = str(S.get(*base, "outcome"))
    if o.startswith("not applied: the primary series' Mann-Kendall test is not significant"):
        return ("Outcome not applied: the primary series' Mann--Kendall test is not significant (Deviation 13); "
                r"$|C_m|/(\mathrm{TPR}-\mathrm{FPR})$ = " + fixed(S.get(*base, "abs_C_m_corrected_scale"), 2, 100)
                + " points of corrected share.")
    if o.startswith("the drift is not consequential"):
        return r"The drift is not consequential: $|C_m| < 0.20 \times |T|$ (Deviation 13, sensitivity 1)."
    if o.startswith("the drift is a material limitation"):
        return (r"The drift is a material limitation: $|C_m| \geq 0.20 \times |T|$; the trend is also stated net of "
                r"$C_m$, $T - C_m$ = " + pts(S.get(*base, "T_minus_C_m")) + " points ("
                + pts(S.get(*base, "T_minus_C_m_corrected_scale")) + " on the corrected scale).")
    if o == "not computed":
        return "Not computed."
    stop(f"series_results.json month_of_year_decomposition.outcome is not one this script knows ({o!r}). {REPORT}")


def labelled_interval(low, high, label: str) -> str:
    """A bracket that says what it holds: [label low to high], in percentage points, signed."""
    if low is None or high is None:
        return f"[{label}: none]"
    return f"[{label} {pts(low)} to {pts(high)}]"


def trend_summary(S: Input, path: tuple) -> str:
    t = S.get(*path)
    if t.get("sen_slope_per_year") is None:
        return "Sen's slope n/a"
    return (f"Sen's slope {pts(S.get(*path, 'sen_slope_per_year'))} points per year "
            + labelled_interval(t.get("gilbert95_low_per_year"), t.get("gilbert95_high_per_year"),
                                r"Gilbert 95\% interval") + r"; $p$ = " + p_cell(S, path))


def exploratory_outcome(S: Input, path: tuple) -> str:
    """The outcome of an exploratory comparison by R3's two criteria with no other stated consequence (Deviation 13:
    a criterion that fails is stated with the series and in the limitations, and the primary series stays the result),
    checked against the statement the series analyses wrote."""
    crit = S.get(*path, "criteria")
    said = statement_body(str(S.get(*path, "statement")))
    if not crit:
        out = "R3's criteria could not be applied."
    elif crit.get("both_hold"):
        out = "Both of R3's criteria hold; the series agrees with the primary series."
    else:
        failed = [n for n, k in (("1", "criterion1_agreement_of_conclusion"), ("2", "criterion2_overlap_of_estimate"))
                  if not crit.get(k)]
        out = (f"R3's criterion {' and '.join(failed)} fails. Exploratory (Family C): stated with the series and in "
               "the limitations, and the primary series stays the result (Deviation 13).")
    if not said.startswith(out.split(". ")[0].rstrip(".")):
        stop(f"series_results.json: the statement of {'.'.join(path)} does not match its criteria. {REPORT}")
    return out


def criteria_text(crit: dict | None) -> str:
    if not crit:
        return "R3's criteria could not be applied."

    def yn(b):
        return "holds" if b else "fails"
    return (f"R3's criterion 1 {yn(crit.get('criterion1_agreement_of_conclusion'))}, "
            f"criterion 2 {yn(crit.get('criterion2_overlap_of_estimate'))}.")


def table_sensitivity(S: Input) -> tuple[str, list]:
    se = ("sensitivities", "seasonality")
    mo = se + ("month_of_year_decomposition",)
    h = S.get(*se, "mean_H1_minus_H2_2016_2024")
    hiv = S.get(*se, "mean_H1_minus_H2_2016_2024", "interval95")
    seasonal = (f"Mean of January--June minus July--December: {pts(h['value'])} points "
                + labelled_interval(hiv.get("low"), hiv.get("high"), r"95\% bootstrap interval") + ".")
    cm = (f"$C_m$ = {pts(S.get(*mo, 'C_m'))} points; $T$ = {pts(S.get(*mo, 'T'))} points; "
          r"$0.20 \times |T|$ = " + fixed(S.get(*mo, "0.20_x_abs_T"), 2, 100) + r"; $C_m/T$ = "
          + m(fixed(S.get(*mo, "C_m_over_T"), 4)) + " (a common trend would give "
          + m(fixed(S.get(*mo, "ratio_a_common_trend_would_produce"), 4)) + ").")
    wf = ("sensitivities", "word_floor_25")
    t1 = ("sensitivities", "tier_strata", "tier1", "trend")
    t2 = ("sensitivities", "tier_strata", "tier2", "trend")
    t4 = ("thread_size_R4",)
    q = S.get("rq1")
    rule = S.get("temporal_calibration_check_rule")
    div = rule.get("difference_interval95_per_year") or {}
    temporal = (criteria_text(rule.get("criteria_block_specific_against_primary"))
                + " Difference in Sen's slope (block-specific minus primary): "
                + pts(S.get("temporal_calibration_check_rule",
                            "difference_in_sen_slope_per_year_block_specific_minus_primary"))
                + " points per year " + labelled_interval(div.get("low"), div.get("high"), r"95\% bootstrap interval")
                + ".")
    r4 = (f"$C$ = {pts(S.get(*t4, 'C'))} points, $T$ = {pts(S.get(*t4, 'T'))} points (classified shares, 2016--2024); "
          r"$|C|$ = " + fixed(S.get(*t4, "abs_C"), 2, 100) + r", $0.20 \times |T|$ = "
          + fixed(S.get(*t4, "0.20_x_abs_T"), 2, 100) + r", $0.50 \times |T|$ = "
          + fixed(S.get(*t4, "0.50_x_abs_T"), 2, 100) + r"; $C/T$ = " + m(fixed(S.get(*t4, "C_over_T"), 4))
          + " (a common trend would give " + m(fixed(S.get(*t4, "ratio_a_common_trend_would_produce"), 4))
          + "). Size-stratified series: " + pts(S.get(*t4, "size_stratified_series", "trend_8_x_sen_slope"))
          + r" points over the span, $p$ = " + p_cell(S, t4 + ("size_stratified_series", "trend")) + ".")
    rows = [
        ("C", "1", "Seasonality: first against second half-year, 2016--2024 (description)", seasonal,
         "Decides nothing: reported as description (Deviation 13)."),
        ("C", "1", r"Seasonality: month-of-year decomposition, $C_m$ against $0.20 \times |T|$", cm, cm_outcome(S)),
        ("C", "2", "Word floor of 25 words", trend_summary(S, wf + ("trend",)) + ". "
         + criteria_text(S.get(*wf, "criteria")), exploratory_outcome(S, wf)),
        ("C", "3", "Tier strata: Tier 1 and Tier 2 separately",
         "Tier 1: " + trend_summary(S, t1) + ". Tier 2: " + trend_summary(S, t2) + ".",
         "No criterion is applied (Deviation 13)."),
        ("R", "", "Pooled series against the reweighted series (R3)",
         trend_summary(S, ("rq1", "pooled_series", "trend")) + ". " + criteria_text(q["pooled_series"].get("criteria")),
         tex(statement_body(S.get("rq1", "pooled_series", "statement")))),
        ("R", "", "Companion series: the subreddits retained in every year (Deviation 13)",
         trend_summary(S, ("rq1", "companion_series", "trend")) + ". "
         + criteria_text(q["companion_series"].get("criteria")),
         tex(statement_body(S.get("rq1", "companion_series", "statement")))),
        ("R", "", "Tier-level reweighting (R3)", trend_summary(S, ("rq1", "tier_level_series", "trend")) + ".",
         "Reported as the robustness check R3 names; no criterion is applied (Deviation 13)."),
        ("R", "", "Three-class correction, CONCERN component (exploratory)",
         trend_summary(S, ("rq1", "three_class_correction", "trend")) + ". "
         + criteria_text(q["three_class_correction"].get("criteria")),
         exploratory_outcome(S, ("rq1", "three_class_correction"))),
        ("R", "", "Thread-size composition (R4)", r4, r4_outcome(S)),
        ("R", "", "Temporal calibration check: block-specific against primary series", temporal,
         tex(S.get("temporal_calibration_check_rule", "statement"))),
    ] + [("N", "", tex(a), tex(b), "--") for a, b in NOT_RUN]
    heads = {"C": "Family C sensitivities (exploratory; Deviation 13)",
             "R": "Comparisons under R3 and R4, and the temporal calibration check",
             "N": "Planned in the project's design and not run (Deviation 13)"}
    L = [r"{\small", rf"\begin{{longtable}}{{{SENSITIVITY_SPEC}}}",
         r"  \caption{Sensitivity Analyses}\label{tab:sensitivity}\\",
         r"  \toprule", "  " + SENSITIVITY_HEADER, r"  \midrule", r"  \endfirsthead",
         r"  \toprule", "  " + SENSITIVITY_HEADER, r"  \midrule", r"  \endhead",
         r"  \bottomrule", r"  \endfoot"]
    seen = set()
    for group, no, analysis, result, outcome in rows:
        if group not in seen:
            if seen:
                L.append(r"  \midrule")
            L.append(rf"  \multicolumn{{4}}{{@{{}}l}}{{\textit{{{heads[group]}}}}} \\")
            seen.add(group)
        L.append(f"  {no} & {analysis} & {result} & {outcome} \\\\")
    L += [r"\end{longtable}", "}"]
    return "\n".join(L) + "\n", \
        ["series_results.json: sensitivities.seasonality.{mean_H1_minus_H2_2016_2024, month_of_year_decomposition}; "
         "sensitivities.word_floor_25.{trend, criteria, statement}; sensitivities.tier_strata.{tier1, tier2}.trend; "
         "rq1.{pooled_series, companion_series, tier_level_series, three_class_correction}.{trend, criteria, "
         "statement}; thread_size_R4; temporal_calibration_check_rule",
         "Deviation 13 (constants in this file): the analyses not run, and their reasons"]


def table_criteria(E: Input, S: Input, P: Input) -> tuple[str, list]:
    rel = ("reliability", "both tranches (200 items)")
    a1 = Fraction(E.get(*rel, "Stage 1", "alpha_exact"))
    a2 = Fraction(E.get(*rel, "Stage 2", "alpha_exact"))
    met1 = a1 >= Fraction(7, 10) and a2 >= Fraction(7, 10)
    if ("met" if met1 else "not met") != E.get("success_criteria", "1", "result"):
        stop(f"evaluation_results.json: success criterion 1 does not follow from the alphas it records. {REPORT}")
    below = [(k, Fraction(E.get(*rel, k, "alpha_exact"))) for k, _ in RELIABILITY_MEASURES[2:]
             if Fraction(E.get(*rel, k, "alpha_exact")) < Fraction(7, 10)]
    out1 = (("Met" if met1 else "Not met") + f": Stage 1 $\\alpha$ {fixed(a1, 3)}, Stage 2 $\\alpha$ {fixed(a2, 3)}"
            + ("; per-class $\\alpha$ below 0.7: " + ", ".join(f"{tex(k)} {fixed(a, 3)}" for k, a in below) if below
               else "; no per-class $\\alpha$ below 0.7") + ".")
    s2 = E.get("stage2", "configurations")
    complete = [c for c in s2 if s2[c].get("cost_usd_per_1000_comments") is not None
                and s2[c].get("refusal_rate_all_items") is not None]
    out2 = (f"Recorded as {tex(E.get('success_criteria', '2', 'result'))} in the evaluation of record: a cost per "
            f"1,000 items and a refusal rate for "
            + (f"all {len(s2)} configurations." if len(complete) == len(s2) else
               f"{len(complete)} of the {len(s2)} configurations."))
    tm = Fraction(E.get("stage2", "prevalence_correction_error_rates", "weighted", "tpr_minus_fpr_exact"))
    met6 = tm >= Fraction(1, 4)
    if ("met" if met6 else "not met") != E.get("success_criteria", "6", "result"):
        stop(f"evaluation_results.json: success criterion 6 does not follow from the rates it records. {REPORT}")
    out6 = (("Met" if met6 else "Not met") + f": TPR $-$ FPR {fixed(tm, 3)} for "
            + tex(E.get("stage2", "configurations", E.get("success_criteria", "6", "configuration"), "name"))
            + " on the primary item set, weighted as the correction uses it (unweighted "
            + fixed(E.get("success_criteria", "6", "unweighted"), 3) + ").")
    ps = S.get("rq1", "primary_series")
    span = [r for r in ps["rows"] if int(str(r.get("period"))[:4]) <= 2024]      # 2016 Q1 to 2024 Q4 (R3)
    pt = S.get("rq1", "primary_series", "trend")
    if len(span) != pt.get("values", 0) + pt.get("periods_without_value", 0):
        stop(f"series_results.json: the primary series' quarters of 2016-2024 do not match its trend. {REPORT}")
    with_iv = sum(1 for r in span if (r.get("interval95") or {}).get("low") is not None)
    tested = list(S.get("rq2", "family_A", "tests"))
    series_file, sample_file = r"\path{results/series_results.json}", r"\path{results/sample_results.json}"
    out3 = (f"Reported: the corrected primary series with a 95\\% interval for {with_iv} of its {len(span)} quarterly "
            f"values, 2016 Q1 to 2024 Q4, and the subsystem measures $\\pi_s$, $C_s$ and $E_s$ under Deviation 9's "
            f"sparsity rule, with Family A of {len(tested)} test{'s' if len(tested) != 1 else ''} ({series_file}); the "
            f"design-weighted subsystem shares on the pooled sample ({sample_file}).")
    br = list(P.get("temporal_calibration_check", "block_rates"))
    if br != ["both tranches", "tranche 1", "tranche 2"]:
        stop(f"sample_results.json: the block rates are not those of both tranches and of each alone. {REPORT}")
    out4 = (f"Reported on both tranches together and on each alone ({sample_file}), and the block-specific series "
            f"against the primary series ({series_file}).")
    rr = P.get("prevalence", "pooled", "relevance_rate", "overall")
    out5 = (f"Reported: {pct(Fraction(rr['estimate_exact']))}\\% [95\\% interval {pct(rr['low'])} to "
            f"{pct(rr['high'])}], design-weighted, beside the composition check and the text-only sensitivity "
            f"({sample_file}).")
    rows = [["1", CRITERIA["1"], out1], ["2", CRITERIA["2"], out2], ["3", CRITERIA["3"], out3],
            ["4", CRITERIA["4"], out4], ["5", CRITERIA["5"], out5], ["6", CRITERIA["6"], out6]]
    spec = "@{}" + col("0.04") + col("0.46") + col("0.44") + "@{}"
    return tabular(spec, ["", "Criterion (Deviation 12, fixed before the model runs)", "Outcome"], rows), \
        ["evaluation_results.json: success_criteria.{1, 2, 6}; reliability.both tranches (200 items).*.alpha_exact; "
         "stage2.prevalence_correction_error_rates.weighted.tpr_minus_fpr_exact; stage2.configurations.*.{"
         "cost_usd_per_1000_comments, refusal_rate_all_items, name}",
         "series_results.json: rq1.primary_series.rows[].interval95.low; rq2.family_A.tests",
         "sample_results.json: temporal_calibration_check.block_rates; prevalence.pooled.relevance_rate.overall",
         "Deviation 12 (constants in this file): the six criteria, word for word"]


# =============================================================================
# the figures
# =============================================================================
def make_figures(E: Input, P: Input, C: Input) -> tuple[dict, dict]:
    """Each figure as PDF and PNG bytes, deterministic: the PDF carries no creation date (its creator and producer are
    matplotlib's fixed version string) and the PNG no software stamp. Each figure is drawn at the size of its slot in
    the report (17 cm wide; 7 cm or 6.5 cm high), so that it is printed at a scale of about 1: text 8 pt, value labels
    7 pt."""
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcdefaults()                        # no matplotlibrc can change the figures
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
                         "legend.fontsize": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "savefig.dpi": 200, "axes.edgecolor": INK, "xtick.color": INK,
                         "ytick.color": INK, "axes.labelcolor": INK, "text.color": INK})
    width = 170 / 25.4                             # the report's text width, 170 mm, in inches
    files, sources = {}, {}

    def save(fig, name):
        for fmt in ("pdf", "png"):
            buf = io.BytesIO()
            fig.savefig(buf, format=fmt, metadata={"CreationDate": None} if fmt == "pdf" else {"Software": None})
            files[f"{name}.{fmt}"] = buf.getvalue()
        plt.close(fig)

    # a. per-class F1 by configuration (slot 17 x 7 cm)
    deployed = E.get("stage2", "deployment", "deployed")
    labels = []
    for c in STAGE2_CONFIGS:
        model, schema = split_name(c, E.get("stage2", "configurations", c, "name"))
        model = model.replace("Claude ", "Claude\n")
        lab = model + "\n" + ("fine-tuned" if schema == "--" else
                              "universal" if schema == "Universal" else "domain\u2020")
        labels.append(lab + ("\n(deployed)" if c == deployed else ""))
    fig, ax = plt.subplots(figsize=(width, 7 / 2.54 - 0.01), layout="constrained")
    x = np.arange(len(STAGE2_CONFIGS), dtype=float)
    w = 0.26
    handles = []
    for j, k in enumerate(CLASSES):
        exact_f1 = [E.get("stage2", "configurations", c, "pooled", "per_class", k, "f1_exact") for c in STAGE2_CONFIGS]
        vals = [float(Fraction(v)) for v in exact_f1]
        sds = [float(E.get("stage2", "configurations", c, "folds", k, "sd")) for c in STAGE2_CONFIGS]
        handles.append(ax.bar(x + (j - 1) * w, vals, width=w * 0.94, color=FIGURE_COLOURS[j], edgecolor="white",
                              linewidth=0.5, label=k, yerr=sds, capsize=1.5,
                              error_kw={"elinewidth": 0.6, "capthick": 0.6, "ecolor": INK}))
        for i, (v, sd, ex) in enumerate(zip(vals, sds, exact_f1)):
            if v < 0.05:                           # a bar this low would look missing: its value is printed above it
                ax.text(x[i] + (j - 1) * w, v + sd + 0.015, fixed(ex, 3), rotation=90, ha="center", va="bottom",
                        fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.55, len(STAGE2_CONFIGS) - 0.45)
    ax.set_ylim(0, 1)
    ax.set_ylabel(f"F1 on the {E.get('item_sets', 'stage2_primary', 'items')} items")
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    note = Line2D([], [], linestyle="none", label="\u2020 Domain-specific schema: exploratory (Family C)")
    fig.legend(handles=handles + [note], loc="outside lower center", ncol=4, handlelength=1.2, columnspacing=1.2)
    save(fig, "stage2_per_class_f1")
    sources["stage2_per_class_f1"] = ["evaluation_results.json: stage2.configurations.*.pooled.per_class.*.f1_exact "
                                      "(bars; printed above a bar below 0.05), stage2.configurations.*.folds.*.sd "
                                      "(error bars: one SD over the five folds), stage2.configurations.*.name, "
                                      "stage2.deployment.deployed"]

    # b. composition of the Tier 1+2 comments by year (slot 17 x 6.5 cm)
    counts = {g: [C.get("composition_by_year", "comments_by_subreddit_and_year", g, y) for y in YEARS]
              for g in SUBREDDITS8}
    totals = [sum(counts[g][i] for g in SUBREDDITS8) for i in range(len(YEARS))]
    for i, y in enumerate(YEARS):
        if totals[i] != C.get("year_totals", "by_year", y, "tier_1_and_2"):
            stop(f"corpus_results.json: the subreddit counts of {y} do not add up to its Tier 1+2 total. {REPORT}")
        for g in SUBREDDITS8:
            recorded = C.get("composition_by_year", "share_of_tier_1_and_2_comments_by_year", y, g)
            if abs(float(ratio(counts[g][i], totals[i])) - float(recorded)) > 5e-7:
                stop(f"corpus_results.json: the share of {g} in {y} does not follow from its counts. {REPORT}")
    names = C.get("corpus", "subreddit_display_names")
    fig, ax = plt.subplots(figsize=(width, 6.5 / 2.54 - 0.01), layout="constrained")
    xs = np.arange(len(YEARS), dtype=float)
    bottom = np.zeros(len(YEARS))
    handles = []
    for j, g in enumerate(SUBREDDITS8):
        share = np.array([100.0 * float(ratio(counts[g][i], totals[i])) for i in range(len(YEARS))])
        tier = C.get("corpus", "tier_of_subreddit", g)
        handles.append(ax.bar(xs, share, bottom=bottom, width=0.72, color=FIGURE_COLOURS[j], edgecolor="white",
                              linewidth=0.6, label=f"r/{names[g]} ({tier})"))
        bottom += share
    ax.set_xticks(xs)
    ax.set_xticklabels([y if y != "2025" else "2025\n(Jan\u2013Apr)" for y in YEARS])
    ax.set_xlim(-0.6, len(YEARS) - 0.4)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of the year's\nTier 1+2 comments (%)")
    fig.legend(handles=handles[::-1], loc="outside right center", ncol=1)    # top of the legend = top of the stack
    save(fig, "composition_by_year")
    sources["composition_by_year"] = ["corpus_results.json: composition_by_year.comments_by_subreddit_and_year "
                                      "(shares of the counts), checked against composition_by_year."
                                      "share_of_tier_1_and_2_comments_by_year and year_totals.by_year.*.tier_1_and_2; "
                                      "corpus.subreddit_display_names, corpus.tier_of_subreddit"]

    # c. relevance rate by era, with and without the subreddit rule (slot 17 x 6.5 cm)
    series = [
        ("Gold labels, all eight subreddits (codebook rule, subreddit rule included)",
         ("prevalence", "pooled", "relevance_rate"), "o", "full"),
        ("Gold labels, the six broad subreddits (relevance judged from the text; exploratory)",
         ("text_only_sensitivity", "b_gold_labels_in_the_six_subreddits", "rates"), "s", "full"),
        ("Text-only Stage 1 classifier, cross-validated, all eight subreddits (exploratory)",
         ("text_only_sensitivity", "a_text_only_variant_cross_validated_predictions", "rates"), "^", "none"),
    ]
    fig, ax = plt.subplots(figsize=(width, 6.5 / 2.54 - 0.01), layout="constrained")
    handles = []
    for j, (label, path, marker, fill) in enumerate(series):
        est, lo, hi = [], [], []
        for era in ERAS:
            est.append(100.0 * float(Fraction(P.get(*path, era, "estimate_exact"))))
            lo.append(100.0 * float(P.get(*path, era, "low")))
            hi.append(100.0 * float(P.get(*path, era, "high")))
        xs = np.arange(len(ERAS)) + (j - 1) * 0.16
        est_a = np.array(est)
        handles.append(ax.errorbar(xs, est_a, yerr=[est_a - np.array(lo), np.array(hi) - est_a], fmt=marker, ms=5,
                                   color=FIGURE_COLOURS[j], mfc=FIGURE_COLOURS[j] if fill == "full" else "white",
                                   mec=FIGURE_COLOURS[j], elinewidth=0.9, capsize=2, capthick=0.9, label=label))
    ax.set_xticks(np.arange(len(ERAS)))
    ax.set_xticklabels([e.replace("-", "\u2013") for e in ERAS])
    ax.set_xlim(-0.6, len(ERAS) - 0.4)
    ax.set_ylim(30, 80)
    ax.set_ylabel("Relevance rate,\ndesign-weighted (%)")
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.legend(handles=handles, loc="outside lower center", ncol=1)
    save(fig, "relevance_by_era")
    sources["relevance_by_era"] = ["sample_results.json: prevalence.pooled.relevance_rate.<era>.{estimate_exact, low, "
                                   "high}; text_only_sensitivity.b_gold_labels_in_the_six_subreddits.rates.<era>; "
                                   "text_only_sensitivity.a_text_only_variant_cross_validated_predictions.rates.<era>"]
    return files, sources


def cost_breakeven_figure(costs: dict) -> dict:
    """Hook for the cost break-even figure (design decision D17). Not drawn by this file: its inputs (annotation
    minutes, the hourly rate and the spend in Australian dollars) are not yet recorded. A later script adds it,
    committed before it runs, reading those inputs from a file with a SHA-256 of record."""
    raise NotImplementedError("the cost break-even figure is not drawn by analysis_04_tables.py")


# =============================================================================
# building and writing
# =============================================================================
def build(loaded: dict) -> tuple[dict, dict, dict]:
    E, P, C, S = (loaded[k] for k in ("evaluation_results.json", "sample_results.json", "corpus_results.json",
                                      "series_results.json"))
    M = loaded["models_config.py"]
    tables, sources = {}, {}
    for name, (text, src) in (("funnel.tex", table_funnel(C)), ("models.tex", table_models(E, M)),
                              ("reliability.tex", table_reliability(E, P)), ("stage2.tex", table_stage2(E)),
                              ("trends.tex", table_trends(S)), ("family_a.tex", table_family_a(S)),
                              ("sensitivity.tex", table_sensitivity(S)),
                              ("criteria.tex", table_criteria(E, S, P))):
        head = (f"% {name}: written by {SCRIPT} from the results files of record; do not edit by hand.\n"
                f"% Sources: " + " | ".join(src) + "\n")
        tables[name] = head + text
        sources[f"tables/{name}"] = src
    figures, fsrc = make_figures(E, P, C)
    for k, v in fsrc.items():
        sources[f"figures/{k}.pdf"] = sources[f"figures/{k}.png"] = v
    return tables, figures, sources


def write_outputs(tables: dict, figures: dict, sources: dict, me: str, out_dir: Path, inputs: dict,
                  libs: dict) -> None:
    """Written to a fresh work folder, then moved into place with the manifest last: a run that fails part-way leaves
    no manifest, so it can simply be run again (it gives the same bytes)."""
    work = OUT_ROOT / f"in_progress_{os.getpid()}_{time.time_ns()}"
    (work / "tables").mkdir(parents=True)
    (work / "figures").mkdir()
    try:
        outputs = {}
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
        write_json(work / "tables_manifest.json", {
            "created": created, "script": {"file": SCRIPT, "sha256_lf": me}, "inputs_sha256": inputs,
            "outputs_sha256": outputs, "sources": sources, "versions": versions})
        out_dir.mkdir(parents=True, exist_ok=True)
        for sub in ("tables", "figures"):
            (out_dir / sub).mkdir(exist_ok=True)
            for name in sorted(os.listdir(work / sub)):
                replace_patiently(work / sub / name, out_dir / sub / name)
        replace_patiently(work / "tables_manifest.json", out_dir / "tables_manifest.json")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rel = out_dir.relative_to(REPO).as_posix()
    man_sha = hashlib.sha256((out_dir / "tables_manifest.json").read_bytes()).hexdigest()
    show_register_block(out_dir / "PASTE_tables_block.txt", [
        f"- `{SCRIPT}` (SHA-256 `{me}`) run {created} with `--confirm-committed`: every input matched its SHA-256 of "
        f"record (`evaluation_results.json`, `results/sample_results.json`, `results/corpus_results.json`, "
        f"`results/series_results.json`, `models_config.py`).",
        f"- Outputs, in `{rel}/` (not committed; copied to `results/report_tables/` and `results/report_figures/`): "
        f"{len(tables)} table files and {len(figures)} figure files, with their SHA-256 in `tables_manifest.json` "
        f"`{man_sha}`. Python {versions['python']}, NumPy {versions['numpy']}, matplotlib {versions['matplotlib']}.",
    ])
    print(f"\nwritten: {out_dir}")
    print("Next: copy its tables folder to results/report_tables/ and its figures folder to results/report_figures/.")


# =============================================================================
# main
# =============================================================================
def main() -> None:
    setup_console()
    ap = argparse.ArgumentParser(description="Report tables and data figures from the results files of record.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks and a build; writes nothing")
    mode.add_argument("--confirm-committed", action="store_true", help="the run of record (after the commit)")
    args = ap.parse_args()
    if not (args.preflight or args.confirm_committed):
        stop("choose one: --preflight (before the commit) or --confirm-committed (after the commit: the run of record)")
    started = time.time()
    print("Report tables and figures: " + ("preflight, before the commit\n" if args.preflight else "the run of record\n"))
    me = own_sha256()
    out_dir = run_folder(me)
    print(f"this script: {SCRIPT} SHA-256 {me}")
    if (out_dir / "tables_manifest.json").exists():
        stop(f"this script's tables have already been written: they are in {out_dir}. They are written once.")
    libs = check_libraries()
    print(f"libraries: {', '.join(f'{n} {v}' for n, v in libs.items())}")
    loaded, shas = load_inputs()
    print("inputs: all five match their SHA-256 of record (evaluation_results.json, sample_results.json, "
          "corpus_results.json, series_results.json, models_config.py)")
    tables, figures, sources = build(loaded)
    print(f"built: {len(tables)} tables and {len(figures) // 2} figures (PDF and PNG)")
    if args.preflight:
        print(f"\nPREFLIGHT PASSED: every input matches the record and every table and figure can be built. "
              f"No output was written ({time.time() - started:.0f} seconds).")
        return
    write_outputs(tables, figures, sources, me, out_dir, shas, libs)
    print(f"({time.time() - started:.0f} seconds)")


if __name__ == "__main__":
    main()
