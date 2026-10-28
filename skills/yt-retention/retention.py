#!/usr/bin/env python3
"""retention.py - read a YouTube Studio audience-retention export and find where people left.

    python3 retention.py retention.csv --duration 612
    python3 retention.py retention.csv --duration 612 --transcript transcript.srt

Get the file: YouTube Studio, the video, Analytics, Engagement, the audience retention chart,
the download icon. The tool accepts the usual shapes: a position column (seconds, mm:ss, or a
share of the video from 0 to 1 or 0 to 100) and a retention column (percent, or a share).
Column names are matched loosely, in Russian or English.

Three different problems, three different fixes:
    HOOK LEAK  what is lost in the first 30 seconds. Under 25% lost is healthy. The fix is
               always the first fifteen seconds of script, never the edit
    CLIFFS     single steep drops: a topic change with no signpost, a sponsor read, a long setup.
               With --transcript the tool prints what was being said at that moment
    SLIDE      the steady bleed across the middle: pacing. The fix is cutting, not rewriting
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import subs  # noqa: E402

POS = re.compile(r"(position|time|момент|время|позици|video position|секунд)", re.I)
RET = re.compile(r"(retention|audience|удержан|аудитор|зрител|%)", re.I)


def num(x):
    x = str(x).strip().replace("%", "").replace(",", ".")
    if re.match(r"^\d+:\d{2}(:\d{2})?$", x):
        p = [int(v) for v in x.split(":")]
        return float(p[-1] + 60 * p[-2] + (3600 * p[-3] if len(p) == 3 else 0)), True
    try:
        return float(x), False
    except ValueError:
        return None, False


def load(path, duration=None):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    pi = next((i for i, h in enumerate(head) if POS.search(h)), 0)
    ri = next((i for i, h in enumerate(head) if i != pi and RET.search(h)), 1)
    pts, clock = [], False
    for r in rows[1:]:
        if len(r) <= max(pi, ri):
            continue
        p, is_clock = num(r[pi])
        v, _ = num(r[ri])
        if p is None or v is None:
            continue
        clock = clock or is_clock
        pts.append([p, v])
    if not pts:
        raise ValueError("no numeric rows found")
    if max(v for _, v in pts) <= 1.5:
        for q in pts:
            q[1] *= 100
    maxp = max(p for p, _ in pts)
    if not clock and maxp <= 100.0 and duration:
        scale = duration / (1.0 if maxp <= 1.0 else 100.0)
        for q in pts:
            q[0] *= scale
    pts.sort()
    return pts


def at(pts, t):
    for (p0, v0), (p1, v1) in zip(pts, pts[1:]):
        if p0 <= t <= p1:
            return v0 + (v1 - v0) * ((t - p0) / (p1 - p0) if p1 > p0 else 0)
    return pts[-1][1] if t > pts[-1][0] else pts[0][1]


def analyse(pts):
    start = pts[0][1]
    end_t = pts[-1][0]
    v30 = at(pts, min(30.0, end_t))
    hook_leak = max(0.0, start - v30)
    cliffs = []
    for (p0, v0), (p1, v1) in zip(pts, pts[1:]):
        if p0 < 30 or p1 <= p0:
            continue
        drop = v0 - v1
        rate = drop / (p1 - p0)
        if drop >= 3 and rate >= 0.4:
            cliffs.append({"at": p0, "drop": round(drop, 1), "per_s": round(rate, 2)})
    cliffs.sort(key=lambda c: -c["drop"])
    mid_a, mid_b = end_t * 0.2, end_t * 0.8
    slide = (at(pts, mid_a) - at(pts, mid_b)) / max(1.0, (mid_b - mid_a) / 60.0)
    return {"start": round(start, 1), "at30": round(v30, 1), "hook_leak": round(hook_leak, 1),
            "cliffs": cliffs[:5], "slide_per_min": round(slide, 1), "end": round(pts[-1][1], 1),
            "duration": end_t}


def biggest(r):
    if r["hook_leak"] >= 25:
        return "HOOK LEAK: %.0f points lost in the first 30 seconds. Rewrite the first fifteen seconds." % r["hook_leak"]
    if r["cliffs"] and r["cliffs"][0]["drop"] >= 6:
        c = r["cliffs"][0]
        return "CLIFF at %s: %.0f points gone. Signpost the change or cut what is there." % (subs.fmt(c["at"]), c["drop"])
    if r["slide_per_min"] >= 4:
        return "SLIDE: %.1f points a minute through the middle. Cut, do not rewrite." % r["slide_per_min"]
    return "The video holds. If it still underperforms, the problem is packaging: title and thumbnail."


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    duration = transcript = None
    if "--duration" in a:
        i = a.index("--duration")
        duration = float(a[i + 1])
        del a[i:i + 2]
    if "--transcript" in a:
        i = a.index("--transcript")
        transcript = subs.load(a[i + 1])
        del a[i:i + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    r = analyse(load(a[0], duration))
    print("RETENTION  start %.0f%%, at 0:30 %.0f%%, end %.0f%%" % (r["start"], r["at30"], r["end"]))
    print("  hook leak   %.1f points in the first 30s  %s" % (r["hook_leak"], "OK" if r["hook_leak"] < 25 else "LEAKING"))
    print("  slide       %.1f points per minute through the middle" % r["slide_per_min"])
    for c in r["cliffs"]:
        said = ""
        if transcript:
            near = [x["text"] for x in transcript if x["start"] - 4 <= c["at"] <= x["end"] + 4]
            said = '  "%s"' % " ".join(near)[:80] if near else ""
        print("  cliff       %s  -%.1f points%s" % (subs.fmt(c["at"]), c["drop"], said))
    print("\n  BIGGEST LEAK  " + biggest(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
