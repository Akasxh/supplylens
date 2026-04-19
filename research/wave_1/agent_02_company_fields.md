# Agent 02 - Crustdata Company Fields: Catalog + Competitive Diff

**Scope:** Every field returned by Crustdata's `POST /company/search` and `POST /company/enrich` endpoints on the `2025-11-01` API version, tagged against Apollo (organization enrich + get-complete-organization-info), PDL (Company Schema), Clearbit (Company/Enrichment API), Harmonic (companies endpoint), ZoomInfo (Enrich Company), Cognism (Enrich/Redeem), and Tracxn.

**Primary sources (verified):**
- `docs.crustdata.com/company-docs/search` - 2025-11-01 Search spec, filter+response fields (extracted from RSC payload).
- `docs.crustdata.com/company-docs/enrichment` - 2025-11-01 Enrich spec, 17 field groups, example responses (`retool.com`, `serverobotics.com`).
- `docs.crustdata.com/company-docs/autocomplete` - supported field universe for autocomplete.
- `docs.crustdata.com/company-docs/identify` - resolver endpoint (returns the same `company_data` shape).
- `crustdata.com/apis/watcher` + `crustdata.com/webhook` - Watcher/webhook signal catalog.
- `docs.peopledatalabs.com/docs/company-schema` - full PDL schema including Company Insights premium.
- `docs.apollo.io/reference/organization-enrichment` + `get-complete-organization-info` (parsed from embedded example JSON - full 59-field org object + `departmental_head_count`).
- Clearbit types/payload references: `github.com/thoughtbot/clearbit/blob/master/types.go`, `help.clearbit.com/.../4419649060119`.
- Crustdata vendor comparison blog (`crustdata.com/blog/b2b-data-api-providers`), Composio MCP tool inventory, Clay integration page.

**Coverage limitations explicitly called out:**
1. Crustdata migrated docs in 2025-11. The legacy `/screener/company` endpoint exposed `linkedin_headcount_timeseries`, `linkedin_headcount_by_function_timeseries`, `funding_milestones_timeseries`, `web_traffic_timeseries`, `linkedin_follower_count_timeseries`, `glassdoor.*`, `g2.*` as directly returnable fields (confirmed via Composio MCP tool inventory and `docs.composio.dev/toolkits/crustdata` which still lists them: "Post Funding Milestone Timeseries Data", "Post Headcount Timeseries Data", "Post Web Traffic Data", "Fetch Headcount by Facet Timeseries", "Retrieve LinkedIn Posts"). **These are not in the 2025-11-01 `/company/enrich` response shape**, which rolls everything up to point-in-time aggregates (`headcount.total`, `roles.growth_6m`, `roles.growth_yoy`, `followers.yoy_percent`, `followers.six_months_growth_percent`, etc.). The full raw time-series endpoints still exist on `api.crustdata.com` but under separate routes (`/screener/company/*_timeseries`) not covered in the new quickstart. For this catalog I treat them as **Dataset-tier differentiated signals Crustdata keeps but no longer surfaces through the standard enrich envelope** - noted where relevant.
2. ZoomInfo and Cognism have auth-gated OpenAPI specs; I could not retrieve their exhaustive field lists. Comparison against them relies on vendor docs, review articles, and their marketing schema summaries.
3. WebFetch returned empty for several Crustdata Mintlify pages; I worked around by pulling the raw RSC payload via `curl` + Next.js `__next_f.push` parsing. The captured MDX text for `company-docs/search`, `/enrichment`, `/autocomplete`, `/identify` matches what renders in the browser.

---

## (A) Commodity fields - you can buy the same thing from 3+ competitors

These are fields where Crustdata ships at-parity with Apollo/PDL/Clearbit/ZoomInfo/Cognism. I'm listing them compactly - the moat isn't here.

### Identity & resolution (all providers have this)

| Crustdata path | Type | Desc / example | Also in |
|---|---|---|---|
| `crustdata_company_id` | integer | Internal Crustdata company ID (`633593` for Retool) | Apollo `id`, PDL `id`, Clearbit `id`, ZoomInfo `zi_id`, Cognism `id` |
| `basic_info.company_id` | integer | Upstream source company ID | all |
| `basic_info.name` | string | `"Retool"` | all |
| `basic_info.primary_domain` | string | `"retool.com"` | all |
| `basic_info.website` | string | Full URL `"https://retool.com/"` | all |
| `basic_info.professional_network_url` | string | LinkedIn company URL | all |
| `basic_info.professional_network_id` | string | LinkedIn company slug/ID | Apollo `linkedin_uid`, PDL `linkedin_id/slug`, Clearbit `linkedin.handle` |
| `basic_info.description` | string | `"Build internal software better with AI..."` | Apollo `short_description`/`seo_description`, PDL `summary`, Clearbit `description` |
| `social_profiles.twitter_url` | string | Twitter/X handle URL | Apollo `twitter_url`, PDL `twitter_url`, Clearbit `twitter.handle`, ZoomInfo |
| `basic_info.company_type` | string | `"Privately Held"` / `"Public Company"` | all (PDL `type`, Apollo `type`, Clearbit `type`) |
| `basic_info.year_founded` | string ISO date | `"2017-01-01"` | Apollo `founded_year` (int), PDL `founded` (int), Clearbit `foundedYear` |
| `basic_info.employee_count_range` | string | `"201-500"` | Apollo `estimated_num_employees` (int), PDL `size` (enum), Clearbit `metrics.employeesRange` |
| `basic_info.markets` | string[] | `["PRIVATE"]`, `["PRIVATE","NASDAQ"]` | Apollo `publicly_traded_exchange`, PDL `mic_exchange` + `type` |

### Industry / taxonomy (commodity)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `basic_info.industries` | string[] | `["Software Development","Technology, Information and Internet"]` | Apollo `industries`+`secondary_industries`, PDL `industry`/`industry_v2`/`naics`/`sic`, Clearbit `category.industry`/`subIndustry` |
| `taxonomy.professional_network_industry` | string | Primary LinkedIn industry label | Apollo `industry`, PDL `industry`, Clearbit `category.industry` |
| `taxonomy.categories` | string[] | LinkedIn specialities / category tags | Apollo `keywords`, PDL `tags`, Clearbit `tags` |
| `taxonomy.professional_network_specialities` | string[] | LinkedIn-sourced specialities | Apollo `keywords`, PDL `tags` |

### Location (commodity)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `locations.hq_country` | string ISO-3 | `"USA"`, `"GBR"` | all |
| `locations.hq_state` | string | `"California"` | all (Apollo `state`, PDL `location.region`) |
| `locations.hq_city` | string | `"San Francisco"` | all |
| `locations.headquarters` | string | Full formatted HQ string | Apollo `raw_address`, PDL `location.*`, Clearbit `geo.*` |
| `locations.largest_headcount_country` | string ISO-3 | Country with most employees | PDL `employee_count_by_country` (richer), Apollo/Clearbit don't expose |

### Funding (mostly commodity)

| Crustdata path | Type | Desc / example | Also in |
|---|---|---|---|
| `funding.total_investment_usd` | number | `141000000.0` (Retool) | Apollo `total_funding`, PDL `total_funding_raised`, Clearbit `metrics.raised`, Cognism, ZoomInfo |
| `funding.last_round_amount_usd` | number | Most recent round amount | Apollo `funding_events[last].amount`, PDL `funding_details[].funding_raised` |
| `funding.last_fundraise_date` | date | Last round close date | Apollo `latest_funding_round_date`, PDL `last_funding_date`, Clearbit |
| `funding.last_round_type` | string | `"series_a"`, `"series_b"` | Apollo `latest_funding_stage`, PDL `latest_funding_stage`, Clearbit |
| `funding.investors` | string[] | Investor names | Apollo `investors`, PDL `funding_details[].investing_companies`/`investing_individuals` (richer: IDs not names) |

### Revenue, market (commodity)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `revenue.estimated.lower_bound_usd` | integer | Estimated revenue lower bound | Apollo `annual_revenue` (point), PDL `inferred_revenue` (band string), Clearbit `metrics.annualRevenue`/`estimatedAnnualRevenue`, ZoomInfo `revenue` |
| `revenue.estimated.upper_bound_usd` | integer | Upper bound of revenue band | Apollo (single point, no band), PDL (band), Clearbit (band) |
| `revenue.public_markets` | string[] | Listed exchanges (e.g. `NASDAQ`) | Apollo `publicly_traded_exchange`, PDL `mic_exchange` |
| `revenue.acquisition_status` | string | `"acquired"` | Apollo `owned_by_organization_id`, PDL `all_subsidiaries`/parents |

### Social reach (commodity baseline - point-in-time)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `followers.count` | integer | LinkedIn follower count | PDL `linkedin_follower_count`, Harmonic, Clearbit doesn't, Apollo doesn't |
| `social_profiles.twitter_url` | string | Twitter handle | all |

### Employee reviews (commodity, and thin)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `employee_reviews.overall_rating` | number | Glassdoor-style overall rating | PDL doesn't expose in standard API, Apollo doesn't, Clearbit doesn't, ZoomInfo has it, Coresignal has it |
| `employee_reviews.culture_and_values_rating` | number | Culture rating | ZoomInfo, Coresignal |
| `employee_reviews.work_life_balance_rating` | number | WLB rating | ZoomInfo, Coresignal |
| `employee_reviews.review_count` | integer | Review count | ZoomInfo, Coresignal |

### Software reviews (commodity - G2 data is a common licensed feed)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `software_reviews.review_count` | integer | G2/Capterra review count | Enlyft, G2 direct, some Clay-integrated providers |
| `software_reviews.average_rating` | number | Avg software rating | Same |

### News (commodity - every vendor scrapes this)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `news.article_url` | string | Recent news URL | Apollo `news_url` (one), PDL news exists via Profile, ZoomInfo Scoops, Cognism |
| `news.article_title` | string | Article title | all |
| `news.article_publish_date` | date | Published date | all |

### Competitors (commodity - everyone has a competitor graph)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `competitors.company_ids` | integer[] | Linked Crustdata competitor IDs | PDL `affiliated_profiles` (looser), Apollo has `similar_companies` in app, Clearbit had `similar_domains` |
| `competitors.websites` | string[] | Competitor domains | Same |

### Metadata (commodity)

| Crustdata path | Type | Desc |
|---|---|---|
| `metadata.growth_calculation_date` | datetime | Anchor date that growth %s are calculated against |
| `status.state` | string | `"enriching"` / `"not_found"` - enrichment processing state |

### People inside the company (partially commodity)

| Crustdata path | Type | Desc | Also in |
|---|---|---|---|
| `people.decision_makers` | object[] | Key contacts at the company | Apollo: `get-complete-organization-info` returns a people block but only via Apollo's people DB; ZoomInfo has it; PDL has it via separate `person/search` |
| `people.founders` | object[] | Founder profiles | PDL via `person/search`, Harmonic, Tracxn (Tracxn specialises here) |
| `people.cxos` | object[] | C-level executive profiles | ZoomInfo, Cognism, Apollo (via people search) |

**Verdict on section A:** Every identity, firmographic, location, funding roll-up, and industry tag Crustdata exposes is also available from at least three of {Apollo, PDL, Clearbit, ZoomInfo, Cognism}. On sheer field count, Crustdata's basic-firmographic shape is *narrower* than PDL or Apollo's. The moat isn't in this table.

---

## (B) Differentiated fields - where Crustdata is unique or rare (one-line moat each)

### B1. Structural differentiators still inside `/company/enrich` (the surfaced API)

| Crustdata field | Type | Moat claim (one line) |
|---|---|---|
| `roles.distribution` | object `{role: count}` | **Point-in-time department headcount that's usable in `/search` as a filter** — Apollo has `departmental_head_count` in the complete-org endpoint but you can't filter on it; PDL's `employee_count_by_class`/`employee_count_by_role` is only in the Insights tier ($$$) and also not filterable. Crustdata exposes both reading it and filtering companies by it ("find SaaS companies with 100+ engineers"). |
| `roles.growth_6m` | object `{role: pct}` | **Six-month growth rate by department, filterable in search** — only PDL Premium `employee_growth_rate_12_month_by_role` is comparable, and PDL doesn't expose a 6-month window; Apollo/Clearbit/ZoomInfo have no equivalent. This is the "engineering team grew 30% in 6 months" signal that HarmonicAI charges for in its VC tier. |
| `roles.growth_yoy` | object `{role: pct}` | **Year-over-year growth by department** — roughly matches PDL `employee_growth_rate_12_month_by_role`; differentiated vs Apollo/Clearbit/ZoomInfo/Cognism which have zero department-level growth. |
| `hiring.openings_count` | integer | **Active job-opening count per company** — Apollo doesn't expose open reqs in enrich (you need their Jobs endpoint separately), Clearbit killed job posting enrichment, PDL has none. LinkUp and Revelio sell this as a standalone product; Crustdata ships it inside company enrich. |
| `hiring.openings_growth_percent` | number | **% change in active openings** — rare; HarmonicAI has it for startups, LinkUp has it licensed, Coresignal has it; Apollo/PDL/Clearbit/Cognism/ZoomInfo do not. A real hiring-velocity signal. |
| `hiring.recent_titles_csv` | string | **Comma-separated recent job titles being hired** — unique packaging. Tells you what roles they're opening right now (e.g. "Senior ML Engineer, Data Platform Lead"), used for ICP lookalike + "who do they think they are today" signal. |
| `followers.mom_percent` | number | **Month-over-month LinkedIn follower growth** — PDL has linkedin_follower_count (point); nobody in the commodity stack has the month-over-month delta. |
| `followers.qoq_percent` | number | **Quarter-over-quarter follower growth** — same gap. |
| `followers.six_months_growth_percent` | number | **Six-month follower growth** — same gap. Follower velocity is a real "brand momentum" proxy and Crustdata is one of ~3 vendors (also Harmonic, Coresignal) that ships it in an API. |
| `followers.yoy_percent` | number | **Year-over-year follower growth** — same. |
| `seo.total_organic_results` | integer | **Number of organic ranking keywords (Ahrefs/Semrush-style)** — bundled inside a B2B enrich API is rare. Similarweb/Ahrefs sell this for $499+/mo; Apollo/PDL/Clearbit/ZoomInfo/Cognism do NOT include it. |
| `seo.monthly_organic_clicks` | integer | **Estimated monthly organic clicks** — same gap. This is Ahrefs-tier SEO intel bundled into firmographic enrichment. |
| `seo.monthly_google_ads_budget` | integer | **Estimated monthly Google Ads spend** — very rare. Semrush/Similarweb have this gated behind separate products; no general B2B data vendor ships it in standard enrich except Crustdata. Lets you identify "high-spend growth-mode SaaS" as a filter. |
| `web_traffic.monthly_visitors` | integer | **Monthly website visitor count** — Clearbit (metrics.alexaGlobalRank is its weak version), PDL doesn't have it, Apollo has `alexa_ranking` (rank, not visitors); Similarweb-grade traffic is rare. |
| `web_traffic.domain_traffic` | object | Traffic by source / channel breakdown — **source breakdown (search/direct/referral/social)** is Similarweb-tier and not exposed by Apollo/PDL/Clearbit/ZoomInfo/Cognism. |
| `funding.tracxn_investors` | string[] | **Investor names normalized from Tracxn's private-market taxonomy, filterable for `company/search`** — nobody else cross-licenses Tracxn and exposes it as an investor filter. This is literally "find companies backed by Sequoia or a16z" at low latency. |
| `basic_info.markets` | string[] | Market tags like `["PRIVATE","NASDAQ"]` — the dual public/private tagging is more granular than Apollo's boolean public flag. Minor. |

### B2. Dataset-tier differentiated signals Crustdata maintains but doesn't surface through `/company/enrich` (still sold; reached via `/screener/company/*` legacy + bulk datasets + MCP tools)

These were in the old `/screener/company` API and remain in Crustdata's MCP tool catalog (Composio still lists them) and their bulk-dataset product. They don't appear in the new enrich envelope but the underlying data is still Crustdata's IP. I'm listing them because the moat question isn't "what's in the JSON" but "what can you buy from them":

| Signal (legacy/dataset field) | Moat claim |
|---|---|
| `linkedin_headcount_timeseries` (monthly point per company) | **Full monthly headcount history, per company, going back years** — only Revelio Labs, Live Data Technologies, and Coresignal also sell this. NOT in PDL standard, NOT in Apollo, NOT in Clearbit, NOT in ZoomInfo standard enrich. Crustdata prices this in their API-feed tier at a small fraction of Revelio's ($100k+/yr). |
| `linkedin_headcount_by_function_timeseries` | **Department-level headcount over time, per company** — the same gap. Matches PDL's Insights Premium `employee_count_by_month_by_role` but Crustdata prices it lower and ships it both as a sync feed and as filterable bulk. |
| `linkedin_headcount_by_geography_timeseries` | **Country-level headcount over time** — same rarity as above; tells you international expansion exactly. Matches PDL's Premium `employee_growth_rate_12_month_by_country`, but Crustdata actually ships the timeseries, not just the growth rate. |
| `funding_milestones_timeseries` | **Funding-event timeseries per company** (round-by-round amounts) — Crunchbase Enterprise sells this; Apollo has `funding_events` array (close equivalent); PDL has `funding_details` array (equivalent). Roughly commodity vs Crunchbase+PDL, differentiated vs Clearbit/ZoomInfo/Cognism. |
| `web_traffic_timeseries` | **Monthly web traffic history** — Similarweb's own product. Apollo has a point-in-time `alexa_ranking`; PDL/Clearbit/ZoomInfo/Cognism nothing. Crustdata normalising this in a B2B-data API is rare. |
| `linkedin_follower_count_timeseries` | **Follower count over time** — Harmonic has this, Coresignal has this; nobody else in the commodity stack does. |
| `linkedin_posts` (company + executive posts) | **Posts-as-a-feed from company and exec LinkedIn pages** — this is Crustdata's most-cited moat. Apollo/PDL/Clearbit don't ship LinkedIn posts as an endpoint at all. The `Retrieve LinkedIn Posts` and `Search LinkedIn Posts by Keyword` tools are live in the Composio integration. Closest competitor is Phantombuster and they require you to run scrapers yourself. |
| Job-listings table (per-company job feed) | **Full open-reqs per company including geo, seniority, and function** — Apollo doesn't have it, Clearbit killed it, PDL none. Competes with LinkUp, Revelio, and Aura (all enterprise-priced). |
| Form D filings (company.sec_filings) | **SEC Form D (Regulation D private offering) filings linked by company** — a niche but real moat. Crustdata is one of the few B2B APIs that enriches this. Public data, but ETL cost is real, and it's how you find companies that quietly raised but didn't PR it. |
| Advertising footprint (`total_ads_count`, `active_ads_count`, `ad_platforms`) | **Ad-platform activity per company (Meta, Google, LinkedIn ads count and platforms)** — mentioned in `crustdata.com/apis/company-discovery`. Very rare: SensorTower and Facebook Ad Library are the substitutes. PDL/Apollo/Clearbit/ZoomInfo/Cognism do not ship this. |
| Product Hunt launches per company | **Per-company Product Hunt launch tracking** — zero commodity parity. |
| Employee-skill distribution per company (`find companies whose employees list Python / AWS / Rust`) | **Skill-graph across company's workforce** — a feature of the search filter layer (`Employee skills` filter). LinkedIn Talent Insights has it (gated hard), Revelio Labs has it, PDL has it rolled into the separate person index but not as a company filter. Crustdata ships it as a company search filter. |

### B3. Event/real-time differentiators (the Watcher + Webhook moat)

This is where Crustdata actually pulls away. No other vendor in the commodity stack ships these as first-party products.

| Signal | Moat claim |
|---|---|
| Fundraise watcher — webhook fires when company raises a new round | **Event-as-a-service on funding, with filters by stage, geo, amount.** Apollo/PDL/Clearbit/ZoomInfo/Cognism do NOT expose webhooks for funding events. Clay does, but Clay is an aggregator layering on top of Crustdata + Harmonic + others. |
| Headcount-growth watcher — webhook on headcount-jumped-by-X%-in-Y-months | **Company-growth-event webhooks.** This is literally the Watcher API's flagship use case. No competitor offers it natively in the commodity stack. Harmonic has momentum alerts but only in their app UI, not webhookable at the same price point. |
| Department-first-hire watcher — "company hired first person in X department" | **First-hire-in-department signal** — e.g. "first Head of RevOps", "first Data Engineer". Extremely specific to Crustdata. Zero commodity parity. |
| International-expansion watcher — "first employee hired in country Y" | **First-employee-in-new-country signal.** Unique. Used for go-to-market trigger detection ("company just opened their first EMEA hire → time for our EMEA rep to call"). |
| Department-headcount-range watcher | **"Alert me when company's eng team crosses 50"** — unique; there's nothing like this in the commodity stack. |
| Job-posting watcher — keyword filter on new reqs | **"Company just posted a job with 'Kubernetes'"** — LinkUp and Ashby have job-feed APIs but no commodity enricher has this as a webhook event. |
| New-in-news watcher | **Company mentioned in news (filterable by keyword)** — ZoomInfo "Scoops" is the closest analog but Scoops is editorial curated, not keyword-filtered webhook. |
| LinkedIn post watcher on company page | **Real-time company LinkedIn posts as events** — no commodity competitor has this. |

### B4. What Crustdata DOESN'T have that competitors do (honest diff)

For the judgment to be fair, note the fields Crustdata is *missing* relative to PDL/Apollo:

- No `employee_count_by_country` dict (PDL has it; Crustdata has only `largest_headcount_country`).
- No `employee_tenure` / `average_employee_tenure` / `median_tenure_by_role` (PDL Insights has full tenure distributions).
- No `employee_churn_rate` / `employee_turnover_rate` as a standalone enrich field (PDL Insights has 3m/12m churn + turnover - Crustdata only has `roles.growth_*` which is net, not gross).
- No `recent_exec_departures` / `recent_exec_hires` as a structured array (PDL Insights has it; Crustdata exposes it as a Watcher event but not as a queryable array on enrich).
- No `top_previous_employers` / `top_next_employers` (PDL Insights exclusive - tells you the talent flow graph).
- No `gross_additions_by_month` / `gross_departures_by_month` (PDL Insights exclusive).
- No NAICS/SIC code tree structure (PDL has the 2/3/4/6-digit rollup; Apollo has `industry_tag_id`; Crustdata's `taxonomy.categories` is flatter).
- No intent data (6sense/Bombora/ZoomInfo Intent territory; Crustdata has **hiring-signal intent but not buying-intent from third-party signal networks**).
- No verified phone numbers / mobile dials for exec (Cognism and ZoomInfo's core moat).
- No technographics at field-level (**this is a real hole - 2025-11-01 enrich doesn't return a `tech_stack` field**; Apollo has `technology_names` + `current_technologies`, PDL premium can ship it, Clearbit had `tech` array, BuiltWith and Wappalyzer sell the underlying data). Crustdata markets "technographics" as a data category but it isn't exposed in the surfaced enrich response; it's only in the Discovery filter layer ("Employee skills" filter, which is a weak proxy).
- No on-chain / crypto / wallet data (none of the surveyed vendors have it; your prompt asked me to flag it - Crustdata does not have it either; Messari, Nansen, and Dune sell this separately).

---

## (C) Bottom-line verdict: what companies data does Crustdata have that competitors don't?

Crustdata's company-data moat is **not in the static firmographic envelope** - on that axis PDL wins (more fields, better tenure/churn math) and Apollo wins (more integrated with outbound tooling). The surfaced `/company/enrich` response is actually narrower than PDL's premium schema and barely at parity with Apollo's enrichment.

**The real Crustdata moat is a three-part bet, and the data proves it:**

1. **Time-derived growth metrics on a per-department, per-location, per-follower basis, usable as *search filters*, not just as read-only fields.** `roles.growth_6m`, `roles.growth_yoy`, `followers.mom_percent` through `followers.yoy_percent`, and `hiring.openings_growth_percent` are all filterable via `POST /company/search`. This means you can compose a single query like *"US-based SaaS companies whose engineering headcount grew >20% YoY AND whose LinkedIn followers grew >30% MoM AND whose open-req count is up >50%"* in one HTTP call. Apollo can't do this (no growth by department). PDL can but only by dropping to the Insights tier and then you can't filter - you have to fetch the object and post-process. Harmonic can but its filter surface is narrower and the API is priced for VCs, not SDR teams. **This composable-growth-filter surface is a real, defensible API-shaped moat.**

2. **SEO/SEM and web-traffic signals (`seo.monthly_organic_clicks`, `seo.monthly_google_ads_budget`, `web_traffic.monthly_visitors`, `web_traffic.domain_traffic`) bundled inside the *same* enrich call that returns firmographics.** Apollo/PDL/Clearbit/ZoomInfo/Cognism either don't have these at all or make you subscribe to a separate product (Semrush/Ahrefs/Similarweb cost $300-$1000/mo each). For an AI SDR or GTM agent trying to qualify an inbound lead in one API call, this is a meaningful consolidation advantage.

3. **Watcher / webhook event catalog with filters that competitors simply don't have as products.** Fundraise + headcount-jump + first-hire-in-department + international-expansion + job-posting-with-keyword + LinkedIn-post are all exposed as webhook subscriptions. The closest analog is Clay's automation layer, but Clay is a customer/reseller of Crustdata + Harmonic. None of Apollo/PDL/Clearbit/ZoomInfo/Cognism ship an event stream for these company-level signals at the commodity tier.

**What this means operationally:**

- If a buyer just needs "enrich a domain and give me firmographics + a revenue band": **Crustdata is not differentiated**. Pick cheapest-reliable (PDL or Apollo).
- If a buyer needs "find companies whose engineering department grew by X% in the last six months that also doubled SEO traffic": **Crustdata wins uniquely**, because the same query in PDL requires two products (Insights + some other SEO feed) and in Apollo is impossible.
- If a buyer needs "tell me the moment any of my 500 target accounts raises a round OR hires its first Head of Data": **Crustdata wins uniquely** via the Watcher API; no commodity vendor ships this webhook surface.
- If a buyer needs "LinkedIn posts from the CEO of every SaaS company with >500 employees, for an AI SDR to personalize off": **Crustdata wins uniquely** via the `Retrieve LinkedIn Posts` and `Search LinkedIn Posts by Keyword` tools; Apollo/PDL/Clearbit do not ship this as an API at all.

**Weaknesses to be honest about:**
- No verified phone numbers at scale → Cognism/ZoomInfo beat them for outbound-calling use cases.
- No third-party buying-intent data (Bombora/6sense) → ZoomInfo beats them for intent-based ABM.
- No technographics surfaced in the 2025-11-01 enrich envelope (only weak proxy via employee-skills filter) → BuiltWith/Wappalyzer/ZoomInfo TechStack beat them for technographic targeting.
- No on-chain/crypto data at all (none of the commodity vendors have it; your prompt flagged this specifically, and Crustdata is not the answer here - Messari/Nansen/Dune are).
- Coverage width of the surfaced `/enrich` response is narrower than PDL's premium schema (PDL ships 60+ Insights fields that Crustdata either doesn't expose or rolls into a single aggregate).

**One-line verdict:** Crustdata's company moat is *time-and-department-granular growth signals, bundled SEO+traffic, and a webhook/watcher event layer that turns enrichment into a subscription-to-change-events*. They're not cheaper-PDL and they're not Apollo-with-better-reach; they're the vendor you pick when your GTM or AI-agent workflow is triggered by *change*, not by *state*. Everyone else is shipping state.

---

## Appendix: Raw field-group summary (Crustdata 2025-11-01 enrich response)

From `POST /company/enrich` the `company_data` object contains exactly these 17 field groups (per the published reference table on docs.crustdata.com/company-docs/enrichment):

| Group | Fields |
|---|---|
| `basic_info` | `name`, `primary_domain`, `website`, `professional_network_url`, `professional_network_id`, `company_id`, `year_founded`, `description`, `company_type`, `employee_count_range`, `industries`, `markets` |
| `headcount` | `total`, `by_role_absolute`, `by_role_percent`, `by_region_absolute`, `growth_percent` |
| `funding` | `total_investment_usd`, `last_round_amount_usd`, `last_fundraise_date`, `last_round_type`, `investors`, `tracxn_investors` |
| `locations` | `hq_country`, `hq_state`, `hq_city`, `headquarters`, `largest_headcount_country` |
| `taxonomy` | `categories`, `professional_network_industry`, `professional_network_specialities` |
| `revenue` | `estimated.lower_bound_usd`, `estimated.upper_bound_usd`, `public_markets`, `acquisition_status` |
| `hiring` | `openings_count`, `openings_growth_percent`, `recent_titles_csv` |
| `followers` | `count`, `mom_percent`, `qoq_percent`, `six_months_growth_percent`, `yoy_percent` |
| `seo` | `total_organic_results`, `monthly_organic_clicks`, `monthly_google_ads_budget` |
| `competitors` | `company_ids`, `websites` |
| `social_profiles` | `twitter_url` (others nested as available) |
| `web_traffic` | `domain_traffic`, `monthly_visitors` |
| `employee_reviews` | `overall_rating`, `culture_and_values_rating`, `work_life_balance_rating`, `review_count` |
| `people` | `decision_makers[]`, `founders[]`, `cxos[]` |
| `news` | `article_url`, `article_title`, `article_publish_date` |
| `software_reviews` | `review_count`, `average_rating` |
| `status` | `state` (`enriching` / `not_found`) |
| `roles` | `distribution`, `growth_6m`, `growth_yoy` (exposed on `/company/search` as filterable fields even though they also come back via `headcount.by_role_*`) |

Request-side controls:
- `domains: string[]`, `names: string[]`, `crustdata_company_ids: integer[]`, `professional_network_profile_urls: string[]` (exactly one per request)
- `fields: string[]` — dot-path subset to reduce payload
- `exact_match: boolean` — strict domain match
- `x-api-version: 2025-11-01` header

Response envelope: `[{ matched_on, match_type, matches: [{ confidence_score, company_data }] }]` — no match returns `200 OK` with `matches: []`; `404` only for malformed domain input.

**Pricing signal:** Enrich is **2 credits/record**; Search is **0.03 credits per result returned** — suggesting the heavy cost is on the enrichment rollup and the search-filter layer is designed to be the cheap-scan entry point. This is consistent with their "use search to find targets, then enrich what you care about" pattern in the docs.
