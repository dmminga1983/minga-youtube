---
name: yt-seo
description: "Write the description, tags and search-facing text for a YouTube video, aimed at the queries real people type, and check it with a local tool: the query test, the first line, chapters, the 500-character tag limit and the hashtag cap. Use for 'description', 'tags', 'SEO', 'nobody finds this video'; RU: описание к видео, теги, SEO, видео не находят в поиске."
---

# yt-seo

```bash
python3 seo.py --title "..." --queries "акт приёмки с замечаниями,гарантия на квартиру" \
               --tags "акт приёмки,приёмка квартиры" description.txt
```

## Before you write

1. Read the channel file: `~/.claude/minga-youtube/channel.md`, or the one the user names in
   `channels/`. No file yet: run /yt-channel, or ask for three of the channel's videos and write it
   from them. A script in the wrong voice is worse than none, because someone has to say it.
2. Never invent a number, a result, a quote or a source. If a figure would help and the channel
   file does not have it, ask for it or write `{{your number}}` and flag it.
3. Reply in the user's language; write the content in the channel's language.

Search is a smaller lever than packaging and a bigger one than people think for evergreen videos.
For a video aimed at the subscriber feed, say so and spend the effort on /yt-package.

## The description

- **The first two lines are the only ones most people read**: above "...more" and in the search
  snippet. What the video gives, in the words the viewer would type.
- The link or the resource next, if there is one.
- Chapters (/yt-chapters).
- Then the longer version: what is covered, who it is for, what it assumes.

## Tags, honestly

A weak signal. Use them for spellings, names, abbreviations people type, then stop: 500 characters
is the limit and fifteen tags is plenty. Unrelated tags are against YouTube's rules.

## The query test

Write the three searches the video should win and run `seo.py`. Every meaningful word of each
query should be in the title or the first two lines. If not, the problem is the title.

## The gate

Nothing here uploads or publishes. Every run ends with a copy-ready block and the question:
**ship it, or change it?**
