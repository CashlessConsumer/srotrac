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
        "accent": "#b91c1c",
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
        "accent": "#1d4ed8",
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
        "accent": "#6d28d9",
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
        "accent": "#047857",
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
        "accent": "#b45309",
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
        "accent": "#15803d",
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
        "accent": "#1e40af",
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
    ("sro-face.html", "FACE"),
    ("sro-uff.html", "UFF"),
    ("sro-fidc.html", "FIDC"),
    ("sro-srpa.html", "SRPA"),
    ("sro-mfin.html", "MFIN"),
    ("sro-sadhan.html", "Sa-Dhan"),
    ("sro-fedai.html", "FEDAI"),
    ("members.html", "Members"),
    ("overlap.html", "Overlap"),
    ("timeline.html", "Timeline"),
    ("activity.html", "Activity"),
    ("blog/index.html", "Blog"),
    ("about.html", "About"),
]


def page(title, active, body, extra_head=""):
    nav = ""
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        nav += f'<a href="/{href}"{cls}>{label}</a>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — SROTrac</title>
<meta name="description" content="Independent tracker of India's RBI-recognised self-regulatory organisations in fintech, NBFC and payments: members, governance, activity, and what they mean for consumers.">
<link rel="stylesheet" href="/css/style.css">
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">SRO<span>Trac</span></a>
    <nav>{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p><strong>SROTrac</strong> — an independent CashlessConsumer project tracking India's fintech self-regulatory organisations. Not affiliated with RBI or any SRO.</p>
    <p><a href="https://cashlessconsumer.in">cashlessconsumer.in</a> · data: <a href="https://github.com/CashlessConsumer/srotrac">GitHub</a> · <a href="/about.html">methodology</a></p>
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
    <a class="sro-card" href="/sro-{sid}.html" style="--c:{s['accent']}">
      <div class="sro-card-head"><span class="sro-abbr">{s['abbr']}</span>
      <span class="pill">{esc(s['status'])}</span></div>
      <h3>{esc(s['name'])}</h3>
      <p class="muted">{esc(s['sector'])}</p>
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
    <h1>Who watches India's fintech watchdogs?</h1>
    <p class="lede">RBI outsources first-line supervision of fintechs, NBFCs and payment operators to <strong>self-regulatory organisations</strong> — industry bodies with the power to write conduct codes and police their own members. SROTrac tracks who sits on these SROs, what they do, and whether they work for consumers.</p>
    <div class="stats">
      <div><strong>{len(SROS)}</strong><span>RBI-recognised SROs</span></div>
      <div><strong>{total}</strong><span>listed member orgs</span></div>
      <div><strong>{both}</strong><span>in 2+ SROs</span></div>
      <div><strong>{srofts}</strong><span>fintech SRO-FTs</span></div>
    </div>
  </div>
</section>
<section class="wrap">
  <h2>The register</h2>
  <div class="sro-grid">{cards}
  </div>
</section>
<section class="wrap">
  <div class="callout">
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
  <h2>SROTrac Weekly</h2>
  <p>A weekly digest of what moved in SRO-land — roster changes, consultations,
  enforcement, recognition news — generated from the tracker's own diffs.</p>
  <p><a class="btn" href="/blog/index.html">Read the blog →</a></p>
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
    payload = [
        {"n": m["member_name"], "s": m["sro"].upper(), "t": m["member_type"] or "member", "w": m["website"]}
        for m in sorted(members, key=lambda x: (x["member_name"].lower(), x["sro"]))
    ]
    body = f"""
<section class="hero slim">
  <div class="wrap">
    <h1>All members</h1>
    <p class="lede">{len(members)} rows across FACE, UFF and SRPA (FIDC publishes no roster). Filter by SRO or search by name.</p>
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


CSS = """:root{--ink:#101828;--muted:#667085;--bg:#faf9f7;--card:#fff;--line:#e6e2da;--accent:#0f766e;--serif:Georgia,'Times New Roman',serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
.wrap{max-width:1060px;margin:0 auto;padding:0 20px}
a{color:var(--accent)}
h1,h2,h3{line-height:1.25}
h1{font-family:var(--serif);font-size:2.1rem;margin:.4em 0}
h2{font-family:var(--serif);font-size:1.5rem;margin-top:2em;border-bottom:1px solid var(--line);padding-bottom:.3em}
h3{font-size:1.05rem}
.muted{color:var(--muted)}.small{font-size:.85rem}
.site-header{position:sticky;top:0;background:rgba(250,249,247,.95);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);z-index:50}
.site-header .wrap{display:flex;align-items:center;justify-content:space-between;height:56px}
.brand{font-weight:800;font-size:1.2rem;color:var(--ink);text-decoration:none;letter-spacing:-.02em}
.brand span{color:var(--accent)}
nav{display:flex;gap:2px;flex-wrap:wrap}
nav a{color:var(--muted);text-decoration:none;font-size:.88rem;padding:6px 9px;border-radius:6px}
nav a:hover{background:#efece6;color:var(--ink)}
nav a.active{background:var(--ink);color:#fff}
main{min-height:60vh;padding-bottom:3rem}
.hero{padding:3.2rem 0 2.2rem;border-bottom:1px solid var(--line);background:linear-gradient(180deg,#fff, var(--bg))}
.hero.slim{padding:2.2rem 0 1.4rem}
.hero .kicker{text-transform:uppercase;letter-spacing:.14em;font-size:.75rem;color:var(--accent);font-weight:700;margin:0}
.lede{font-size:1.08rem;color:#3d4757;max-width:52rem}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:1.6rem;max-width:52rem}
.stats div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.7rem 1rem}
.stats strong{display:block;font-size:1.7rem;font-family:var(--serif)}
.stats span{font-size:.8rem;color:var(--muted)}
.sro-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:1rem 0 2rem}
.sro-card{--c:var(--accent);display:block;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:10px;padding:1rem 1.1rem;text-decoration:none;color:var(--ink);transition:box-shadow .15s}
.sro-card:hover{box-shadow:0 4px 18px rgba(16,24,40,.09)}
.sro-card-head{display:flex;justify-content:space-between;align-items:center;gap:8px}
.sro-abbr{font-weight:800;color:var(--c);font-size:1.15rem}
.sro-card h3{margin:.35rem 0 .2rem;font-size:1rem}
.pill{display:inline-block;font-size:.68rem;background:color-mix(in srgb,var(--accent) 10%,#fff);border:1px solid var(--line);color:var(--ink);padding:2px 8px;border-radius:999px}
.pill.small{font-size:.66rem}
.badge{--c:#57534e;display:inline-block;font-size:.68rem;font-weight:700;color:var(--c);border:1px solid color-mix(in srgb,var(--c) 40%,#fff);background:color-mix(in srgb,var(--c) 8%,#fff);padding:1px 7px;border-radius:6px;text-decoration:none;margin-right:6px}
.meta{font-size:.82rem;color:var(--muted)}
.callout{background:#f2f7f6;border:1px solid #d5e5e2;border-radius:12px;padding:1.2rem 1.4rem;margin:1.2rem 0}
.feed{list-style:none;padding:0;margin:1rem 0}
.feed li{padding:.55rem 0;border-bottom:1px dashed var(--line)}
.date{font-variant-numeric:tabular-nums;font-size:.8rem;color:var(--muted);margin-right:.5rem}
.btn{display:inline-block;background:var(--ink);color:#fff;padding:.55rem 1.1rem;border-radius:8px;text-decoration:none;font-size:.9rem}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:2.5rem}
@media(max-width:800px){.cols{grid-template-columns:1fr}}
.ticks{padding-left:1.1rem}.ticks li{margin:.5rem 0}
.watchlist{padding-left:1.1rem}.watchlist li{margin:.5rem 0}
.sro-hero{--c:var(--accent);border-bottom:1px solid var(--line);background:linear-gradient(180deg,color-mix(in srgb,var(--c) 6%,#fff),var(--bg));padding:2.4rem 0 1.6rem}
.abbr-chip{font-family:-apple-system,sans-serif;font-size:.9rem;vertical-align:middle;color:var(--c);border:2px solid var(--c);border-radius:8px;padding:2px 10px;margin-left:.4rem}
.factbar{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:1.2rem}
.factbar div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.6rem .9rem}
.factbar span{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
table.listing,.people{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:.92rem}
th,td{text-align:left;padding:.55rem .8rem;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f4f1ea;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fbf8f2}
.linkcell a{word-break:break-all;color:var(--muted)}
.filters{display:flex;flex-wrap:wrap;gap:.8rem;align-items:center;margin:1rem 0}
#mq,#achips{width:100%}
#mq{padding:.6rem .9rem;border:1px solid var(--line);border-radius:8px;font-size:1rem;background:var(--card);max-width:380px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:.35rem .9rem;font-size:.85rem;cursor:pointer;color:var(--ink)}
.chip.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.timeline{position:relative;margin:1.5rem 0;padding-left:26px;border-left:2px solid var(--line)}
.tl-year{font-family:var(--serif);font-weight:700;font-size:1.25rem;margin:1.6rem 0 .6rem;color:var(--accent)}
.tl-item{position:relative;padding:0 0 1.4rem}
.tl-dot{position:absolute;left:-34px;top:6px;width:12px;height:12px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 3px var(--bg),0 0 0 4px var(--line)}
.tl-dot[data-t="recognition"]{background:#b45309}
.tl-dot[data-t="framework"]{background:#1d4ed8}
.tl-body h3{margin:.15rem 0 .2rem;font-size:1.02rem}
.tl-body p{margin:.2rem 0;color:#3d4757}
.alist{display:grid;gap:.7rem}
.alist .card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.85rem 1.1rem}
.alist .card h3{margin:.1rem 0 .2rem;font-size:1rem}
.site-footer{border-top:1px solid var(--line);background:#f4f1ea;padding:1.6rem 0;color:var(--muted);font-size:.85rem}
.site-footer p{margin:.3rem 0}"""

JS = """// SROTrac: nav helpers + members/activity filtering
(function(){
  // highlight current page
  var path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav a').forEach(function(a){
    var href = a.getAttribute('href').split('/').pop();
    if (href === path) a.classList.add('active'); else a.classList.remove('active');
  });

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
        out += '<tr><td>'+m.n+'</td><td><span class="badge" style="--c:var(--accent)">'+m.s+'</span></td>'+
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
        var badge = ['FACE','UFF','FIDC','SRPA'].indexOf(a.s) >= 0
          ? '<a class="badge" href="/sro-'+a.s.toLowerCase()+'.html">'+a.s+'</a>'
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
