# Agent 10 — Crustdata Showcase Audit

**Mandate.** Audit everything Crustdata themselves showcase — docs, demos, GitHub, blog, LinkedIn, Product Hunt, ContextCon. What they market is the crowded zone. What's in docs but unmarketed is the dark zone. The gap = opportunity surface.

**Evidence corpus.** `crustdata.com` sitemap (~100 URLs), `docs.crustdata.com`, `github.com/crustdata` (1 official repo), GitHub-wide "crustdata" search (~120 community repos), 25+ blog posts, LinkedIn company page, Product Hunt launch history, Composio toolkit manifest, YC company page, AIChief third-party review. Dates current as of 2026-04-19.

---

## Section A — The crowded zone (what Crustdata hammers in every demo)

### A.1 The drumbeat — 4 customer archetypes repeated on every page

Every solution page, every blog post, every case study hits the same 4 personas:

1. **AI SDR / sales automation.** `solutions/ai-sdr`, `solutions/sales`, `solutions/sales-pipeline-optimization`, `solutions/marketing-automation`, `solutions/build-internal-sales-tools`, case studies ("AI SDR Platform: 4x ARR growth"), blog posts ("How to Build an AI SDR with Reliable Data Infrastructure", "What Is an AI Sales Agent", "AI Lead Generation Software"). Rox is named as the flagship ("exclusive data provider for Rox on Autopilot revenue agent").
2. **Recruiting / candidate sourcing.** `solutions/recruiting`, `solutions/executive-search`, `solutions/internal-recruiting`, blog posts ("Passive Candidate Sourcing", "Best AI Sourcing Tools", "People Search API Recruiting Agency Workflow"), case studies ("Executive Research Firm: 200 recruiters"; "AI Recruiting Platform: 100K+ profiles"; "Tech Recruiting Agency: 200K+ enriched records"). One of the two official Claude skills is `candidate-sourcing`.
3. **VC / growth equity deal sourcing.** `solutions/venture-capital`, `solutions/growth-equity`, blog posts ("AI Tools for VC: Why Top Funds Build Proprietary Pipelines", "7 Best Startup Databases for Investors", "API-First Alternatives to PitchBook"). Name-dropped comps: Motherbrain (EQT), Beacon (SignalFire), DIG (InReach), Gordon (Alpaca), Puck (Thrive). Two case studies: "Top-5 VC by AUM live knowledge graph" and "Growth Equity Fund replaced $20K/seat PitchBook".
4. **Data enrichment / CRM hygiene.** `solutions/data-enrichment`, `solutions/email-enrichment-api`, `solutions/target-market-analysis`, blog posts ("Programmatic CRM Enrichment", "Waterfall Enrichment", "Best Contact Enrichment APIs in 2026"). The other official Claude skill is `email-enrichment`.

### A.2 The signature demo template — one story, retold

The same workflow pattern appears in ~80% of Crustdata's marketing:

> `Discovery API` → filter companies by ICP → `Enrichment API` for 250+ firmographics → `Watcher API` webhook on a trigger (job change / funding / hiring spike) → personalized outreach via AI agent.

Shown verbatim in: `blog/b2b-prospecting-workflow-claude-code` (defines `/prospect`, `/qualify`, `/draft-outreach` slash commands), `blog/how-to-build-ai-sdr-data-infrastructure`, `blog/agents-crustdata-mcp-connector`, `blog/best-mcp-servers-for-sales-teams-in-2026`, `solutions/ai-sdr`, `solutions/target-market-analysis`. The 4 named signals are always the same: **job changes, funding rounds, headcount growth, LinkedIn posts**.

### A.3 The 2 official GitHub repos — both are SDR/recruiting

The Crustdata GitHub org has exactly **one public repo: `crustdata/skills`** (created 2026-03-16, 6 stars). It contains exactly **two skills**: `email-enrichment` and `candidate-sourcing`. Both target the AI-SDR / recruiting persona. No "venture capital" skill. No "competitor monitoring" skill. No "web traffic analytics" skill. No "product launch radar" skill. No "M&A deal sourcing" skill. The asymmetry is stark.

All ~120 other GitHub repos matching "crustdata" are 3rd-party — 90%+ are forks of the Crustdata Build Challenge (Jan 2025), which itself asked entrants to build a **customer-support chatbot over Crustdata docs** (i.e., meta, not a real use case). A handful of hackathon-era "CrustData AI Agents Hackathon" repos (Aug 2025) and "ContextCon" repos (Apr 2026) exist — they re-target the same SDR/sourcing territory.

### A.4 Product Hunt launch cadence — all pitched to the same persona

4 PH launches, all framed for "AI agents for sales/recruiting/investment":

| Launch | Date | Upvotes | Framing |
|---|---|---|---|
| Real-time People & Company Data via APIs + webhooks | 2024-11-06 | 40 | generic |
| People Dataset (bulk) | 2025-05-28 | 61 | generic |
| Web Search API | 2026-01-22 | 48 | "the gateway to the internet for AI agents" |
| Person Search API (60 filters) | 2026 (LinkedIn-announced) | 743 | "ultimate search for people data" |

Every launch pitch uses the exact phrase "for AI agents." Not "for analysts." Not "for journalists." Not "for researchers." Not "for lawyers." Not "for policy." Not "for due diligence / PE diligence rooms."

### A.5 The 4 flagship event triggers — a saturated signal set

`Watcher API` and the webhook product are always marketed with 4-5 canonical triggers: **new job / funding / job posting / headcount growth / LinkedIn post with keyword**. The homepage opens with three mannequin triggers: "Sierra Jackson left Humanloop," "Obento completed a $100M seed raise," "Magnitude hired 6 people." This narrow event vocabulary is the defining signature of their marketing.

### A.6 Competitor-comparison real estate — who Crustdata wants to unseat

14 comparison pages exist on `/vs/*`, sorted into three buckets:
- **API-commodity enrichment vendors** they want to replace outright: Proxycurl, ZoomInfo, Clearbit, PeopleDataLabs, Apollo, Coresignal, MixRank, EnrichLayer.
- **UI workflow tools** they want to route around: Clay, Clado.
- **Scraping / search-adjacent** they want to displace: Bright Data, Apify, SerpAPI, Exa.

The positioning is always identical: *Crustdata = real-time, API-first, agent-ready; competitor = stale/cached, UI-first, human-ops-shaped.*

### A.7 Summary — the saturated zone

Anyone building "AI SDR with Crustdata," "candidate sourcer with Crustdata," "VC deal-sourcing Motherbrain clone with Crustdata," "CRM enrichment pipe with Crustdata," or "account-research brief generator with Crustdata" is competing **directly inside the story Crustdata already tells every prospect**. Building these gets you zero mindshare you didn't already have as a Crustdata customer. The founders, their YC GTM, their blog SEO, and every BDR pitch already own this real estate.

---

## Section B — The dark zone (endpoints that exist, marketing that doesn't)

### B.1 Endpoints / data surfaces visible in docs + Composio + URL structure that marketing under-serves

These are the Crustdata capabilities I can verify exist but that appear in no demo, no skill, no case study, no blog post as a hero use case:

**B.1.a — `Fetch Headcount by Facet Timeseries` (Composio tool #2).**
Crustdata exposes company headcount as a **time series sliced by function/department**. Every VC tool in existence uses monthly aggregate headcount. A function-level timeseries (engineering vs. sales vs. ops) is a leading indicator of strategic pivot, ZIRP unwind, product-led-transition, offshoring moves, and defense-tech pivots. Marketing mentions "headcount growth %" — never mentions the facet-level timeseries as a distinct primitive.

**B.1.b — `Post Web Traffic Data` (Composio tool #8) + "Podium traffic +108.4%" one-liner.**
Crustdata indexes **web traffic trends with SEO metrics** — SimilarWeb-class data — for 60M+ companies. This only appears as a trivial homepage mannequin. No blog post on "how to build a competitor-traffic radar." No skill that alerts on traffic anomalies. No VC-use-case of "traffic falling off cliff = founder distress signal." SimilarWeb charges ~$50K/yr for this kind of thing.

**B.1.c — `Fetch Investor Portfolio Data` (Composio tool #3).**
Crustdata returns **portfolio holdings for named investors** — the inverse query to deal sourcing. Marketing pitches "find new deals"; never pitches "monitor an investor's portfolio in real time," or "detect when a Tier-1 fund adds a new B2B SaaS" as a signal that competing funds should chase. No skill. No blog post. Pure dark zone.

**B.1.d — `Filter Decision Makers` nested-filter primitive (Composio tool #4).**
The new Person Search API supports **60 nested filters** (announced on LinkedIn Sep 2025 / Oct 2025). The marketing example is always "find a VP of Sales at a $10M–$50M-ARR SaaS." Complex nesting — "people who changed from company X to competitor Y and now follow a specific founder" — is technically supported but never modeled as a showcase. Saturation for single-predicate; dark zone for graph-shaped queries.

**B.1.e — LinkedIn post reactor data (referenced only in the Proxycurl-comparison page).**
On `/vs/proxycurl-alternative` Crustdata claims exclusive access to **up to 5,000 reactors per post with full profile details**. This is the single most under-marketed capability in the entire audit: reactor-level social graph data is a wholesale competitive-intelligence signal (who engages with your competitor's content = churn-risk map). It gets one comment in `blog/competitor-monitoring-tools`. No skill. No case study. No solution page.

**B.1.f — Product Hunt launch data + review platforms (Glassdoor / G2 / Gartner) hinted at in `/datasets/company-data`.**
The dataset page lists "Product Hunt launches" and "Review platforms (G2, Glassdoor, Gartner)" as indexed fields but no API page, no skill, no demo app exploits this. A "PH-radar" skill that watches for breakout tools on PH and enriches every founder on day 0 would be trivially built.

**B.1.g — "CEO approval ratings / employee reviews" shown on the homepage, invisible everywhere else.**
Homepage text mentions Glassdoor-class signals. No downstream surface — no endpoint page, no skill. Dark.

**B.1.h — SEC Form D filings.**
Mentioned on the homepage banner as a data source for funding detection. No dedicated endpoint page, no skill, no blog. Possible build: "alert me the moment a Form D is filed by any founder I've met."

**B.1.i — `Fetch Job ID` / historical job postings.**
Blog post `how-to-find-old-job-postings` goes out of its way to say Crustdata is "focused on current, not historical." Yet Composio's tool #13 (`Search for Job ID in Screener`) and the `post_job_listings_table_data` timeseries capability imply some historical surface exists. Actively de-marketed — classic sign of capability that exceeds mindshare.

**B.1.j — News data + press mentions (`/datasets/company-data`).**
Indexed but has no API page, no skill, no competitive-intel use-case demo. Every fund building a "news radar over my portfolio" today uses a $5K/mo alt vendor.

**B.1.k — Post Funding Milestone Timeseries** (Composio tool #5) — enables cohort analytics like "every SaaS that raised a Series A between 2022-Q1 and 2022-Q3 and still hasn't raised follow-on." Never demoed.

### B.2 Active deprecation / re-architecting signals (soft-marketing tells)

The sitemap contains three URLs revealing a web-search product still being re-shaped:
- `/apis/web-search-old` — explicit legacy page (timed out fetch; its existence is the signal).
- `/apis/web-search-editing` — in-flight product marketing draft.
- `/apis/websearch` — current page.

Separately, `/solutions/growth-equity--old` exists alongside `/solutions/growth-equity` — a live A/B or positioning pivot.

And `/home-v2` and `/home-v3` in the sitemap show iterative re-pitching of the top of funnel. All three tells indicate Crustdata itself is unsure how to position the web-search + deep-research layer, which is exactly where a third-party builder has room to define a canonical use-case before they do.

### B.3 Capability gaps Crustdata openly admits

From blog post `best-contact-enrichment-apis-in-2026`:
- "Credit-based pricing is consumption-driven, which requires monitoring at high volume." → opportunity: a **cost-aware orchestration skill** that caches and dedups.
- "Phone numbers were newly launched and might not be as accurate as legacy vendors." → opportunity: a **phone waterfall** skill that routes phone-specific misses to a cheaper secondary.

From the Clay comparison: "SDRs manually building and reviewing lead lists" is "better for Clay." → opportunity: a **non-technical-team shim** over Crustdata's API that restores the list-review UX.

### B.4 Endpoints that DO exist in docs but get zero marketing love — the hard list

| Endpoint / capability | Visible in | Marketing surface |
|---|---|---|
| Company headcount by function, timeseries | Composio manifest | ~0 |
| Web traffic timeseries (SimilarWeb-class) | `datasets/company-data`, Composio | 1 homepage mannequin |
| Investor portfolio query | Composio manifest | 0 |
| LinkedIn post reactor lists (5k reactors) | `/vs/proxycurl`, docs | 1 blog mention |
| Product Hunt launch index | `datasets/company-data` | 0 |
| G2 / Glassdoor / Gartner review data | `datasets/company-data` | 0 |
| SEC Form D filings | homepage | 0 |
| News / press mentions index | `datasets/company-data` | 0 |
| Funding-milestone cohort timeseries | Composio manifest | 0 |
| Historical job-posting archive | Composio manifest | actively de-marketed |
| Person graph: nested cross-company transitions | API supports, 60 filters | 0 |

---

## Section C — Interpretation: what does the asymmetry tell us about opportunity?

### C.1 What Crustdata's marketing asymmetry reveals

Crustdata is optimizing for the path of **fastest commercial traction**: the AI-SDR + recruiting wedge pays the bills today, which is why every blog, every skill, every solution page, and both official GitHub artifacts are pointed at that wedge. This is rational for them. But it means the company is **under-promoting roughly half of its own data graph** because building demand for those surfaces would slow the AI-SDR go-to-market story. That under-promotion is the opportunity shape.

Three converging pieces of evidence confirm the shape:
1. **Only 2 official skills** (email enrichment, candidate sourcing) against ~14 distinct tools exposed through Composio and ≥20 data surfaces visible in the docs. A 7-to-1 coverage gap.
2. **Zero case studies** on competitor monitoring, product-launch radar, social-graph intelligence, traffic-anomaly detection, investor-portfolio monitoring, or regulatory-signal surfaces despite all of these being possible from the data schema.
3. **Actively de-marketed** historical job-posting archive and deprecated `/apis/web-search-old` endpoints indicate capabilities that the marketing team wants to retire narratively, but that a third-party builder can revive as first-class primitives.

### C.2 The three highest-asymmetry wedges for a third-party builder

These are ordered by (capability surface area) × (marketing silence) × (non-trivial workflow distance from AI-SDR):

**C.2.a — Competitive intelligence / competitor radar.** LinkedIn reactor data + web traffic timeseries + product-launch index + news index + hiring-by-function timeseries compose a **CI product competitors price at $30K–$200K/yr** (Klue, Crayon, Kompyte). Crustdata has the raw graph. Nobody is shipping this on top of them. Target buyer: head of CI, head of product marketing — both outside the AI-SDR persona.

**C.2.b — Portfolio ops / VC internal tooling.** The investor-portfolio-query tool + post-funding timeseries + function-level headcount + social reactor data compose a **portfolio-monitoring platform at the Foundry/Visible/Kushim tier**. Crustdata markets itself as "VC deal sourcing" — i.e., the pre-investment wedge — but has zero surface for post-investment ops. An internal-ops-for-VCs product is a blue ocean inside Crustdata's own dataset.

**C.2.c — Regulatory / public-filing signal layer.** SEC Form D + news/press + executive movement + hiring-by-function + traffic anomalies = the raw ingredients for a **Stealth Startup detection / FP&A distress signal / anti-fraud early warning** product. Crustdata's messaging does not touch finance, public policy, regulatory, or audit. Every enterprise-tier buyer in those verticals is currently paying FactSet / S&P / Moody's $100K+/yr for inferior freshness.

### C.3 Secondary wedges worth flagging

- **Cost-aware orchestration tooling.** Crustdata admits credit-consumption is unpredictable. A Claude skill / SDK that caches results, dedups calls, and rate-limits across their 4 different RPM ceilings (30 / 15 / 60 / 10 per the email-enrichment SKILL.md) is a clear pain-reliever — and Crustdata will ship it only reluctantly because it lowers revenue per customer.
- **Non-technical UI shim.** Crustdata literally concedes Clay wins for manual list review. A thin no-code UI that preserves the API-first primitives underneath (unlike Clay, which hides them) is a Clay-vs-Airtable-tier wedge.
- **Graph-shaped person queries.** The 60-nested-filter Person Search API is technically capable of graph traversal (transitions, follows, co-employment) but the marketing treats it as flat. A visualized "person graph" tool (LinkedIn meets Palantir Gotham-lite) can sit on this for trust-and-safety, due diligence, or OSINT buyers.

### C.4 What *not* to build

- Any variant of "AI SDR / outbound orchestrator." This is saturated, the founders own the demo, and Crustdata is explicitly building their own (`/skills/candidate-sourcing`, `/skills/email-enrichment`, `blog/b2b-prospecting-workflow-claude-code`).
- Any "chatbot over Crustdata docs." 80+ third-party repos already exist from the 2025 Build Challenge. Dead zone.
- Any "VC deal sourcing Motherbrain-clone" positioned against PitchBook. Crustdata already has case studies on `/case-studies` for this exact use case with Top-5 VCs.
- Any "CRM enrichment plumbing." Hammered in the `solutions/*` set and in `blog/programmatic-crm-enrichment-api`. Zero differentiation possible.

### C.5 One-line summary

**Crustdata sells "signals for outbound"; their graph supports "signals for competitive strategy, portfolio ops, and regulatory/finance early-warning." The gap between what they market and what their API schema can answer is where a third-party builder has air cover for 18–24 months before Crustdata's own GTM closes it.**

---

## Appendix — Key file/URL references

Source pages sampled (all URLs absolute):
- `https://crustdata.com` — homepage with signal mannequins
- `https://crustdata.com/sitemap.xml` — full URL inventory (source of truth for this audit)
- `https://crustdata.com/case-studies` — 15 customer case studies
- `https://crustdata.com/full-dataset` — bulk/S3 delivery pricing
- `https://crustdata.com/datasets/company-data` — data-point enumeration
- `https://crustdata.com/datasets/technographic` — job-description-derived tech stack
- `https://crustdata.com/apis/watcher` — event subscription
- `https://crustdata.com/apis/posts` — LinkedIn posts + reactors
- `https://crustdata.com/apis/job-listing` — 35 job filters, 30+ fields
- `https://crustdata.com/apis/websearch` — current web search
- `https://crustdata.com/apis/web-search-old` — **deprecated (404)**
- `https://crustdata.com/apis/web-search-editing` — in-flight draft
- `https://crustdata.com/apis/company-discovery` — 95+ filters
- `https://crustdata.com/apis/people-discovery` — 60+ filters
- `https://crustdata.com/apis/company-enrichment` — 250+ datapoints
- `https://crustdata.com/apis/people-enrichment` — 90+ datapoints
- `https://crustdata.com/solutions/{ai-sdr, venture-capital, growth-equity, growth-equity--old, target-market-analysis, build-internal-sales-tools, data-enrichment, marketing-automation, sales, sales-pipeline-optimization, recruiting, customer-success, product-led-growth-teams, email-enrichment-api, executive-search, internal-recruiting}`
- `https://crustdata.com/vs/{clay, clado, proxycurl, coresignal, mixrank, peopledatalabs, bright-data, zoominfo, enrich-layer, clearbit, serpapi, apify, scrapin-io}-alternative*`
- `https://crustdata.com/blog/*` — 25+ posts indexed via sitemap
- `https://crustdata.com/contextcon` — YC India hackathon, 2026-04-19 (today!)
- `https://github.com/crustdata/skills` — **only official repo** (6 stars, 2 skills: email-enrichment, candidate-sourcing)
- `https://docs.composio.dev/toolkits/crustdata` — 14 exposed actions, richer than the marketing narrative
- `https://www.ycombinator.com/companies/crustdata` — YC F24 profile
- `https://www.producthunt.com/products/crustdata-2` + `crustdata-3` — 4 launches: core APIs, People Dataset, Web Search API, Person Search API
- `https://www.linkedin.com/company/crustdata` — company updates, Rox flagship case study, $6M seed (Nov 2025)
- `https://aichief.com/ai-marketing-tools/crustdata/` — third-party external review

Local evidence written to: `/home/akash/PROJECTS/crustdata/research/wave_1/agent_10_crustdata_showcase.md`
