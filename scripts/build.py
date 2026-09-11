#!/usr/bin/env python3
"""Build SROTrac member datasets.

Sources (data/raw/):
  - face_membership.html : https://faceofindia.org/membership/
  - uff_home.html        : https://unifiedfintech.in/  (member logo wall)
  - srpa_home.html       : https://srpa.org.in/  (partner logo wall)

Outputs (data/):
  - face_members.csv, uff_members.csv, srpa_members.csv,
    sros.csv, srotrac.duckdb, docs/members.md
"""
import csv
import re
import html
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

SECTION_LABELS = {
    "A structured channel for engagement with regulators and government",
    "Participation in working groups, forums, and consultations",
    "Access to advisories, guidance notes, standards-related work, and practical resources",
    "Member meetings, webinars, roundtables, and thematic discussions",
    "Research, insights, and practical knowledge-sharing",
    "Opportunities for collaboration, visibility, and ecosystem engagement",
    "A trusted platform for collective industry representation",
    "Stronger connections across FinTech, infrastructure, policy, and partner networks",
    "Eligibility",
    "How Members Engage",
    "Annual Membership Fee",
    "Instagram",
    "LinkedIn",
    "Twitter",
    "facebook",
    "logo",
}


def parse_face():
    h = (RAW / "face_membership.html").read_text(encoding="utf-8", errors="ignore")
    i = h.find("Our Members")
    seg = h[i:] if i > 0 else h
    pairs = re.findall(
        r'(?:<a[^>]*href="([^"]*)"[^>]*>\s*)?<img[^>]*alt="([^"]+)"[^>]*>', seg
    )
    rows, seen = [], set()
    for href, alt in pairs:
        alt = html.unescape(alt).strip()
        if not alt or alt in SECTION_LABELS or alt in seen:
            continue
        seen.add(alt)
        rows.append({"sro": "FACE", "member_name": alt,
                     "website": href.strip(), "member_type": "member"})
    return rows


# UFF logo filename -> canonical member name (logo wall has many generic filenames)
UFF_NAME = {
    "AXIO-2.png": "Axio", "INDIALENDS-2.png": "IndiaLends", "INDIFI-2.png": "Indifi",
    "LENDINGKART-2.png": "Lendingkart", "MONEYVIEW.png": "Moneyview",
    "NEO-GROWTH.png": "NeoGrowth", "finbox.png": "FinBox", "KREDIT.png": "KreditBee",
    "Navi.png": "Navi", "UNI.png": "Uni", "Yubi.png": "Yubi", "CAPRI.png": "Capri Loans",
    "IGNOSIS.png": "iGnosis", "lendingkart.png": "PayU Finance", "Signzy-1.png": "Signzy",
    "avanse.png": "Avanse", "KINARA.png": "Kinara Capital", "TRUE-BALANCE.png": "True Balance",
    "Advance.ai_.png": "Advance.ai", "117.png": "AuthBridge", "116.png": "Bank of Baroda",
    "BUREAU.png": "Bureau", "112.png": "Credit Saison", "Decentro.webp": "Decentro",
    "110.png": "Eko", "109.png": "Experian", "106.png": "Fi Money", "104.png": "Finpedia",
    "HYPERVERGE.png": "HyperVerge", "IIFL.png": "IIFL", "ISPIRT.png": "iSPIRT",
    "MOBIKWIK.png": "MobiKwik", "NELITO.png": "Nelito", "NEOKRED.png": "NeoKred",
    "NORTHERN-ARC.png": "Northern Arc", "PERFIOS.png": "Perfios", "PROTIUM.png": "Protium",
    "RAPIDRUPEE.png": "RapidRupee", "RBL.png": "RBL Bank", "SAAFE.png": "Saafe",
    "SCOREME.png": "ScoreMe", "zaggle.png": "Zaggle", "KHAITAN.png": "Khaitan & Co",
    "KPMG.png": "KPMG", "BDO.png": "BDO", "logo-bpj-horizont-01.png": "BPJ N BFC",
    "bharat-nxt.png": "BharatNXT", "BSFG.png": "BSFG Finance", "Clari5.png": "Clari5",
    "2-3.png": "PaySprint", "WhatsApp-Image-2025-03-26-at-2.06.58-PM.webp": "Cyber Ambassador",
    "Deleverage-1.svg": "Deleverage", "Entitled.png": "Entitled", "Fame-Score.png": "FameScore",
    "Fundfina.png": "Fundfina", "up-182x55.jpg": "GetKosh", "frog8.png": "Frog8",
    "lucidledger.png": "Lucid Ledger", "Mimo.png": "MiMo IQ", "My-Paisaa-2.png": "MyPaisaa",
    "Rezolv.svg": "Rezolve.ai", "capitabel.png": "Capitabel",
    "DMI-Logo-CYMK.ai-182-x-55-px.png": "NBFC Advisor", "128-1.png": "Achiievers Finance",
    "APOLLO.png": "Apollo Finvest", "Asipre-upi.webp": "Aspire", "bharatpe_logo.png": "BharatPe",
    "BRANCH.png": "Branch", "BUENO.png": "Bueno Finance", "CADRE.png": "CADRE",
    "CARS24.png": "CARS24", "117-1.png": "Chinmay Finlease", "CRED.webp": "CRED",
    "CREDITT.png": "Creditt", "CREDIT-SEA.png": "CreditSea", "128.png": "DMI Finance",
    "ECOFIN.png": "Ecofin Services", "EDUVANZ.png": "Eduvanz", "EZFINANZ.png": "Ezfinanz",
    "FINOVA.png": "Finova", "FLEXI-LAONS.png": "FlexiLoans", "GROMOR.png": "Gromor",
    "INCRED.png": "InCred", "132.png": "IndiaGold", "LENDING-PLATE.png": "LendingPlate",
    "LIGHT-2.png": "Light Microfinance", "LOANEY.png": "Loaney", "FREO.png": "Freo",
    "MONEY.png": "Moneyloji", "133.png": "Muthoot Fincorp", "niro.png": "Niro",
    "NIYOGIN.png": "Niyogin", "ok.png": "OKCredit", "OXYZO.png": "Oxyzo",
    "PAISABAZAAR.png": "Paisabazaar", "rubik.png": "PayRupik", "PAYTM.png": "Paytm",
    "PROGCAP.png": "Progcap", "QUADRILLION.png": "Quadrillion Finance", "REVFIN.png": "Revfin",
    "SALARY-DAY.png": "SalaryDay", "SHUBH-LOAN.png": "Shubh Loans", "SMART-COIN.png": "SmartCoin",
    "SMC-FINANCE.png": "SMC Finance", "SPICE-MONEY.png": "Spice Money", "TALA.png": "Tala",
    "TEZZRACT.png": "Tezz Capital", "UDAAN.png": "Udaan", "UGRO.png": "UGRO Capital",
    "VIABHAV.png": "Vaibhav Vyapaar", "VIVIFI.png": "Vivifi", "voxomos.ai_-1-165x53.png": "Voxomos",
    "WERIZE-165x53.png": "WeRize", "ZETA-165x53.png": "Zeta", "CRIF-165x53.png": "CRIF High Mark",
    "swipeloan-165x53.png": "SwipeLoan", "108.png": "EY", "DRN-Legal.png": "DRN Legal",
    "LEXIS.png": "LexisNexis Risk", "TELESIGN.png": "TeleSign", "GETVANTAGE.png": "GetVantage",
}

# UFF associate (service-provider / advisory / bank-side) members
UFF_ASSOCIATE = {
    "KPMG", "BDO", "EY", "Khaitan & Co", "DRN Legal", "LexisNexis Risk", "TeleSign",
    "CRIF High Mark", "Bureau", "Clari5", "iSPIRT", "Bank of Baroda", "RBL Bank",
    "Nelito", "Signzy", "Voxomos", "Cyber Ambassador", "NBFC Advisor",
}


def parse_uff():
    h = (RAW / "uff_home.html").read_text(encoding="utf-8", errors="ignore")
    blocks = re.findall(r"wd-gallery-item.*?</div>", h, flags=re.S)
    rows, seen = [], set()
    for b in blocks:
        img = re.search(r'src="([^"]+\.(?:png|jpg|jpeg|webp|svg))"', b)
        href = re.search(r'href="([^"]+)"', b)
        if not img:
            continue
        fn = img.group(1).split("/")[-1]
        if fn not in UFF_NAME:
            continue  # event photos / unnamed tiles
        url = href.group(1).strip() if href else ""
        if url.startswith("http://unifiedfintech.in") or url == "#":
            url = ""
        name = UFF_NAME[fn]
        if name in seen:
            continue
        seen.add(name)
        rows.append({
            "sro": "UFF",
            "member_name": name,
            "website": url,
            "member_type": "associate" if name in UFF_ASSOCIATE else "member",
            "logo_file": fn,
        })
    return rows


# SRPA partner logo wall (srpa.org.in). Filenames are truncated; names decoded
# from the logo images themselves (see docs/members.md caveats).
SRPA_MEMBERS = [
    ("BillDesk", "bill.jpg", "https://www.billdesk.com"),
    ("CRED", "cred.jpg", "https://cred.club"),
    ("Euronet", "euro.jpg", "https://www.euronetworldwide.com"),
    ("Infibeam Avenues", "infi.jpg", "https://www.infibeam.com"),
    ("In-Solutions Global (ISG)", "isg.jpg", "https://insolutionsglobal.com"),
    ("MobiKwik", "mob.jpg", "https://www.mobikwik.com"),
    ("Mswipe", "mswipe.jpg", "https://www.mswipe.com"),
    ("Concerto Software & Systems", "oncerto.jpg", ""),
    ("Open", "open.jpg", "https://open.money"),
    ("OxyMoney", "oxy.jpg", "https://www.oxymoney.com"),
    ("PayGlocal", "pay.jpg", "https://payglocal.com"),
    ("PayWorld", "payword.jpg", "https://www.payworldindia.com"),
    ("PhonePe", "phonepay.jpg", "https://www.phonepe.com"),
    ("Razorpay", "razor.jpg", "https://razorpay.com"),
    ("SabPaisa", "sab.jpg", "https://sabpaisa.com"),
    ("Spice Money", "spice.jpg", "https://www.spicemoney.com"),
    ("Unimoni", "uni.jpg", "https://www.unimoni.com"),
    ("Zokudo", "zok.jpg", "https://www.zokudo.com"),
]


def parse_srpa():
    h = (RAW / "srpa_home.html").read_text(encoding="utf-8", errors="ignore")
    present = set(re.findall(r'partner/([^"\')\s]+\.jpg)', h))
    rows = []
    for name, fn, url in SRPA_MEMBERS:
        if fn not in present:
            continue  # logo no longer on the live page
        rows.append({"sro": "SRPA", "member_name": name, "website": url,
                     "member_type": "member", "logo_file": fn})
    return rows


def clean_logo_name(fn):
    """Derive a member name from a logo filename: strip ext, region prefixes, numerics."""
    n = fn.rsplit(".", 1)[0]
    n = re.sub(r"[-_](?:North|South|East|West|Central)$", "", n, flags=re.I)
    n = re.sub(r"^\d+[.\-]\d*[-_]?", "", n)
    n = re.sub(r"[_-]+", " ", n).strip()
    return n.title() if n and not re.fullmatch(r"[\d ]+", n) else ""


def parse_mfin():
    """Parse MFIN member logo wall (region carousels tab01-tab05)."""
    src = RAW / "mfin_members.html"
    if not src.exists():
        return []
    h = src.read_text(encoding="utf-8", errors="ignore")
    rows, seen = [], set()
    for tab in ["tab01", "tab02", "tab03", "tab04", "tab05"]:
        i = h.find(f'id="{tab}"')
        if i < 0:
            continue
        j = h.find(f'id="tab0', i + 10)
        seg = h[i:j if j > 0 else i + 200000]
        for m in re.finditer(r'<a href="([^"]+)"[^>]*>\s*<img src="[^"]*/([^"/]+)"', seg):
            u, fn = m.group(1).strip(), m.group(2)
            if fn.lower() in seen or u in ("#", "#0"):
                continue
            seen.add(fn.lower())
            name = NAME_MAP_MFIN.get(fn.lower()) or clean_logo_name(fn)
            rows.append({"sro": "MFIN", "member_name": name, "website": u,
                         "member_type": "member", "logo_file": fn})
    return rows



def parse_fedai():
    """Parse FEDAI member tables (bank name + LEI, grouped by category)."""
    src = RAW / "fedai_members.html"
    if not src.exists():
        return []
    h = src.read_text(encoding="utf-8", errors="ignore")
    rows, seen = [], set()
    # sections: Public Sector Banks / Foreign Banks / Private Sector Banks / Co-Operative...
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", h, flags=re.S):
        cells = [re.sub(r"<[^>]+>", "", c) for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(1), flags=re.S)]
        cells = [re.sub(r"\s+", " ", c).strip() for c in cells]
        if len(cells) < 2:
            continue
        # find slno + name + optional lei
        name = None
        lei = ""
        for idx, c in enumerate(cells):
            if re.fullmatch(r"\d{1,3}", c) and idx + 1 < len(cells) and len(cells[idx + 1]) > 2:
                name = cells[idx + 1]
                if idx + 2 < len(cells) and re.fullmatch(r"[A-Z0-9]{10,}", cells[idx + 2].replace(" ", "")):
                    lei = cells[idx + 2].replace(" ", "")
                break
        if not name:
            continue
        name = re.sub(r"\s*[-\u2013]?\s*\"Surrender of AD.*$", "", name).strip(" -")
        if name.lower() in seen or len(name) < 3:
            continue
        seen.add(name.lower())
        rows.append({"sro": "FEDAI", "member_name": name, "website": "",
                     "member_type": "member", "lei": lei})
    return rows

NAME_MAP_MFIN = {
    "fccl - iti vikas logo.jpg": "ITI Vikas (FCCL)",
    "bwda.jpg": "BWDA Finance",
    "vikas.png": "ITI Vikas Trust",
    "smfg.png": "SMFG India Credit",
    "advertising-finance-pvt-ltd-west.jpg": "Avanti Finance",
    "fincare.jpg": "Fincare Small Finance Bank",
    "avanti.png": "Avanti Finance",
    "axis_bank.jpg": "Axis Bank",
    "yes_bank.png": "Yes Bank",
    "hdfc-bank-logo.png": "HDFC Bank",
    "icici_bank.png": "ICICI Bank",
    "idfc_first_bharat.jpg": "IDFC First Bank",
    "l&t-1.jpg": "L&T Finance",
    "rbl_apno_ka_bank.jpg": "RBL Bank",
    "indusind_bank.jpg": "IndusInd Bank",
    "unity logo.jpg": "Unity Small Finance Bank",
    "au sfb.jpg": "AU Small Finance Bank",
    "utkarsh.png": "Utkarsh SFB",
    "bandhan.jpeg": "Bandhan Bank",
    "jana.jpg": "Jana SFB",
    "esaf.png": "ESAF SFB",
    "equitas.png": "Equitas SFB",
    "ujjivan.jpg": "Ujjivan SFB",
    "suryoday.png": "Suryoday SFB",
    "sib.jpg": "South Indian Bank",
    "bajaj_1200x1200px-01.jpg": "Bajaj Finance",
    "tatacapital.png": "Tata Capital",
    "piramal finance-01.jpg": "Piramal Enterprises",
    "northernarc.png": "Northern Arc Capital",
    "creditaccess_grameen_ltd.jpg": "CreditAccess Grameen",
    "chaitanya.jpg": "Navi (Chaitanya India Fin)",
    "growing-opp.jpg": "Grameen Koota (Growing Opportunity)",
    "swarna.jpeg": "Sarwadi (Swarna)",
    "sarwana.jpeg": "Sarwadi",
    "sarala.png": "Sarala (Adikar?)",
    "adhikar.jpg": "Adhikar Microfinance",
    "light.jpg": "Light Microfinance",
    "svatantra.jpg": "Svatantra Microfin",
    "hindustan_micro.jpg": "Hindusthan Microfinance",
    "unnatti finserv pvt ltd logo.png": "Unnati Microfinance",
    "m_power.jpg": "M Power Microfinance",
    "satin.jpg": "Satin Creditcare",
    "vrukhsha.jpg": "Vrukhsha Microfin",
    "asirvad_microfinance.png": "Asirvad Microfinance",
    "dvara.png": "Dvara KGFS",
    "muthoot.jpg": "Muthoot Microfin",
    "share.jpg": "Share Microfin (Mera Money)",
    "spandana.jpg": "Spandana Sphoorty",
    "samasta.png": "Samasta Microfinance",
    "inditrade.jpg": "Inditrade Capital",
    "msm-microfinance-pvt-ltd-south.jpg": "MSM Microfinance",
    "kpb.jpg": "K P Microfin",
    "gsms logo.png": "Grameen Shakti",
    "adi_chitragupta.png": "Adi Chitragupta Finance",
    "annapurna.png": "Annapurna Finance",
    "annapurna.jpg": "Annapurna Finance",
    "annapurna.JPG": "Annapurna Finance",
    "asai_logo.jpg": "ASA India",
    "gu_finance.png": "GU Finance",
    "jagran.png": "Jagaran Microfin",
    "janakalyan.jpg": "Janakalyan Financial Services",
    "saija.jpg": "Saija Finance",
    "nightingale.jpg": "Nightingale Finvest",
    "savi.jpg": "Save Microfinance (Savi)",
    "unacco-finance-pvt-ltd-east.jpg": "Unacco Finance",
    "vector_finance.png": "Vector Finance",
    "vfs.jpg": "VFSC Capital",
    "aviral-finance-private.png": "Aviral Finance",
    "agora.JPG": "AMIL (Agora)",
    "centrum-microcredit-pvt-ltd.jpg": "Centrum Microcredit",
    "finofinance.png": "Fino Finance",
    "namra.png": "Namra Finance",
    "svasti.jpg": "Svasti Microfinance",
    "lolc_logo.png": "LOLC (India)",
    "radhya.jpg": "Radhya Financing",
    "arth.png": "Arth",
    "margdarshak-financial-services-ltd-north.jpg": "Margdarshak Financial Services",
    "mitrata.png": "Mitrata Inclusive Financial Services",
    "samavesh.jpg": "Samavesh MFI",
    "satya.png": "Satya Microcapital",
    "djt microfinance secondary logo (full).png": "DJT Finserv",
    "midland microfin-1.jpg": "Midland Microfin",
    "belstar.jpeg": "Belstar Microfinance",
    "vaya.jpg": "Vaya Finserv",
    "srifin.jpg": "Srifin Credit",
    "southindiafinvest.png": "South India Finvest",
    "magentafinance": "Magenta Finance",
    "magenta.jpg": "Magenta Finance",
    "fusion.jpg": "Fusion Microfinance",
    "fusion.JPG": "Fusion Microfinance",
    "arohan.jpg": "Arohan Financial Services",
    "vrukhsha.jpg": "Vruksha Microfin",
}


SROS = [
    {
        "sro_id": "face", "name": "Fintech Association for Consumer Empowerment",
        "abbr": "FACE", "website": "https://faceofindia.org",
        "nlp_site": "https://faceofindia.org/membership/",
        "recognition": "RBI-recognised SRO-FT (first)",
        "recognised_date": "2024-08-28", "status": "active", "sector": "fintech",
    },
    {
        "sro_id": "uff", "name": "Unified Fintech Forum",
        "abbr": "UFF", "website": "https://unifiedfintech.in",
        "nlp_site": "https://unifiedfintech.in/members-network/",
        "recognition": "RBI-recognised SRO-FT (second); rebranded from DLAI (Apr 2025)",
        "recognised_date": "2026-09-10", "status": "active", "sector": "fintech",
    },
    {
        "sro_id": "srpa", "name": "Self-Regulated PSO Association",
        "abbr": "SRPA", "website": "https://srpa.org.in",
        "nlp_site": "https://srpa.org.in/",
        "recognition": "RBI-recognised SRO for Payment System Operators (not a fintech SRO-FT); tracked for context",
        "recognised_date": "2025-11-11", "status": "related", "sector": "pso",
    },
    {
        "sro_id": "fidc", "name": "Finance Industry Development Council",
        "abbr": "FIDC", "website": "https://www.fidcindia.org.in",
        "nlp_site": "https://www.fidcindia.org.in/membership-details/",
        "recognition": "RBI-recognised SRO for NBFCs (not a fintech SRO-FT); tracked for context",
        "recognised_date": "2025-10-03", "status": "related", "sector": "nbfc",
    },
    {
        "sro_id": "mfin", "name": "Microfinance Institutions Network",
        "abbr": "MFIN", "website": "https://mfinindia.org",
        "nlp_site": "https://mfinindia.org/members",
        "recognition": "RBI-recognised SRO for NBFC-MFIs (first; RBI letter dated 16 Jun 2014)",
        "recognised_date": "2014-06-16", "status": "active", "sector": "microfinance",
    },
    {
        "sro_id": "sadhan", "name": "Sa-Dhan",
        "abbr": "Sa-Dhan", "website": "https://www.sa-dhan.net",
        "nlp_site": "https://www.sa-dhan.net/what-we-do/sro/",
        "recognition": "RBI-recognised SRO for NBFC-MFIs (second; Mar 2015)",
        "recognised_date": "2015-03-11", "status": "active", "sector": "microfinance",
    },
    {
        "sro_id": "fedai", "name": "Foreign Exchange Dealers' Association of India",
        "abbr": "FEDAI", "website": "https://www.fedai.org.in",
        "nlp_site": "https://www.fedai.org.in/Default.aspx",
        "recognition": "RBI-recognised SRO for all Authorised Dealers in foreign exchange (Omnibus framework; 1-yr transition to Jan 2027)",
        "recognised_date": "2026-01-14", "status": "active", "sector": "forex",
    },
]

# SROs whose full member roster is not published on the public site.
NO_ROSTER = {
    "Sa-Dhan": "No public member directory on sa-dhan.net. Sa-Dhan is a broad network "
               "(claims 200+ institutions incl. MFIs, banks, SFBs); membership data is "
               "published via its Bharat Microfinance Report / portal, not a webpage.",
    "FIDC": "No public member roster. The 'list of NBFCs' page is RBI registration "
            "lists by scale/type, not FIDC's own membership. FIDC claims ~400 members "
            "in press material; roster available only via annual report / on request.",
}


def write_members_md(rosters, sros):
    """Render docs/members.md from the parsed rosters."""
    from datetime import date
    today = date.today().isoformat()
    all_rows = [r for rows in rosters.values() for r in rows]
    names = {}
    for r in all_rows:
        names.setdefault(r["member_name"], set()).add(r["sro"])
    shared = {n: v for n, v in names.items() if len(v) > 1}

    lines = [
        "# SROTrac — Member Listings",
        "",
        f"_Generated {today} by `scripts/build.py`. Do not hand-edit._",
        "",
        "India's RBI-recognised self-regulatory organisations in payments and fintech. "
        "**FACE** and the **Unified Fintech Forum** are the two SRO-FTs; **SRPA** (payment "
        "system operators) and **FIDC** (NBFCs) are included for context.",
        "",
        "## Totals",
        "",
        "| SRO | Sector | Status | Members captured |",
        "|-----|--------|--------|------------------|",
    ]
    for s in sros:
        rows = rosters.get(s["abbr"], [])
        n = len(rows) if rows else ("not published" if s["abbr"] in NO_ROSTER else "0")
        lines.append(f"| {s['abbr']} | {s['sector']} | {s['status']} | {n} |")
    lines += [""]

    if shared:
        lines += ["## Organisations in more than one SRO", ""]
        for n, v in sorted(shared.items()):
            lines.append(f"- {n} — {', '.join(sorted(v))}")
        lines += [""]

    for abbr, rows in rosters.items():
        if not rows:
            if abbr in NO_ROSTER:
                lines += [f"## {abbr} — members", "", NO_ROSTER[abbr], ""]
            continue
        lines += [f"## {abbr} — {len(rows)} members", "",
                  "| # | Member | Website | Type |", "|---|--------|---------|------|"]
        for i, r in enumerate(rows, 1):
            lines.append(f"| {i} | {r['member_name']} | {r['website']} | {r['member_type']} |")
        lines.append("")

    lines += [
        "## Caveats",
        "",
        "- FACE publicly claims **200+ fintech members** in press material, but its "
        "`/membership/` page renders only the logos captured above. The published "
        "roster is a subset of the claimed membership.",
        "- UFF `member_type` is heuristic (vendors/consultancies/bureaus tagged `associate`).",
        "- SRPA partner names were decoded from logo images; filenames are truncated "
        "abbreviations, and the site does not link partners to their sites.",
        "- These are marketing pages, not filings. Treat rosters as directional.",
        "",
    ]
    (OUT.parent / "docs" / "members.md").write_text("\n".join(lines), encoding="utf-8")


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main():
    face = parse_face()
    uff = parse_uff()
    srpa = parse_srpa()
    mfin = parse_mfin()
    fedai = parse_fedai()
    rosters = {"FACE": face, "UFF": uff, "SRPA": srpa, "MFIN": mfin, "FEDAI": fedai}

    write_csv(OUT / "face_members.csv", face, ["sro", "member_name", "website", "member_type"])
    write_csv(OUT / "uff_members.csv", uff, ["sro", "member_name", "website", "member_type", "logo_file"])
    write_csv(OUT / "srpa_members.csv", srpa, ["sro", "member_name", "website", "member_type", "logo_file"])
    write_csv(OUT / "mfin_members.csv", mfin, ["sro", "member_name", "website", "member_type", "logo_file"])
    write_csv(OUT / "fedai_members.csv", fedai, ["sro", "member_name", "website", "member_type", "lei"])
    write_csv(OUT / "sros.csv", SROS, ["sro_id", "name", "abbr", "website", "nlp_site", "recognition", "recognised_date", "status", "sector"])

    db = OUT / "srotrac.duckdb"
    if db.exists():
        db.unlink()
    union = "\n      UNION ALL ".join(
        f"SELECT sro, member_name, website, member_type FROM read_csv_auto('{OUT/f'{k.lower()}_members.csv'}')"
        for k in ["face", "uff", "srpa", "mfin", "fedai"]
    )
    sql = f"""
    CREATE TABLE sros AS SELECT * FROM read_csv_auto('{OUT/'sros.csv'}');
    CREATE TABLE members AS
      {union};
    """
    subprocess.run(["duckdb", str(db)], input=sql, text=True, check=True)

    write_members_md(rosters, SROS)
    total = sum(len(r) for r in rosters.values())
    print(f"FACE members: {len(face)}")
    print(f"UFF members:  {len(uff)}")
    print(f"SRPA members: {len(srpa)}")
    print(f"Total members: {total}")
    print("Wrote docs/members.md")


if __name__ == "__main__":
    main()
