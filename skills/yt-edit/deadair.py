#!/usr/bin/env python3
"""deadair.py - turn a raw recording's transcript into an edit decision list. Russian and English.

    python3 deadair.py transcript.srt               # .srt, .vtt, Whisper JSON or YouTube json3
    python3 deadair.py transcript.srt --floor 0.6   # shortest pause worth cutting, seconds
    python3 deadair.py transcript.srt --json
    python3 deadair.py transcript.srt --csv cuts.csv

It finds three kinds of cut:
    DEAD     a pause longer than the floor. Trimmed from the middle, leaving a breath on both
             sides: cutting flush against speech makes a tightened take sound gasping
    FILLER   a cue that is nothing but filler: "ну", "короче", "типа", "um", "so yeah"
    RETAKE   a sentence started again: compared with the last real line, not the literal
             previous cue, because most retakes have an "эээ" between the two attempts

It prints the cuts; you apply them in your editor. It never touches media, and it cannot see
silent B-roll or a demo with no talking: check the report against the footage before trusting
the runtime at the bottom.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ruen  # noqa: E402
import subs  # noqa: E402

BREATH = 0.15


def norm(text):
    return " ".join(ruen.words(text))


def is_filler(text, lg):
    w = ruen.words(text)
    if not w:
        return True
    rest = norm(text)
    for f in sorted(ruen.FILLERS[lg], key=len, reverse=True):
        rest = re.sub(r"(?<!\w)%s(?!\w)" % re.escape(f), " ", rest)
    rest = re.sub(r"\b(э+|м+|а+|ээм|эм|uh+|um+|hmm+|ну да|вот так|so yeah)\b", " ", rest)
    return not rest.strip()


def similar(a, b):
    wa, wb = ruen.words(a), ruen.words(b)
    if len(wa) < 3 or len(wb) < 3:
        return False
    k = min(4, len(wa), len(wb))
    return wa[:k] == wb[:k]


def decide(cues, floor=0.6):
    if not cues:
        return {"cuts": [], "total": 0, "kept": 0, "lang": "ru"}
    lg = ruen.lang(" ".join(c["text"] for c in cues))
    cuts = []
    last_real = None
    for i, c in enumerate(cues):
        if i:
            gap = c["start"] - cues[i - 1]["end"]
            if gap > floor:
                cuts.append({"kind": "DEAD", "start": cues[i - 1]["end"] + BREATH,
                             "end": c["start"] - BREATH, "text": "%.1fs pause" % gap})
        if is_filler(c["text"], lg):
            cuts.append({"kind": "FILLER", "start": c["start"], "end": c["end"], "text": c["text"]})
            continue
        if last_real is not None and similar(cues[last_real]["text"], c["text"]):
            prev = cues[last_real]
            cuts.append({"kind": "RETAKE", "start": prev["start"], "end": prev["end"],
                         "text": "keep the second take: " + prev["text"][:60]})
        last_real = i
    cuts = [x for x in cuts if x["end"] > x["start"]]
    cuts.sort(key=lambda x: x["start"])
    merged = []
    for x in cuts:
        if merged and x["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], x["end"])
            merged[-1]["kind"] += "+" + x["kind"] if x["kind"] not in merged[-1]["kind"] else ""
        else:
            merged.append(dict(x))
    total = cues[-1]["end"] - cues[0]["start"]
    removed = sum(x["end"] - x["start"] for x in merged)
    return {"cuts": merged, "total": round(total, 1), "kept": round(total - removed, 1), "lang": lg}


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    floor, out_csv = 0.6, None
    if "--floor" in a:
        i = a.index("--floor")
        floor = float(a[i + 1])
        del a[i:i + 2]
    if "--csv" in a:
        i = a.index("--csv")
        out_csv = a[i + 1]
        del a[i:i + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    r = decide(subs.load(a[0]), floor)
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["kind", "start", "end", "start_tc", "end_tc", "note"])
            for x in r["cuts"]:
                w.writerow([x["kind"], round(x["start"], 2), round(x["end"], 2),
                            subs.fmt(x["start"]), subs.fmt(x["end"]), x["text"]])
    print("EDIT DECISION LIST  %d cuts" % len(r["cuts"]))
    print("=" * 72)
    for x in r["cuts"]:
        print("  %-12s %8s - %-8s %5.1fs  %s" % (x["kind"], subs.fmt(x["start"]), subs.fmt(x["end"]),
                                                x["end"] - x["start"], x["text"][:40]))
    pct = 100 * (1 - r["kept"] / r["total"]) if r["total"] else 0
    print("-" * 72)
    print("  speech span %s, after cuts about %s (%.0f%% less). Check silent demos by eye."
          % (subs.fmt(r["total"]), subs.fmt(r["kept"]), pct))
    return 0


if __name__ == "__main__":
    sys.exit(main())
