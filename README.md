# minga-youtube

**Eleven Claude skills for long-form YouTube, in Russian and English: the channel's voice, scripts timed section by section, the title and thumbnail linted as one pairing, edit decision lists from a transcript, chapters that actually render, retention read properly, SEO, comments, plans, research and an audit that ends in one fix.**

Part of the [Minga](https://github.com/dmminga1983/minga) ecosystem. The long-form companion to [minga-reels](https://github.com/dmminga1983/minga-reels): same hook formulas, same Russian and English text engine, and Shorts cut from a long video go to `/reels-repurpose`. Free, MIT, no API key, nothing to connect. **Nothing is uploaded for you:** every skill ends with a copy-ready block and "ship it, or change it?".

[Русская версия →](README.ru.md)

## The eleven

| command | what it does |
| --- | --- |
| `/yt-channel` | The channel file every skill reads: the one viewer, the promise, how the host talks, the format. |
| `/yt-script` | Five hooks from 26 formulas, scored; the turn by 0:45; beats with what is on screen; timed by `outline.py`. |
| `/yt-package` | Title and thumbnail as one unit, linted by `title.py`: mobile cut, concreteness, hype, caps, repetition. |
| `/yt-edit` | A transcript into an edit decision list: dead air, filler, retakes, with timecodes and a CSV. |
| `/yt-chapters` | Chapters from a transcript, validated against YouTube's rules so they render. |
| `/yt-retention` | The Studio retention export: hook leak, cliffs with what was said there, the slide, and one change. |
| `/yt-seo` | The description and tags, and the query test: do the title and first two lines contain the searches? |
| `/yt-comment` | Comment triage, replies in the channel's voice, which one to pin. |
| `/yt-plan` | A week that fits the hours: one anchor, one cheap one, Shorts from the anchor. |
| `/yt-viral` | What works in the niche, by multiple over each channel's own median, with the title formula. |
| `/yt-audit` | The whole channel, ending in ONE fix rather than twenty. |

## Install

**Claude Code**, as a plugin:

```
/plugin marketplace add dmminga1983/minga-youtube
/plugin install minga-youtube@minga-youtube
```

Or copy the folders for plain `/yt-script` and so on:

```bash
git clone https://github.com/dmminga1983/minga-youtube.git
cp -r minga-youtube/skills/yt-* ~/.claude/skills/
```

**claude.ai**: zip one skill folder and upload it under Settings, Capabilities, Skills.

The tools need Python 3.8 or newer and nothing else. Then run `/yt-channel`, or send Claude three of your videos and say "write the channel file from these".

## The tools

Standard-library Python, no network, nothing uploaded.

```bash
python3 skills/yt-script/hookscore.py hooks.txt                 # hook panel, 26 formulas
python3 skills/yt-script/outline.py script.md --pace 4.8         # time each section
python3 skills/yt-package/title.py --title "..." --thumb "..."   # the pairing
python3 skills/yt-edit/deadair.py transcript.srt --csv cuts.csv  # edit decision list
python3 skills/yt-chapters/chapters.py transcript.srt --target 8 # valid chapters
python3 skills/yt-chapters/chapters.py --check chapters.txt
python3 skills/yt-retention/retention.py retention.csv --duration 612 --transcript t.srt
python3 skills/yt-seo/seo.py --title "..." --queries "q1,q2" --tags "t1,t2" desc.txt
python3 skills/yt-viral/swipe.py collected.tsv --min 2
```

Transcripts can be SubRip, WebVTT, Whisper JSON or YouTube's json3 captions. The retention reader accepts Studio exports with Russian or English column names and positions in seconds, mm:ss or shares of the video.

```bash
python3 -m unittest discover -s tests -v
```

## The fine print

- **It does not upload.** YouTube's API would allow it with your own OAuth; it is still not built here on purpose. You publish.
- **The hook score is a heuristic.** It catches weak openings well and cannot pick the winner between two good ones. `calibrate.py` in minga-reels measures it on your own videos.
- **Title formulas describe the words, not the cause.** When `/yt-viral` names a formula, that is about the title you can see, not why the video got its views.
- **Research reads, it does not scrape.** Public listings with `yt-dlp` on your own computer, never a logged-in session.
- **Tags barely matter**, and the pack says so instead of selling you a tag generator.
- **Nothing invents a number.** A missing figure is asked for or left as `{{your number}}`.
- **Platform numbers move.** The limits here were checked in October 2026. If YouTube says otherwise, YouTube is right.

## Credit

Made by [dmminga1983](https://github.com/dmminga1983). Inspired by Jake Schincariol's [youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill); the tools and skills here are written from scratch, for Russian and English.

## License

MIT.
