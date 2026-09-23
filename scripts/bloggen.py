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
    text = "\n".join(lines[body_start:])
    m = re.match(r"^\s*#\s+.+\n+", text)
    if m:
        text = text[m.end():]
    return meta, text


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
        "Blog", "blog/index.html",
        f'''<section class="wrap page-head"><h1>SROTrac Weekly</h1>
        <p>What changed in India's SRO-land this week — roster moves, consultations,
        enforcement, recognition news. Generated from the tracker's own diffs plus
        source monitoring.</p></section>
        <section class="wrap grid-posts">{items}</section>''',
    ), encoding="utf-8")

    for p in posts:
        (out_dir / f'{p["slug"]}.html').write_text(page(
            f'{p["title"]}', "blog/index.html",
            f'''<section class="wrap"><article class="post-full"><div class="date">{fmt_date(p["date"])}</div>
            <h1>{esc(p["title"])}</h1>
            {p["html"]}</article>
            <p><a href="/blog/index.html">&larr; All posts</a></p></section>''',
        ), encoding="utf-8")
    return len(posts)


def main():
    n = build()
    print(f"blog: wrote index + {n} post page(s)")


if __name__ == "__main__":
    main()
