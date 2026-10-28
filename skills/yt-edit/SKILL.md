---
name: yt-edit
description: "Turn a raw recording's transcript into an edit decision list: dead air trimmed from the middle, filler cues, restarted sentences, with timecodes and a CSV for the editor. Russian and English fillers. Use for 'edit this', 'cut the pauses', 'tighten the video', 'I rambled', 'remove the ums'; RU: смонтируй, вырежи паузы, убери э-э, сократи видео, монтажный лист."
---

# yt-edit

```bash
python3 deadair.py transcript.srt              # .srt, .vtt, Whisper JSON, YouTube json3
python3 deadair.py transcript.srt --floor 0.6 --csv cuts.csv
```

No transcript yet: make one first with Whisper or faster-whisper on the user's computer
(`whisper video.mp4 --language ru --output_format srt`), or upload unlisted and download
YouTube's automatic captions. Do not guess timings.

## What it finds

- **DEAD**: pauses longer than the floor, trimmed from the middle so both sides keep a breath.
- **FILLER**: cues that are nothing but "ну", "короче", "типа", "э-э", "um", "so yeah".
- **RETAKE**: a sentence started again; it keeps the second take.

## What it cannot do

It never touches media and cannot see silent footage. A long demo with no talking looks like dead
air to it: check the list against the timeline before cutting, and treat the runtime at the
bottom as speech time, not video time.

## Output

The list, the CSV path for the editor, and the honest line: how much shorter, and which cuts to
check by eye. Shorts candidates noticed along the way go to /reels-repurpose.
