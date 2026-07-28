#!/usr/bin/env python3
"""
Blog builder — turns blog/posts/*.md into the site's article pages.

    python3 blog/build.py            # build everything
    python3 blog/build.py --check    # build to a temp dir and diff, changing nothing

Each post is a Markdown file with a frontmatter block:

    ---
    title: The bugs that survive an ERP upgrade
    subtitle: Migrating five major versions forward
    date: 2026-07-28
    lang: en                  # en | es
    slug: erp-migration       # output filename; pairs EN/ES when shared
    summary: One or two sentences for the index, the feed and social cards.
    tags: odoo, migration
    ---

Outputs: writing/<slug>.html, es/writing/<slug>.html, both index pages,
feed.xml and sitemap.xml.
"""

import argparse
import html
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from markdown_min import convert, reading_minutes, slugify  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "blog" / "posts"
SITE = "https://ssebv.github.io"

MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]
RFC_MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

T = {
    "en": dict(sections="Sections", skip="Skip to content", back="← Sebastián Allende",
               backfoot="← Back to portfolio", read="min read", next="Read next",
               anchor="Link to this section", writing="Writing",
               tagline="Notes on running ERP and financial systems in production",
               langlabel="Language", themelabel="Switch colour theme", case="Case study"),
    "es": dict(sections="Secciones", skip="Saltar al contenido", back="← Sebastián Allende",
               backfoot="← Volver al portafolio", read="min de lectura", next="Sigue leyendo",
               anchor="Enlace a esta sección", writing="Escritos",
               tagline="Notas sobre operar sistemas ERP y financieros en producción",
               langlabel="Idioma", themelabel="Cambiar tema de color", case="Caso"),
}

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
           "%3Crect width='100' height='100' rx='22' fill='%232f5bd7'/%3E%3Ctext x='50' y='68' "
           "font-family='Helvetica,Arial,sans-serif' font-size='48' font-weight='700' fill='%23fff' "
           "text-anchor='middle'%3ESA%3C/text%3E%3C/svg%3E")

NOFLASH = ("<script>\n(function(){try{var t=localStorage.getItem('theme');"
           "if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}})();\n</script>")

TOGGLE = """<button class="theme-toggle" id="themeToggle" type="button" aria-label="{lbl}" title="{lbl}">
  <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
  <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
</button>"""

SCRIPTS = """<script>
(function(){
  var b=document.getElementById('themeToggle');if(!b)return;
  b.addEventListener('click',function(){
    var sysDark=window.matchMedia('(prefers-color-scheme: dark)').matches;
    var cur=document.documentElement.getAttribute('data-theme')||(sysDark?'dark':'light');
    var next=cur==='dark'?'light':'dark';
    document.documentElement.setAttribute('data-theme',next);
    try{localStorage.setItem('theme',next);}catch(e){}
  });
})();
</script>
<script>
(function(){
  if (window.innerWidth < 1280) return;
  var heads = [].slice.call(document.querySelectorAll('main h2[id], article h2[id]'));
  if (heads.length < 3) return;
  var nav = document.createElement('nav');
  nav.className = 'toc';
  nav.setAttribute('aria-label','%SECTIONS%');
  nav.innerHTML = '<div class="toc-label">%SECTIONS%</div><ol></ol>';
  var ol = nav.querySelector('ol');
  heads.forEach(function(h){
    var text = (h.textContent || '').replace(/#$/, '').trim();
    var li = document.createElement('li'), a = document.createElement('a');
    a.href = '#' + h.id; a.textContent = text; a.dataset.target = h.id;
    li.appendChild(a); ol.appendChild(li);
  });
  document.body.appendChild(nav);
  requestAnimationFrame(function(){ nav.classList.add('ready'); });
  var links = {};
  [].slice.call(nav.querySelectorAll('a')).forEach(function(a){ links[a.dataset.target] = a; });
  function setActive(id){ for (var k in links) links[k].classList.toggle('active', k === id); }
  var obs = new IntersectionObserver(function(entries){
    var v = entries.filter(function(e){ return e.isIntersecting; });
    if (v.length) { v.sort(function(a,b){ return a.boundingClientRect.top - b.boundingClientRect.top; });
      setActive(v[0].target.id); }
  }, { rootMargin: '-15% 0px -70% 0px', threshold: 0 });
  heads.forEach(function(h){ obs.observe(h); });
  setActive(heads[0].id);
})();
</script>
<script>
(function(){
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-reveal');
    var targets = [].slice.call(document.querySelectorAll('article > *, .post, section > *'));
    targets.forEach(function(el){ el.setAttribute('data-reveal',''); });
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (!e.isIntersecting) return;
        e.target.style.transitionDelay = Math.min((+e.target.dataset.i||0)*45,180)+'ms';
        e.target.classList.add('shown'); io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    var groups = {};
    targets.forEach(function(el){
      var k = el.parentNode; groups[k] = groups[k] || 0; el.dataset.i = groups[k]++; io.observe(el);
    });
    setTimeout(function(){
      targets.forEach(function(el){
        if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add('shown');
      });
    }, 30);
  }
  if (!reduce && document.querySelector('article')) {
    var bar = document.createElement('div'); bar.className = 'progress';
    document.body.appendChild(bar);
    var tick = function(){
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
    };
    window.addEventListener('scroll', tick, { passive: true });
    window.addEventListener('resize', tick); tick();
  }
})();
</script>"""


def parse_post(path):
    raw = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        sys.exit(f"ERROR: {path.name} has no frontmatter block (--- ... ---)")
    meta = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for req in ("title", "date", "lang", "slug", "summary"):
        if req not in meta:
            sys.exit(f"ERROR: {path.name} is missing '{req}' in its frontmatter")
    if meta["lang"] not in ("en", "es"):
        sys.exit(f"ERROR: {path.name} has lang '{meta['lang']}' (expected en or es)")
    meta["body"] = m.group(2)
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["minutes"] = reading_minutes(m.group(2))
    meta["source"] = path.name
    return meta


def human_date(iso, lang):
    y, mo, d = (int(x) for x in iso.split("-"))
    return (f"{d} de {MONTHS_ES[mo-1]} de {y}" if lang == "es"
            else f"{d} {MONTHS_EN[mo-1]} {y}")


def rfc_date(iso):
    y, mo, d = (int(x) for x in iso.split("-"))
    return f"{d:02d} {RFC_MON[mo-1]} {y} 12:00:00 GMT"


def render_post(post, siblings, out_root):
    lang, slug = post["lang"], post["slug"]
    t = T[lang]
    body, _ = convert(post["body"], anchor_label=t["anchor"])
    prefix = "es/writing" if lang == "es" else "writing"
    depth = "../../" if lang == "es" else "../"

    url = f"{SITE}/{prefix}/{slug}.html"
    alt_lang = "es" if lang == "en" else "en"
    alt_prefix = "es/writing" if alt_lang == "es" else "writing"
    has_alt = any(s["slug"] == slug and s["lang"] == alt_lang for s in siblings)
    alt_url = f"{SITE}/{alt_prefix}/{slug}.html"

    og = f"{SITE}/og-{slug}.png"
    if not (out_root / f"og-{slug}.png").exists():
        og = f"{SITE}/og.png"

    alt_tags = ""
    if has_alt:
        alt_tags = (f'<link rel="alternate" hreflang="{lang}" href="{url}">\n'
                    f'<link rel="alternate" hreflang="{alt_lang}" href="{alt_url}">\n')
        rel = (f"../{alt_prefix.split('/')[-1]}/{slug}.html" if lang == "es"
               else f"../es/writing/{slug}.html")
        lang_nav = (f'<nav class="lang-switch" aria-label="{t["langlabel"]}">\n'
                    f'  <a href="{"../../writing/" + slug + ".html" if lang == "es" else "./" + slug + ".html"}" '
                    f'hreflang="en"{"" if lang == "es" else " aria-current=\"true\""}>EN</a>\n'
                    f'  <a href="{"./" + slug + ".html" if lang == "es" else "../es/writing/" + slug + ".html"}" '
                    f'hreflang="es"{" aria-current=\"true\"" if lang == "es" else ""}>ES</a>\n'
                    f'</nav>\n')
    else:
        lang_nav = ""

    # next post: same language, most recent other than this one
    others = sorted([s for s in siblings if s["lang"] == lang and s["slug"] != slug],
                    key=lambda s: s["date"], reverse=True)
    next_up = ""
    if others:
        o = others[0]
        next_up = f"""
    <nav class="next-up" aria-label="{t['next']}">
      <div class="label">{t['next']}</div>
      <a class="proj" href="./{o['slug']}.html">
        <div class="proj-top">
          <span class="proj-name">{html.escape(o['title'])}</span>
          <span class="tag">{t['case']}</span>
        </div>
        <p>{html.escape(o['summary'])}</p>
      </a>
    </nav>
"""

    subtitle = post.get("subtitle", "")
    meta_line = (f'<time datetime="{post["date"]}">{human_date(post["date"], lang)}</time>'
                 + (f'<span class="dot">·</span>{html.escape(subtitle)}' if subtitle else "")
                 + f'<span class="dot">·</span>{post["minutes"]} {t["read"]}')

    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
{NOFLASH}

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{html.escape(post['title'])} — Sebastián Allende</title>
<meta name="description" content="{html.escape(post['summary'])}">
<link rel="canonical" href="{url}">
{alt_tags}
<meta property="og:type" content="article">
<meta property="og:locale" content="{'es_CL' if lang == 'es' else 'en_US'}">
<meta property="og:title" content="{html.escape(post['title'])}">
<meta property="og:description" content="{html.escape(post['summary'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta property="article:published_time" content="{post['date']}">

<link rel="icon" href="{FAVICON}">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{html.escape(post['title'])}",
  "description": "{html.escape(post['summary'])}",
  "datePublished": "{post['date']}",
  "author": {{ "@type": "Person", "name": "Sebastián Allende Cuello", "url": "{SITE}/" }},
  "inLanguage": "{lang}"
}}
</script>

<link rel="alternate" type="application/rss+xml" title="Sebastián Allende — Writing" href="/feed.xml">
<link rel="stylesheet" href="{depth}style.css">
</head>
<body>

{lang_nav}{TOGGLE.format(lbl=t['themelabel'])}

<a class="skip" href="#main">{t['skip']}</a>

<div class="wrap">
  <a class="back" href="../">{t['back']}</a>

  <main id="main">
  <article>

    <h1>{html.escape(post['title'])}</h1>
    <p class="meta">{meta_line}</p>

{body}
{next_up}
  </article>
  </main>

  <footer>
    <span><a href="../">{t['backfoot']}</a></span>
    <span>sallendec@outlook.com</span>
  </footer>
</div>
{SCRIPTS.replace('%SECTIONS%', t['sections'])}
</body>
</html>
"""
    dest = out_root / prefix / f"{slug}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc)
    return dest


def render_index(posts, lang, out_root):
    t = T[lang]
    prefix = "es/writing" if lang == "es" else "writing"
    depth = "../../" if lang == "es" else "../"
    mine = sorted([p for p in posts if p["lang"] == lang], key=lambda p: p["date"], reverse=True)

    items = "\n".join(f"""    <a class="post" href="./{p['slug']}.html">
      <div class="when"><time datetime="{p['date']}">{human_date(p['date'], lang)}</time> · {p['minutes']} {t['read']}</div>
      <h3>{html.escape(p['title'])}</h3>
      <p>{html.escape(p['summary'])}</p>
    </a>""" for p in mine)

    other = "es" if lang == "en" else "en"
    other_href = "../es/writing/" if lang == "en" else "../../writing/"
    lang_nav = (f'<nav class="lang-switch" aria-label="{t["langlabel"]}">\n'
                f'  <a href="{"./" if lang == "en" else "../../writing/"}" hreflang="en"'
                f'{" aria-current=\"true\"" if lang == "en" else ""}>EN</a>\n'
                f'  <a href="{"../es/writing/" if lang == "en" else "./"}" hreflang="es"'
                f'{" aria-current=\"true\"" if lang == "es" else ""}>ES</a>\n'
                f'</nav>')

    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
{NOFLASH}

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{t['writing']} — Sebastián Allende</title>
<meta name="description" content="{t['tagline']}.">
<link rel="canonical" href="{SITE}/{prefix}/">
<link rel="alternate" hreflang="en" href="{SITE}/writing/">
<link rel="alternate" hreflang="es" href="{SITE}/es/writing/">

<meta property="og:type" content="website">
<meta property="og:title" content="{t['writing']} — Sebastián Allende">
<meta property="og:description" content="{t['tagline']}.">
<meta property="og:url" content="{SITE}/{prefix}/">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="{FAVICON}">
<link rel="alternate" type="application/rss+xml" title="Sebastián Allende — Writing" href="/feed.xml">
<link rel="stylesheet" href="{depth}style.css">
</head>
<body>

{lang_nav}

{TOGGLE.format(lbl=t['themelabel'])}

<a class="skip" href="#main">{t['skip']}</a>

<div class="wrap">
  <a class="back" href="../">{t['back']}</a>

  <main id="main">
    <h1>{t['writing']}</h1>
    <p class="meta">{t['tagline']}</p>

{items}
  </main>

  <footer>
    <span><a href="../">{t['backfoot']}</a></span>
    <span>sallendec@outlook.com</span>
  </footer>
</div>
{SCRIPTS.replace('%SECTIONS%', t['sections'])}
</body>
</html>
"""
    dest = out_root / prefix / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc)
    return dest


def render_feed(posts, out_root):
    en = sorted([p for p in posts if p["lang"] == "en"], key=lambda p: p["date"], reverse=True)
    items = "\n".join(f"""    <item>
      <title>{html.escape(p['title'])}</title>
      <link>{SITE}/writing/{p['slug']}.html</link>
      <guid isPermaLink="true">{SITE}/writing/{p['slug']}.html</guid>
      <pubDate>{rfc_date(p['date'])}</pubDate>
      <description>{html.escape(p['summary'])}</description>
    </item>""" for p in en)
    (out_root / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Sebastián Allende — Writing</title>
    <link>{SITE}/writing/</link>
    <description>Notes on running ERP and financial systems in production.</description>
    <language>en</language>
    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
{items}
  </channel>
</rss>
""")


def render_sitemap(posts, out_root):
    urls = [f"""  <url>
    <loc>{SITE}/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/"/>
    <xhtml:link rel="alternate" hreflang="es" href="{SITE}/es/"/>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{SITE}/es/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/"/>
    <xhtml:link rel="alternate" hreflang="es" href="{SITE}/es/"/>
    <priority>1.0</priority>
  </url>
  <url><loc>{SITE}/writing/</loc><priority>0.8</priority></url>
  <url><loc>{SITE}/es/writing/</loc><priority>0.8</priority></url>"""]
    for p in sorted(posts, key=lambda p: (p["date"], p["lang"]), reverse=True):
        pre = "es/writing" if p["lang"] == "es" else "writing"
        urls.append(f'  <url><loc>{SITE}/{pre}/{p["slug"]}.html</loc><priority>0.8</priority></url>')
    (out_root / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n")


def build(out_root):
    posts = [parse_post(p) for p in sorted(POSTS.glob("*.md"))]
    if not posts:
        sys.exit(f"ERROR: no posts found in {POSTS}")
    written = []
    for p in posts:
        written.append(render_post(p, posts, out_root))
    for lang in ("en", "es"):
        if any(p["lang"] == lang for p in posts):
            written.append(render_index(posts, lang, out_root))
    render_feed(posts, out_root)
    render_sitemap(posts, out_root)
    return posts, written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="build into a temp dir and report differences without writing")
    args = ap.parse_args()

    if args.check:
        tmp = pathlib.Path(tempfile.mkdtemp())
        for f in ("style.css",):
            if (ROOT / f).exists():
                shutil.copy(ROOT / f, tmp / f)
        posts, written = build(tmp)
        print(f"{len(posts)} posts → {len(written)} pages (dry run in {tmp})")
        diffs = 0
        for w in written:
            rel = w.relative_to(tmp)
            cur = ROOT / rel
            if not cur.exists():
                print(f"  NEW      {rel}"); diffs += 1
            elif cur.read_text() != w.read_text():
                print(f"  CHANGED  {rel}"); diffs += 1
        print("no changes" if not diffs else f"{diffs} file(s) would change")
        return

    posts, written = build(ROOT)
    by_lang = {}
    for p in posts:
        by_lang[p["lang"]] = by_lang.get(p["lang"], 0) + 1
    print(f"Built {len(posts)} posts " +
          " · ".join(f"{v} {k.upper()}" for k, v in sorted(by_lang.items())))
    for w in written:
        print(f"  {w.relative_to(ROOT)}")
    print("  feed.xml\n  sitemap.xml")


if __name__ == "__main__":
    main()
