#!/usr/bin/env python3
"""chapters.py - YouTube chapters from a transcript, checked against YouTube's rules.

    python3 chapters.py transcript.srt --target 8
    python3 chapters.py --check chapters.txt       # validate a list you wrote by hand

YouTube only turns the list in a description into chapters when all three hold:
    the first timestamp is 0:00
    there are at least three timestamps, in ascending order
    every chapter lasts at least 10 seconds
Break any of them and the block just sits in the description doing nothing. This tool checks
all three and refuses to print an invalid list.

Boundaries are chosen at the pauses where the vocabulary changes most. The titles it prints are
the topic words of each section: a draft. Rewrite each as the promise of that section, three to
five words, in the channel's voice.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ruen  # noqa: E402
import subs  # noqa: E402

MIN_LEN = 10.0
STOP = set(("и в во не на с со что как а но это то же за к ко по из у о об от для до так вот "
            "ну он она они мы вы ты я его её их мне вам нам там тут уже ещё еще бы ли же "
            "есть был была было были будет если когда чтобы потому очень просто тоже "
            "the a an and or but to of in on at for is it this that with you i we they "
            "be are was were have has so just like").split())


def content(text):
    return [w for w in ruen.words(text) if len(w) > 3 and w not in STOP and not w.isdigit()]


def shift(left, right):
    a, b = set(left), set(right)
    if not a or not b:
        return 0.0
    return 1.0 - len(a & b) / float(len(a | b))


def boundaries(cues, target=8, window=6):
    if len(cues) < 6:
        return [0]
    total = cues[-1]["end"]
    min_gap = max(MIN_LEN, total / (target * 2.5))
    cand = []
    for i in range(1, len(cues)):
        pause = cues[i]["start"] - cues[i - 1]["end"]
        left = [w for c in cues[max(0, i - window):i] for w in content(c["text"])]
        right = [w for c in cues[i:i + window] for w in content(c["text"])]
        cand.append((shift(left, right) + min(pause, 2.0) * 0.25, i))
    cand.sort(reverse=True)
    picked = [0]
    for _, i in cand:
        t = cues[i]["start"]
        if all(abs(t - cues[p]["start"]) >= min_gap for p in picked):
            picked.append(i)
        if len(picked) >= target:
            break
    return sorted(picked)


def title_for(cues):
    freq = {}
    for c in cues:
        for w in content(c["text"]):
            freq[w] = freq.get(w, 0) + 1
    top, seen = [], set()
    for w in sorted(freq, key=lambda w: (-freq[w], w)):
        if w[:5] not in seen:
            seen.add(w[:5])
            top.append(w)
        if len(top) == 3:
            break
    return " ".join(top).capitalize() if top else "Section"


def build(cues, target=8):
    idx = boundaries(cues, target)
    out = []
    for k, i in enumerate(idx):
        j = idx[k + 1] if k + 1 < len(idx) else len(cues)
        start = 0.0 if k == 0 else cues[i]["start"]
        out.append({"start": start, "title": title_for(cues[i:j])})
    return out


def validate(chapters, duration=None):
    errs = []
    if not chapters:
        return ["no chapters"]
    if chapters[0]["start"] != 0:
        errs.append("the first chapter must start at 0:00")
    if len(chapters) < 3:
        errs.append("YouTube needs at least three chapters, this has %d" % len(chapters))
    for a, b in zip(chapters, chapters[1:]):
        if b["start"] <= a["start"]:
            errs.append("timestamps must go up: %s then %s" % (subs.fmt(a["start"]), subs.fmt(b["start"])))
        elif b["start"] - a["start"] < MIN_LEN:
            errs.append("'%s' lasts %.0fs, under the 10-second minimum" % (a["title"], b["start"] - a["start"]))
    if duration is not None and chapters and duration - chapters[-1]["start"] < MIN_LEN:
        errs.append("the last chapter lasts under 10 seconds")
    return errs


def parse_list(text):
    out = []
    for line in text.splitlines():
        m = re.match(r"\s*((?:\d+:)?\d{1,2}:\d{2})\s*[-.)]?\s*(.*)", line)
        if m:
            parts = [int(x) for x in m.group(1).split(":")]
            sec = parts[-1] + 60 * parts[-2] + (3600 * parts[-3] if len(parts) == 3 else 0)
            out.append({"start": float(sec), "title": m.group(2).strip()})
    return out


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if "--check" in a:
        i = a.index("--check")
        ch = parse_list(open(a[i + 1], encoding="utf-8").read())
        errs = validate(ch)
        for e in errs:
            print("  INVALID  " + e)
        print("  VALID: %d chapters" % len(ch) if not errs else "  fix these and check again")
        return 1 if errs else 0
    target = 8
    if "--target" in a:
        i = a.index("--target")
        target = int(a[i + 1])
        del a[i:i + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    cues = subs.load(a[0])
    ch = build(cues, target)
    errs = validate(ch, cues[-1]["end"] if cues else None)
    if errs:
        for e in errs:
            print("  INVALID  " + e)
        print("  The video may be too short for chapters, or try a smaller --target.")
        return 1
    print("CHAPTERS (draft titles: rewrite each as the promise of the section)\n")
    for c in ch:
        print("%s %s" % (subs.fmt(c["start"]), c["title"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
