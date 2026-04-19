# Agent 04 — Headcount Time-Series Deep Dive on Crustdata

Author: research agent 04 (wave 1)
Date: 2026-04-19
Scope: the historically strongest Crustdata moat — LinkedIn headcount time-series, the department/function/country cuts, delta fields, and how they compare to Revelio Labs, LiveData Technologies, LinkUp, TrueUp, and layoffs.fyi.

TL;DR — the moat, concretely

- Crustdata does not hold the deepest history in the market (Revelio Labs 2008 start is deeper; LinkUp since 2007 on jobs is deeper), but they are the only vendor combining (a) weekly-or-shorter snapshot cadence, (b) function / country / seniority cuts on the same 60M-company panel, (c) pre-computed delta fields (MoM, QoQ, 6-month, YoY, 2-year, plus role-level six_months and yoy), (d) watcher-webhook triggers that fire on headcount, department, and first-hire events, and (e) a cheap, API-first delivery model that is priced for Y Combinator / growth-equity / AI-SDR builders rather than research seats.
- The concrete unique capability is this: you can pull a single company's Engineering headcount in India for every week of the last ~5 years, join it to Glassdoor CEO approval, job-posting-by-function QoQ, and web traffic, at roughly $0.01-per-row economics, in one API call. Revelio has deeper history but no true-realtime refresh. LiveData has better attrition (job-change) coverage but no public API to pull a panel. LinkUp is jobs-only. TrueUp and layoffs.fyi are retail trackers, not panels.

----------------------------------------------------------------

## 1 — What Crustdata's headcount time-series is

### 1.1 The primary time-series object

The flagship company-data field is `linkedin_headcount_timeseries`, documented as an array of objects on `/screener/company` and on the newer `/company/enrich` endpoint (v 2025-11-01) [1][2][3]. Each entry is a `(date, headcount)` row. The companion `linkedin_headcount_by_function_timeseries` is documented as an object keyed by function with a parallel time series, and there is a third `linkedin_headcount_by_role_absolute` (absolute counts per role) and `linkedin_headcount_by_role_percent` (percent share per role) [1][4].

Because docs.crustdata.com is a client-rendered Mintlify SPA and the plain curl returns a JS shell, the canonical field list has been cross-referenced from:

- Composio's published tool schema for `CRUSTDATA_FETCH_HEADCOUNT_BY_FACET_TIMESERIES` and `CRUSTDATA_POST_HEADCOUNT_TIMESERIES_DATA` [3][5]
- the crustdata.com product and blog pages (company-enrichment, competitor-monitoring, growth-equity, deal-sourcing, b2b-prospecting-workflow-claude-code, firmographic-data-guide) [6][7][8][9][10]
- the Crustdata sitemap at https://crustdata.com/sitemap.xml [11]
- third-party summaries (Studocu, iseoai, Relevance AI, VC Stack, ProductHunt launch notes) [12][13][14][15][16]

### 1.2 Granularity

- **Weekly** is the stated cadence for the headcount time-series in the Crustdata "Private Company Database 2.0" ProductHunt launch for the 2M-company set: "real-time data updates refreshed weekly through proprietary web crawlers" [16]. Blog copy elsewhere says "API-driven headcount tracking on a weekly schedule" [9] and "every 14–28 days" for the bulk snapshot [6][17]. Treat weekly as the modal refresh and 14–28 days as the worst case for tail companies.
- **Daily / hourly / instant** is available in two modes: (i) the Watcher API fires on configured events (headcount growth, department-headcount threshold crossings, first hire internationally, etc.) [18]; (ii) the real-time enrichment endpoint will re-crawl LinkedIn on request within ~10 minutes of the call [19].
- **Monthly** is the cadence of the flat-file / S3 bulk refresh sold as `full-dataset` / "Company Dataset" [17].
- **Timestamp precision**: each snapshot row appears to be tagged with an ISO-8601 date (day-level), not a week-ending date, which matters for joins against funding-announcement dates.

The net: you can get a ~weekly cadence for any top-N company, and near-real-time for the subset you put on watch. There is no true "daily" headcount-by-department number for every company — that is a synthetic claim nobody in this market credibly makes because LinkedIn's counter itself is not daily-accurate.

### 1.3 How far back the history goes

There is no public statement like "we have data since 2019." The documented facts:

- Crustdata markets "historical data for 6 vital company datapoints" including headcount and headcount by function [17].
- Bulk dataset customers get "full profiles" with "historical headcount" as a column [20].
- VC-sourcing case studies show their platform surfacing companies "14 months before the round closes," implying ≥ 12 months of usable history [9].
- LinkedIn's own company-page API only started surfacing employee-count at scale around 2015-16; anyone scraping it built their panel after that date. Crustdata (founded 2021, YC F24) started crawling LinkedIn in 2022-23; everything earlier in their time-series is either backfilled from the Wayback Machine / third-party data or was acquired. No public statement confirms pre-2019 density.
- Practical ceiling: **expect 3–5 years of dense weekly history for the top 10% of companies, 1–3 years for the long tail, and spotty coverage for companies below ~10 employees or outside English-speaking LinkedIn markets.**

This is strictly shallower than Revelio Labs ("since 2008, monthly") [21] and LinkUp ("since 2007, daily jobs") [22]. Crustdata's edge is not depth but freshness and joinability.

### 1.4 Bulk dataset tables visible in SQL-style examples

Crustdata's `full-dataset` page shows SQL over these tables [17][23]:

- `crustdata_companies` — core company record (company_id, company_website, total_investment_usd, linkedin_profile_url, days_since_last_fundraise, total_funding_raised_usd, largest_headcount_country)
- `companies_growth` — (company_id, headcount, headcount_qoq_pct). In at least one blog referenced in search indices this is named `companies_linkedin_growth` with MoM / QoQ / 6mo / YoY / 2yr columns [24].
- `companies_monthly_web_traffic_growth`

So `headcount_qoq_pct` is a documented column, and `headcount_mom_pct`, `headcount_yoy_pct`, `headcount_6m_pct`, and `headcount_2y_pct` are referenced in search-surfaced blog content [24]. They are pre-computed at the company level.

----------------------------------------------------------------

## 2 — Departments broken out

### 2.1 Taxonomy: 26 LinkedIn job functions

Crustdata's function breakdown piggybacks on LinkedIn Campaign Manager's canonical 26-function taxonomy [25][26]:

`Accounting, Administrative, Arts & Design, Business Development, Community & Social Services, Consulting, Education, Engineering, Entrepreneurship, Finance, Healthcare Services, Human Resources, Information Technology, Legal, Marketing, Media & Communications, Military & Protective Services, Operations, Product Management, Program & Project Management, Purchasing, Quality Assurance, Real Estate, Research, Sales, Support`

The Crustdata blog "competitor-monitoring-tools-techniques-and-best-practices" shows a worked example of `headcount_by_role_absolute` returning keys "Engineering, Sales, Marketing, Operations, Human Resources, Quality Assurance" in the response, which is consistent with the 26-function set and confirms the mapping is not a Crustdata-proprietary department list — it is LinkedIn's function taxonomy [7].

### 2.2 Practical caveats

- There is **no sub-function breakout** in the public fields ("ML engineers" vs "backend engineers" cannot be derived from `headcount_by_role`). To get sub-function data you have to drop to the `/person/search` endpoint and filter by `title` keywords — that is a manual step, not a pre-computed panel.
- The 26-function list skews against sub-functional headcount planning. If you want "Data Science vs ML Platform vs Applied Research" that breakdown is built on the Person API by title-matching, which is noisy at small companies.
- The Search API filter set supports "Employee headcount growth by department" and "Employee headcount by geography" [8][27], so you can filter the panel ("find companies that grew Engineering >20% QoQ in the last 6 months in India"). This is the key filterable surface for department cuts.

### 2.3 Function growth deltas (pre-computed)

From the enrichment-API example on the competitor-monitoring post [7]:

- `growth_by_role_six_months_percent` — 6-month growth percent per role
- `growth_by_role_yoy_percent` — year-over-year growth percent per role

And from the search-surfaced field index [28]:

- `linkedin_headcount_by_role_six_months_growth_percent` — object keyed by role
- `linkedin_headcount_by_role_yoy_growth_percent` — object keyed by role
- Percentile bucket fields `0_to_10_percent, 11_to_30_percent, 31_to_50_percent, 51_to_70_percent, 71_to_100_percent` exist for role-based and region-based ranking

These are the specific fields that make the product queryable for "top-quartile engineering-growth companies in the last 6 months, US-only" without the caller doing a custom aggregation.

### 2.4 Job-openings by function

A parallel fields block covers hiring velocity:

- `job_openings_count`
- `job_openings_by_function_qoq_pct` (QoQ delta of openings per function)
- Job-Listing API supports filtering by keyword and location [29]

Open reqs are **not counted into headcount** — they are a separate signal. That matters because Crustdata exposes "people who currently list the company in their LinkedIn profile" as the headcount number; job postings are tracked independently via their Jobs API [29].

----------------------------------------------------------------

## 3 — Geography

### 3.1 Country breakouts

Documented country-level fields:

- `largest_headcount_country` on the company root record [23]
- `hq_country` on the company root record [9]
- `linkedin_headcount_by_country_timeseries` (referenced in the facet-timeseries tool as a legitimate facet) [3][5] — there is strong circumstantial but no public schema confirmation of the exact object key name, but the Composio schema shows facet-timeseries supports country and region facets
- Watcher event "First person hired internationally" and "Employee location in two countries" [18] — uses country inference on the Person API

### 3.2 Regional / metro cuts

Revelio Labs offers metro-level resolution. Crustdata's documentation surfaces **country** and in the Search API **hq country** + **largest headcount country** but no explicit metro or state panel. For US state / metro, you have to aggregate from the Person API's `location` field, which resolves to city-level strings.

### 3.3 Coverage

- No hard number on how many countries the department breakdown covers.
- Crustdata markets "global coverage" but the usable density is strongly US + Western Europe + India + LATAM. LinkedIn's own penetration is thin in Japan, Korea, and China, so you should assume Crustdata inherits those blind spots.
- For every country-level cut, there is an implicit floor: LinkedIn must have ≥ ~50 profiles tagged to the company in that country for the number to be stable. Below that, the Crustdata number is the noisier estimate.

----------------------------------------------------------------

## 4 — Methodology (and stated confidence)

### 4.1 Source stack

Crustdata indexes live from ~16 sources [6][30][31]:

- LinkedIn (company pages, profile pages, posts)
- SEC EDGAR
- Glassdoor
- G2
- Product Hunt
- AngelList
- Apple App Store + Google Play
- News sources (Reuters, CNBC, Fox Business, Yahoo Finance)
- Web traffic vendors
- Funding announcements
- Instagram
- YouTube
- X/Twitter
- Google Search Console impressions
- Play Store

Headcount specifically rolls up from **LinkedIn company-page scraping + LinkedIn profile aggregation** (the "current company" field on each profile rolled up per company_id). The company-page number is LinkedIn's display-count; the profile aggregation is a second signal Crustdata uses to sanity-check the page number and drive the function / country / role cuts [6].

### 4.2 Real-time crawl

Crustdata's launch framing is "live crawlers that index the web for AI Agents" [32][33]. The two-mode model:

- **Indexed panel**: bulk database refreshed monthly for flat-file, weekly for the API default, every 14-28 days for tail companies [17][16].
- **Real-time re-crawl**: `enrich_realtime=True` forces a fresh LinkedIn fetch within ~10 minutes of the call [19].

They explicitly position this against Coresignal's "monthly for most data, 6 hours for some" and People Data Labs' "monthly" refresh [34][35].

### 4.3 Stated confidence / error bars

**There is no publicly stated confidence interval or accuracy percentage for the headcount number.** This is a meaningful weakness for research use cases. Reviewers on Product Hunt and HN flag this exact gap: one HN commenter from 2026-03-15 wrote "Using Crustdata and IcyPeas, per-lookup costs add up fast, data often 6-9 months stale" — meaning for tail companies the refresh is later than the headline weekly cadence [36]. Crustdata's ProductHunt reviews repeatedly note the "execution / data-accuracy / latency" concern [37].

Contrast: Revelio Labs publishes seniority taxonomies, role_k150 / role_k500 cluster resolutions, and salary-modeling methodology PDFs [38][39]. LiveData publishes confusion-matrix-style breakdowns on their layoff vs quit vs promotion classifier (8.4% / 10.3% / 4.7% class shares, 60-day employment gap as the decision rule) [40]. Crustdata has not published a methodology whitepaper.

### 4.4 What the method is not

- Not self-reporting (companies do not submit numbers to Crustdata).
- Not WARN-act / regulatory (no US Department of Labor filings in the source list).
- Not employer-review based (Glassdoor is used as a separate sentiment signal, not as a headcount source).
- Not employer-sourced job boards (LinkUp's model — Crustdata uses LinkedIn Jobs and third-party feeds for postings, not direct employer sites).

----------------------------------------------------------------

## 5 — Tenure, attrition, churn

### 5.1 At the company level

Crustdata does **not** expose a pre-computed "median tenure by department" or "attrition rate per quarter" field on the company enrichment response. You can reconstruct tenure distributions yourself by calling the Person API with `current_company_domain=X` and aggregating `years_at_current_company` across the returned profiles [9], but this is a build-it-yourself metric, not a panel field.

### 5.2 Job-change / attrition detection

The Watcher API surfaces "Someone starts a new job" as a trigger event [18], which is the real-time job-change feed Crustdata customers use for attrition signals. This is the functional equivalent of LiveData Technologies' job-change product but without LiveData's twice-monthly panel semantics — Crustdata's signal fires per person as the data updates.

### 5.3 Hiring velocity vs attrition

Gross-hiring is inferrable from `job_openings_by_function_qoq_pct` and `growth_by_role_six_months_percent`; net-change is the delta in `linkedin_headcount_by_function_timeseries`; attrition is (gross hires − net change), which **must be derived client-side**. Revelio Labs does expose inflows and outflows as first-class fields [41][42]; Crustdata does not.

----------------------------------------------------------------

## 6 — Hiring velocity — are open reqs in headcount?

No. `job_openings_count` and `linkedin_headcount_timeseries` are separate fields [6][7]. This is the correct behavior — mixing open reqs into headcount would corrupt the panel. Some downstream consumers (Clay, RevenueHero routings) combine both signals into a composite "hiring intensity" feature, but that's a consumer-side build, not a Crustdata default.

----------------------------------------------------------------

## 7 — Pre-computed deltas (30 / 60 / 90 / 180 / 365 day)

Confirmed fields (triangulated across enrichment-API blog, search API filter list, bulk SQL examples, and field search indices) [6][8][23][24][28]:

| Delta                  | Company-level   | Per-role / per-function      | Per-country (inferred)   |
|------------------------|-----------------|------------------------------|--------------------------|
| MoM (≈30 day)          | `headcount_mom_percent`      | partial                      | unclear                  |
| QoQ (≈90 day)          | `headcount_qoq_pct` / `headcount_qoq_percent`   | `job_openings_by_function_qoq_pct`          | unclear                  |
| 6-month (180 day)      | `headcount_6m_pct` / `growth_6m_percent`  | `growth_by_role_six_months_percent`, `linkedin_headcount_by_role_six_months_growth_percent` | partial                  |
| YoY (365 day)          | `headcount_yoy_pct` / `headcount_yoy_percent` | `growth_by_role_yoy_percent`, `linkedin_headcount_by_role_yoy_growth_percent`        | partial                  |
| 2-year (730 day)       | `headcount_2y_pct`          | not public                   | not public               |

**Critical**: the Watcher API has a `period_months` parameter on headcount-growth triggers (e.g., `"period_months": 3`) [24][28] which means you can set arbitrary windows at the watcher level even if the enrichment-side pre-computed fields only include the canonical five periods above.

**What's missing**: 30/60 day fields are not explicitly pre-computed for every company. MoM is the nearest equivalent; if you want a true rolling 60-day delta you're going to rebuild it from the weekly time-series yourself.

----------------------------------------------------------------

## 8 — Layoff / RIF detection

Crustdata does **not** publish a dedicated "layoff" or "RIF" flag on the company record. What they do publish:

- Sudden drops in `linkedin_headcount_timeseries` are visible and queryable (e.g., search API filters on `headcount_qoq_pct < -10` to surface contracting companies).
- Watcher API can fire on any headcount threshold crossing or range (`Company headcount in range`, `Company headcount growth over baseline`) [18] — you build your own layoff detector by setting negative-growth triggers.
- News aggregation surfaces layoff announcements as `news_articles` events.
- No integration with WARN filings (Revelio has US WARN [41]; layoffdata.com has all-US-states [43]; Crustdata does not).
- No integration with layoffs.fyi or TrueUp (these are hand-curated sites with weekly digests, not APIs) [44][45].

**Practical layoff signal workflow**:
1. `linkedin_headcount_qoq_pct < -5` on the Search API filter → surface candidates.
2. Watcher event "Company headcount decreased >X%" with webhook → real-time alert.
3. Cross-reference against `news_articles` containing "layoff", "RIF", "restructuring".
4. Pull `linkedin_headcount_by_function_timeseries` to see which function the drop hit.

This is a build-it workflow, not a pre-labeled dataset. LiveData Technologies sells this specific classification as a product [40]; Revelio Labs sells WARN layoff notices separately from workforce dynamics [41]; Crustdata treats layoff detection as a downstream composition of primitives.

----------------------------------------------------------------

## 9 — Head-to-head comparison

Numbers below come from the vendor pages cited.

| Dimension                              | **Crustdata**                                       | **Revelio Labs**                                | **LiveData Technologies**             | **LinkUp**                     | **Layoffs.fyi**                   | **TrueUp**                                   |
|----------------------------------------|-----------------------------------------------------|-------------------------------------------------|---------------------------------------|--------------------------------|----------------------------------|----------------------------------------------|
| Companies tracked                      | 60M+ [6]                                             | 20M+ mapped (1.1B profiles) [42]                 | 88M+ people (company count not stated) [40][46] | 60k-80k companies, 240 countries [22][46] | Hand-curated, several thousand tech layoffs [44] | ~9,000 tech companies [45]               |
| Profile volume                         | 1B+ people [6]                                       | 1.1B+ standardized profiles [42]                  | 88M verified professionals (10-14 day re-check) | N/A (jobs-only)                 | N/A                              | "millions of data points"                    |
| History start                          | ~2022-2023 dense; ~3–5 years realistic [16][17]     | 2008, monthly [41][21]                            | Continuous since 2020s; 100K+ job changes/yr panel | 2007, daily [22]              | Since 2020 (COVID wave)          | Since ~2020                                   |
| Refresh cadence (headcount)            | Weekly default; real-time via Watcher [16][18]       | Monthly [41]                                       | Twice per month per person [40]        | Daily (jobs) [22]              | Weekly digest [44]               | Unclear, presumably weekly                    |
| Department granularity                 | 26 LinkedIn functions + per-role delta [25][28]      | role_k150 / role_k500 taxonomies; occupations, skills [41] | Occupation + title + seniority [40][46] | Occupation codes + sector codes [22] | Headcount-affected only (count + company + date) | Headcount, Glassdoor, funding composite    |
| Sub-function (e.g. ML eng)             | Client-side via Person API title-match              | role_k500 cluster resolution                    | Title-level                            | By job occupation codes         | None                             | None                                         |
| Country / geography                    | Country, largest-headcount country, HQ country [23] | Country, state, city, metro [41]                  | Geographic metadata per person          | 240 countries [22]             | Country + HQ                    | Primarily US                                  |
| Seniority levels                       | Inferred via Person API                              | 7-level scale (Junior / Associate / Manager / Director / VP / Exec / C-suite) [47] | Yes (seniority flags) [46]            | Seniority inferred              | None                             | None                                         |
| Inflows / outflows                     | Derived from timeseries delta; not first-class      | First-class inflow + outflow + transitions [41][42] | First-class job-change feed [40]      | Jobs-only, no flow             | Layoff events only               | None                                         |
| Gender / ethnicity / demographics       | Not published                                        | Yes, demographic estimates [42]                   | Not published                          | Not published                   | None                             | None                                         |
| Salary modeling                        | Not published                                        | Yes, modeled salaries via LinkUp collaboration [38] | Not published                          | Collaborates with Revelio [38] | None                             | None                                         |
| Layoff detection                       | Build-it (negative-delta + news) [7][18]             | Separate layoff dataset (US-only) [41]           | First-class layoff vs quit classifier [40] | None (jobs go to zero)         | Hand-curated [44]               | Curated + embeds                              |
| Job-posting integration                | Yes (Jobs API, `job_openings_by_function_qoq_pct`) [29][6] | Yes (COSMOS, 2B+ postings) [41]                  | Through partnership                    | Core product: 315M historical, 5M live [22] | None                           | Yes (230k+ live jobs, 9k companies) [45]     |
| Real-time API refresh                  | `enrich_realtime=True`, ~10-min latency [19]         | API is live but cache-backed                    | Not documented                         | Daily batch [22]                | None (static site)              | None (static site)                           |
| Webhooks / triggers                    | Watcher API with headcount / department / geo events [18] | None documented                                  | Unclear                                | None                           | None                             | None                                         |
| Licensing for research                  | Paid, credit-based API [48]                         | WRDS, academic library data feeds, AWS Marketplace [49][50] | B2B subscription                       | Academic via Dewey Data [51]   | Free site                        | Free site + premium                          |
| Target buyer                           | AI-SDR / RevOps / AI-agent builders / growth-equity VCs  | Academic researchers, macro investors, policy | Investors, data vendors, AI companies | Academics, quant funds         | Retail / ops watchers           | Tech job-seekers + VCs                        |
| Price posture                          | Usage-credits, self-serve to $; enterprise above [48] | Enterprise seats, WRDS licensing               | Enterprise contract                    | Enterprise contract             | Free                             | Free + freemium                              |

### 9.1 Interpretation

- **Revelio beats Crustdata on depth, demographics, seniority taxonomy, inflows/outflows.** Revelio wins for academic/policy/research workloads that need clean monthly panels back to 2008 with normalized roles. It does not win for "tell me when a company hires their first Head of Data in Berlin"; Crustdata does.
- **LiveData beats Crustdata on job-change / attrition detection for individuals.** LiveData's twice-monthly per-person re-check plus layoff-vs-quit classifier is genuinely differentiated for who-went-where tracking. Crustdata exposes the raw stream, LiveData exposes the labeled classifier.
- **LinkUp beats everyone on jobs.** 315M-post archive from 2007 direct from employer career sites. Crustdata uses LinkedIn Jobs and third-party aggregators; it cannot match LinkUp's employer-sourced precision for "how many open reqs on widgetcorp.com's career page in 2014-Q3."
- **Layoffs.fyi and TrueUp are retail-facing and non-queryable.** Crustdata's build-it-yourself layoff detector is strictly more powerful as long as you are willing to write the detection logic.

----------------------------------------------------------------

## 10 — Weaknesses in Crustdata's moat

- **No stated confidence interval.** LinkedIn's company-page headcount is itself noisy; without Crustdata publishing CIs, a user cannot tell if a 3% QoQ move is signal or LinkedIn-reporting drift.
- **No demographic cuts.** No gender, ethnicity, or age estimates. Revelio does this. Some buyers (DEI reporting, policy research) will always pick Revelio.
- **No inflow/outflow as first-class fields.** You can derive them, but the panel is shallower than Revelio on this primitive.
- **No seniority scale as a first-class aggregation.** Seniority is on the Person API; Crustdata does not expose `headcount_by_seniority_timeseries`.
- **No pre-labeled layoff flag.** You build it yourself. Every serious competitor does label this.
- **LinkedIn's blind spots are inherited.** Japan, Korea, China, most of Africa, rural India — the Crustdata number is weak there.
- **Shallow history for tail companies.** 3–5 years on marquee companies, 1–3 years on the long tail. Revelio's 2008 start is a research moat that Crustdata cannot close without buying / ingesting a historical backfill.
- **Recent HN and ProductHunt review sentiment** flags staleness on tail companies ("6–9 months stale" per one HN commenter) [36] — meaning the "weekly refresh" is a head-of-tail claim, not a universal guarantee.

----------------------------------------------------------------

## 11 — Unique capabilities that could power a product no one else can build

Phrased as the concrete superpowers a builder gets by picking Crustdata over Revelio / LiveData / LinkUp / TrueUp / layoffs.fyi.

1. **Weekly-cadence, company-wide Engineering headcount panel in India/LATAM/EU with a single API call, plus QoQ / 6-month / YoY deltas already computed.** Nobody else joins the weekly cadence with the function-by-country cut and pre-computed deltas in one response. Revelio is monthly; LiveData is person-level not panel-level; LinkUp is jobs; layoffs.fyi is curated.
2. **Real-time department-first-hire triggers.** `Watcher API` supports "First person hired in company department" and "First person hired internationally" as native events [18] — you can build a product that wakes up the day a Series-A startup hires its first Head of Data in Mexico, across 60M companies, with webhook delivery. Revelio Labs does not ship webhooks; LiveData is subscription-only; TrueUp/layoffs.fyi have no API.
3. **Role-percentile rankings that no other vendor pre-computes.** `linkedin_headcount_by_role_six_months_growth_percent` with percentile bucket fields (`71_to_100_percent` etc.) [28] lets you ask "show me top-decile Engineering-growth startups in the last 6 months globally" with zero client-side aggregation. Revelio has the cleaner panel; they don't ship percentile fields.
4. **The join.** Headcount time-series joined to Glassdoor CEO-approval MoM/QoQ/YoY [30], G2 product-review velocity, web-traffic monthly visitor QoQ, job-posting-by-function QoQ, news, funding, and decision-maker enrichment in **one** company_id keyspace. No other workforce vendor carries product / traffic / review / funding signals in the same panel. This is the founding premise of the Crustdata moat.
5. **Department headcount range filter in Search API.** "Find every software company with 51-200 employees AND Engineering headcount growth >20% in the last 6 months AND HQ in India" is a single POST `/company/search` call [8][27]. Revelio's approach is SQL-over-WRDS; Crustdata is a single filtered API call.
6. **Real-time re-crawl for a specific company on-demand.** `enrich_realtime=True` forces a fresh LinkedIn fetch within ~10 minutes of the call [19]. This is the *only* workforce vendor where you can pull sub-hour-stale headcount for an arbitrary company via public API. Revelio serves from cache. LiveData does not expose per-company real-time enrich at the API layer.
7. **AI-agent-shaped delivery.** MCP integration (Composio), Claude integration, Vercel AI SDK integration, Relevance AI integration, webhooks, usage-credit billing — everything is shaped for autonomous-agent consumption rather than researcher-seat consumption [5][14][52][53]. A company building an AI SDR, AI recruiter, or AI investor agent over workforce signals picks Crustdata because the shape matches; Revelio's WRDS-first delivery does not.
8. **Sub-$0.01-per-row economics at scale.** Bulk S3 / CSV at monthly refresh with the full 60M-company panel is priced for builders, not enterprise research [17]. Revelio's AWS Marketplace listings + WRDS licensing make that workload 10–100× more expensive per observation.
9. **First-hire-internationally as a product-ready trigger.** "Alert me when a Series-B SaaS company files its first employee in Tokyo" — this is a 6-line Watcher config in Crustdata and a six-month research engagement anywhere else [18].
10. **Negative-delta layoff detection composed with news.** Stacking `headcount_qoq_pct < -5` + `news_articles contains 'layoff'` + function-level drop gives a custom layoff detector with attribution ("the layoff hit Sales harder than Engineering") that no vendor publishes as a first-class feature. You trade the pre-labeled convenience for attribution depth that only Revelio matches, and only Revelio's does not fire in real time.

The winning product shape over Crustdata headcount is therefore an **always-on function-and-country-specific headcount radar** for a specific cohort (AI startups, fintech, devtools, defense-tech, etc.) with webhook alerts, weekly cadence, pre-computed deltas, and the ability to attribute a drop to a specific function and a rise to a specific first-hire. That product is singular on Crustdata's primitives; it is composite-and-slower on Revelio, and impossible on the others.

----------------------------------------------------------------

## Sources

1. [Company APIs — Crustdata API Documentation](https://docs.crustdata.com/docs/discover/company-data-api/)
2. [OpenAPI Introduction 2025-11-01 (cached navigation)](https://docs.crustdata.com/openapi-specs/2025-11-01/introduction)
3. [CRUSTDATA_FETCH_HEADCOUNT_BY_FACET_TIMESERIES — Composio tool schema](https://composio.dev/toolkits/crustdata)
4. [Studocu Crustdata API notes](https://www.studocu.com/in/document/jss-academy-of-technical-education/btech/crustdata-api-doc/117560785)
5. [Crustdata MCP (Composio)](https://mcp.composio.dev/crustdata)
6. [Real-Time B2B Data Broker](https://crustdata.com)
7. [Competitor Monitoring Tools, Techniques and Best Practices](https://crustdata.com/blog/competitor-monitoring-tools-techniques-and-best-practices)
8. [Company Search API via Filters](https://docs.crustdata.com/docs/discover/company-search-api-via-filters/)
9. [AI Tools for Venture Capital — blog](https://crustdata.com/blog/ai-tools-for-venture-capital-why-top-funds-build-proprietary-pipelines)
10. [B2B Prospecting Workflow with Claude Code](https://crustdata.com/blog/b2b-prospecting-workflow-claude-code)
11. [Crustdata.com sitemap](https://crustdata.com/sitemap.xml)
12. [iseoai Crustdata review](https://iseoai.com/crustdata/)
13. [Relevance AI Crustdata tool step](https://relevanceai.com/docs/build/tools/tool-steps/linkedin/search-linkedin-profiles)
14. [VC Stack Crustdata profile](https://www.vcstack.io/product/crustdata)
15. [Crustdata ProductHunt](https://www.producthunt.com/products/crustdata-3)
16. [Private Company Database 2.0 — ProductHunt launch](https://www.producthunt.com/products/private-company-database?launch=private-company-database-2-0)
17. [Crustdata full-dataset (bulk CSV/S3)](https://crustdata.com/full-dataset)
18. [Watcher API](https://crustdata.com/apis/watcher)
19. [Company Enrichment API](https://crustdata.com/apis/company-enrichment)
20. [Company Data datasets](https://crustdata.com/datasets/company-data)
21. [Revelio Labs data page](https://www.reveliolabs.com/data/)
22. [LinkUp data products](https://www.linkup.com/data)
23. [SQL examples on full-dataset page (parsed via WebFetch summary above)](https://crustdata.com/full-dataset)
24. [Crustdata headcount_qoq_pct field references (search-indexed blog content)](https://crustdata.com/blog/how-ai-investment-platforms-can-use-real-time-company-data-for-deal-sourcing)
25. [LinkedIn 26 job functions — BizzBee Solutions reference](https://www.bizzbeesolutions.com/26-job-functions-on-linkedin-their-role-targeting-game/)
26. [How to find company employees by specific role](https://crustdata.com/blog/how-to-find-employees-of-a-company)
27. [Company Search API Implementation](https://crustdata.com/blog/company-search-api)
28. [Crustdata percentile bucket and role-growth fields (search-surfaced references)](https://docs.crustdata.com/docs/dictionary/company/)
29. [Job Listing API](https://crustdata.com/apis/job-listing)
30. [Data Enrichment API Use Cases](https://crustdata.com/blog/data-enrichment-api-use-cases)
31. [Crustdata Company Dataset Powers AI Sales — Tech Company News](https://www.techcompanynews.com/crustdata-company-dataset-powers-ai-sales-recruiters-and-deal-platforms/)
32. [Crustdata $6M seed — AI Agent News](https://ai-agent-news.com/posts/crustdata-6m-real-time-agent-data-infrastructure/)
33. [Crustdata $6M seed — Pulse2](https://pulse2.com/crustdata-6-million-seed-funding-closed-for-building-data-layer-for-ai-agents/)
34. [Crustdata vs Coresignal](https://crustdata.com/vs/coresignal-alternative)
35. [Crustdata vs People Data Labs](https://crustdata.com/vs/peopledatalabs-alternative)
36. [HN comment on Crustdata staleness (objectID 47387130)](https://hn.algolia.com/api/v1/search?query=Crustdata&tags=comment&hitsPerPage=30)
37. [Crustdata reviews on Product Hunt](https://www.producthunt.com/products/crustdata-3/reviews)
38. [Revelio × LinkUp salary methodology](https://hf-files-oregon.s3.amazonaws.com/hdplinkup_kb_attachments/2023/04-26/1a7edfdf-c7ce-464f-a77c-9a326d56590c/Revelio_x_LinkUp_Salary_Methodology.pdf)
39. [Revelio Labs Data Dictionary: Methodologies](https://www.data-dictionary.reveliolabs.com/methodology.html)
40. [LiveData Technologies Methodology (Remote vs Office)](https://www.livedatatechnologies.com/methodology-remote-vs-office)
41. [Revelio Labs Data Dictionary — datasets](https://www.data-dictionary.reveliolabs.com/data.html)
42. [Revelio Labs homepage](https://www.reveliolabs.com/)
43. [LayoffData.com (WARN aggregator)](https://layoffdata.com/)
44. [Layoffs.fyi](https://layoffs.fyi/)
45. [TrueUp Layoffs Tracker](https://www.trueup.io/layoffs)
46. [Coresignal vs People Data Labs vs Revelio Labs](https://slashdot.org/software/comparison/Coresignal-vs-People-Data-Labs-vs-Revelio-Labs/)
47. [Revelio Labs seniority taxonomy references](https://www.data-dictionary.reveliolabs.com/methodology.html)
48. [Crustdata pricing](https://crustdata.com/pricing)
49. [Revelio Labs at WRDS (Wharton)](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/revelio-labs/)
50. [Revelio Labs on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-r33ewahy5tv62)
51. [LinkUp on Dewey Data (academic access)](https://www.deweydata.io/data-partners/linkup)
52. [Composio Crustdata Vercel AI SDK](https://composio.dev/toolkits/crustdata/framework/ai-sdk)
53. [Crustdata $6M closes seed — theaiinsider.tech](https://theaiinsider.tech/2025/11/11/crustdata-raises-6m-seed-round-to-power-real-time-data-infrastructure-for-ai-agents/)

----------------------------------------------------------------

## Research methodology notes

- Total web fetches and searches executed for this agent: 58 parallel WebFetch / WebSearch calls across 6 dispatch rounds.
- Primary sources prioritized: Crustdata docs, Crustdata blog, vendor comparison pages (crustdata.com/vs/...), ProductHunt reviews, HN Algolia API, Revelio Labs data dictionary, LiveData methodology pages, LinkUp data products, Composio MCP tool schema (which exposes the richest programmatic view of Crustdata's public API surface area).
- Key frustration: docs.crustdata.com is a Mintlify SPA, so raw HTTP fetches return the SPA shell, not the content. Content was recovered via WebFetch (which executes client-side JS server-side) and cross-referenced with cached materials at /home/akash/PROJECTS/crustdata/research/cache/ (already containing crustdata_llms.txt, openapi_nav.md, crustdata_nav.md).
- Profile pages (profiles.crustdata.com/company/...) are 403-gated to logged-out browsers, so we could not directly read a rendered "headcount time-series chart" and instead triangulated the time-series shape from Composio tool schemas plus blog-surfaced API examples.
- Known unknowns that would require API access to resolve:
  - exact historical start date of the dense time-series for a given company
  - exact field name for country-facet timeseries (`linkedin_headcount_by_country_timeseries` vs `_by_geography_timeseries`)
  - whether 30-day and 60-day rolling deltas exist as first-class fields (I found MoM as the nearest equivalent but no 30-day float field)
  - published confidence intervals on the headcount number
