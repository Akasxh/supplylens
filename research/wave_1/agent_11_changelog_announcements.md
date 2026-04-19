# Crustdata — 12-Month Shipment Timeline & Virgin-Territory Analysis

**Agent 11 | Wave 1 | 2026-04-19**

## Scope & Methodology

Goal: build a dated shipment timeline for Crustdata from the last ~18 months (Nov 2024 → Apr 2026) and identify capabilities that have shipped but which no third-party app has meaningfully built on yet. The intent is to surface virgin territory for later research waves.

**Sources actually reached** (all ✓ unless noted):
- `crustdata.com/blog` index (front page only surfaces April 2026; older posts reached by targeted URL)
- `crustdata.com/contextcon`, `crustdata.com/apis/{watcher,posts,job-listing}`, `crustdata.com/datasets/company-data`, `crustdata.com/full-dataset`, `crustdata.com/webhook`, `crustdata.com/about`, `crustdata.com/blog/{crustdata-closes-6m-seed-round, best-mcp-servers-for-sales-teams-in-2026, b2b-prospecting-workflow-claude-code, what-is-websearch-api}`
- Product Hunt: `/products/crustdata-2` (main), `/products/crustdata-3` (People), `/products/signal-watcher`, `/products/private-company-database`
- YC: `/companies/crustdata`, `/launches/M6F-crustdata-live-company-and-people-data-via-apis`
- Luma event page: `luma.com/6ftay6mq` (ContextCon)
- Hacker News Algolia API: 3 queries across 18 months
- GitHub: `github.com/crustdata` org + `crustdata/skills` repo
- piwheels/PyPI: `crustdata-mcp` package metadata
- Composio MCP toolkit: `composio.dev/toolkits/crustdata` (14 tools)
- Docs: `docs.crustdata.com/openapi-specs/2025-11-01/introduction` + cached HTML (see Agent 01)

**Sources that failed or were blocked**:
- `docs.crustdata.com/changelog` → redirects to login; no public changelog exists
- `crustdata.com/changelog`, `blog.crustdata.com` → 404 / DNS NXDOMAIN. There is **no dedicated changelog surface**.
- `x.com/TheChowdhary`, `x.com/chrispisarski`, `x.com/crustdata` → 402 / CF challenge (Twitter requires auth for scraped fetches). Founder posts only reachable via Google-surfaced snippets.
- `linkedin.com/company/crustdata/posts/`, Abhilash's `linkedin.com/in/abhilashchowdhary/` → 60s timeout on every attempt (LinkedIn blocks `WebFetch`). Individual posts fetched via direct URLs.
- `web.archive.org` → hard-blocked in this environment.
- Slack / Discord / Linen: **no public community exists.** `crustdata.com/about` lists no community links. Customer support is private 1:1 Slack with the engineering team (stated in the $6M seed announcement); no public customer community is referenced anywhere.

**Key implication**: Crustdata does not maintain a public changelog, a public roadmap, a public community, or a public SDK changelog. All "what shipped when" evidence is reconstructed from launch announcements (PH + YC launches + seed posts + LinkedIn snippets) and implicit signals (API version header, blog post dates, PyPI upload timestamps).

---

## Shipment Timeline (chronological, oldest → newest)

| Date | Shipment | Category | Source URL | Third-party adoption evidence |
|---|---|---|---|---|
| **~Oct 29, 2024** | YC Launch: "Crustdata: Live Company and People Data via APIs" — original positioning around company/people enrichment + Watcher for instant/hourly/daily updates | Platform launch | `ycombinator.com/launches/M6F-crustdata-live-company-and-people-data-via-apis` ; `linkedin.com/posts/y-combinator_crustdata-yc-f24-provides-apis-and-webhooks-activity-7254884321210048513-Y_2r` (YC company page post, activity ID 7254884321210048513, Oct 2024) | Core APIs now used by YC (founder discovery), MNTN (AI SDR), Dharmesh Shah's agent.ai |
| **Nov 6, 2024** | Product Hunt launch #1 — "Crustdata: Real-time people and company data via APIs and webhooks" — 703 upvotes, #2 of day, #4 of week | Public launch | `producthunt.com/products/crustdata-2` | Reached #2 of day. Broad adoption of /screener/person/search and /screener/company/search via Clay, Relevance AI, Latenode integrations post-launch |
| **(May 30, 2024, pre-period)** | Product Hunt — "Private Company Database" (Crustdata's **first** PH launch, 2M+ co profiles, 150+ firmographic metrics) — 576 upvotes | Dataset launch | `producthunt.com/products/private-company-database` | Predates our window but is the foundation for the Company Dataset |
| **May 28, 2025** | Product Hunt launch #2 — "People Dataset" — full people data on hundreds of millions of profiles, Parquet delivery, 568 upvotes, #3 of day | Dataset launch | `producthunt.com/products/crustdata-2?launch=people-dataset` | Used internally by recruiting platforms for "candidate warehouse" use case; no public third-party app known to have specifically built on the *bulk* Parquet feed (vs. the API) |
| **Sep 17, 2025** | Product Hunt launch #3 — "Person search API" — 60+ filters, real-time crawling at request time, 743 upvotes (PH reports 110 / hunted.space reports 743), #2 of day, #3 of week, #4 of month | API launch | `producthunt.com/products/crustdata-3` ; `linkedin.com/posts/crustdata_we-launched-our-new-people-search-api-on-activity-7374207770457198592-Yn7D` | Became the most-integrated endpoint in Composio's MCP toolkit; the People Search filter explosion is the single biggest driver of API usage per their own marketing |
| **Oct 22, 2025** | $6M seed round closed — lead Y Combinator + A.Capital; GC, SV Angel, Phosphor, Lobster, Liquid 2, Transpose participated. Announced roadmap: "expand from 8 to 15+ data sources, launch web search APIs, add contact data" | Funding + roadmap pre-announce | `crustdata.com/blog/crustdata-closes-6m-seed-round` ; `linkedin.com/posts/chris-pisarski_im-incredibly-excited-to-announce-crustdata-activity-7387148602747383808-BuWx` ; Garry Tan quote on `linkedin.com/posts/garrytan_theres-people-data-out-there-but-then-theres-activity-7256807194388504577-_Rub` | N/A (funding event); triggered press coverage across pulse2.com, einpresswire, artiverse.ca, justainews, startuphub.ai |
| **Nov 15, 2025** | Product Hunt launch #4 — **"Signal Watcher"** — 350+ datapoints, 3 watcher types (People / Company / Event), real-time webhooks, 205 upvotes, #7 of day | API + webhook launch | `producthunt.com/products/signal-watcher` | Exposed as MCP tool (see Apr 2026 row). Of all Crustdata shipments, this is the one with the **weakest** third-party app presence — no standalone apps built on event-watcher webhooks are findable via HN, PH, or Google as of Apr 19, 2026 |
| **~Nov 1, 2025 (inferred)** | API v**2025-11-01** header release — new Bearer-token + `x-api-version` scheme, `/company/search` + `/person/search` + `/web/search` + `/web/fetch` + Identify/Enrich on canonical `api.crustdata.com/*` paths. Replaces legacy `api.crustdata.com/screener/*` + `Authorization: Token` scheme (still live for enterprise) | API versioning / platform | `docs.crustdata.com/openapi-specs/2025-11-01/introduction` (12 endpoints across Company/Person/Web) ; corroborated in Agent 01's cached `crustdata_openapi-specs_2025-11-01_introduction.html` | **No third-party tooling has migrated** — Composio's toolkit and the community `crustdata-mcp` PyPI package still target legacy `/screener/*` endpoints with `Authorization: Token` |
| **Jan 22, 2026** | Product Hunt launch #5 — **"Web Search API by Crustdata"** — "the fastest web search API for AI Agents", 346 upvotes, #2 of day. Proprietary entity-linking to person/company IDs, Web Fetch endpoint (up to 10 URLs/call) | API launch (flagship) | `producthunt.com/products/crustdata-2` (shared umbrella) ; `launches.uicomet.com/products/web-search-api-by-crustdata-zlRpB` ; `linkedin.com/posts/dougwebb_crustdata-people-and-company-search-apis-activity-7420181964139307008-JdXF` | Referenced as "option for Data MCP" in agent workflows. See Feb 25, 2026 Show HN — community engagement **very low**: 10 points, 0 comments |
| **Feb 25, 2026** | Show HN: "Crustdata (YC F24) – Web Search API for Token-Efficient AI Agents" | Community launch | `news.ycombinator.com/item?id=47146819` ; Algolia objectID 47146819, `loondri` (Abhilash) | **10 points, 0 comments** — this is the only Crustdata-related Show HN in 18 months and it failed to generate any community discussion. Massive gap between marketing narrative and dev community awareness |
| **Mar 12-13, 2026** | Third-party `crustdata-mcp` PyPI package v0.1.0 and v0.1.1 uploaded (MCP server for Claude Desktop / Cursor) | Third-party integration | `piwheels.org/project/crustdata-mcp/` | This is **community-authored**, not by Crustdata. First third-party dev actually building on the new v2025-11-01 API |
| **~Mar 2026 (inferred)** | Crustdata MCP Server officially listed — exposes company search (95+ filters), people search (60+ filters), in-DB enrichment (250+/co, 90+/person), social posts, web search, **Watcher alerts**. Works with Claude Desktop + Claude Code. Crustdata's own blog says "every major sales vendor launched an MCP server in the past six months" (relative to Apr 2026) | MCP distribution | `crustdata.com/blog/best-mcp-servers-for-sales-teams-in-2026` ; `composio.dev/toolkits/crustdata` (Composio toolkit v20260407_00, 14 tools) ; `mcp.composio.dev/crustdata` ; `zapier.com/mcp/crustdata` ; `mcp.deco.site/mcp/crustdata` | Available via Composio, Zapier, Deco. Composio markets it as "14 tools". **But** the Composio toolkit still exposes *legacy* `screener/*` endpoints — so it's distribution without modernization |
| **Apr 8, 2026** | ContextCon announcement tweet — "Crustdata has partnered with YC to host first-ever YC hackathon in Bangalore" | Event announcement | `x.com/TheChowdhary/status/2041945340803535127` (Abhilash Chowdhary, @TheChowdhary, Apr 8, 2026) ; `linkedin.com/posts/loveena-sirohi_for-the-first-time-y-combinator-is-coming-activity-7441863147910688768-nKyR` | Drove registration to `luma.com/6ftay6mq` |
| **~Apr 9, 2026** | `github.com/crustdata/skills` public repo — open-source Claude Code + Cowork skills (email-enrichment, candidate-sourcing). Latest release tag v2026.04.09-9. 6 stars. | Developer enablement | `github.com/crustdata/skills` | Only Crustdata-authored open-source repo publicly visible. 1 fork, tiny adoption |
| **Apr 18, 2026** | Wave of product-page publishes (Watcher, Posts, Job-listing, Company Dataset all show publish date `Apr 18, 2026, 7:07 PM UTC`) — likely a site-wide re-render / migration, not a launch | Site / docs refresh | `crustdata.com/apis/watcher`, `/apis/posts`, `/apis/job-listing`, `/datasets/company-data` | N/A — marketing page refresh |
| **Apr 19, 2026** | **ContextCon** live — first YC hackathon in Bangalore. 6-hour build, mandatory Crustdata API usage, $8K/$3K/$1K prizes, guaranteed YC office hours with Jon Xu. Hosts: Nithish A, Abhilash Chowdhary, Daniel Ahmadizadeh, Ajay Suwalka, Chris Pisarski, Manmohit, Jai Ganesh. Sponsored by Stripe Atlas (20% off / full fee waiver for winners). Tracks explicitly open: "sales intelligence, recruiting, market research, AI investment agents, or novel applications welcome." No new API announced at the event per the event page — it's a build-on-existing-APIs hackathon | Ecosystem event | `crustdata.com/contextcon` ; `luma.com/6ftay6mq` | Event is happening **today** (Apr 19, 2026). Results / demos will surface in the following 1-2 weeks |

---

## HOT shipments (last 90 days — Jan 19 → Apr 19, 2026) with weak or zero third-party app presence

The following shipped in the last 90 days but have **no findable consumer-facing third-party app built on them** as of today:

| # | Feature | Shipped | Third-party presence (as of 2026-04-19) |
|---|---|---|---|
| **H1** | **`/web/search` + `/web/fetch` endpoints** (Web Search API v2025-11-01) — entity-linked results, up to 10 URLs per fetch, geo/domain/source filters, fetch_content=true for full HTML | **Jan 22, 2026** | Show HN: 10 points, 0 comments. No apps on Product Hunt, HN, or GitHub (outside crustdata-mcp) built on this specifically. Composio toolkit does not expose `/web/*`. This is the flagship shipment of 2026 and the ecosystem has not caught up. |
| **H2** | **Signal Watcher — Event Watchers** (job posting with keyword, company hiring % change, department-level hires, funding announcement, LinkedIn post with keyword) — real-time webhook push | Nov 15, 2025 (inside 90d if you squint, just outside if strict) | **Zero findable apps.** Watcher is consistently listed on Crustdata's own product pages but I cannot find a single public third-party app, Chrome extension, CRM plugin, Slack bot, or n8n/Zapier community workflow that subscribes to Watcher webhooks and does something novel with them. This is the starkest whitespace. |
| **H3** | **MCP Server with Watcher tools exposed** — Claude Desktop / Code can subscribe to Watchers via MCP | ~Mar 2026 | Only the Crustdata-authored `crustdata/skills` repo (email-enrichment, candidate-sourcing) uses the MCP. No third-party Claude Code "skill" or "agent" on the community side has shipped a Watcher-driven automation. |
| **H4** | **`/person/search` with 60+ filters** + live crawling at request time (rebranded from legacy `/screener/person/search`) | Sep 17, 2025 (RECENT, but still within scope) | Widely referenced but almost exclusively via Crustdata's own integrations/OEM (agent.ai, YC, MNTN). No standalone "people-search-as-a-service" app consumer-facing product is built on it. |
| **H5** | **API v2025-11-01 Bearer + version-header scheme** (`/company/search`, `/person/search`, `/company/enrich`, `/person/enrich`, `/person/autocomplete`, `/company/autocomplete`, `/company/identify`, `/person/identify`, `/web/search`, `/web/fetch`, + 2 more = 12 endpoints) | ~Nov 1, 2025 | Composio (14 tools), Zapier, Deco all still ship against **legacy** `/screener/*` + `Authorization: Token`. The v2025-11-01 modernization is invisible in the tool ecosystem. |

## RECENT shipments (3–12 months old: Apr 2025 → Jan 2026)

- **People Dataset (Parquet bulk delivery)** — May 28, 2025 — used by some recruiting platforms but no novel consumer app
- **Person Search API (60+ filter explosion)** — Sep 17, 2025 — driver of API usage; flagship Recent shipment
- **Signal Watcher** — Nov 15, 2025 — see H2 above
- **Job Listing API with 35 filters + 30+ datapoints** — quietly in-market; no dedicated launch but present on `crustdata.com/apis/job-listing`; full coverage since at least the Oct 2025 seed
- **Social Posts API** (`/apis/posts`) — get posts by person/company/keyword, engagement + engager profiles; pre-dates the Nov 2025 v2025-11-01 scheme but still actively marketed
- **`crustdata/skills` open-source repo** — effectively Apr 9, 2026 (latest tag), borderline HOT; tiny adoption (6 stars)

## MATURE shipments (older than 12 months, pre-Apr 2025)

- **Original Company Enrichment + Search APIs** — pre-YC F24
- **Private Company Database** (PH launch May 30, 2024) — the foundation product
- **Initial Watcher concept** (monthly/weekly/daily/hourly/instant updates, framed in the Oct 2024 YC launch)
- **CSV / S3 bulk dataset delivery** — active since before Nov 2024 PH launch
- **Core `/screener/*` legacy endpoints** — still alive (return 401, not 404 per Agent 01 probing)

---

## Founder channel summary (Twitter/LinkedIn - last 12 months)

Unable to scrape Twitter directly (CF-blocked for `WebFetch`). Evidence via search snippets:

- **@TheChowdhary** (Abhilash Chowdhary): active; the only visible post is the ContextCon announcement (Apr 8, 2026, status 2041945340803535127). An older PH-launch tweet from May 2024 surfaced (status 1796108959771980032) — pre-period. No other high-signal tweets surfaced.
- **@chrispisarski** (Chris Pisarski): Twitter fetch returned 402. Only LinkedIn snippet reached: the seed-round announcement post (activity 7387148602747383808) from ~Oct 22, 2025 ("5 months ago" from Apr 2026).
- **@crustdata** (official): Twitter fetch blocked by network restriction. Bio text seen in Google snippet: "Realtime company and people data".
- **Crustdata LinkedIn company page**: blocked by LinkedIn anti-scrape. Via Google snippets, evidence of: YC F24 announcement post (activity 7254950250220527616, Oct 2024); People Search PH-launch post (activity 7374207770457198592, ~Sep 17, 2025); $6M seed posts.

**There is no evidence of active Twitter/X thought leadership from either founder** beyond milestone posts. Compare against peers (Clay, Apollo, ZoomInfo) whose founders post 2–4x/week.

## Community channel summary

- **No public Slack / Discord / Linen / GitHub Discussions.** Confirmed by searching `crustdata.com/about`, `crustdata.com/docs`, GitHub org, and direct Google queries.
- Customer support is "24/7 Slack-based with engineering team access" per the seed-round blog post — but this is **private per-customer Slack Connect**, not a community.
- The only public developer-facing assets: `github.com/crustdata/skills` (6 ⭐) and third-party PyPI `crustdata-mcp` (45KB wheel).

## HN discussion summary

Ran 3 Algolia queries over 18 months (`created_at_i >= 1729275486`). Results:

- **1 Show HN** (Feb 25, 2026, Web Search API, 10 pts, 0 comments) — the only Crustdata-originated HN story in the window.
- **1 ambient comment** (Jan 7, 2026, on a Foundertrace Show HN at id 46482685) where user `loondri` (i.e. Abhilash) mentions Crustdata is the data source.
- **1 competitor comment** (Mar 15, 2026, on story 47387103) from user `ptrtht` comparing Crustdata and IcyPeas on "high per-lookup costs and stale data." Borderline negative signal.
- The rest of the "crustdata" Algolia hits are noise — mostly "Crustafarianism" (a separate AI-religion satire project from a different domain), plus `crtdatabase.com` (CRT monitor database).

**Conclusion**: HN community is essentially unaware of Crustdata's 2026 product line. This is a ripe vacuum for a third-party app that goes on HN with "Built X using Crustdata's Web Search / Watcher" — would be novel content to the HN crowd.

---

## Newest capabilities third-party apps could exploit before the ecosystem catches up

Ranked by asymmetry (how much is shipped vs. how little is built on it):

1. **Watcher event-webhooks as the push-signal layer for autonomous agents.** Signal Watcher has 3 watcher types (People / Company / Event) and 350+ datapoints, but literally zero consumer-facing third-party apps exploit the *push* model. Everyone is still polling. The obvious build: a "job-change-to-CRM-update" agent, a "funding-round-to-LinkedIn-congrats" agent, a "champion-left-account-to-CS-alert" agent — each a 200-LoC MCP/Zapier app. Watcher is the biggest single lever in the product and the biggest single hole in the ecosystem.

2. **`/web/search` + `/web/fetch` as a token-efficient RAG substrate for agent frameworks.** The Web Search API (shipped Jan 22, 2026) returns entity-linked, deduped results. Anyone building a LangChain/CrewAI/AutoGen agent is currently wasting tokens on SerpApi + Firecrawl + custom dedup. A drop-in Crustdata Web Search tool + a Crustdata Web Fetch tool for each of those frameworks would ship in a day and would be the first such integration anywhere. Crustdata's own Composio toolkit does **not** currently expose `/web/*`.

3. **The entity-ID graph (`crustdata_company_id`, `crustdata_person_id`) as a canonical identifier for AI agents.** Every Crustdata response attaches stable IDs. No third-party graph DB, vector DB, or CRM currently treats these as first-class IDs — everyone still keys on LinkedIn URL or domain. A "knowledge graph sync" tool that keys on Crustdata IDs would be novel.

4. **API v2025-11-01 SDKs in TS / Go / Python.** No official first-party SDK exists. Composio and Zapier both still target legacy `/screener/*`. Writing a typed TS SDK for the 12 modern endpoints would immediately become the reference.

5. **Bulk People Dataset (Parquet) as an embedding-indexing substrate for passive candidate / prospect search.** The dataset is "hundreds of millions of profiles, monthly refresh, Parquet delivery." No third-party has built a public embedding index on top of it for semantic candidate search. Recruiting platforms rolling their own internal versions is confirmed (per the PH launch copy), but nothing developer-facing.

6. **LinkedIn Posts API for AI-SDR personalization loops.** The Posts API returns posts + engagers with full employment context. No consumer app currently monitors target-account posts and auto-drafts comments — the closest is Taplio, which uses its own data. A Crustdata-backed "comment-on-my-target-accounts-posts" Chrome extension would be virgin territory.

7. **ContextCon demos will be the first real stress-test of the ecosystem.** Whatever ships today (Apr 19, 2026) from the hackathon will tell us what 100+ engineers decided was buildable in 6 hours. Results worth monitoring in Wave 2.

**Biggest single takeaway for later waves**: Crustdata's product surface has lapped its developer ecosystem. The v2025-11-01 API scheme, the `/web/*` endpoints, and the Signal Watcher webhook model are all shipped and documented but functionally invisible to the third-party tooling layer (Composio/Zapier still on legacy; HN unaware; no official SDKs). This is a rare state where capability > awareness for a well-funded YC company — anyone who moves in the next 60 days is early.
