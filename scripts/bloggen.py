#!/usr/bin/env python3
"""Generate blog/index.html + blog/<slug>.html from blog/posts/*.md (front-matter: title, date, summary).

Standalone step after site.py; imports its page/CSS helpers.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("srotrac_site", _HERE / "site.py")
_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_site)
import os
page, ROOT, esc, fmt_date = _site.page, _site.ROOT, _site.esc, _site.fmt_date


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
    return meta, "\n".join(lines[body_start:])


def build():
    posts_dir = Path(ROOT) / "blog" / "posts"
    out_dir = Path(ROOT) / "blog"
    out_dir.mkdir(parents=True, exist_ok=True)
    posts = []
    for md in sorted(posts_dir.glob("*.md")):
        meta, text = parse_post(md)
        posts.append({
            "slug": md.stem,
            "title": meta.get("title", md.stem),
            "date": meta.get("date", ""),
            "summary": meta.get("summary", ""),
            "html": md_to_html(text),
        })
    posts.sort(key=lambda x: x["date"], reverse=True)

    items = ""
    for p in posts:
        items += (
            f'<article class="post-card"><div class="date">{fmt_date(p["date"])}</div>'
            f'<h3><a href="/blog/{p["slug"]}.html">{esc(p["title"])}</a></h3>'
            f'<p>{esc(p["summary"])}</p></article>'
        )
    if not items:
        items = '<p class="muted">No posts yet.</p>'

    (out_dir / "index.html").write_text(page(
        "Blog — SROTrac", "blog/index.html",
        f'''<section class="page-head"><h1>SROTrac Weekly</h1>
        <p>What changed in India's SRO-land this week — roster moves, consultations,
        enforcement, recognition news. Generated from the tracker's own diffs plus
        source monitoring.</p></section>
        <section class="grid-posts">{items}</section>''',
    ), encoding="utf-8")

    for p in posts:
        (out_dir / f'{p["slug"]}.html').write_text(page(
            f'{p["title"]} — SROTrac', "blog/index.html",
            f'''<article class="post-full"><div class="date">{fmt_date(p["date"])}</div>
            <h1>{esc(p["title"])}</h1>
            {p["html"]}</article>
            <p><a href="/blog/index.html">&larr; All posts</a></p>''',
        ), encoding="utf-8")
    return len(posts)


BLOG_CSS = """
.grid-posts{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:20px}
.post-card{background:#fff;border:1px solid #e7e2d8;border-radius:10px;padding:16px 18px}
.post-card .date{font-size:.8rem;color:#8a8375;margin-bottom:6px}
.post-card h3{margin:0 0 6px;font-size:1.02rem}
.post-card a{color:var(--ink);text-decoration:none}
.post-card a:hover{color:var(--accent)}
.post-card p{margin:0;color:#57534e;font-size:.9rem}
.post-full{max-width:780px;margin:0 auto;background:#fff;border:1px solid #e7e2d8;border-radius:10px;padding:32px 36px}
.post-full .date{font-size:.85rem;color:#8a8375;margin-bottom:10px}
.post-full h1{margin:0 0 18px;font-size:1.7rem}
.post-full h2{margin:26px 0 10px;font-size:1.2rem}
.post-full table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.88rem}
.post-full th,.post-full td{border:1px solid #e7e2d8;padding:6px 9px;text-align:left}
.post-full th{background:#f6f3ec}
.post-full blockquote{border-left:3px solid var(--accent);margin:12px 0;padding:4px 14px;color:#57534e;background:#f8f6f1}
.post-full code{background:#f3efe6;padding:1px 5px;border-radius:4px;font-size:.86em}
"""


def main():
    n = build()
    # append blog styles once
    css_path = Path(ROOT) / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    if ".grid-posts" not in css:
        css_path.write_text(css + "\n" + BLOG_CSS, encoding="utf-8")
    print(f"blog: wrote index + {n} post page(s)")


if __name__ == "__main__":
    main()
