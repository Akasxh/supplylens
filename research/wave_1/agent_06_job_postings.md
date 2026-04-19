# Agent 06 — Crustdata Job Postings Data: Deep Dive

**Author:** Agent 06 (Research wave 1)
**Date:** 2026-04-19
**Scope:** Crustdata's job posting dataset vs LinkUp, Greenhouse, LinkedIn Talent Insights, TalentNeuron, Revelio, Lightcast, Indeed, TrueUp, Coresignal, Bloomberry, TheirStack, Techmap.

---

## 0. TL;DR

Crustdata does **not** run a LinkUp-class daily-crawled global job index. What it ships is:

1. A **`Jobs API` / `Job Listing API`** (`crustdata.com/apis/job-listing`) that returns **30+ datapoints per posting, 35 search filters** in one call, oriented at real-time prospecting rather than archival analytics.
2. A **Watcher API** that pushes webhooks when a tracked company opens roles matching keyword + location rules — this is the product, not "the 500M-record dataset."
3. **Company-level hiring metrics** (`job_openings`, `Total Job Listings`, `Job Listing Growth By Function`) surfaced in the Company Data API / dictionary — i.e. derived aggregates over the underlying postings.
4. An explicit **`Web Search API`** used to surface postings that exist only on company career pages and never hit boards.

Crustdata has positioned as the **real-time, event-driven, entity-linked** layer — explicitly not trying to out-LinkUp LinkUp on multi-year archival depth. Coresignal's own comp page ([coresignal.com/coresignal-vs-crustdata](https://coresignal.com/coresignal-vs-crustdata/)) claims Crustdata refreshes "monthly" with 30-60s API latency — this is a **competitor spin** and contradicts both Crustdata's own material and its webhook architecture. Real mechanism: live, on-demand crawl of the target surface at request time, plus continuous polling for Watcher-tracked entities.

---

## 1. Sources — Exact List

Crustdata publicly names the following job-data ingestion surfaces:

| Source class | Evidence |
|---|---|
| **Major job boards** | "Pull structured job postings from major job boards via the Jobs API" (crustdata.com/blog/best-apis-for-job-posting-data) — unnamed but the context implies the mainstream aggregators (LinkedIn Jobs, Indeed, Glassdoor, Wellfound class). |
| **Company career pages** | "Users can access the websearch API to surface roles posted directly on specific company career pages that never make it to job boards." This is the Web Search API fallback path (docs.crustdata.com/docs/discover/web-search-api). |
| **Greenhouse / Lever / Workday (ATS)** | Not named as direct ingestion targets in public material. Crustdata's own competitor blog treats LinkUp as the leader for "employer career pages, ATS" and positions its own product differently. The Merge agent-handler connector (docs.merge.dev/merge-agent-handler/connectors/crustdata) exposes a `search_job_listings` tool with company_id/title/location/date_posted/url/seniority filters — an aggregated output, source-blind. |
| **LinkedIn (company posts + job listings)** | `get_company_linkedin_posts` tool captures LinkedIn activity ([Composio/Merge]). LinkedIn Jobs mentioned as a source in the broader 16+ source aggregation ("16+ verified sources"). |
| **Not disclosed: direct ATS API keys (Greenhouse JobBoardAPI, Lever postings, Workday CXS)** | No public disclosure that Crustdata consumes the free Greenhouse JobBoardAPI or Lever public postings JSON. That's the obvious low-cost path and Bloomberry/TheirStack/Techmap all do it; Crustdata's silence here is conspicuous but not a no. |

**Self-consistent picture:** Crustdata is a *meta-aggregator over both API-scraped boards and on-demand career-page crawls*, resolving results to company entities via its internal ID graph. It is **not** a primary ATS scraper in the LinkUp / Techmap sense.

---

## 2. Historical Depth — Oldest Posting Retained

**Public claim: historical data from 2019 to present is available** (surfaced via doc-search snippets from a third-party write-up cited above: "Historical data from 2019 to present is available, covering job postings going back for most companies, useful for multi-year trend analysis").

**Caveat:** Crustdata's own `how-to-find-old-job-postings` blog explicitly punts — it praises **Revelio Labs' 4.1 billion current-and-historic postings** rather than boasting its own archive. The Crustdata framing is: *"Most job data tools show you what companies hired for in the past. Crustdata shows you what is happening right now."* That is a **real-time-first** positioning; historical depth is a secondary feature, not a product pillar.

**Working estimate:** 2019–present for the company-level aggregate series (`Total Job Listings` over time, by function, by geography). For raw per-posting payload with description/URL, retention is probably tighter (months rather than years), consistent with the competitor landscape:
- LinkUp: 2007+ (daily, employer-only) — the archival champion.
- Lightcast: 2010+ US — deep academic/government-grade series.
- Revelio COSMOS: 4.1B current + historic postings.
- Techmap: Jan 2020+.
- Bloomberry: 2020+ (career pages only).
- Crustdata: **2019+ aggregates, real-time raw, unconfirmed per-posting retention window.**

---

## 3. Refresh Cadence & Latency

**Three-tier latency model** inferred from the product surface:

1. **Watcher API (push)** — "the moment a defined trigger fires" per Crustdata. No scheduled polling from the customer side. Expected latency: seconds to minutes from crawl detection to webhook fire. This is the hot path for "new role opened" events.
2. **Jobs API / Job Listing API (pull, on-demand)** — "live data crawling." For untracked companies/domains Crustdata claims ability to return fresh data "within minutes." For already-indexed entities, cached + delta-refreshed per Watcher cycle.
3. **Bulk company-level metrics (`job_openings`, `Total Job Listings`)** — these are aggregates; in competitor comparisons Coresignal claims Crustdata is "monthly" but that describes **full-dataset bulk refresh**, not incremental event detection.

**Latency from posting-goes-live to appears-in-API:**
- For **Watcher-tracked companies**: minutes (continuous poll of the source).
- For **untracked companies queried on-demand**: minutes (request triggers crawl).
- For **aggregated company metrics**: daily to monthly (rollup bounded by bulk dataset cycle).

The Coresignal "30-60s API response time" claim is response *latency* of the HTTP call, not freshness. Mixing the two is a standard competitor-comp tactic.

---

## 4. Title Normalization — Taxonomy

**No public evidence that Crustdata uses O\*NET-SOC, ESCO, or NAICS occupation codes.** The public field list advertises:

- `job category / department` (free-text-ish)
- `workplace type` (onsite / remote / hybrid — 3-value enum)
- `title` (raw posting title, not normalized)

Third-party sources describe "normalized job title, region, company domain, and full-text description" for career-page crawls — this suggests a **proprietary normalization layer** rather than an ISO-grade taxonomy mapping.

**"Senior ML Engineer" vs "ML Engineer II" dedup quality:** likely **weak** in the absence of a published taxonomy. Crustdata's differentiation is **entity resolution at the company/person level**, not occupation-code-grade title resolution. For title-class matching at Lightcast / Revelio / TalentNeuron quality you want O\*NET-SOC 2019 (1,016 titles, 923 data-level) or the O\*NET→ESCO crosswalk. Crustdata does not claim that.

**Implication:** if the downstream use case is **"count all Senior ML roles hiring in Q2 2026 across Bay Area"** at survey-grade granularity, Crustdata is the wrong tool — use Lightcast or Revelio. If the use case is **"alert me when Brex opens any ML role"**, Crustdata's entity-level tracking is sharper than taxonomy-first vendors.

---

## 5. Salary Coverage

**No disclosed salary-coverage percentage for Crustdata.** The published field list for the Job Listing API does **not** include salary as a top-line datapoint — it lists: job title, category/department, description, URL, openings count, reposted flag, workplace type, date added/updated, location (city/district/state/country + codes + pincode + geocodes), company metadata.

Salary is mentioned only obliquely in third-party MCP documentation ("salary range where public" via career-page crawls).

**Structural ceiling on salary coverage** (industry baseline, applies to anyone in this space):

| Jurisdiction | Law | Effective | Affects coverage |
|---|---|---|---|
| Colorado | Equal Pay for Equal Work Act | 2021-01-01 | First US state to mandate. |
| California | SB 1162 (amended) | 2026-01-01 (updated def. of "pay scale") | 15+ employee firms must include pay range in ads; $100–$10,000/posting penalty. |
| New York State + NYC | State Pay Transparency Law | 2023 / NYC 2022 | 4+ employee firms in NYC, statewide 4+. |
| Washington, Hawaii, Illinois, Minnesota, MD, MA, VT, NJ, DC | Various | 2023–2025 | 17 US states + DC as of 2026. |
| **EU-27** | **EU Pay Transparency Directive (Dir 2023/970)** | **transposition deadline 2026-06-07** | All member states must mandate salary ranges in job ads pre-interview. Slovakia first (2026-06), Netherlands slipping to 2027-01. |

**Practical coverage estimate for any job-data vendor in 2026:**
- **US postings**: ~50-60% carry salary (driven by CA+NY+CO+WA covering majority of tech hiring metros).
- **EU postings**: climbing from <20% (pre-2026) toward ~80%+ by end of 2027 as the directive transposes.
- **Rest-of-world**: 10–25%.
- Crustdata's coverage should track these jurisdictional numbers; there is no evidence of independent salary inference (Revelio does, Lightcast does — Crustdata does not claim it).

---

## 6. Geography

**Crustdata public claims:** "1 billion people across global profiles, 60 million companies indexed, 12M+ companies in bulk dataset." On jobs specifically, the API supports location filters at city / district / state / country (with codes) / pincode granularity and geocodes. No country-count disclosure.

**"Pincode" terminology is telling** — pincode is South-Asian usage (Indian postal codes specifically), strongly implying substantive **India coverage**. That's consistent with Crustdata's India-based data infra (and the founder's background).

**Comparative geography coverage:**

| Provider | Countries |
|---|---|
| Techmap | 254 |
| LinkUp | Global since 2007 (not country-counted publicly) |
| Lightcast | 40+ (academic-grade); 160+ at the Talent Analytics tier |
| TheirStack | 195+ |
| Revelio | 195 |
| Coresignal | Global |
| **Crustdata** | **Not disclosed; location filtering implies global + strong US + strong India (pincode field evidence)** |

**LatAm / Africa:** No evidence of deliberate coverage depth. Standard web-aggregator coverage expected (thin outside major metros), not Techmap/Lightcast-grade coverage.

---

## 7. Fields Per Posting

Confirmed fields from the public `apis/job-listing` page (exact list):

**Job entity:**
- Job title
- Full job description (free text)
- Job URL
- Job category / department
- Number of openings
- Workplace type — onsite / remote / hybrid (3-enum)
- Date added
- Date last updated
- Reposted-job flag

**Location (attached to job):**
- City, district, state, country (+ codes), pincode, location text
- Geocodes for district and state

**Company context embedded per posting:**
- Company info, website domain, industry, company size, largest-headcount country
- Investment stage / valuation
- Acquisition status

**Unconfirmed but implied (via Merge MCP / Composio wrapper):**
- Seniority (exposed via Merge's filter schema)
- Management level / urgency flag / shift schedule (Coresignal-comp table reference to "Multi-Source" tiers — unclear if Crustdata matches)

**Not publicly listed (conspicuous absences):**
- Salary range as first-class field (only "where public" via career-page crawl path).
- Benefits.
- Extracted tech stack per posting (aggregated at company level via headcount-derived tech-stack signal, not per-posting skill tags).
- O\*NET / SOC normalized occupation code.
- Standardized skill list.
- Employment type (full-time / contract / internship) as a clean enum.

**Skill / tech-stack extraction:** Crustdata's "technology signals extracted from job descriptions" claim is framed as a **company-level** aggregation — "identify technologies mentioned in postings to surface companies using or evaluating specific tools, programming languages, CRMs, databases, SaaS products." This is a technographic inference layer, not per-posting NER-style skill tagging at the granularity Lightcast Skills or ESCO ships.

---

## 8. Signals Derived From Postings

Confirmed derived-signal products:

1. **Hiring acceleration by function** — exposed as `Job Listing Growth By Function` in the company data dictionary (docs.crustdata.com/docs/dictionary/company). Direct hiring-velocity metric per department.
2. **Total Job Listings** — company-level aggregate time series.
3. **Geographic-expansion detection** — "target account opening roles in a new country" is a first-class Watcher trigger.
4. **New-department formation** — "a new department forming" is explicitly called out as a Watcher trigger event.
5. **Founding-role detection** — Crustdata markets "founding-role titles automatically surfaced." The trigger is recognizing "Founding Engineer / First Designer / Early GTM Hire"–class titles.
6. **Stealth-mode detection** — Crustdata's own stealth-founder blog (`crustdata.com/blog/the-complete-guide-to-tracking-and-finding-stealth-startup-founders`) describes exactly the signal chain — "Founder / Stealth" title changes on LinkedIn, "people leaving top companies without a listed next role," domain registrations, and jobs posted under anonymized company names ("Stealth e-commerce startup (Series A)"). This is a **marketed product**, not an emergent one.
7. **Remote-first hiring** — `workplace_type = remote` filter surfaces companies hiring remote-first globally.
8. **Early team formation** — hiring the first person in a department, or the first international hire, are named Watcher triggers.

**What Crustdata does NOT publicly claim to derive:**
- Skill-trend time series (which skill mentions are rising/falling across an industry — Lightcast's core product).
- Attrition / turnover rates (Revelio's core product, inferred from people-side data, not jobs).
- Wage / salary trend series (Revelio, Lightcast; needs salary inference).
- Occupation-level labor demand indexes.

---

## 9. Dedup Across Sources

**Architecture-level claim:** Crustdata's Feb 2026 Show HN (news.ycombinator.com/item?id=47146819) markets **entity resolution** as the core value: "maps search results to specific people, companies, or events using internal IDs rather than string matching." The job-posting path inherits this — the same posting surfacing on Greenhouse + LinkedIn + the company's own career page would resolve to one company entity, though whether the **postings themselves** (as separate records) collapse to one is unstated.

**Implicit dedup pipeline** (standard industry pattern, consistent with Crustdata's stack):
1. Exact URL match (cheap, catches most duplicates of the same posting crawled twice).
2. Title + company-entity-id + location + date-posted (same posting across Greenhouse → LinkedIn → aggregator).
3. Fuzzy description match for republishes.

**Weakness vs Coresignal / Revelio:** Crustdata has no publicly documented **multi-source dedup tier** (Coresignal explicitly has "Base" = single-source and "Multi-Source" = deduplicated as a product choice; Revelio markets a "dynamic deduplication model"). Crustdata is silent on the pipeline. Customers should treat Crustdata job-posting counts as **likely overcounted vs dedup-first vendors** when the same posting hits multiple channels — but undercounted on unique postings surfaced only through career-page crawling where LinkedIn-only vendors miss.

---

## 10. Volume

**Not publicly disclosed.** Nowhere in crustdata.com, docs.crustdata.com (public portions), any blog, or third-party review is a monthly jobs-indexed number posted. Adjacent disclosures that constrain the answer:

- **60M companies** total in the corpus.
- **12M+** in the bulk dataset.
- **"16+ verified sources"** in aggregate.

**Competitor volume benchmarks (for sizing):**

| Provider | Total jobs indexed | Daily/monthly cadence |
|---|---|---|
| LinkUp | 315M+ global since 2007 | Daily |
| Revelio COSMOS | 4.1B current + historic | Real-time updates |
| Coresignal | 461M+ (as of this cycle, was 425M earlier) | 500k+/day added |
| Lightcast | 2.5B total across 40+ countries | Daily |
| TheirStack | 171M from 195+ countries | Hourly |
| Techmap | Not posted | Hourly |
| Bloomberry | Not posted | 3–7 day refresh |
| **Crustdata** | **undisclosed** | **real-time on-demand + Watcher-triggered** |

**Educated estimate:** If Crustdata covers ~12M primary-tracked companies, and US+EU+IN typical active-posting density is ~1–2% of companies with open roles at any given time with ~5 openings average, the live-index floor is **~600k–1.2M active postings at steady state**, with monthly flow on the order of ~3–10M new/updated postings. **This is an order-of-magnitude smaller live index than LinkUp / Coresignal / Lightcast.** Crustdata is not trying to win on volume; it is trying to win on **fresh + entity-linked + triggered**.

---

## 11. Vs. Competitors — Summary Table

| Dimension | Crustdata | LinkUp | Greenhouse scraping | LinkedIn Talent Insights | TalentNeuron | Revelio COSMOS | Lightcast | Indeed | TrueUp | Coresignal | Bloomberry | TheirStack |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Sources** | Mixed: job boards + career pages + LinkedIn + on-demand web crawl | Employer career pages + ATS (direct, since 2007) | Greenhouse JobBoardAPI (free, ATS-native) | LinkedIn Jobs + profile signal | Proprietary aggregation | 440k company websites + boards + staffing firms | Multi-source + government feeds | Indeed's own aggregation | Jobs aggregator | LinkedIn + Indeed + Glassdoor + Wellfound | Career pages only | LinkedIn + 16 boards |
| **Historical depth** | 2019+ (aggregates) | 2007+ | customer-held (30–60 days on API) | LinkedIn-internal | not specified | 4.1B current+historic | 2010+ US | ~30 days public | real-time | Years (unspecified) | 2020+ | (not specified) |
| **Refresh** | Real-time (Watcher) + on-demand | Daily | Real-time via API poll | Daily | Weekly | Real-time | Daily | Real-time | Daily | Every 6h + 500k/day added | 3–7 days | Hourly |
| **Title normalization** | Custom / proprietary | Custom | None (ATS raw) | LinkedIn's taxonomy | Proprietary + O\*NET | Proprietary suite (occupation/seniority/geo) | O\*NET-SOC + ESCO grade | Custom | Custom | Normalized via Multi-Source tier | Custom | Custom |
| **Salary coverage** | Not disclosed; "where public" | Where public | N/A (raw postings) | LinkedIn inferred | Proprietary enrichment | Enriched variable | Inferred + public | Inferred | Public-only | type+range+currency | Where public | (not specified) |
| **Geography** | Global; strong US + IN inferred | Global | Depends on customer list | Global | 180+ countries | 195 | 40–160+ | Global | Primarily US | Global | Not posted | 195+ |
| **Skill extraction** | Company-level aggregate | Basic parse | None | LinkedIn's graph | Proprietary | Per-posting enrichment | Lightcast Skills (gold standard) | Limited | Limited | Multi-Source enriched | Limited | Limited |
| **Dedup across sources** | Entity-linked at company, per-posting unstated | Employer-direct so inherently deduped | N/A (single source) | N/A | Proprietary | Dynamic model | Rigorous | Internal | Aggregator-grade | Built-in multi-source | Career-page-only | Varies |
| **Volume** | Undisclosed (est. ~1M active live) | 315M+ global | per-tenant | undisclosed | proprietary | 4.1B | 2.5B total | ~42M | niche | 461M+ | Not posted | 171M |
| **Webhook / Trigger** | **Yes (Watcher API, differentiator)** | No | Webhooks per ATS | No | No | No | No | No | No | No | No | No |

---

## 12. Confidence & Gaps

**High confidence:**
- Crustdata is real-time/event-driven first, not archival first.
- Exposes `job_openings` and `Total Job Listings` / `Job Listing Growth By Function` as company-level metrics.
- Watcher API is the key differentiator vs the job-data-provider cohort.
- No public O\*NET/SOC/ESCO normalization.
- No public salary-inference layer.
- Supports India-specific location granularity (pincode).

**Medium confidence:**
- Historical depth bottoms at 2019 for aggregates; per-posting retention likely shorter.
- Volume is order-of-magnitude smaller than LinkUp/Coresignal at the live-index level.
- Source list is job boards + career pages + LinkedIn + on-demand crawl, not direct ATS API integration.

**Low confidence / unresolved gaps:**
- Exact per-posting retention window (90 days? 1 year? 2 years?).
- Whether Crustdata consumes Greenhouse's free JobBoardAPI and Lever public postings JSON. (Public docs are gated — login redirect at `docs.crustdata.com/docs/jobs`.)
- Salary-coverage percentage by geography.
- Per-posting deduplication-pipeline specifics and across-source merge behavior.
- Total monthly postings indexed.

**The docs.crustdata.com/docs/jobs page 307-redirects to a login** — full public API reference is gated. The research above reconstructs the picture from crustdata.com marketing pages, the competitor-comparison blog, third-party MCP wrappers (Composio, Merge), and HN activity.

---

## Non-obvious Products Enabled By This Job Data

Only a real-time, entity-linked, webhook-pushed job-posting feed — specifically Crustdata's shape — unlocks these:

1. **Competitor-expansion early-warning radar for VCs.** Fire a webhook the moment a tracked portfolio company's competitor opens its first role in Bengaluru / São Paulo / Warsaw. The investor gets 4–8 weeks of warning before a press release announces the market-entry strategy. Not possible with daily batch feeds — the early entrant moves faster than your refresh cycle. The `first-person-hired-internationally` trigger is the native primitive.

2. **Stealth-company founder-tracking for recruiters and seed funds.** Crustdata already markets the signal chain (Founder-title change + no-next-role departure + "Founding Engineer" posting on a fresh domain). Productize it as a daily feed of "people probably starting a company in the next 90 days" ordered by pedigree and vertical — this is a list you cannot build from LinkedIn alone, and cannot build batch. It requires the domain-registration-cross-reference + job-posting-anonymized-company-name + LinkedIn-change fan-out that Crustdata's entity graph already performs.

3. **GTM-shift detection for sales competitive intelligence.** When a competitor posts "VP Enterprise Sales" after 3 years of only posting "Founding AE," that is a go-up-market signal measurable weeks before it shows up in traffic, pricing, or LinkedIn positioning changes. Track the *seniority delta* in new postings per function, per company, as a first-derivative time series. No O\*NET taxonomy needed — just entity-linked reposts-of-title deltas. Existing tools surface job counts; nobody surfaces title-seniority curvature.

4. **Customer acquisition cost forecasting for B2B sales automation.** Tie company-level `Job Listing Growth By Function` (Eng + Product + Design acceleration) to future buying-committee size and budget-cycle timing. The company that grew eng hiring 3x in Q1 will have a bigger software budget in Q3. This is a regression on already-exposed Crustdata data that AI SDR tooling (Clay, Apollo, Outreach) does not currently surface as a first-class buying-intent score — Crustdata's Watcher + aggregates makes it one webhook-handler away.

5. **Labor-arbitrage radar for remote-first engineering orgs.** Cross-reference `workplace_type=remote` postings × `location=LatAm/India/EU` × salary-when-public × seniority. Surface the exact corridor (SF-based eng leadership building a remote LatAm team for $80k-120k full-stack engineers) as a ranked feed. Not feasible from LinkedIn (salary mostly missing) and not feasible from US-salary-transparency-law-constrained feeds alone — requires the career-page fallback path that Crustdata's websearch API provides, because the most informative postings are on company career pages that deliberately disclose salary to signal seriousness.

---

## Sources cited

- [crustdata.com/apis/job-listing](https://crustdata.com/apis/job-listing) — field schema, 30+ datapoints, 35 filters.
- [crustdata.com/blog/best-apis-for-job-posting-data](https://crustdata.com/blog/best-apis-for-job-posting-data) — Top-8 comparison table, Crustdata self-description.
- [crustdata.com/blog/how-to-find-old-job-postings](https://crustdata.com/blog/how-to-find-old-job-postings) — historical-depth positioning (real-time vs archive).
- [crustdata.com/apis/watcher](https://crustdata.com/apis/watcher) — job-posting trigger types.
- [crustdata.com/blog/the-complete-guide-to-tracking-and-finding-stealth-startup-founders](https://crustdata.com/blog/the-complete-guide-to-tracking-and-finding-stealth-startup-founders) — stealth-mode detection product.
- [crustdata.com/vs/coresignal-alternative](https://crustdata.com/vs/coresignal-alternative) — real-time-vs-monthly positioning.
- [docs.crustdata.com/docs/dictionary/company](https://docs.crustdata.com/docs/dictionary/company/) — `job_openings`, `Total Job Listings`, `Job Listing Growth By Function` fields.
- [docs.crustdata.com/docs/discover/company-data-api](https://docs.crustdata.com/docs/discover/company-data-api/) — Company Data API endpoints.
- [docs.crustdata.com/docs/jobs](https://docs.crustdata.com/docs/jobs) — gated (307 → login).
- [docs.merge.dev/merge-agent-handler/connectors/crustdata](https://docs.merge.dev/merge-agent-handler/connectors/crustdata) — `search_job_listings` tool signature (company_name, company_id, title, location, date_posted, url, seniority).
- [mcp.composio.dev/crustdata](https://mcp.composio.dev/crustdata) — Composio MCP wrapper tool list.
- [news.ycombinator.com/item?id=47146819](https://news.ycombinator.com/item?id=47146819) — 2026-02-25 Show HN on entity-linked web search.
- [coresignal.com/coresignal-vs-crustdata](https://coresignal.com/coresignal-vs-crustdata/) — competitor claim of Crustdata "monthly updates, 30-60s API."
- [coresignal.com/alternative-data/job-postings-data](https://coresignal.com/alternative-data/job-postings-data/) — Coresignal 461M+ benchmark.
- [www.reveliolabs.com/job-postings-cosmos](https://www.reveliolabs.com/job-postings-cosmos/) — Revelio 4.1B postings / 6.6M companies / 195 countries / 440k company sites.
- [www.linkup.com/products/raw](https://www.linkup.com/products/raw) — LinkUp Raw spec (403 on direct fetch; referenced via third-party summaries).
- [www.paycor.com/resource-center/articles/pay-transparency-laws-by-state](https://www.paycor.com/resource-center/articles/pay-transparency-laws-by-state/) — US 17 states + DC pay-transparency status.
- [ogletree.com/insights-resources/blog-posts/the-june-2026-eu-pay-transparency-directive-implementation-deadline-looms](https://ogletree.com/insights-resources/blog-posts/the-june-2026-eu-pay-transparency-directive-implementation-deadline-looms/) — EU directive 2023/970 deadline 2026-06-07.
- [www.onetcenter.org/taxonomy.html](https://www.onetcenter.org/taxonomy.html) — O\*NET-SOC 2019 (1,016 titles / 923 data-level / 4-level hierarchy).
