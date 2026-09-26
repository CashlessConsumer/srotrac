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
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from work_content import WORK
from entity_types import classify, TYPES, GROUP_ORDER
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

SROS = {
    "face": {
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "FACE", "name": "Fintech Association for Consumer Empowerment",
        "sector": "Fintech / digital lending",
        "order": "1st", "recognised": "2024-08-28",
        "website": "https://faceofindia.org",
        "members_site": "https://faceofindia.org/membership/",
        "hq": "INNOV8, Peninsula Business Park, Lower Parel, Mumbai 400013",
        "cin": "U91990MH2020NPL346315",
        "status": "Active SRO-FT",
        "accent": "#1d4ed8",
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
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "UFF", "name": "Unified Fintech Forum",
        "sector": "Fintech (broad): lenders, wallets/PPIs, neobanks, BNPL",
        "order": "2nd", "recognised": "2026-09-10",
        "website": "https://unifiedfintech.in",
        "members_site": "https://unifiedfintech.in/members-network/",
        "hq": "Mumbai (rebranded from Digital Lenders Association of India, Apr 2025)",
        "cin": "",
        "status": "Active SRO-FT (recognised at GFF 2026)",
        "accent": "#0e7490",
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
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "FIDC", "name": "Finance Industry Development Council",
        "sector": "NBFCs (incl. digital lenders) — recognised under omnibus framework, not the SRO-FT framework",
        "order": "—", "recognised": "2025-10-03",
        "website": "https://www.fidcindia.org.in",
        "members_site": "https://www.fidcindia.org.in/membership-details/",
        "hq": "Mumbai",
        "cin": "",
        "status": "Active SRO (NBFC)",
        "accent": "#475569",
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
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "SRPA", "name": "Self-Regulated PSO Association",
        "sector": "Payment system operators: payment aggregators, wallets/PPIs, POS",
        "order": "1st", "recognised": "2025-11-11",
        "website": "https://srpa.org.in",
        "members_site": "https://srpa.org.in/",
        "hq": "Siddharth, 11th Floor, Tilak Road, Santacruz West, Mumbai 400054",
        "cin": "",
        "status": "Active SRO (PSO)",
        "accent": "#64748b",
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
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "MFIN", "name": "Microfinance Institutions Network",
        "sector": "NBFC-MFIs (+ banks/SFBs lending microfinance as associate members)",
        "order": "1st", "recognised": "2014-06-16",
        "website": "https://mfinindia.org",
        "members_site": "https://mfinindia.org/members",
        "hq": "New Delhi / Mumbai",
        "cin": "",
        "status": "Active SRO (microfinance; RBI letter 16 Jun 2014 — first SRO in this family)",
        "accent": "#334155",
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
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "Sa-Dhan", "name": "Sa-Dhan (Association of Community Development Finance Institutions)",
        "sector": "Microfinance (broad network: MFIs, SFBs, banks, investors)",
        "order": "2nd", "recognised": "2015-03-11",
        "website": "https://www.sa-dhan.net",
        "members_site": "https://www.sa-dhan.net/what-we-do/sro/",
        "hq": "New Delhi",
        "cin": "",
        "status": "Active SRO (microfinance; recognised Mar 2015)",
        "accent": "#5b6472",
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
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "FEDAI", "name": "Foreign Exchange Dealers' Association of India",
        "sector": "Authorised Dealers in foreign exchange (banks + FEMA-authorised entities)",
        "order": "—", "recognised": "2026-01-14",
        "website": "https://www.fedai.org.in",
        "members_site": "https://www.fedai.org.in/InnerPageContent.aspx?Cid=2&SCid=1&SSCid=0",
        "hq": "Mumbai (est. 1958, Section 25 company)",
        "cin": "",
        "status": "Active SRO (FX; Omnibus framework; 1-yr transition to Jan 2027)",
        "accent": "#6b7280",
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
    "sahamati": {
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "Sahamati", "name": "Sahamati",
        "sector": "Account Aggregator (AA) ecosystem — AAs, FIPs, FIUs, TSPs",
        "order": "8", "recognised": "2026-06-05",
        "website": "https://sahamati.org.in",
        "members_site": "https://sahamati.org.in/current-re-members/",
        "hq": "Mumbai (Section 8; founded 2019 as AA ecosystem collective)",
        "cin": "",
        "status": "Active SRO (AA ecosystem; 8th RBI-recognised SRO)",
        "accent": "#2563eb",
        "consumer": [
            "The 8th RBI-recognised SRO (5 Jun 2026) and the first for open finance — it governs the account aggregator network you may use to share bank statements with a lender or app.",
            "110 ecosystem REs listed: account aggregators, banks/NBFCs as data providers (FIPs), data consumers (FIUs) and tech service providers — searchable in the members table.",
            "For customers: Sahamati's dashboards track AA usage and grievances; if a fintech misuses your consented financial data, the AA framework is where accountability begins.",
        ],
        "watch": [
            "Young SRO for a consent-based data ecosystem — watch how it handles complaints against FIUs and whether Fair Use rules get teeth.",
            "Roster mixes differently-regulated entities (RBI banks, SEBI brokers, IRDAI insurers); cross-regulator discipline is its hardest test.",
        ],
    },
    "fimmda": {
        "regulator": "RBI",
        "regulator": "RBI",
        "abbr": "FIMMDA", "name": "Fixed Income Money Market and Derivatives Association of India",
        "sector": "Financial markets: fixed income, money market and derivatives (banks, primary dealers, insurers, public financial institutions)",
        "order": "1st", "recognised": "2025-05-07",
        "website": "https://www.fimmda.org",
        "members_site": "https://www.fimmda.org/UploadPopupPageFiles/MembersList_8May2025.pdf",
        "hq": "Bandra Kurla Complex, Mumbai (incorporated 4 May 1998, Section 25 company)",
        "cin": "",
        "status": "Active SRO (financial markets; first under the Aug 2024 framework)",
        "accent": "#0f766e",
        "consumer": [
            "The bond and money-market rules your mutual fund, pension fund and insurer trade under are drafted here — FIMMDA sets market practices, standard agreements and the code of fair conduct for the fixed-income market.",
            "RBI mandates its valuation of government bonds, corporate bonds and securitised papers — the daily prices that sit inside nearly every debt portfolio in the country.",
            "Constituted a Disciplinary Committee (1 Sep 2026, chaired by an independent director) — the enforcement machinery its new SRO status requires.",
        ],
        "watch": [
            "Its overview page claims a “115 member strong” body (13 PSBs, 19 private banks, 35 foreign banks…) — its own member-list PDF (8 May 2025) shows 116 rows with different category counts, and the list has not been refreshed since.",
            "Recognised on 7 May 2025; disciplinary committee only constituted 16 months later (Sep 2026) — enforcement record starts from zero.",
            "Website is a legacy frameset and the roster ships as a PDF — public disclosure lags peer SROs like FEDAI.",
        ],
    },

    "basl": {
        "regulator": "SEBI",
        "abbr": "BASL", "name": "BSE Administration and Supervision Ltd",
        "sector": "Investment advisers (IAASB) + research analysts (RAASB)",
        "order": "—", "recognised": "2021-06-01",
        "website": "https://www.basl.in",
        "members_site": "",
        "hq": "Mumbai (wholly-owned BSE subsidiary)",
        "cin": "",
        "status": "Active SRO-body (IAASB + RAASB)",
        "accent": "#b45309",
        "consumer": [
            "Every SEBI-registered <strong>investment adviser</strong> — anyone paid to advise you on stocks or MFs — is deemed a BASL member; SEBI's 2024 framework made BSE/BASL also the supervisory body (RAASB) for <strong>research analysts</strong>.",
            "Runs registration vetting, compliance supervision and grievance handling for the advice industry; recognised as IAASB for a 3-year term from 1 Jun 2021, continuing under the 2024 supervisory-body framework.",
            "If your adviser or a Telegram 'research analyst' rips you off, BASL's complaint desk is the industry-level stop before SEBI.",
        ],
        "watch": [
            "<strong>No public member roster.</strong> Membership derives from SEBI's IA/RA registers, but BASL publishes no list, no inspection outcomes, no action counts.",
            "The IAASB recognition began as a 3-year term (Jun 2021) — watch renewal terms and how many advisers actually face action.",
        ],
    },
    "aibi": {
        "regulator": "SEBI",
        "abbr": "AIBI", "name": "Association of Investment Bankers of India",
        "sector": "Merchant bankers / investment banks",
        "order": "—", "recognised": "1997-98 (AR)",
        "website": "https://aibi.org.in",
        "members_site": "https://aibi.org.in/member.asp",
        "hq": "Mumbai (as AMBI; renamed AIBI)",
        "cin": "",
        "status": "Active SRO (investment banking)",
        "accent": "#b45309",
        "consumer": [
            "The SEBI-recognised body for merchant bankers — the intermediaries that price and run the IPOs retail money flows into. Recognition is recorded in SEBI's own annual report back to 1997-98.",
            "Represents the industry on SEBI's Primary Market Advisory Committee; runs an annual summit where the SEBI chair is chief guest.",
            "Claims ~109 members; eligibility requires a live SEBI merchant-banker licence.",
        ],
        "watch": [
            "<strong>No public member roster</strong> — member.asp is a join page, not a list.",
            "No published enforcement or code-of-conduct machinery despite decades of recorded recognition.",
        ],
    },
    "lic": {
        "regulator": "IRDAI",
        "abbr": "LI Council", "name": "Life Insurance Council",
        "sector": "Life insurers (entire industry)",
        "order": "—", "recognised": "1938 (s.64C)",
        "website": "http://www.lifeinscouncil.org",
        "members_site": "http://www.lifeinscouncil.org/consumers/ListOfCompanies",
        "hq": "Mumbai (statutory council under the Insurance Act, 1938)",
        "cin": "",
        "status": "Active statutory SRO (life insurance)",
        "accent": "#be123c",
        "consumer": [
            "The entire life-insurance industry self-regulates here by statute — s.64C of the Insurance Act, 1938, not a regulator's discretionary recognition.",
            "Publishes the industry's code of conduct; its own member list covers 27 life insurers, LIC to Acko Life.",
            "Beyond the insurance ombudsman, this council is the industry-level body a life-policy grievance escalates through.",
        ],
        "watch": [
            "Statutory status from 1938 predates IRDAI (1999) — the council's independence from the insurers that fund it is structural, not chosen.",
            "The website publishes little on member discipline; watch for gaps vs IRDAI's own action counts.",
        ],
    },
    "gic": {
        "regulator": "IRDAI",
        "abbr": "GI Council", "name": "General Insurance Council",
        "sector": "General + health insurers and reinsurers",
        "order": "—", "recognised": "1938 (s.64C)",
        "website": "https://www.gicouncil.in",
        "members_site": "https://www.gicouncil.in/members-of-gi-council/",
        "hq": "Mumbai (statutory council under the Insurance Act, 1938)",
        "cin": "",
        "status": "Active statutory SRO (general insurance)",
        "accent": "#be123c",
        "consumer": [
            "General, health and reinsurance companies' statutory self-regulator — 49 members from Acko General and Care Health to GIC Re, Lloyd's and Swiss Re branches.",
            "Its code of good insurance practices shapes claims handling across motor, health and fire policies — the fine print of every general-insurance claim you file.",
            "Publishes a member directory with named CEOs — the only insurer roster on this register with named accountability.",
        ],
        "watch": [
            "Same 1938 statutory-independence question as the Life Council.",
            "Claims-handling and cashless-network discipline live here — watch whether hospital-network disputes ever surface enforcement.",
        ],
    },
    "iiipi": {
        "regulator": "IBBI",
        "abbr": "IIIPI", "name": "Indian Institute of Insolvency Professionals of ICAI",
        "sector": "Insolvency professionals (IPA, reg. IBBI/IPA/16-17/01)",
        "order": "—", "recognised": "2016-17",
        "website": "https://www.iiipicai.in",
        "members_site": "",
        "hq": "New Delhi (ICAI subsidiary, s.8 company)",
        "cin": "",
        "status": "Active SRO-body (insolvency; IBBI/IPA/16-17/01)",
        "accent": "#7c3aed",
        "consumer": [
            "One of three IBBI-registered insolvency professional agencies — the bodies that license and police the professionals running <strong>Corporate Insolvency Resolution Processes</strong> when companies you have deposits, jobs or dues with go under.",
            "First of the three agencies registered (2016-17); the ICAI's section-8 subsidiary.",
            "Its members decide how creditor money is marshalled in every big NCLT case.",
        ],
        "watch": [
            "<strong>No public member roster on its site</strong> — the register sits inside IBBI's IP database and member areas.",
            "IP disciplinary statistics are thin; IBBI's annual reports carry the enforcement numbers.",
        ],
    },
    "icsiip": {
        "regulator": "IBBI",
        "abbr": "ICSI IIP", "name": "ICSI Institute of Insolvency Professionals",
        "sector": "Insolvency professionals (IPA, reg. IBBI/IPA/16-17/02)",
        "order": "—", "recognised": "2016-17",
        "website": "https://www.icsiiip.in",
        "members_site": "",
        "hq": "New Delhi (ICSI subsidiary, s.8 company)",
        "cin": "",
        "status": "Active SRO-body (insolvency; IBBI/IPA/16-17/02)",
        "accent": "#7c3aed",
        "consumer": [
            "The ICSI-run insolvency professional agency — second of the three IBBI-registered bodies that gate and discipline insolvency professionals.",
            "Calls itself a 'frontline regulator' under the Insolvency and Bankruptcy Code, 2016 — self-regulation by statute.",
            "Which agency an IP belongs to decides whose code of conduct governs your insolvency case.",
        ],
        "watch": [
            "<strong>No public member roster</strong> — enrolment lists sit behind its portal.",
            "Watch IBBI orders against its members — that is where its discipline actually shows.",
        ],
    },
    "ipaicmai": {
        "regulator": "IBBI",
        "abbr": "IPA ICMAI", "name": "Insolvency Professional Agency of the Institute of Cost Accountants of India",
        "sector": "Insolvency professionals (IPA, reg. IBBI/IPA/16-17/03)",
        "order": "—", "recognised": "2016-17",
        "website": "https://www.ipaicmai.in",
        "members_site": "",
        "hq": "New Delhi (ICMAI subsidiary, s.8 company)",
        "cin": "",
        "status": "Active SRO-body (insolvency; IBBI/IPA/16-17/03)",
        "accent": "#7c3aed",
        "consumer": [
            "The cost accountants' insolvency professional agency — third of the three IBBI-registered bodies (reg. IBBI/IPA/16-17/03).",
            "Completes the trio: nearly every insolvency professional in India belongs to one of three institute-run agencies.",
            "Three institutes and no independent challenger — concentration worth watching.",
        ],
        "watch": [
            "<strong>No public member roster</strong> — same IBBI-database arrangement as its siblings.",
            "Smallest of the three agencies; check its fee and exam pipeline for capacity red flags.",
        ],
    },
    "amfi": {
        "regulator": "SEBI",
        "abbr": "AMFI", "name": "Association of Mutual Funds in India",
        "sector": "Asset management companies (all SEBI-registered AMCs)",
        "order": "—", "recognised": "— (association, 1995)",
        "website": "https://www.amfiindia.com",
        "members_site": "https://www.amfiindia.com/aboutamfi (Members tab)",
        "hq": "Mumbai (CIN U65991MH1995NPL092062)",
        "cin": "U65991MH1995NPL092062",
        "status": "Industry body — not a recognised SRO",
        "accent": "#78716c",
        "consumer": [
            "Sets the codes your mutual fund operates under — the AMC code of conduct, ARN distributor registration, risk disclosures — without ever being recognised as an SRO.",
            "All 56 AMCs captured here as context: the most consequential self-regulatory body in Indian finance that no regulator ever formally anointed.",
            "Publishes the industry's monthly AUM and SIP data that journalists and regulators quote back at it.",
        ],
        "watch": [
            "SEBI's 2004 SRO regulations and the World Bank's 2007 review both note AMFI was never officially recognised — the ambiguity has now run two decades.",
            "Watch whether SEBI's 2024-25 SRO push for advisers and analysts eventually reaches mutual funds.",
        ],
    },
    "anmi": {
        "regulator": "SEBI",
        "abbr": "ANMI", "name": "Association of National Exchanges Members of India",
        "sector": "Stock brokers (NSE, BSE, MSE trading members)",
        "order": "—", "recognised": "— (association, 1996)",
        "website": "https://anmi.in",
        "members_site": "",
        "hq": "Mumbai (est. 1996)",
        "cin": "",
        "status": "Industry body — not a recognised SRO",
        "accent": "#78716c",
        "consumer": [
            "~900 stock brokers' pan-India association — the voice arguing your broker's regulatory burden up or down — that has <strong>campaigned for formal SRO status</strong> without getting it.",
            "Its members hold the customer funds and margins SEBI keeps tightening rules on; ANMI self-regulates by code, not by recognition.",
            "Context entry: if SEBI ever recognises a brokers' SRO under its 2024-25 framework, ANMI is the likely candidate.",
        ],
        "watch": [
            "ANMI's own press releases say it 'seeks SRO status' — a public record of its non-recognition.",
            "Watch SEBI's brokers-SRO work for a recognition decision that would move ANMI into the tracked register.",
        ],
    },
}


CAPTURE_DATES = {"amfi": "2026-09-26", "lic": "2026-09-26", "gic": "2026-09-26"}


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
    ("timeline.html", "Timeline"),
    ("activity.html", "Activity"),
    ("social.html", "Social"),
    ("blog/index.html", "Blog"),
    ("about.html", "About"),
]


BASE = "https://srotrac.cashlessconsumer.in"
GENERIC_DESC = "Independent tracker of India's financial-sector self-regulatory organisations across RBI, SEBI, IRDAI and IBBI: members, governance, activity, and what they mean for consumers."


def page(title, active, body, extra_head="", desc=None):
    import time
    v = time.strftime("%Y%m%d%H%M")
    # SRO dropdown: single menu holding the register
    is_sro = active.startswith(("sro-", "work-"))
    sro_rows = ""
    for sid, s in SROS.items():
        row_cls = ' class="active"' if active in (f"sro-{sid}.html", f"work-{sid}.html") else ""
        wcls = ' class="dd-work active"' if active == f"work-{sid}.html" else ' class="dd-work"'
        sro_rows += (f'<div class="dd-row"><a href="/sro-{sid}.html"{row_cls}>'
                     f'<span class="dd-abbr" style="--c:{s["accent"]}">{s["abbr"]}</span>'
                     f'<span class="dd-name">{esc(s["name"])}</span></a>'
                     f'<a{wcls} href="/work-{sid}.html">work</a></div>')
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
<meta name="description" content="{esc(desc or GENERIC_DESC)}">
<link rel="canonical" href="{BASE}/{active}">
<meta property="og:site_name" content="SROTrac">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)} — SROTrac">
<meta property="og:description" content="{esc(desc or GENERIC_DESC)}">
<meta property="og:url" content="{BASE}/{active}">
<meta property="og:image" content="{BASE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ededf0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="icon" href='data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="%231d4ed8"/><text x="32" y="46" font-family="Georgia,serif" font-size="38" font-weight="bold" text-anchor="middle" fill="%23faf9f7">S</text></svg>'>
<link rel="stylesheet" href="/css/style.css?v={v}">
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap mast-main">
    <a class="brand" href="/">SRO<span>Trac</span><small>A CashlessConsumer Register</small></a>
    <nav>{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<section class="stack" aria-label="The sousveillance stack">
  <div class="wrap">
    <p class="stack-kicker"><b>The Sousveillance Stack</b> — who writes, borrows and buys the rules</p>
    <div class="stack-row">
      <a href="https://regtrac.cashlessconsumer.in/"><i>Layer 1 · rule-writers</i><b>RegTrac</b><span>India's statutory financial regulators</span><em>live</em></a>
      <a href="/"><i>Layer 2 · rule-borrowers</i><b>SROTrac</b><span>India's financial-sector self-regulatory organisations</span><em class="here">you are here</em></a>
      <a href="https://lobbywatch.cashlessconsumer.in/"><i>Layer 3 · rule-buyers</i><b>LobbyWatch</b><span>consultations, access, revolving doors</span><em>live</em></a>
    </div>
  </div>
</section>
<footer class="site-footer">
  <div class="wrap">
    <p><strong>SROTrac</strong> — an independent CashlessConsumer project tracking India's self-regulatory organisations. Not affiliated with RBI or any SRO.</p>
    <p class="colophon">Layer 2 of the sousveillance stack: <a href="https://regtrac.cashlessconsumer.in/">RegTrac</a> (rule-writers) · SROTrac (rule-borrowers) · <a href="https://lobbywatch.cashlessconsumer.in/">LobbyWatch</a> (rule-buyers).</p>
    <p><a href="https://cashlessconsumer.in">cashlessconsumer.in</a> · data: <a href="https://github.com/CashlessConsumer/srotrac">GitHub</a> · <a href="/about.html">methodology</a></p>
    <p><strong>Data: CC BY 4.0</strong> — copy, remix and republish with attribution to SROTrac / CashlessConsumer. Code: MIT.</p>
    <p class="colophon">Scope: recognised + statutory SROs across RBI, SEBI, IRDAI and IBBI · context: AMFI, ANMI &middot; Agent entry: <a href="/llms.txt">llms.txt</a></p>
  </div>
</footer>
<script src="/js/main.js?v={v}"></script>
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
    home_ld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "name": "SROTrac", "url": BASE + "/",
             "publisher": {"@type": "Organization", "name": "CashlessConsumer", "url": "https://cashlessconsumer.in"}},
            {"@type": "Organization", "name": "SROTrac", "url": BASE + "/",
             "description": "Independent register of India's financial-sector self-regulatory organisations (RBI, SEBI, IRDAI, IBBI).",
             "parentOrganization": {"@type": "Organization", "name": "CashlessConsumer"}},
        ],
    })
    total = len(members)
    both = sum(1 for o in overlap if len(o["sros"]) > 1)
    srofts = sum(1 for s in SROS.values() if "SRO-FT" in s["status"])
    regs = len({s.get("regulator", "—") for s in SROS.values()})
    regs = len({s.get("regulator", "—") for s in SROS.values()})
    counts = defaultdict(int)
    for m in members:
        counts[sid_of(m["sro"])] += 1
    recent = activity[:6]
    cards = ""
    for sid, s in SROS.items():
        cards += f"""
    <a class="sro-card" href="/sro-{sid}.html" style="--c:{s['accent']}" data-abbr="{s['abbr']}">
      <div class="sro-card-head">
      <span class="pill">{esc(s['status'])}</span></div>
      <h3>{esc(s['name'])}</h3>
      <p class="sector">{esc(s['sector'])}</p>
      <p class="meta">{esc(s.get("regulator", "—"))} · {esc(s["recognised"])} · {counts.get(sid, 0)} members</p>
    </a>"""
    items = ""
    for a in recent:
        items += f"""
      <li><span class="date">{a['date']}</span> {sro_badge(a['sro'])}
      <a href="{esc(a['url'])}" rel="noopener">{esc(a['title'])}</a></li>"""
    body = f"""
<section class="hero">
  <div class="wrap">
    <p class="kicker rise">Register of India&rsquo;s financial-sector self-regulatory organisations &middot; RBI &middot; SEBI &middot; IRDAI &middot; IBBI</p>
    <h1 class="rise">Who watches India&rsquo;s fintech <em>watchdogs</em>?</h1>
    <div class="hero-stamps">
      <span class="stamp seal-in">Recognised SROs × {len(SROS)}</span>
      <span class="stamp blue seal-in" style="animation-delay:.45s">{srofts} × SRO-FT</span>
    </div>
    <p class="lede rise">India&rsquo;s regulators outsource first-line supervision to <strong>self-regulatory organisations</strong> — industry bodies empowered to write conduct codes and police their own members. SROTrac tracks who sits on them, what they do, and whether they work for consumers — across <strong>RBI, SEBI, IRDAI and IBBI</strong>, plus the two industry giants (AMFI, ANMI) that self-regulate without ever being recognised.</p>
    <div class="stats rise">
      <div><strong>{len(SROS)}</strong><span>SROs tracked</span></div>
      <div><strong>{regs}</strong><span>regulators</span></div>
      <div><strong>{total}</strong><span>listed member orgs</span></div>
      <div><strong>{both}</strong><span>in 2+ SROs</span></div>
      <div><strong>{srofts}</strong><span>fintech SRO-FTs</span></div>
    </div>
  </div>
</section>
<section class="wrap" id="register">
  <h2>The register</h2>
  <p class="muted small">Sixteen recognised bodies across four regulators, plus two unrecognised associations tracked for context. Click a folder for members, governance and activity.</p>
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
  <div class="notice">
    <p class="kicker">Weekly gazette</p>
    <h2>SROTrac Weekly</h2>
    <p>A weekly digest of what moved in SRO-land — roster changes, consultations,
    enforcement, recognition news — generated from the tracker's own diffs.</p>
    <p><a class="btn" href="/blog/index.html">Read the blog →</a></p>
  </div>
</section>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Dataset","name":"SROTrac","description":"Members, governance and activity of India's financial-sector self-regulatory organisations across RBI, SEBI, IRDAI and IBBI","url":"https://srotrac.cashlessconsumer.in/","creator":{{"@type":"Organization","name":"CashlessConsumer","url":"https://cashlessconsumer.in"}},"license":"https://creativecommons.org/licenses/by/4.0/"}}
</script>
<script type="application/ld+json">{home_ld}</script>"""
    return page("India's fintech SROs, tracked", "", body)

def build_sro(sid, members, activity, leadership, social=None, check=None):
    s = SROS[sid]
    org_ld = json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": s["name"], "alternateName": s["abbr"], "url": s["website"],
        "description": "Self-regulatory organisation for " + s["sector"]
                       + ". Recognition: " + s["recognised"] + " (" + s.get("regulator", "—") + ").",
        "identifier": {"@type": "PropertyValue", "name": "Recognition", "value": s["recognised"]},
    })
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
    ty_counts = defaultdict(int)
    for m in mem:
        ty_counts[classify(m["member_name"])[0]] += 1
    typeline = " · ".join(f"{v} {TYPES[k][0]}" for k, v in sorted(ty_counts.items(), key=lambda x: -x[1])[:4])
    srows = sorted((r for r in (social or []) if sid_of(r["sro"]) == sid),
                   key=lambda r: PLATFORM_ORDER.get(r["platform"], 9))
    if srows:
        social_html = '<div class="acct-row">' + "".join(acct_chip(r) for r in srows) + "</div>"
    else:
        social_html = '<p class="muted">No official social media accounts tracked yet.</p>'
    body = f"""
<section class="sro-hero" style="--c:{s['accent']}">
  <div class="wrap">
    <p class="kicker">{esc(s.get("regulator", "—"))} &middot; SRO register</p>
    <h1>{esc(s['name'])}{'' if s['name'] == s['abbr'] else f' <span class="abbr-chip">{s["abbr"]}</span>'}</h1>
  <p class="work-jump"><a href="/work-{sid}.html">Deep-dive: what {s['abbr']} actually does &rarr;</a></p>
    <p class="lede">{esc(s['sector'])}</p>
    <div class="factbar">
      <div><span>Recognised ({esc(s.get("regulator", "—"))})</span><strong>{esc(s["recognised"])}</strong></div>
      <div><span>Status</span><strong>{esc(s['status'])}</strong></div>
      <div><span>Listed members</span><strong>{len(mem) if mem else 'n/p'}</strong> <em class="muted">({esc(typeline) if typeline else 'no public roster'})</em></div>
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
  <p class="muted small">Captured from {esc(s["members_site"] or "the SRO's published member page")} on {CAPTURE_DATES.get(sid, "2026-09-10")}. Marketing rosters, not filings — see <a href="/about.html">methodology</a>.</p>
</section>
<section class="wrap">
  <h2>Activity</h2>
  <ul class="feed">{act_html if act_html else '<li>No dated public activity captured yet.</li>'}
  </ul>
</section>
<section class="wrap" id="social">
  <h2>Social media</h2>
  {social_html}
  <p class="muted small"><a href="/social.html">Full social media monitor &rarr;</a></p>
</section>
<script type="application/ld+json">{org_ld}</script>"""
    return page(s["abbr"] + " — " + s["name"], f"sro-{sid}.html", body,
                desc=f"{s['name']} ({s['abbr']}), the {s.get('regulator', '—')}-governed self-regulatory body for {s['sector']}. Full member list, governance, activity and gaps — tracked by SROTrac.")


def org_table(members):
    """Group member rows into unique organisations with SRO membership + entity type."""
    accents = {x["abbr"]: x["accent"] for x in SROS.values()}
    abbr_map = {x["abbr"].casefold(): x["abbr"] for x in SROS.values()}
    orgs = {}
    for m in members:
        sro = abbr_map.get(m["sro"].strip().casefold(), m["sro"].strip().upper())
        name = m["member_name"].strip()
        o = orgs.setdefault(name, {"sros": [], "w": ""})
        if sro not in o["sros"]:
            o["sros"].append(sro)
        if not o["w"] and m.get("website"):
            o["w"] = m["website"]
    etype_cache = {}
    payload = []
    for n, o in orgs.items():
        if n not in etype_cache:
            etype_cache[n] = classify(n)
        ty, grp = etype_cache[n]
        payload.append({
            "n": n,
            "s": sorted(o["sros"], key=lambda x: list(SROS_abbr_order()).index(x) if x in SROS_abbr_order() else 99),
            "ty": ty,
            "g": grp,
            "t": TYPES[ty][0],
            "c": {x: accents.get(x, "#6b7280") for x in o["sros"]},
            "w": o["w"],
        })
    payload.sort(key=lambda x: x["n"].lower())
    return payload


def SROS_abbr_order():
    return [s["abbr"] for s in SROS.values()]


def build_members(members, leadership):
    payload = org_table(members)
    ty_counts = defaultdict(int)
    for r in payload:
        ty_counts[r["ty"]] += 1
    type_order = sorted(ty_counts, key=lambda t: (-ty_counts[t], TYPES[t][0]))
    type_chips = "".join(
        f'<button class="chip" data-ty="{esc(t)}">{esc(TYPES[t][0])} ({ty_counts[t]})</button>'
        for t in type_order
    )
    sro_chips = "".join(
        f'<button class="chip" data-sro="{esc(s["abbr"])}">{esc(s["abbr"])}</button>'
        for s in SROS.values() if s["abbr"] in {r for p in payload for r in p["s"]}
    )
    abbrs = SROS_abbr_order()
    matrix = {a: {b: 0 for b in abbrs} for a in abbrs}
    for r in payload:
        for x in r["s"]:
            for b in r["s"]:
                matrix[x][b] += 1
    mrows = ""
    for a in abbrs:
        cells = ""
        for b in abbrs:
            v = matrix[a][b]
            if a == b:
                cells += f'<td class="mx-self">{v}</td>'
            else:
                link = f"#sro={a.lower()},{b.lower()}&multi=1" if v else ""
                cells += (f'<td class="mx-cell{" mx-hot" if v else ""}">'
                          + (f'<a href="{link}">{v}</a>' if v else "&middot;") + "</td>")
        mrows += f'<tr><th class="mx-row">{esc(a)}</th>{cells}</tr>'
    head = "<tr><th></th>" + "".join(f'<th class="mx-col">{esc(b)}</th>' for b in abbrs) + "</tr>"
    multi = [r for r in payload if len(r["s"]) > 1]
    rows = ""
    for r in multi:
        badges = "".join(sro_badge(x.lower()) for x in r["s"])
        ty = f'<span class="pill small">{esc(TYPES[r["ty"]][0])}</span>'
        rows += f"<tr><td>{esc(r['n'])}</td><td>{ty}</td><td>{badges}</td></tr>"
    people = defaultdict(set)
    for l in leadership:
        key = l["name"].lower().replace("mr. ", "").replace("ms. ", "").replace("dr. ", "").strip()
        people[key].add((l["sro"], l["name"], l["role"]))
    prows = ""
    for key, entries in sorted(people.items()):
        sros = {e[0] for e in entries}
        if len(sros) > 1:
            detail = "; ".join(f"{e[0]}: {e[2]}" for e in sorted(entries))
            prows += f"<tr><td>{esc(next(iter(entries))[1])}</td><td>{esc(detail)}</td></tr>"
    body = f"""
<section class="hero slim">
  <div class="wrap">
    <h1>All members</h1>
    <p class="lede">{len(payload)} organisations across the thirteen published rosters (FIDC, Sa-Dhan, BASL, AIBI and the three insolvency agencies publish none). One row per organisation — SRO badges show every register it appears in. Filter by SRO, entity type, or search by name. Cross-SRO membership overlap is <a href="#overlap">below the table</a>.</p>
  </div>
</section>
<section class="wrap">
  <div class="filters">
    <input id="mq" type="search" placeholder="Search organisation…" autocomplete="off">
    <div class="chips" id="srochips">
      <span class="chip-label">SRO</span>
      <button class="chip active" data-sro="ALL">All</button>
      {sro_chips}
      <button class="chip" data-sro="MULTI">In 2+ SROs</button>
    </div>
    <div class="chips" id="typechips">
      <span class="chip-label">Type</span>
      <button class="chip active" data-ty="ALL">All</button>
      {type_chips}
    </div>
  </div>
  <p class="muted small" id="mcount"></p>
  <div class="table-scroll">
  <table class="listing" id="mtable">
    <thead><tr><th>Organisation</th><th>Entity type</th><th>SROs</th><th>Website</th></tr></thead>
    <tbody id="mrows"></tbody>
  </table>
  </div>
  <noscript><p>Enable JavaScript to browse the interactive table, or grab the raw CSVs on GitHub.</p></noscript>
</section>

<section class="wrap" id="overlap">
  <h2>Shared members matrix</h2>
  <p class="muted small">Each cell counts organisations registered with <em>both</em> the row and column SRO. Click a cell to open those organisations in the members table.</p>
  <div class="table-scroll">
  <table class="listing matrix"><thead>{head}</thead><tbody>{mrows}</tbody></table>
  </div>
</section>
<section class="wrap">
  <h2>Organisations in 2+ SROs ({len(multi)})</h2>
  <div class="table-scroll">
  <table class="listing"><thead><tr><th>Organisation</th><th>Type</th><th>SROs</th></tr></thead><tbody>{rows}</tbody></table>
  </div>
</section>
<section class="wrap">
  <h2>People in 2+ SROs</h2>
  <table class="listing"><thead><tr><th>Person</th><th>Roles</th></tr></thead><tbody>{prows if prows else '<tr><td colspan="2">None found in published leadership data.</td></tr>'}</tbody></table>
  <div class="callout">
    <p><strong>Why this matters:</strong> the omnibus SRO framework requires SROs to avoid conflicts of interest. Shared directors and EC members across SROs are legal — but when the same fintech executives shape conduct rules at multiple bodies, consumers should know whose interests get harmonised first.</p>
  </div>
</section>
<script id="member-data" type="application/json">{json.dumps(payload)}</script>"""
    return page("Members", "members.html", body)


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


PLATFORM_LABEL = {"x": "X (Twitter)", "linkedin": "LinkedIn", "youtube": "YouTube",
                  "facebook": "Facebook", "instagram": "Instagram"}
PLATFORM_ORDER = {k: i for i, k in enumerate(["x", "linkedin", "youtube", "facebook", "instagram"])}


def acct_chip(r):
    label = PLATFORM_LABEL.get(r["platform"], r["platform"].title())
    accent = SROS.get(sid_of(r["sro"]), {}).get("accent", "#57534e")
    if r.get("source") == "official site":
        mark = '<span class="ok" title="Linked from the SRO\'s own website">&#10003;</span>'
    else:
        mark = '<span class="ann" title="Verified via the SRO\'s own announcement or platform search">&#9998;</span>'
    tip = esc(r.get("notes") or "")
    title = f' title="{tip}"' if tip else ""
    return (f'<a class="acct" href="{esc(r["url"])}" rel="noopener" style="--c:{accent}"{title}>'
            f'<span class="pf">{esc(label)}</span>'
            f'<span class="hd">{mark} {esc(r["handle"])}</span></a>')


def build_social(social, check):
    by_sro = defaultdict(list)
    for r in social:
        sid = sid_of(r["sro"])
        if sid:
            by_sro[sid].append(r)
    for rows in by_sro.values():
        rows.sort(key=lambda r: PLATFORM_ORDER.get(r["platform"], 9))

    total = len(social)
    n_x = sum(1 for r in social if r["platform"] == "x")
    with_x = sum(1 for sid in SROS if any(r["platform"] == "x" for r in by_sro.get(sid, [])))
    li_only = sum(1 for sid in SROS if by_sro.get(sid)
                  and all(r["platform"] == "linkedin" for r in by_sro[sid]))

    cards = ""
    for sid, s in SROS.items():
        rows = by_sro.get(sid, [])
        chips = "".join(acct_chip(r) for r in rows)
        absent = ""
        if rows:
            have = {r["platform"] for r in rows}
            bits = (["No X account"] if "x" not in have else []) + (["No YouTube"] if "youtube" not in have else [])
            if bits:
                absent = f'<p class="absent">{" &middot; ".join(bits)}</p>'
        else:
            chips = '<p class="muted small">No official accounts found.</p>'
        cards += f"""
    <div class="acct-card" style="--c:{s['accent']}">
      <h3><a href="/sro-{sid}.html" style="color:inherit;text-decoration:none">{esc(s['abbr'])}</a></h3>
      <p class="sector muted small">{esc(s['name'])}</p>
      {chips}
      {absent}
    </div>"""

    if check and check.get("official_site_accounts"):
        miss = check.get("missing_from_site") or []
        drift = (f"Last drift check {esc(check.get('checked', '?'))}: "
                 f"{check.get('still_linked', 0)}/{check.get('official_site_accounts', 0)} "
                 "official-site links still live.")
        if miss:
            drift += f' <strong style="color:#b42318">&#9888; No longer linked: {esc(", ".join(miss))}</strong>'
    else:
        drift = "Drift check has not run yet."

    body = f"""
<section class="hero">
  <div class="wrap">
    <p class="kicker rise">Social media monitor &middot; tracked SROs</p>
    <h1 class="rise">Where the SROs <em>post</em></h1>
    <p class="lede rise">Codes of conduct, consultation responses and discipline machinery often surface first on an SRO&rsquo;s own channels &mdash; usually LinkedIn, sometimes X. This page tracks every official account of the tracked SROs, and the daily refresh re-checks each one against the SRO&rsquo;s own website. <strong>&#10003;</strong> = still linked from the SRO&rsquo;s site today &middot; <strong>&#9998;</strong> = verified via the SRO&rsquo;s own announcement or platform search.</p>
    <div class="stats rise">
      <div><strong>{total}</strong><span>official accounts tracked</span></div>
      <div><strong>{n_x}</strong><span>handles on X (Twitter)</span></div>
      <div><strong>{with_x} of {len(SROS)}</strong><span>SROs reachable on X</span></div>
      <div><strong>{li_only}</strong><span>LinkedIn-only &mdash; no public feed</span></div>
    </div>
  </div>
</section>
<section class="wrap" id="accounts">
  <h2>The accounts</h2>
  <p class="muted small">Nine cards, one per SRO. Hover a handle for notes; click through to follow.</p>
  <div class="acct-grid">{cards}
  </div>
</section>
<section class="wrap">
  <div class="callout">
    <h2>How this is monitored</h2>
    <ul class="ticks">
      <li>The daily refresh re-fetches the SROs&rsquo; own pages, then a drift check (<code>scripts/social_check.py</code>) confirms every &#10003;-marked account is still linked from its official site. {drift}</li>
      <li>X, LinkedIn, Facebook and Instagram block robots, so follower counts and post contents are not scraped here &mdash; links are curated, dated (verified 2026-09-25) and re-verified in the direction platforms can&rsquo;t block: the SRO&rsquo;s own website.</li>
      <li>A handle vanishing from an official site is the cheapest early signal of a rebrand, a takeover or a quietly deleted account &mdash; it shows here as a &#9888; flag.</li>
      <li>Spotted a new or dead handle? It&rsquo;s a one-row fix in <a href="https://github.com/CashlessConsumer/srotrac">data/social.csv</a> (CC BY 4.0).</li>
    </ul>
  </div>
</section>"""
    return page("Social media monitor", "social.html", body,
                desc="Every official social media account of India's tracked financial-sector SROs "
                     "(FACE, UFF, FIDC, SRPA, MFIN, Sa-Dhan, FEDAI, Sahamati, FIMMDA) on X, LinkedIn, "
                     "YouTube, Facebook and Instagram — with a daily drift check against the SROs' own websites.")


def build_work(sid):
    w = WORK[sid]
    s = SROS[sid]
    org_ld = json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": s["name"], "alternateName": s["abbr"], "url": s["website"],
        "description": w["tagline"],
        "identifier": {"@type": "PropertyValue", "name": "RBI SRO recognition", "value": s["recognised"]},
    })
    secs = ""
    for sec in w["sections"]:
        body = ""
        if "prose" in sec:
            body += f'<p>{esc(sec["prose"])}</p>'
        for it in sec.get("items", []):
            body += f'<li>{esc(it)}</li>'
        items = f'<ul class="ticks">{body}</ul>' if sec.get("items") else ""
        secs += f'<section class="work-sec"><h2>{esc(sec["h"])}</h2>{body if not sec.get("items") else ""}{items}</section>'
    gaps = "".join(f"<li>{esc(g)}</li>" for g in w["gaps"])
    srcs = "".join(f'<li><a href="{esc(u)}" rel="noopener">{esc(t)}</a></li>' for t, u in w["sources"])
    body = f"""
<section class="hero slim"><div class="wrap">
  <p class="kicker">What {s['abbr']} actually does</p>
  <h1>{esc(s['name'])} <span class="abbr-chip">{s['abbr']}</span></h1>
  <p class="lede">{esc(w['tagline'])}</p>
</div></section>
<section class="wrap">
  <p class="work-summary">{esc(w['summary'])}</p>
  {secs}
  <section class="work-sec"><h2>Gaps &amp; open questions</h2><ul class="watchlist">{gaps}</ul></section>
  <section class="work-sec"><h2>Sources</h2><ul class="srcs">{srcs}</ul>
  <p class="meta">Captured 2026-09-10&ndash;11 from {s['abbr']}&rsquo;s own site. Deep-dive under <a href="/about.html">methodology</a> &middot; <a href="/sro-{sid}.html">&larr; register entry</a></p></section>
</section>
<script type="application/ld+json">{org_ld}</script>"""
    return page(f"{s['abbr']} — work", f"work-{sid}.html", body,
                desc=w["tagline"] + " — what " + s["abbr"] + " does for its members and consumers, tracked by SROTrac.")


def build_about(members, activity):
    faq = [
        ("Which SROs does India have?",
         "The Reserve Bank of India has recognised nine self-regulatory organisations: FACE and UFF for fintech (SRO-FT framework), FIDC for NBFCs, SRPA for payment system operators, MFIN and Sa-Dhan for microfinance lenders, FEDAI for authorised dealers in foreign exchange, Sahamati for the account aggregator ecosystem, and FIMMDA for the fixed income, money market and derivatives markets."),
        ("Does SROTrac cover SEBI or IRDAI industry bodies?",
         "No. SROTrac tracks only RBI-recognised SROs. Bodies like AMFI (mutual funds) or the Insurance Institute are recognised by other regulators and are out of scope."),
        ("Is SROTrac affiliated with the RBI or any SRO?",
         "No. SROTrac is an independent project by CashlessConsumer, a consumer collective. It uses only publicly available sources: SRO websites, RBI press releases and dated news reports."),
        ("Is Sahamati recognised by the RBI?",
         "Yes. RBI recognised Sahamati as the SRO for the account aggregator (AA) ecosystem on 5 June 2026. Before recognition, Sahamati spent five years as the AA ecosystem's non-profit standards body (spun out of iSPIRT's work). Its directory lists 110 regulated entities across AAs, FIPs, FIUs and TSPs."),
        ("How many members do the SROs have?",
         "As of the latest capture: FACE 85, UFF 121, SRPA 18, MFIN 84, FEDAI 108, Sahamati 110, FIMMDA 116, AMFI 56, GI Council 49 and LI Council 27 listed members — 774 rows across the 18 tracked bodies. FIDC, Sa-Dhan, BASL, AIBI and the three IBBI IPAs publish no public roster. Counts are floors, not filings: SRO member pages are marketing pages."),
        ("Can I reuse the data?",
         "Yes. Data is licensed CC BY 4.0 — copy, remix and republish with attribution to SROTrac / CashlessConsumer. The CSVs are linked on the members page and in the GitHub repo."),
    ]
    faq_html = "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in faq)
    faq_ld = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq],
    }, ensure_ascii=False)
    body = f"""
<section class="hero slim"><div class="wrap">
  <h1>About SROTrac</h1>
  <p class="lede">An independent, open-data register of India's <strong>RBI-recognised</strong> self-regulatory organisations — built by CashlessConsumer, a consumer collective working on digital payments and fintech. Licensed <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> (data) and MIT (code).</p>
</div></section>
<section class="wrap"><div class="callout">
    <h2>Scope: RBI&rsquo;s SROs only</h2>
    <p>India has several self-regulatory bodies across financial regulators. SROTrac tracks only the nine recognised by the <strong>Reserve Bank of India</strong>: the two SRO-FTs (FACE, UFF), FIDC (NBFCs), SRPA (payment operators), MFIN and Sa-Dhan (microfinance), FEDAI (authorised dealers), Sahamati (Account Aggregator ecosystem), and FIMMDA (fixed income, money market and derivatives). Bodies under other regulators — e.g. AMFI and IIFL under SEBI, the Insurance Institute under IRDAI — are not covered here, however senior their profiles.</p>
  </div></section>
<section class="wrap">
  </section>
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
<section class="wrap" id="faq">
  <h2>FAQ</h2>
  {faq_html}
</section>
<script type="application/ld+json">{faq_ld}</script>
<section class="wrap">
  <h2>License &amp; reuse</h2>
  <p>Code: MIT. Data: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> — copy, remix and republish with attribution to SROTrac / CashlessConsumer.</p>
  <h2>Related CashlessConsumer properties</h2>
  <ul>
    <li><a href="https://cyber.cashlessconsumer.in">cyber.cashlessconsumer.in</a> — security investigations hub</li>
    <li><a href="https://cashlessconsumer.in">cashlessconsumer.in</a> — fintech newsletter &amp; research</li>
  </ul>
</section>"""
    return page("About", "about.html", body,
                desc="What SROTrac covers (recognised SROs across RBI, SEBI, IRDAI and IBBI), how the data is built, caveats, FAQ, and CC BY 4.0 licensing. An independent CashlessConsumer project.")


CSS = """:root{
  --paper:#ededf0; --paper-deep:#e2e3e7; --paper-hi:#f8f8fa; --card:#fbfbfc;
  --ink:#191b20; --ink-soft:#41454e; --faded:#6f747f;
  --rule:#c6c9cf; --rule-soft:#dbdde1;
  --seal:#1d4ed8; --seal-soft:#5b7cd6;
  --gold:#5c6470;
  --accent:#1d4ed8;
  --mono:'IBM Plex Mono',ui-monospace,'Courier New',monospace;
  --serif:'Fraunces',Georgia,'Times New Roman',serif;
  --text:'Newsreader',Georgia,serif;
}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{
  margin:0;font:17px/1.65 var(--text);color:var(--ink);background:var(--paper);
  background-image:repeating-linear-gradient(0deg,transparent 0 31px,rgba(90,95,112,.06) 31px 32px);
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
.site-header::before{content:"";display:block;height:3px;border-top:2px double var(--seal);border-bottom:1px solid var(--seal)}
.site-header .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:42px;flex-wrap:wrap;padding-top:3px;padding-bottom:3px}
.brand{font-family:var(--serif);font-weight:800;font-size:1.12rem;color:var(--ink);text-decoration:none;letter-spacing:-.02em;line-height:1;display:flex;align-items:baseline;gap:.6rem}
.brand em{font-style:normal;color:var(--seal)}
.brand small{font-family:var(--mono);font-weight:400;font-size:.56rem;letter-spacing:.14em;text-transform:uppercase;color:var(--faded);border-left:1px solid var(--rule);padding-left:.55rem}
nav{display:flex;gap:1px;flex-wrap:wrap}
nav a{font-family:var(--mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);text-decoration:none;padding:5px 8px;border-bottom:2px solid transparent}
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
.nav-drop .trigger{font-family:var(--mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-soft);text-decoration:none;padding:5px 8px;border-bottom:2px solid transparent;
  display:inline-flex;align-items:center;gap:.35rem;cursor:pointer;white-space:nowrap}
.nav-drop .trigger:hover{color:var(--seal);border-bottom-color:var(--rule)}
.nav-drop .trigger.active{color:var(--paper-hi);background:var(--seal);border-bottom-color:var(--ink)}
.nav-drop .trigger.active:hover{border-bottom-color:var(--ink)}
.nav-drop .caret{font-size:.55rem;transition:transform .18s}
.dd-panel{display:none;position:absolute;top:100%;right:0;width:min(430px,calc(100vw - 16px));
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
.dd-name{font-family:var(--serif);font-size:.9rem;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}
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
.sro-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px;margin:2.4rem 0 2rem}
.sro-card{--c:var(--seal);position:relative;display:block;background:var(--card);border:1px solid var(--rule);border-top:none;
  padding:1.15rem 1.1rem .95rem;margin-top:14px;text-decoration:none;color:var(--ink);
  box-shadow:0 1px 0 var(--rule);transition:transform .18s cubic-bezier(.2,.7,.3,1),box-shadow .18s}
.sro-card::before{content:attr(data-abbr);position:absolute;top:-14px;left:10px;font-family:var(--mono);font-size:.66rem;font-weight:600;letter-spacing:.14em;
  background:color-mix(in srgb,var(--c) 16%,var(--card));color:var(--c);border:1px solid var(--rule);border-bottom:none;padding:.22em .8em .5em}
.sro-card::after{content:"";position:absolute;top:-1px;right:-1px;width:20px;height:20px;
  background:linear-gradient(225deg,var(--paper) 50%,transparent 50%);border-left:1px solid var(--rule)}
.sro-card:hover{transform:translateY(-5px);box-shadow:0 10px 22px rgba(60,45,20,.18)}
.sro-card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-top:.2rem}
.sro-card h3{margin:.4rem 0 .25rem;font-size:1.02rem;font-weight:600}
.pill{display:inline-block;font-family:var(--mono);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-soft);border:1px solid var(--rule);background:var(--paper-hi);padding:2px 8px;border-radius:2px;white-space:normal;overflow-wrap:anywhere}
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
.post-card h2,.post-card h3{font-size:1.15rem;margin:.4em 0;border:none}
.post-card h2::after{display:none}
.post-card h3 a,.post-card h2 a{color:var(--ink);text-decoration:none}
.post-card h3 a:hover,.post-card h2 a:hover{color:var(--seal)}
.post-card .date{display:block;margin-bottom:.2rem}
.page-head{margin:2.4rem 0 .4rem}
.page-head h1{margin-bottom:.15em}
.post-full{max-width:46rem;margin:0 auto}
.post-full h2{font-size:1.3rem}
.post-full table{display:block;border-collapse:collapse;width:100%;margin:14px 0;font-size:.88rem;overflow-x:auto}
.post-full th,.post-full td{border:1px solid var(--rule);padding:6px 9px;text-align:left}
.post-full th{background:var(--paper-hi);font-family:var(--mono);font-size:.78rem}
.post-full blockquote{border-left:3px solid var(--seal);margin:12px 0;padding:4px 14px;color:var(--ink-soft);background:var(--paper-hi)}
.post-full code{background:var(--paper-deep);padding:1px 5px;border-radius:4px;font-size:.86em}
.post-full pre{background:var(--paper-hi);border:1px solid var(--rule);padding:12px 14px;overflow-x:auto}
.post-full pre code{background:none;padding:0}

/* ---------- sousveillance stack band ---------- */
.stack{border-top:1px solid var(--rule);background:var(--paper)}
.stack .wrap{padding-top:1.3rem;padding-bottom:1.3rem}
.stack-kicker{font-family:var(--mono);font-size:.62rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--faded);margin:0 0 .8rem}
.stack-kicker b{color:var(--seal)}
.stack-row{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--rule);border:1px solid var(--ink)}
.stack-row>*{background:var(--paper-hi);padding:.7rem .9rem .8rem;display:block}
.stack-row a{text-decoration:none}
.stack-row i{display:block;font-family:var(--mono);font-style:normal;font-size:.56rem;letter-spacing:.14em;text-transform:uppercase;color:var(--faded)}
.stack-row b{display:block;font-family:var(--serif);font-weight:800;font-size:1rem;color:var(--ink);margin:.12rem 0 .05rem;letter-spacing:-.01em}
.stack-row span{display:block;font-size:.76rem;color:var(--ink-soft);line-height:1.45}
.stack-row em{display:inline-block;font-family:var(--mono);font-style:normal;font-size:.55rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--seal);border:1px solid var(--seal);border-radius:2px;padding:2px 7px;margin-top:.5rem}
.stack-row a:hover b{color:var(--seal)}
.stack-row em.here{background:var(--seal);color:var(--paper-hi)}
.stack-row .planned{background:var(--paper-deep)}
.stack-row .planned b{color:var(--faded)}
.stack-row .planned em{color:var(--faded);border-color:var(--faded)}
@media(max-width:640px){
  .stack-row{grid-template-columns:1fr}
  .stack-row>*{padding:.6rem .8rem .7rem}
}

/* ---------- footer ---------- */
.site-footer{border-top:1px solid var(--ink);background:var(--paper-deep);padding:1.8rem 0;color:var(--ink-soft);font-size:.88rem;position:relative}
.site-footer::before{content:"";position:absolute;top:4px;left:0;right:0;border-top:1px solid var(--rule)}
.site-footer p{margin:.35rem 0}
.dd-row{display:flex;align-items:center;gap:10px;justify-content:space-between}
.dd-row>a:first-child{flex:1;min-width:0}
.dd-work{font-family:var(--mono);font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--faded);border:1px solid var(--rule);padding:3px 8px;border-radius:2px;white-space:nowrap}
.dd-row:hover .dd-work{color:var(--seal);border-color:var(--seal)}
.work-jump{margin:-.4rem 0 1.6rem}
.work-jump a{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;border-bottom:1px solid var(--seal)}
.work-summary{font-size:1.05rem;max-width:52rem;border-left:3px solid var(--seal);padding-left:14px;margin:0 0 1.8rem;color:var(--ink-soft)}
.work-sec{margin:0 0 2rem}
.work-sec h2{font-size:1.05rem;margin-bottom:.7rem}
.srcs{font-size:.86rem;color:var(--muted)}
.srcs a{word-break:break-all}
.site-footer .colophon{font-family:var(--mono);font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--faded)}
@media print{body::after{display:none}.site-header{position:static}}
/* ---------- mobile + wide tables ---------- */
.table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.table-scroll table.listing,.table-scroll .people{min-width:640px}
@media(max-width:700px){
  body{font-size:16px}
  .hero{padding:2.6rem 0 1.8rem}
  .stats{grid-template-columns:1fr 1fr}
  .factbar{grid-template-columns:1fr 1fr}
  .factbar div{border-right:1px solid var(--rule-soft)}
  .factbar div:nth-child(2n){border-right:none}
  nav a{padding:10px 12px}
  .sro-grid{grid-template-columns:1fr 1fr;gap:14px}
}
@media(max-width:460px){.sro-grid{grid-template-columns:1fr}}
/* ---------- social monitor ---------- */
.acct-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px;margin:0}
.acct-card{background:var(--card);border:1px solid var(--rule);border-top:3px solid var(--c);padding:16px 16px 12px}
.acct-card h3{margin:.1rem 0 .15rem;font-size:1.02rem;font-weight:700}
.acct{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:7px 9px;border:1px solid var(--rule-soft);margin-bottom:6px;text-decoration:none}
.acct:hover{background:color-mix(in srgb,var(--c) 8%,var(--card));text-decoration:none}
.acct .pf{font-family:var(--mono);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);white-space:nowrap}
.acct .hd{font-weight:600;font-size:.82rem;text-align:right;word-break:break-word}
.acct .ok{color:#1a7f37;font-weight:700}
.acct .ann{color:#9a6700;font-weight:700}
.absent{font-family:var(--mono);font-size:.62rem;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-soft);margin:.4rem 0 0}
.acct-row{display:flex;flex-wrap:wrap;gap:8px}
.acct-row .acct{margin-bottom:0}
@media(max-width:700px){.acct-row .acct{width:100%}}
"""

JS = r"""/// SROTrac: nav helpers + members/activity filtering
var SRO_KEYS = ["FACE", "UFF", "FIDC", "SRPA", "MFIN", "Sa-Dhan", "FEDAI", "Sahamati"];
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

  // Members page: org-grouped rows, multi-select SRO + type chips, URL-hash state
  var dataEl = document.getElementById('member-data');
  if (dataEl){
    var members = JSON.parse(dataEl.textContent);
    var rowsEl = document.getElementById('mrows');
    var countEl = document.getElementById('mcount');
    var q = '', sroSel = new Set(), tySel = new Set(), multi = false;

    function parseHash(){
      var h = location.hash.replace(/^#/, '');
      if (!h){ q=''; sroSel.clear(); tySel.clear(); multi=false; return; }
      var parts = {};
      h.split('&').forEach(function(kv){ var p = kv.split('='); parts[p[0]] = decodeURIComponent(p[1]||''); });
      q = parts.q || '';
      sroSel = new Set((parts.sro||'').split(',').filter(Boolean).map(function(v){
        var k = v.toLowerCase();
        var hit = SRO_KEYS.filter(function(K){ return K.toLowerCase() === k; })[0];
        return hit || v;
      }));
      tySel = new Set((parts.ty||'').split(',').filter(Boolean));
      multi = parts.multi === '1';
      var iq = document.getElementById('mq'); if (iq) iq.value = q;
    }
    function writeHash(){
      var h = [];
      if (q) h.push('q='+encodeURIComponent(q));
      if (sroSel.size) h.push('sro='+Array.from(sroSel).join(','));
      if (tySel.size) h.push('ty='+Array.from(tySel).join(','));
      if (multi) h.push('multi=1');
      var newHash = h.length ? '#'+h.join('&') : '';
      if (location.hash !== newHash) history.replaceState(null, '', location.pathname + newHash);
    }
    function syncChips(){
      document.querySelectorAll('#srochips .chip').forEach(function(c){
        var v = c.dataset.sro;
        c.classList.toggle('active',
          v === 'MULTI' ? multi : (v === 'ALL' ? sroSel.size===0 && !multi : sroSel.has(v)));
      });
      document.querySelectorAll('#typechips .chip').forEach(function(c){
        var v = c.dataset.ty;
        c.classList.toggle('active', v === 'ALL' ? tySel.size===0 : tySel.has(v));
      });
    }
    function match(m){
      if (multi && m.s.length < 2) return false;
      if (sroSel.size && !m.s.some(function(x){ return sroSel.has(x) || sroSel.has(x.toLowerCase()); })) return false;
      if (tySel.size && !tySel.has(m.ty)) return false;
      if (q && m.n.toLowerCase().indexOf(q.toLowerCase()) === -1) return false;
      return true;
    }
    function render(){
      var out = '', shown = 0;
      members.forEach(function(m){
        if (!match(m)) return;
        shown++;
        var badges = m.s.map(function(x){
          return '<a class="badge" style="--c:'+(m.c[x]||'#57534e')+'" href="/sro-'+x.toLowerCase().replace(' ','-')+'.html">'+x+'</a>';
        }).join(' ');
        var link = m.w ? '<a href="'+m.w+'" rel="noopener">'+m.w.replace(/^https?:\/\//,'')+'</a>' : '<span class="muted">—</span>';
        out += '<tr><td>'+m.n+'</td><td><span class="pill small">'+m.t+'</span></td><td>'+badges+'</td><td class="linkcell">'+link+'</td></tr>';
      });
      rowsEl.innerHTML = out || '<tr><td colspan="4">No matches.</td></tr>';
      countEl.textContent = shown + ' of ' + members.length + ' organisations shown';
    }
    document.getElementById('mq').addEventListener('input', function(e){ q = e.target.value; writeHash(); render(); });
    document.querySelector('#srochips').addEventListener('click', function(e){
      var b = e.target.closest('.chip'); if (!b) return;
      var v = b.dataset.sro;
      if (v === 'ALL'){ sroSel.clear(); multi = false; }
      else if (v === 'MULTI'){ multi = !multi; }
      else { sroSel.has(v) ? sroSel.delete(v) : sroSel.add(v); }
      writeHash(); syncChips(); render();
    });
    document.querySelector('#typechips').addEventListener('click', function(e){
      var b = e.target.closest('.chip'); if (!b) return;
      var v = b.dataset.ty;
      if (v === 'ALL'){ tySel.clear(); }
      else { tySel.has(v) ? tySel.delete(v) : tySel.add(v); }
      writeHash(); syncChips(); render();
    });
    window.addEventListener('hashchange', function(){ parseHash(); syncChips(); render(); });
    parseHash(); syncChips(); render();
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
          ? '<a class="badge" href="/sro-'+sl.replace(/\s+/g,'-')+'.html">'+a.s+'</a>'
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


def strip_html(h):
    h = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    h = re.sub(r"<style.*?</style>", "", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    h = re.sub(r"&nbsp;", " ", h)
    h = re.sub(r"[ \t]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n\n", h).strip()


def write_agent_files(members, outputs):
    """robots.txt, sitemap.xml, llms.txt, llms-full.txt (SEO/AEO/agent layer)."""
    root = ROOT
    today = date.today().isoformat()

    # --- robots.txt: everyone + AI crawlers explicitly allowed ---
    robots = "User-agent: *\nAllow: /\n\n"
    for bot in ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-Web",
                "anthropic-ai", "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot"]:
        robots += f"User-agent: {bot}\nAllow: /\n\n"
    robots += f"Sitemap: {BASE}/sitemap.xml\n"
    with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    # --- sitemap.xml ---
    core = [("members.html", "0.9", "daily"),
            ("activity.html", "0.8", "daily"), ("social.html", "0.8", "daily"),
            ("timeline.html", "0.7", "weekly"),
            ("about.html", "0.6", "monthly")]
    entries = [("", "1.0", "daily")] + core
    for sid in SROS:
        entries.append((f"sro-{sid}.html", "0.9", "daily"))
        entries.append((f"work-{sid}.html", "0.8", "weekly"))
    entries.append(("blog/index.html", "0.7", "weekly"))
    blog_dir = os.path.join(root, "blog", "posts")
    if os.path.isdir(blog_dir):
        for fn in sorted(os.listdir(blog_dir)):
            if fn.endswith(".md"):
                entries.append((f"blog/{fn[:-3]}.html", "0.7", "weekly"))
    urls = []
    for path, pri, freq in entries:
        loc = BASE + "/" if not path else f"{BASE}/{path}"
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
                    f"<changefreq>{freq}</changefreq><priority>{pri}</priority></url>")
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sm)

    # --- llms.txt (llmstxt.org) ---
    reg = []
    for sid, s in SROS.items():
        n = sum(1 for m in members if sid_of(m["sro"]) == sid)
        roster = "no published roster" if n == 0 else f"{n} listed members"
        reg.append(f"- [{s['abbr']}]({BASE}/sro-{sid}.html): {s['name']} — RBI recognition {s['recognised']}; {roster}.")
    dives = [f"- [{s['abbr']} work]({BASE}/work-{sid}.html): {WORK[sid]['tagline']}" for sid, s in SROS.items()]
    datasets = sorted(fn for fn in os.listdir(os.path.join(root, "data")) if fn.endswith(".csv"))
    ds = "\n".join(f"- [{fn}]({BASE}/data/{fn})" for fn in datasets)
    llms = f"""# SROTrac — India's self-regulatory organisations, tracked

> Independent register of India's self-regulatory organisations across four regulators: RBI (FACE, UFF, FIDC, SRPA, MFIN, Sa-Dhan, FEDAI, Sahamati, FIMMDA), SEBI (BASL for investment advisers/research analysts, AIBI for investment bankers; AMFI and ANMI tracked as unrecognised context), IRDAI (Life Insurance Council, General Insurance Council — statutory councils under the Insurance Act 1938 s.64C), and IBBI (the three insolvency professional agencies: IIIPI of ICAI, ICSI IIP, IPA of ICMAI). Tracks member rosters, governance, activity and enforcement gaps from a consumer-protection lens. Run by CashlessConsumer. Scope: recognised and statutory SROs of RBI, SEBI, IRDAI and IBBI (18 entries; AMFI and ANMI flagged as unrecognised context). Data CC BY 4.0.

Base URL: {BASE}

## Register
{chr(10).join(reg)}

## Deep dives (what each SRO actually does)
{chr(10).join(dives)}

## Cross-cutting pages
- [All members]({BASE}/members.html): searchable 642-row roster with per-SRO filters.
- [Members]({BASE}/members.html): filterable register of all listed entities; includes the cross-SRO overlap matrix and 2+ SRO memberships.
- [Timeline]({BASE}/timeline.html): 2020–2026 regulatory milestones (frameworks, recognitions, consultations).
- [Activity]({BASE}/activity.html): dated log of SRO/RBI developments with sources.
- [Social]({BASE}/social.html): official X/LinkedIn/YouTube/Facebook/Instagram accounts of the nine RBI-recognised SROs (register covers RBI SROs at present), with a daily drift check against their own websites.
- [About & methodology]({BASE}/about.html): scope, method, caveats, FAQ.
- [Blog]({BASE}/blog/index.html): weekly summaries.

## Datasets (CC BY 4.0)
{ds}

## For agents
- Full text of this site: {BASE}/llms-full.txt
- Machine-readable pages: semantic HTML, JSON-LD (Dataset, Organization, FAQPage), canonical URLs.
"""
    with open(os.path.join(root, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(llms)

    # --- llms-full.txt: text of every page + blog posts raw ---
    pages = []
    for name in ["index.html", "members.html", "timeline.html",
                 "activity.html", "social.html", "about.html"]:
        title = name.replace(".html", "").replace("index", "home")
        h = outputs.get(name, "")
        mstart, mend = h.find("<main"), h.find("</main>")
        body_html = h[mstart:mend] if 0 <= mstart < mend else h
        pages.append((name, title, strip_html(body_html)))
    for sid, s in SROS.items():
        h = outputs.get(f"sro-{sid}.html", "")
        mstart, mend = h.find("<main"), h.find("</main>")
        pages.append((f"sro-{sid}.html", f"{s['abbr']} register entry", strip_html(h[mstart:mend])))
        h = outputs.get(f"work-{sid}.html", "")
        mstart, mend = h.find("<main"), h.find("</main>")
        pages.append((f"work-{sid}.html", f"{s['abbr']} work deep-dive", strip_html(h[mstart:mend])))
    parts = [f"# SROTrac — full text for AI agents\nSource: {BASE} (CC BY 4.0). One section per page."]
    for name, title, text in pages:
        loc = BASE + "/" if name == "index.html" else f"{BASE}/{name}"
        parts.append(f"\n## {title} — {loc}\n{text}")
    blog_dir = os.path.join(root, "blog", "posts")
    if os.path.isdir(blog_dir):
        for fn in sorted(os.listdir(blog_dir)):
            if fn.endswith(".md"):
                md = open(os.path.join(blog_dir, fn), encoding="utf-8").read()
                parts.append(f"\n## Blog post: {fn[:-3]} — {BASE}/blog/{fn[:-3]}.html\n{md}")
    with open(os.path.join(root, "llms-full.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts) + "\n")
    print(f"wrote robots.txt, sitemap.xml ({len(urls)} urls), llms.txt, llms-full.txt ({len(pages)} pages + blog)")


def main():
    members = []
    for sid in SROS:
        members.extend(read_csv(f"{sid}_members.csv"))
    for m in members:
        m["sro"] = m["sro"].upper()
    activity = sorted(read_csv("activity.csv"), key=lambda a: a["date"], reverse=True)
    leadership = read_csv("leadership.csv")
    social = read_csv("social.csv")
    try:
        with open(os.path.join(DATA, "social_check.json"), encoding="utf-8") as f:
            social_check = json.load(f)
    except (OSError, ValueError):
        social_check = None

    orgs = defaultdict(set)
    for m in members:
        orgs[m["member_name"]].add(m["sro"])
    overlap = [{"name": n, "sros": sorted(s)} for n, s in orgs.items()]

    outputs = {
        "index.html": build_home(members, activity, overlap),
        "members.html": build_members(members, leadership),
        "timeline.html": build_timeline(activity),
        "activity.html": build_activity(activity),
        "social.html": build_social(social, social_check),
        "about.html": build_about(members, activity),
    }
    for sid in SROS:
        outputs[f"sro-{sid}.html"] = build_sro(sid, members, activity, leadership, social, social_check)
    for sid in SROS:
        outputs[f"work-{sid}.html"] = build_work(sid)

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

    # overlap.html retired -> redirect stub
    with open(os.path.join(ROOT, "overlap.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<title>Cross-SRO overlap — SROTrac</title>'
                '<link rel="canonical" href="https://srotrac.cashlessconsumer.in/members.html#overlap">'
                '<meta http-equiv="refresh" content="0;url=/members.html#overlap"></head>'
                '<body>Moved to <a href="/members.html#overlap">Members → Cross-SRO overlap</a>.</body></html>')
    print("wrote overlap.html (redirect stub)")

    # wide-table wrappers for mobile scroll
    for name, content in list(outputs.items()):
        outputs[name] = re.sub(r'(<table class="(?:listing|people)".*?</table>)',
                               r'<div class="table-scroll">\1</div>', content, flags=re.S)
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(outputs[name])

    write_agent_files(members, outputs)


if __name__ == "__main__":
    main()
