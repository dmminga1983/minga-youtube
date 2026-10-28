---
name: yt-package
description: "Write and lint the title and thumbnail of a YouTube video as one pairing: ten titles, scored by a local tool for length, mobile cut, concreteness, hype, caps and repetition between title and thumbnail, plus a thumbnail brief. Use for 'title ideas', 'what should I call this', 'thumbnail text', 'my CTR is low', 'repackage this video'; RU: название для видео, текст на превью, обложка, низкий CTR, переупаковать."
---

# yt-package

```bash
python3 title.py --title "Я переплатил 40 000 из-за одного пункта" --thumb "НЕ ПОДПИСЫВАЙ"
python3 title.py titles.txt      # one per line, "title | thumbnail text"
```

## Before you write

1. Read the channel file: `~/.claude/minga-youtube/channel.md`, or the one the user names in
   `channels/`. No file yet: run /yt-channel, or ask for three of the channel's videos and write it
   from them. A script in the wrong voice is worse than none, because someone has to say it.
2. Never invent a number, a result, a quote or a source. If a figure would help and the channel
   file does not have it, ask for it or write `{{your number}}` and flag it.
3. Reply in the user's language; write the content in the channel's language.

## One unit

The title and the thumbnail are read together in under a second. Different words, the same
promise. If the thumbnail repeats the title, half the click surface is wasted, and the tool says
so.

What the tool enforces: up to 100 characters, about 60 visible in desktop search and 40 to 50 in
the mobile feed (the subject must survive the mobile cut); a number, a name or a date; no hype
words or clickbait the video cannot pay off; two all-caps words at most; three words at most on
the thumbnail.

## Write ten, keep two

Write ten titles from different formulas, run them all, show the top three with their scores and
the specific issue on each. For the winner, the thumbnail brief: the expression, the framing, the
three words, the one object, and what the background does to hold contrast at feed size. The
thumbnail must be true to the video: a promise the video breaks costs retention and trust.

If the persona is an AI character, the thumbnail uses the same character and the video carries
the AI label.

## The gate

Nothing here uploads or publishes. Every run ends with a copy-ready block and the question:
**ship it, or change it?**
