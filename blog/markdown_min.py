"""
Minimal Markdown → HTML converter, no dependencies.

Supported, deliberately: headings (##, ###), paragraphs, **bold**, *italic*,
`code`, [links](url), fenced code blocks (```lang), unordered and ordered
lists, blockquotes (>), callouts (::: note ... :::), tables,
horizontal rules (---), and images.

Deliberately not supported: HTML passthrough beyond raw blocks, footnotes,
definition lists, nested blockquotes. If you need one of those, the honest
move is to add it here rather than to reach for a dependency.
"""

import html
import re


def _inline(text):
    """Inline formatting. Code spans are protected first so their contents
    are never treated as markup."""
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)

    # images before links: ![alt](src)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
                  r'<img src="\2" alt="\1" loading="lazy">', text)
    # [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2)}"'
                            f'{" target=_blank rel=noopener" if m.group(2).startswith("http") else ""}'
                            f'>{m.group(1)}</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", text)

    for i, code in enumerate(spans):
        text = text.replace(f"\x00{i}\x00", f"<code>{html.escape(code, quote=False)}</code>")
    return text


def slugify(text):
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def convert(md, anchor_label="Link to this section"):
    """Returns (html, [(level, id, text), ...]) so callers can build a TOC."""
    lines = md.replace("\r\n", "\n").split("\n")
    out, toc = [], []
    i, n = 0, len(lines)

    def flush_para(buf):
        if buf:
            out.append(f"<p>{_inline(' '.join(buf).strip())}</p>")
            buf.clear()

    para = []
    while i < n:
        line = lines[i]

        # fenced code
        if line.startswith("```"):
            lang = line[3:].strip()
            flush_para(para)
            body, i = [], i + 1
            while i < n and not lines[i].startswith("```"):
                body.append(lines[i]); i += 1
            i += 1
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>")
            continue

        # callout: ::: note ... :::
        if line.strip().startswith(":::"):
            flush_para(para)
            body, i = [], i + 1
            while i < n and not lines[i].strip().startswith(":::"):
                body.append(lines[i]); i += 1
            i += 1
            inner, _ = convert("\n".join(body))
            out.append(f'<div class="note">{inner}</div>')
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}", line.strip()):
            flush_para(para); out.append("<hr>"); i += 1; continue

        # headings
        m = re.match(r"^(#{2,4})\s+(.*)$", line)
        if m:
            flush_para(para)
            lvl, text = len(m.group(1)), m.group(2).strip()
            sid = slugify(text)
            toc.append((lvl, sid, text))
            inner = _inline(text)
            anchor = (f'<a class="anchor" href="#{sid}" aria-label="{anchor_label}">#</a>'
                      if lvl == 2 else "")
            out.append(f'<h{lvl} id="{sid}">{inner}{anchor}</h{lvl}>')
            i += 1; continue

        # blockquote
        if line.startswith(">"):
            flush_para(para)
            body = []
            while i < n and lines[i].startswith(">"):
                body.append(lines[i].lstrip(">").strip()); i += 1
            chunks = " ".join(body).split("  ")
            out.append("<blockquote>" +
                       "".join(f"<p>{_inline(c.strip())}</p>" for c in chunks if c.strip()) +
                       "</blockquote>")
            continue

        # table
        if "|" in line and i + 1 < n and re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", lines[i + 1]) \
                and "-" in lines[i + 1]:
            flush_para(para)
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]
            head = cells(line); i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(cells(lines[i])); i += 1
            th = "".join(f"<th>{_inline(c)}</th>" for c in head)
            body = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>"
                           for r in rows)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead>'
                       f"<tbody>{body}</tbody></table></div>")
            continue

        # lists
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            flush_para(para)
            ordered = bool(re.match(r"\d+\.", m.group(2)))
            items, base = [], len(m.group(1))
            while i < n:
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if mm and len(mm.group(1)) == base:
                    items.append(mm.group(3)); i += 1
                elif lines[i].strip() and lines[i].startswith(" " * (base + 2)) and items:
                    items[-1] += " " + lines[i].strip(); i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + f"</{tag}>")
            continue

        # raw HTML block passthrough
        if line.strip().startswith("<") and not line.strip().startswith("<http"):
            flush_para(para); out.append(line); i += 1; continue

        if not line.strip():
            flush_para(para); i += 1; continue

        para.append(line); i += 1

    flush_para(para)
    return "\n".join(out), toc


def word_count(md):
    body = re.sub(r"```.*?```", " ", md, flags=re.S)
    body = re.sub(r"[#>*`|_\-\[\]()]", " ", body)
    return len(body.split())


def reading_minutes(md, wpm=200):
    return max(1, round(word_count(md) / wpm))
