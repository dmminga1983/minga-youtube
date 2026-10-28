#!/usr/bin/env python3
"""seo.py - check that a video's title, description and tags can win the searches it is for.

    python3 seo.py --title "..." --queries "акт приёмки замечания,как подписать акт" description.txt
    python3 seo.py --title "..." --tags "акт приёмки,приёмка квартиры" description.txt

The query test: for each search the video should win, every meaningful word of the query
should appear in the title or in the first two lines of the description, which are also the
search snippet. If they do not, the fix is the title, not the description.

Also checked: description length (5,000 characters at most), the first line above the fold,
chapters present and valid if there are timestamps, the 500-character limit on tags, and
hashtags (more than 60 and YouTube ignores all of them).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ruen  # noqa: E402

DESC_MAX, TAGS_MAX, HASHTAGS_MAX = 5000, 500, 60
STOP = set(("и в во не на с со что как а но это то за к по из у о об от для до так ли бы же "
            "the a an and or but to of in on at for is it this that with how what why do "
            "does can my your").split())
TS = re.compile(r"(?m)^\s*((?:\d+:)?\d{1,2}:\d{2})\b")


def stem(w):
    return w[:5] if ruen.CYR.search(w) else w[:6]


def query_test(query, title, desc):
    head = title + " " + " ".join(desc.strip().split("\n")[:2])
    have = {stem(w) for w in ruen.words(head)}
    need = [w for w in ruen.words(query) if w not in STOP and len(w) > 1]
    missing = [w for w in need if stem(w) not in have]
    return missing


def check(title, desc, queries=(), tags=()):
    out = []
    n = len(desc)
    out.append(("FAIL" if n > DESC_MAX else "PASS", "DESCRIPTION", "%d / %d characters" % (n, DESC_MAX)))
    first = desc.strip().split("\n")[0] if desc.strip() else ""
    if not first:
        out.append(("WARN", "FIRST LINE", "empty: the first line is the search snippet"))
    elif len(first) > 150:
        out.append(("WARN", "FIRST LINE", "%d characters: say what the video gives in the first 100 to 150" % len(first)))
    else:
        out.append(("PASS", "FIRST LINE", "%d characters" % len(first)))
    for q in queries:
        miss = query_test(q, title, desc)
        out.append(("PASS" if not miss else "WARN", "QUERY", '"%s"%s' % (
            q, "" if not miss else ": missing from the title and first two lines: " + ", ".join(miss))))
    stamps = TS.findall(desc)
    if stamps:
        first_ts = stamps[0]
        ok = first_ts in ("0:00", "00:00", "0:00:00") and len(stamps) >= 3
        out.append(("PASS" if ok else "FAIL", "CHAPTERS", "%d timestamps%s" % (
            len(stamps), "" if ok else ": the first must be 0:00 and there must be at least three. Run chapters.py --check")))
    if tags:
        total = sum(len(t) for t in tags) + max(0, len(tags) - 1)
        out.append(("FAIL" if total > TAGS_MAX else "PASS", "TAGS", "%d tags, %d / %d characters" % (len(tags), total, TAGS_MAX)))
        if len(tags) > 15:
            out.append(("WARN", "TAGS", "over 15: tags are a weak signal, use them for spellings and names, then stop"))
    hashtags = re.findall(r"(?<!\w)#[\wЀ-ӿ]+", title + " " + desc)
    if len(hashtags) > HASHTAGS_MAX:
        out.append(("FAIL", "HASHTAGS", "%d: over %d and YouTube ignores all of them" % (len(hashtags), HASHTAGS_MAX)))
    return out


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    opts = {"title": "", "queries": "", "tags": ""}
    for k in list(opts):
        if "--" + k in a:
            i = a.index("--" + k)
            opts[k] = a[i + 1]
            del a[i:i + 2]
    desc = open(a[0], encoding="utf-8").read() if a and os.path.exists(a[0]) else ""
    if not opts["title"] and not desc:
        print(__doc__)
        return 1
    split = lambda s: [x.strip() for x in s.split(",") if x.strip()]
    res = check(opts["title"], desc, split(opts["queries"]), split(opts["tags"]))
    for status, name, msg in res:
        print("  %-4s  %-12s %s" % (status, name, msg))
    return 1 if any(r[0] == "FAIL" for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())
