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
]

# SROs whose full member roster is not published on the public site.
NO_ROSTER = {
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
    rosters = {"FACE": face, "UFF": uff, "SRPA": srpa}

    write_csv(OUT / "face_members.csv", face, ["sro", "member_name", "website", "member_type"])
    write_csv(OUT / "uff_members.csv", uff, ["sro", "member_name", "website", "member_type", "logo_file"])
    write_csv(OUT / "srpa_members.csv", srpa, ["sro", "member_name", "website", "member_type", "logo_file"])
    write_csv(OUT / "sros.csv", SROS, ["sro_id", "name", "abbr", "website", "nlp_site", "recognition", "recognised_date", "status", "sector"])

    db = OUT / "srotrac.duckdb"
    if db.exists():
        db.unlink()
    union = "\n      UNION ALL ".join(
        f"SELECT sro, member_name, website, member_type FROM read_csv_auto('{OUT/f'{k.lower()}_members.csv'}')"
        for k in ["face", "uff", "srpa"]
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
