import filecmp
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import unittest
import warnings
from contextlib import redirect_stdout, redirect_stderr

warnings.simplefilter("ignore", ResourceWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SKILLS = os.path.join(ROOT, "skills")


def load(skill, mod):
    path = os.path.join(SKILLS, skill, mod + ".py")
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("%s_%s" % (skill.replace("-", "_"), mod), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


deadair = load("yt-edit", "deadair")
chapters = load("yt-chapters", "chapters")
retention = load("yt-retention", "retention")
title = load("yt-package", "title")
seo = load("yt-seo", "seo")
outline = load("yt-script", "outline")
hookscore = load("yt-script", "hookscore")
swipe = load("yt-viral", "swipe")
subs = load("yt-edit", "subs")


def tmp(text, suffix=".txt"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def srt(cues):
    def ts(s):
        h, m = int(s // 3600), int(s % 3600 // 60)
        return ("%02d:%02d:%06.3f" % (h, m, s % 60)).replace(".", ",")
    return "\n".join("%d\n%s --> %s\n%s\n" % (i, ts(a), ts(b), t) for i, (a, b, t) in enumerate(cues, 1))


CUES = [(0.0, 3.0, "Я переплатил сорок тысяч за ремонт из-за одного пункта."), (3.2, 4.0, "ну"),
        (4.1, 7.5, "Сегодня разберём договор подряда целиком."),
        (9.5, 12.0, "Первый пункт договора про сроки работ."),
        (12.1, 15.0, "Первый пункт договора про сроки работ и штрафы."),
        (15.2, 19.0, "Сроки работ надо прописать датами, а не словами."),
        (19.5, 23.0, "Штраф за просрочку считается от цены договора."),
        (25.0, 29.0, "Теперь поговорим про приёмку квартиры и акт."),
        (29.2, 33.0, "Акт приёмки подписывают с перечнем замечаний."),
        (33.5, 37.0, "Замечания в акте фиксируют фотографиями."), (37.2, 38.0, "короче"),
        (40.0, 44.0, "Последняя часть про гарантию на окна и двери."),
        (44.2, 48.0, "Гарантия на окна обычно короче, чем на дом."),
        (48.3, 52.0, "Окна проверяют зимой, когда видно продувание."),
        (52.5, 58.0, "Один пункт в договоре стоил мне сорок тысяч.")]


class TestSubs(unittest.TestCase):
    def test_formats(self):
        a = subs.load(tmp(srt(CUES), ".srt"))
        self.assertEqual(len(a), len(CUES))
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:02.500\n<c>Привет</c> мир\n"
        self.assertEqual(subs.load(tmp(vtt, ".vtt"))[0]["text"], "Привет мир")
        wj = {"segments": [{"start": 0, "end": 1.5, "text": " hello "}]}
        self.assertEqual(subs.load(tmp(json.dumps(wj), ".json"))[0]["end"], 1.5)
        j3 = {"events": [{"tStartMs": 1000, "dDurationMs": 500, "segs": [{"utf8": "раз"}, {"utf8": " два"}]}]}
        self.assertEqual(subs.load(tmp(json.dumps(j3), ".json"))[0]["text"], "раз два")


class TestDeadair(unittest.TestCase):
    def test_kinds(self):
        r = deadair.decide(subs.load(tmp(srt(CUES), ".srt")), 0.6)
        kinds = {c["kind"].split("+")[0] for c in r["cuts"]}
        self.assertTrue({"DEAD", "FILLER", "RETAKE"} <= kinds)
        self.assertLess(r["kept"], r["total"])
        for c in r["cuts"]:
            if c["kind"] == "DEAD":
                self.assertGreater(c["end"] - c["start"], 0)

    def test_english_fillers(self):
        self.assertTrue(deadair.is_filler("um, you know", "en"))
        self.assertFalse(deadair.is_filler("the contract matters", "en"))


class TestChapters(unittest.TestCase):
    def test_build_is_valid(self):
        cues = subs.load(tmp(srt(CUES), ".srt"))
        ch = chapters.build(cues, 3)
        self.assertEqual(ch[0]["start"], 0)
        self.assertEqual(chapters.validate(ch, cues[-1]["end"]), [])

    def test_rules(self):
        bad = chapters.parse_list("0:05 Intro\n0:30 Middle\n")
        errs = " ".join(chapters.validate(bad))
        self.assertIn("0:00", errs)
        self.assertIn("three", errs)
        short = chapters.parse_list("0:00 A\n0:05 B\n0:40 C\n")
        self.assertIn("10-second", " ".join(chapters.validate(short)))
        ok = chapters.parse_list("00:00 A\n1:00 B\n1:02:00 C\n")
        self.assertEqual(chapters.validate(ok), [])


class TestRetention(unittest.TestCase):
    def test_share_positions_and_cliff(self):
        rows = ["Video position,Audience retention"]
        vals = [100, 92, 80, 70, 66, 64, 62, 61, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 38, 37]
        rows += ["%.2f,%.1f" % (i / 20, v) for i, v in enumerate(vals)]
        pts = retention.load(tmp("\n".join(rows), ".csv"), duration=600)
        self.assertAlmostEqual(pts[-1][0], 600, places=0)
        r = retention.analyse(pts)
        self.assertTrue(r["cliffs"])
        self.assertIn("CLIFF", retention.biggest(r))

    def test_hook_leak(self):
        rows = ["Время,Удержание аудитории (%)", "0:00,100", "0:10,60", "0:30,55", "1:00,50", "5:00,40"]
        r = retention.analyse(retention.load(tmp("\n".join(rows), ".csv")))
        self.assertGreaterEqual(r["hook_leak"], 25)
        self.assertIn("HOOK LEAK", retention.biggest(r))


class TestTitle(unittest.TestCase):
    def test_good_beats_bad(self):
        g = title.lint("Я переплатил 40 000 за ремонт из-за одного пункта", "НЕ ПОДПИСЫВАЙ")
        b = title.lint("НЕВЕРОЯТНЫЙ ШОК ЛАЙФХАК ДЛЯ РЕМОНТА ВЫ НЕ ПОВЕРИТЕ", "невероятный лайфхак для ремонта")
        self.assertGreater(g["score"], 80)
        self.assertLess(b["score"], 30)

    def test_repeat_and_limit(self):
        r = title.lint("Один пункт договора", "ОДИН ПУНКТ")
        self.assertTrue(any("repeats" in m for _, m in r["issues"]))
        r = title.lint("x" * 101)
        self.assertEqual(r["issues"][0][0], "fail")


class TestSeo(unittest.TestCase):
    def test_query_and_tags(self):
        desc = "Как подписать акт приёмки квартиры с замечаниями.\nШаблон в комментарии.\n\n0:00 Начало\n0:40 Акт\n2:10 Гарантия\n"
        res = seo.check("Акт приёмки: как подписать с замечаниями", desc,
                        ["акт приёмки с замечаниями", "гарантия застройщика"], ["акт"] * 3)
        d = {(r[1], r[2].split('"')[1] if '"' in r[2] else ""): r[0] for r in res}
        self.assertEqual(d[("QUERY", "акт приёмки с замечаниями")], "PASS")
        self.assertEqual(d[("QUERY", "гарантия застройщика")], "WARN")
        self.assertEqual(d[("CHAPTERS", "")], "PASS")
        res = seo.check("t", "d", tags=["x" * 300, "y" * 300])
        self.assertIn(("FAIL", "TAGS"), [(r[0], r[1]) for r in res])


class TestOutline(unittest.TestCase):
    def test_flags_intro(self):
        r = outline.analyse("Всем привет, меня зовут Дима, подписывайтесь.\nСегодня про договор.\n"
                            "## Сроки\nСроки пишут датами: 1 марта.\n## Итог\nВот и всё.\n")
        self.assertEqual(len(r["sections"]), 3)
        self.assertTrue(any("intro" in f for f in r["flags"]))


class TestSwipe(unittest.TestCase):
    def test_titles(self):
        p = tmp("account\tmedian\tviews\thook\nA\t10000\t50000\tЯ переплатил 40 000 за ремонт\n"
                "A\t10000\t9000\tОбзор квартиры\nB\t5000\t4000\tПочему все советуют звонить\n")
        rows, _ = swipe.load(p)
        res = swipe.analyse(rows)
        top = res["rows"][0]
        self.assertEqual((top["account"], top["multiple"], top["formula"]), ("A", 5.0, "cost"))
        self.assertIsNotNone(top["score"])


class TestRepo(unittest.TestCase):
    def test_frontmatter(self):
        names = sorted(os.listdir(SKILLS))
        self.assertEqual(len(names), 11)
        for n in names:
            text = open(os.path.join(SKILLS, n, "SKILL.md"), encoding="utf-8").read()
            m = re.match(r'---\nname: (.+)\ndescription: "(.+?)"\n---\n', text, re.S)
            self.assertTrue(m, n)
            self.assertEqual(m.group(1), n)
            self.assertLessEqual(len(m.group(2)), 1024)

    def test_shared_copies_identical(self):
        for mod in ("ruen.py", "subs.py"):
            copies = [os.path.join(SKILLS, d, mod) for d in os.listdir(SKILLS)
                      if os.path.exists(os.path.join(SKILLS, d, mod))]
            self.assertGreaterEqual(len(copies), 3, mod)
            for c in copies[1:]:
                self.assertTrue(filecmp.cmp(copies[0], c, shallow=False), c)

    def test_hook_formulas_present(self):
        self.assertEqual(len(hookscore.FORMULAS), 26)

    def test_no_long_dashes(self):
        for base, _, files in os.walk(ROOT):
            if ".git" in base:
                continue
            for f in files:
                if f.endswith((".md", ".json", ".txt", ".py")):
                    self.assertNotIn(chr(0x2014), open(os.path.join(base, f), encoding="utf-8").read(),
                                     os.path.join(base, f))

    def test_manifests(self):
        p = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json")))
        self.assertEqual(p["name"], "minga-youtube")
        json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")))


if __name__ == "__main__":
    unittest.main()
