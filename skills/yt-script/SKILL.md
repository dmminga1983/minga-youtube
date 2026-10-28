---
name: yt-script
description: "Write a long-form YouTube script from an idea: five hooks from 26 formulas scored by a local tool, the turn by 0:45, beats with what is on screen, the payoff said out loud, timed section by section. Use for 'write my video', 'YouTube script', 'outline this video', 'what do I say in the first 30 seconds'; RU: сценарий для ютуба, напиши видео, структура ролика, что говорить в начале."
---

# yt-script

```bash
python3 hookscore.py hooks.txt            # rank hook options (Russian and English)
python3 outline.py script.md --pace 4.8   # time each section, flag the slow parts
```

## Before you write

1. Read the channel file: `~/.claude/minga-youtube/channel.md`, or the one the user names in
   `channels/`. No file yet: run /yt-channel, or ask for three of the channel's videos and write it
   from them. A script in the wrong voice is worse than none, because someone has to say it.
2. Never invent a number, a result, a quote or a source. If a figure would help and the channel
   file does not have it, ask for it or write `{{your number}}` and flag it.
3. Reply in the user's language; write the content in the channel's language.

## The shape

**The first fifteen seconds are the whole job.** They confirm the click the title promised, open
a question the viewer cannot close, and prove the payoff exists.

1. **Hook.** Write five against `hooks.json`, run `hookscore.py`, keep the top two, show both with
   their scores. Never hand over one hook. The packaging (/yt-package) and the hook must promise
   the same thing.
2. **The turn**, by 0:45. One sentence on what the video will do, then start doing it. No channel
   intro, no "before we start", no subscribe pitch: those cause the 0:30 cliff more than anything.
3. **The body.** One idea per beat, each beat marked `[SCREEN: ...]` with what the viewer sees: a
   talking head with nothing to look at is a podcast. A pattern break (a cut, a graphic, a demo)
   at least every 60 to 90 seconds.
4. **The payoff.** Deliver what the hook promised, explicitly, and say that you are delivering it.
5. **The close.** One ask. Not three.

Write it with `## headings` per section and run `outline.py`. Fix every flag: opening past 45
seconds, an intro or a pitch up front, a section over three minutes with nothing on screen, a
section with nothing concrete, a close that never refers back to the opening.

## Output

The two hooks with scores, the script by section with `[SCREEN]` notes, the runtime from
`outline.py`, and one line on which formula the winning hook uses and why it fits. Shorts hiding
inside it: hand the script or the transcript to /reels-repurpose if minga-reels is installed.

## The gate

Nothing here uploads or publishes. Every run ends with a copy-ready block and the question:
**ship it, or change it?**
