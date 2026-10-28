#!/usr/bin/env python3
"""outline.py - time a long-form YouTube script section by section. Russian and English.

    python3 outline.py script.md
    python3 outline.py script.md --pace 4.8      # syllables per second, the host's pace

Sections start with a markdown heading ("## The turn"). Lines in square brackets or starting
with "ЭКРАН:" / "SCREEN:" are on-screen notes, not timed. Speaking time is counted in syllables.

It flags what usually causes the early cliff and the mid-video slide:
    the opening (everything before the second heading) runs past 45 seconds
    a channel intro, a greeting or a subscribe pitch in the first section
    a section that runs past 3 minutes with no on-screen note: a talking head with nothing to
    look at is a podcast
    a section with nothing concrete in it
    no payoff line: the last section never refers back to the first one
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ruen  # noqa: E402

NOTE = re.compile(r"^\s*(\[.*\]|(экран|screen|on screen|на экране)\s*:.*)$", re.I)


def parse(text):
    sections, cur = [], {"title": "(opening)", "lines": [], "notes": 0}
    for line in text.splitlines():
        if re.match(r"^\s*#{1,3}\s+\S", line):
            if cur["lines"] or cur["notes"] or sections:
                sections.append(cur)
            cur = {"title": line.strip("# ").strip(), "lines": [], "notes": 0}
        elif NOTE.match(line):
            cur["notes"] += 1
        elif line.strip():
            cur["lines"].append(line.strip())
    sections.append(cur)
    return [s for s in sections if s["lines"] or s["notes"]]


def analyse(text, pace=None):
    lg = ruen.lang(text)
    secs = parse(text)
    t, out, flags = 0.0, [], []
    for i, s in enumerate(secs):
        body = " ".join(s["lines"])
        d = ruen.speech_seconds(body, lg, pace) if body else 0
        out.append({"title": s["title"], "start": round(t, 1), "seconds": round(d, 1),
                    "words": len(ruen.words(body)), "notes": s["notes"],
                    "concrete": ruen.concrete(body, lg)})
        t += d
    if not out:
        return {"lang": lg, "sections": [], "total": 0, "flags": ["no script found"]}
    if out[0]["seconds"] > 45:
        flags.append("the opening runs %.0fs: the turn into the video should come by 0:45" % out[0]["seconds"])
    first = " ".join(secs[0]["lines"])
    pre = ruen.hits(" ".join(ruen.words(first)[:12]), ruen.PREAMBLE[lg] + ["меня зовут", "my name is"])
    if pre:
        flags.append("the opening has an intro or a pitch (%s): the most common cause of the 0:30 cliff" % ", ".join(pre))
    for s in out:
        if s["seconds"] > 180 and s["notes"] == 0:
            flags.append("'%s' runs %.0fs with no on-screen note: give the viewer something to look at" % (s["title"], s["seconds"]))
        if s["words"] > 30 and s["concrete"] == 0:
            flags.append("'%s' has nothing concrete: a number, a name or an example" % s["title"])
    if len(secs) > 1:
        a = {w[:5] for w in ruen.words(" ".join(secs[0]["lines"])) if len(w) > 4}
        b = {w[:5] for w in ruen.words(" ".join(secs[-1]["lines"])) if len(w) > 4}
        if not a & b:
            flags.append("the last section never refers back to the opening: deliver the promise explicitly")
    return {"lang": lg, "sections": out, "total": round(t, 1), "flags": flags}


def fmt(s):
    m, sec = divmod(int(round(s)), 60)
    return "%d:%02d" % (m, sec)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    pace = None
    if "--pace" in a:
        i = a.index("--pace")
        pace = float(a[i + 1])
        del a[i:i + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    r = analyse(open(a[0], encoding="utf-8").read(), pace)
    print("OUTLINE  %d sections  about %s" % (len(r["sections"]), fmt(r["total"])))
    print("=" * 68)
    for s in r["sections"]:
        print("  %6s  %5s  %4d words  %d notes  %s" % (fmt(s["start"]), fmt(s["seconds"]), s["words"], s["notes"], s["title"][:36]))
    print("-" * 68)
    for f in r["flags"] or ["clean"]:
        print("  - " + f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
