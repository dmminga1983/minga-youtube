#!/usr/bin/env python3
"""ruen.py - shared Russian and English text helpers for the Minga content tools.

Standard library only. Every tool that scores, times or lints text imports this file
from its own folder, so each skill folder stays self-contained when copied on its own.

    lang(text)            -> "ru" or "en", by the share of Cyrillic letters
    words(text)           -> lower-case word tokens, Cyrillic, Latin, digits, %, $, rub sign
    sentences(text)       -> sentences, split on . ! ? and line breaks
    syllables(word, lang) -> syllable count (vowel count for Russian, vowel groups for English)
    speech_seconds(text)  -> how long the text takes to say out loud at a given pace
    concrete(text)        -> concrete markers: digits, numbers said as words, money, durations
    second_person(text)   -> how many times the text speaks to "you"
    hits(text, phrases)   -> which phrases from a list occur, matched on word boundaries

The word lists below are meant to be edited. They are data, not logic.
"""
import re

CYR = re.compile(r"[Ѐ-ӿ]")
LAT = re.compile(r"[A-Za-z]")
WORD = re.compile(r"[0-9A-Za-zЀ-ӿ'%$₽]+(?:[.,][0-9]+)?")

# Speaking pace in syllables per second. Russian packs more syllables into a word, so a
# words-per-minute pace from English guides overestimates how much fits into a Reel.
PACE = {"ru": 5.0, "en": 4.0}

RU_VOWELS = set("аеёиоуыэюя")
EN_VOWELS = re.compile(r"[aeiouy]+")

NUM_WORDS = {
    "ru": ("ноль один одна одно два две три четыре пять шесть семь восемь девять десять "
           "одиннадцать двенадцать тринадцать четырнадцать пятнадцать шестнадцать "
           "семнадцать восемнадцать девятнадцать двадцать тридцать сорок пятьдесят "
           "шестьдесят семьдесят восемьдесят девяносто сто двести триста четыреста "
           "пятьсот шестьсот семьсот восемьсот девятьсот тысяча тысячи тысяч миллион "
           "миллиона миллионов миллиард полтора полторы половина треть четверть "
           "дважды трижды вдвое втрое первый первая первое первых").split(),
    "en": ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
           "fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty "
           "sixty seventy eighty ninety hundred thousand million billion half twice "
           "double triple first").split(),
}
DURATION = re.compile(
    r"\b(секунд\w*|минут\w*|час\w*|дн(?:я|ей|ём|ем)|день|сутк\w*|недел\w*|месяц\w*|"
    r"год\w*|лет|second|minute|hour|day|week|month|year)s?\b", re.I)
MONEY = re.compile(r"(\$\s?\d|\d\s?(\$|₽|руб|р\.|тыс|к\b|млн|млрд|k\b|m\b))", re.I)
DIGITS = re.compile(r"\d")

YOU = {
    "ru": re.compile(r"\b(ты|тебе|тебя|тобой|твой|твоя|твоё|твое|твои|твоих|вы|вам|вас|вами|"
                     r"ваш|ваша|ваше|ваши|ваших|\w+(?:ешь|ёшь|ишь))\b", re.I),
    "en": re.compile(r"\b(you|your|you're|youre|yours|yourself)\b", re.I),
}

FILLERS = {
    "ru": ["ну", "короче", "типа", "как бы", "вот", "значит", "собственно", "в общем",
           "э", "эм", "ээ", "мм", "так сказать", "это самое", "как его", "получается"],
    "en": ["um", "uh", "erm", "like", "basically", "so yeah", "you know", "i mean", "kind of",
           "sort of", "literally", "actually"],
}

PREAMBLE = {
    "ru": ["всем привет", "привет", "здравствуйте", "добрый день", "друзья", "в этом видео",
           "в сегодняшнем видео", "сегодня я расскажу", "сегодня поговорим",
           "сегодня я хочу", "давайте разберёмся", "давайте разберемся", "подписывайтесь",
           "ставьте лайк", "листай дальше", "не листай", "остановись", "смотри до конца"],
    "en": ["hey guys", "hi guys", "welcome back", "in this video", "in today's video",
           "today i want", "today we", "let's dive", "stop scrolling", "wait for it",
           "watch till the end", "subscribe"],
}

HYPE = {
    "ru": ["невероятный", "невероятно", "потрясающий", "потрясающе", "шок", "шокирующий",
           "шокирующая", "лучший", "лучшая", "топ", "секрет", "секретный", "лайфхак", "мега",
           "супер", "гениальный", "уникальный", "революционный", "бомба", "огонь", "взрыв",
           "магия", "волшебный", "идеальный", "крутой"],
    "en": ["amazing", "incredible", "insane", "crazy", "huge", "massive", "game changer",
           "secret", "powerful", "ultimate", "best", "revolutionary", "mind blowing",
           "unbelievable", "epic", "perfect"],
}

STAKES = {
    "ru": re.compile(r"\b(потерял\w*|потеря\w*|теря\w*|переплат\w*|ошиб\w*|штраф\w*|суд\w*|"
                     r"должн\w*|долг\w*|разор\w*|бросил\w*|бросают|провал\w*|проиграл\w*|"
                     r"никогда|хватит|перестань|перестаньте|прекрати\w*|пока не|прежде чем|"
                     r"поздно|риск\w*|опасн\w*|умира\w*|выброс\w*|зря|впустую|стоил\w*)\b", re.I),
    "en": re.compile(r"\b(lose|lost|losing|wasting|waste|quit|fail\w*|broke|cost\w*|risk\w*|"
                     r"before|stop|never|die|dying|dead|too late|owe\w*|fined|sued)\b", re.I),
}

CURIOSITY = {
    "ru": re.compile(r"\b(почему|зачем|как|что|какой|какая|никто|ни один|кроме|пока|но|однако|"
                     r"оказалось|оказывается|на самом деле|причина|вот что|вот почему|"
                     r"правда|до сих пор|всё равно|все равно)\b", re.I),
    "en": re.compile(r"\b(why|how|what|which|until|before|but|nobody|almost|except|reason|"
                     r"actually|turns out|still)\b", re.I),
}
CLOSED = {
    "ru": re.compile(r"\b(потому что|поэтому|так что|то есть|из-за этого)\b", re.I),
    "en": re.compile(r"\b(because|so that|which means|that's why)\b", re.I),
}


def lang(text):
    c = len(CYR.findall(text))
    l = len(LAT.findall(text))
    return "ru" if c and c >= l * 0.5 else "en"


def words(text):
    return [w.lower() for w in WORD.findall(text)]


def sentences(text):
    parts = re.split(r"(?<=[.!?…])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def syllables(word, lg=None):
    w = word.lower()
    lg = lg or lang(w)
    if DIGITS.search(w):
        # a number is said out loud: roughly two syllables per digit, capped
        return min(8, 2 * len(re.sub(r"\D", "", w)) or 1)
    if lg == "ru" or CYR.search(w):
        return max(1, sum(1 for ch in w if ch in RU_VOWELS))
    groups = EN_VOWELS.findall(w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def speech_seconds(text, lg=None, pace=None):
    lg = lg or lang(text)
    rate = pace or PACE[lg]
    syl = sum(syllables(w, lg) for w in words(text))
    pauses = len(re.findall(r"[.!?…]", text)) * 0.25 + len(re.findall(r"[,;:]", text)) * 0.1
    return syl / rate + pauses


def _phrase_re(p):
    return re.compile(r"(?<![0-9A-Za-zЀ-ӿ])" + re.escape(p.lower()) +
                      r"(?![0-9A-Za-zЀ-ӿ])")


def hits(text, phrases):
    t = text.lower().replace("ё", "е")
    found = []
    for p in phrases:
        if _phrase_re(p.replace("ё", "е")).search(t):
            found.append(p)
    return found


def count(text, phrases):
    t = text.lower().replace("ё", "е")
    return sum(len(_phrase_re(p.replace("ё", "е")).findall(t)) for p in phrases)


def concrete(text, lg=None):
    lg = lg or lang(text)
    w = words(text)
    n = len(re.findall(r"\d[\d\s.,]*", text))
    n += sum(1 for x in w if x in NUM_WORDS[lg])
    n += len(MONEY.findall(text))
    n += len(DURATION.findall(text))
    # names: capitalised words that do not start a sentence
    for s in sentences(text):
        toks = s.split()
        n += sum(1 for t in toks[1:] if t[:1].isupper() and not t.isupper())
    return n


def second_person(text, lg=None):
    lg = lg or lang(text)
    return len(YOU[lg].findall(text))
