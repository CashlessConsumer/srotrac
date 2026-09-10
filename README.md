# SROTrac

**Live:** https://srotrac.cashlessconsumer.in · repo: `CashlessConsumer/srotrac` (GitHub Pages, workflow deploy)

Knowledge repository tracking India's **fintech self-regulatory organisations (SROs)** — the register, member rosters, governance, activity, and the regulatory timeline — run by CashlessConsumer.

RBI created a Self-Regulatory Organisation framework for the fintech sector (draft Jan 2024) and has since recognised two SRO-FTs. SROTrac records who they are, and — the part that matters for a consumer desk — **who their members are**, because membership is where industry consensus on fees, grievance handling, and codes of conduct actually gets formed.

## Deployment

- Repo: `CashlessConsumer/srotrac` → GitHub Pages, workflow deploy (`.github/workflows/deploy.yml`).
- Fallback while DNS is pending: https://cashlessconsumer.github.io/srotrac/
- Custom domain `srotrac.cashlessconsumer.in` is set in repo Pages config + `CNAME`.
- **DNS TODO:** zone `cashlessconsumer.in` is on Netlify DNS (NS1). The stored
  `NETLIFY_AUTH_TOKEN` cannot write DNS records (records API 404s). Add manually:
  Netlify dashboard → Domain management → cashlessconsumer.in → DNS → new record:
  `CNAME`, host `srotrac`, value `cashlessconsumer.github.io`, TTL 3600.
  HTTPS cert provisions automatically after DNS propagates.

## The SROs tracked

| SRO | Full name | Recognised | Website |
|-----|-----------|-----------|---------|
| **FACE** | Fintech Association for Consumer Empowerment | 28 Aug 2024 (first SRO-FT) | https://faceofindia.org |
| **UFF** | Unified Fintech Forum (formerly DLAI) | 10 Sep 2026 (second SRO-FT) | https://unifiedfintech.in |

`data/sros.csv` holds the register. It also carries two **related** RBI SROs for context — they are not fintech SRO-FTs but they sit in the same regulatory family and are often compared to FACE/UFF:

| SRO | Sector | Recognised | Website | Status |
|-----|--------|-----------|---------|--------|
| **FIDC** — Finance Industry Development Council | NBFC | 3 Oct 2025 | https://www.fidcindia.org.in | related |
| **SRPA** — Self-Regulated PSO Association | Payment system operators | 11 Nov 2025 | https://srpa.org.in | related |

SRPA lists 18 PSO members (BillDesk, Razorpay, PhonePe, CRED, MobiKwik, Mswipe, Infibeam Avenues, Euronet, SabPaisa, Spice Money, …), captured in `data/srpa_members.csv`. These names were decoded from the logo images on the site, which are not text. FIDC publishes no member roster (see above), so it has no members file.

Add new SROs there.

## Data

| File | Contents |
|------|----------|
| `data/sros.csv` | SRO register: id, name, abbr, website, source page, recognition, date, status |
| `data/face_members.csv` | FACE members (name, website) |
| `data/uff_members.csv` | UFF members (name, website, member_type, logo_file) |
| `data/srpa_members.csv` | SRPA PSO members (name, website, logo_file) |
| `data/srotrac.duckdb` | `sros` + `members` tables, built from the CSVs |
| `docs/members.md` | Human-readable member listings + overlap between the two SROs |
| `data/raw/` | Raw HTML snapshots the lists were parsed from |

Snapshot (2026-09-10): **FACE 85 members**, **UFF 121** (103 members + 18 associates), **SRPA 18 PSO members** — 224 rows total, **27 organisations appear in more than one SRO** (23 in both FACE and UFF).

## Build

```bash
python3 scripts/build.py     # parse data/raw/*.html -> CSVs -> DuckDB
```

The SRPA list is parsed by matching the partner logo filenames on the homepage against a name map (filenames like `oncerto.jpg` are truncated). The FACE list is parsed from image `alt` text + surrounding links on `/membership/`. The UFF list comes from the linked logo gallery on the homepage; several UFF logos use opaque filenames (`117.png`, `128-1.png`, …), so `scripts/build.py` carries a name map for those. Verify a mapping before trusting it.

Sources can drift — re-snapshot the raw HTML before rebuilding if the counts move.

## Querying

```bash
duckdb data/srotrac.duckdb -c "SELECT sro, count(*) FROM members GROUP BY 1;"
duckdb data/srotrac.duckdb -c "SELECT member_name FROM members GROUP BY 1 HAVING count(DISTINCT sro)>1;"
```

## Caveats

- **UFF `member_type` is heuristic.** The site does not label tiers; entities that are clearly vendors, consultancies, law firms, or bureaus (KPMG, BDO, EY, Khaitan, LexisNexis, TeleSign, CRIF, …) are tagged `associate`, everything else `member`.
- **FACE does not publish a tier or category** — all rows are `member`.
- Membership lists are marketing pages and are not authoritative; treat the roster as directional, not as a filing.
