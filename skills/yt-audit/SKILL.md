---
name: yt-audit
description: "Audit a YouTube channel end to end and end in ONE fix: the last ten titles as a set, thumbnails at feed size, the first fifteen seconds of recent videos, upload rhythm, retention. Use for 'audit my channel', 'why isn't my channel growing', 'review my videos', a pasted channel URL; RU: аудит канала, почему канал не растёт, разбери мой канал, что улучшить на канале."
---

# yt-audit

An audit that lists twenty problems is a way of avoiding the one that matters. This one ends in
one fix.

## Before you write

1. Read the channel file: `~/.claude/minga-youtube/channel.md`, or the one the user names in
   `channels/`. No file yet: run /yt-channel, or ask for three of the channel's videos and write it
   from them. A script in the wrong voice is worse than none, because someone has to say it.
2. Never invent a number, a result, a quote or a source. If a figure would help and the channel
   file does not have it, ask for it or write `{{your number}}` and flag it.
3. Reply in the user's language; write the content in the channel's language.

## What to look at, in this order

1. **The last ten titles as a set**, the way the channel page shows them. Run them through
   `../yt-package/title.py`. Every title the same shape is a format problem, not a title problem.
2. **The thumbnails at feed size.** Shrink them. If three are unreadable small, that is the fix and
   nothing else matters yet.
3. **The first fifteen seconds of the three most recent videos.** Transcribe and score the hooks
   with `../yt-script/hookscore.py`. Most channels lose here.
4. **Upload rhythm**: consistency, not frequency.
5. **Retention**, if the user can export it: /yt-retention.

## What to hand back

- The single biggest fix, named, with what to do this week.
- Three things that already work, specifically, so they do not get broken.
- What not to do yet, and why.

Never open with praise you do not mean, and never end with a list of twenty.
