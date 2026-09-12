#!/usr/bin/env python3
"""Entity-type classification for SROTrac member organisations.

classify(name) -> (entity_type, entity_group)
Explicit OVERRIDES win; otherwise RULES (ordered regex) apply; default 'other'.
"""
import re

# type -> (label, group)
TYPES = {
    "bank": ("Bank", "Banking"),
    "sfb": ("Small Finance Bank", "Banking"),
    "ppb": ("Payments Bank", "Banking"),
    "coop": ("Cooperative Bank", "Banking"),
    "dfi": ("Development FI", "Banking"),
    "nbfc": ("NBFC", "Credit"),
    "hfc": ("Housing Finance", "Credit"),
    "mfi": ("NBFC-MFI", "Credit"),
    "fintech": ("Fintech / LSP", "Credit"),
    "aa": ("Account Aggregator", "Open Finance"),
    "payments": ("Payments / PSO", "Payments"),
    "card": ("Card Network", "Payments"),
    "pexchange": ("Forex / Remittance", "Payments"),
    "broker": ("Securities Broker", "Capital Markets"),
    "amc": ("AMC / Mutual Fund", "Capital Markets"),
    "minfra": ("Market Infrastructure", "Capital Markets"),
    "insurer": ("Insurer", "Insurance"),
    "tech": ("Tech / TSP", "Tech"),
    "bureau": ("Credit Bureau", "Credit"),
    "invest": ("Investments / Wealth", "Capital Markets"),
    "other": ("Other / Services", "Other"),
    "pd": ("Primary Dealer", "Capital Markets"),
}

GROUP_ORDER = ["Banking", "Credit", "Payments", "Open Finance",
               "Capital Markets", "Insurance", "Tech", "Other"]

# Known-organisation overrides (casefolded keys). Everything ambiguous goes here.
OVERRIDES = {
    # payments majors / PSOs
    "phonepe": ("payments", None), "google pay india": ("payments", None),
    "razorpay": ("payments", None), "cashfree": ("payments", None),
    "cashfree payments": ("payments", None), "payu": ("payments", None),
    "billdesk": ("payments", None), "india ideas": ("payments", None),
    "juspay": ("payments", None), "innoviti": ("payments", None),
    "mswipe": ("payments", None), "ezetap": ("payments", None),
    "pine labs": ("payments", None), "airpay": ("payments", None),
    "paynearby": ("payments", None), "spice money": ("payments", None),
    "transcorp international": ("payments", None),
    "zap money": ("payments", None), "payu india": ("payments", None),
    "itio innovex": ("payments", None), "fss": ("payments", None),
    "network international": ("payments", None),
    "worldline india": ("payments", None), "atome": ("payments", None),
    "zoko": ("payments", None), "unipay": ("payments", None),
    # card networks
    "visa": ("card", None), "mastercard": ("card", None),
    "american express banking corp india": ("card", None),
    "diners club": ("card", None), "rupay": ("card", None),
    # forex / remittance specialists
    "thomas cook india": ("pexchange", None), "ebixcash": ("pexchange", None),
    "ebixcash world money": ("pexchange", None), "orient exchange": ("pexchange", None),
    "bookmyforex": ("pexchange", None), "shareremittance": ("pexchange", None),
    "abhiwake": ("pexchange", None), "centrum forex": ("pexchange", None),
    "uae exchange": ("pexchange", None), "wall street finance": ("pexchange", None),
    "muthoot forex": ("pexchange", None), "paul merchants": ("pexchange", None),
    "kochupurackal john thomas": ("pexchange", None),
    # account aggregators (ReBI ecosystem)
    "cams financial information services private limited": ("aa", None),
    "finvu (cookiejar technologies)": ("aa", None),
    "cookiejar technologies": ("aa", None),
    "onemoney (finsec labs)": ("aa", None),
    "finsec labs": ("aa", None),
    "anumati (perpios account aggregation services)": ("aa", None),
    "perpios account aggregation services": ("aa", None),
    "protean account aggregation": ("aa", None),
    "setu aa (galaxy fintech)": ("aa", None),
    "galaxy fintech": ("aa", None),
    "nadl services": ("aa", None),
    "aa okasia": ("aa", None), "okasia": ("aa", None),
    "knmunification (krishnai novel multipurpose union)": ("aa", None),
    "krishnai novel multipurpose union (knmu)": ("aa", None),
    "vettech (india)": ("aa", None),
    "skylark design automation": ("aa", None),
    # capital markets infra
    "central depository services (india)": ("minfra", None),
    "cdsl": ("minfra", None), "nsdl": ("minfra", None),
    "national stock exchange of india": ("minfra", None),
    "bse": ("minfra", None), "ncdex": ("minfra", None),
    "metropolitan stock exchange of india": ("minfra", None),
    "indian clearing corporation": ("minfra", None),
    "nsdl payments bank": ("ppb", None),
    # insurers / insurtech
    "policybazaar": ("insurer", None), "pb fintech": ("insurer", None),
    "insurance repository": ("insurer", None),
    # tech majors in rosters
    "infosys": ("tech", None), "tata consultancy services": ("tech", None),
    "wipro": ("tech", None), "hcltech": ("tech", None),
    "oracle india": ("tech", None), "ibm india": ("tech", None),
    "zoho": ("tech", None), "freshworks": ("tech", None),
    "tally solutions": ("tech", None),
    "centre for development of advanced computing (c-dac)": ("tech", None),
    "c-dac": ("tech", None),
}

# --- FEDAI foreign banks / dealers without 'bank' in display name ---
for _n, _t in {
    "bnp paribas": "bank", "citibank n.a.": "bank", "citibank": "bank",
    "cooperatieve rabobank u.a": "bank", "cooperatieve rabobank u.a.": "bank",
    "mashreqbank p.s.c": "bank", "sberbank": "bank",
    "natwest markets plc.": "broker", "natwest markets": "broker",
    "societe generale": "bank", "ubs ag": "bank",
    "morgan stanley india primary dealer private limited": "pd",
    "morgan stanley india primary dealer private ltd": "pd",
    "pnb gilts limited": "pd", "pnb gilts ltd": "pd", "pnb gilts": "pd",
    "goldman sachs (i) capital markets private limited": "pd",
    "sbi dfhi": "pd", "sbi dfhi ltd": "pd",
    "nomura fixed income securities": "pd",
    "stci primary dealer limited": "pd",
    "icici securities primary dealership limited": "pd",
    "the clearing corporation of india ltd": "minfra",
    "thomas cook (india) limited": "pexchange",
    "deutsche bank ag": "bank", "standard chartered bank": "bank",
    "hsbc": "bank", "the hongkong and shanghai banking corporation": "bank",
    "emu": "pexchange", "abhi bus": "other",
}.items():
    OVERRIDES[_n] = (_t, None)

# --- AA ecosystem (Sahamati roster uses bare brand names) ---
for _n in ("finvu", "onemoney", "anumati", "setu aa", "nadl",
           "nesl asset data limited (nadl)", "protean suraksha aa",
           "cams finserv", "cams financial information services",
           "aa okasia"):
    OVERRIDES[_n] = ("aa", None)

# --- bureaus ---
for _n in ("crif", "crif high mark", "experian", "cibil", "equifax",
           "transunion cibil"):
    OVERRIDES[_n] = ("bureau", None)

# --- investments / wealth / advisers ---
for _n in ("abakkus asset manager private limited", "aditya birla money limited",
           "dezerv investments private limited", "epifi wealth private ltd.",
           "fee only investment advisers llp", "finteller advisors private limited",
           "finwiser", "incred wealth and investment services private limited",
           "indstocks private limited",
           "jio blackrock investment advisers private limited",
           "navi investment advisors private limited",
           "mobikwik investment adviser private limited",
           "upstox", "angel one", "angel one ltd.", "groww", "iifl",
           "computer age management services limited (nps)",
           "computer age management services", "finny", "zERODHA"):
    OVERRIDES[_n.casefold()] = ("invest", None)
OVERRIDES["zerodha"] = ("invest", None)

# --- payments / wallets / merchant pay brands ---
for _n in ("bharatpe", "mobikwik", "true balance", "novopay", "eko",
           "zaggle", "paysprint", "bharatnxt", "euronet", "infibeam avenues",
           "oxymoney", "payglocal", "payworld", "sabpaisa", "zokudo",
           "payrupik", "easebuzz", "payu india", "unipay"):
    OVERRIDES[_n] = ("payments", None)
OVERRIDES["unimoni"] = ("pexchange", None)

# --- clearly NBFC ---
for _n in ("incred", "avanse", "neogrowth", "oxyzo", "piramal enterprises",
           "kotak mahindra prime limited", "apollo finvest",
           "chinmay finlease", "muthoot fincorp", "gromor",
           "navi (chaitanya india fin)", "chaitanya india fin credit",
           "northern arc", "protium", "vivifi", "eduvanz", "bpj n bfc"):
    OVERRIDES[_n] = ("nbfc", None)

# --- fintech / lending platforms ---
for _n in ("finmantri", "fibe", "earlysalary services private limited (fibe)",
           "faircent", "branch", "billmart", "bankbazaar", "ayekart",
           "onecard", "olyv", "navanc", "moneyview", "bimapay", "lxme",
           "lightmoney", "lendbox", "kreditbee", "krazybee services private limited",
           "knight fintech", "kissht", "india gold", "indiagold", "flexmoney",
           "rupeek", "paisabazaar", "finarkein", "zoop money", "uni",
           "transbnk", "spocto x", "simpl", "dpdzero", "manipal fintech",
           "revfin", "progcap", "pocketly", "axio", "indialends", "indifi",
           "lendingkart", "navi", "yubi", "getvantage", "cred",
           "pivot money", "neokred", "rapiderupee", "rapidrupee",
           "salaryday", "smartcoin", "tala", "vaibhav vyapaar", "werize",
           "arth", "lendingplate", "freo", "moneyloji", "niro", "niyogin",
           "cars24", "udaan", "deleverage", "fundfina", "getkosh",
           "mypaisaa", "capitabel", "finova", "ezfinanz", "open", "fi money",
           "stable money", "uddan"):
    OVERRIDES[_n] = ("fintech", None)

# --- tech / TSP / SaaS / KYC infra ---
for _n in ("doqfy", "digio", "decentro", "credgenics", "castler",
           "the bureau", "bureau", "idsy", "idfy", "hyperverge", "gnani.ai",
           "leadquared", "leadsquared", "finbox", "zeta", "surepass",
           "advance.ai", "authbridge", "finpedia", "ignosis", "ignition",
           "signzy", "nelito", "scoreme", "clari5", "frog8", "lucid ledger",
           "mimo iq", "rezolve.ai", "famescore", "saafe", "ongrid",
           "perfios", "perfiostech", "voxomos", "digilo", "declogic"):
    OVERRIDES[_n] = ("tech", None)

# --- microfinance institutes without 'microfin' in name ---
for _n in ("spandana sphoorty", "grameen koota (growing opportunity)",
           "iti vikas trust", "dvara kgfs", "grameen shakti", "asa india",
           "jeevan utthan", "nightingale finvest", "sarwadi (swarna)",
           "sarwadi", "vruksha", "samavesh mfi", "belstar", "salt"):
    OVERRIDES[_n] = ("mfi", None)

# --- professional services / think tanks: leave explicitly 'other' ---
for _n in ("khaitan & co", "kpmg", "bdo", "ey", "drn legal",
           "lexisnexis risk", "telesign", "ispirit", "microsave consulting",
           "cyber ambassador", "entitled", "ecofin services", "lunchbrake classic private limited",
           "nbfc advisor", "agora", "cadre", "rezolv", "teleperforme"):
    OVERRIDES[_n] = ("other", "Other")

# --- residual stragglers (second pass) ---
for _n, _t in {
    "cadre": "other", "finagg": "fintech", "rezolv": "tech",
    "aspire": "fintech", "angelone": "invest", "paytm": "payments",
    "pay nearby": "payments", "paynearby": "payments", "lolc (india)": "nbfc",
    "lolc india": "nbfc", "nabard": "dfi", "sidbi": "dfi",
    "digio internet private limited": "tech",
    "paisabazaar marketing and consulting private limited": "fintech",
    "sarala (adikar?)": "mfi", "adj utility apps private limited": "other",
    "earlysalary": "fintech", "krazybee": "fintech",
    "sahamati member": None,
}.items():
    if _t: OVERRIDES[_n] = (_t, None)

RULES = [
    # banking family (order matters)
    (r"small finance bank", "sfb"),
    (r"payments bank", "ppb"),
    (r"co[- ]?operative", "coop"),
    (r"development bank|\bnabfid\b|\bfinancing infrastructure\b|\bnational housing bank\b|\bexport[- ]import\b|\bdeposit insurance\b", "dfi"),
    (r"\bbank\b|\bbanking\b", "bank"),
    (r"\bnabarl|\bnabcard|\bsidbi\b|\bnhb\b|\bexim\b", "dfi"),
    (r"\bifci\b|\bidbi\b", "dfi"),
    (r"primary dealer", "pd"),
    # insurance
    (r"insurance|assurance|insurtech", "insurer"),
    # capital markets
    (r"mutual fund|asset management|\bamc\b|trustee", "amc"),
    (r"securities|broking|stock broker|commodity|depository", "broker"),
    (r"\bnse\b|\bbse\b|\bcdsl\b|\bnsdl\b|\bncdex\b", "minfra"),
    # credit family
    (r"\bsfb\b", "sfb"),
    (r"\bmfi\b", "mfi"),
    (r"micro[\s-]?fin", "mfi"),
    (r"finlease|fincorp|finvest|fin\s?corp", "nbfc"),
    (r"housing finance", "hfc"),
    (r"finance|financ|finserv|capital|credit|loan", "nbfc"),
    # open finance
    (r"account aggregat", "aa"),
    # payments / forex
    (r"payment|wallet|remittance|forex|money transfer", "payments"),
    # tech-ish
    (r"technolog|software|systems|solutions|infotech|digital|labs?\b", "tech"),
]

DEFAULT = ("other", "Other")


def classify(name):
    key = re.sub(r"\s+", " ", str(name)).strip().casefold()
    ov = OVERRIDES.get(key)
    if ov:
        t, g = ov
        return (t, g or TYPES[t][1])
    for pat, t in RULES:
        if re.search(pat, key):
            return (t, TYPES[t][1])
    return DEFAULT

# --- FIMMDA member-list spellings (captured 2026-09-12) ---
for _n, _t in {
    "citibank na": "bank", "emirates nbd pjsc": "bank", "mashreqbank psc": "bank",
    "cooperatieve rabobak u.a": "bank", "sumitomo mitsui": "bank",
    "natwest markets plc": "broker",
    "india infrastructure finance company limited": "dfi",
}.items():
    OVERRIDES[_n] = (_t, None)
