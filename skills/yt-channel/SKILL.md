---
name: yt-channel
description: "Create or update the channel file every minga-youtube skill reads: the one viewer, the promise, how the host talks on camera, the format, what the channel will not claim. Use for 'set up my channel', 'channel voice', 'write my channel profile from these videos'; RU: настрой канал, профиль канала, голос канала, опиши мой канал. Run it first."
---

# yt-channel

Writes `~/.claude/minga-youtube/channel.md` from `templates/channel.md` in this repository
(headings: Who it is for, How the host talks on camera, Format, Will not claim, Proof the host can
use). Several channels: one file each in `~/.claude/minga-youtube/channels/<slug>.md`.

## Two ways

**From videos (better).** Ask for two or three of the channel's best videos as transcripts or
links. Fill the file from how the host actually talks: words, sentence length, how the viewer is
addressed, how videos open, the pace. Quote the transcript as evidence.

**From questions,** in one batch, when there are no videos yet: the one viewer, the promise, the
format, what it leads to, what it will never claim.

## Rules

- **The viewer is one person in a situation**, not a demographic.
- **Proof is real or empty.** Empty is fine; the other skills will leave placeholders.
- **If the host is already a minga-reels persona**, link that file and only add what long-form
  needs: format, rhythm, best upload time.

Output: the path, the file, and one line on what is still thin.
