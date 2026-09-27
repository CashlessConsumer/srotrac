#!/usr/bin/env python3
"""Generate the SROTrac blog layer from blog/posts/*.md.

Front matter: title, date, summary, category (optional — defaults to `note`;
taxonomy: roster · enforcement · consultation · recognition · weekly · note).

Outputs (blog/):
  index.html      latest 12 editions + year nav + archive link
  archive.html    full corpus grouped year -> month, category chips
  <year>.html     per-year page, month anchors, category chips
  feed.xml        RSS 2.0 (latest 20)
  <slug>.html     post pages
Also patches sitemap.xml with any missing blog URLs (archive/years included),
so build order (build.py -> site.py -> bloggen.py) never leaves gaps.
"""
import calendar
import importlib.util
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("srotrac_site", _HERE / "site.py")
_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_site)
import os
page, ROOT, esc, fmt_date = _site.page, _site.ROOT, _site.esc, _site.fmt_date

SITE = "https://srotrac.cashlessconsumer.in"
BLOG_TITLE = "SROTrac Weekly"
FEED_TITLE = "SROTrac Weekly"
FEED_DESC = "Weekly editions from the SRO register: rosters, recognition moves, consultations and enforcement signals across India's financial-sector SROs."
DEFAULT_CATEGORY = "note"
CATEGORIES = ["roster", "enforcement", "consultation", "recognition", "weekly", "note"]


def md_to_html(md_text):
    try:
        r = subprocess.run(
            ["pandoc", "-f", "gfm", "-t", "html"], input=md_text,
            capture_output=True, text=True, check=True, timeout=60,
        )
        return r.stdout
    except Exception:
        return "<pre>" + esc(md_text) + "</pre>"


def parse_post(md_path):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    meta, body_start = {}, 0
    if lines and lines[0].strip() == "---":
        for i, ln in enumerate(lines[1:], start=1):
            if ln.strip() == "---":
                body_start = i + 1
                break
            m = re.match(r"^(\w+):\s*(.+)$", ln.strip())
            if m:
                meta[m.group(1).lower()] = m.group(2).strip().strip('"')
    text = "\n".join(lines[body_start:])
    m = re.match(r"^\s*#\s+.+\n+", text)
    if m:
        text = text[m.end():]
    return meta, text


ARCHIVE_CSS = """<style>
.achips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 4px}
.achip{font:inherit;font-size:.8rem;border:1px solid #d6d3d1;border-radius:20px;padding:3px 12px;color:inherit;text-decoration:none;cursor:pointer;background:transparent}
.achip[aria-pressed="true"]{background:#1d4ed8;color:#fff;border-color:#1d4ed8}
.arch-year{font-size:1.25rem;margin:30px 0 6px;border-bottom:2px solid #1d4ed8;padding-bottom:6px}
.arch-year a{color:inherit;text-decoration:none}
.arch-count{color:#71717a;font-weight:400;font-size:.85rem}
.arch-month{font-variant:small-caps;letter-spacing:.05em;color:#52525b;margin:18px 0 8px;font-size:1.05rem}
.post-card .pcat{color:#1d4ed8;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em}
.post-card.hide{display:none}
.archnav{margin:10px 0 0}
</style>
<script>
document.addEventListener('click',function(e){
  var b=e.target.closest('.achip');if(!b||!b.dataset.cat&&b.dataset.cat!=='')return;
  if(!e.currentTarget||!e.target.closest('#achips'))return;
  var wrap=b.closest('#achips');
  var on=b.getAttribute('aria-pressed')==='true';
  wrap.querySelectorAll('.achip').forEach(function(x){x.setAttribute('aria-pressed','false')});
  if(!on)b.setAttribute('aria-pressed','true');
  var cat=on?null:b.dataset.cat;
  document.querySelectorAll('[data-pcat]').forEach(function(c){
    c.classList.toggle('hide',cat!==null&&c.dataset.pcat!==cat);
  });
});
</script>"""


def card(p):
    return (f'<article class="post-card" data-pcat="{esc(p["category"])}">'
            f'<div class="date">{fmt_date(p["date"])} · <span class="pcat">{esc(p["category"])}</span></div>'
            f'<h3><a href="/blog/{p["slug"]}.html">{esc(p["title"])}</a></h3>'
            f'<p>{esc(p["summary"])}</p></article>')


def chips(cats, active=""):
    out = f'<button class="achip" data-cat="" aria-pressed="{"true" if not active else "false"}">All</button>'
    for c in cats:
        out += (f'<button class="achip" data-cat="{esc(c)}" '
                f'aria-pressed="{"true" if c == active else "false"}">{esc(c)}</button>')
    return out


def group_months(year_posts):
    months = {}
    for p in year_posts:
        months.setdefault(p["date"][5:7], []).append(p)
    return [(m, months[m]) for m in sorted(months, reverse=True)]


def year_sections(posts, link_years=True):
    sections = ""
    for y in sorted({p["date"][:4] for p in posts}, reverse=True):
        yp = [p for p in posts if p["date"][:4] == y]
        head = f'<a href="{y}.html">{y}</a>' if link_years else y
        sections += (f'<h2 class="arch-year">{head} '
                     f'<span class="arch-count">· {len(yp)} post{"s" if len(yp) != 1 else ""}</span></h2>')
        for m, mp in group_months(yp):
            sections += (f'<h3 class="arch-month">{calendar.month_name[int(m)]} {y}</h3>'
                         f'<div class="grid-posts">{"".join(card(p) for p in mp)}</div>')
    return sections


def archive_page(posts, cats, year=None):
    shown = [p for p in posts if not year or p["date"][:4] == year]
    title = f"{BLOG_TITLE} — Archive {year}" if year else f"{BLOG_TITLE} — Archive"
    ynav = " ".join(f'<a class="achip" href="{y}.html">{y}</a>'
                    for y in sorted({p["date"][:4] for p in posts}, reverse=True))
    body = f'''<section class="wrap page-head"><h1>{esc(title)}</h1>
    <p>Every edition since launch, grouped by month. {len(shown)} post{"s" if len(shown) != 1 else ""}{f" in {year}" if year else ""}.</p>
    <div class="achips" id="achips">{chips(cats)}</div>
    <p class="archnav">Years: {ynav} · <a href="index.html">Latest</a></p></section>
    <section class="wrap">{year_sections(shown, link_years=not year)}</section>'''
    return page(title, "blog/index.html", body, extra_head=ARCHIVE_CSS)


def index_page(posts):
    latest = posts[:12]
    items = "".join(card(p) for p in latest)
    years = sorted({p["date"][:4] for p in posts}, reverse=True)
    ynav = " ".join(f'<a class="achip" href="{y}.html">{y}</a>' for y in years)
    body = f'''<section class="wrap page-head"><h1>{BLOG_TITLE}</h1>
    <p>What moved in India's SRO layer this week — roster changes, new recognitions,
    consultations that touch member conduct, enforcement signals. Generated from the
    register's own diffs plus source monitoring.</p>
    <p class="archnav">Editions: {ynav} · <a class="achip" href="archive.html">Full archive</a></p></section>
    <section class="wrap grid-posts">{items}</section>'''
    return page(BLOG_TITLE, "blog/index.html", body, extra_head=ARCHIVE_CSS)


def rss(posts):
    items = ""
    for p in posts[:20]:
        link = f"{SITE}/blog/{p['slug']}.html"
        try:
            pub = datetime.strptime(p["date"][:10], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")
        except ValueError:
            pub = ""
        items += (f'\n  <item>\n    <title>{esc(p["title"])}</title>\n    <link>{link}</link>\n'
                  f'    <guid isPermaLink="true">{link}</guid>\n    <pubDate>{pub}</pubDate>\n'
                  f'    <category>{esc(p["category"])}</category>\n'
                  f'    <description>{esc(p["summary"])}</description>\n  </item>')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>{FEED_TITLE}</title>
  <link>{SITE}/blog/</link>
  <description>{FEED_DESC}</description>
  <language>en-in</language>
  <lastBuildDate>{datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>{items}
</channel></rss>
'''


def patch_sitemap(extra_paths):
    sm = Path(ROOT) / "sitemap.xml"
    if not sm.exists():
        return
    txt = sm.read_text(encoding="utf-8")
    add = ""
    for p in extra_paths:
        loc = f"<loc>{SITE}/{p}</loc>"
        if loc not in txt:
            add += f'<url>{loc}<changefreq>monthly</changefreq><priority>0.5</priority></url>'
    if add and "</urlset>" in txt:
        sm.write_text(txt.replace("</urlset>", add + "</urlset>"), encoding="utf-8")


def build():
    posts_dir = Path(ROOT) / "blog" / "posts"
    out_dir = Path(ROOT) / "blog"
    out_dir.mkdir(parents=True, exist_ok=True)
    posts = []
    for md in sorted(posts_dir.glob("*.md")):
        meta, text = parse_post(md)
        cat = meta.get("category", DEFAULT_CATEGORY).strip().lower()
        if cat not in CATEGORIES:
            cat = DEFAULT_CATEGORY
        posts.append({
            "slug": md.stem,
            "title": meta.get("title", md.stem),
            "date": meta.get("date", ""),
            "summary": meta.get("summary", ""),
            "category": cat,
            "html": md_to_html(text),
        })
    posts.sort(key=lambda x: x["date"], reverse=True)
    cats = sorted({p["category"] for p in posts})
    years = sorted({p["date"][:4] for p in posts}, reverse=True)

    (out_dir / "index.html").write_text(index_page(posts), encoding="utf-8")
    (out_dir / "archive.html").write_text(archive_page(posts, cats), encoding="utf-8")
    for y in years:
        (out_dir / f"{y}.html").write_text(archive_page(posts, cats, year=y), encoding="utf-8")
    (out_dir / "feed.xml").write_text(rss(posts), encoding="utf-8")

    for p in posts:
        (out_dir / f'{p["slug"]}.html').write_text(page(
            f'{p["title"]}', "blog/index.html",
            f'''<section class="wrap"><article class="post-full"><div class="date">{fmt_date(p["date"])} · <span class="pcat">{esc(p["category"])}</span></div>
            <h1>{esc(p["title"])}</h1>
            {p["html"]}</article>
            <p><a href="/blog/index.html">&larr; All posts</a> · <a href="/blog/archive.html">Archive</a></p></section>''',
        ), encoding="utf-8")

    patch_sitemap(["blog/archive.html"] + [f"blog/{y}.html" for y in years] + ["blog/feed.xml"])
    return len(posts), len(years)


def main():
    n, y = build()
    print(f"blog: wrote index(capped) + archive + {y} year page(s) + feed.xml + {n} post page(s)")


if __name__ == "__main__":
    main()
