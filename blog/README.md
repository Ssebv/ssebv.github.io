# Blog

Writing is Markdown in `blog/posts/`. One command turns it into pages.

```bash
python3 blog/build.py
git add -A && git commit -m "Nuevo post: ..." && git push
```

No dependencies, no Ruby, no `npm install`. Plain `python3` — it will still work in five years.

---

## Writing a post

Create `blog/posts/YYYY-MM-DD-slug.LANG.md`:

```markdown
---
title: Why our nightly job failed a day late
subtitle: A short line shown next to the date
date: 2026-08-14
lang: en
slug: nightly-job
summary: One or two sentences. Used in the index, the RSS feed and the social card.
tags: postgres, debugging
---

Opening paragraph. No `# H1` — the title comes from the frontmatter.

## A section

Body text with **bold**, *italic*, `inline code` and [links](https://example.com).

- A list item
- Another one

```python
print("fenced code blocks work, with syntax label")
```

> A pull quote for something worth emphasising.

::: note
A callout box, for the lesson you want the reader to leave with.
:::

| Column | Column |
|---|---|
| Tables | work too |
```

**Required frontmatter:** `title`, `date`, `lang`, `slug`, `summary`.
**Optional:** `subtitle`, `tags`.

`lang` is `en` or `es`. Two files sharing the same `slug` with different `lang` are
treated as translations of each other and cross-linked automatically by the EN/ES switch.

---

## What the build does

| Output | From |
|---|---|
| `writing/<slug>.html` | each `lang: en` post |
| `es/writing/<slug>.html` | each `lang: es` post |
| `writing/index.html`, `es/writing/index.html` | all posts, newest first |
| `feed.xml` | the English posts |
| `sitemap.xml` | every page, with `hreflang` alternates |

Reading time, section anchors, the floating section nav, the `hreflang` tags, the JSON-LD
and the "read next" card are all generated. You never touch HTML.

Check what would change without writing anything:

```bash
python3 blog/build.py --check
```

---

## Social preview card

Posts fall back to the site-wide `og.png`. For a dedicated card, drop an image at
`og-<slug>.png` (1200×630) in the site root and the build picks it up on its own.

---

## The Markdown subset

`markdown_min.py` is ~170 lines and deliberately supports only what a technical post needs:
headings, paragraphs, bold, italic, inline code, links, images, fenced code blocks, ordered
and unordered lists, blockquotes, callouts, tables and horizontal rules.

If you need something it does not do, add it there. That is cheaper than taking on a
dependency that has to be installed on every machine you ever write from.
