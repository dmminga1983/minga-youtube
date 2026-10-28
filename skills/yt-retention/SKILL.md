---
name: yt-retention
description: "Read a YouTube Studio audience-retention export and say where viewers actually left and what to change: hook leak in the first 30 seconds, cliffs with what was being said at that moment, the mid-video slide. Use for 'why do people stop watching', 'my retention is bad', a retention CSV or chart, 'fix my pacing'; RU: удержание, почему уходят зрители, досматриваемость, график удержания."
---

# yt-retention

```bash
python3 retention.py retention.csv --duration 612
python3 retention.py retention.csv --duration 612 --transcript transcript.srt
```

The file: Studio, the video, Analytics, Engagement, the audience-retention chart, the download
icon. A screenshot of the chart works for a first look: read the values off it into a CSV.

## Three problems, three fixes

- **HOOK LEAK**: points lost in the first 30 seconds. Under 25 is healthy. Always the first fifteen
  seconds of script, never the edit. Go to /yt-script.
- **CLIFFS**: single steep drops. With `--transcript` the tool prints what was said there: a topic
  change with no signpost, a sponsor read, a long setup. Signpost it or cut it.
- **SLIDE**: the steady bleed through the middle. Pacing: cut, do not rewrite. /yt-edit.

## What to hand back

The single biggest leak and one change for it. Not five. If the hook holds and the slide is flat,
say the video is fine and the problem is packaging: /yt-package.
