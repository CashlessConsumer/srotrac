#!/usr/bin/env python3
"""Social-presence drift check for SROTrac.

For every account in data/social.csv whose source is 'official site',
verify the handle still appears in the latest raw snapshots under data/raw/.
Writes data/social_check.json; site.py renders the result on social.html.

Platform walls (X, LinkedIn, Facebook, Instagram) block automated fetches,
so this checks the *other* direction: does the SRO's own website still link
the account? A handle removed from the official site is the cheapest early
signal of a rebrand, a takeover, or an account quietly deleted.

Usage: python3 scripts/social_check.py
"""
import csv
import glob
import html as htmllib
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load_raw_text():
    """Concatenate all raw snapshots, normalising HTML-entity slashes and casing."""
    chunks = []
    for path in glob.glob(os.path.join(DATA, "raw", "*.html")):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                chunks.append(f.read())
        except OSError:
            continue
    text = "\n".join(chunks)
    text = htmllib.unescape(text)          # &#x2F; and friends -> /
    text = re.sub(r"https?://(www\.)?", "", text)
    return text.lower()


def probe_for(url):
    """Candidate substrings; twitter.com and x.com are equivalent."""
    p = re.sub(r"^https?://(www\.)?", "", url.strip()).rstrip("/").lower()
    cands = [p]
    if p.startswith("x.com/"):
        cands.append("twitter.com/" + p[6:])
    elif p.startswith("twitter.com/"):
        cands.append("x.com/" + p[12:])
    if p.startswith("youtube.com/channel/"):
        cands.append(p.rsplit("/", 1)[-1])
    return cands


def main():
    with open(os.path.join(DATA, "social.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    corpus = load_raw_text()

    checked, present, missing = 0, 0, []
    for r in rows:
        if r["source"] != "official site":
            continue
        checked += 1
        if any(c in corpus for c in probe_for(r["url"])):
            present += 1
        else:
            missing.append(f'{r["sro"]}:{r["platform"]}:{r["handle"]}')

    out = {
        "checked": date.today().isoformat(),
        "official_site_accounts": checked,
        "still_linked": present,
        "missing_from_site": missing,
    }
    with open(os.path.join(DATA, "social_check.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"social check {out['checked']}: {present}/{checked} official-site links still present"
          + (f" — MISSING: {', '.join(missing)}" if missing else ""))


if __name__ == "__main__":
    main()
