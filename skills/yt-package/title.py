#!/usr/bin/env python3
"""title.py - lint a YouTube title and its thumbnail text as one pairing. Russian and English.

    python3 title.py --title "Я переплатил 40 000 за ремонт" --thumb "ОДИН ПУНКТ"
    python3 title.py titles.txt          # one title per line, optional " | thumbnail text"
    python3 title.py titles.txt --json

The title and the thumbnail are one unit. Written separately, the thumbnail repeats the title
and half of the click surface says the same thing twice.

Checks and why:
    up to 100 characters is the limit; about 60 show in desktop search, about 40 to 50 in the
    mobile feed, and a mobile cut can lose the subject
    a number, a name or a date beats every adjective
    the thumbnail does not repeat the title's words: different words, same promise
    three words at most on the thumbnail: at feed size a fourth is a grey smear
    two all-caps words at most in the title before it reads as spam
    no hype words, no clickbait the video cannot pay off
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ruen  # noqa: E402

LIMIT, DESKTOP, MOBILE = 100, 60, 45
BAIT = {"ru": ["вы не поверите", "шок", "это изменит всё", "до конца", "смотреть всем", "срочно",
               "жесть", "больше никогда", "100%"],
        "en": ["you won't believe", "shocking", "gone wrong", "must watch", "you need to see",
               "this changes everything", "100%"]}
STOP = set(("и в во не на с что как а но это то за к по из у о от для до так я мы вы ты "
            "the a an and or but to of in on at for is it this that with you i we my your").split())


def stems(text):
    return {w[:5] for w in ruen.words(text) if len(w) > 2 and w not in STOP}


def lint(title, thumb=""):
    lg = ruen.lang(title + " " + thumb)
    t = title.strip()
    issues, oks = [], []
    score = 100
    n = len(t)
    if n > LIMIT:
        issues.append(("fail", "%d characters: YouTube allows %d" % (n, LIMIT)))
        score -= 40
    elif n > DESKTOP:
        issues.append(("warn", "%d characters: desktop search cuts at about %d" % (n, DESKTOP)))
        score -= 10
    else:
        oks.append("%d characters, inside the desktop cut" % n)
    if n > MOBILE:
        head = t[:MOBILE]
        if not (ruen.concrete(head, lg) or re.search(r"[A-ZА-ЯЁ][a-zа-яё]+", head[1:])):
            issues.append(("warn", "the mobile feed shows about %d characters and nothing concrete is in them" % MOBILE))
            score -= 8
    if ruen.concrete(t, lg):
        oks.append("carries a number, a name or a date")
    else:
        issues.append(("warn", "no number, name or date: swap an adjective for one"))
        score -= 15
    hype = ruen.hits(t, ruen.HYPE[lg])
    if hype:
        issues.append(("warn", "hype words: " + ", ".join(hype)))
        score -= 8 * len(hype)
    bait = ruen.hits(t, BAIT[lg])
    if bait:
        issues.append(("warn", "clickbait the video has to pay off: " + ", ".join(bait)))
        score -= 10
    caps = [w for w in re.findall(r"\b[A-ZА-ЯЁ]{2,}\b", t) if len(w) > 2]
    if len(caps) > 2:
        issues.append(("warn", "%d all-caps words: two is the ceiling" % len(caps)))
        score -= 10
    if t.endswith(("...", "…")):
        issues.append(("warn", "ends on an ellipsis: say the thing"))
        score -= 5
    if chr(0x2014) in t:
        issues.append(("warn", "long dash: reads as generated, use a colon or a comma"))
        score -= 5
    if thumb.strip():
        tw = ruen.words(thumb)
        if len(tw) > 3:
            issues.append(("warn", "thumbnail has %d words: three is the most that reads at feed size" % len(tw)))
            score -= 10
        dup = stems(thumb) & stems(t)
        if dup:
            issues.append(("warn", "thumbnail repeats the title (%s): say what the title does not" % ", ".join(sorted(dup))))
            score -= 12
        else:
            oks.append("thumbnail adds something the title does not say")
    return {"title": t, "thumb": thumb.strip(), "lang": lg, "score": max(0, score),
            "issues": issues, "ok": oks}


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    pairs = []
    if "--title" in a:
        title = a[a.index("--title") + 1]
        thumb = a[a.index("--thumb") + 1] if "--thumb" in a else ""
        pairs = [(title, thumb)]
    elif a and os.path.exists(a[0]):
        for line in open(a[0], encoding="utf-8").read().splitlines():
            if line.strip():
                t, _, th = line.partition("|")
                pairs.append((t.strip(), th.strip()))
    else:
        print(__doc__)
        return 1
    res = sorted((lint(t, th) for t, th in pairs), key=lambda r: -r["score"])
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    for r in res:
        print('\n  "%s"%s' % (r["title"], "  +  [%s]" % r["thumb"] if r["thumb"] else ""))
        print("  score %d/100" % r["score"])
        for kind, msg in r["issues"]:
            print("    %-4s  %s" % ("x" if kind == "fail" else "!", msg))
        for msg in r["ok"]:
            print("    ok    " + msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
