# MAP — Crustdata's Unique Capability Surface (Wave 1 Synthesis)

**Date:** 2026-04-19
**Synthesis of:** agents 01–11 (endpoint inventory, company fields, people fields, headcount time-series, news/signals, job postings, funding/investor, techstack/traffic, pricing/limits, Crustdata's own showcase, 2025–26 shipments)

---

## TL;DR (one page)

**What you can build on Crustdata that you demonstrably cannot build elsewhere comes from exactly three orthogonal moats, stacked.** First, a **push-first event substrate** (Watcher API, `POST /apis/watcher`, shipped Nov 15, 2025; webhook delivery on 6 trigger primitives that include `first_person_hired_in_company_department`, `international_hiring_expansion`, `linkedin_post_with_keywords`, `person_starts_new_job`, `new_funding_announcement`, `company_headcount_increased_by_pct`) — a class of signals where competitor commodity APIs (Apollo, PDL, Clearbit/Breeze, Cognism, ZoomInfo) offer *nothing* webhookable, PredictLeads has a firehose-with-filters but no LinkedIn pipeline and no person-level watches, and Harmonic has monitoring only in UI not API. Second, a **LinkedIn-canonical time-derived growth panel** exposed as *search filters, not just read fields* (`roles.growth_6m`, `roles.growth_yoy`, `linkedin_headcount_by_role_six_months_growth_percent`, `hiring.openings_growth_percent`, `followers.mom_percent` through `yoy_percent`) — a compose-one-query surface where you can say "US SaaS with eng headcount up 20% YoY AND followers up 30% MoM AND open reqs up 50%" in one `POST /company/search` call, a shape that PDL only exposes in the Insights premium tier (non-filterable, must post-process), Apollo cannot express at all, and Revelio only serves through SQL-over-WRDS seats. Third, a **LinkedIn↔GitHub identity graph** (`dev_platform_profiles[]` with a numeric `confidence_score` cross-matching LinkedIn to GitHub, plus `org_memberships[]`, `declared_handles[]` from GitHub's canonical social-accounts feature, 22 GitHub-native fields per person) — the single most differentiated thing in the person schema, matched nowhere in Apollo/PDL/Clearbit/Cognism/ZoomInfo, and the substrate of every DevRel and B2D go-to-market.

Stack these three and you can build products nobody else can: a champion-graph SaaS that fires when a closed-won champion changes jobs AND posts about their new priorities AND their new employer is in your competitor set, with a LinkedIn↔GitHub identity-resolved decision-maker graph — all at roughly **$0.02/credit** (~$0.04/company enrich, ~$0.14/full-person-enrich) vs PDL's $0.20–$0.28/credit, Clearbit/Breeze's $0.10/enrich, or ZoomInfo's $50k/yr floor. The *cost* of the moat is that Crustdata is pricing-opaque, enterprise-gated on the live endpoints (`/person/professional_network/enrich/live`, `/company/professional_network/search/live`, `/social_post/professional_network/*`), has structurally weak funding-diligence data (no per-round array, no valuations, no investor-entity object, no MCA/RoC), weak phone data (flat `string[]`, no source/type/last-seen metadata), no technographic scanning beyond job-posting NLP, no salary inference, no demographic cuts, and a 6-month credit-expiration clock that kills hoarding. The structurally virgin territory — Watcher webhooks, the v2025-11-01 API scheme, `/web/search/live`, and the LinkedIn↔GitHub graph — has **zero consumer-facing third-party apps built on it** as of 2026-04-19, with the only Crustdata-originated HN Show post (Feb 2026, `/web/search`) sitting at 10 points / 0 comments. Capability has lapped awareness. For the next 60–90 days any serious builder is *early*.

---

## I. Endpoint Inventory (compact)

Convention: **M** = marketed zone (Crustdata's own demos/solutions pages lean on it), **D** = dark zone (exists in docs/Composio but has near-zero showcase or third-party adoption), **E** = enterprise-gated.

| # | Endpoint | Auth | Credits/call | Rate | Freshness | M/D/E |
|---|---|---|---|---|---|---|
| 1 | `POST /company/search` | Bearer v2025-11-01 | 0.03/result | 15 rpm | Indexed (weekly → 14–28d tail) | M |
| 2 | `POST /company/identify` | Bearer | **Free** | 15 rpm | Indexed | M |
| 3 | `POST /company/enrich` | Bearer | 2/record | 15 rpm | Indexed | M |
| 4 | `POST /company/search/autocomplete` | Bearer | Free | 15 rpm | Indexed | M |
| 5 | `POST /company/professional_network/search/live` | Bearer | 2/company | 15 rpm | Live crawl | E |
| 6 | `POST /person/search` | Bearer | 0.03/result | 15 rpm | Indexed | M |
| 7 | `POST /person/enrich` | Bearer | **1–7/record additive** (1 base + 2 personal email + 2 phone + 1 biz email + 1 dev platform) | 15 rpm | Cached | M |
| 8 | `POST /person/professional_network/enrich/live` | Bearer | 7/profile | 15 rpm | Live | E |
| 9 | `POST /person/professional_network/search/live` | Bearer | 2/profile | 15 rpm | Live | E |
| 10 | `POST /person/search/autocomplete` | Bearer | Free | 15 rpm | Indexed | M |
| 11 | `POST /web/search/live` | Bearer | 1/query | 15 rpm | Live SERP | M |
| 12 | `POST /web/enrich/live` | Bearer | 1/page, max 10 URLs | 15 rpm | Live fetch | M |
| 13 | `POST /job/search` | Bearer | 0.03/result | 15 rpm | Indexed | M |
| 14 | `POST /job/professional_network/search/live` | Bearer | 2/result | 15 rpm | Live | E |
| 15 | `POST /professional_network/search/autocomplete` | Bearer | Free | 15 rpm | — | E |
| 16 | `POST /dev_platform/enrich` | Bearer | (add-on 1 via /person) | 15 rpm | — | D |
| 17 | `POST /employee_review/enrich` | Bearer | quote | 15 rpm | — | D |
| 18 | `POST /social_post/professional_network/enrich/live` | Bearer | quote | 15 rpm | Live | D/E |
| 19 | `POST /social_post/professional_network/search/live` | Bearer | quote | 15 rpm | Live | D/E |
| 20 | **Watcher API / webhook** | quote | quote | — | Real-time push | **D** (most under-marketed asset) |
| 21 | `GET /screener/company` | Token (legacy) | credit | 15 rpm | cached + `enrich_realtime=True` (~10 min) | D |
| 22 | `POST /screener/screen/` | Token | credit | 15 rpm | Indexed | D |
| 23 | `POST /screener/company/search` | Token | credit | 15 rpm | Real-time | D |
| 24 | `POST /screener/person/search` | Token | credit | 15 rpm | Real-time | D |
| 25 | `POST /screener/persondb/search/` | Token | credit | 15 rpm | 30-day refresh | D |
| 26 | `GET /screener/person/enrich` | Token | credit | 15 rpm | 30–60 min enrich | D |
| 27 | `GET /screener/social_posts` | Token | credit | 15 rpm | Live (30–60s) | D |
| 28 | `POST /screener/web-search` | Token | 1 credit | 15 rpm | Real-time | D (legacy) |
| 29 | `POST /screener/web-fetch` | Token | credit | 15 rpm | Real-time | D (legacy) |
| 30 | `POST /data_lab/headcount_by_facet/` | Token | quote | 15 rpm | Timeseries | **D (huge)** |
| 31 | `POST /data_lab/headcount_timeseries/` | Token | quote | 15 rpm | Timeseries | **D (huge)** |
| 32 | `POST /data_lab/funding_milestone_timeseries/` | Token | quote | 15 rpm | Timeseries | **D (huge)** |
| 33 | `POST /data_lab/job_listings/` | Token | quote | 15 rpm | — | D |
| 34 | `POST /data_lab/web_traffic/` | Token | quote | 15 rpm | Timeseries | **D (huge)** |
| 35 | `POST /data_lab/decision_makers/` | Token | quote | 15 rpm | — | D |
| 36 | `GET /data_lab/investor_portfolio/?investor_name=` | Token | quote | 15 rpm | Not real-time | **D (investor-inverse)** |
| 37 | `POST /data_lab/screen_data/` | Token | quote | 15 rpm | — | D |

**Totals:** 15 current (`2025-11-01`) self-serve + enterprise-gated endpoints, 9 legacy `/screener/*`, 8 `/data_lab/*` timeseries, 1 Watcher webhook system = **36 distinct HTTP routes + 1 push channel**. *Of 36 routes, only ~10 are marketed. 26 live in the dark zone.*

---

## II. Differentiated Capabilities (ranked)

### D1. Watcher API — push-first event substrate over LinkedIn-canonical entities
- **One-line:** Webhook fires within minutes of a trigger; 6 primitives (`linkedin_post_with_keywords`, `person_starts_new_job`, `new_funding_announcement`, `job_posting_with_keyword_and_location`, `first_person_hired_in_company_department`, `international_hiring_expansion`, plus `company_headcount_increased_by_pct` / `department_headcount_range` variants).
- **Evidence endpoints:** `crustdata.com/apis/watcher`, the Composio `create_watch`/`get_watch` tools, blog `how-ai-sdrs-use-webhooks-to-time-outreach`. Shipped **Nov 15, 2025** as "Signal Watcher" (Product Hunt #4, 205 upvotes, #7 of day).
- **Competitive diff:** Apollo/PDL/Clearbit/Cognism/ZoomInfo — **zero webhookable events** at the commodity tier. PredictLeads — firehose-with-filter on 29 event types but **no LinkedIn pipeline, no person-level watches, no live crawl**; the ML-classifier pipeline adds hours of latency vs Watcher's "live crawl + push." Harmonic — event monitoring in UI only, not webhookable at SDR-price-point. Owler — 15 trigger-event Instant Insight *emails*, not structured webhooks. Clay — aggregator on top of Crustdata + Harmonic, not an originator.
- **Economic viability:** Webhook pricing is undocumented; almost certainly enterprise-only. Once you have webhook access, poll-avoidance saves credits.
- **Maturity/timestamp:** Nov 15, 2025 (Signal Watcher launch). Zero consumer-facing third-party apps built on it as of Apr 19, 2026. *Virgin.*

### D2. Composable time-derived growth filters on `/company/search`
- **One-line:** Growth deltas on 30/90/180/365-day windows per department / per role / per country / per follower metric, exposed as *filterable fields*, not only readable outputs.
- **Evidence endpoints:** `POST /company/search` with `filters.field` ∈ `{roles.growth_6m, roles.growth_yoy, followers.mom_percent, followers.qoq_percent, followers.six_months_growth_percent, followers.yoy_percent, hiring.openings_growth_percent, hiring.openings_count, headcount.total}` plus legacy `linkedin_headcount_by_role_six_months_growth_percent`, `job_openings_by_function_qoq_pct`, percentile-bucket fields (`71_to_100_percent`). Covers `headcount_mom_pct / qoq_pct / 6m_pct / yoy_pct / 2y_pct` at company level.
- **Competitive diff:** PDL has `employee_count_by_role` and `employee_growth_rate_12_month_by_role` only in Insights *Premium* and **not filterable** — you fetch and post-process. Apollo has `departmental_head_count` in `get-complete-organization-info` but **cannot filter** on it. Clearbit/Breeze/ZoomInfo/Cognism — no department-level growth. Revelio has cleaner panels back to 2008 but delivered via **WRDS/SQL/AWS Marketplace seats** and serves from cache — not a live API with a filter language. Harmonic has momentum filters for VCs but narrower filter surface and VC-seat priced.
- **Economic viability:** Search is 0.03/result (~$0.0006). This is the cheapest query in the catalog. Composable-growth queries are the *entry point* by design.
- **Maturity/timestamp:** Matured through 2025 (the 60-filter Person Search launched Sep 17, 2025). Field coverage expanded with the v2025-11-01 API.

### D3. LinkedIn ↔ GitHub identity graph (B2D substrate)
- **One-line:** Per-person `dev_platform_profiles[]` cross-matches LinkedIn to GitHub with a numeric `confidence_score`, exposes `org_memberships[]` (GitHub orgs with created_at / last_updated), `declared_handles[]` (Twitter / Mastodon / Bluesky declared on GitHub's canonical social-accounts feature), 22 GitHub-native fields (public_repo_count, followers/following, is_hireable, email, bio, company_text, etc.).
- **Evidence endpoints:** `POST /person/enrich` with `fields=["dev_platform_profiles"]` (+1 credit add-on); standalone `POST /dev_platform/enrich` (dark-zone).
- **Competitive diff:** PDL exposes `github_url` + `github_username` — two strings. Apollo — nothing. Clearbit — nothing. Cognism/ZoomInfo — nothing. Clay integrates GitHub as a *separate* provider with no cross-linkage. Crustdata ships the **resolution**, not just the strings.
- **Economic viability:** +1 credit (~$0.02) to add dev_platform to a person enrich. Unit economic is fine for B2D vendors.
- **Maturity/timestamp:** Active since pre-2025. No third-party product foregrounds it — marketed once in Clay integration blurb.

### D4. Per-role historical context on `experience.employment_details.past[]`
- **One-line:** For every past job of every person: `company_headcount_latest`, `company_headcount_range`, `seniority_level`, `function_category`, `years_at_company_raw`, `business_email_verified`, canonical HQ components — all filterable.
- **Evidence endpoints:** `POST /person/search` with filters on `experience.employment_details.past.*`; `POST /person/enrich` returns the full history array.
- **Competitive diff:** PDL exposes `job_company_employee_count` only for the **current** employer; per-past-job company context is not populated. Apollo — current only. Nobody else ships it. Enables career-trajectory ICPs ("joined at <50 headcount, left at >1000"), champion-tracking ("scaled from 50→5k at last company, now at 100-person company"), and per-past-role warm-referral routing (`business_email_verified` per past employer).
- **Economic viability:** 1 credit base person enrich (~$0.02). Search is 0.03/result.
- **Maturity:** Active baseline field for the v2025-11-01 spec.

### D5. SEO/SEM + web-traffic bundled inside `/company/enrich`
- **One-line:** `seo.total_organic_results`, `seo.monthly_organic_clicks`, `seo.monthly_google_ads_budget`, `web_traffic.monthly_visitors`, `web_traffic.domain_traffic` (source split) — shipped as fields of the *same* enrich call that returns firmographics and funding.
- **Evidence endpoints:** `POST /company/enrich`; `POST /data_lab/web_traffic/` for bulk timeseries.
- **Competitive diff:** Ahrefs/Semrush/SimilarWeb charge $300–$1k/mo for this *separately*. Apollo has `alexa_ranking` (rank, not visitors). PDL has nothing. Clearbit had `metrics.alexaGlobalRank`. Consolidation advantage for any AI SDR / GTM agent trying to qualify a lead in one API call. However — **no bounce rate, no SEO keyword list, no top-referring domains** (SimilarWeb still wins on those).
- **Economic viability:** Folded into the 2-credit company enrich (~$0.04). Single call returns everything.
- **Maturity:** Active. Marketing uses "Podium traffic +108.4%" as a mannequin but no skill/demo exploits `/data_lab/web_traffic/`.

### D6. LinkedIn post corpus with reactor graphs (`/apis/posts`, `/social_post/*`)
- **One-line:** Get company + executive LinkedIn posts with engagement metadata; per-post reactor lists up to 5,000 reactors with full profile details.
- **Evidence endpoints:** `POST /social_post/professional_network/search/live`, `POST /social_post/professional_network/enrich/live` (MCP: `search_linkedin_posts_by_keyword`, `retrieve_linkedin_posts`); legacy `GET /screener/social_posts`.
- **Competitive diff:** Apollo/PDL/Clearbit — zero. PredictLeads — no LinkedIn pipeline. Phantombuster — self-run scrapers. Taplio — own data, own use case. **The 5,000-reactors-with-profile surface is literally unmatched** — foundational for competitor-CI (who engages with your competitor's posts = churn map).
- **Economic viability:** Enterprise-quoted. Legacy `/screener/social_posts` is credit-based.
- **Maturity:** Live since pre-period but under-marketed — one mention on `/vs/proxycurl`, otherwise near silent.

### D7. First-hire-per-department + international-expansion as Watcher-native primitives
- **One-line:** `first_person_hired_in_company_department` fires once per company per department; `international_hiring_expansion` fires on first hire in a new country.
- **Evidence:** Watcher API. Documented triggers.
- **Competitive diff:** Unique. PredictLeads has `hires_key_personnel` but not "first-ever in department". Revelio has aggregate flows, not first-hire-event. The "first Head of Data in Mexico the day it happens" product is 6 lines of Watcher config on Crustdata and a six-month research engagement anywhere else.
- **Economic viability:** Enterprise webhook tier.
- **Maturity:** Nov 15, 2025 (Signal Watcher).

### D8. Job-posting NLP for backend/AI stack detection
- **One-line:** Extract technologies mentioned in hiring reqs — Snowflake, Databricks, Pinecone, OpenAI, Anthropic, LangChain, HuggingFace — the stack BuiltWith *structurally cannot see* (no HTML/JS footprint).
- **Evidence endpoints:** `POST /job/search` + `POST /data_lab/job_listings/`; company-level aggregation in `/company/enrich`.
- **Competitive diff:** BuiltWith (111k technologies, 673M domains) detects *deployed* frontend + pixels; invisible to Snowflake/Databricks/Jira/Okta/K8s. Crustdata sees *intent-to-deploy* via job postings. PredictLeads + TheirStack are the category peers (3 players total). BuiltWith+Crustdata fusion catches the intent→deployment window.
- **Economic viability:** Job search at 0.03/result.
- **Maturity:** Active. BuiltWith category taxonomy not published; open-ended.

### D9. Investor-portfolio inverse query
- **One-line:** Given an investor name, return their portfolio companies with holdings/performance.
- **Evidence endpoint:** `GET /data_lab/investor_portfolio/?investor_name={name}` (Composio: `CRUSTDATA_FETCH_INVESTOR_PORTFOLIO_DATA`).
- **Competitive diff:** PitchBook/Crunchbase/CB Insights all have this UI-side; none expose an *inverse* query API at Crustdata's price point. Crustdata *does not market it* — agent_10 flags it as dark zone; *agent_07 flags Crustdata as structurally weak on investor entities*. The asymmetry: the API *can* query the dimension, but the surrounding entity model is thin (no investor object, no fund/vintage/IRR). So the use case is "monitor Tier-1 fund adds" not "full investor diligence."
- **Economic viability:** Quote-based.
- **Maturity:** Composio-listed; no third-party app built on it.

### D10. Live-crawl / real-time modes (`enrich_realtime=True`, `/*/live`)
- **One-line:** Force a fresh LinkedIn/web fetch within ~10 minutes of the call, for arbitrary company/person, via public API.
- **Evidence endpoints:** Enterprise `/person/professional_network/enrich/live` (7 credits, live), `/company/professional_network/search/live` (2 credits), legacy `/screener/company?enrich_realtime=True`.
- **Competitive diff:** PDL is monthly batch. Apollo is cached. Revelio serves from cache. LiveData is subscription-only panel. Crustdata is the only workforce-data vendor with *public-API sub-hour re-crawl* for an arbitrary entity.
- **Economic viability:** 7 credits/live-enrich (~$0.14). Enterprise-gated.
- **Maturity:** Active.

---

## III. Commoditized Zone (avoid)

Anything Crustdata does that ≥5 competitors also do. *Banned from idea generation — no differentiation possible.*

- **Static firmographics:** name, domain, website, LinkedIn URL, industry, HQ location, year founded, employee_count_range, company_type, markets, basic taxonomy. Every commodity vendor ships this. PDL ships a wider field set than Crustdata here.
- **Point-in-time headcount total** (without growth deltas). LinkedIn, Apollo, PDL, ZoomInfo, Cognism, Clearbit/HubSpot all have it.
- **Current-role title and current employer** on a person. Every people-data vendor has this. Crustdata's *past-role context* is differentiated (D4), but "current title" alone is not.
- **Business email with verified flag.** Every vendor. Crustdata's `contact.business_emails[].status ∈ {verified, unverified}` is standard.
- **Total funding raised + last-round headline.** Crunchbase, PitchBook, Apollo, PDL, Clearbit all have this. Crustdata is *worse* here — no per-round array, no valuation, no lead-investor flag, no instrument.
- **LinkedIn connections count, follower count point-in-time.** Everyone has it. *Growth deltas on follower count* (D2) are the differentiator, not the level.
- **Glassdoor-style employee reviews** (overall_rating, culture_and_values_rating, work_life_balance_rating). ZoomInfo, Coresignal, Crustdata all ship — commodity.
- **G2 / software_reviews counts and avg ratings.** Direct G2 + every data vendor that licenses the feed. Commodity.
- **Recent news URL / press mention.** Apollo, Owler, Meltwater, ZoomInfo Scoops — commodity.
- **Competitor graph (similar companies).** Apollo, Clearbit, PDL affiliates — everyone has a version.
- **Current-employer industry taxonomy (LinkedIn industries).** All LinkedIn-sourced vendors have it. Industry taxonomy is 147 LinkedIn-flat; *weaker* than PitchBook (30k+ verticals), CB Insights (500+), Tracxn (2500+).
- **Raw LinkedIn skills on a person.** `skills.professional_network_skills` is a flat string array. PDL + Apollo expose it; Crustdata has no ONET/ESCO canonicalization edge.
- **Static job posting count per company.** LinkUp + Coresignal + Revelio all have it. Crustdata wins on *function-level QoQ/6mo growth*, not on the static count.
- **Email → person reverse lookup.** Commodity.

Do not build products that exist inside any of these commoditized axes in isolation.

---

## IV. Dark Zone (the richest seam)

Endpoints that exist in docs / Composio / dataset surface but that Crustdata does NOT heavily market AND where no third-party app has shipped.

1. **Watcher API (`crustdata.com/apis/watcher`).** *The single biggest asymmetry in the entire surface.* 6 trigger primitives shipped Nov 15, 2025; zero third-party apps exploit the push model as of Apr 19, 2026. Everyone still polls. Build anything — job-change-to-CRM-update agent, funding-round-to-LinkedIn-congrats agent, champion-left-account-to-CS-alert agent.
2. **`POST /data_lab/headcount_by_facet/` + `/data_lab/headcount_timeseries/`.** Company headcount time-series segmented by role / region / seniority, back 3–5 years dense for top companies. The LinkedIn monthly panel priced at $100k+/yr by Revelio. Composio-listed, zero demos from Crustdata.
3. **`POST /data_lab/web_traffic/`.** Monthly-visitors timeseries in `/data_lab/*`. SimilarWeb-grade, never demoed as an anomaly-detection primitive. The homepage shows "Podium +108.4%" once and never again. A traffic-radar skill is 200 LoC.
4. **`GET /data_lab/investor_portfolio/`.** Investor-inverse query — Composio tool #3. Crustdata markets "deal sourcing" (pre-investment); zero post-investment/portfolio-ops surface. Blue ocean inside their own dataset.
5. **`POST /social_post/professional_network/enrich/live`** with the 5,000-reactors-per-post capability. Referenced only on `/vs/proxycurl`. Every CI / reputation-risk / competitive-monitoring use case lives here. Klue, Crayon, Kompyte charge $30–$200k/yr for less data.
6. **`POST /data_lab/funding_milestone_timeseries/`.** Cohort funding analytics — "every SaaS that raised Series A 2022-Q1–Q3 with no follow-on." Composio tool #5. Zero demos.
7. **`POST /dev_platform/enrich` standalone.** Dark D3. The LinkedIn↔GitHub graph without the person-enrich dependency. No marketing.
8. **`POST /employee_review/enrich` standalone.** Glassdoor-class with per-field timestamps. No demos; no case study; no skill.
9. **Product Hunt launches / SEC Form D / news-press-mentions index** (listed on `/datasets/company-data` as indexed sources). No API pages, no skills, no demos. Each is one skill away from a product.
10. **v2025-11-01 endpoints (Bearer + `x-api-version`).** Shipped ~Nov 2025; Composio, Zapier, Deco all still target **legacy `/screener/*`**. There are **no official first-party SDKs in TS/Go/Python.** A typed TS SDK over the 12 modern endpoints would immediately become the reference.
11. **`POST /web/search/live` + `POST /web/enrich/live`.** Shipped Jan 22, 2026 as the flagship of 2026; Show HN got 10 points / 0 comments. Composio toolkit does not expose `/web/*`. The token-efficient entity-linked RAG substrate that every LangChain/CrewAI/AutoGen agent framework could drop in.
12. **`crustdata_company_id` / `crustdata_person_id` as canonical identifiers.** Every Crustdata response carries stable IDs. No third-party graph DB, vector DB, or CRM treats them as first-class — everyone keys on LinkedIn URL or domain. A "knowledge-graph sync" tool keyed on Crustdata IDs would be novel.

**The pattern:** Crustdata's GTM optimizes for the AI-SDR + recruiting + VC-deal-sourcing wedge because that wedge pays today. Roughly half the data graph is structurally unmarketed. That under-promotion is the opportunity shape, and the timing window is 18–24 months before their GTM closes it.

---

## V. Economic Constraints That Shape Products

*From agent_09 (pricing/limits). Every number below comes from public docs or triangulated community signal.*

### Hard numbers (published)
- **Rate limit:** **15 requests/minute per key** across most endpoints (= 900 rph = 21,600 rpd ceiling per key). 429 on breach. Enterprise plans get higher but not published.
- **Credit expiry:** **6 months from purchase.** No rolling-annual. Use-it-or-lose-it.
- **Batch sizes:** `/person/enrich` max 25 profiles/request; `/web/enrich/live` max 10 URLs/request.
- **Free tier exists** (no credit card), but **credit count not published.** Community inference: ~100 credits/mo permanent free.
- **No published $ / credit.** No public SLA. No published overage rate. No published webhook pricing.

### Per-credit cost (triangulated from competitor comp page + HN commentary)
- **~$0.02/credit** is the best community-derived peg (HN 47387103: Companies.social launch explicitly cited "$0.04/lookup tax" on Crustdata — company enrich is 2 credits → $0.04/lookup → $0.02/credit).
- `/company/identify` = **free**
- `/company/enrich` = 2 credits ≈ **$0.04**
- `/person/enrich` basic = 1 credit ≈ **$0.02**
- `/person/enrich` full (biz email + personal email + phone + dev) = 7 credits ≈ **$0.14**
- `/web/search/live` = 1 credit ≈ **$0.02/query**

### Tier inference
- **Starter ~$95–$200/mo** (3rd-party aggregators; prospeo/gurusup/skywork cite this band).
- **Growth $1–3k/mo.**
- **Enterprise $5k+/mo.**
- **Harmonic comparator:** $25k/yr minimum, ~$10k/seat/yr, 3-seat min. **ZoomInfo:** $50k/yr floor. **PDL:** $0.20–$0.28/credit — **10× Crustdata at full-enrich unit level** (Crustdata's 7-credit full enrich $0.14 vs PDL's 1-credit equivalent $0.20–$0.28). **Clearbit/HubSpot Breeze:** $0.10/enrichment. **Coresignal Premium:** $0.03/record at $1,500/mo tier.

### What pricing KILLS
- **Any consumer-facing $5/mo app.** Even 25 lookups/user/mo at $0.02/lookup breaks even — free tier covers ~14 users total.
- **Free ad-supported company-lookup search.** $0.02 cost/lookup vs $0 revenue.
- **Reselling arbitrage.** Thin ~3× markup + likely TOS violation.
- **Bulk list-building > 22k/day via API.** Rate-limit ceiling. Must shift to bulk flat-file (enterprise-quoted, ~$5k+/mo).
- **Self-serve API marketplace.** 15 rpm cap below marketplace aggregate throughput.
- **Anything where unit value per user < $30/mo with meaningful lookup volume.**

### What pricing ENABLES
- **$200+/mo B2B SaaS, 5–50 seats.** Absorbs $50–$150/seat in data cost. Natural fit.
- **$500+/mo KYB/compliance/onboarding.** High per-customer LTV, low lookup volume, high price-insensitivity. Strongly viable.
- **Research co-pilot for AI agents.** `/web/search/live` at ~$0.02/query is genuinely cheaper than Perplexity's API. Token-efficient response shape fits. 5–20 calls per task × $0.10 cost → $0.50 revenue break-even.
- **Agentic tools calling Crustdata N times per task** where agent value > $1/task (lead-gen automation, research co-pilot, recruiter AI).
- **Investor intelligence / VC deal-flow tools.** Low volume, extreme per-decision value.
- **Real-time alerts products** for small-watchlist (<1,000 companies) via polling; enterprise webhook for bigger.

**Rule of thumb:** price floor per customer = ~$50/mo. Sweet spot $200–$2,000/mo B2B SaaS where data cost = 10–20% of customer's price. Enterprise-data-cost products >$5k/mo work if the value per decision justifies the full tier.

---

## VI. 2025–2026 Virgin Territory (<6 months old, zero/minimal third-party adoption)

*From agent_11. These are the concrete shipping dates movers can beat.*

### HOT (<90 days, with shipping dates)
1. **`/web/search/live` + `/web/enrich/live`** — shipped **Jan 22, 2026** (Product Hunt #5, 346 upvotes). Entity-linked, deduped, up to 10 URLs/fetch. **Show HN (Feb 25, 2026): 10 points, 0 comments.** Composio does NOT expose `/web/*`. No apps built on it outside the community `crustdata-mcp` PyPI package.
2. **v2025-11-01 API scheme** — shipped **~Nov 1, 2025.** New Bearer + `x-api-version` header, 12 canonical endpoints. **Composio/Zapier/Deco still target legacy `/screener/*` + `Authorization: Token`.** Modernization invisible to the tool ecosystem. No official first-party SDK in TS/Go/Python.
3. **MCP Server exposing Watcher** — shipped **~Mar 2026.** Claude Desktop / Code can subscribe to Watchers via MCP. Only the Crustdata-authored `crustdata/skills` (6 stars) uses it.
4. **`crustdata/skills` open-source repo** — latest release **Apr 9, 2026**. Two skills only (email-enrichment, candidate-sourcing). **7-to-1 coverage gap** between what's marketed (~2 skills) and what the API exposes (~14 Composio tools, ~20+ data surfaces).

### RECENT (3–12 months old, weak third-party presence)
5. **Signal Watcher (webhooks)** — shipped **Nov 15, 2025** (PH #4, 205 upvotes). **Zero consumer-facing third-party apps** as of Apr 19, 2026 — the starkest whitespace in the entire product. No Chrome extension, no CRM plugin, no Slack bot, no n8n/Zapier community workflow subscribes to Watcher webhooks and does something novel.
6. **Person Search API with 60+ filters** — shipped **Sep 17, 2025** (PH #3, 743 upvotes). Used internally by agent.ai / MNTN / YC; no standalone "people-search-as-a-service" consumer product built on it.
7. **People Dataset (bulk Parquet)** — shipped **May 28, 2025** (PH #2). No public embedding-indexed semantic candidate search built on top.

### Near-term (ContextCon, today, Apr 19, 2026)
8. **First YC hackathon in Bangalore** — live *today*. 6-hour build, mandatory Crustdata API usage, $8k/$3k/$1k prizes. Whatever ships will tell us what 100+ engineers decided was buildable in 6 hours on these primitives. Worth monitoring in Wave 2.

**Pattern:** Capability has lapped awareness. HN has 1 Show HN with 0 comments. Crustdata's founders post ~1x/year on Twitter (vs Clay/Apollo/ZoomInfo founders at 2–4x/week). No public Slack / Discord / community. A third-party builder ships something on Watcher or `/web/search` today and they are *first*.

---

## VII. Known Weaknesses (where to NOT play)

Honest failure modes — products in these weak areas will lose head-to-head.

1. **Funding diligence / per-round detail.** No per-round array, no pre/post valuation, no lead-investor flag, no instrument (SAFE/debt/convertible), no board seats, no dilution. 5-field `funding.*` sub-object only. **PitchBook, Harmonic, Crunchbase win.** Do not build diligence tools.
2. **Investor entity / fund intelligence.** `funding.investors` is a `string[]`. No investor object, no AUM, no fund vintages, no LP-commit tracking, no MOIC/IRR/DPI, no partner-level attribution. **PitchBook owns this.** Dark-zone `investor_portfolio` gives a slim inverse query but not full profiles.
3. **India MCA/RoC ground truth.** No integration with MCA21, PAS-3, AOC-4, MGT-7, SH-7, ADT-1. **Tracxn owns India filings.** Crustdata's "strong India" claim is LinkedIn depth + founder signal, not filings.
4. **Phone verification at scale.** `contact.phone_numbers` ships as a flat `string[]` with no source/type/last-seen metadata. **Cognism (12.5M "Diamond Data") + ZoomInfo + PDL all win.** Do not build cold-dial products.
5. **Historical headcount depth.** 3–5 years dense on marquee companies, 1–3 years on tail. **Revelio (2008+) + LinkedUp (2007+, jobs) win for academic-grade panels.** HN commenter (2026-03-15, ptrtht) flagged "6–9 months stale" on some fields.
6. **Inflow / outflow / churn as first-class fields.** Crustdata has net `roles.growth_*`, not gross. **Revelio owns inflow/outflow/transitions. LiveData Technologies owns labeled layoff-vs-quit classifier.**
7. **Demographic cuts** (gender, ethnicity, age). Not exposed. **Revelio ships them for DEI/policy research.** Crustdata is GDPR-conservative here.
8. **Seniority scale as a headcount aggregation.** Crustdata exposes `seniority_level` on Person but not `headcount_by_seniority_timeseries`. Revelio has it.
9. **Technographic scanning** (JS fingerprinting, HTTP headers, SSL CT, WHOIS, IP/ASN, subdomains). Nothing documented. **BuiltWith, Wappalyzer, SecurityTrails, Censys own this.** Crustdata's tech detection is intent-via-job-posting only, not deployment evidence.
10. **Pricing page extraction, screenshot diff, website change detection.** None. **Visualping, Kompyte own this.** Crustdata's own blog recommends external tools.
11. **Industry taxonomy depth.** LinkedIn-flat 147 industries. **PitchBook 30k+ verticals, CB Insights 500+, Tracxn 2,500+, Lightcast ESCO/O\*NET-SOC-grade.** Sector-thematic VC sourcing cannot be done cleanly.
12. **Salary inference.** No `inferred_salary`. **Revelio + Lightcast ship modeled wages.** Where salary appears it's "where public" (US pay-transparency + EU directive).
13. **Occupation code normalization on jobs.** No ONET/ESCO/SOC. "Senior ML Engineer" vs "ML Engineer II" dedup is weak. **Lightcast + Revelio win for occupation-code-grade counts.**
14. **Non-English NER.** PredictLeads covers EN/ES/DE/NL/FR. Crustdata is English-biased.
15. **Event history / taxonomy breadth.** 6 Watcher trigger primitives vs PredictLeads' 29 typed event categories + 9M-event historical corpus. Crustdata has no queryable event-history warehouse — watchers fire forward only. **PredictLeads owns backtesting.**
16. **Pricing opacity.** No public $ tiers. No SLA. No overage rate. No concurrent-connection cap. No rollover. Kills procurement-bound buyers, raises activation friction for builders.
17. **v2025-11-01 ecosystem.** Composio/Zapier/Deco still on legacy. No first-party SDKs. Docs at `docs.crustdata.com/docs/*` are gated behind login.

---

## VIII. Summary — The Three Crustdata Superpowers

*Stack these and build what nobody else can.*

### Superpower 1 — Watcher: the push-first event substrate over LinkedIn-canonical entities
- **Endpoint:** `crustdata.com/apis/watcher` + webhook delivery. 6 trigger primitives including `linkedin_post_with_keywords`, `person_starts_new_job`, `first_person_hired_in_company_department`, `international_hiring_expansion`, `new_funding_announcement`, `company_headcount_increased_by_pct` / `department_headcount_range`.
- **Evidence files:** agent_05 (§1, §10), agent_04 (§11), agent_11 (H2, Nov 15 2025).
- **Timestamp of maturity:** Shipped **Nov 15, 2025** as "Signal Watcher" (Product Hunt #4). No third-party consumer apps as of **Apr 19, 2026**.
- **Why it's a superpower:** No commodity competitor has this as a webhookable product. PredictLeads' firehose lacks LinkedIn + person-level watches. Harmonic is UI-only. Push architecture inverts the SDR/RevOps/VC/CS workflow from polling to triggered.

### Superpower 2 — Composable time-derived growth filters as search primitives
- **Endpoint:** `POST /company/search` (self-serve, 0.03/result, ~$0.0006/result) + `POST /data_lab/headcount_by_facet/` + `POST /data_lab/headcount_timeseries/` + `POST /data_lab/web_traffic/` + `POST /data_lab/funding_milestone_timeseries/`.
- **Fields:** `roles.growth_6m`, `roles.growth_yoy`, `hiring.openings_growth_percent`, `followers.mom_percent` through `.yoy_percent`, per-role percentile bucket fields, `linkedin_headcount_by_role_six_months_growth_percent`, `job_openings_by_function_qoq_pct`, `headcount_{mom,qoq,6m,yoy,2y}_pct`. All filterable at search time.
- **Evidence files:** agent_02 (§B1), agent_04 (§1.4, §2.3, §7, §11), agent_06 (§8), agent_08 (§4).
- **Timestamp of maturity:** Core filter surface active since pre-2025; v2025-11-01 API unified schema Nov 1 2025; 60-filter People Search Sep 17 2025.
- **Why it's a superpower:** Single-call queries that require two products + post-processing in PDL, are impossible in Apollo, and require WRDS-SQL-seats in Revelio. Compose across headcount-by-dept × traffic × followers × funding × hiring velocity in one HTTP call at search tier (cheapest in the catalog).

### Superpower 3 — LinkedIn ↔ GitHub identity graph + per-role historical context
- **Endpoints:** `POST /person/enrich` with `dev_platform_profiles` field group (+1 credit add-on) + standalone `POST /dev_platform/enrich` + per-past-role context on `experience.employment_details.past[]`.
- **Fields:** `dev_platform_profiles[].confidence_score` (LinkedIn↔GitHub match), `.org_memberships[]` (with created_at / last_updated), `.declared_handles[]` (GitHub-canonical social accounts), 22 GitHub-native fields. Plus `experience.employment_details.past[].company_headcount_latest`, `.seniority_level`, `.function_category`, `.years_at_company_raw`, `.business_email_verified` — for every past job of every person.
- **Evidence files:** agent_03 (§B10, B11, B12, B1, B5).
- **Timestamp of maturity:** Active baseline for v2025-11-01. No competitor product surfaces this. Composio exposes `/dev_platform/enrich`; Crustdata markets it in one Clay blurb.
- **Why it's a superpower:** Every DevRel / B2D GTM, every champion-graph product, every recruiting platform targeting developers, every investor-scout tool for AI/infra founders needs this. PDL ships two strings. Apollo ships nothing. Building a developer-identity-resolved graph elsewhere means hiring an NER team and running 3–5 years.

---

## The one-line thesis

**Build on Crustdata where push (Watcher) + time-derived filters (growth deltas) + the LinkedIn↔GitHub graph intersect. Avoid diligence-grade funding, phone dialers, demographic cuts, technographic scanning, and industry-taxonomy-deep VC thematic products — those are losing head-to-heads. The virgin territory has shipping dates between Sep 2025 and Apr 2026, zero third-party apps, and a 60–90 day window before the ecosystem catches up.**
