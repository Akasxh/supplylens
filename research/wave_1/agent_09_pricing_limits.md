# Agent 09 — Crustdata Pricing, Rate Limits, Quotas

**Wave**: 1  
**Date**: 2026-04-19  
**Scope**: Every hard number governing what you can build on top of the Crustdata API. Includes Crustdata's own structure plus the competitive price envelope (Apollo, PDL, Clearbit/HubSpot, Coresignal, Clay, ZoomInfo, Harmonic) so the relative economics are clear.

---

## 0. Executive summary (the numbers that decide everything)

| Axis | Crustdata reality | Implication |
|---|---|---|
| **Public $ price list** | **None.** No tier dollar amounts on `crustdata.com/pricing`. Sales-gated. | You cannot self-serve a per-seat SaaS over it without a contract-size negotiation. |
| **Credit unit cost (documented)** | Per-endpoint credit costs ARE public; dollar/credit is NOT. Third-party estimates imply **~$0.03–$0.04 per API lookup** (see §1, §5). | At $0.04/full-profile-enrich a $10/mo consumer app can afford ~250 lookups before margin dies. |
| **Cheapest documented entry** | **Free tier exists** (permanent, not a trial) — exact credit count NOT published. ~$95–$200/month is the commonly cited "Starter" floor per 3rd-party aggregators. | Real pilot projects that need ≥1 credit/user/day will blow past the free tier. |
| **Rate limit** | **15 requests / minute** on most self-serve endpoints (published). | 900/hour ceiling. A background batch job hits the wall at ~22k records/day. |
| **Credit expiration** | **6 months from purchase date** (published). | No "buy once, use forever" — encourages treadmill. |
| **Enterprise floor** | Third-party estimates: **$1,000–$3,000/mo (Growth)**, **$5,000+/mo (Enterprise/bulk)**. | Any product whose unit economics need <$1,000/mo of data is probably killed unless ≥ $200/mo tier is real. |
| **Enterprise-only endpoints** | `/professional_network/*` live endpoints are enterprise-gated. | Real-time LinkedIn-style lookups are not available at the free/starter tier. |

**The brutal one-line takeaway**: Crustdata is priced for B2B GTM teams running 4–6 figure monthly contracts. Consumer-facing per-user apps are structurally killed unless the per-user value is ≥ $30/mo.

---

## 1. Crustdata API pricing — what is actually published

Source of record: [docs.crustdata.com/general/pricing](https://docs.crustdata.com/general/pricing). Dollar tiers are NOT on this page; only per-endpoint credit costs. Dollar/credit conversion is sales-gated.

### 1.1 Self-serve endpoint credit costs (all published)

| Endpoint | Credit cost | Notes |
|---|---|---|
| `/person/search` | **0.03 credits / result** | Note: fractional. 100 results = 3 credits. |
| `/person/search/autocomplete` | **Free** | |
| `/person/enrich` | **1–7 credits / record** | Additive — see §1.2 |
| `/company/search` | **0.03 credits / result** | |
| `/company/search/autocomplete` | **Free** | |
| `/company/enrich` | **2 credits / record** | Flat. |
| `/company/identify` | **Free** | Helpful — domain-to-ID resolution costs nothing. |
| `/job/search` | **0.03 credits / result** | |
| `/web/search/live` | **1 credit / query** | Web search API (the token-efficient one from the Show HN) |
| `/web/enrich/live` | **1 credit / page** | URL fetcher — extracts company/person data from a URL |
| `/dev_platform/enrich` | (credit cost not listed but rate-limited at 15 rpm) | |
| `/employee_review/enrich` | (credit cost not listed, rate-limited at 15 rpm) | |
| `/social_post/professional_network/*` | enterprise-only | |

### 1.2 Person enrich additive pricing

Base = 1 credit; stack these:

| Add-on | Additional credits |
|---|---|
| Personal email data | **+2** |
| Phone data | **+2** |
| Business email data | **+1** |
| Developer platform data | **+1** |
| **Max per record** | **7 credits** |

Canonical examples Crustdata documents:
- Basic lookup: **1 credit**
- Sales outreach (base + business email): **2 credits**
- Full prospecting (base + business email + phone): **4 credits**
- Full payload (everything): **7 credits**

### 1.3 Enterprise live endpoints (gated)

| Endpoint | Credit cost |
|---|---|
| `/person/professional_network/search/live` | **2 credits / profile** |
| `/person/professional_network/enrich/live` | **7 credits / profile** |
| `/company/professional_network/search/live` | **2 credits / company** |
| `/job/professional_network/search/live` | **2 credits / result** |
| `/professional_network/search/autocomplete` | **Free** |

Note the "live" endpoints are the real-time professional-network (LinkedIn-style) lookups. 7 credits per LinkedIn enrich is the most expensive operation in the catalog.

### 1.4 Preview mode

From the docs (company enrichment page): *"Preview mode returns only basic profile fields and charges 0 credits. Cannot be combined with enrich_realtime."* — Good to know there is a zero-cost sanity-check path before you burn credits.

### 1.5 What is NOT public

- Named tier prices (no "Starter at $X/mo" on the pricing page)
- Dollar value of 1 credit
- Overage pricing
- SLA / uptime guarantees
- Concurrent connection limits
- Per-day / per-month request ceilings
- Webhook / streaming pricing (webhooks are marketed as a delivery channel but no pricing is published)
- Bulk-flat-file pricing (sales-gated only)

---

## 2. Rate limits (published)

Source: [docs.crustdata.com/general/rate-limits](https://docs.crustdata.com/general/rate-limits).

- **Default rate limit: 15 requests / minute**, applied per API key, documented across these 12 endpoints:
  - `/person/search/autocomplete`
  - `/person/professional_network/enrich/live`
  - `/person/professional_network/search/live`
  - `/job/professional_network/search/live`
  - `/job/search`
  - `/web/search/live`
  - `/web/enrich/live`
  - `/dev_platform/enrich`
  - `/employee_review/enrich`
  - `/social_post/professional_network/enrich/live`
  - `/social_post/professional_network/search/live`
  - `/professional_network/search/autocomplete`

- **429 response code** returned on limit breach.
- Docs note: *"Exact per-endpoint limits can change by plan and endpoint version"* — meaning enterprise plans likely get higher limits but nothing is published.
- **No published**: rps, daily, concurrent connection, or burst numbers.

**Implication**: at 15 rpm → 900 rph → 21,600 requests/day maximum. That is *the absolute ceiling* on what a single API key can drive through the self-serve plan. A nightly enrichment batch of 50k records hits the wall and forces either multiple keys or an enterprise uplift.

---

## 3. Quota resets, overages, SLAs

All **unpublished**. Third-party reporting:

- **Credit validity**: **6 months from purchase** (published). So there is an effective "use it or lose it" on a half-year cadence, not a rolling annual.
- **Overage pricing**: No public rate card. prospeo.io writeup: *"Credit-based billing without published per-credit rates makes cost forecasting difficult. Credits burn fast with AI agent usage at scale."*
- **Quota reset**: Monthly billing is standard; annual is offered. Rollover not publicly documented.
- **Burst allowances**: None published.
- **SLA / uptime**: No public SLA page. Standard enterprise B2B assumption is 99.5%–99.9% on negotiated contracts, but this is NOT guaranteed publicly.

---

## 4. Free tier / trial

- **Exists**: *"Real-time API access — Try it for free"* is on the crustdata.com/pricing landing page. Credit-card-free.
- Described by third parties as a *"permanent free tier"* (not time-limited), with *"usage limits"* left unspecified.
- **Exact credit count at signup: not published.** Community reports vary; one prospeo.io-adjacent mention cites "100 credits/month" but this is unconfirmed and conflicts with a claim elsewhere that Crustdata has "no free tier at all" — the landing page CTA "Try it for free" plus the docs saying "see Pricing before you build a live workflow" strongly implies there IS a free tier, but the magnitude is unknown until signup.

### What the signup wall likely looks like (inferred)

Best inference combining the docs tone + third-party aggregator reports + the "permanent free tier" framing:
- **Likely 100 credits/month, free forever**, enough to:
  - 3,333 search results (at 0.03/result) OR
  - 100 basic person lookups OR
  - ~14 full-payload person enriches (at 7 credits) OR
  - 50 company enrichments OR
  - 100 web searches
- This is just about enough to *evaluate* the API, not to run a product on it.

(Treat the 100/mo figure as unconfirmed-inferred, not published.)

---

## 5. The missing piece: what is 1 credit worth in dollars?

Crustdata does not tell you. But you can triangulate:

- **Third-party "Starter" estimate**: **$95–$200/month** (prospeo.io, iseoai.com, skywork.ai aggregators; numbers float between $95 and $200 depending on the source — the $95 number comes from skywork.ai saying "starting around $95/month for extra searches"; $200 comes from gurusup.com's comparison table).
- **Growth teams**: **$1,000–$3,000/month** (industry-standard for this tier of enrichment API).
- **Enterprise/bulk**: **$5,000+/month**.

### The $0.04/lookup benchmark (Show HN evidence)

A competitor ("Companies.social", [HN 47387103](https://news.ycombinator.com/item?id=47387103), March 2026) launched explicitly branded as *"company enrichment without the $0.04/lookup tax"*, citing Crustdata by name:

> "I was using Crustdata and IcyPeas and kept running into two problems: the per-lookup cost adds up fast, and the data is often 6–9 months stale." — ptrtht, HN comment 47387130

This is the **single most specific community-reported dollar figure**: **~$0.04 per company lookup** on Crustdata. If that number is right, then:

- 1 credit ≈ $0.02 (since company enrich = 2 credits → $0.04)
- A full 7-credit person enrich = ~$0.14
- 1000 lookups/day = $40/day = ~$1,200/month, matching the "Growth tier $1,000–$3,000/mo" band.

**Treat $0.02/credit as the best community-derived peg. It's consistent across the Growth tier estimates and the HN comment.**

### Cross-checks

At $0.02/credit:
- `/person/search` at 0.03 credits = ~$0.0006/result (search is effectively free)
- `/company/identify` = free
- `/person/enrich` basic = ~$0.02/profile
- `/person/enrich` full = ~$0.14/profile
- `/web/search/live` = ~$0.02/query
- Free tier of 100 credits = ~$2 of value (plausible evaluation-only budget)

---

## 6. Data export / bulk download

- Sales-gated. *"Flat file company & people data"* is a separate product line: monthly-refresh dumps of millions of records as CSV/JSON.
- One aggregator ([saasworthy](https://www.saasworthy.com/product/crustdata)): *"unlimited data without rate limits for products needing high volumes, with data accessible via a flexible REST API and data feed (including CSV) for bulk delivery. Customers can combine the full dataset delivery (refreshed monthly, quarterly, or yearly) with API usage to balance cost and freshness."*
- **No published price.** Third-party estimate: $5k+/month.
- **Key insight**: bulk + API hybrid is actively positioned, so a high-volume product can buy the monthly snapshot and then API-top-up only fresh records. This is where the economics get better for high-volume plays.

---

## 7. Webhook / streaming pricing

- Crustdata markets webhooks publicly (Product Hunt tagline: *"Real-time people and company data via APIs and webhooks"*).
- **No per-event fee published.** Likely included in enterprise contracts. Not available on self-serve from the public docs.

---

## 8. Endpoint cost variation (what to avoid)

Biggest credit sinks:

1. **Full person enrich (7 credits)** — ~$0.14 at estimated $0.02/credit. If your product runs this on every lead, 10,000 leads/month = $1,400/month alone.
2. **`/person/professional_network/enrich/live` (7 credits + enterprise-only)** — doubly expensive because it requires an enterprise contract.
3. **Company enrich (2 credits)** — ~$0.04. Acceptable but multiplies fast.

Cheap operations (use these generously):
- `/company/identify` — free; domain → ID resolution before deciding to enrich
- `/person/search/autocomplete`, `/company/search/autocomplete` — free
- Preview mode on enrichment — 0 credits, basic fields only

Design principle: **always hit `/identify` or `/search` before `/enrich`**. The search-then-enrich pattern costs 0.03 + 1 = 1.03 credits for a basic lookup, vs. 7 credits for a blind full-enrich.

---

## 9. Free trial / current promo signals

Known:
- Permanent free tier (unknown credit count, likely ~100/mo).
- *"Try it for free"* CTA on pricing page — no credit card required.
- Founder-level outreach available (contact in docs: `gtm@crustdata.co`, `abhilash@crustdata.com`).
- Crustdata is a YC F24 company, which historically means they are aggressive on early-customer deals (YC credits + founder-level customer acquisition).
- YC alumni programs and HN presence suggest startup credit promos are available on request but not publicly listed.

Not found: time-limited trials, signup bonuses, public credit codes, partner offers.

---

## 10. Competitor pricing — the relative economics

All dollar figures are current-public as of 2026-04. Where multiple tiers exist, the cheapest usable API tier is shown.

### 10.1 Apollo.io ([docs.apollo.io/docs/api-pricing](https://docs.apollo.io/docs/api-pricing), [Salesmotion 2026 breakdown](https://salesmotion.io/blog/apollo-pricing))

| Plan | Price | Credits | Notes |
|---|---|---|---|
| Free | $0 | 10,000 email credits, 5 mobile, 10 export | Monthly, resets |
| Basic | **$49/user/mo (annual)** / $59 monthly | +1,000 email, 75 mobile, 2,000 export | |
| Professional | **$79/user/mo (annual)** / $99 monthly | +100 mobile, 2,000 export, 10k data credits/yr | Most popular. Includes dialer. |
| Organization | **$119/user/mo (annual)** / $149 monthly | More of everything, international dialer | 3-user min |

**API-specific**:
- Unlimited-plan API credits = min($ paid / $0.025, 1M credits/year)
- Overage: **$0.20 / credit**, min 250 monthly or 2,500 annual
- Phone number = 8 credits; full enrichment = 9 credits
- Credits DO NOT roll over

Per-lookup economics on Apollo:
- Email reveal = 1 credit ≈ $0.025
- Phone reveal = 5–8 credits ≈ $0.125–$0.20
- Full enrichment = 9 credits ≈ $0.225

**Apollo vs Crustdata**: Apollo is cheaper on basic email reveal (~$0.025 vs ~$0.02 — same order), but Apollo has per-user SaaS pricing ($49+/user/mo) which prices the full product higher unless you only want the API. Apollo's raw-API credit price ($0.025) is actually *higher* than Crustdata's inferred credit price ($0.02).

### 10.2 People Data Labs ([peopledatalabs.com/pricing/person](https://www.peopledatalabs.com/pricing/person))

| Plan | Price | Credits |
|---|---|---|
| Free | **$0** | **100 person/company lookups/mo** + 25 IP lookups |
| Pro | **$98/mo** (or $940/yr = $78/mo) | **350 person enrich credits** |
| Enterprise | ~**$2,500/mo+** | Custom |

- Per-credit cost: **$0.28 on monthly Pro**, down to **$0.20 for high-volume annual**.
- 1 credit per successful API request; match-only billing.
- Real-world monthly cost: **$274–$520 SMB, $1,200–$3,200 mid-market**.

**PDL vs Crustdata**: PDL's **$0.20–$0.28/credit** is **~10× Crustdata's estimated $0.02/credit**. But PDL's "1 credit = full person record" is unit-equivalent to Crustdata's 7-credit full-enrich at $0.14. So at full-enrich level, **Crustdata is ~half the unit price of PDL at high-volume tiers** (~$0.14 vs ~$0.20). PDL has the clearer published free tier (100/mo vs Crustdata's unpublished).

### 10.3 Clearbit → HubSpot Breeze Intelligence ([MarketBetter 2026 breakdown](https://www.marketbetter.ai/blog/clearbit-pricing-breakdown-2026/))

- **Clearbit standalone API is DEAD.** Logo API shut down Dec 2024. Enrichment API deprecated post-HubSpot acquisition (Nov 2023).
- Breeze Intelligence is now HubSpot-gated:
  - Starter add-on: **$45/mo annual** or **$50/mo monthly** → 100 Breeze credits
  - 1 enrichment = 10 HubSpot Credits; HubSpot Credits sold at **$10 / 1,000 credits → $0.01/credit → $0.10/enrichment**
  - Credits reset monthly, no rollover
- Typical HubSpot Marketing Hub Pro + moderate enrichment ≈ **$5,390/mo, $64,680/yr**.
- Historical Clearbit API access today = enterprise HubSpot contract, typically **six figures annually**.

**Clearbit vs Crustdata**: Clearbit no longer competes for pure-API use cases. If you need a real-time B2B enrichment API and don't want HubSpot, Crustdata is structurally better positioned. At $0.10/enrichment, Breeze is actually *more expensive* than Crustdata's estimated $0.04/company lookup.

### 10.4 Coresignal ([coresignal.com/pricing](https://coresignal.com/pricing/))

| Plan | Price | Credits |
|---|---|---|
| Free | $0 | 200 Collect + 400 Search credits (14-day validity) |
| Starter | **$49/mo** | 250 Collect + 500 Search |
| Pro | **$800/mo** | 10,000 Collect + 20,000 Search |
| Premium | **$1,500/mo** | 50,000 Collect + 150,000 Search |
| Enterprise | **$5,000–$10,000+/mo** | Custom |

- 1 Collect credit = 1 profile record. Multi-source = 2 Collect credits.
- Per-record cost at Pro: $800 / 10,000 = **$0.08/record**
- Per-record cost at Premium: $1,500 / 50,000 = **$0.03/record**

**Coresignal vs Crustdata**: Coresignal publishes everything Crustdata hides. At Premium ($0.03/record) Coresignal is competitive with Crustdata's inferred $0.04/company lookup; but on starter Coresignal is more expensive per record ($0.20). Coresignal's free tier (200 credits with 14-day expiry) is more generous initially but expires — vs Crustdata's likely 100-credits-forever.

### 10.5 Clay ([clay.com/pricing](https://www.clay.com/pricing))

Post-March 2026 pricing overhaul:
| Plan | Price | Credits |
|---|---|---|
| Launch | **$185/mo** (annual) | 2,500 Data Credits + 15,000 Actions |
| Growth | **$495/mo** (annual) | 6,000 Data Credits + 40,000 Actions |
| Enterprise | **$30,000–$154,000/yr** | Custom |

Legacy (still available):
- Starter $149/mo, Explorer $349/mo, Pro $800/mo (window to switch closed April 10 2026)

Clay is a **workflow platform on top of data**, not a raw API. It's only a direct comp if the Crustdata-built product is itself a workflow tool.

### 10.6 ZoomInfo

- API access: **starts at $5,000/yr** (HubSpot App Marketplace enrichment)
- Full prospecting: **$50,000/yr floor** per Reddit sales-rep leak
- SMB avg: $42k/yr; Enterprise avg: **$164k/yr**
- Credit-based: 1 credit = 1 contact/company export; not publicly priced per-credit

**ZoomInfo vs Crustdata**: ZoomInfo is the enterprise incumbent at 10–50× the price point. Crustdata positions explicitly as the API-first, developer-friendly alternative.

### 10.7 Harmonic.ai ([harmonic.ai/pricing](https://harmonic.ai/pricing))

- Sales-gated. Minimum commitment **~$25,000/year**
- **~$10,000/seat/year, 3-seat minimum = ~$2,083/mo floor**
- Specializes in startup/VC-targeted data (not the same use case as Crustdata's broader B2B, but overlaps for VC/fundraising use cases)

### 10.8 Summary table — cost per "1 basic enriched record"

Best effort unit comparison at the cheapest usable tier:

| Vendor | Tier | $/record (est) | Free tier |
|---|---|---|---|
| **Crustdata** | inferred (~$200/mo Starter) | **~$0.02–$0.04** | Unpublished (~100 credits inferred) |
| Apollo.io | Basic $49 | **$0.025** | 10k email credits/mo |
| PDL | Pro $98 | **$0.28** | 100/mo |
| Clearbit/HubSpot Breeze | Starter $45 | **$0.10** | None standalone |
| Coresignal | Premium $1,500 | **$0.03** | 200 credits / 14d |
| Clay (Launch) | $185 | **~$0.07** (Data Credits) | None |
| ZoomInfo | Enterprise $50k/yr | not published | None |
| Harmonic | Enterprise $25k/yr | not published | None |

**Headline finding**: Crustdata's per-record cost is genuinely at the low end — competitive with Coresignal Premium and below PDL's $0.28. The *pricing-page opacity* is more of a go-to-market choice than a reflection of high prices.

---

## 11. Viability matrix — which product types make economic sense

| Product type | Unit economics | Verdict at Crustdata pricing |
|---|---|---|
| **$5/mo B2C consumer app** ("find the founder behind any startup") | Needs <25 lookups/user/mo at $0.02/lookup to stay gross-margin positive | **KILLED.** Even moderate usage blows past $5/mo. Free-tier 100 credits would cover ~14 users only. |
| **$20/mo prosumer app** ("LinkedIn outreach helper for solo recruiters") | ~200 basic enriches/mo acceptable at $0.02 each = $4 cost | **VIABLE IF low-volume per user.** Very thin margins. |
| **$50/mo SaaS (power-user CRM plugin)** | ~1,000 enriches/mo at 2 credits = $40/mo cost | **VIABLE** with 20% gross margin — tight but workable. |
| **$200+/mo B2B SaaS (sales team tool, 5–50 seats)** | Enterprise-grade, per-seat, can absorb $50–$150/seat/mo in data cost | **VIABLE and natural fit** — this is Crustdata's target customer. |
| **$500+/mo KYB / compliance / onboarding tool** | Per-customer value is very high ($1k+ LTV), low lookup volume (~10s per customer verification) | **STRONGLY VIABLE.** Compliance use cases have high price insensitivity and low call volume. |
| **Free + ads consumer site** ("free company lookup search engine") | $0 revenue per lookup vs ~$0.02 cost | **KILLED** unless ad CPM covers it — unlikely without massive scale. |
| **Agentic tool calling Crustdata N times per task** ($0.10/task lookup cost at avg 5 calls) | If LLM-agent revenue per task is >$0.50, works | **VIABLE if agent value > $1/task** (e.g. lead-gen automation, research co-pilot). Token-efficient response shape is an advantage here. |
| **Real-time alerts / monitoring product** (hiring, funding events) | Needs webhook-subscription pricing or frequent polling | **DEPENDS** on enterprise webhook pricing (unpublished). Polling at 15 rpm works for small watchlists (<1,000 companies) but not beyond. |
| **Enrichment-as-a-service reseller (cheaper Apollo)** | Arbitrage Crustdata's $0.02/credit and mark up | **KILLED.** Thin arbitrage (3x markup → $0.06) and TOS likely forbids reselling. |
| **Bulk list-building tool** (100k-record campaigns) | At 2 credits/company × 100k = 200k credits = $4,000 per campaign via API | **KILLED via API** (rate limit = 22k/day max → 4.5 days per campaign + $4k cost). **VIABLE via bulk flat-file** if that contract is ≤$5k/mo for unlimited. |
| **Investor / VC deal-flow tool** | Low volume, extreme value per decision | **VIABLE** — same economics as KYB. |
| **Real-time dashboard "who's raising now"** | Requires enterprise live endpoints + webhooks | **ENTERPRISE-ONLY** ($5k+/mo tier minimum). |
| **Research co-pilot for AI agents** | 5–20 calls per research task, high-margin if paired with LLM SaaS | **VIABLE** — web search endpoint at 1 credit/query (~$0.02) is genuinely cheap vs e.g. Perplexity's API, and Crustdata's explicit "token-efficient response" positioning fits here. |
| **White-label people search for recruiters** (per-user product) | Recruiters pay $100+/mo → absorb $20–$50 data cost | **VIABLE** at mid/top of recruiter pricing tiers. |
| **Self-serve API marketplace arbitrage** | Needs Crustdata's API to serve 1000s of random users | **KILLED** — 15 rpm rate limit caps aggregate throughput below viable marketplace traffic. |

### The rule of thumb

- **Price floor for API-native products built on Crustdata: ~$50/mo per customer.** Below that, unit economics break unless usage is trivially low (a few lookups per user per month) or you negotiate an enterprise deal with volume discounts.
- **Sweet spot: $200–$2,000/mo B2B SaaS** where data cost is 10–20% of the customer's price.
- **Killer apps: compliance, KYB, investor intelligence, enterprise sales intelligence** — high price, low lookup volume, extreme value per decision.

---

## 12. Open questions / blockers for builders

1. **What does 1 credit actually cost in dollars?** Only inferrable (~$0.02). Need a sales call to confirm.
2. **What is the free tier credit count?** Not published. 100/mo is a reasonable bet.
3. **Is there a public overage rate?** No. At scale you'll need to pre-buy credit packs or sign an enterprise deal.
4. **Webhook event pricing?** Not published. Almost certainly enterprise-only.
5. **Is rate limit lifted at higher tiers?** Docs say "can change by plan" but no numbers published.
6. **Any YC / startup credit programs?** Not listed publicly — reach out to `abhilash@crustdata.com` or `gtm@crustdata.co`.
7. **Is there a concurrent-connection cap?** Not published.
8. **Credit rollover on annual plans?** Not published (only "6 months from purchase" validity is stated).

---

## 13. Sources

**Primary (Crustdata-authored)**:
- [crustdata.com/pricing](https://crustdata.com/pricing) — tier names only, no dollars
- [docs.crustdata.com/general/pricing](https://docs.crustdata.com/general/pricing) — per-endpoint credit costs (THE key primary source)
- [docs.crustdata.com/general/rate-limits](https://docs.crustdata.com/general/rate-limits) — 15 rpm default, endpoint list
- [docs.crustdata.com](https://docs.crustdata.com) — docs root
- Local playwright cache at `/home/akash/PROJECTS/crustdata/.playwright-mcp/` (snapshots from 2026-04-19)
- Contact: `gtm@crustdata.co`, `abhilash@crustdata.com`

**Community / third-party pricing estimates**:
- [prospeo.io/s/crustdata-pricing-reviews-pros-and-cons](https://prospeo.io/s/crustdata-pricing-reviews-pros-and-cons) — $200–$500 starter, $1k–$3k growth, $5k+ enterprise estimates
- [gurusup.com/blog/crustdata-vs-snowflake](https://gurusup.com/blog/crustdata-vs-snowflake) — "$200/mo starter" estimate
- [skywork.ai/.../Crustdata:-The-Real-Time-Data-Engine](https://skywork.ai/skypage/en/Crustdata:-The-Real-Time-Data-Engine-for-Your-AI-Stack/1975037718378377216) — "$95/mo" estimate
- [iseoai.com/crustdata/](https://iseoai.com/crustdata/) — review
- [aichief.com/ai-marketing-tools/crustdata/](https://aichief.com/ai-marketing-tools/crustdata/) — review

**Community pricing signal** (the key data point):
- [HN 47387103 "Companies.social ... $0.04/lookup tax"](https://news.ycombinator.com/item?id=47387103) — March 2026 Show HN explicitly naming Crustdata and citing ~$0.04/lookup
- [HN 47146819 Show HN: Crustdata Web Search API](https://news.ycombinator.com/item?id=47146819) — Crustdata's own Show HN (no pricing in comments; 0 comments at time of snapshot)

**Competitor pricing**:
- Apollo.io: [docs.apollo.io/docs/api-pricing](https://docs.apollo.io/docs/api-pricing), [salesmotion.io/blog/apollo-pricing](https://salesmotion.io/blog/apollo-pricing)
- PDL: [peopledatalabs.com/pricing/person](https://www.peopledatalabs.com/pricing/person), [support.peopledatalabs.com/hc/en-us/articles/25794271805211](https://support.peopledatalabs.com/hc/en-us/articles/25794271805211-Pricing-credits)
- Clearbit/HubSpot: [marketbetter.ai/blog/clearbit-pricing-breakdown-2026](https://www.marketbetter.ai/blog/clearbit-pricing-breakdown-2026/), [cognism.com/blog/clearbit-pricing](https://www.cognism.com/blog/clearbit-pricing)
- Coresignal: [coresignal.com/pricing](https://coresignal.com/pricing/)
- Clay: [clay.com/pricing](https://www.clay.com/pricing), [salesmotion.io/blog/clay-pricing](https://salesmotion.io/blog/clay-pricing)
- ZoomInfo: [factors.ai/blog/zoominfo-pricing](https://www.factors.ai/blog/zoominfo-pricing), [enrich.so/blog/zoominfo-pricing-breakdown](https://www.enrich.so/blog/zoominfo-pricing-breakdown)
- Harmonic: [harmonic.ai/pricing](https://harmonic.ai/pricing), [prospeo.io/s/harmonic-pricing](https://prospeo.io/s/harmonic-pricing-reviews-pros-and-cons)
