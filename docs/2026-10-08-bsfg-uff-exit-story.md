# The Silent Exit — story draft

_Status: DRAFT — not wired into any site build. Right-of-reply SENT 2026-10-08: BSFG → connect@bsfg.finance (Gmail msg 1a11a57879ea5c63); UFF → contact@unifiedfintech.in (Gmail msg 1a11a5786cebfcd8). Response deadline: end of day IST, Sunday 11 October 2026._
_Angles: A (silent exit) spine · B (ZestMoney lineage) the who · C (unregulated layer) the so-what · E (agentic method) sidebar._

---

## About SROTrac (introduction — required in every surface this story runs on)

**About SROTrac.** This story was found, not assigned. SROTrac is CashlessConsumer's agentic tracker of India's financial self-regulatory organisations — an automated watchtower that fetches the published member rosters, governance pages and activity feeds of all 18 recognised SROs across RBI, SEBI, IRDAI and IBBI every day, with no reporter on the beat. It is the second layer of CashlessConsumer's sousveillance stack: RegTrac watches the rule-writers (the statutory regulators), SROTrac watches the rule-borrowers (the industry bodies that write the codes of conduct), and LobbyWatch watches the rule-buyers (the interests trying to shape both). Nobody announced the exit at the centre of this story. It exists as a fact only because SROTrac's daily capture job fetched the same page two days in a row and a version-control diff showed one row missing. Every number in this story traces to a timestamped, committed capture at srotrac.cashlessconsumer.in — the evidence ledger is published alongside the story.

## Working title options

1. **The Silent Exit** — UFF loses its first member, and won't say why
2. **One Row Missing** — how India's second fintech SRO dropped a member without a word
3. **ZestMoney's Second Act, Interrupted** — the ex-ZestMoney venture that joined the SRO wall and quietly left

## Lede (working)

At some point on 30 September 2026, a page edited on the Unified Fintech Forum's website dropped one row from its member wall. The row said "BSFG Finance." It had been there on every one of SROTrac's daily captures since 10 September — the day the RBI recognised UFF as India's second self-regulatory organisation for fintech. It was gone by the next morning's fetch. The roster went from 121 to 120. No announcement followed, from UFF or from BSFG. Twenty-one days into its life as a regulator-recognised SRO, India's fintech industry body had its first membership exit — and said nothing about it.

## Section 1 — The exit (Angle A)

- Facts: BSFG Finance present in captures 2026-09-10 → 2026-09-30 (git `248e7c9`); absent from 2026-10-01 fetch (`c09d909`); confirmed absent through 2026-10-07 (`f09e81a`, four consecutive daily fetches). UFF's page schema metadata shows a modification on 30 September. About page now reads: "At present UFF has 120 members."
- Register-level effect: the cross-SRO register's total listed memberships fell from 774 to 773; overlap count held at 79 because BSFG sat only in UFF.
- The transparency point: the exit is visible only because UFF publishes its roster — 8 of the register's 18 SROs publish nothing. But visibility without a stated reason is half the protection. A consumer cannot tell whether BSFG resigned, lapsed, or was removed. SROs that enforce conduct codes should say so when membership ends.

## Section 2 — Who left (Angle B)

- BSFG = Berkeley Square Finance Group, Delaware-registered 2024. A platform providing "balance sheet and capital solutions" — debt placement and capital-markets access — for fast-growing lenders.
- Founded by Lizzie Chapman, co-founder/CEO of ZestMoney, India's first big BNPL: raised ~$140M (Goldman Sachs, PayU, Zip, Quona), peaked at $450M valuation.
- Collapse mechanics: RBI's June 2022 PPI credit-line ban gutted the core product; September 2022 digital-lending guidelines tightened the LSP/FLDG model; PhonePe's $200–300M acquisition collapsed March–April 2023 over due diligence (reported high defaults, $35–40M debt liabilities). Founders out May 2023; shutdown announced 5 December 2023 (150 staff); January 2024 fire sale to DMI Group — brands + platform + talent; TechCrunch reported every investor lost money.
- Chapman's arc: ZestMoney → Swiffy Labs (Jio-backed, with ZestMoney cofounder Anantharaman) → quit Feb 2025 → BSFG (started late 2024 as partner). BSFG's legal head: Hamsaanandini Nanduri, ex-ZestMoney AGC (via Akaaya Law). Risk/tech leads ex-RBL/Amex/Stashfin.
- India entity: BSFG Fund Manager Private Limited, CIN U70200DL2025PTC452362, incorporated 30 July 2025, ROC Delhi, WeWork Eldeco Centre Malviya Nagar; ₹10L authorised / ₹1L paid-up; NIC 70200 (head office/management consultancy). No visible NBFC or other RBI registration.
- The fair question: the person who ran India's biggest BNPL collapse now sells capital resilience to its successors. What changed in the model? (Comment requested; see drafts below.)

## Section 3 — The gap (Angle C)

- RBI's SRO-FT framework scopes membership to fintechs regulated by RBI, excluding banks. A ₹1-lakh consultancy-class subsidiary of a Delaware holdco was an odd fit for that wall.
- The deeper point: capital arrangers and fund managers — the layer that decides which lenders get funded and which die like ZestMoney did — sit outside SRO oversight and largely outside direct regulation. RBI's own digital-lending framework flagged unregulated entities in risk-sharing (FLDG) structures.
- Policy hook: a live question for the SRO framework's periodic review — should the capital side of the credit chain be visible to the SROs whose members it funds?

## Sidebar — How the story was found (Angle E)

- Daily cron fetches unifiedfintech.in → CSV committed to a public git repo each run.
- The 1 October commit's diff: one deleted row. Schema metadata in the page HTML dated the edit to 30 September.
- No press release, no news coverage found on the exit (searched [date range]).
- Framing for the Agentic Journalism course (future public case study): the monitor is the reporter; the diff is the tip; the journalist's job is the comment request and the context.

## Evidence ledger

| # | Claim | Artifact |
|---|-------|----------|
| E1 | BSFG listed 10–30 Sep 2026, 121 members | `Projects/srotrac/data/uff_members.csv` @ git b6d61de (10 Sep), 248e7c9 (17 Sep, row `UFF,BSFG Finance,https://bsfg.finance/,member,BSFG.png`) |
| E2 | Absent from 1 Oct 2026, 120 members | same file @ c09d909 (1 Oct), f09e81a (7 Oct) |
| E3 | UFF page edited 30 Sep; "At present UFF has 120 members" | `data/raw/uff_home.html` capture; https://unifiedfintech.in/about-us-2 |
| E4 | Register total 773; BSFG single-SRO (overlap unchanged at 79) | SROTrac register build, weekly #5 |
| E5 | BSFG self-description | https://bsfg.finance/about |
| E6 | Chapman founded BSFG late 2024 as partner; ex-ZestMoney CEO; Swiffy exit | https://economictimes.indiatimes.com/tech/technology/reliance-backed-swiffy-labs-cofounder-lizzie-chapman-steps-down/articleshow/118208212.cms |
| E7 | India entity details | https://www.instafinancials.com/company/bsfg-fund-manager-private-limited-U70200DL2025PTC452362 |
| E8 | Team (Nanduri ex-ZestMoney legal; Dutta ex-RBL/Amex/Stashfin; Sood ex-Stashfin) | https://bsfg.finance/team |
| E9 | ZestMoney collapse timeline (PPI ban, guidelines, PhonePe walkaway, shutdown, DMI fire sale, investors wiped) | yourstory.com/2023/12/zestmoney-to-shut-down-operations-lay-off-150-employees · moneycontrol.com/news/business/startup/phonepe-calls-off-deal-with-zest-money-over-due-diligence-concerns-10335551.html · techcrunch.com/2024/01/17/goldman-sachs-backed-zestmoney-once-valued-at-450-million-sold-to-dmi-in-fire-sale |
| E10 | SRO-FT membership scope (RBI-regulated fintechs, excluding banks) | RBI Framework for SRO-FT, 30 May 2024 — fidcindia.org.in/wp-content/uploads/2019/06/RBI-FINTECH-SRO-FRAMEWORK-30-05-24.pdf |

## Right-of-reply (SENT 2026-10-08 — BSFG msg 1a11a57879ea5c63 · UFF msg 1a11a5786cebfcd8; deadline EOD IST 11 Oct 2026)

### To Lizzie Chapman / BSFG — `connect@bsfg.finance`

> Subject: Comment request — UFF membership and Berkeley Square Finance Group in India
>
> Dear BSFG Team / Ms Chapman,
>
> I write for Cashless Consumer, an Indian consumer collective covering digital finance (cashlessconsumer.in). Our story is based on SROTrac, our automated public register of India's financial self-regulatory organisations (srotrac.cashlessconsumer.in), which fetches and archives SRO member rosters daily. SROTrac recorded "BSFG Finance" as a listed member of the Unified Fintech Forum's published roster on every daily capture from 10 September 2026; it no longer appears from the 1 October 2026 capture. Neither UFF nor BSFG has publicly stated a reason.
>
> We plan to publish a story this week and would value your comment on:
> 1. Whether BSFG resigned, lapsed, or was removed from UFF membership, and the reason.
> 2. BSFG's current activities in India, including BSFG Fund Manager Private Limited's mandate and any arrangements with Indian lenders (debt placement, co-lending, FLDG or other risk-sharing structures).
> 3. Your view on whether capital-side intermediaries such as BSFG should fall within SRO-FT oversight, which RBI's framework currently scopes to RBI-regulated fintechs.
>
> We will reflect any response received by end of day IST on 11 October 2026 in full and fairly.

### To UFF secretariat — contact@unifiedfintech.in (site footer mailto, found via agent-browser 2026-10-08; site blocks sandbox curl)

> Subject: Comment request — BSFG Finance exit from UFF member roster
>
> Dear UFF secretariat,
>
> SROTrac, Cashless Consumer's automated register of India's financial self-regulatory organisations (srotrac.cashlessconsumer.in), archives UFF's published member roster daily. Our records show BSFG Finance listed through the 30 September 2026 capture and absent from 1 October 2026 — the first roster change since RBI's 10 September recognition of UFF as an SRO-FT. We plan to publish on this and would value your comment on:
> 1. The reason for BSFG's removal (resignation, lapse, or removal by UFF).
> 2. UFF's membership criteria for entities that are not themselves RBI-regulated, and whether BSFG met them at the time of listing.
> 3. Whether UFF has a policy of disclosing membership exits and their nature, given its role as an RBI-recognised SRO-FT.
>
> We will reflect any response received by end of day IST on 11 October 2026 in full and fairly.

## Reply log

- **2026-10-08** — both queries sent from cashlessconsumerin@gmail.com (as "Cashless Consumer"). BSFG: `connect@bsfg.finance`, thread 1a11a57879ea5c63. UFF: `contact@unifiedfintech.in`, thread 1a11a5786cebfcd8. Deadline: EOD IST 2026-10-11.
- One-shot follow-up agent runs 2026-10-12 09:30 IST: checks both threads for replies, updates this log, emails status. No further sends or publishing without approval.

## Guardrails

- No claim about why BSFG exited — we don't know; the story's point is that nobody does.
- ZestMoney framed as regulatory + commercial collapse, not fraud.
- Borrower complaints (Trustpilot/Reddit) stay anecdotal and clearly labelled; no pattern claim.
- Every figure keyed to the ledger above; unverified items stay out of the published story.
