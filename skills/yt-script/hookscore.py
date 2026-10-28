#!/usr/bin/env python3
"""hookscore.py - score a Reel or Shorts hook before you shoot it. Russian and English.

    python3 hookscore.py hooks.txt              # one hook per line, ranked
    python3 hookscore.py --hook "одна строка"   # score a single hook
    python3 hookscore.py --json hooks.txt       # machine-readable
    python3 hookscore.py --pace 5.5 hooks.txt   # your own speaking pace, syllables per second

Six properties, 0-100 each. The verdict is 60% the mean and 40% the weakest one: a hook with
five strong properties and one dead one leaks at the dead one, and an average would hide it.

    FRONTLOAD    how early the payload arrives. A greeting or a preamble scores 0.
    SPECIFICITY  numbers (also said as words), money, durations, names. Hype words cost points.
    ADDRESS      speaks to the viewer ("ты", "вы", "you") or opens on your own story ("я", "мы").
    STAKES       what it costs to keep doing it the current way.
    CURIOSITY    an open question the viewer cannot close without watching.
    BREVITY      seconds to say it out loud. A Reel hook has about three.

WHAT THIS CAN AND CANNOT TELL YOU. It is a heuristic over the words. It reliably catches weak
hooks: greetings, preambles, nothing concrete, too long to say in three seconds. It cannot tell
you which of two decent hooks will travel, because that is decided by the face, the edit, the
sound and who the platform shows it to. Measure it on your own videos with calibrate.py.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ruen  # noqa: E402

FORMULAS = json.load(open(os.path.join(HERE, "hooks.json"), encoding="utf-8"))["hooks"]
ME = {"ru": re.compile(r"\b(я|мы|мне|меня|мой|моя|моё|мои|нам|нас|наш)\b", re.I),
      "en": re.compile(r"\b(i|i'm|i've|we|my|our|me|us)\b", re.I)}

FIX = {
    "FRONTLOAD": {"ru": "начните с сути: уберите приветствие и всё, что стоит до первой цифры или утверждения",
                  "en": "start on the payload: cut the greeting and everything before the first number or claim"},
    "SPECIFICITY": {"ru": "замените одно прилагательное на цифру, имя или срок",
                    "en": "swap one adjective for a number, a name or a date"},
    "ADDRESS": {"ru": "скажите «вы» или «ты» в первых шести словах, или начните со своей истории",
                "en": "say 'you' in the first six words, or open on your own story"},
    "STAKES": {"ru": "назовите, чего стоит зрителю продолжать по-старому",
               "en": "name what it costs them to keep doing it the current way"},
    "CURIOSITY": {"ru": "отрежьте половину фразы, которая сама себя объясняет",
                  "en": "cut the half of the sentence that answers itself"},
    "BREVITY": {"ru": "уложитесь в три секунды: прочитайте вслух и остановитесь, где кончилось дыхание",
                "en": "fit it into three seconds: read it out loud and stop where your breath runs out"},
}


def frontload(t, lg):
    w = ruen.words(t)
    if not w:
        return 0
    if ruen.hits(" ".join(w[:4]), ruen.PREAMBLE[lg]):
        return 0
    if ruen.hits(" ".join(w[:3]), ruen.HYPE[lg]):
        return 20
    for i, tok in enumerate(w):
        payload = (re.search(r"\d", tok) or tok in ruen.NUM_WORDS[lg]
                   or ruen.STAKES[lg].search(tok) or ruen.YOU[lg].fullmatch(tok)
                   or ruen.CURIOSITY[lg].fullmatch(tok) or ME[lg].fullmatch(tok))
        if payload:
            return max(0, 100 - 14 * max(0, i - 2))
    return 25


def specificity(t, lg):
    w = ruen.words(t)
    if not w:
        return 0
    s = 30 + 22 * ruen.concrete(t, lg) - 15 * ruen.count(t, ruen.HYPE[lg]) \
        - 6 * ruen.count(t, ruen.FILLERS[lg])
    return max(0, min(100, s))


def address(t, lg):
    you = ruen.second_person(t, lg)
    first6 = " ".join(t.split()[:6])
    s = 30 + you * 20 + (25 if ruen.YOU[lg].search(first6) else 0)
    if ME[lg].search(" ".join(t.split()[:4])):
        s = max(s, 65)
    return max(0, min(100, s))


def stakes(t, lg):
    n = len(ruen.STAKES[lg].findall(t))
    money = 15 if ruen.MONEY.search(t) else 0
    return max(0, min(100, 32 + 24 * n + money))


def curiosity(t, lg):
    n = len(ruen.CURIOSITY[lg].findall(t))
    q = 15 if t.strip().endswith("?") else 0
    closed = -20 if ruen.CLOSED[lg].search(t) else 0
    mid = 20 if re.match(r"\s*(\.\.\.|…)", t) else 0
    return max(0, min(100, 36 + 16 * n + q + closed + mid))


def brevity(t, lg, pace=None):
    sec = ruen.speech_seconds(t, lg, pace)
    if sec <= 0.6:
        return 40
    if sec <= 3.5:
        return 100
    return max(10, int(100 - (sec - 3.5) * 16))


PROPS = ["FRONTLOAD", "SPECIFICITY", "ADDRESS", "STAKES", "CURIOSITY", "BREVITY"]


def classify(t, lg):
    """The formula with the most matching patterns; on a tie, the one that matches earliest,
    because the start of a hook is what the viewer hears first."""
    best, key = None, None
    for f in FORMULAS:
        found = [m for m in (re.search(p, t, re.I) for p in f["match"][lg]) if m]
        if not found:
            continue
        k = (len(found), -min(m.start() for m in found))
        if key is None or k > key:
            best, key = f, k
    return best, (key[0] if key else 0)


def dealbreakers(t, lg):
    out = []
    w = ruen.words(t)
    if ruen.hits(" ".join(w[:4]), ruen.PREAMBLE[lg]):
        out.append({"ru": "приветствие или вступление в начале: зритель пришёл не за этим",
                    "en": "opens on a greeting or a preamble: nobody came to the feed for that"}[lg])
    if ruen.hits(t, ["не листай", "остановись", "stop scrolling", "wait for it"]):
        out.append({"ru": "просьба о внимании доказывает, что внимание ещё не заслужено",
                    "en": "asking for attention proves you have not earned it"}[lg])
    return out


def score(t, pace=None):
    lg = ruen.lang(t)
    parts = {"FRONTLOAD": frontload(t, lg), "SPECIFICITY": specificity(t, lg),
             "ADDRESS": address(t, lg), "STAKES": stakes(t, lg),
             "CURIOSITY": curiosity(t, lg), "BREVITY": brevity(t, lg, pace)}
    vals = list(parts.values())
    verdict = round(0.6 * sum(vals) / len(vals) + 0.4 * min(vals), 1)
    breaks = dealbreakers(t, lg)
    if breaks:
        verdict = min(verdict, 25.0)
    f, hits = classify(t, lg)
    weakest = min(parts, key=parts.get)
    return {"hook": t.strip(), "lang": lg, "properties": parts, "verdict": verdict,
            "band": band(verdict), "formula": f["id"] if f else None,
            "formula_name": (f["name_ru"] if lg == "ru" else f["name_en"]) if f else None,
            "formula_num": f["num"] if f else None, "matched": hits,
            "seconds": round(ruen.speech_seconds(t, lg, pace), 1),
            "weakest": weakest, "fix": FIX[weakest][lg], "dealbreakers": breaks}


def band(v):
    return "STRONG" if v >= 65 else "OK" if v >= 48 else "WEAK"


def report(r):
    print("\n  %s" % r["hook"])
    print("  " + "-" * min(72, max(20, len(r["hook"]))))
    for k in PROPS:
        v = r["properties"][k]
        print("    %-12s %3d  %s" % (k, v, "#" * (v // 5)))
    print("    %-12s %5.1f  %s   (%.1fs out loud)" % ("VERDICT", r["verdict"], r["band"], r["seconds"]))
    if r["formula"]:
        print("    formula      #%d %s" % (r["formula_num"], r["formula_name"]))
    else:
        print("    formula      none matched (often a summary, not a hook)")
    print("    weakest      %s: %s" % (r["weakest"], r["fix"]))
    for b in r["dealbreakers"]:
        print("    DEALBREAKER  " + b)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    pace = None
    if "--pace" in a:
        i = a.index("--pace")
        pace = float(a[i + 1])
        del a[i:i + 2]
    if "--hook" in a:
        lines = [a[a.index("--hook") + 1]]
    elif a and os.path.exists(a[0]):
        lines = [l for l in open(a[0], encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print(__doc__)
        return 1 if a else 0
    out = sorted((score(t, pace) for t in lines), key=lambda r: -r["verdict"])
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0
    for r in out:
        report(r)
    if len(out) > 1:
        print("\n  winner: %s  (%.1f %s)\n" % (out[0]["hook"], out[0]["verdict"], out[0]["band"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
