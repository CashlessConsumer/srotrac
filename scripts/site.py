#!/usr/bin/env python3
"""Generate the SROTrac static site (srotrac.cashlessconsumer.in).

Reads data/*.csv produced by build.py (or curated by hand) and emits static
HTML pages at the project root, following the cyber.cashlessconsumer.in
pattern (plain HTML/CSS/JS, GitHub Pages).

Usage: python3 scripts/site.py
"""
import csv
import html
import json
import os
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

SROS = {
    "face": {
        "abbr": "FACE", "name": "Fintech Association for Consumer Empowerment",
        "sector": "Fintech / digital lending",
        "order": "1st", "recognised": "2024-08-28",
        "website": "https://faceofindia.org",
        "members_site": "https://faceofindia.org/membership/",
        "hq": "INNOV8, Peninsula Business Park, Lower Parel, Mumbai 400013",
        "cin": "U91990MH2020NPL346315",
        "status": "Active SRO-FT",
        "accent": "#7c2d3a",
        "consumer": [
            "Runs the <strong>DLA Validator</strong> — check a lending app before you borrow from it.",
            "Publishes a <strong>Grievance &amp; Dispute Resolution</strong> (GDR) framework and an Oversight &amp; Enforcement policy for members.",
            "Studies personal-loan pricing and borrower outcomes (Personal Loan Report 2026) and pushed Google on predatory lending apps.",
        ],
        "watch": [
            "Member count claims (~200+) vs published roster (~85 logos) — the public list is a marketing page, not a register.",
            "Enforcement actions are not published; the SRO-FT framework expects oversight of member conduct.",
        ],
    },
    "uff": {
        "abbr": "UFF", "name": "Unified Fintech Forum",
        "sector": "Fintech (broad): lenders, wallets/PPIs, neobanks, BNPL",
        "order": "2nd", "recognised": "2026-09-10",
        "website": "https://unifiedfintech.in",
        "members_site": "https://unifiedfintech.in/members-network/",
        "hq": "Mumbai (rebranded from Digital Lenders Association of India, Apr 2025)",
        "cin": "",
        "status": "Active SRO-FT (recognised at GFF 2026)",
        "accent": "#1f3a5f",
        "consumer": [
            "Second RBI-recognised fintech SRO — now both major fintech lobbies are under RBI's SRO-FT rules: codes of conduct, member monitoring, grievance redress.",
            "Has a dedicated <strong>SRO portfolio</strong> in its Executive Committee (Chair: Progcap; Co-chair: Vivifi) — the desk expected to police members.",
            "Independent board stacked with ex-regulators: two former RBI Deputy Governor/ED-level officials, ex-CMD of SIDBI, ex-SBI Deputy MD.",
        ],
        "watch": [
            "Freshly recognised — codes of conduct and enforcement machinery are yet to be tested in public.",
            "Track whether UFF publishes member-discipline actions, unlike FACE's unpublished enforcement record.",
        ],
    },
    "fidc": {
        "abbr": "FIDC", "name": "Finance Industry Development Council",
        "sector": "NBFCs (incl. digital lenders) — recognised under omnibus framework, not the SRO-FT framework",
        "order": "—", "recognised": "2025-10-03",
        "website": "https://www.fidcindia.org.in",
        "members_site": "https://www.fidcindia.org.in/membership-details/",
        "hq": "Mumbai",
        "cin": "",
        "status": "Active SRO (NBFC)",
        "accent": "#6e4a1f",
        "consumer": [
            "Self-regulates the NBFC industry — the sector behind most vehicle, gold, MSME and many personal loans.",
            "Monitors fair-practices-code compliance and recovery-agent conduct across member NBFCs.",
        ],
        "watch": [
            "<strong>No public member roster.</strong> Claims ~400 members in press material but publishes no list — a transparency gap this tracker flags.",
            "The 'List of NBFCs' page on its site contains RBI registration statistics, not its own membership.",
        ],
    },
    "srpa": {
        "abbr": "SRPA", "name": "Self-Regulated PSO Association",
        "sector": "Payment system operators: payment aggregators, wallets/PPIs, POS",
        "order": "1st", "recognised": "2025-11-11",
        "website": "https://srpa.org.in",
        "members_site": "https://srpa.org.in/",
        "hq": "Siddharth, 11th Floor, Tilak Road, Santacruz West, Mumbai 400054",
        "cin": "",
        "status": "Active SRO (PSO)",
        "accent": "#55612c",
        "consumer": [
            "Founded by the people who run India's payment rails at the merchant end: CCAvenue's Vishwas Patel and BillDesk's M N Srinivasu.",
            "Expected to police member PSOs on settlement reliability, outage handling, merchant onboarding fraud and RBI payment-circular compliance.",
        ],
        "watch": [
            "Website is skeletal ('more details coming soon') — no code of conduct, grievance process or member list published yet.",
            "18 members vs ~30+ licensed payment aggregators: check who is and isn't covered.",
        ],
    },
    "mfin": {
        "abbr": "MFIN", "name": "Microfinance Institutions Network",
        "sector": "NBFC-MFIs (+ banks/SFBs lending microfinance as associate members)",
        "order": "1st", "recognised": "2014-06-16",
        "website": "https://mfinindia.org",
        "members_site": "https://mfinindia.org/members",
        "hq": "New Delhi / Mumbai",
        "cin": "",
        "status": "Active SRO (microfinance; RBI letter 16 Jun 2014 — first SRO in this family)",
        "accent": "#2f5d5a",
        "consumer": [
            "India's oldest RBI-recognised SRO in this set — created after the 2010 Andhra Pradesh microfinance crisis on the Malegam committee's recommendation.",
            "Runs a code of conduct with field-level monitoring and its own dispute-resolution machinery for micro-borrower complaints.",
            "84 member institutions listed on its member wall, from Fusion, Asirvad and CreditAccess Grameen to bank lenders like Axis, HDFC and ICICI.",
        ],
        "watch": [
            "Roster is a logo wall organised by region — no join/exit dates published.",
            "Site text says 53 primary members (Mar 2025) but the logo wall shows 84 organisations — the extra tiles are likely associates; MFIN does not label them.",
            "Microfinance distress and RBI tightening make MFIN's enforcement record the one to watch for borrower-side harm.",
        ],
    },
    "sadhan": {
        "abbr": "Sa-Dhan", "name": "Sa-Dhan (Association of Community Development Finance Institutions)",
        "sector": "Microfinance (broad network: MFIs, SFBs, banks, investors)",
        "order": "2nd", "recognised": "2015-03-11",
        "website": "https://www.sa-dhan.net",
        "members_site": "https://www.sa-dhan.net/what-we-do/sro/",
        "hq": "New Delhi",
        "cin": "",
        "status": "Active SRO (microfinance; recognised Mar 2015)",
        "accent": "#4b3a70",
        "consumer": [
            "Second microfinance SRO — RBI recognition gave NBFC-MFIs a choice between MFIN and Sa-Dhan.",
            "Publishes the Bharat Microfinance Report, the sector's main data benchmark.",
            "Claims 200+ member institutions but publishes no public member directory — roster visibility is a gap this tracker flags.",
        ],
        "watch": [
            "No public member list; membership data only via its report/portal.",
            "Watch its stricter member norms (2024) translate into visible discipline actions.",
        ],
    },
    "fedai": {
        "abbr": "FEDAI", "name": "Foreign Exchange Dealers' Association of India",
        "sector": "Authorised Dealers in foreign exchange (banks + FEMA-authorised entities)",
        "order": "—", "recognised": "2026-01-14",
        "website": "https://www.fedai.org.in",
        "members_site": "https://www.fedai.org.in/InnerPageContent.aspx?Cid=2&SCid=1&SSCid=0",
        "hq": "Mumbai (est. 1958, Section 25 company)",
        "cin": "",
        "status": "Active SRO (FX; Omnibus framework; 1-yr transition to Jan 2027)",
        "accent": "#8f4a26",
        "consumer": [
            "The newest RBI-recognised SRO (Jan 2026) — formalises six decades of self-set forex rules for banks dealing in foreign exchange.",
            "108 member authorised dealers listed with LEI numbers — the cleanest public roster of any SRO tracked here.",
            "For customers: FEDAI rules govern how banks quote, convert and disclose FX charges on your inward/outward remittances and card spends abroad.",
        ],
        "watch": [
            "Has until Jan 2027 to align governance with the Omnibus SRO framework and extend membership to all AD categories.",
            "Website is a legacy frameset — public disclosure quality lags its new regulatory status.",
        ],
    },
}


def esc(s):
    return html.escape(str(s or ""))


def read_csv(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmt_date(d):
    try:
        dt = date.fromisoformat(d)
        return dt.strftime("%d %b %Y")
    except Exception:
        return d


NAV = [
    ("", "Home"),
    ("members.html", "Members"),
    ("overlap.html", "Overlap"),
    ("timeline.html", "Timeline"),
    ("activity.html", "Activity"),
    ("blog/index.html", "Blog"),
    ("about.html", "About"),
]


def page(title, active, body, extra_head=""):
    # SRO dropdown: single menu holding the register
    is_sro = active.startswith("sro-")
    sro_rows = ""
    for sid, s in SROS.items():
        row_cls = ' class="active"' if active == f"sro-{sid}.html" else ""
        sro_rows += (f'<a href="/sro-{sid}.html"{row_cls}>'
                     f'<span class="dd-abbr" style="--c:{s["accent"]}">{s["abbr"]}</span>'
                     f'<span class="dd-name">{esc(s["name"])}</span></a>')
    trig_cls = ' class="trigger active"' if is_sro else ' class="trigger"'
    drop = (f'<div class="nav-drop"><a{trig_cls} href="/#register">'
            f'SROs <span class="caret">▾</span></a>'
            f'<div class="dd-panel">{sro_rows}</div></div>')
    nav = ""
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        nav += f'<a href="/{href}"{cls}>{label}</a>'
        if href == "":
            nav += drop
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — SROTrac</title>
<meta name="description" content="Independent tracker of India's RBI-recognised self-regulatory organisations in fintech, NBFC and payments: members, governance, activity, and what they mean for consumers.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="/css/style.css">
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="mast-top"><div class="wrap">
    <span>A CashlessConsumer Register</span><span>Open data · CC BY 4.0</span>
  </div></div>
  <div class="wrap mast-main">
    <a class="brand" href="/">SRO<span>Trac</span></a>
    <p class="mast-sub">India&rsquo;s self-regulatory organisations, watched</p>
    <nav>{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p><strong>SROTrac</strong> — an independent CashlessConsumer project tracking India's self-regulatory organisations. Not affiliated with RBI or any SRO.</p>
    <p><a href="https://cashlessconsumer.in">cashlessconsumer.in</a> · data: <a href="https://github.com/CashlessConsumer/srotrac">GitHub</a> · <a href="/about.html">methodology</a></p>
    <p class="colophon">Set in Fraunces, Newsreader &amp; IBM Plex Mono · Regenerated nightly from source captures</p>
  </div>
</footer>
<script src="/js/main.js"></script>
</body>
</html>"""

def sid_of(v):
    v = str(v).strip()
    if v.lower() in SROS:
        return v.lower()
    for sid, s in SROS.items():
        if v.upper() == s["abbr"]:
            return sid
    return None


def sro_badge(sro_id):
    sid = sid_of(sro_id)
    if not sid:
        return '<span class="badge" style="--c:#57534e">RBI</span>'
    s = SROS[sid]
    return f'<a class="badge" style="--c:{s["accent"]}" href="/sro-{sid}.html">{s["abbr"]}</a>'


def build_home(members, activity, overlap):
    total = len(members)
    both = sum(1 for o in overlap if len(o["sros"]) > 1)
    srofts = sum(1 for s in SROS.values() if "SRO-FT" in s["status"])
    counts = defaultdict(int)
    for m in members:
        counts[sid_of(m["sro"])] += 1
    recent = activity[:6]
    cards = ""
    for sid, s in SROS.items():
        cards += f"""
    <a class="sro-card" href="/sro-{sid}.html" style="--c:{s['accent']}" data-abbr="{s['abbr']}">
      <div class="sro-card-head"><span class="sro-abbr">{s['abbr']}</span>
      <span class="pill">{esc(s['status'])}</span></div>
      <h3>{esc(s['name'])}</h3>
      <p class="sector">{esc(s['sector'])}</p>
      <p class="meta">Recognised {fmt_date(s['recognised'])} · {counts.get(sid, 0)} listed members</p>
    </a>"""
    items = ""
    for a in recent:
        items += f"""
      <li><span class="date">{a['date']}</span> {sro_badge(a['sro'])}
      <a href="{esc(a['url'])}" rel="noopener">{esc(a['title'])}</a></li>"""
    body = f"""
<section class="hero">
  <div class="wrap">
    <p class="kicker rise">Register of self-regulatory organisations · India</p>
    <h1 class="rise">Who watches India&rsquo;s fintech <em>watchdogs</em>?</h1>
    <div class="hero-stamps">
      <span class="stamp seal-in">RBI-Recognised × {len(SROS)}</span>
      <span class="stamp blue seal-in" style="animation-delay:.45s">{srofts} × SRO-FT</span>
    </div>
    <p class="lede rise">RBI outsources first-line supervision of fintechs, NBFCs and payment operators to <strong>self-regulatory organisations</strong> — industry bodies with the power to write conduct codes and police their own members. SROTrac tracks who sits on these SROs, what they do, and whether they work for consumers.</p>
    <div class="stats rise">
      <div><strong>{len(SROS)}</strong><span>RBI-recognised SROs</span></div>
      <div><strong>{total}</strong><span>listed member orgs</span></div>
      <div><strong>{both}</strong><span>in 2+ SROs</span></div>
      <div><strong>{srofts}</strong><span>fintech SRO-FTs</span></div>
    </div>
  </div>
</section>
<section class="wrap" id="register">
  <h2>The register</h2>
  <p class="muted small">Seven bodies, one contract with the regulator. Click a folder for members, governance and activity.</p>
  <div class="sro-grid">{cards}
  </div>
</section>
<section class="wrap">
  <div class="callout">
    <p class="kicker">Consumer notice</p>
    <h2>What is an SRO, in plain words?</h2>
    <p>RBI can't directly supervise thousands of fintechs, NBFCs and payment companies. So it recognises industry associations as <em>self-regulatory organisations</em> — with a contract: broad membership, independent boards, codes of conduct, monitoring of member compliance, and grievance redress. In return the regulator gets a first line of supervision, and the industry gets a single voice.</p>
    <p>For consumers, the SRO is one more place to escalate when a lender or payment company misbehaves — but only if the SRO actually enforces. That is what this tracker watches: rosters, governance, consultations, enforcement, and the gaps in between.</p>
  </div>
</section>
<section class="wrap">
  <h2>Latest activity</h2>
  <ul class="feed">{items}
  </ul>
  <p><a class="btn" href="/activity.html">Full activity log →</a></p>
</section>
<section class="wrap">
  <div class="notice">
    <p class="kicker">Weekly gazette</p>
    <h2>SROTrac Weekly</h2>
    <p>A weekly digest of what moved in SRO-land — roster changes, consultations,
    enforcement, recognition news — generated from the tracker's own diffs.</p>
    <p><a class="btn" href="/blog/index.html">Read the blog →</a></p>
  </div>
</section>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Dataset","name":"SROTrac","description":"Members, governance and activity of RBI-recognised self-regulatory organisations in India (FACE, UFF, FIDC, SRPA, MFIN, Sa-Dhan, FEDAI)","url":"https://srotrac.cashlessconsumer.in/","creator":{{"@type":"Organization","name":"CashlessConsumer","url":"https://cashlessconsumer.in"}},"license":"https://creativecommons.org/licenses/by/4.0/"}}
</script>"""
    return page("India's fintech SROs, tracked", "", body)

def build_sro(sid, members, activity, leadership):
    s = SROS[sid]
    mem = [m for m in members if sid_of(m["sro"]) == sid]
    types = defaultdict(int)
    for m in mem:
        types[m["member_type"] or "member"] += 1
    rows = ""
    for m in sorted(mem, key=lambda x: x["member_name"].lower()):
        t = m["member_type"] or "member"
        rows += f'<tr><td>{esc(m["member_name"])}</td><td><span class="pill small">{esc(t)}</span></td><td class="linkcell"><a href="{esc(m["website"])}" rel="noopener">{esc((m["website"] or "").replace("https://", "").replace("http://", "").rstrip("/"))}</a></td></tr>'
    acts = [a for a in activity if sid_of(a["sro"]) == sid]
    act_html = ""
    for a in acts:
        act_html += f'<li><span class="date">{a["date"]}</span> <span class="pill small">{esc(a["type"])}</span> <a href="{esc(a["url"])}" rel="noopener">{esc(a["title"])}</a></li>'
    cats = [
        ("board", "Board / Governing Council"),
        ("executive", "Executive Committee / Office bearers"),
        ("advisory", "Advisory Council"),
        ("committee", "Board committees"),
    ]
    lead_html = ""
    grouped = defaultdict(list)
    for l in leadership:
        if l["sro"] == s["abbr"]:
            grouped[l["category"]].append(l)
    for cat, label in cats:
        if cat not in grouped:
            continue
        lead_html += f'<h3>{label}</h3><table class="people"><thead><tr><th>Name</th><th>Role</th><th>Affiliation</th></tr></thead><tbody>'
        for l in grouped[cat]:
            lead_html += f'<tr><td>{esc(l["name"])}</td><td>{esc(l["role"])}</td><td>{esc(l["affiliation"])}</td></tr>'
        lead_html += "</tbody></table>"
    consumer_html = "".join(f"<li>{c}</li>" for c in s["consumer"])
    watch_html = "".join(f"<li>{c}</li>" for c in s["watch"])
    typeline = " · ".join(f"{v} {k}" for k, v in sorted(types.items()))
    body = f"""
<section class="sro-hero" style="--c:{s['accent']}">
  <div class="wrap">
    <p class="kicker">RBI-recognised SRO</p>
    <h1>{esc(s['name'])} <span class="abbr-chip">{s['abbr']}</span></h1>
    <p class="lede">{esc(s['sector'])}</p>
    <div class="factbar">
      <div><span>Recognised</span><strong>{fmt_date(s['recognised'])}</strong></div>
      <div><span>Status</span><strong>{esc(s['status'])}</strong></div>
      <div><span>Listed members</span><strong>{len(mem)}</strong> <em class="muted">({esc(typeline)})</em></div>
      <div><span>Site</span><strong><a href="{esc(s['website'])}" rel="noopener">{esc(s['website'].replace('https://', ''))}</a></strong></div>
    </div>
  </div>
</section>
<section class="wrap cols">
  <div class="col">
    <h2>Why it matters if you borrow or pay</h2>
    <ul class="ticks">{consumer_html}</ul>
  </div>
  <div class="col">
    <h2>What we're watching</h2>
    <ul class="watchlist">{watch_html}</ul>
  </div>
</section>
<section class="wrap">
  <h2>Governance</h2>
  {lead_html if lead_html else '<p class="muted">No published governance page.</p>'}
</section>
<section class="wrap">
  <h2>Members ({len(mem)})</h2>
  <table class="listing">
    <thead><tr><th>Organisation</th><th>Type</th><th>Website</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="muted small">Parsed from the SRO's published member page on 2026-09-10. Marketing rosters, not filings — see <a href="/about.html">methodology</a>.</p>
</section>
<section class="wrap">
  <h2>Activity</h2>
  <ul class="feed">{act_html if act_html else '<li>No dated public activity captured yet.</li>'}
  </ul>
</section>"""
    return page(s["abbr"] + " — " + s["name"], f"sro-{sid}.html", body)


def build_members(members):
    accents = {x["abbr"]: x["accent"] for x in SROS.values()}
    payload = [
        {"n": m["member_name"], "s": m["sro"].upper(), "t": m["member_type"] or "member", "w": m["website"],
         "c": accents.get(m["sro"].upper(), "#57534e")}
        for m in sorted(members, key=lambda x: (x["member_name"].lower(), x["sro"]))
    ]
    body = f"""
<section class="hero slim">
  <div class="wrap">
    <h1>All members</h1>
    <p class="lede">{len(members)} rows across FACE, UFF, SRPA, MFIN and FEDAI (FIDC and Sa-Dhan publish no roster). Filter by SRO or search by name.</p>
  </div>
</section>
<section class="wrap">
  <div class="filters">
    <input id="mq" type="search" placeholder="Search organisation…" autocomplete="off">
    <div class="chips" id="chips">
      <button class="chip active" data-f="ALL">All</button>
      <button class="chip" data-f="FACE">FACE</button>
      <button class="chip" data-f="UFF">UFF</button>
      <button class="chip" data-f="SRPA">SRPA</button>
      <button class="chip" data-f="MULTI">In 2+ SROs</button>
    </div>
  </div>
  <p class="muted small" id="mcount"></p>
  <table class="listing" id="mtable">
    <thead><tr><th>Organisation</th><th>SRO</th><th>Type</th><th>Website</th></tr></thead>
    <tbody id="mrows"></tbody>
  </table>
  <noscript><p>Enable JavaScript to browse the interactive table, or grab the raw CSVs on GitHub.</p></noscript>
</section>
<script id="member-data" type="application/json">{json.dumps(payload)}</script>"""
    return page("Members", "members.html", body)


def build_overlap(members, leadership):
    orgs = defaultdict(set)
    for m in members:
        orgs[m["member_name"]].add(m["sro"])
    multi = sorted(((n, sorted(s)) for n, s in orgs.items() if len(s) > 1), key=lambda x: x[0].lower())
    rows = ""
    for n, ss in multi:
        badges = "".join(sro_badge(x.lower()) for x in ss)
        rows += f"<tr><td>{esc(n)}</td><td>{badges}</td></tr>"
    # people overlap: same person in two SROs' leadership
    people = defaultdict(set)
    for l in leadership:
        key = l["name"].lower().replace("mr. ", "").replace("ms. ", "").replace("dr. ", "").strip()
        people[key].add((l["sro"], l["name"], l["role"]))
    prows = ""
    for key, entries in sorted(people.items()):
        sros = {e[0] for e in entries}
        if len(sros) > 1:
            detail = "; ".join(f"{e[0]}: {e[2]}" for e in sorted(entries))
            prows += f"<tr><td>{esc(entries.pop()[1])}</td><td>{esc(detail)}</td></tr>"
    body = f"""
<section class="hero slim">
  <div class="wrap">
    <h1>Cross-SRO overlap</h1>
    <p class="lede">Companies (and people) sitting in more than one self-regulatory organisation. Useful for spotting conflicts of interest and coordinated lobbying.</p>
  </div>
</section>
<section class="wrap">
  <h2>Organisations in 2+ SROs ({len(multi)})</h2>
  <table class="listing"><thead><tr><th>Organisation</th><th>SROs</th></tr></thead><tbody>{rows}</tbody></table>
</section>
<section class="wrap">
  <h2>People in 2+ SROs</h2>
  <table class="listing"><thead><tr><th>Person</th><th>Roles</th></tr></thead><tbody>{prows if prows else '<tr><td colspan="2">None found in published leadership data.</td></tr>'}</tbody></table>
  <div class="callout">
    <p><strong>Why this matters:</strong> the omnibus SRO framework requires SROs to avoid conflicts of interest. Shared directors and EC members across SROs are legal — but when the same fintech executives shape conduct rules at multiple bodies, consumers should know whose interests get harmonised first.</p>
  </div>
</section>"""
    return page("Cross-SRO overlap", "overlap.html", body)


def build_timeline(activity):
    items = sorted(activity, key=lambda a: a["date"], reverse=True)
    html_items = ""
    cur_year = None
    for a in items:
        y = a["date"][:4]
        if y != cur_year:
            cur_year = y
            html_items += f'<div class="tl-year">{y}</div>'
        badge = sro_badge(a["sro"])
        html_items += f"""
      <div class="tl-item">
        <div class="tl-dot" data-t="{esc(a['type'])}"></div>
        <div class="tl-body">
          <p class="meta"><span class="date">{a['date']}</span> {badge} <span class="pill small">{esc(a['type'])}</span></p>
          <h3><a href="{esc(a['url'])}" rel="noopener">{esc(a['title'])}</a></h3>
          <p>{esc(a['summary'])}</p>
        </div>
      </div>"""
    body = f"""
<section class="hero slim">
  <div class="wrap">
    <h1>Regulatory timeline</h1>
    <p class="lede">How RBI built the SRO system — frameworks, recognitions, and what each SRO did about it.</p>
  </div>
</section>
<section class="wrap">
  <div class="timeline">{html_items}</div>
</section>"""
    return page("Timeline", "timeline.html", body)


def build_activity(activity):
    counts = defaultdict(int)
    for a in activity:
        counts[a["type"]] += 1
    chips = '<button class="chip active" data-f="ALL">All</button>'
    for t in sorted(counts):
        chips += f'<button class="chip" data-f="{esc(t)}">{esc(t)} ({counts[t]})</button>'
    payload = [
        {"d": a["date"], "s": a["sro"], "t": a["type"], "h": a["title"], "u": a["url"], "x": a["summary"]}
        for a in activity
    ]
    body = f"""
<section class="hero slim">
  <div class="wrap">
    <h1>Activity log</h1>
    <p class="lede">Frameworks, recognitions, consultation responses, reports and announcements — dated and linked.</p>
  </div>
</section>
<section class="wrap">
  <div class="filters"><div class="chips" id="achips">{chips}</div></div>
  <div id="alist" class="alist"></div>
</section>
<script id="activity-data" type="application/json">{json.dumps(payload)}</script>"""
    return page("Activity log", "activity.html", body)


def build_about(members, activity):
    body = f"""
<section class="hero slim"><div class="wrap">
  <h1>About SROTrac</h1>
  <p class="lede">An independent, open-data tracker of India's RBI-recognised self-regulatory organisations — built by CashlessConsumer, a consumer collective working on digital payments and fintech.</p>
</div></section>
<section class="wrap cols">
  <div class="col">
    <h2>Method</h2>
    <ul class="ticks">
      <li>Member rosters are parsed from each SRO's own published member pages (captured <strong>2026-09-10</strong>).</li>
      <li>Governance data comes from SRO governance/leadership pages; roles are quoted as published.</li>
      <li>The activity log links only to primary sources (RBI press releases, TRAI filings, SRO pages) or dated news reports.</li>
      <li>The SRPA roster was decoded from its logo wall (filenames are truncated) — treat spelling with care.</li>
      <li>Everything rebuilds from CSV via a single script; the <a href="https://github.com/CashlessConsumer/srotrac">GitHub repo</a> carries the raw captures.</li>
    </ul>
  </div>
  <div class="col">
    <h2>Caveats</h2>
    <ul class="watchlist">
      <li>SRO member pages are <strong>marketing pages, not registers</strong>. FACE claims 200+ members but shows ~85 logos; treat counts as a floor.</li>
      <li><strong>FIDC publishes no member roster at all</strong> — its "list of NBFCs" page holds RBI registration statistics, not membership.</li>
      <li>Membership changes constantly; dates matter. Each dataset notes its capture date.</li>
      <li>Recognition ≠ effectiveness. An SRO can be fully compliant on paper and still never discipline a member. This tracker will log enforcement actions as they surface.</li>
    </ul>
  </div>
</section>
<section class="wrap">
  <h2>License &amp; reuse</h2>
  <p>Code: MIT. Data: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> — copy, remix and republish with attribution to SROTrac / CashlessConsumer.</p>
  <h2>Related CashlessConsumer properties</h2>
  <ul>
    <li><a href="https://cyber.cashlessconsumer.in">cyber.cashlessconsumer.in</a> — security investigations hub</li>
    <li><a href="https://cashlessconsumer.in">cashlessconsumer.in</a> — fintech newsletter &amp; research</li>
  </ul>
</section>"""
    return page("About", "about.html", body)


CSS = """:root{
  --paper:#f2ecdd; --paper-deep:#e9e1cc; --paper-hi:#f8f4e9; --card:#fbf7ec;
  --ink:#211b10; --ink-soft:#4a4232; --faded:#7d735d;
  --rule:#c9bd9f; --rule-soft:#ddd3b8;
  --seal:#9e2b25; --seal-soft:#b9574f;
  --gold:#8a6d1f;
  --accent:#9e2b25;
  --mono:'IBM Plex Mono',ui-monospace,'Courier New',monospace;
  --serif:'Fraunces',Georgia,'Times New Roman',serif;
  --text:'Newsreader',Georgia,serif;
}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{
  margin:0;font:17px/1.65 var(--text);color:var(--ink);background:var(--paper);
  background-image:repeating-linear-gradient(0deg,transparent 0 31px,rgba(120,105,70,.055) 31px 32px);
}
body::after{content:"";position:fixed;inset:0;pointer-events:none;opacity:.5;z-index:99;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .05 0'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E");}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}
::selection{background:var(--seal);color:var(--paper-hi)}
a{color:var(--seal);text-decoration-thickness:1px;text-underline-offset:3px;text-decoration-color:color-mix(in srgb,var(--seal) 45%,transparent);transition:text-decoration-color .15s}
a:hover{text-decoration-color:var(--seal);text-decoration-style:wavy}
h1,h2,h3{line-height:1.18;font-family:var(--serif);font-weight:560;letter-spacing:-.01em}
h1{font-size:clamp(2rem,4.5vw,3.1rem);margin:.4em 0;font-variation-settings:"opsz" 100}
h2{font-size:1.55rem;margin-top:2.2em;padding-bottom:.3em;border-bottom:2px solid var(--ink);position:relative}
h2::after{content:"";position:absolute;left:0;bottom:-5px;width:56px;border-bottom:1px solid var(--ink)}
h3{font-size:1.08rem;margin:1.4em 0 .4em}
.muted{color:var(--faded)}.small{font-size:.85rem}
p{margin:.6em 0}

/* ---------- masthead ---------- */
.site-header{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--paper) 94%,transparent);backdrop-filter:blur(5px);border-bottom:1px solid var(--ink)}
.site-header::before{content:"";display:block;height:5px;border-top:3px double var(--seal);border-bottom:1px solid var(--seal)}
.site-header .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:60px;flex-wrap:wrap;padding-top:6px;padding-bottom:6px}
.brand{font-family:var(--serif);font-weight:800;font-size:1.5rem;color:var(--ink);text-decoration:none;letter-spacing:-.02em;line-height:1;display:flex;align-items:baseline;gap:.6rem}
.brand em{font-style:normal;color:var(--seal)}
.brand small{font-family:var(--mono);font-weight:400;font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;color:var(--faded);border-left:1px solid var(--rule);padding-left:.6rem}
nav{display:flex;gap:1px;flex-wrap:wrap}
nav a{font-family:var(--mono);font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-soft);text-decoration:none;padding:8px 9px;border-bottom:2px solid transparent}
nav a:hover{color:var(--seal);border-bottom-color:var(--rule)}
nav a.active{color:var(--paper-hi);background:var(--seal);border-bottom-color:var(--ink)}
main{min-height:60vh;padding-bottom:3.5rem}

/* ---------- load-in motion ---------- */
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes stampIn{0%{opacity:0;transform:rotate(-14deg) scale(1.9)}55%{opacity:1;transform:rotate(-6deg) scale(.94)}75%{transform:rotate(-7deg) scale(1.03)}100%{opacity:1;transform:rotate(-6.5deg) scale(1)}}
@media(prefers-reduced-motion:no-preference){
  .hero .wrap>*{animation:rise .5s cubic-bezier(.2,.7,.3,1) backwards}
  .hero .wrap>*:nth-child(2){animation-delay:.08s}.hero .wrap>*:nth-child(3){animation-delay:.16s}
  .hero .wrap>*:nth-child(4){animation-delay:.24s}.hero .wrap>*:nth-child(5){animation-delay:.32s}
  .stamp{animation:stampIn .55s cubic-bezier(.2,.9,.3,1.2) .35s backwards}
  .sro-card,.stats div,.factbar div{animation:rise .5s cubic-bezier(.2,.7,.3,1) backwards}
  .sro-card:nth-child(2){animation-delay:.07s}.sro-card:nth-child(3){animation-delay:.14s}
  .sro-card:nth-child(4){animation-delay:.21s}.sro-card:nth-child(5){animation-delay:.28s}
  .sro-card:nth-child(6){animation-delay:.35s}.sro-card:nth-child(7){animation-delay:.42s}
}

/* ---------- stamps ---------- */
.stamp{display:inline-block;font-family:var(--mono);font-size:.68rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--seal);
  border:3px double var(--seal);border-radius:5px;padding:.5em 1em;transform:rotate(-6.5deg);
  mix-blend-mode:multiply;opacity:.92;box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--seal) 30%,transparent)}
.stamp.alt{color:var(--gold);border-color:var(--gold);transform:rotate(3deg);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--gold) 30%,transparent)}
.stamp.small{font-size:.58rem;border-width:2px;padding:.35em .7em}

/* ---------- SRO dropdown ---------- */
.nav-drop{position:relative}
.nav-drop .trigger{font-family:var(--mono);font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--ink-soft);text-decoration:none;padding:8px 9px;border-bottom:2px solid transparent;
  display:inline-flex;align-items:center;gap:.35rem;cursor:pointer;white-space:nowrap}
.nav-drop .trigger:hover{color:var(--seal);border-bottom-color:var(--rule)}
.nav-drop .trigger.active{color:var(--paper-hi);background:var(--seal);border-bottom-color:var(--ink)}
.nav-drop .trigger.active:hover{border-bottom-color:var(--ink)}
.nav-drop .caret{font-size:.55rem;transition:transform .18s}
.dd-panel{display:none;position:absolute;top:100%;right:0;min-width:min(340px,86vw);
  background:var(--card);border:1px solid var(--ink);box-shadow:5px 5px 0 var(--rule);
  padding:6px;z-index:300}
.dd-panel a{display:flex;gap:.6rem;align-items:center;padding:.42rem .55rem;
  text-decoration:none;border-bottom:1px dotted var(--rule-soft)}
.dd-panel a:last-child{border-bottom:none}
.dd-panel a:hover{background:var(--paper-hi)}
.dd-panel a.active{background:var(--paper-hi);outline:1px solid var(--rule)}
.dd-abbr{font-family:var(--mono);font-size:.62rem;font-weight:600;color:var(--c,#5f5540);
  border:1px solid color-mix(in srgb,var(--c,#5f5540) 55%,transparent);border-radius:2px;
  padding:.08em .35em;min-width:4.1em;text-align:center;flex:none;background:color-mix(in srgb,var(--c,#5f5540) 8%,var(--paper-hi))}
.dd-name{font-family:var(--serif);font-size:.9rem;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dd-name small{display:block;font-family:var(--mono);font-size:.58rem;letter-spacing:.1em;text-transform:uppercase;color:var(--faded)}
.nav-drop.open .dd-panel{display:block}
.nav-drop.open .caret{transform:rotate(180deg)}
.nav-drop:focus-within .dd-panel{display:block}
@media(hover:hover) and (min-width:801px){
  .nav-drop:hover .dd-panel{display:block}
  .nav-drop:hover .caret{transform:rotate(180deg)}
}

/* ---------- hero ---------- */
.hero{padding:3.4rem 0 2.4rem;border-bottom:1px solid var(--rule);position:relative;
  background:linear-gradient(180deg,var(--paper-hi),var(--paper))}
.hero::after{content:"";position:absolute;right:0;top:0;width:44%;height:100%;pointer-events:none;opacity:.6;
  background-image:radial-gradient(circle at 78% 30%,color-mix(in srgb,var(--seal) 7%,transparent),transparent 60%)}
.hero.slim{padding:2.4rem 0 1.6rem}
.kicker{font-family:var(--mono);font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--seal);font-weight:600;margin:0 0 .6rem}
.lede{font-size:1.12rem;color:var(--ink-soft);max-width:54rem}
.lede strong{color:var(--ink)}

/* ---------- stats ledger ---------- */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0;margin-top:2rem;max-width:56rem;border:1px solid var(--ink);background:var(--card);box-shadow:4px 4px 0 var(--rule)}
.stats div{padding:.8rem 1.1rem;border-right:1px solid var(--rule-soft);border-bottom:1px solid var(--rule-soft)}
.stats div:nth-child(2n){border-right:none}
.stats div:nth-last-child(-n+2){border-bottom:none}
.stats strong{display:block;font-family:var(--serif);font-weight:600;font-size:2.1rem;line-height:1.1;color:var(--seal);font-variant-numeric:tabular-nums}
.stats span{font-family:var(--mono);font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:var(--faded)}

/* ---------- register cards (file folders) ---------- */
.sro-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px;margin:1.4rem 0 2rem}
.sro-card{--c:var(--seal);position:relative;display:block;background:var(--card);border:1px solid var(--rule);border-top:none;
  padding:1.15rem 1.1rem .95rem;margin-top:14px;text-decoration:none;color:var(--ink);
  box-shadow:0 1px 0 var(--rule);transition:transform .18s cubic-bezier(.2,.7,.3,1),box-shadow .18s}
.sro-card::before{content:attr(data-abbr);position:absolute;top:-14px;left:10px;font-family:var(--mono);font-size:.66rem;font-weight:600;letter-spacing:.14em;
  background:color-mix(in srgb,var(--c) 16%,var(--card));color:var(--c);border:1px solid var(--rule);border-bottom:none;padding:.22em .8em .5em}
.sro-card::after{content:"";position:absolute;top:-1px;right:-1px;width:20px;height:20px;
  background:linear-gradient(225deg,var(--paper) 50%,transparent 50%);border-left:1px solid var(--rule)}
.sro-card:hover{transform:translateY(-5px);box-shadow:0 10px 22px rgba(60,45,20,.18)}
.sro-card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-top:.2rem}
.sro-abbr{display:none}
.sro-card h3{margin:.4rem 0 .25rem;font-size:1.02rem;font-weight:600}
.pill{display:inline-block;font-family:var(--mono);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-soft);border:1px solid var(--rule);background:var(--paper-hi);padding:2px 8px;border-radius:2px;white-space:nowrap}
.pill.small{font-size:.58rem}
.badge{--c:#5f5540;display:inline-block;font-family:var(--mono);font-size:.64rem;font-weight:600;letter-spacing:.06em;
  color:var(--c);border:1.5px solid color-mix(in srgb,var(--c) 65%,transparent);background:color-mix(in srgb,var(--c) 7%,var(--paper-hi));
  padding:1px 7px;border-radius:3px;text-decoration:none;margin-right:6px;transform:rotate(-1deg)}
a.badge:hover{background:color-mix(in srgb,var(--c) 16%,var(--paper-hi));text-decoration:none}
.meta{font-family:var(--mono);font-size:.72rem;color:var(--faded)}

/* ---------- notice / callout ---------- */
.callout{position:relative;background:var(--paper-hi);border:1px solid var(--ink);box-shadow:5px 5px 0 var(--rule);
  padding:1.3rem 1.5rem;margin:1.6rem 0}
.callout::before{content:"CONSUMER NOTICE";position:absolute;top:-0.7em;left:14px;background:var(--paper-hi);
  font-family:var(--mono);font-size:.6rem;letter-spacing:.2em;color:var(--seal);padding:0 .6em}
.callout p:first-of-type{margin-top:0}

/* ---------- feed ---------- */
.feed{list-style:none;padding:0;margin:1.2rem 0}
.feed li{display:flex;flex-wrap:wrap;align-items:baseline;gap:.45rem;padding:.6rem .2rem;border-bottom:1px dotted var(--rule)}
.feed a{font-weight:500}
.date{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:.72rem;color:var(--faded);margin-right:.25rem}

/* ---------- buttons ---------- */
.btn{display:inline-block;font-family:var(--mono);font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;font-weight:600;
  color:var(--ink);background:transparent;border:1.5px solid var(--ink);padding:.65rem 1.25rem;text-decoration:none;
  box-shadow:3px 3px 0 var(--ink);transition:all .15s}
.btn:hover{background:var(--ink);color:var(--paper-hi);box-shadow:1px 1px 0 var(--ink);transform:translate(2px,2px);text-decoration:none}

/* ---------- columns & lists ---------- */
.cols{display:grid;grid-template-columns:1fr 1fr;gap:3rem}
@media(max-width:800px){.cols{grid-template-columns:1fr}}
.ticks li,.watchlist li{margin:.55rem 0;padding-left:1.4rem;position:relative;list-style:none}
.ticks li::before{content:"✓";position:absolute;left:0;color:var(--gold);font-weight:700}
.watchlist{padding-left:0}
.watchlist li::before{content:"→";position:absolute;left:0;color:var(--seal)}

/* ---------- SRO file page ---------- */
.sro-hero{--c:var(--seal);border-bottom:1px solid var(--rule);padding:2.6rem 0 1.8rem;position:relative;
  background:linear-gradient(180deg,color-mix(in srgb,var(--c) 5%,var(--paper-hi)),var(--paper))}
.sro-hero::before{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:repeating-linear-gradient(90deg,transparent 0 46px,color-mix(in srgb,var(--c) 5%,transparent) 46px 47px)}
.abbr-chip{font-family:var(--mono);font-size:.95rem;font-weight:600;vertical-align:.35em;color:var(--paper-hi);background:var(--c);
  padding:.15em .55em;margin-left:.5rem;letter-spacing:.05em}
.factbar{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:0;margin-top:1.6rem;border:1px solid var(--ink);background:var(--card);box-shadow:4px 4px 0 var(--rule)}
.factbar div{padding:.65rem .95rem;border-right:1px solid var(--rule-soft)}
.factbar div:last-child{border-right:none}
.factbar span{display:block;font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--faded)}
.factbar strong{font-weight:600}
.factbar a{word-break:break-all}

/* ---------- ledgers (tables) ---------- */
table.listing,.people{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--ink);
  box-shadow:4px 4px 0 var(--rule);font-size:.9rem;margin:1.2rem 0}
th,td{text-align:left;padding:.55rem .85rem;border-bottom:1px dotted var(--rule);vertical-align:top}
th{font-family:var(--mono);font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft);
  background:var(--paper-deep);border-bottom:2px solid var(--ink)}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:var(--paper-hi)}
.linkcell a{font-family:var(--mono);font-size:.74rem;word-break:break-all;color:var(--faded)}
.people td{font-size:.86rem}

/* ---------- filters ---------- */
.filters{display:flex;flex-wrap:wrap;gap:.9rem;align-items:center;margin:1.2rem 0}
#mq,#achips{width:100%}
#mq{font-family:var(--mono);padding:.65rem .95rem;border:1.5px solid var(--ink);background:var(--card);font-size:.95rem;max-width:400px;box-shadow:3px 3px 0 var(--rule)}
#mq:focus{outline:none;box-shadow:3px 3px 0 var(--seal);border-color:var(--seal)}
.chips{display:flex;gap:7px;flex-wrap:wrap}
.chip{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;border:1px solid var(--rule);
  background:var(--card);padding:.4rem .85rem;cursor:pointer;color:var(--ink-soft);transition:all .12s}
.chip:hover{border-color:var(--seal);color:var(--seal)}
.chip.active{background:var(--ink);color:var(--paper-hi);border-color:var(--ink)}

/* ---------- timeline (notification register) ---------- */
.timeline{position:relative;margin:1.8rem 0 1rem;padding-left:30px;border-left:2px solid var(--ink)}
.tl-year{display:inline-block;font-family:var(--mono);font-weight:600;font-size:.85rem;letter-spacing:.16em;color:var(--paper-hi);
  background:var(--ink);padding:.15em .7em;margin:1.8rem 0 .7rem;transform:rotate(-1deg)}
.tl-item{position:relative;padding:0 0 1.5rem}
.tl-dot{position:absolute;left:-38px;top:8px;width:11px;height:11px;background:var(--seal);transform:rotate(45deg);
  box-shadow:0 0 0 4px var(--paper),0 0 0 5px var(--rule)}
.tl-dot[data-t="framework"]{background:var(--gold)}
.tl-dot[data-t="consultation"]{background:#1f3a5f}
.tl-dot[data-t="report"],.tl-dot[data-t="newsletter"]{background:var(--ink-soft)}
.tl-body h3{margin:.15rem 0 .25rem;font-size:1.05rem}
.tl-body p{margin:.25rem 0;color:var(--ink-soft);max-width:46rem}

/* ---------- activity cards ---------- */
.alist{display:grid;gap:.9rem}
.alist .card{background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--seal);padding:.9rem 1.15rem}
.alist .card h3{margin:.15rem 0 .25rem;font-size:1.02rem}

/* ---------- blog ---------- */
.grid-posts{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:18px;margin-top:1.4rem}
.post-card{background:var(--card);border:1px solid var(--rule);box-shadow:3px 3px 0 var(--rule);padding:1.2rem 1.25rem;transition:transform .16s,box-shadow .16s}
.post-card:hover{transform:translateY(-4px);box-shadow:6px 8px 0 var(--rule)}
.post-card h2{font-size:1.15rem;margin:.4em 0;border:none}
.post-card h2::after{display:none}
.post-card .date{display:block;margin-bottom:.2rem}
.page-head{margin:2.4rem 0 .4rem}
.page-head h1{margin-bottom:.15em}
.post-full{max-width:46rem}
.post-full h2{font-size:1.3rem}

/* ---------- footer ---------- */
.site-footer{border-top:1px solid var(--ink);background:var(--paper-deep);padding:1.8rem 0;color:var(--ink-soft);font-size:.88rem;position:relative}
.site-footer::before{content:"";position:absolute;top:4px;left:0;right:0;border-top:1px solid var(--rule)}
.site-footer p{margin:.35rem 0}
.site-footer .colophon{font-family:var(--mono);font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--faded)}
@media print{body::after{display:none}.site-header{position:static}}
"""

JS = """// SROTrac: nav helpers + members/activity filtering
var SRO_KEYS = ["FACE", "UFF", "FIDC", "SRPA", "MFIN", "Sa-Dhan", "FEDAI"];
(function(){
  // highlight current page
  function normPath(p){ return (p.length > 1 && p.charAt(p.length-1) === '/') ? p.slice(0, -1) : p; }
  var path = normPath(location.pathname) || '/';
  document.querySelectorAll('nav > a').forEach(function(a){
    var href = normPath(a.getAttribute('href')) || '/';
    if (href === path) a.classList.add('active'); else a.classList.remove('active');
  });

  // SRO dropdown: tap/click toggles on touch; hover handled by CSS on pointer devices
  var drop = document.querySelector('.nav-drop');
  if (drop) {
    drop.querySelector('.trigger').addEventListener('click', function(e){
      e.preventDefault();
      drop.classList.toggle('open');
    });
    document.addEventListener('click', function(e){
      if (!drop.contains(e.target)) drop.classList.remove('open');
    });
  }

  function chipFilter(containerSel, apply){
    var box = document.querySelector(containerSel);
    if (!box) return;
    box.addEventListener('click', function(e){
      var b = e.target.closest('.chip');
      if (!b) return;
      box.querySelectorAll('.chip').forEach(function(c){c.classList.remove('active');});
      b.classList.add('active');
      apply(b.dataset.f);
    });
  }

  // Members page
  var dataEl = document.getElementById('member-data');
  if (dataEl){
    var members = JSON.parse(dataEl.textContent);
    var rowsEl = document.getElementById('mrows');
    var countEl = document.getElementById('mcount');
    var q = '', f = 'ALL';
    var multi = {};
    members.forEach(function(m){ multi[m.n] = (multi[m.n]||0)+ (multi[m.n]?0:0); });
    var countByOrg = {};
    members.forEach(function(m){ countByOrg[m.n] = (countByOrg[m.n]||0)+1; });
    function render(){
      var out = '', shown = 0;
      var needle = q.toLowerCase();
      members.forEach(function(m){
        if (f === 'MULTI' && countByOrg[m.n] < 2) return;
        if (f !== 'ALL' && f !== 'MULTI' && m.s !== f) return;
        if (needle && m.n.toLowerCase().indexOf(needle) === -1) return;
        shown++;
        out += '<tr><td>'+m.n+'</td><td><span class="badge" style="--c:'+m.c+'">'+m.s+'</span></td>'+
               '<td><span class="pill small">'+m.t+'</span></td>'+
               '<td class="linkcell"><a href="'+m.w+'" rel="noopener">'+m.w.replace(/^https?:\\/\\//,'')+'</a></td></tr>';
      });
      rowsEl.innerHTML = out || '<tr><td colspan="4">No matches.</td></tr>';
      countEl.textContent = shown + ' of ' + members.length + ' rows shown';
    }
    document.getElementById('mq').addEventListener('input', function(e){ q = e.target.value; render(); });
    chipFilter('#chips', function(v){ f = v; render(); });
    render();
  }

  // Activity page
  var actEl = document.getElementById('activity-data');
  if (actEl){
    var acts = JSON.parse(actEl.textContent);
    var list = document.getElementById('alist');
    var f2 = 'ALL';
    function render2(){
      var out = '';
      acts.forEach(function(a){
        if (f2 !== 'ALL' && a.t !== f2) return;
        var sl = a.s.toLowerCase();
        var badge = SRO_KEYS.indexOf(a.s) >= 0
          ? '<a class="badge" href="/sro-'+sl+'.html">'+a.s+'</a>'
          : '<span class="badge">RBI</span>';
        out += '<div class="card"><p class="meta"><span class="date">'+a.d+'</span> '+badge+
               ' <span class="pill small">'+a.t+'</span></p><h3><a href="'+a.u+'" rel="noopener">'+a.h+'</a></h3><p>'+a.x+'</p></div>';
      });
      list.innerHTML = out;
    }
    chipFilter('#achips', function(v){ f2 = v; render2(); });
    render2();
  }
})();
"""


def main():
    members = []
    for s in SROS.values():
        members.extend(read_csv(f"{s['abbr'].lower()}_members.csv"))
    for m in members:
        m["sro"] = m["sro"].upper()
    activity = sorted(read_csv("activity.csv"), key=lambda a: a["date"], reverse=True)
    leadership = read_csv("leadership.csv")

    orgs = defaultdict(set)
    for m in members:
        orgs[m["member_name"]].add(m["sro"])
    overlap = [{"name": n, "sros": sorted(s)} for n, s in orgs.items()]

    outputs = {
        "index.html": build_home(members, activity, overlap),
        "members.html": build_members(members),
        "overlap.html": build_overlap(members, leadership),
        "timeline.html": build_timeline(activity),
        "activity.html": build_activity(activity),
        "about.html": build_about(members, activity),
    }
    for sid in SROS:
        outputs[f"sro-{sid}.html"] = build_sro(sid, members, activity, leadership)

    for name, content in outputs.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote", name)

    css_dir = os.path.join(ROOT, "css")
    js_dir = os.path.join(ROOT, "js")
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    with open(os.path.join(css_dir, "style.css"), "w") as f:
        f.write(CSS)
    with open(os.path.join(js_dir, "main.js"), "w") as f:
        f.write(JS)
    print("wrote css/style.css, js/main.js")


if __name__ == "__main__":
    main()
