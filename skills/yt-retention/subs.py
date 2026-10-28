#!/usr/bin/env python3
"""subs.py - read timed transcripts into one shape. Standard library only.

    cues = load(path)   ->  [{"start": seconds, "end": seconds, "text": "..."}]

Reads SubRip (.srt), WebVTT (.vtt), Whisper or faster-whisper JSON ({"segments": [...]}) and
YouTube's json3 caption format ({"events": [...]}). Shared by the yt-edit, yt-chapters and
yt-retention tools; each folder keeps its own copy so it works when copied on its own.
"""
import json
import re

TS = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")


def to_seconds(ts):
    m = TS.search(ts)
    if not m:
        raise ValueError("not a timestamp: %r" % ts)
    h, mi, s, ms = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000.0


def fmt(sec):
    sec = max(0, int(round(sec)))
    h, rest = divmod(sec, 3600)
    m, s = divmod(rest, 60)
    return "%d:%02d:%02d" % (h, m, s) if h else "%d:%02d" % (m, s)


def _clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{[^}]+\}", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_srt_vtt(text):
    cues = []
    blocks = re.split(r"\n\s*\n", text.replace("\r", "").strip())
    for b in blocks:
        lines = [l for l in b.split("\n") if l.strip()]
        for i, l in enumerate(lines):
            if "-->" in l:
                a, z = l.split("-->", 1)
                try:
                    start, end = to_seconds(a), to_seconds(z)
                except ValueError:
                    break
                body = _clean(" ".join(lines[i + 1:]))
                if body:
                    cues.append({"start": start, "end": end, "text": body})
                break
    return cues


def parse_json(data):
    if isinstance(data, dict) and "segments" in data:
        return [{"start": float(s["start"]), "end": float(s["end"]), "text": _clean(s.get("text", ""))}
                for s in data["segments"] if _clean(s.get("text", ""))]
    if isinstance(data, dict) and "events" in data:
        cues = []
        for e in data["events"]:
            segs = e.get("segs") or []
            text = _clean("".join(s.get("utf8", "") for s in segs))
            if not text:
                continue
            start = e.get("tStartMs", 0) / 1000.0
            end = start + e.get("dDurationMs", 0) / 1000.0
            cues.append({"start": start, "end": end, "text": text})
        return cues
    if isinstance(data, list):
        return [{"start": float(s["start"]), "end": float(s["end"]), "text": _clean(s["text"])}
                for s in data if _clean(s.get("text", ""))]
    raise ValueError("unknown JSON transcript shape")


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    if path.lower().endswith(".json") or text.lstrip().startswith(("{", "[")):
        cues = parse_json(json.loads(text))
    else:
        cues = parse_srt_vtt(text)
    cues.sort(key=lambda c: c["start"])
    return cues
