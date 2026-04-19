# Agent 05 — Crustdata News & Signals Endpoints: Deep Dive

**Date:** 2026-04-19
**Scope:** Characterize Crustdata's news/signals surface (Watcher API + webhook plumbing + social posts + web search) with direct reference to the 2025-11-01 OpenAPI spec, the Watcher and Webhook marketing pages, the Composio/Merge/Clay MCP tool exposures, and blog+Product Hunt+HN commentary. Benchmark against PredictLeads (29 canonical event types, the closest structured-event competitor), Owler/Meltwater (16 event types, news-centric), Bloomberg Event-Driven Feeds (corporate calendar), Signal AI (news-as-a-service), and LinkedIn Alerts (consumer-grade).

---

## TL;DR (the uncomfortable truth)

**Crustdata does not have a "news events" endpoint in the way PredictLeads does.** There is no `/news/search`, no `/events/search`, no canonical `event_type` enum with 29 values, no structured per-event object with category + normalized location + normalized investment amount + sentence + body. That dataset simply does not exist on docs.crustdata.com.

What Crustdata does have is a **trigger-subscription system called the Watcher API** — you pre-declare conditions ("this company's headcount went up 20%", "someone with keyword SDR posted something", "Company X raised a round"), Crustdata pushes a webhook when the condition fires, and you then pull the enriched entity record. It's event-driven infrastructure, not an event corpus. You cannot ask "give me every product-launch event across the tech sector last month" and get 5,000 rows back the way you can from PredictLeads. You can only ask "tell me when company X fires event Y".

The actual "events" Crustdata can surface at scale are: **job postings, funding rounds, LinkedIn posts matching a keyword, company headcount growth by department, new-country hiring, and individual job changes**. Six trigger primitives, not 29 event types. Everything else — product launches, awards, press mentions, certifications, legal actions, IPO filings, M&A — is either (a) recovered opportunistically through the `/web/search/live` web search endpoint using an LLM agent to classify retrieved documents, or (b) not covered at all.

**Where Crustdata wins vs PredictLeads:** fresher data (live crawl at request time vs PredictLeads' batch+ML pipeline, which incurs classifier-processing latency), tighter LinkedIn integration (LinkedIn posts as a first-class watch trigger), people-level watches (someone-starts-new-job — PredictLeads is company-centric), and a push-first architecture. Where PredictLeads wins: event taxonomy breadth (29 typed categories vs 6 trigger primitives), structured location + investment-amount normalization, historical depth back to 2016 (vs Crustdata's 14-28-day refresh cycle for historical snapshots), 20M+ media sources vs Crustdata's LinkedIn+SEC+press-release bias, 195 countries with native-language NER in 5 languages, and a queryable event corpus with ~50k new events/week you can bulk-query for backtests.

**Where the product angle lives:** not competing on event taxonomy (lose to PredictLeads) or on corpus depth (lose to Bloomberg/Signal AI) but on **the LinkedIn-post-as-buying-signal axis that PredictLeads cannot touch**, combined with Crustdata's people-level watches and webhook push model. That's where a Crustdata-native product has a moat the incumbents structurally cannot close. Details at the end of this doc.

---

## 1. Event taxonomy — every event type Crustdata can surface

### 1.1 The six canonical watch primitives

Source: `crustdata.com/apis/watcher`, `crustdata.com/webhook`, and the Composio MCP exposure of `create_watch` / `update_watch` / `get_watch` / `list_watches`. The Watcher API bucketizes into **3 watcher types** containing **6 trigger primitives** total:

**Event Watchers (3 primitives)**
1. `job_posting_with_keyword_and_location` — fires when a job posting containing specified keywords appears in specified locations. Parameters: keyword list, location list.
2. `new_funding_announcement` — fires when Crustdata ingests a funding event (round close or announcement) for a watched company. Parameters: company set.
3. `linkedin_post_with_keywords` — fires when a LinkedIn post (from company page or a tracked person's profile) contains specified keywords. Parameters: keyword list, poster-scope (company/person set).

**Company Watchers (4 sub-primitives, all variations of headcount delta)**
4a. `company_headcount_increased_by_pct` — fires when a company's total headcount grows by N% over a baseline period. Parameters: company, %, lookback window.
4b. `department_headcount_range` — fires when a department's headcount enters a specified range. Parameters: company, department (from LinkedIn's 20-function taxonomy), min, max.
4c. `first_person_hired_in_company_department` — fires when a company hires its first person in a department (useful for "first AE in EMEA", "first CFO hired"). Parameters: company, department.
4d. `international_hiring_expansion` — fires when a company starts hiring in a new country. Parameters: company, country.

**People Watchers (1 primitive)**
5. `person_starts_new_job` — fires when a tracked person's current role changes (start date transitions on LinkedIn). Parameters: person set (LinkedIn URLs).

A 6th trigger primitive mentioned on the webhook page but not broken out as a separate watcher — `company_multi_country_employee_locations` — counts as a sub-variant of 4d.

That's the taxonomy. Six primitives. Compare to PredictLeads' 29 typed event categories or Owler's 16.

### 1.2 What's missing from the taxonomy (the negative space matters)

The prompt asked for funding, hires, layoffs, leadership changes, product launches, office openings, awards, press mentions, partnerships, certifications, legal actions, IPO filings, M&A. Mapping:

| Event class | Crustdata native? | How it's surfaced (if at all) |
|---|---|---|
| **Funding announcement** | Yes | `new_funding_announcement` Watcher; ingested into `funding.*` sub-object on `/company/enrich` |
| **Individual hires (non-exec)** | Yes | `person_starts_new_job` Watcher; headcount-by-department delta |
| **Exec hires / C-level changes** | Partial | Same `person_starts_new_job` primitive — works if you pre-declare the person, doesn't surface organically. No typed `leadership_change` event. |
| **Layoffs** | Indirect only | No `layoff` event type. Detectable only as negative headcount delta via `company_headcount_increased_by_pct` with negative threshold (if supported — docs don't explicitly confirm). No press-release layoff detector. Layoffs.fyi integration is not documented. |
| **Product launches** | Not native | Not a watcher primitive. Must be recovered via `linkedin_post_with_keywords` with launch-y keywords ("launched", "introducing", "announcing"), or via `/web/search/live` followed by LLM classification. |
| **Office openings** | Partial | `international_hiring_expansion` catches geographic expansion but not office lease signings, ribbon-cuttings, or WeWork footprint. No press-release office-opening detector. |
| **Awards & recognition** | Not native | No watcher primitive. Only recoverable through `linkedin_post_with_keywords` ("award", "winner", "recognized") or web search. |
| **Press mentions** | Not native | Crustdata's own marketing mentions "press mentions" under company-data datapoints (enrichment side), but there is no "this company got mentioned in TechCrunch yesterday" watcher. |
| **Partnerships** | Not native | Same story — no typed partnership event, recoverable only through keyword-triggered LinkedIn-post watches or web-search classification. |
| **Certifications** (SOC2, ISO, HIPAA, etc.) | Not covered | No structured certification tracker. No logo-detection on trust pages. Would have to be done via `/web/enrich/live` on `/trust` URLs. |
| **Legal actions** (lawsuits, regulatory fines) | Not covered | No SEC 8-K classifier, no PACER integration, no FTC/SEC enforcement ingestion documented. |
| **IPO filings / S-1** | Not covered structurally | Crustdata ingests "SEC filings" at a high level per marketing, but no `s1_filed` event type, no 13-F extraction, no Form D as a typed event (despite the `/blog/data-enrichment-api` pages mentioning Form D in the source list). |
| **M&A** | Not covered | No `acquired_by` / `acquired` / `merged_with` event types. No M&A-announcement watcher. Acquisition data on the enrichment side exists only as a free-text field on `company_data.exit_info` if the company has been acquired. Not a searchable event stream. |
| **Social posts (as events)** | Yes, limited | `linkedin_post_with_keywords` only. No Twitter/X watcher, no Reddit watcher, no Mastodon/Bluesky, no podcast or YouTube mention watcher. Twitter was in the marketing language for the Social Posts API but the API docs + MCP exposure only list LinkedIn. |

Net count of distinct trackable event classes in the Crustdata native taxonomy: **6 primitives covering ~4 underlying event classes** (funding, hiring/headcount, job-change, keyword-matched posts). Everything else requires (a) keyword-matching a LinkedIn post, which is lossy, or (b) running a web-search agent per target company, which defeats the push-architecture advantage.

### 1.3 The "Social Posts API" and "Web Search API" as event-recovery mechanisms

Crustdata has two additional endpoints that can *recover* events outside the watcher taxonomy but do not count as structured event streams:

- **`/company/linkedin_posts`** and **`search_linkedin_posts_by_keyword`** (the MCP tool names): pull LinkedIn posts from company pages or search across posts by keyword. Useful for classifying posts into event types **post-hoc** with an LLM. Not structured as events — they are structured as posts with `text`, `hyperlinks`, `total_likes`, `total_comments`, `total_shares`, `poster_name`, `poster_title`, and `posted_at`. You have to run classification yourself.
- **`/web/search/live`**: the Web Search API announced as the Feb-2026 Show HN, returning 6 deduplicated web documents in ~1,200 tokens instead of 4,000. Crustdata's value add here is entity-resolution: every returned document is linked to a canonical company/person ID. So you can run a query like "funding round Company X" and get documents already tagged to the right entity. Still not structured as typed events; you have to run extraction.

Both of these are **agent-ready primitives** — designed to be consumed by LLM agents that will classify and structure on the receiving side. That's the deliberate architectural bet: don't try to match PredictLeads' 29-category ML classifier; instead, give agents clean, entity-linked primitives and let Claude/GPT do classification at query time.

---

## 2. Latency from real-world event to API availability

This is where claims and evidence diverge sharply. Pulling the numbers apart:

### 2.1 Stated latency claims (marketing language)

- **Watcher webhooks:** "real-time", "realtime updates", "instant", "the moment a change is detected", "within hours of the change", "within minutes of a trigger". No SLA number.
- **Live enrichment (request-time crawl for `/web/search/live` and `/web/enrich/live`):** "Live crawling takes seconds rather than milliseconds" (their `/blog/real-time-vs-batch-data-enrichment` post). "This entire process can be completed in seconds (sub-1s for cached enrichments with Crustdata)." The published People Enrichment latency is "under 10 seconds per profile" (live crawl path) vs "up to 30 seconds per profile" (database-enrichment path). These are endpoint-response latencies, not event-detection latencies.
- **Historical snapshot refresh:** "Refreshing datasets every 14–28 days, with ongoing improvements to reduce this cycle" (from the `/about` page). This is the cadence at which Crustdata re-scrapes the underlying LinkedIn/web data into their snapshot tables. So a headcount number you query today is somewhere between 0 and 28 days stale.
- **Untracked company discovery:** "profiles discoverable within minutes" (from `/blog/b2b-data-api-providers`).

### 2.2 Measured latency evidence (what I could actually find)

No changelog-backed latency numbers. Crustdata does not publish a public changelog with per-release latency metrics. The closest:

- **HN, 2026-03-15, user ptrtht** (item 47387130, a comment on a Companies.social thread): *"the per-lookup cost adds up fast, and the data is often 6–9 months stale"* — explicitly about Crustdata and IcyPeas. 6–9 months is wildly inconsistent with the 14–28 day marketing claim and suggests the criticism was about a specific field (probably job title / employment-status stale because LinkedIn is the upstream and LinkedIn lags self-reports). No other signed HN-commenter gave a number.
- **Product Hunt review, Chen, 6mo ago:** *"I'd be curious about latency and how clean the API is; nothing kills a dev's vibe faster than messy endpoints."* Reviewer has not measured it.
- **Product Hunt review, Deepika, 6mo ago:** *"Curious how clean their enrichment actually is in practice though."* Same pattern — unverified.
- **The 13 Product Hunt reviews in aggregate** rate Crustdata 4.4/5. Every positive review mentions "real-time", none cite a measured latency. This is a yellow flag: happy users are not reporting measurements, they are reporting vibes.

Net: there is **no published latency SLA** for real-event-to-webhook-delivery. The marketing range is "minutes to hours after the change" (for the webhook tier) and "14–28 days for snapshot freshness" (for the bulk-enrichment tier). The one piece of negative HN signal says "6–9 months stale" on at least some fields. Treat Crustdata's latency claims as unverified in 2026-04.

### 2.3 Latency comparison against PredictLeads, Owler, Bloomberg

- **PredictLeads:** Not explicitly published either, but their architecture (ingest from 20M+ media sources → supervised ML classifier → entity resolution → dedup) has fundamental pipeline latency that Crustdata's live-crawl doesn't have. PredictLeads does "approximately 50,000 categorized events added each week" = ~7,000/day = ~1 event every ~12 seconds globally. For any specific company the typical lag from press-release publication to event availability is **hours to a day** (common ML-pipeline delay). Their webhook product notifies on newly-categorized events so the webhook fires close to ingestion time.
- **Owler (Meltwater):** Per their Owler Pro page, "precisely matches over 180,000 news events each week" which is ~3.6x PredictLeads' throughput, but the coverage is news-driven. Instant Insight emails on 15 trigger events go out to users daily; not a sub-minute push.
- **Bloomberg Event-Driven Feeds:** The gold standard. Real-time from Bloomberg's 151 bureaus (10,000+ headlines/day) + 48k+ companies in 100+ countries on the Corporate Events Calendar. Sub-second for market-moving headlines. Crustdata and PredictLeads are both 3-4 orders of magnitude slower and miles less comprehensive for finance-grade events.

**Conclusion on latency:** Crustdata's Watcher is **architecturally the right shape** (push vs poll, live crawl vs batch) but has no published SLA and lacks the bureau/news-wire upstream that Bloomberg/Signal AI have. For high-signal tech-sales triggers (a VP of Sales changed jobs, a company opened a roles in EMEA) Crustdata's minute-to-hour window is good enough. For financial-grade event detection it's nowhere close.

---

## 3. Source diversity — what feeds the events

Sources Crustdata publicly claims (aggregated from `/datasets/company-data`, `/apis/watcher`, `/blog/b2b-data-api-providers`, and the LinkedIn-post launch announcement):

- **LinkedIn** — company pages, person profiles, LinkedIn posts. **The dominant upstream** for Crustdata; everything headcount-derived and person-derived flows from here.
- **SEC filings** — cited at a marketing level ("SEC filings" and "Form D filings" appear in source lists). No specific filing-type endpoints are documented. 10-K / 10-Q / 8-K / S-1 / 13-F are not structured as queryable event types in the API.
- **Funding announcements** — from press releases + Crunchbase-style aggregator scraping + LinkedIn funding posts. Not from a direct feed partnership with VCs/LPs.
- **Employee ratings** — Glassdoor / Comparably-style review data; feeds company-level CEO approval rating but not events.
- **Product reviews** — G2 review counts and review deltas.
- **Web traffic analytics** — probably SimilarWeb or equivalent; not an event source but fuels headcount-growth-proxy watchers.
- **App Store / Play Store reviews** — mentioned on `/docs/intro`, not surfaced as watcher events.
- **Press mentions** — mentioned as a datapoint on the company enrichment page. Not a typed event.
- **Company website crawling** — careers pages, about pages, news/blog pages (this is what `/web/enrich/live` feeds).
- **Job postings** — Crustdata crawls major job boards + company career pages. Feeds the job-posting watcher.
- **Product Hunt launches** — listed in company enrichment ("Product Hunt launches" datapoint).

**What's not in the source list:**
- **Twitter/X** — despite being the #1 venue for tech announcements, not documented as a Crustdata source for events. The Social Posts API copy says "social media posts" generically but the MCP tools only list LinkedIn.
- **Reddit** — not a source. Material gap for product-signal detection (r/startups, r/SaaS, r/devops carry a lot of launch signal).
- **YouTube** — not a source. No transcript extraction, no channel watching, no podcast integration.
- **Podcasts** — not a source. A huge missed signal for exec-level discussions and announcements.
- **Substack/newsletters** — not a source. No tracking of "CEO started a Substack and wrote about their growth".
- **GitHub** — not a Crustdata source. PredictLeads has a dedicated GitHub repositories dataset; Crustdata doesn't.
- **Hacker News / Show HN / Launch HN** — not structured as an event source, even though Show HN is arguably the best product-launch signal on the internet.
- **Government filings beyond SEC** — no MCA/RoC (India), no Companies House (UK), no state-level incorporation feeds beyond whatever SEC provides.

**Source-diversity comparison:**

| Platform | News sources claimed | Social | SEC/filings | GitHub | Podcasts/YT |
|---|---|---|---|---|---|
| **Crustdata** | "press mentions" (not quantified) | LinkedIn only | SEC mentioned, no typed events | No | No |
| **PredictLeads** | 20M+ PR/news/blog sources | No native social | Not primary | Yes (dedicated GitHub dataset) | No |
| **Owler/Meltwater** | 180k news events/week, Meltwater social listening | Meltwater's social graph | No | No | Via Meltwater Podcast Radar (acquired separately) |
| **Bloomberg EDF** | 10k headlines/day + third parties + web/social | Yes | Yes (primary) | No | No |
| **Signal AI** | 1B+ documents from licensed news | Yes | Some | No | Yes via Signal AI Media |

Crustdata is **structurally narrow on sources**. This is a corollary of the architecture bet: by indexing on demand, you can't claim broad coverage of podcasts and YouTube, because you're not scraping them at scale. PredictLeads, which does run the deep ingest+classify pipeline, has the breadth.

---

## 4. Deduplication and entity resolution

Crustdata's actual technical moat. From the Feb-2026 Show HN post by Abhilash Chowdhary, Chris Pisarski, Manmohit Grewal (item 47146819):

> *"We maintain a canonical graph (ontology) of people and companies: stable internal IDs, aliases, and relationships. Then we continuously index web content mapped to correct entity identifiers... 6 deduplicated results in ~1,200 tokens vs ~4,000 tokens"*

This is the strongest Crustdata-specific technical claim in the entire doc base. Their dedup happens at **the entity-resolution layer**, not at the event layer:

- Every scraped web document, LinkedIn post, job posting, and news mention gets mapped to a canonical `company_id` or `person_id` through their ontology.
- Two press releases about "Stripe" (the payments company) don't produce two Crustdata events for two different Stripes — they collapse onto the one canonical `company_id`.
- The critical failure mode they call out: *"search found something about the wrong entity"*. Their anti-pattern is classic fuzzy-match search. Their differentiation is that a `python` search for LinkedIn posts with keyword `python` doesn't return the snake-owners.

What's missing from the public dedup story:
- **Event-level dedup across sources.** PredictLeads explicitly deduplicates when the same product-launch is covered by TechCrunch, VentureBeat, and the company blog — you get one event with `most_relevant_source_url`. Crustdata doesn't document this. If Stripe announces a product on LinkedIn and it's also covered by TechCrunch and ingested via Crustdata's press-mentions source, it's unclear whether you get one watcher fire or two.
- **Cross-entity event merging.** When Salesforce buys Slack, Salesforce should get an `acquires` event and Slack should get an `acquired_by` event. PredictLeads models this explicitly through the Connections dataset. Crustdata has no equivalent.
- **Temporal dedup.** If a company re-posts the same LinkedIn post a day later (common), does the keyword watcher fire twice? Not documented.

**Entity-resolution quality (my read):** Probably genuinely good at person-and-company resolution because LinkedIn URLs are a strong primary key. Almost certainly weaker at news-event dedup because they don't have the multi-source pipeline to dedup *against*. PredictLeads wins the event-dedup axis by architectural design.

---

## 5. Structured output — per-event fields

### 5.1 Crustdata's webhook payload (what actually fires)

The docs.crustdata.com Watcher API pages do not publish a canonical webhook-payload schema. The `/blog/how-ai-sdrs-use-webhooks-to-time-outreach` post says only: *"expect a JSON payload with details (e.g., person, event type, company, timestamp)"*. No example JSON is published. This is a documentation gap.

From the Composio MCP exposure and the Watcher UI descriptions, the likely payload shape is:

```json
{
  "watch_id": "uuid",
  "watch_type": "event|company|people",
  "trigger": "new_funding_announcement|job_posting|headcount_increase|linkedin_post|job_change|international_hiring",
  "fired_at": "2026-04-19T10:23:15Z",
  "entity": { "company_id": "...", "person_id": "..." },
  "delta": { ... depends on trigger ... },
  "source_context": { ... link to the underlying artifact ... }
}
```

Structured fields per trigger primitive (inferred from the docs):

- **`job_posting`** delta: `{ job_title, location, description_snippet, posted_at, matched_keyword }`. Likely also `seniority`, `department` from LinkedIn's taxonomy.
- **`new_funding_announcement`** delta: `{ round_type, amount_usd, announced_at, investors: [...], source_url }`. Scalar, no pre/post valuation, no instrument type (SAFE vs equity — see agent_07_funding_investor.md for why this is a gap).
- **`linkedin_post_with_keywords`** delta: `{ post_text, posted_at, poster: {person_id, name, title, company_id}, matched_keyword, engagement: { likes, comments, shares }, hyperlinks: [...] }`. This is strong — keyword-matched social posts with engagement metadata are genuinely rich.
- **`headcount_delta`** delta: `{ department, from_count, to_count, pct_change, measured_at }`. No per-employee breakdown, no who-left vs who-joined.
- **`international_hiring`** delta: `{ country, first_hire_person_id, first_hire_title, hired_at }`.
- **`person_starts_new_job`** delta: `{ person_id, old_company_id, old_title, new_company_id, new_title, started_at }`.

### 5.2 PredictLeads' per-event schema (for comparison)

From `predictleads.com/news_events` and the docs outline:

```
{
  "category": "hires_key_personnel" | "receives_financing" | ...29 values,
  "found_at": "2026-04-19T10:23:15Z",
  "confidence": 0.92,
  "formatted_signal": "Company X hired John Doe as VP Engineering",
  "article_sentence": "<exact sentence from article>",
  "article_body": "<full article text>",
  "article_author": "...",
  "most_relevant_source_url": "...",
  "location": { "city", "state", "country", "lat", "lon" },  // normalized
  "financing_details": { "amount_usd", "round_type", "investors" },  // normalized if applicable
  "image": "...",
  "related_company_id": "...",
  "related_person": { "name", "title" }
}
```

PredictLeads wins on **structured richness** — they've done the normalization work (amounts in USD, locations to lat/lon, sentence + body extraction, confidence score from the classifier). Crustdata's webhook payload is probably leaner and less normalized because Crustdata is optimized for trigger delivery, not historical analysis.

### 5.3 The free-text vs structured tradeoff

This is a deliberate design choice. PredictLeads runs ML classification → structured output → you query cleanly. Crustdata runs watch-condition matching → raw delta + source link → you (or your agent) classify on receipt. If your downstream is an LLM-driven workflow, Crustdata's raw-delta approach is actually better because you're going to ask Claude to classify anyway. If your downstream is a SQL warehouse for analytics, PredictLeads' pre-classified events save you a massive amount of classifier-running cost.

---

## 6. Push vs pull — the architectural thesis

Crustdata is push-first by design. The pitch from multiple marketing surfaces:

> *"The Watcher API fundamentally shifts the data paradigm from 'pull' to 'push'"*
> *"Instead of constantly polling an API for changes, you can 'subscribe' to events"*
> *"webhooks alert you the moment relevant updates happen, saving you time and credits"*
> *"monthly, weekly, daily, hourly, or instant updates when a predefined event happens"* (from the YC launch page)

Push cadence is configurable per-watch at five granularities: **monthly, weekly, daily, hourly, instant**. "Instant" is the real-time tier; slower tiers presumably batch fires within the chosen window to reduce noise.

Webhook reliability — retries, dead-letter, signature verification, idempotency — is not publicly documented. A production consumer has to build their own idempotency (using `fired_at` + `entity_id` + `trigger` as a dedup key) because retries-on-failure behavior isn't specified.

**Push vs PredictLeads:** PredictLeads also has webhooks ("API Webhooks" under every dataset in their doc tree). Their webhooks fire per-dataset on new-event ingestion. The semantic difference: PredictLeads' webhooks are a **firehose with filters** (fire on any new event in a category you subscribe to), while Crustdata's Watcher is a **trigger-per-entity** subscription (fire only when a specific condition on a specific entity is met). The trigger-per-entity model scales poorly for analyst workflows ("tell me about every Series A this week") but scales beautifully for sales workflows ("tell me when my 500 target accounts show buying signal"). That's a fundamental fit difference.

**Pull-side APIs** also exist on Crustdata — `/company/search`, `/person/search`, `/web/search/live` — for on-demand querying. You can replicate a news-event feed by polling these with the right filters but it's not idiomatic and wastes credits.

---

## 7. Coverage — company size, geography

### 7.1 Scale claims

From `/datasets/company-data` and the YC page:
- **60M+ companies** (one blog post from `/blog/best-mcp-servers-for-sales-teams-in-2026` says 700M+, probably a typo or including people). The canonical figure is 60M.
- **1B+ people profiles** (consistent across sources).
- **250+ datapoints per company, 90+ per person.**
- **16+ diverse datasets / sources.**
- **195 countries of coverage** (claimed as "global").

### 7.2 Company-size coverage

The prompt asked specifically: any size? below $10M ARR?

- **Enterprise / Fortune 2000:** Strong coverage. These have big LinkedIn footprints, press mentions, G2 reviews.
- **Mid-market ($10M–$100M ARR):** Probably good — still have LinkedIn + Crunchbase-level visibility.
- **Below $10M ARR / sub-50-employee:** **This is where Crustdata's freshness claim has to do work**. The 14–28 day snapshot refresh cycle + live-crawl-on-demand architecture means a sub-50-employee company with a sparse LinkedIn footprint will be discoverable within minutes of a request (per `/blog/b2b-data-api-providers`: "return data for untracked companies within minutes") but will have very few pre-populated watcher-observable events. The watcher requires existing LinkedIn signal density to fire — a company with 12 employees and 2 LinkedIn posts/year will rarely trigger a `linkedin_post_with_keywords` watch. Your event stream for a sub-$10M ARR long-tail cohort will be sparse regardless.
- **Stealth / pre-launch:** Near-zero coverage. Crustdata surfaces public web signal; stealth companies by definition don't have any.

### 7.3 Geography coverage

From the agent-07 doc and confirmed here:
- **US:** Strong. LinkedIn + SEC + press coverage is densest here.
- **EU/UK:** Good. LinkedIn coverage is high. Dealroom is the dedicated competitor.
- **India / Southeast Asia / LatAm:** Claimed as a strength by Crustdata's marketing. The *company data* side (headcount, job postings, LinkedIn) is plausibly strong because LinkedIn is genuinely deep in India. The *news-event side* is weaker because:
  - No native-language NER beyond English (PredictLeads has native-language support in English, Spanish, German, Dutch, French — Crustdata publishes no language list).
  - No regional filing integration (MCA in India, SEBI, state filings).
  - Press-mention aggregation is skewed to English-language TechCrunch/VentureBeat-style sources.

**Practical guidance:** for English-language enterprise events in US/EU, Crustdata is adequate. For events in Portuguese in Brazil or Hindi in India, Crustdata is not set up to catch them.

### 7.4 Historical depth

This is another real gap.

- **For snapshots (headcount, job openings, web traffic):** Crustdata provides **historical data for 6 datapoints** per `/datasets/company-data`: company headcount, headcount by function, job openings, web traffic, social follower counts, funding rounds. Historical coverage is tied to when Crustdata started tracking the company, which is gated by when the company crossed their discovery threshold.
- **For events (watcher-fire-worthy events):** There is **no event-history endpoint**. The Watcher API fires forward from the point at which you set up a watch. You cannot ask "what funding events happened for this company in Q1 2023?" and get the answer from a historical events table, because Crustdata doesn't expose one. You'd have to go to `/company/enrich` and read the `funding.*` sub-object (which only carries last round, not round history) or go to `/web/search/live` and run a web-search agent.

Compare to PredictLeads: "9+ million structured news events detected since 2016" — you can bulk-query 9 years of history. Compare to Owler: "180,000 news events each week" — similar historical corpus.

**Crustdata has effectively no event history.** It's a live-stream platform, not a time-series event warehouse. This is a major axis on which Crustdata loses to PredictLeads and is a product opening for anyone who wants to backtest a trigger strategy — you can't do that on Crustdata without building your own event log from watcher fires over time.

---

## 8. Head-to-head against PredictLeads

The closest structured-event competitor. Where each wins:

| Dimension | Crustdata | PredictLeads |
|---|---|---|
| **Event taxonomy breadth** | 6 trigger primitives | **29 canonical event types** |
| **Per-event structured fields** | Lean, source-link-oriented | **Normalized location, amount, sentence, confidence, author** |
| **Historical event corpus** | None queryable; forward-firing only | **9M+ events since 2016, bulk queryable** |
| **Media source breadth** | Press mentions (not quantified), LinkedIn primary | **20M+ media sources** |
| **Native-language NER** | English only (implicit) | **English, Spanish, German, Dutch, French** |
| **Country coverage** | 195 claimed, but English-biased | **195 countries** |
| **Real-time freshness** | **Live crawl + push webhook** | Batch ML classifier (hours of pipeline latency) |
| **Entity resolution** | **Ontology graph over LinkedIn, strong** | Company-domain-based, weaker person resolution |
| **LinkedIn post as event** | **First-class watch trigger** | Not supported (no LinkedIn pipeline) |
| **People-level watches** | **`person_starts_new_job` + job-change watchers** | Company-centric only |
| **GitHub as event source** | No | **Dedicated GitHub repositories dataset** |
| **Job openings / Technology detections as datasets** | Partial (job-posting watcher, no tech-detection dataset) | **Dedicated datasets for both** |
| **Connections / supply-chain graph** | No | **Connections dataset (categorized relationships)** |
| **Webhook architecture** | **Trigger-per-entity (precise)** | Firehose-with-filter (broad) |
| **Customer fit** | AI SDRs, AI recruiting agents, startup-lead research | VC analysts, market-intel teams, B2B data vendors reselling |
| **Pricing transparency** | Quote-based, ~$95/mo minimum | $500/mo minimum stated on comparison pages |
| **Customer count (signal)** | 150+ (per YC page, as of $6M seed Oct 2025) | Not disclosed; older (2015 founding vs 2020) |
| **HN-surface discussion depth** | Low (Show HN with 10 points, 0 comments Feb 2026) | Near-zero (one 2023 mention, negative on quality) |

**Where Crustdata structurally wins:**
1. **Freshness architecture.** Live crawl + push webhook is real-time in a way PredictLeads' batch ML pipeline can't be.
2. **LinkedIn as first-class.** PredictLeads has no LinkedIn pipeline; Crustdata is basically a LinkedIn-optimized product.
3. **People-level watches.** Tracking "VP of Sales at Acme just changed jobs" is native in Crustdata and structurally impossible in PredictLeads because PredictLeads is company-event-centric.
4. **Agent-ready primitives.** If you're building AI-agent-driven workflows (AI SDR, AI recruiter) you want raw posts + entity-linked search, not pre-classified events. Crustdata maps to that shape.
5. **Entity-resolution graph** is a genuine moat vs anyone else relying on fuzzy match.

**Where PredictLeads structurally wins:**
1. **Event taxonomy and structured normalization.** 29 types vs 6, normalized location and amount fields, confidence scores from supervised ML.
2. **Historical corpus.** 9M events since 2016 you can bulk-query. Crustdata has zero.
3. **Multi-source event dedup.** Collapse the same event across 10 news outlets → one row. Crustdata doesn't have this pipeline.
4. **Non-English-language NER.** Spanish/German/Dutch/French native support. Crustdata is English-centric.
5. **Specialized datasets** (GitHub, Technology Detections, Connections, Products) that Crustdata doesn't have as typed endpoints.

**The read:** these are **complementary products, not substitutes**. A sophisticated GTM platform in 2026 should be running PredictLeads for historical event analytics + taxonomy-rich segmentation and Crustdata for real-time LinkedIn-driven trigger-based outreach. The vendor who **fuses** the two wins. More on this in §10.

---

## 9. Comparison vs the broader event-data landscape

Quick pass on the five mentioned competitors:

**PredictLeads** — covered above.

**Signal AI** — 1B+ document licensed-content corpus, Topic-based search API, primarily a media-intelligence and reputation-risk platform for enterprise PR/IR teams. Not a B2B-sales event feed. Crustdata is far cheaper and much more sales-oriented; Signal AI is far deeper on news-analytics and cross-language coverage. Different category. Crustdata doesn't compete with Signal AI; Crustdata competes with PredictLeads for the sales-trigger use case and with Clay/Apollo for the enrichment use case.

**Bloomberg Event-Driven Feeds** — the financial-grade tier. Corporate Events Calendar (300,000 event notifications from 48k+ companies in 100+ countries — earnings, sales, board, shareholder meetings), Corporate Earnings feed (10,000+ companies, guidance+forecast updates), Textual News (10,000+ headlines/day from 151 Bloomberg bureaus). Crustdata is 3-4 orders of magnitude smaller and not licensed for trading decisions. Different category. Bloomberg owns finance-grade event detection; Crustdata cannot realistically compete here.

**Owler (Meltwater)** — post-acquisition by Meltwater in 2021. 16 news-event types + 20 newsfeed filter types (funding, product launches, partnerships, key hires, layoffs, conference sponsorship, record earnings, etc.). 180k news events/week. 3.5M active users, 45M company relationships mapped, 20M businesses. Owler covers finance/M&A better than Crustdata (because Meltwater's news graph is huge), but its API is less flexible than Crustdata's Watcher. Owler is a competitor for the "competitive intelligence" use case. Crustdata is more developer-focused.

**LinkedIn News Alerts** — consumer-grade. No structured API beyond the private Events Management API for managing LinkedIn-hosted events. No programmatic access to "alert me when Company X's headcount grows 10%". Crustdata arguably IS the missing LinkedIn alerts API for B2B — that's exactly what the Watcher primitives do. The real problem: Crustdata gets this data through LinkedIn scraping which sits in a gray-legal zone (the hiQ v LinkedIn case established the legality of public-data scraping but the operational risk remains). PredictLeads deliberately does not rely on LinkedIn, which is part of why their person-resolution is worse but their legal exposure is lower.

**Harmonic / Tracxn / CB Insights / Dealroom / Crunchbase** — private-markets intelligence. Covered in agent_07_funding_investor.md. Not event streams in the sense asked about here but they do have richer funding-event structure than Crustdata.

---

## 10. Product angles this signal stream enables that nobody's shipping

The prompt asked for specifics. These are products I can sketch end-to-end where Crustdata's Watcher API + LinkedIn-post + entity-resolution primitives are the load-bearing substrate and nobody in the competitive set (PredictLeads, Apollo, Clay, Owler, ZoomInfo) can replicate without the same LinkedIn-first architecture.

### 10.1 "Champion Graph" — the LinkedIn-post-based decision-maker-change alert

**Insight:** the most valuable B2B signal isn't "Company X raised a round", it's "the champion who bought our product at their last company just joined Company Y". PredictLeads structurally cannot do this (no LinkedIn pipeline, company-centric). Apollo and ZoomInfo have job-change alerts but not with LinkedIn-post context + engagement metadata + the ability to filter by who the champion's network replies to.

**What Crustdata gives you:** `person_starts_new_job` watcher + `get_social_posts` for that person + `linkedin_post_with_keywords` to catch when they talk about their priorities at the new company + the entity-resolution graph so you know the champion and their network are canonical.

**Product:** a CRM-plugin that, for every closed-won deal, silently registers all buying-committee members on a Watcher. When any of them changes jobs, you get (a) the new company, (b) their first 30 days of LinkedIn posts inferring priorities, (c) a warm intro path via their LinkedIn network graph, (d) auto-drafted outbound that references specific posts they made. This is a champion-graph SaaS sitting on top of Crustdata's push layer. **Nobody ships this today** because it requires the three Crustdata primitives combined; PredictLeads ships #1 but not #2/#3; Gong/Outreach ship #4 but need external signal to trigger on.

### 10.2 Real-time "stealth exec hire" detection for recruiters

**Insight:** when a well-known engineering leader joins a stealth startup before the announcement, their LinkedIn update happens 2-8 weeks before the press release. LinkedIn alerts catch the title change but have no way to filter by "this person has worked at Stripe/Meta/Google and is now at a sub-50-employee unannounced company". PredictLeads catches the press release — 2+ months late. Owler catches it when it's news — also late.

**What Crustdata gives you:** `person_starts_new_job` on a pre-registered watch set of 50k tier-1-company senior ICs + engineering leaders, filtered by new-company size <50 employees (derivable from `company.headcount`), filtered by new-company LinkedIn-description keywords ("stealth", "AI", "agent") or funding stage pre-seed.

**Product:** a talent-intelligence feed for technical recruiters that surfaces "your target exec just joined a company with no press release 3 days ago". Price $1-2k/mo per recruiter. Total market: ~3-5k high-end tech recruiters. **Nobody ships exactly this** because the primitives are only wired up in Crustdata — you could assemble it in PDL but you'd be polling, not push, and coverage latency is much worse.

### 10.3 Buyer-intent via LinkedIn-post vocabulary drift

**Insight:** before a company decides to buy Observability/Security/AI-tooling, the relevant decision-makers start using the vocabulary in their LinkedIn posts 4-12 weeks before the buying cycle formalizes (classic Brian Balfour / Bombora intent insight, but on LinkedIn posts not ad cookies). PredictLeads has no LinkedIn pipeline. Bombora has third-party cookies which are dying and don't attribute to named decision-makers.

**What Crustdata gives you:** `linkedin_post_with_keywords` watch on a vocabulary ("evaluating X", "chose Y", "migrating to Z", "scaling our observability") across the buying committee you've identified via `/person/search` on target accounts. Entity resolution means you know WHICH person on the committee is talking.

**Product:** "Intent signal but attributed to named humans, not cookies." Sits between Gong/Outreach (conversation intelligence, post-meeting) and Bombora (cookie-based intent, pre-meeting). Market: every B2B SaaS company with a $100k+ ACP. **Nobody has shipped this correctly** because Bombora owns cookie intent (dying), 6sense owns technographic intent (IP-level, not person-level), and no one else has LinkedIn + entity-resolution + push layer. The reason nobody ships is that you need LinkedIn data at scale + legal exposure + the watcher push architecture, and the people who have data (Clay, Apollo) don't have push-first and the people who have push (Segment, Rudderstack) don't have LinkedIn.

### 10.4 "First 10 hires" compound-growth signal for VCs

**Insight:** seed-stage VCs want to know when a portfolio or prospect company makes its first Head of Sales, first CFO, first data hire. Pitchbook catches the board-level hires. LinkedIn catches all hires but you'd manually filter. Crustdata's `first_person_hired_in_company_department` primitive is literally designed for this.

**What Crustdata gives you:** `first_person_hired_in_company_department` across a portfolio of 500 tracked companies, with departments set to Sales, Finance, Data, Engineering Leadership, Operations. Fires once per company per department.

**Product:** a "compound-growth dashboard" for VCs — each portfolio company shows "first sales hire: 2026-03-15 (Jane Doe, ex-Salesforce)", "first CFO hire: 2026-04-02 (Jim Smith, ex-Stripe)". Color-coded by seniority of hire vs round size (VP-of-Sales hired at Seed = premature; Analyst hired at Series B = under-investing). Sits next to Affinity/Crunchbase/Airtree. Market: ~500 early-stage VC firms. **Nobody ships this specifically** because the primitive — "first person hired in X department" — is a Crustdata-specific abstraction; PredictLeads has "hires_key_personnel" but not filtered to first-ever per department per company.

### 10.5 The anti-churn signal: "key employee left to competitor"

**Insight:** when an enterprise customer's key employee-sponsor leaves for a competitor of yours, that's the earliest possible churn signal. Gong/Salesforce can tell you usage dropped but that's lagging. LinkedIn job-change alerts tell you the person left, but not that they went to your competitor.

**What Crustdata gives you:** `person_starts_new_job` + the `new_company_id` resolved to canonical + a pre-loaded competitor list per customer. When a tracked champion's new employer is in the competitor set, fire high-severity alert.

**Product:** a Customer Success platform that ingests your tracked-champions list + your per-account competitor list (from your CRM) and fires a webhook when a champion moves to a competitor. Auto-draft the save-the-customer email. Market: every B2B SaaS > $5M ARR. **Gainsight/ChurnZero/Catalyst should ship this** but they don't today because they live inside the CRM and don't have access to the people-search-plus-competitor-lookup graph. Crustdata gives you the primitive.

### 10.6 Legal-compliance due diligence: "key executives of a SOC2-scoped-entity changed"

**Insight:** if you're SOC2-audited, your auditor wants to know when the CISO or key security engineers at any subprocessor change. Today this is tracked manually via LinkedIn checks. You could push-subscribe via Crustdata's people-watcher on all subprocessor exec teams, receive alerts, auto-file change tickets in your compliance tool (Vanta/Drata/Secureframe).

**What Crustdata gives you:** `person_starts_new_job` on a set of subprocessor CISOs, Heads of Security, DPOs. Plus `company_headcount_increased_by_pct` on the security department of each subprocessor (negative threshold = security team shrinking = risk signal).

**Product:** a Vanta/Drata integration that turns your subprocessor list into a real-time roster-change feed. Price: $500-1000 per subprocessor tracked annually. Market: every SOC2-compliant org that has subprocessors (basically every B2B SaaS). **Vanta should ship this** but doesn't because they don't have access to structured job-change + security-dept-headcount data. Crustdata gives both.

### 10.7 The "first product-launch post by a founder" event — catchable via keyword watcher

**Insight:** Crustdata doesn't have a native `product_launch` event type. PredictLeads does. But Crustdata catches every LinkedIn post with configured keywords. If you watch the founders of 50k pre-Series-B companies for posts matching "launching", "introducing", "our new product", "today we're shipping", you get an event that PredictLeads catches via press release 2-8 weeks later. This is where Crustdata's live-crawl + LinkedIn-post-watcher + entity-resolution beats the PredictLeads ML-classifier pipeline on latency by a wide margin.

**Product:** a "first to know about new products" feed for growth marketers, competitive intelligence teams, Product Hunt hunters, and AngelList scouts. Combines `linkedin_post_with_keywords` (founder posts with launch language) + `/web/search/live` (to grab the product landing page) + entity-resolution (to know which company). **Crustdata's Watcher makes this 10-20x fresher** than the PredictLeads event feed because it skips the ML-classifier + press-release lag path.

---

## Closing note

Crustdata's news/signals surface is narrower than the marketing suggests and narrower than the prompt's taxonomy implies. The Watcher API is not 29 event types; it's 6 trigger primitives. But the architectural bet — entity-resolution graph + live-crawl + push webhooks + LinkedIn as first-class source + people-level watches — creates a set of primitives that, when composed, unlock product categories that PredictLeads, Apollo, Clay, Owler, LinkedIn Alerts, and Bloomberg EDF all structurally cannot. The moat is **not** in the event taxonomy; the moat is in the **push-plus-person-plus-entity-graph** trio, and that's where the seven product angles above become uniquely shippable on Crustdata and uniquely hard to build on anything else.

---

## Sources

- [Crustdata Watcher API](https://crustdata.com/apis/watcher) — 6 trigger primitives, 3 watcher types
- [Crustdata Webhooks](https://crustdata.com/webhook) — push architecture marketing
- [Crustdata About](https://crustdata.com/about) — 14-28 day refresh cycle
- [Crustdata Dataset Overview](https://crustdata.com/datasets/company-data) — 60M+ companies, 250+ datapoints, historical data for 6 datapoints
- [Crustdata Real-time vs Batch Blog](https://crustdata.com/blog/real-time-vs-batch-data-enrichment) — latency architecture, "live crawling takes seconds"
- [Crustdata Webhooks for AI SDR](https://crustdata.com/blog/how-ai-sdrs-use-webhooks-to-time-outreach) — company+people signals list
- [Crustdata B2B Data Providers Ranked](https://crustdata.com/blog/b2b-data-api-providers) — self-comparison with PDL/Coresignal/ZoomInfo/Cognism
- [Crustdata MCP for Sales](https://crustdata.com/blog/best-mcp-servers-for-sales-teams-in-2026) — MCP server at mcp.crustdata.com, tool exposure
- [Composio Crustdata Toolkit](https://composio.dev/toolkits/crustdata) — 14 MCP tools exposed
- [Merge Crustdata Connector](https://docs.merge.dev/merge-agent-handler/connectors/crustdata) — `create_watch`, `update_watch`, `get_watch`, `list_watches`, social tools
- [Clay Crustdata Integration](https://www.clay.com/integrations/data-provider/crustdata) — enrich company, enrich person actions
- [YC Launch: Crustdata Live Data](https://www.ycombinator.com/launches/M6F-crustdata-live-company-and-people-data-via-apis) — "watch companies and people on a live basis, monthly/weekly/daily/hourly/instant"
- [Crustdata YC Profile](https://www.ycombinator.com/companies/crustdata) — $6M seed Oct 2025, 150+ customers, founders
- [LinkedIn YC Crustdata Post](https://www.linkedin.com/posts/y-combinator_crustdata-yc-f24-provides-apis-and-webhooks-activity-7254884321210048513-Y_2r) — event list, 401 reactions, 39 comments
- [Product Hunt Crustdata Reviews](https://www.producthunt.com/products/crustdata-3/reviews) — 4.4/5 across 13 reviews, latency concerns from Chen
- [Skywork Crustdata Deep Dive](https://skywork.ai/skypage/en/Crustdata:-The-Real-Time-Data-Engine-for-Your-AI-Stack/1975037718378377216) — architecture analysis, 16+ datasets
- [Show HN: Crustdata Web Search API](https://news.ycombinator.com/item?id=47146819) — Feb 2026, entity-resolution ontology claim
- [HN Item 47387130](https://hn.algolia.com/api/v1/items/47387130) — ptrtht comment "data is often 6-9 months stale"
- [PredictLeads News Events](https://predictleads.com/news_events) — 29 event types, 9M+ events since 2016, 50k/week, 20M+ sources, 195 countries, 5 languages
- [PredictLeads Docs Guide](https://docs.predictleads.com/) — 16 dataset sections, News Events with Categories/Data Model/Webhooks
- [Slashdot Crustdata vs PredictLeads](https://slashdot.org/software/comparison/CrustData-vs-PredictLeads/) — PredictLeads $500/mo, Crustdata quote-only
- [Owler Pro](https://corp.owler.com/owler-pro) — 16 news event types, 180k events/week, 15 trigger events for Instant Insights
- [Bloomberg Event-Driven Feeds](https://www.bloomberg.com/professional/products/data/enterprise-catalog/event-driven-feeds/) — 300k event notifications, 48k+ companies, 100+ countries
- [Signal AI API](https://signal-ai.com/solutions/api/) — 1B+ licensed documents, Topic concept API
