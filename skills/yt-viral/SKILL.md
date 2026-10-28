---
name: yt-viral
description: "Find what is working in the channel's niche on YouTube long-form and rank each video by its multiple over its own channel's median, then name the title formula and the one structural thing the winners share. Use for 'what's working', 'competitor research', 'find outliers in my niche', 'why did this video blow up'; RU: что заходит на ютубе, анализ конкурентов, найди залетевшие видео, почему видео выстрелило."
---

# yt-viral

```bash
python3 swipe.py collected.tsv --min 2 --out ~/.claude/minga-youtube/swipe.md
```

Uses `../yt-script/hooks.json` for formula names and `../yt-package/title.py` for title scores.

## The idea

Raw views rank channel size. Rank by **multiple over the channel's own median**, which is about
the video. For long-form, 2x is already a signal.

## Collecting

At least eight long videos per channel, or the median means nothing. On the user's own computer:

```bash
python3 -m yt_dlp --flat-playlist --playlist-end 30 -J "https://www.youtube.com/@HANDLE/videos" > ch.json
```

The cloud session usually cannot reach YouTube: say so and ask the user to run it. Public
listings only, never a logged-in session. Write `collected.tsv` with account, median, views, hook
(the title), and optional length and url.

## Reading it

The formula is a judgement about the title's words, not a claim about why the video got its
views: say so. Hand back the top five with multiples and formulas, the ONE structural thing they
share, and the harder line: which of them this channel could make this week, in its own voice,
with what it has.
