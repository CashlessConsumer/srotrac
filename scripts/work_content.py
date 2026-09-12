#!/usr/bin/env python3
"""Deep-dive work pages: what each RBI-recognised SRO actually does.

All content grounded in the SRO's own site captures (data/raw/, and
sro_work captures in the conversation workspace) — dates included where
the source published them. Gaps are stated honestly.
"""

WORK = {
    "sahamati": {
        "tagline": "Standards body of the account-aggregator ecosystem — now its RBI-recognised SRO",
        "summary": (
            "Sahamati (non-profit catalyst for the Account Aggregator rail since 2020; "
            "recognised as the AA ecosystem's SRO on 5 June 2026) is the eighth and newest "
            "entry in RBI's SRO register. Its 110 RE members span AAs, FIPs, FIUs and TSPs, "
            "and it publishes operational dashboards no other SRO matches."
        ),
        "sections": [
            {
                "h": "What Sahamati is",
                "prose": "Sahamati began in 2020 as a non-profit ecosystem catalyst for the Account Aggregator (AA) framework — the RBI-regulated consent-based data-sharing rail that lets customers pull their financial data (bank accounts, investments, GST, insurance) into any FIU app with revocable, purpose-bound consent. Spun out of iSPIRT's product-thought work, it coordinated AAs, FIPs, FIUs and TSPs for five years before the RBI\u2019s omnibus SRO framework gave it a formal home: recognised on 5 June 2026 as the SRO for the AA ecosystem.",
            },
            {
                "h": "Membership",
                "items": [
                    "110 RE members listed in its Current RE Members directory (captured 2026-09-11) — the widest net of any new SRO: the eight licensed AAs plus FIPs (banks, AMCs, depositories), FIUs (lenders, wealth apps) and TSPs.",
                    "Membership categories mirror AA-ecosystem roles rather than legal form — a design choice worth watching as RBI's SRO rules technically cover 'regulated entities'.",
                ],
            },
            {
                "h": "Published infrastructure",
                "items": [
                    "AA Usage Metrics & Industry Stats dashboards — volumes of consents, data requests and fulfilled requests across the network.",
                    "Grievances Dashboard — complaint volumes and resolution rates, self-published by the industry body itself.",
                    "AA APIs Health Dashboard and Central Registry status — operational transparency tools no other SRO runs.",
                    "Certification and FIP-AA integration playbooks — de facto standards for onboarding data providers.",
                ],
            },
            {
                "h": "What to watch",
                "items": [
                    "Enforcement record: dashboards show volumes, but no public disciplinary actions yet — the shift from catalyst to regulator is untested.",
                    "Scope question: TSPs are not RBI-regulated entities; how an SRO recognised under the omnibus framework governs them remains to be seen.",
                    "Conflict optics: Sahamati both promotes AA adoption and polices it — the dual hat the omnibus rules ask SROs to manage.",
                ],
            },
        ],
        "gaps": [
            "No public disciplinary/enforcement log yet — dashboards show volumes, not actions.",
            "Board, EC and conflict-of-interest disclosures are thinner than FACE's published governance.",
            "Unclear how TSPs (not RBI-regulated) sit inside an omnibus-framework SRO.",
        ],
        "sources": [
            ("Current RE Members", "https://sahamati.org.in/current-re-members/"),
            ("Industry stats & dashboards", "https://sahamati.org.in/industry-stats/"),
            ("SRO recognition (what-we-do)", "https://sahamati.org.in/what-we-do/sro/"),
        ],
    },

    "face": {
        "tagline": "Standards, oversight & dispute resolution for digital lending",
        "summary": (
            "FACE (registered 24 August 2020, recognised 28 August 2024) is the first RBI-recognised "
            "SRO-FT. Its published work splits into five streams: standards, oversight & enforcement, "
            "grievance & dispute resolution (GDR), policy engagement, and knowledge tooling."
        ),
        "sections": [
            {
                "h": "Standards & guidelines (dated trail)",
                "items": [
                    "Guidelines on Arbitration Framework in Loan Agreement — 2 Sep 2026",
                    "Guidelines on DLG (Default Loss Guarantee) disclosure — Jul 2026",
                    "Guidelines for LSP–RE agreements (lending service provider ↔ regulated entity) — 31 Mar 2026",
                    "Guidelines on Whistleblower Mechanism — Sep 2025",
                    "Guidelines on Debt Recovery — 29 Aug 2025",
                    "Guidelines on Penal Charges — Jun 2025",
                    "Guidelines on Cybersecurity Measures — 13 May 2025",
                    "Pricing of Digital Loans by NBFCs — Jan 2025",
                ],
            },
            {
                "h": "Practical tooling for members",
                "items": [
                    "List of Regulatory Policies for base-layer NBFCs — 31 Aug 2026",
                    "List of Supervisory Returns for NBFCs — 28 Aug 2026",
                    "Checklist for Responsible & Trustworthy AI in digital lending (with Dvara and PwC) — 18 Mar 2026",
                    "Checklist for public disclosure on DLAs and LSP/RE websites — 14 Aug 2025",
                    "Checklist on Customer Grievance Redressal — 13 Mar 2024; defence guide against unauthorised use of company details — 4 Mar 2024",
                    "Baseline technology standards suggestions for DLAs — Mar 2023",
                ],
            },
            {
                "h": "Oversight & enforcement",
                "prose": (
                    "The Oversight & Enforcement Policy (18 Aug 2025) sets out monitoring, review, "
                    "escalation and enforcement across self-regulatory work: company-level monitoring, "
                    "industry-level pattern analysis (including tracking app marketplaces), distinguishing "
                    "isolated lapses from recurring deviations, with escalation paths to member-support, "
                    "cautions, and RBI referral."
                ),
            },
            {
                "h": "Grievance & dispute resolution (GDR)",
                "prose": (
                    "A governed pathway for member disputes and complaints: submission via prescribed digital "
                    "channels → initial review by the nodal officer and CEO → escalation to the Grievance and "
                    "Dispute Redressal Committee → examination → formal closure. Documented, confidential, "
                    "time-bound; positioned as an alternative to escalation and litigation."
                ),
            },
            {
                "h": "Policy & knowledge work",
                "items": [
                    "Consultation responses and structured dialogue with RBI, government and regulators — engagement framed as evidence-based and balanced across buy/sell side",
                    "Industry surveys and reports under its Knowledge stream; member-only advisories",
                    "Client-insight channel and engagement with marketplaces and app ecosystems",
                ],
            },
        ],
        "gaps": [
            "The DAK (Digital Assurance & Keeping?) scorecard detail referenced in its framework pages is not published as a standalone document",
            "No public complaint statistics or enforcement actions register",
            "Full member agreements/code sign-offs are not public",
        ],
        "sources": [
            ("faceofindia.org — Standards", "https://faceofindia.org/standards/"),
            ("FACE — Oversight & Enforcement Policy", "https://faceofindia.org/oversight-enforcement/"),
            ("FACE — Grievance & Dispute Resolution", "https://faceofindia.org/grievance-dispute-resolution/"),
            ("FACE — Policy", "https://faceofindia.org/policy/"),
            ("FACE — Governance", "https://faceofindia.org/governance/"),
        ],
    },
    "uff": {
        "tagline": "Digital lending's second SRO-FT: born as DLAI, recognised 10 Sep 2026",
        "summary": (
            "The Unified Fintech Forum (formerly the Digital Lenders Association of India, founded 2016) "
            "became RBI's second fintech SRO on 10 September 2026. Its self-described remit spans the "
            "fintech stack — digital lending, payments, wealthtech, insurtech — with working groups under "
            "a governance council and a secretariat."
        ),
        "sections": [
            {
                "h": "Governance architecture",
                "items": [
                    "Independent-dominated board: Alok Prasad (Chair) with ex-RBI Deputy Governor N S Vishwanathan, ex-RBI ED Meena Hemchandra, ex-SBI Deputy MD Dhananjay Tambe, ex-SIDBI CMD Mohammad Mustafa and others alongside founder-member promoters (Indifi, Freo, Axio, Lendingkart)",
                    "Governance Council, committees, working groups, and a Code-of-Conduct sub-committee under its published governance philosophy",
                    "Professional secretariat; executive committee drawn from member CEOs",
                ],
            },
            {
                "h": "Client protection work",
                "items": [
                    "Voluntary Code of Conduct for digital lenders — developed pre-SRO as a market benchmark that fed into the RBI's digital lending framework",
                    "Capacity building and collaborations on predatory lending, harassment and fraud concerns",
                    "Public trust positioning: consumer research and fair-recovery / collections norms advocacy",
                ],
            },
            {
                "h": "Policy & consultation engagement",
                "items": [
                    "Position papers and consultation responses to RBI, Ministry of Finance, MeitY and NITI Aayog",
                    "Roundtables with policymakers; the association advocated for the SRO-FT framework it now operates under",
                    "Publications: whitepapers and industry reports via its publications portal",
                ],
            },
        ],
        "gaps": [
            "The UFF Code of Conduct text is not published as a downloadable PDF on its site",
            "No published member disciplinary/enforcement log yet (SRO licence granted 10 Sep 2026 — early days)",
            "Member counts claimed in press (~200+) vs the site's own member wall (121 listed) — treat roster as directional",
        ],
        "sources": [
            ("UFF — Governance & Secretariat", "https://unifiedfintech.in/uff-governance-and-secretariat/"),
            ("UFF — Client Protection", "https://unifiedfintech.in/client-protection/"),
            ("UFF — Policy & Advocacy", "https://unifiedfintech.in/policy-advocacy/"),
            ("UFF — Publications", "https://unifiedfintech.in/publications/"),
        ],
    },
    "fidc": {
        "tagline": "NBFCs' SRO: the most active consultation respondent",
        "summary": (
            "FIDC (Section 8 company, incorporated 10 August 2011; recognised 3 October 2025) is the SRO "
            "for NBFCs — a broader, older sector than fintech lending. Its distinctive published work is a "
            "dense, dated trail of policy representations and member advisories, plus a governing council "
            "of 14 drawn from the biggest NBFC groups."
        ),
        "sections": [
            {
                "h": "Policy representations (selected, dated)",
                "items": [
                    "Feedback on RBI draft circular on Interest Rate on Loans — 11 Sep 2026",
                    "Revolving credit feedback — 27 Aug 2026; credit-risk implications of AGR — 11 Aug 2026",
                    "Responsible Business Conduct comments — 30 May 2026; eNACH feedback — 25 May 2026",
                    "Comments on prevention of financial fraud via voice/SMS — 24 Dec 2025",
                    "Regulatory parity for loan-against-shares (LAS) — 8 Dec 2025; pre-budget memorandum FY2026-27",
                    "Feedback on scale-based regulation amendments — 21 Nov 2025; lending to related parties — 20 Oct 2025",
                ],
            },
            {
                "h": "Member advisories (selected)",
                "items": [
                    "GST on co-lending arrangements — 13 Mar 2025",
                    "Fair Business Practices advisory — 23 Dec 2024",
                    "Code of Conduct — 11 Jan 2024; Vision Document for NBFCs — 11 Jan 2024",
                    "Outsourcing guidelines — 14 Oct 2022; microfinance code of conduct — 4 Oct 2022",
                    "COVID-19 moratorium advisory — 4 Apr 2020",
                ],
            },
            {
                "h": "Governance & advocacy machinery",
                "items": [
                    "Governing Council of 14: Chair Umesh Revankar (EVC, Shriram Finance), Vice-Chair Sanjay Gulati (Aditya Birla Finance), with representatives of Tata Sons, Bajaj Finance, Cholamandalam, L&T Finance, Piramal and others",
                    "CEO Raman Agrawal; committee structure covering regulations, taxation and state-level advocacy",
                    "Members asked to follow RBI's Fair Practices Code; FIDC positions itself as the NBFC sector's single voice",
                ],
            },
        ],
        "gaps": [
            "No public member roster — annual reports 2019-20 through 2025-26 contain no member list; the only register found is the 14-name Section-8 register in the 15th Annual Report (2018-19)",
            "Claims 400+ members in PR materials — unverifiable from its own publications",
            "Advisories are PDF-backed but many sit behind vague page links; some circulars are member-only",
        ],
        "sources": [
            ("FIDC — Representation", "https://www.fidcindia.org.in/representation/"),
            ("FIDC — Advisories", "https://www.fidcindia.org.in/advisory/"),
            ("FIDC — 22nd Annual Report 2025-26 (PDF)", "https://www.fidcindia.org.in/wp-content/uploads/2026/07/FIDC-22ND-ANNUAL-REPORT-2025-26.pdf"),
            ("FIDC — 15th Annual Report 2018-19 (member register)", "https://www.fidcindia.org.in/wp-content/uploads/2019/06/FIDC-15TH-ANNUAL-REPORT-2018-19.pdf"),
        ],
    },
    "srpa": {
        "tagline": "Payment aggregators' young SRO: founded by practitioners, one year old",
        "summary": (
            "SRPA (recognised 11 November 2025) is the youngest SRO — founded by payment-system operators, "
            "with CCAvenue's Vishwas Patel and BillDesk's M N Srinivasu on its board. Its first-year output "
            "is deliberately narrow: a code of conduct, market-integrity cautions, and DPIIT recognition "
            "plumbing."
        ),
        "sections": [
            {
                "h": "Code of conduct & standards",
                "items": [
                    "Code of Conduct adopted 8 Jan 2026 — fair merchant pricing, transparent onboarding, consumer data protection",
                    "EMI and chargeback standards in draft per its public materials",
                    "Marketplace-integrity positioning against onboarding fraud",
                ],
            },
            {
                "h": "Ecosystem & trust work",
                "items": [
                    "Caution circulars aligned with RBI and police cyber-CID warnings on payment fraud",
                    "DPIIT recognition application (industry status for PA sector)",
                    "Merchant-education advocacy; 18 payment operators on its partner wall (Razorpay, PhonePe, CRED, MobiKwik, Mswipe, SabPaisa, PayU and others)",
                ],
            },
        ],
        "gaps": [
            "Site is sparse — no roster page with membership categories or join dates; logos are the only roster signal",
            "No published enforcement or complaint-handling framework yet",
            "Founding date/entity registration details not published on the site",
        ],
        "sources": [
            ("SRPA — home (partner wall, code of conduct)", "https://srpa.org.in/"),
        ],
    },
    "mfin": {
        "tagline": "The original SRO experiment: NBFC-MFIs since 16 June 2014",
        "summary": (
            "MFIN (formed Sep 2013; RBI recognition letter dated 16 June 2014) was the first sector SRO "
            "under RBI's 2011 NBFC-MFI direction. Its SRO machinery — supervision, field visits, watchlists, "
            "client protection — is a decade old and is the template the fintech SRO-FTs are now judged "
            "against."
        ),
        "sections": [
            {
                "h": "SRO functions & supervision",
                "items": [
                    "Monitoring member compliance with RBI's NBFC-MFI direction and the industry Code of Conduct",
                    "Field assessment visits and a Self-Assessment & Monitoring Tool for members",
                    "Interest-rate monitoring and public rates disclosure for NBFC-MFIs",
                    "Early-warning watchlists; institutional-level risk analysis",
                ],
            },
            {
                "h": "Client protection & consumer touchpoints",
                "items": [
                    "Toll-free customer helpline 1800-102-1080 and customercomplaint@mfinindia.org for grievances against member NBFC-MFIs",
                    "Client-protection code framework aligned to global SMART-Campaign practice",
                    "Collector training and conduct standards for field recovery agents",
                ],
            },
            {
                "h": "Data & industry reporting",
                "items": [
                    "Quarterly industry data capture (Microscope) covering the large majority of NBFC-MFI loan volumes",
                    "Annual state-of-sector reporting; district-level outreach studies",
                ],
            },
            {
                "h": "Membership structure",
                "items": [
                    "53 primary NBFC-MFI members; an Associate programme admits banks, SFBs, wholesale/direct NBFCs, credit bureaus, insurers, payment banks, fintechs and telcos — which is why its site wall shows ~84 organisations",
                    "Governance: board chaired by Devesh Sachdev (Fusion Microfinance founder) with former RBI ED Arnab Roy as independent member; CEO Dr Alok Misra",
                ],
            },
        ],
        "gaps": [
            "Primary-member roster (the 53) is not published as a clean list; the public wall mixes members and associates",
            "Enforcement actions and watchlist contents are not public",
        ],
        "sources": [
            ("MFIN — SRO recognition (16 Jun 2014)", "https://mfinindia.org/about/sro"),
            ("MFIN — Client protection & associates", "https://mfinindia.org/clientprotection"),
            ("MFIN — Leadership", "https://mfinindia.org/about/leadership"),
        ],
    },
    "sadhan": {
        "tagline": "Community-development finance's SRO: standards since 2015",
        "summary": (
            "Sa-Dhan (RBI recognition 2015) is the SRO for the microfinance and community-development "
            "finance sector. Its published SRO practice is the most tool-like of the older SROs: field "
            "assessment, self-assessment instruments, district-level studies and an annual statistical "
            "benchmark (Bharat Microfinance Report)."
        ),
        "sections": [
            {
                "h": "SRO tools & supervision",
                "items": [
                    "Regular Field Assessment Visits to member MFIs",
                    "Self-Assessment & Monitoring Tool; institutional-level risk analysis",
                    "Credit Assessment Framework; district-level microfinance status studies",
                    "Compliance Officer mechanism anchoring SRO processes",
                ],
            },
            {
                "h": "Consumer touchpoints",
                "items": [
                    "GRM toll-free grievance number 1800-8899-270",
                    "Industry Code of Conduct; Sankalp guardrails for sector conduct",
                    "District-wise interest-rate tracking and publication",
                ],
            },
            {
                "h": "Data & benchmarking",
                "items": [
                    "Bharat Microfinance Report — the sector's annual statistical benchmark",
                    "Quarterly microfinance reports; '10 Years As SRO' retrospective (2015-2025)",
                ],
            },
        ],
        "gaps": [
            "Member roster not published (claims 200+ institutions in PR materials)",
            "GRM outcomes/complaint statistics not published",
        ],
        "sources": [
            ("Sa-Dhan — SRO", "https://www.sa-dhan.net/what-we-do/sro/"),
            ("Sa-Dhan — 10 Years As SRO", "https://www.sa-dhan.net/10-years-sro-2/"),
        ],
    },
    "fedai": {
        "tagline": "Authorised dealers' rulebook: 30 years of forex standards",
        "summary": (
            "FEDAI (established 12 Feb 1995; recognised as AD SRO 14 January 2026) has long set the rules "
            "for forex business among banks — quoting practices, risk management, broker accreditation — "
            "and runs the sector's training machinery. Recognition formalised its role in RBI's new "
            "AD-SRO framework."
        ),
        "sections": [
            {
                "h": "Rule-making & standards",
                "items": [
                    "Frames rules for forex business inter se ADs (with RBI approval): quotation, documentation, risk practices",
                    "Accreditation framework for foreign-exchange brokers",
                    "Daily reference-rate and market-convention publications (incl. USD/INR 10-year LAV)",
                ],
            },
            {
                "h": "Training & committees",
                "items": [
                    "Workshop calendar: 5-day orientation programmes, FX-derivative workshops with Bloomberg, TBML counter-measures, LC documentation",
                    "Technical Advisory Committee (16 banks) and an Education Committee; local committees across centres",
                    "Managing Committee chaired by State Bank of India, with DBS Bank India as Vice Chairman",
                ],
            },
            {
                "h": "Membership",
                "items": [
                    "108 Authorised Dealer members with LEIs (published list with categories: foreign banks incl. branches, PSBs, private banks, SFBs, others)",
                    "Liaison role between RBI and ADs on forex-market operations",
                ],
            },
        ],
        "gaps": [
            "Rule books and circular archives require member access; the public site publishes only summaries",
            "As an AD SRO recognised in Jan 2026, its SRO-period enforcement record is still building",
        ],
        "sources": [
            ("FEDAI — About", "https://www.fedai.org.in/InnerPageContent.aspx?Cid=1&SCid=0&SSCid=0"),
            ("FEDAI — Managing Committee", "https://www.fedai.org.in/InnerPageContent.aspx?Cid=2&SCid=2&SSCid=0"),
            ("FEDAI — Member banks", "https://www.fedai.org.in/InnerPageContent.aspx?Cid=2&SCid=1&SSCid=0"),
            ("FEDAI — Workshops", "https://www.fedai.org.in/InnerPageContent.aspx?Cid=5&SCid=16&SSCid=0"),
        ],
    },

    "fimmda": {
        "tagline": "The bond market's own rulebook: valuations, market practices and standard agreements",
        "summary": (
            "FIMMDA (incorporated 4 May 1998) is the oldest market body in the register and the first "
            "SRO recognised in the financial markets (7 May 2025, RBI PR 2025-2026/274) under RBI's "
            "August 2024 financial-markets SRO framework. Its 116 listed members span public, private, "
            "foreign, small-finance and payments banks, primary dealers, insurers, development "
            "institutions and CCIL."
        ),
        "sections": [
            {
                "h": "What FIMMDA does",
                "items": [
                    "Principal interface with RBI, SEBI and the Ministry of Finance for the fixed income, money and derivatives markets",
                    "RBI-mandated valuation of government bonds, corporate bonds and securitised papers — the daily prices that bank and primary-dealer portfolios are marked at",
                    "Standardisation of market practices: FIMMDA Operational Circulars, the Handbook of Market Practices, standard legal agreements (MRA, GMRA, CDS) and the Code of Fair Practices",
                    "Developmental role: introduced benchmarks (MIBOR history), new products (CPs, securitised papers, OIS) and runs an extensive training programme",
                ],
            },
            {
                "h": "Membership",
                "items": [
                    "116 members in its published list (PDF dated 8 May 2025): 12 public-sector banks, 21 private banks, 34 foreign banks, 7 primary dealers, 5 financial institutions (Exim, NABARD, NHB, SIDBI, NaBFID), 20 insurers, 11 SFBs, 3 payments banks, CCIL, IFCI and IIFCL",
                    "Fee model: Rs 2.5 lakh one-time registration + Rs 2.5 lakh annual membership (+GST) — an institution-funded body",
                    "Accredited brokers in the interest-rate-derivatives voice market are governed by a separate accreditation framework and code of conduct",
                ],
            },
            {
                "h": "SRO transition since recognition",
                "items": [
                    "Site header now brands FIMMDA a 'Self-Regulatory Organisation in the Financial Markets Regulated by RBI'",
                    "Disciplinary Committee of the Board constituted 1 Sep 2026 (Art. 34 AoA): chaired by independent director Manoj Rane, with nominee directors from Union Bank and ICICI Bank",
                    "Nine-member Board (Sep 2026) led by Shamsher Singh (SBI DMD, Global Markets) as Chairman and Neeraj Gambhir (Axis) as Vice Chairman, with three independent directors",
                    "Standing committees cover new products, technical market practices, membership, valuation, accreditation of brokers, CDS and skill development",
                ],
            },
        ],
        "gaps": [
            "Overview page still claims a '115 member strong' body with category counts that do not match its own 116-row PDF — and the list has not been refreshed since 8 May 2025",
            "No public disciplinary actions, consultation responses or member circular archive without login; circulars are one-page PDFs",
            "Legacy frameset website: rosters and disclosures ship as PDFs, not structured pages",
        ],
        "sources": [
            ("RBI press release — FIMMDA recognised as SRO (7 May 2025)", "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60389"),
            ("FIMMDA member list (PDF, 8 May 2025)", "https://www.fimmda.org/UploadPopupPageFiles/MembersList_8May2025.pdf"),
            ("FIMMDA — Board of Directors", "https://www.fimmda.org/PageContent.aspx?Iid=NDk="),
            ("FIMMDA — Committees", "https://www.fimmda.org/PageContent.aspx?Iid=MTA3"),
            ("FIMCIR/2026-27/20 — Constitution of Disciplinary Committee (1 Sep 2026)", "https://www.fimmda.org/UploadPopupPageFiles/FIMCIR_2026_27_20.pdf"),
        ],
    },
}
