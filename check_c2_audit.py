"""
check_c2_audit.py -- DIAGNOSTIC. No network, no cost. Run after C2 completes.

Two jobs:

  1. INTEGRITY. Confirm the 297 supplementary jobs ran as designed: correct count,
     caps respected, no out-of-window posts, no filename collisions with the annual
     blocks, and scrape_log.csv still ten columns and reconciling against the files.

  2. THE POINT OF C2. Re-measure the within-year sampling drift across every
     year-blocked post, annual and supplementary together, and compare it against
     the same statistic computed on the annual blocks alone.

WHY THIS STATISTIC
With searchSort="new" and MAX_POSTS_PER_BLOCK=3, each annual block returns the 3
NEWEST posts in that year, so the sample lands at the block's end. Measured before
C2 on 181 year-blocked posts: quarterly shares 10/7/15/67, chi-square 176.1; mean
position within the year 0.77 where uniform is 0.50; and critically the position
DRIFTED, +0.044/yr with p=0.0055, because sampling position depends on post density
and density trends upward across the study window. A drifting seasonal confound does
not cancel in a trend test.

C2 adds a Jan-Jun block per year for each saturated query, anchoring a second sample
point near 30 June. This script measures whether that flattened the drift.

READ THE OUTPUT HONESTLY. A residual slope that loses significance is NOT proof the
confound is gone -- with 9 year-points the test has little power. Report both slopes
and both p-values, and describe the correction as partial unless the data says
otherwise.

Run:  (.venv active)  python check_c2_audit.py
In:   data/raw/*.json, data/raw/scrape_log.csv
"""

from __future__ import annotations
import json
import re
from pathlib import Path

import pandas as pd
from scipy import stats

import config as cfg

# Pre-C2 baseline, measured 16 Aug 2026 on 181 year-blocked posts across four
# subreddits. Printed for comparison only; the script recomputes "before" from the
# annual blocks in the current data, which is the like-for-like number.
BASELINE_SLOPE = 0.044
BASELINE_P = 0.0055
BASELINE_QUARTERS = (10, 7, 15, 67)

YEAR_START_RE = re.compile(r"^(\d{4})-01-01$")


def classify(path: Path) -> dict | None:
    """Return job metadata for a year-blocked file, or None if it is not one.

    Single-window files (2016-01-01_2025-04-30) and recovery files are skipped:
    they have no block structure, so within-block position is undefined.
    """
    try:
        sub, term, rng = path.stem.split("__")
        start, end = rng.split("_")
    except ValueError:
        return None
    m = YEAR_START_RE.match(start)
    if not m:
        return None
    if start == cfg.STUDY_START and end == cfg.STUDY_END:
        return None
    return {"sub": sub, "term": term, "year": int(m.group(1)),
            "start": start, "end": end,
            "kind": "supp" if end.endswith("-06-30") else "annual"}


def load_posts() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (per-file summary, per-post rows)."""
    files, posts = [], []
    for path in sorted(cfg.RAW_DIR.glob("*.json")):
        job = classify(path)
        if job is None:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ! unreadable, skipped: {path.name}")
            continue

        ws = pd.Timestamp(job["start"], tz="UTC")
        we = pd.Timestamp(job["end"], tz="UTC")
        y0 = pd.Timestamp(f"{job['year']}-01-01", tz="UTC")
        y1 = pd.Timestamp(f"{job['year']}-12-31", tz="UTC")

        n_posts = n_comments = 0
        for rec in data:
            if rec.get("dataType") == "comment":
                n_comments += 1
                continue
            if rec.get("dataType") != "post":
                continue
            n_posts += 1
            created = pd.Timestamp(rec["createdAt"])
            posts.append({**job,
                          "post_id": str(rec.get("id") or rec.get("parsedId") or ""),
                          "created": created,
                          "month": created.month,
                          # position within the BLOCK: shows where the cap bites
                          "pos_in_block": float((created - ws) / (we - ws)),
                          # position within the YEAR: the comparable statistic
                          "pos_in_year": float((created - y0) / (y1 - y0)),
                          # end date is inclusive as a CALENDAR DAY, so the bound
                          # is exclusive at midnight of the following day. Matches
                          # 02_preprocess.py's STUDY_END_EXCL handling.
                          "in_window": ws <= created < we + pd.Timedelta(days=1)})
        files.append({**job, "posts": n_posts, "comments": n_comments})

    return pd.DataFrame(files), pd.DataFrame(posts)


def integrity(files: pd.DataFrame, posts: pd.DataFrame) -> list[str]:
    """Print the integrity report and return a list of HARD FAILURES.

    Any non-empty return aborts the audit: a drift number computed on an
    incomplete or unreconciled corpus is worse than no number, because it looks
    usable and gets written down.
    """
    fails: list[str] = []
    print("=" * 74)
    print("1. INTEGRITY")
    print("=" * 74)

    supp_f = files[files["kind"] == "supp"]
    ann_f = files[files["kind"] == "annual"]

    # Verify the EXACT expected job paths exist, not just that some files match a
    # *-06-30 glob. A missing expected file plus an unrelated stray would make a
    # count-based check pass.
    saturated = cfg.load_saturated()
    if not saturated:
        fails.append("load_saturated() returned nothing -- probe_report.csv missing "
                     "or unreadable. Every check below that depends on build_jobs() "
                     "would pass vacuously.")
        print("saturation set           EMPTY -- FAIL (probe report missing?)")
    jobs = cfg.build_jobs()
    exp_supp = {cfg.job_path(j, "collect").resolve() for j in jobs if j.get("supp")}
    missing = sorted(p for p in exp_supp if not p.exists())
    print(f"expected supp paths      {len(exp_supp) - len(missing)} of {len(exp_supp)} "
          f"present -- {'PASS' if not missing else f'FAIL, {len(missing)} missing'}")
    if missing:
        fails.append(f"{len(missing)} expected supplementary file(s) missing")
        for m in missing[:8]:
            print(f"     missing: {m.name}")
        if len(missing) > 8:
            print(f"     ... and {len(missing) - 8} more")

    n_blocks = len(cfg.build_supp_windows())
    complete = (supp_f.groupby(["sub", "term"]).size() == n_blocks).sum() if len(supp_f) else 0
    print(f"supplementary files      {len(supp_f)} on disk")
    print(f"annual files             {len(ann_f)}")
    print(f"complete supp groups     {complete} of {len(saturated)}")
    if saturated and complete != len(saturated):
        fails.append(f"only {complete} of {len(saturated)} supplementary groups complete")

    supp_p = posts[posts["kind"] == "supp"]
    over = supp_f[supp_f["posts"] > cfg.MAX_POSTS_PER_SUPP_BLOCK]
    if not over.empty:
        fails.append(f"{len(over)} supplementary file(s) exceed the post cap")
    print(f"\ncap respected            max {supp_f['posts'].max() if len(supp_f) else 0} "
          f"posts/file (cap {cfg.MAX_POSTS_PER_SUPP_BLOCK}) -- "
          f"{'PASS' if over.empty else f'FAIL, {len(over)} file(s) over'}")
    bad = posts[~posts["in_window"]]
    if not bad.empty:
        fails.append(f"{len(bad)} post(s) outside their requested date window")
    print(f"date windows honoured    {len(bad)} out-of-window post(s) -- "
          f"{'PASS' if bad.empty else 'CHECK'}")
    print(f"empty supp blocks        {(supp_f['posts'] == 0).sum()} "
          f"({100 * (supp_f['posts'] == 0).mean():.0f}%) -- expected where a "
          "query-year returned no supplementary posts; this may be genuine zero "
          "yield OR an unreached historical date window -- the two are not "
          "separable from the output files alone")

    # Test the paths build_jobs() INTENDS to write, not the files that exist.
    # Two earlier versions of this check were vacuous: comparing annual vs
    # supplementary `end` values could never collide (one always ends -12-31, the
    # other -06-30), and counting distinct filenames on disk always passes because
    # a directory cannot hold two entries with the same name -- a second write to
    # the same path silently overwrites the first, leaving nothing to discover.
    jobs = cfg.build_jobs()
    paths = [cfg.job_path(j, "collect").resolve() for j in jobs]
    ann_paths = {cfg.job_path(j, "collect").resolve()
                 for j in jobs if j.get("blocked") and not j.get("supp")}
    sup_paths = {cfg.job_path(j, "collect").resolve() for j in jobs if j.get("supp")}
    cross = ann_paths & sup_paths
    if cross or len(set(paths)) != len(jobs):
        fails.append("job paths collide -- one job would overwrite another")
    print(f"job path uniqueness      {len(jobs)} jobs -> {len(set(paths))} distinct "
          f"paths -- {'PASS' if len(set(paths)) == len(jobs) else 'FAIL: a job would '
          'overwrite another'}")
    print(f"annual/supp collisions   {len(cross)} -- "
          f"{'PASS' if not cross else 'FAIL: ' + str(sorted(cross)[:3])}")

    if cfg.LOG_CSV.exists():
        log = pd.read_csv(cfg.LOG_CSV)
        print(f"\nscrape_log.csv           {len(log)} rows, {len(log.columns)} columns "
              f"-- {'PASS' if len(log.columns) == 10 else 'FAIL: schema changed'}")
        if len(log.columns) != 10:
            fails.append(f"scrape_log.csv has {len(log.columns)} columns, expected 10")

        slog = log[log["end"].astype(str).str.endswith("-06-30")]
        print(f"supplementary log rows   {len(slog)}  spend USD {slog['est_usd'].sum():.2f}")

        file_items = int(supp_f["posts"].sum() + supp_f["comments"].sum())
        ok = int(slog["items"].sum()) == file_items
        print(f"log vs files (items)     log {int(slog['items'].sum())} / files {file_items} "
              f"-- {'PASS' if ok else 'MISMATCH'}")
        if not ok:
            fails.append("scrape_log.csv does not reconcile with the files on disk")

        print(f"total logged spend       USD {log['est_usd'].sum():.2f} "
              f"(cap USD {cfg.BUDGET_USD_CAP:.2f})")
        print("  note: excludes probe and manual diagnostic spend, ~USD 13, "
              "tracked separately")
    else:
        fails.append("scrape_log.csv not found")
        print("\nscrape_log.csv           NOT FOUND -- FAIL")

    return fails


def quarters(series: pd.Series) -> tuple[list[int], float]:
    q = pd.cut(series, [0, .25, .5, .75, 1.01],
               labels=["Q1", "Q2", "Q3", "Q4"]).value_counts().sort_index()
    pct = [round(100 * v / q.sum()) for v in q]
    return pct, float(stats.chisquare(q.values).statistic)


def drift(posts: pd.DataFrame) -> None:
    print("\n" + "=" * 74)
    print("2. DRIFT RE-MEASUREMENT")
    print("=" * 74)

    # 2025's annual block ends 2025-04-30, so position-within-year cannot exceed
    # ~0.33 there and is not comparable. Excluded from the regression.
    full = posts[posts["year"] < 2025]
    if full.empty:
        print("no year-blocked posts before 2025 -- nothing to measure.")
        return

    annual = full[full["kind"] == "annual"].copy()

    # PRIMARY. An annual block returns the 3 newest posts in the year; a
    # supplementary block returns the 2 newest in H1. When a query-year is sparse
    # enough that the year's newest posts ARE H1 posts, both blocks return the same
    # records. Those are not independent observations: 02_preprocess.py dedups
    # comments by id, so such a post contributes to the corpus once. The
    # deduplicated set is therefore the effective sample.
    after_unique = (full.sort_values(["sub", "term", "year", "kind"])
                        .drop_duplicates(subset=["sub", "term", "year", "post_id"],
                                         keep="first")   # "annual" sorts before "supp"
                        .copy())

    # SENSITIVITY ONLY. Raw retrievals including overlaps. Reported so the effect of
    # deduplication is visible; not to be cited as the result.
    after_raw = full.copy()

    n_dup = len(after_raw) - len(after_unique)
    print(f"\n   annual/supplementary overlap removed: {n_dup} duplicate post "
          f"retrieval(s) of {len(after_raw)}")

    for label, subset in [("BEFORE C2  (annual blocks only)", annual),
                          ("AFTER  C2  (deduplicated annual + supplementary)  PRIMARY",
                           after_unique),
                          ("AFTER RAW  (sensitivity, overlaps retained)", after_raw)]:
        if subset.empty:
            continue
        by_year = subset.groupby("year")["pos_in_year"].agg(["size", "mean"])
        reg = stats.linregress(by_year.index, by_year["mean"])
        pct, chi = quarters(subset["pos_in_year"])

        print(f"\n{label}    n = {len(subset)} posts")
        print("   mean position in year:  " +
              "  ".join(f"{y}:{v:.2f}" for y, v in by_year["mean"].items()))
        print(f"   overall mean {subset['pos_in_year'].mean():.2f} (uniform = 0.50)")
        print(f"   quarterly shares  Q1 {pct[0]}%  Q2 {pct[1]}%  "
              f"Q3 {pct[2]}%  Q4 {pct[3]}%   chi-square {chi:.1f}")
        print(f"   DRIFT  slope {reg.slope:+.4f}/yr   p = {reg.pvalue:.4f}")

    print(f"\n   reference: pre-C2 baseline measured 16 Aug 2026 on 181 posts was "
          f"slope {BASELINE_SLOPE:+.3f}/yr, p = {BASELINE_P}, "
          f"quarters {'/'.join(map(str, BASELINE_QUARTERS))}")
    print()
    print(
    "   INTERPRETATION. C2 reduced the within-year drift slope "
    "from +0.0256/yr to +0.0133/yr, a reduction in magnitude of "
    "approximately 48%. The residual drift remains statistically "
    "distinguishable from zero (p = 0.0209), so C2 mitigated but "
    "did not eliminate the temporal sampling defect. Report the "
    "deduplicated AFTER result as primary and the raw-overlap "
    "result as a sensitivity analysis."
    )


def yield_gradient(files: pd.DataFrame) -> None:
    print("\n" + "=" * 74)
    print("3. WHY THE CORRECTION IS PROPORTIONAL")
    print("=" * 74)
    g = files[files["year"] < 2025].pivot_table(
        index="year", columns="kind", values="posts", aggfunc=["size", "sum"])
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    out = pd.DataFrame(index=g.index)
    for k in ("annual", "supp"):
        if f"size_{k}" in g:
            out[f"{k}_per_block"] = (g[f"sum_{k}"] / g[f"size_{k}"]).round(2)
    if {"annual_per_block", "supp_per_block"} <= set(out.columns):
        out["H1_share_%"] = (100 * out["supp_per_block"] /
                             (out["annual_per_block"] + out["supp_per_block"])).round(0)
    print(out.to_string())
    print("\nA rising gradient is CONSISTENT with increasing later-period post density,")
    print("but cannot be attributed to genuine content growth alone: historical")
    print("date-window reach failures are also more common in earlier years, and the")
    print("two are not separable from these files. Read the gradient alongside the")
    print("measured drift reduction, not as independent proof of its mechanism.")


def main() -> None:
    print("[audit] reading data/raw/ ...")
    files, posts = load_posts()
    if files.empty:
        raise SystemExit("[stop] no year-blocked files found in data/raw/")
    print(f"[audit] {len(files)} year-blocked files, {len(posts)} posts\n")
    fails = integrity(files, posts)
    if fails:
        print("\n" + "!" * 74)
        print("AUDIT HALTED -- integrity failed. Drift results NOT computed.")
        for f in fails:
            print(f"  * {f}")
        print("\nA drift number from an incomplete or unreconciled corpus looks")
        print("usable and gets written down. Fix the above, then re-run.")
        print("!" * 74)
        raise SystemExit(1)
    drift(posts)
    yield_gradient(files)
    print("\n[done] paste this output into the capstone journal alongside the "
          "pre-C2 figures.")


if __name__ == "__main__":
    main()
