---
name: yt-plan
description: "Plan a week or a month of YouTube uploads sized to the hours the creator actually has: one anchor video, one cheap one built from what exists, Shorts cut from the anchor, with what each promises and what is already made. Use for 'plan my week', 'content calendar', 'what should I make next'; RU: план видео, контент-план для ютуба, что снимать дальше, график выхода."
---

# yt-plan

## Before you write

1. Read the channel file: `~/.claude/minga-youtube/channel.md`, or the one the user names in
   `channels/`. No file yet: run /yt-channel, or ask for three of the channel's videos and write it
   from them. A script in the wrong voice is worse than none, because someone has to say it.
2. Never invent a number, a result, a quote or a source. If a figure would help and the channel
   file does not have it, ask for it or write `{{your number}}` and flag it.
3. Reply in the user's language; write the content in the channel's language.

Ask two things before writing: **how many hours there really are**, and **what is already half
made**. Read `~/.claude/minga-youtube/swipe.md` and the last /yt-audit if they exist.

## The shape of a week

- **One anchor**: the video the week is for. Most of the time. Published on the day and hour the
  channel's own analytics say is best: ask, do not assume.
- **One cheap one**: built from something that exists: a follow-up to the most-replied comment,
  a reaction, a short tutorial cut from the anchor's research.
- **Shorts from the anchor**: two or three, cut from the long video (/reels-repurpose if
  minga-reels is installed), not written separately.

Three uploads in seven days, not seven. Consistency beats volume: one a fortnight forever beats
six in a week and then a month of nothing.

## Output

A table: day, format, working title, the one sentence it promises, what already exists for it.
Then the honest line: how many hours this costs and what to drop first if the week goes wrong.
