"""Illustrative comments for the report: a random draw of human-labelled comments in four groups, from which the
author takes one short quote per group for a table (docs/decision_register.md, the entry that commits this file).

From the repository folder, with the virtual environment active (no GPU, no internet):
    python quotes_01_draw.py
It runs no model and sends nothing. It writes data/analysis/quotes/quote_candidates.csv, which holds comment text
and is not committed, and prints the number of comments in each group and the file's SHA-256.

Rules fixed with this file
  1. The comments are the 598 annotated items with a gold Stage 2 class (Deviation 12), read and checked by
     analysis_01_sample.load_all; their year, subreddit and tier come from corpus v2.2, checked by
     analysis_01_sample.load_corpus_items.
  2. Groups, by the gold labels: (1) CONCERN with the gold primary subsystem sensing; (2) CONCERN with the gold
     primary subsystem none; (3) CONCERN with any other gold primary subsystem (in-vehicle networks, V2X,
     cybersecurity, privacy, data governance); (4) ENDORSEMENT, whatever the subsystem. An item without a gold
     primary subsystem is in no CONCERN group.
  3. In group g, 8 comments are drawn without replacement with numpy.random.default_rng([24916660, 16, g]) over the
     group's ids sorted as strings in code-point order (a group with fewer than 8 gives all of them), and are listed
     in the order drawn.
  4. The file holds, for each comment drawn: the group, the order drawn, the id, the year, the subreddit, the tier,
     the number of words and the text as the annotators saw it (clean_body).
  5. From these, one quote of at most 15 consecutive words (the project's ethics commitments allow no verbatim
     quotation longer than fifteen words) is taken from one comment of each group used, word for word; quotes are
     illustrative only, give no figure, and are shown without usernames.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

import numpy as np

import analysis_01_sample as sample
import models_01_prepare as prep
import models_05_evaluate as ev
import models_common as mc
import models_config as cfg

SCRIPT = "quotes_01_draw.py"
REPORT = "Report this message before going further."
MODULES_OF_RECORD = {                             # SHA-256 with LF line endings: the files in the repository at aff4276
    "models_config.py": "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a",
    "models_common.py": "65e7cbdef6c7594fabc71cb0b0f8bf22774e64749205fbbba3e7a18de1e57980",
    "models_01_prepare.py": "bb50327400d5e53d2633205bdd380fad9364affb35bdb072e143ed219a6074e0",
    "models_05_evaluate.py": "98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734",
    "analysis_01_sample.py": "95f7a48c7509c58eca11330814be32fef0a8c1e430447790fdccfa5da6fdd952",
}
SEED = [cfg.SEED, 16]                             # rule 3: numpy.random.default_rng([24916660, 16, g])
PER_GROUP = 8
OTHER_SUBSYSTEMS = ["in_vehicle_networks", "v2x", "cybersecurity", "privacy", "data_governance"]
GROUPS = [                                        # rule 2: (number, name, gold class, gold primary subsystems or None)
    (1, "concern, sensing", "CONCERN", ["sensing"]),
    (2, "concern, no specific subsystem", "CONCERN", ["none"]),
    (3, "concern, another subsystem", "CONCERN", OTHER_SUBSYSTEMS),
    (4, "endorsement", "ENDORSEMENT", None),
]
OUT = cfg.REPO / "data" / "analysis" / "quotes" / "quote_candidates.csv"
COLUMNS = ["group", "group_name", "order_drawn", "id", "year", "subreddit", "tier", "words", "text"]
EXPECTED_ITEMS = 598                              # models_05_evaluate.GOLD_ITEMS["stage2"]


def stop(message: str) -> None:
    mc.stop(message)


def check_modules() -> None:
    for module in (cfg, mc, prep, ev, sample):
        path = Path(module.__file__).resolve()
        want = MODULES_OF_RECORD.get(path.name)
        got = mc.text_sha256(path.read_bytes().decode("utf-8").replace("\r\n", "\n"))
        if got != want:
            stop(f"{path.name} is not the file in the repository at aff4276 (SHA-256 {got[:16]}...). {REPORT}")


def draw(ids: list, g: int) -> list:
    ids = sorted(ids)
    if len(ids) <= PER_GROUP:
        return ids
    pick = np.random.default_rng([*SEED, g]).choice(len(ids), PER_GROUP, replace=False)
    return [ids[int(k)] for k in pick]


def main() -> None:
    mc.setup_console()
    print(f"Illustrative comments: the draw\nthis script: {SCRIPT}")
    check_modules()
    data = sample.load_all()["data"]
    ids = list(data["ids"])
    prim = data["prim"]
    if int(prim.sum()) != EXPECTED_ITEMS:
        stop(f"{int(prim.sum())} annotated items have a gold Stage 2 class; the record has {EXPECTED_ITEMS}. {REPORT}")
    items, _ = sample.load_corpus_items(ids)
    pos = {i: k for k, i in enumerate(ids)}
    rows, counts = [], {}
    for g, name, cls, subs in GROUPS:
        members = [i for k, i in enumerate(ids) if prim[k] and data["g2"][k] == cls
                   and (subs is None or data["gsub"][k] in subs)]
        counts[name] = len(members)
        for order, i in enumerate(draw(members, g), start=1):
            text = str(data["text"][pos[i]])
            rows.append([g, name, order, i, int(items.at[i, "year"]), "r/" + str(data["sub"][pos[i]]),
                         str(items.at[i, "tier"]), len(text.split()), text])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    w.writerows(rows)
    OUT.write_bytes(buf.getvalue().encode("utf-8"))
    print("comments in each group (gold labels): " + "; ".join(f"{n} {c}" for n, c in counts.items()))
    print(f"drawn: {len(rows)} comments, at most {PER_GROUP} a group; years "
          f"{min(r[4] for r in rows)}-{max(r[4] for r in rows)}")
    print(f"written: {OUT.relative_to(cfg.REPO).as_posix()} SHA-256 {mc.sha256_file(OUT)} (comment text: not "
          f"committed)")
    print("\nDRAW DONE. Attach this file to the chat with Claude; do not commit it.")


if __name__ == "__main__":
    main()
