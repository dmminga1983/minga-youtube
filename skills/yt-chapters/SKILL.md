---
name: yt-chapters
description: "Write YouTube chapters from a transcript and check them against YouTube's own rules so they actually render: first at 0:00, at least three, each at least 10 seconds. Also validates a hand-written list. Use for 'add chapters', 'timestamps', 'split this video into sections'; RU: главы, таймкоды, раздели видео на части, тайм-коды в описание."
---

# yt-chapters

```bash
python3 chapters.py transcript.srt --target 8
python3 chapters.py --check chapters.txt
```

## The rules, which are not optional

YouTube only turns a list into chapters when the first timestamp is 0:00, there are at least
three in ascending order, and each chapter lasts at least 10 seconds. Break one and the block sits
in the description doing nothing. The tool refuses to print an invalid list.

## Retitle every line

The tool finds the boundaries well: the pauses where the vocabulary changes most. Its titles are
topic words, a draft. Rewrite each as the promise of that section, three to five words, in the
channel's voice ("Как подписать акт с замечаниями", not "Акт замечаний квартиры").

Chapters double as a retention check: a section that cannot be named in five words is two
sections or filler. Say so.

Paste the final list into the description, then run `../yt-seo/seo.py` on it.

## The gate

Nothing here uploads or publishes. Every run ends with a copy-ready block and the question:
**ship it, or change it?**
