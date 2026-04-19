# Agent 07 — Crustdata Funding & Investor Endpoints: Deep Dive

**Date:** 2026-04-19
**Scope:** Compare Crustdata's funding & investor data surface against Crunchbase, PitchBook, Harmonic, Tracxn, CB Insights, Dealroom, PrivCo. Assess coverage, depth, latency, source mix, schema richness, India/SAFE/emerging-fund gaps, and where a product can exploit the delta.

---

## TL;DR (the uncomfortable truth)

Crustdata **does not have a dedicated funding-rounds endpoint**. There is no `/funding-rounds/search`, no `/investors`, no `/funds`. Funding is a *flat 5-field sub-object* on `/company/enrich`:

```
funding.total_investment_usd
funding.last_round_amount_usd
funding.last_fundraise_date
funding.last_round_type
funding.investors
```

That's it. No per-round array, no valuation (pre/post), no lead-investor flag, no instrument (equity/SAFE/debt), no dilution, no board seats, no fund-level profile, no LP-commitment data, no IRR/MOIC, no MCA/RoC integration, no Form D endpoint — despite SEC filings being cited as an ingested source.

Crustdata is a **real-time company/people enrichment platform that happens to carry a sliver of funding data as a secondary axis**, not a private-markets intelligence platform. Calling it a Crunchbase/PitchBook replacement on the funding axis is wrong. Calling it a Crunchbase/PitchBook *complement* on the pre-funding-signal axis is where the actual value lives.

If a product wants to exploit a delta, the delta is **not in the funding database** (they will lose a head-to-head). The delta is in **real-time upstream signals that precede a round showing up in Crunchbase**, combined with **India/emerging-market LinkedIn depth** and **webhook plumbing**. See the closing section.

---

## 1. Funding round coverage — stages, geography, sectors

### 1.1 What the API actually exposes

From the official `2025-11-01` OpenAPI spec (`docs.crustdata.com/openapi-specs/2025-11-01/introduction`), the full endpoint list is **12 endpoints** across Company / Person / Web:

- Company: `/company/search`, `/company/identify`, `/company/enrich`, `/company/search/autocomplete`, `/company/professional_network/search/live`
- Person: `/person/search`, `/person/enrich`, `/person/professional_network/enrich/live`, `/person/professional_network/search/live`, `/person/search/autocomplete`
- Web: `/web/search/live`, `/web/enrich/live`

No `/funding`, no `/rounds`, no `/investors`, no `/funds`, no `/deals`. Every piece of funding information rides on the `funding.*` sub-object inside `company_data` returned by `/company/enrich`, or as a filterable scalar inside `/company/search`.

### 1.2 Stage coverage

- **Stage captured:** The `last_round_type` field is a *single string* (e.g. "Series A", "Seed", "Pre-Seed"). The Tracxn profile of Crustdata itself confirms Crustdata classifies its own 2024-12-04 round as "Pre Seed"; Crunchbase calls it "Seed VC - II" — so stage taxonomy alignment with Crunchbase/Pitchbook is approximate, not canonical.
- **Pre-seed / SAFE:** Not a structural field. Instrument type is simply not in the schema, which means a $1M SAFE at a $15M cap looks identical to $1M priced equity at a $10M pre — you get `last_round_amount_usd: 1000000` and nothing more. For pre-seed / SAFE / convertible coverage Crustdata is **structurally weaker than Carta, AngelList-derived datasets, and PrivCo** (which models SAFEs explicitly). It is roughly at parity with Crunchbase for pre-seed *presence* (both backfill from announcement news) but worse than Harmonic for pre-seed *earliness*.
- **Series F+ / late stage / growth:** Same flat schema. No growth-equity, secondary, or continuation-fund types as native enum values. You know total funding and the last round; you cannot reconstruct the round-by-round cap table trajectory through the API. **Below PitchBook** for late-stage diligence by a wide margin.

### 1.3 Geographic coverage

Claimed coverage is **60M+ companies, 16+ sources, global**. In practice:

- **US:** Strong. LinkedIn + SEC filings + announcements give good breadth.
- **India:** Claimed as a strength ("notably strong coverage in India, Southeast Asia, Latin America" per Crustdata's own 7-best-databases post). The *company* side is plausibly real (LinkedIn has deep India coverage). The *funding* side is heavily LinkedIn-announcement + press-release driven — **no documented MCA/RoC integration**. MCA is the authoritative source for Indian private-company filings (Form AOC-4, MGT-7, ADT-1); Tracxn has a home-turf advantage here because they are Bengaluru-based and have baked MCA into their collection loop since 2012.
- **LatAm:** Crustdata's claim of "strong" coverage is marketing without a data backing; no regional filing integration is documented. Dealroom has deeper European and Distill.ai/LAVCA have deeper LatAm.
- **Europe:** Dealroom owns this — they track more global funding rounds than anyone else per their own docs and were founded in Amsterdam in 2013 specifically for European coverage.

### 1.4 Sector coverage

Industry filter uses `basic_info.industries` and `taxonomy.professional_network_industry` — both derived from LinkedIn's industry taxonomy, which is **coarse** (147 LinkedIn industries vs PitchBook's 30k+ verticals, CB Insights' 500+ proprietary categories, Tracxn's 2,500+ sectors). For "AI infra" vs "AI apps" vs "AI agents" vs "voice AI" you cannot cleanly filter in Crustdata the way you can in CB Insights or Tracxn. It's a **sector-taxonomy-disadvantaged** platform for thematic VC sourcing.

---

## 2. Historical depth

**No documented cut-off date for funding data.** The docs do not publish a "coverage from year X" commitment. Inference:

- Crustdata the company was founded 2020 and YC F24. Data collection loop is younger than Crunchbase (2007), PitchBook (2007), CB Insights (2010), Tracxn (2012), Dealroom (2013).
- They ingest from LinkedIn (post-2003 data but messy pre-2015) + SEC filings (structured data since 1993 via EDGAR) + announcements (depends on press archive).
- Realistic historical depth: **good from 2018 forward** (when LinkedIn post-driven signal collection became reliable and most venture news moved to Twitter/LinkedIn announcements), **thin 2010–2017**, **essentially absent pre-2010**.

By contrast: PitchBook claims coverage back to the 1980s for private equity, Crunchbase back to 2007, CB Insights has structured data back to ~2004. **For historical VC analysis (vintages, cohort IRRs, exit-velocity studies), Crustdata is unusable — go PitchBook or CB Insights.**

---

## 3. Latency — days from announcement to in-API

This is the cleanest Crustdata win.

### 3.1 Crustdata's pipeline

- Real-time crawl at request time for `/professional_network/search/live` and `/web/enrich/live`.
- Pre-indexed dataset refreshed on a rolling basis for `/company/enrich`, with live-crawl fallback.
- **Watcher API** pushes webhook notifications the moment a signal is detected — explicitly named "new funding announcement" as a supported trigger type ([docs.crustdata.com/webhook](https://crustdata.com/webhook), [crustdata.com/apis/watcher](https://crustdata.com/apis/watcher)).
- Practical latency: announcement on LinkedIn/Twitter/press → indexed in Crustdata within **hours, not days**, based on the product positioning. They do not publish a numeric SLA; their marketing language is "the moment it happens."

### 3.2 Competitor latencies (documented)

- **Crunchbase:** Dataset refreshed every 2 weeks for the commercial API; seed rounds specifically "commonly get added to the dataset weeks after they close" per Crunchbase's own methodology notes. The "Crunchbase lag" your question cites (30+ days on seed) is **real and self-admitted**.
- **PitchBook:** Private valuations delayed **45–60 days** per their methodology doc. Quarterly restatement of funding classifications is standard. This is *correct* and *deep*, not *fast*.
- **Harmonic:** Claims 6–12 months *before* announcement for pre-announcement detection — they trade announcement-time precision for pre-announcement signal. Not directly comparable.
- **Tracxn:** Sector-feed refreshed "quickly" per their docs, reportedly 1–2 weeks on seed, faster on series A+.
- **CB Insights:** Mosaic-score signals are real-time; structured funding rounds lag Crunchbase by a few days.
- **Dealroom:** Europe-real-time, rest-of-world on weekly cycle.
- **PrivCo:** Not real-time; quarterly-refreshed financial estimates are the core product.

### 3.3 Net latency verdict

Crustdata is **the fastest to push a webhook** when a funding announcement hits LinkedIn or a press wire. Hours vs Crunchbase's weeks. That is the most-defensible marketing claim they make, and it is true for *public announcements*. It is not faster than Harmonic for *pre-announcement* detection, because Harmonic inverts the problem (they detect Delaware filings and founder signals before announcement).

---

## 4. Sources

### 4.1 Crustdata's ingested sources (documented)

Per Crustdata's own marketing and the "AI-tools-for-VC" blog post:

1. **LinkedIn** — company pages, job postings, founder profiles, LinkedIn posts (this is the core substrate; the "professional_network" in the endpoint names is LinkedIn-by-another-name to avoid trademark issues)
2. **SEC filings** — including Form D (Regulation D private placement disclosures, filed within 15 days of first sale). This is the only non-press, non-LinkedIn funding-primary source in the stack.
3. **Press-release / news wires** — announcements from TechCrunch, company blogs, PR Newswire, etc.
4. **Company websites / domain-registration patterns**
5. **Web traffic** (Similarweb-class signals)
6. **GitHub** (for engineering team proxies)
7. **G2** (product reviews)
8. **Google Search** impressions / SEO data
9. **Employee reviews** (Glassdoor-class)
10. **Social signals** (Twitter/X founder activity)
11–16. Unnamed "verified" sources (Crustdata claims 16+ total).

### 4.2 Sources that are **unique among the competitor set**

Honestly? **None are exclusive to Crustdata.** Every source Crustdata uses is used by at least one competitor:
- LinkedIn: used by everyone who isn't blocked
- SEC Form D: used by PrivCo, Harmonic (the Delaware-filings origin story), Crunchbase
- GitHub: used by CB Insights (via acquisitions), Specter
- Web traffic: used by CB Insights (Mosaic), Specter

What is differentiated is **the combination + real-time recompute + webhook delivery**, not the source mix.

### 4.3 Sources that are **conspicuously missing**

- **MCA / RoC (India)** — no documented integration. This matters because in India, every private-company funding round has a corresponding MCA filing (PAS-3 for share allotment, SH-7 for authorized capital change, MGT-14 for board resolutions). Tracxn integrates MCA; Crustdata appears to rely on LinkedIn + press for India, which misses the pre-announcement filing window.
- **Companies House (UK)** — not documented.
- **BORIS (Germany), Infocamere (Italy), INFOGREFFE (France)** — not documented.
- **Delaware Division of Corporations / BizFile** — Harmonic's founding insight; not documented for Crustdata.
- **SEC Form ADV** — RIA investor filings with AUM and client-type data; not documented.
- **Carta cap-table data** — obviously not (Carta is proprietary).
- **PitchBook-grade LP commitment data** — no.

---

## 5. Fields per round

### 5.1 What Crustdata returns per company (not per round)

```
funding: {
  total_investment_usd: number,
  last_round_amount_usd: number,
  last_fundraise_date: date,
  last_round_type: string,
  investors: [string]   // flat list, order-undefined, no lead flag, no stake, no check size
}
```

**Notable absences:**

| Field | Crustdata | Crunchbase | PitchBook | Harmonic | Tracxn |
|---|---|---|---|---|---|
| Per-round array | No | Yes | Yes | Yes | Yes |
| Round date (per round) | Last only | Yes | Yes | Yes | Yes |
| Round amount (per round) | Last only | Yes | Yes | Yes | Yes |
| Pre-money valuation | No | Partial | Yes | Partial | Partial |
| Post-money valuation | No | Partial | Yes | Partial | Partial |
| Lead investor flag | No | Yes | Yes | Yes (`isLead`) | Yes |
| Instrument type (equity/SAFE/debt/convertible/note) | No | Partial | Yes | No | Partial |
| Use of proceeds | No | No | Partial | No | No |
| Dilution | No | No | Yes | No | No |
| Board seats / observer rights | No | No | Yes | No | No |
| Liquidation preference | No | No | Yes | No | No |
| Option pool expansion | No | No | Yes | No | No |
| Source link / citation | No | Yes | Yes | Yes | Yes |
| Participating investors (ordered) | Unordered list | Ordered | Ordered | Ordered | Ordered |

**Net:** Crustdata's per-round schema is *weaker than every single competitor in the set for diligence use*, and the missing pieces (valuation, lead flag, instrument, dilution) are exactly the ones VCs actually need. Crustdata is **not a diligence tool**; it is a discovery tool.

### 5.2 Harmonic's advantage on this axis

Harmonic's API exposes `fundingRounds[]` with `fundingAmount`, `fundingRoundType`, `investors[].investorName`, `investors[].isLead`, `Last Funding Round Lead Investors`, `Prior Funding Rounds Lead Investors`. This is *structurally richer* than what Crustdata returns. On a pure funding-schema basis, Harmonic > Crustdata.

---

## 6. Investor profiles

### 6.1 What Crustdata does NOT have

**There is no investor entity in Crustdata.** The `funding.investors` field is a list of *strings* (firm names), not references to structured investor objects. You cannot:

- Query "show me all portfolio companies of Accel India"
- Get Accel's AUM, fund vintages, or LP base
- Get the partner who led the deal
- Get MOIC, IRR, DPI for Accel Fund IX
- Get Accel's typical check-size distribution
- Get Accel's stage focus or sector thesis
- Get Accel's new-fund-closing status
- Identify which partner at Accel has been posting about a sector

### 6.2 Work-around (and it's janky)

You'd have to:
1. Pull the string "Accel" from `funding.investors`.
2. Manually map "Accel" → their LinkedIn company URL.
3. Call `/company/enrich` on Accel to get *the firm's* LinkedIn data (headcount, industry=Venture Capital, website).
4. Call `/person/search` with filter `currentCompany = Accel` to get partners.

None of this is a first-class investor object. It's a client-side JOIN.

### 6.3 Competitor positioning on investor side

- **PitchBook:** Gold-standard. Investor AUM, check-size, stage focus, partner-level deal attribution, fund-level IRR/MOIC/DPI (self-reported from LPs), LP commitment tracking.
- **CB Insights:** Strong investor profiles, Mosaic-scored portfolios, partner tracking, predictive "who will invest in X" models.
- **Tracxn:** Decent investor profiles, strong India-focused investor roster, partner tracking.
- **Crunchbase:** Investor-as-entity with portfolio-of-investments view, partner-level attribution spotty.
- **Harmonic:** Investor-as-entity, lead/co-lead tagging, portfolio views.
- **Dealroom:** Investor profiles with European depth; fund tracking.
- **PrivCo:** Financial-profile-oriented; investor side is weaker.
- **Crustdata:** **No investor object at all.** This is the biggest structural gap vs. every named competitor.

**Verdict:** On investor intelligence, Crustdata is not competitive. The product was not designed for this use case.

---

## 7. Pre-funding signals

This is where Crustdata actually differentiates.

### 7.1 Pre-funding signals Crustdata does surface

Crustdata explicitly markets on these signals (per the stealth-tracking and VC-solutions pages):

- **Stealth detection:** Job-title changes to "Founder", "Co-founder", "CEO (Stealth Startup)", "Building something new", "NewCo". The Watcher API fires webhooks on these title transitions.
- **Unexplained career gaps:** Departures from established tech companies with no new employer listed.
- **Founding-engineer hiring:** Job-posting signals like "Founding Engineer", "First Designer".
- **Founder social narrative:** Twitter/X activity shifts (increased posting, VC-audience engagement).
- **Domain registration patterns:** Unannounced domain launches.
- **Headcount velocity:** 20%+ six-month growth as a pre-Series-A indicator.
- **Web traffic acceleration:** 40–60% quarterly web-traffic growth.
- **Infra hiring:** VP Finance / VP GTM hires as a fundraise-prep indicator (9–18 months before raise).
- **Banker hires:** Not directly named, but detectable via headcount + role filter ("Hired banker from Qatalyst" is a known pre-IPO / pre-growth signal).
- **PPM distribution:** NOT tracked (this is a PDF-attached-to-email signal that nobody tracks systematically; PitchBook catches PPMs that come across their analyst desk).

### 7.2 What this means as a product angle

Crustdata has unambiguously invested in **pre-funding signal infrastructure**, and this is where they beat Crunchbase/PitchBook (both of whom are announcement-time platforms). The question is whether Crustdata's pre-funding coverage beats Harmonic. The honest answer:

- **Harmonic** is **stronger on Delaware-state-filings + founder-bio pattern matching**. They productize "show me stealth AI companies that just formed."
- **Crustdata** is **stronger on LinkedIn-title-change webhooks + job-posting signals**. They productize "ping me when Sarah switches from 'VP Eng @ Stripe' to 'Building something new'."

Different leading indicators. **Crustdata is better for talent-driven deal sourcing; Harmonic is better for entity-driven deal sourcing.**

---

## 8. SAFE / pre-seed coverage

### 8.1 Crustdata's structural weakness

Because the funding schema has no `instrument` field and no per-round array, SAFEs are indistinguishable from priced rounds. A $500K SAFE and a $500K seed look identical in the API. **This is the same weakness Crunchbase has** — neither platform models SAFEs as a first-class citizen.

### 8.2 Who actually has SAFE coverage

- **Carta:** Native — every SAFE issued on Carta is tracked as a security type with cap, discount, valuation cap, MFN. Not API-accessible to outsiders though.
- **PrivCo:** Partial — their financial models account for SAFE conversion but don't always expose as a round type.
- **AngelList (now Republic):** SAFE-native for their syndicates.
- **CB Insights, Tracxn, Dealroom:** Partial — flag some rounds as SAFE/convertible in instrument field if the announcement names it.
- **Harmonic:** No SAFE-specific field.
- **Crustdata:** No.

**Net:** Crustdata is *average* on SAFE coverage (i.e., whatever gets announced publicly), not a leader and not a laggard. Given that 70%+ of pre-seed is now SAFE-based, this is a coverage hole for everyone except Carta.

### 8.3 Pre-seed visibility

Pre-seed rounds are often **not announced publicly for 6–18 months** (founders don't want to signal they've raised a small round). Coverage depends on whether the round surfaces through:
- A partner LinkedIn post → Crustdata sees it (fast via Watcher)
- An SEC Form D filing → Crustdata sees it (15-day filing window)
- A TechCrunch/Business Insider leak → Crustdata sees it
- An MCA filing (India) → Crustdata does **not** see it (no integration)

**Harmonic explicitly markets "pre-announcement surfacing 6–12 months ahead"; Crustdata does not make this specific claim.** The pre-seed data coverage gap is real but not unique to Crustdata.

---

## 9. India-specific

### 9.1 The MCA / RoC integration gap

As called out earlier: **Crustdata does not integrate MCA**. Every private company registered in India under the Companies Act files:

- AOC-4 (financial statements, annual)
- MGT-7 / MGT-7A (annual return)
- PAS-3 (return of allotment — *fires whenever shares are allotted, i.e. every funding round*)
- SH-7 (authorized capital change)
- ADT-1 (auditor appointment)
- MGT-14 (resolutions, including funding-round resolutions)

PAS-3 is **the Indian equivalent of Form D** and fires on every allotment. The 30-day filing window + MCA21 public-search portal make this *more structurally accessible than SEC Form D* for anyone willing to scrape MCA21. Tracxn does this (they were built in Bengaluru specifically to exploit this data substrate). Crustdata does not.

### 9.2 What Crustdata does have for India

LinkedIn has strong India coverage (largest LinkedIn market outside the US by user count). India founders actively announce on LinkedIn. Job postings from Indian startups populate LinkedIn. So for **India company discovery by headcount/hiring/founder signals**, Crustdata is usable. For **India funding-round ground-truth**, Crustdata lags Tracxn significantly.

### 9.3 India competitive landscape summary

| Need | Best tool |
|---|---|
| India private-company filings (MCA) | Tracxn, Inc42, VCCircle, Entrackr |
| India LinkedIn-surface signals (hiring, founder moves) | Crustdata, Harmonic |
| India valuation / late-stage | Tracxn, Venture Intelligence |
| India seed / SAFE | Harmonic (partial), LetsVenture |

---

## 10. Emerging-fund tracking

### 10.1 New VC fund launches (emerging GPs raising Fund I/II)

Tracking emerging GPs requires:
- SEC Form ADV filings (RIAs with >$100M AUM)
- SEC Form D for the fund vehicle itself (every fund files a Form D when it first takes LP capital)
- Press announcements
- LP announcements (GP-specific)
- LinkedIn partner-page changes

**Crustdata catches only the last two** (announcements + LinkedIn). They do not have a structured "emerging manager" feed.

### 10.2 Work-around via Crustdata

You could:
1. Filter `/company/search` for `basic_info.industries = Venture Capital` + `headcount.growth_percent > X` + `year_founded >= 2020`.
2. Cross-reference with LinkedIn partner moves via `/person/search`.
3. Pipe through Watcher API for title-change webhooks.

That gives you a *probabilistic* emerging-GP tracker, not a canonical one. **PitchBook and CB Insights both have native "Emerging Manager" reports with LP-commitment tracking**; Crustdata does not.

### 10.3 Open opportunity

There is no public API today that cleanly surfaces:
- "All Fund I vehicles that filed Form D in the last 30 days, cross-referenced with the GP's prior portfolio performance at their previous firm."

This is a *real gap in the market*. Crustdata does not fill it; neither does anyone else cleanly.

---

## Where Crustdata beats Crunchbase/PitchBook/Harmonic

**Opinionated take — the dimensions where a product can actually exploit the Crustdata delta:**

### 1. **Webhook-latency on public funding announcements (hours vs weeks)**

Crunchbase has a documented 2-week dataset refresh; PitchBook has 45–60 day valuation delays. Crustdata's Watcher fires within hours of a LinkedIn/press announcement. **Build:** A VC workflow product that sends push notifications the moment a company in the fund's thematic watchlist announces, with auto-draft outreach ready. This is a legitimate 10x-speed product vs. "check Crunchbase Wednesday."

### 2. **Stealth-founder detection on LinkedIn title changes**

Harmonic's stealth detection is built around Delaware filings + founder-bio pattern matching; Crustdata's is built around LinkedIn-title-change webhooks. These are **complementary, not redundant**. **Build:** A stealth-founder-sourcing product that subscribes to both Harmonic and Crustdata, de-dupes, and surfaces a *single ranked feed* of new stealth signals. Early-stage VCs will pay for this because neither platform alone is complete.

### 3. **Pre-fundraise infrastructure-hiring signal (9–18 month leading indicator)**

VP Finance, VP GTM, Head of People, first full-time recruiter — these hires *precede* Series B by 6–12 months with reasonable reliability. Crustdata's `hiring` + `headcount` + `people.decision_makers` stack lets you build this. Crunchbase cannot because they only have announcement data. **Build:** A pre-Series-B pipeline scorer that ranks companies by "infra hire velocity" and ships the top 50 to a growth fund's deal team weekly.

### 4. **LinkedIn-Post sentiment around fundraising**

Founders tease rounds on LinkedIn/Twitter for weeks before announcement. Crustdata indexes LinkedIn posts (via the people-search API + web-search API). **Build:** A natural-language query layer — "show me founders of pre-Series-B AI startups who posted about 'exciting news coming' or 'crazy quarter' in the last 14 days" — and deliver the list. Pure post-signal mining. Nobody else does this cleanly.

### 5. **Emerging-market talent-driven sourcing (India, LatAm)**

Tracxn owns India filings. Crustdata owns India LinkedIn-depth. **Build:** An India-specific deal-sourcing product that combines MCA filings (via Tracxn or direct-scrape) with Crustdata's founder-title-change webhook. Target India-based emerging-fund GPs and US funds with India strategies. Crustdata alone isn't enough; Crustdata + MCA is.

### 6. **AI-agent-native deal-sourcing substrate**

Crustdata has a Composio MCP integration, webhook-native delivery, and a live-crawl architecture. Crunchbase/PitchBook have REST-only, batch-refreshed APIs built for the 2015 SaaS era. **Build:** An agentic VC deal-sourcing harness where a Claude/GPT agent continuously runs Crustdata queries, scores leads, drafts warm intros, and maintains a CRM — with Crustdata as the backend because the agent can actually *stream-subscribe* via webhook. This is where the platform's architectural choice (real-time > batch) pays off.

### Where Crustdata *loses* head-to-head and you should not build on it

- **Diligence workflows** (need PitchBook-grade per-round + valuation + lead-flag + instrument). Crustdata's 5-field funding object cannot support this.
- **Historical analysis / cohort IRR / vintage studies.** Too shallow historically.
- **Investor intelligence products** (fund AUM, LP-commit tracking, partner-level IRR). No investor object.
- **India MCA-derived funding ground-truth.** Use Tracxn.
- **SAFE/pre-seed instrument-level tracking.** Use Carta-derived data if you can get it.

**The thesis:** Crustdata wins on **speed + signal-breadth + agent-native plumbing** for deal *sourcing*, loses on **depth + investor-side + historical** for deal *evaluation*. A product built on Crustdata should lean hard into sourcing (webhook-driven, agent-native, pre-announcement signal mining) and outsource evaluation to PitchBook/Tracxn/Harmonic (or to the fund's own analyst).

---

## Sources consulted

### Primary (Crustdata docs & product pages)
- https://docs.crustdata.com — API documentation home, endpoint list
- https://docs.crustdata.com/openapi-specs/2025-11-01/introduction — formal API reference, all 12 endpoints
- https://docs.crustdata.com/company-docs/quickstart — `funding.total_investment_usd` field confirmed
- https://docs.crustdata.com/company-docs/enrichment — full `funding` sub-object schema (5 fields)
- https://crustdata.com/apis/watcher — Watcher API, funding-announcement webhook
- https://crustdata.com/webhook — fundraise webhook confirmation
- https://crustdata.com/solutions/venture-capital — VC marketing page, stealth signals
- https://crustdata.com/solutions/growth-equity — growth-equity framing
- https://crustdata.com/blog/ai-tools-for-venture-capital-why-top-funds-build-proprietary-pipelines — pre-fundraise signal inventory
- https://crustdata.com/blog/the-complete-guide-to-tracking-and-finding-stealth-startup-founders — stealth-detection methodology
- https://crustdata.com/blog/7-best-startup-databases-for-investors-in-2026 — Crustdata's own comparison vs Crunchbase/PitchBook/Harmonic/Tracxn/CB Insights/Dealroom
- https://crustdata.com/full-dataset — bulk-dataset claims
- https://crustdata.com/apis/company-enrichment — enrichment product page

### Competitors / context
- https://data.crunchbase.com — Crunchbase API reference
- https://support.crunchbase.com/hc/en-us/articles/33614980592787-Funding-Predictions-in-the-API — Crunchbase methodology / latency acknowledgment
- https://pitchbook.com/news/pitchbook-report-methodologies — PitchBook 45–60 day delay confirmation
- https://www.harmonic.ai — Harmonic startup database, 30M+ companies
- https://www.worldofdaas.com/p/harmonic-ai — Harmonic's Delaware-filings origin
- https://tracxn.com — Tracxn overview, 1.3M+ funding rounds
- https://w.tracxn.com/funding-database — Tracxn funding DB scope
- https://dealroom.co/our-data — Dealroom's "more funding rounds than any other provider" claim
- https://www.privco.com — PrivCo positioning, 893K+ US private companies
- https://www.cbinsights.com/what-we-offer/api — CB Insights API, 11M companies

### Indirect / inferred
- https://www.mca.gov.in — MCA21 portal (India filings)
- PAS-3, AOC-4, MGT-7 form references via Indian compliance blogs
- SEC Form D via PrivCo knowledge bank

---

*End of report.*
