# Crustdata API — Flat Endpoint Inventory

**Agent 01 | Wave 1 | 2026-04-19**

## Scope & Methodology

The Crustdata documentation lives in two distinct, partially overlapping surfaces:

1. **Current docs at `docs.crustdata.com`** (Mintlify site, api.crustdata.com base URL, `2025-11-01` API version, Bearer-token auth) — publicly readable for the 10 canonical endpoints in its API Reference sidebar. Additional enterprise-only live endpoints are named on the Introduction, Rate Limits, and Pricing pages but have no dedicated reference pages (they require `Book a demo`).
2. **Legacy docs at `docs.crustdata.com/docs/*`** — now **gated behind `/login`**. Recovered via `web.archive.org` captures (Sept 2025 – Jan 2026) and cross-referenced against the public-facing product pages at `crustdata.com/apis/*`, the Composio MCP toolkit spec (14 tools), and third-party blog posts. These endpoints use the `api.crustdata.com/screener/*` and `api.crustdata.com/data_lab/*` paths, and use `Authorization: Token $token` (not Bearer). Most remain live — probing api.crustdata.com returned 401 (auth required, i.e. endpoints exist) rather than 404.

There is **no publicly exposed OpenAPI/Swagger JSON**. Tested `api.crustdata.com/{openapi.json, openapi.yaml, swagger.json, swagger.yaml, docs/openapi.json, v1/openapi.json, api-docs, redoc}` — all return 404. `docs.crustdata.com/openapi.json` redirects to login.

All pages cached under `/home/akash/PROJECTS/crustdata/research/cache/`.

---

## Global conventions

| Aspect | Current API (`2025-11-01`) | Legacy API (`/screener/*`, `/data_lab/*`) |
|---|---|---|
| Base URL | `https://api.crustdata.com` | `https://api.crustdata.com` |
| Auth header | `Authorization: Bearer YOUR_API_KEY` | `Authorization: Token $token` |
| Version header | `x-api-version: 2025-11-01` (required) | None |
| Content-Type | `application/json` | `application/json` |
| Default rate-limit | 15 requests/minute per endpoint (email `gtm@crustdata.co` to raise) | Same 15 req/min baseline (documented) |
| Status codes | 200 / 400 / 401 / 403 / 404 / 500 | 200 / 400 / 401 / 402 (payment) / 500 |
| Pagination | Cursor (`cursor` ↔ `next_cursor`) on newer endpoints | Offset / page (`offset`+`count`, or `page`) |
| Credits expiry | 6 months from purchase | — |
| Error body | `{ "error": "...", "description": "..." }` (Person API uses `reason` instead of `description`) | `{"error": "Failed to parse filters"}` style |

---

## CATEGORY 1 — Company APIs (current, v2025-11-01)

### 1.1 `POST /company/search` — Search Companies

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/company/search` |
| Auth | Bearer token + `x-api-version` |
| Pricing | 0.03 credits per result returned |
| Rate limit | 15 req/min |
| Pagination | Cursor-based. Pass `next_cursor` → `cursor`. `null` = last page |
| Refresh cadence | Indexed dataset (Crustdata-maintained). Timeseries fields (headcount, followers, etc.) are refreshed continuously; growth metrics anchored by `metadata.growth_calculation_date`. |

**Request body**
| Parameter | Type | Req | Default | Description |
|---|---|---|---|---|
| `filters` | object | No | — | `SearchCondition` or nested `{op: "and"|"or", conditions: [...]}`. Omit → match all |
| `filters.field` | string | Y | — | Dot-path indexed field (see searchable fields below) |
| `filters.type` | enum | Y | — | `=, !=, <, =<, >, =>, in, not_in, contains, not_contains, is_null, is_not_null, (.), [.]` — note `>=` and `<=` are **not** supported; use `=>` and `=<` |
| `filters.value` | any | Y | — | Depends on operator |
| `cursor` | string | No | — | Opaque page cursor |
| `limit` | int | No | 20 | 1..1000 |
| `sorts[]` | array | No | — | `{column: dotpath, order: asc|desc}` |
| `fields[]` | string[] | No | all | Dot-paths or top-level groups |

**Searchable fields (indexed)**: `crustdata_company_id`, `updated_at`, `indexed_at`, `metadata.growth_calculation_date`, `basic_info.{company_id, name, primary_domain, website, professional_network_url, professional_network_id, company_type, year_founded, employee_count_range, markets, industries}`, `revenue.estimated.{lower_bound_usd, upper_bound_usd}`, `revenue.acquisition_status`, `funding.{total_investment_usd, last_round_amount_usd, last_fundraise_date, last_round_type, investors, tracxn_investors}`, `headcount.total`, `roles.distribution.*` (accounting, administrative, arts_and_design, business_development, community_and_social_services, consulting, customer_success_and_support, education, engineering, entrepreneurship, finance, healthcare_services, human_resources, information_technology, legal, marketing, media_and_communication, military_and_protective_services, operations, product_management, program_and_project_management, purchasing, quality_assurance, real_estate, research, sales, support), `roles.growth_6m`, `roles.growth_yoy`, `locations.{country, state, city, headquarters, hq_country, largest_headcount_country}`, `headcount.largest_headcount_country`, `taxonomy.{professional_network_industry, categories}`, `followers.{count, mom_percent, qoq_percent, six_months_growth_percent, yoy_percent}`, `competitors.{company_ids, websites}`.

**Response (200)**
```
{ companies: [ { crustdata_company_id, basic_info, headcount, revenue, funding,
                 hiring, locations, social_profiles, taxonomy, followers,
                 software_reviews, metadata } ],
  next_cursor: string|null, total_count: integer|null, query: object }
```
Notes: `news`, `people`, `web_traffic`, `employee_reviews` are NOT indexed for search — they return empty in `/company/search` and must be fetched via `/company/enrich`.

---

### 1.2 `POST /company/identify` — Identify Companies

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/company/identify` |
| Auth | Bearer + `x-api-version` |
| Pricing | **Free** |
| Rate limit | 15 req/min |

**Body** — exactly one of:
`names: string[]`, `domains: string[]`, `crustdata_company_ids: integer[]`, `professional_network_profile_urls: string[]`.
Optional: `fields: string[]`, `exact_match: boolean|null` (null = auto).

**Response (200)** — top-level array (OpenAPI spec also declares `results` wrapper; both shapes accepted):
```
[{ matched_on, match_type: "name"|"domain"|"crustdata_company_id"|"professional_network_profile_url",
   matches: [{ confidence_score, company_data: { crustdata_company_id, basic_info:
     { name, primary_domain, all_domains, website, professional_network_url,
       professional_network_id, profile_name, logo_permalink, description,
       company_type, year_founded, employee_count_range, markets, industries }}]}]
```

---

### 1.3 `POST /company/enrich` — Enrich Companies

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/company/enrich` |
| Auth | Bearer + `x-api-version` |
| Pricing | 2 credits per record |
| Rate limit | 15 req/min |
| No-match | 200 with empty `matches: []` (OpenAPI spec also documents 404 — handle both) |

**Body** — exactly one of `names[]`, `domains[]`, `crustdata_company_ids[]`, `professional_network_profile_urls[]`; plus optional `fields[]`, `exact_match`.

**Valid `fields` groups**: `basic_info`, `revenue`, `headcount`, `funding`, `hiring`, `web_traffic`, `seo`, `competitors`, `employee_reviews`, `people`, `locations`, `taxonomy`, `followers`, `news`, `software_reviews`, `social_profiles`, `status`.

**Response** — same wrapper as identify, but `company_data` is the full enriched profile:
- `basic_info` — name, primary_domain, all_domains, website, profile_name, logo, description, company_type, year_founded, employee_count_range, markets, industries, professional_network_url, professional_network_id
- `headcount` — total, by_role_absolute, by_role_percent, by_region_absolute, growth_percent
- `funding` — total_investment_usd, last_round_amount_usd, last_fundraise_date, last_round_type, investors
- `revenue` — estimated.{lower_bound_usd, upper_bound_usd}, public_markets, acquisition_status
- `locations` — hq_country, hq_state, hq_city, headquarters
- `taxonomy` — professional_network_industry, professional_network_specialities, categories
- `hiring` — openings_count, openings_growth_percent, recent_titles_csv, by_function_qoq_pct, by_function_6m_pct
- `followers` — count, mom_percent, qoq_percent, yoy_percent
- `seo` — total_organic_results, monthly_organic_clicks, monthly_google_ads_budget
- `competitors` — company_ids, websites
- `social_profiles` — crunchbase, twitter_url
- `web_traffic` — domain_traffic.monthly_visitors and traffic sources
- `employee_reviews` — overall_rating, culture_and_values_rating, work_life_balance_rating, review_count
- `people` — decision_makers, founders, cxos
- `news` — article_url, article_title, article_publish_date
- `software_reviews` — review_count, average_rating
- `status` — state (`enriching`, `not_found`)

Data freshness: enriched fields come from the indexed Crustdata dataset (no explicit cadence stated; individual records show `last_updated_date`).

---

### 1.4 `POST /company/search/autocomplete` — Company Autocomplete

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/company/search/autocomplete` |
| Auth | Bearer + `x-api-version` |
| Pricing | **Free** |
| Rate limit | 15 req/min |

**Body**: `field` (required string, allowlisted), `query` (required; empty = top by frequency), `limit` (1..100, default 20), optional `filters` object `{field, type, value}` (operator set: `=, !=, <, =<, >, =>, in, not_in, contains`).

**Allowlisted fields**: `basic_info.{name, primary_domain, website, professional_network_url, professional_network_id, company_type, year_founded, employee_count_range, markets, industries}`, `revenue.estimated.{lower_bound_usd, upper_bound_usd}`, `revenue.acquisition_status`, `funding.{total_investment_usd, last_round_type, last_fundraise_date, investors}`, `headcount.{latest_count, largest_headcount_country}`, `locations.{country, state, city}`, `taxonomy.{professional_network_industry, professional_network_specialities, categories}`, `followers.latest_count`, `social_profiles.crunchbase.url`, `social_profiles.twitter_url`.

**Response (200)**: `{ suggestions: [{ value: string }] }`.

---

### 1.5 `POST /company/professional_network/search/live` — Live Company Search (🔒 enterprise)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/company/professional_network/search/live` |
| Auth | Bearer + `x-api-version` — plan-gated, book a demo |
| Pricing | 2 credits per company |
| Rate limit | 15 req/min |
| Freshness | Real-time — fetched from the professional network at request time |

Named on the API Introduction table and on the Rate Limits / Pricing pages, but no dedicated public reference page. Use the same company search semantics; the response is fetched live rather than from the indexed dataset.

---

## CATEGORY 2 — Person APIs (current, v2025-11-01)

### 2.1 `POST /person/search` — Search People

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/person/search` |
| Auth | Bearer + `x-api-version` |
| Pricing | 0.03 credits per result |
| Rate limit | 15 req/min |
| Pagination | Cursor. `limit` default 20, 1..1000 (alias `count`) |

**Request body**
| Param | Type | Req | Description |
|---|---|---|---|
| `filters` | object | Y | PersonSearchCondition or nested and/or group |
| `filters.field` | string | Y | See list below |
| `filters.type` | enum | Y | `=, !=, <, =<, >, =>, in, not_in, (.), [.], geo_distance` |
| `filters.value` | any | Y | For `(.)` supports `|` for OR; `[.]` = substring; `geo_distance` value = `{location, distance, unit: km|mi|miles|m|ft}` |
| `sorts[]` | array | No | `{field, order: asc|desc}` |
| `limit` / `count` | int | No | 1..1000, default 20 |
| `cursor` | string | No | |
| `post_processing` | object | No | `{exclude_profiles[], exclude_names[]}` |
| `return_query` | bool | No | Debug flag |
| `preview` | bool | No | Basic-fields fast path |

**Searchable fields** (hundreds): `crustdata_person_id`, `basic_profile.{name, first_name, last_name, headline, summary, languages, last_updated, location.{full_location, city, state, country, continent}}`, `professional_network.{connections, open_to_cards, location.raw}`, `skills.professional_network_skills`, `experience.employment_details.{company_name, company_id, title, description, location, start_date, end_date, seniority_level, function_category, company_website_domain, company_headcount_latest, company_headcount_range, company_industries, company_professional_network_industry, company_type, company_headquarters_country, company_hq_location, years_at_company_raw, business_email_verified}`, full `experience.employment_details.current.*` and `experience.employment_details.past.*` mirrors, `education.schools.{school, degree, field_of_study}`, `certifications.{name, issue_date, expiration_date, credential_url, issuing_organization, credential_id}`, `honors.title`, `social_handles.twitter_handle`, `recently_changed_jobs`, `years_of_experience_raw`, `metadata.{last_scraped_source, updated_at}`.

**Sortable fields**: `crustdata_person_id`, `basic_profile.name`, `basic_profile.location.*`, `professional_network.connections`, `experience.employment_details.{start_date, company_id}`, `metadata.updated_at`.

**Response (200)**: `{ profiles: [...person], next_cursor: string|null, total_count: integer|null }`.

---

### 2.2 `POST /person/enrich` — Enrich People (cached)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/person/enrich` |
| Auth | Bearer + `x-api-version` |
| Pricing | **Additive:** 1 (base) + 2 (personal email) + 2 (phone) + 1 (business email) + 1 (dev platform) — max 7 |
| Rate limit | 15 req/min |
| Batch | Max **25 profiles** per request |
| No-match | 200 with empty `matches: []` (spec also declares 404) |

**Body** — exactly one of:
- `professional_network_profile_urls: string[]` (max 25)
- `business_emails: string[]` (reverse lookup)

Optional: `fields[]` (basic_profile, professional_network, skills, contact, social_handles, experience, education, certifications, honors, dev_platform_profiles), `min_similarity_score` (0..1 for email match), `preview` (basic-profile only, 0 credits; cannot combine with `enrich_realtime`).

**Response (200)** — top-level array:
```
[{ matched_on, match_type: "professional_network_profile_url"|"business_email",
   matches: [{ confidence_score, person_data: { basic_profile, experience,
     education, certifications, honors, skills, contact, social_handles,
     professional_network, dev_platform_profiles, metadata }}]}]
```

---

### 2.3 `POST /person/professional_network/enrich/live` — Live Person Enrich (🔒 enterprise)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/person/professional_network/enrich/live` |
| Auth | Bearer + `x-api-version` |
| Pricing | 7 credits per profile |
| Rate limit | 15 req/min |
| Freshness | **Live** — fetches fresh profile data from the web at request time |
| Body / response | Same shape as `/person/enrich` |

---

### 2.4 `POST /person/professional_network/search/live` — Live Person Search (🔒 enterprise)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/person/professional_network/search/live` |
| Auth | Bearer + `x-api-version` |
| Pricing | 2 credits per profile |
| Rate limit | 15 req/min |
| Freshness | **Live** |
| Body / response | Same filter shape as `/person/search`; results sourced live from the web |

---

### 2.5 `POST /person/search/autocomplete` — Person Autocomplete

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/person/search/autocomplete` |
| Auth | Bearer + `x-api-version` |
| Pricing | **Free** |
| Rate limit | 15 req/min |

**Body**: `field` (allowlisted), `query`, `limit` (1..100, default 20), optional `filters` object (same operator set as company autocomplete).

**Allowlisted fields**: `basic_profile.{name, headline, languages, location.raw/.city/.state/.country/.continent}`, `professional_network.location.*`, `skills.professional_network_skills`, `experience.employment_details.current.{name, title, seniority_level, function_category, company_industries, company_type, company_hq_location, company_website_domain}`, `experience.employment_details.past.{name, title}`, `education.schools.{school, degree, field_of_study}`, `certifications.{name, issuing_organization}`, `honors.title`, `social_handles.twitter_identifier.slug`.

Sending an unsupported field returns 400 with the full allowlist in the error message.

**Response**: `{ suggestions: [{ value }] }`.

---

## CATEGORY 3 — Web APIs (current, v2025-11-01)

### 3.1 `POST /web/search/live` — Web Search

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/web/search/live` |
| Auth | Bearer + `x-api-version` (enum, must equal `2025-11-01`) |
| Pricing | 1 credit per query (self-serve + enterprise) |
| Rate limit | 15 req/min |
| Freshness | **Live SERP** — fetched at request time |

**Body**:
| Param | Type | Req | Default | Description |
|---|---|---|---|---|
| `query` | string | Y | — | 1..5000 chars, supports `site:`, `filetype:` operators |
| `location` | string\|null | No | — | ISO 3166-1 alpha-2 (US, CA, MX, BR, AR, CL, CO, PE, VE, GB, DE, FR, IT, ES, PT, NL, BE, CH, AT, PL, SE, NO, DK, FI, IE, RU, UA, CZ, GR, TR, RO, HU, JP, CN, KR, IN, ID, TH, VN, MY, SG, PH, TW, HK, SA, AE, IL, EG, AU, NZ, ZA, NG, KE) |
| `sources[]` | enum[] | No | all | `news, web, scholar-articles, scholar-articles-enriched, scholar-author, ai, social` |
| `site` | string\|null | No | — | Restrict to a domain (max 500 chars) |
| `start_date` | int\|null | No | — | Unix seconds |
| `end_date` | int\|null | No | — | Unix seconds |
| `human_mode` | bool | No | false | Attempt Cloudflare bypass |
| `page` | int | No | 1 | ≥1 |

**Response**:
```
{ success: bool, query, timestamp (ms),
  results: [{ source, title, url, snippet, position,
              metadata, pdf_url, authors, citations,       // scholar-articles
              name, affiliation, website, interests,
              thumbnail, h_index, i10_index, articles,     // scholar-author
              content, references, images                   // ai overview
            }],
  metadata: { totalResults, failedPages, emptyPages } }
```

---

### 3.2 `POST /web/enrich/live` — Web Fetch

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/web/enrich/live` |
| Auth | Bearer + `x-api-version` |
| Pricing | 1 credit per page |
| Rate limit | 15 req/min |
| Batch | Max **10 URLs** per request |

**Body**: `urls: string[]` (1..10, each must start with http:// or https://, max 2000 chars), `human_mode: bool` (default false).

**Response** — array of `{ success, url, timestamp (sec), title, content (raw HTML) }`. Failed URLs carry null fields.

---

## CATEGORY 4 — Jobs API (current, v2025-11-01)

### 4.1 `POST /job/search` — Search Jobs

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/job/search` |
| Auth | Bearer + `x-api-version` |
| Pricing | 0.03 credits per result |
| Rate limit | 15 req/min |
| Pagination | Cursor-based |
| Freshness | Indexed job dataset; each listing exposes `metadata.date_added` and `metadata.updated_at` |

**Request body**:
| Param | Type | Req | Default | Description |
|---|---|---|---|---|
| `filters` | object | No | — | Condition or and/or group, same grammar as `/company/search` |
| `cursor` | string | No | — | |
| `limit` | int | No | 20 | 0..1000 — set 0 for aggregations-only |
| `sorts[]` | array | No | — | `{column, order}` |
| `fields[]` | string[] | No | all | Dot-paths. Top-level groups: `crustdata_job_id, job_details, company, location, content, metadata` |
| `aggregations[]` | array | No | — | `{type: "count"|"group_by", column, agg: "count", size}` |

**Common filter fields**: `company.basic_info.{company_id, name, primary_domain}`, `job_details.{title, url, category, openings}`, `location.{country, state, city, raw}`, `metadata.{date_added, updated_at}`.

**Response**:
```
{ job_listings: [{ crustdata_job_id, job_details:{title,url,category,openings,description,...},
                   company:{basic_info,headcount,followers,revenue,funding,competitors,...},
                   location:{country,state,city,raw},
                   content:"full description",
                   metadata:{date_added, updated_at} }],
  next_cursor: string|null,
  total_count: integer|null,
  aggregations: [{type, column, value}]  // only if requested
}
```

---

### 4.2 `POST /job/professional_network/search/live` — Live Job Search (🔒 enterprise)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/job/professional_network/search/live` |
| Auth | Bearer + `x-api-version` |
| Pricing | 2 credits per result |
| Rate limit | 15 req/min |
| Freshness | **Live** — fresh live job search for a single company |

Named on Rate Limits page and Pricing page. Use case: "track companies building early teams or launching new departments" (product page). No public reference page.

---

## CATEGORY 5 — Shared autocomplete (current, v2025-11-01)

### 5.1 `POST /professional_network/search/autocomplete` — Shared Live-Search Autocomplete (🔒 enterprise)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/professional_network/search/autocomplete` |
| Auth | Bearer + `x-api-version` |
| Pricing | **Free** (when enabled for the account) |
| Rate limit | 15 req/min |
| Availability | Enterprise-only / plan-gated |

Listed on the Pricing page and Rate Limits page as "Shared live-search autocomplete when enabled for your account." No public reference page.

---

## CATEGORY 6 — Enterprise extensions (current, v2025-11-01)

These endpoints are listed in the public **Rate Limits** table but have no documented request/response schemas in the public site — implied to be enterprise-only extensions to the Person and Social surfaces.

### 6.1 `POST /dev_platform/enrich` — Developer Platform Enrich

- Full URL: `POST https://api.crustdata.com/dev_platform/enrich`
- Rate limit: 15 req/min (Rate Limits page)
- Scope: Returns developer-platform data (profile, repos, orgs, activity). Also surfaces inside `/person/enrich` as the `dev_platform_profiles` group (+1 credit add-on when requested via `/person/enrich` fields).

### 6.2 `POST /employee_review/enrich` — Employee Review Enrich

- Full URL: `POST https://api.crustdata.com/employee_review/enrich`
- Rate limit: 15 req/min
- Scope: Standalone access to employee review data (overall_rating, culture_and_values_rating, work_life_balance_rating, review_count). Also accessible as an `employee_reviews` group inside `/company/enrich`.

### 6.3 `POST /social_post/professional_network/enrich/live` — Social Post Enrich (Live)

- Full URL: `POST https://api.crustdata.com/social_post/professional_network/enrich/live`
- Rate limit: 15 req/min
- Freshness: Live — fetched at request time
- Scope: Enrich a specific social post (LinkedIn) — engagement metrics, commenter profiles.

### 6.4 `POST /social_post/professional_network/search/live` — Social Post Search (Live)

- Full URL: `POST https://api.crustdata.com/social_post/professional_network/search/live`
- Rate limit: 15 req/min
- Freshness: Live
- Scope: Search LinkedIn posts by keyword / by person / by company. Maps to the public "Posts API" product page and to Composio's `CRUSTDATA_SEARCH_LINKED_IN_POSTS_BY_KEYWORD` + `CRUSTDATA_RETRIEVE_LINKED_IN_POSTS` tools (see Category 8).

---

## CATEGORY 7 — Legacy Screener API (`/screener/*`) — still live

Probed each with `curl` at `api.crustdata.com`: they return 401 (auth required) rather than 404, confirming they are still routable. Legacy uses `Authorization: Token $token` (not Bearer), returns up to 25 results per page, uses `page` integer pagination on the filter-based endpoints.

### 7.1 `GET /screener/company` — Company Enrichment (legacy)

| | |
|---|---|
| Full URL | `GET https://api.crustdata.com/screener/company?company_domain={domain}[,domain2,...]` |
| Auth | `Authorization: Token $token` |
| Params (query-string) | `company_domain` (comma-separated), `fields` (comma-separated dot-paths; e.g. `company_name,headcount.headcount,job_openings,news_articles`), `enrich_realtime=True` (force live enrichment within ~10 minutes for companies not yet tracked) |
| Freshness | Cached by default; `enrich_realtime=True` forces live scrape (real-time enrich). |

### 7.2 `POST /screener/screen/` — Company Discovery / Screening

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/screener/screen/` |
| Auth | Token |
| Body | `{ filters: {op: "and"|"or", conditions: [{column, type, value, allow_null}]}, hidden_columns: [], offset: int, count: int (default 150), sorts: [] }` |
| Operators | `=, !=, <, =<, >, =>, in, not_in, (.), [.]` etc. |
| Columns (sample) | `total_investment_usd, headcount, largest_headcount_country, company_website_domain, employee_skills_31_to_50_pct, num_of_impressions_qoq_growth, num_of_impressions_yoy_growth, followers, followers_mom_growth, followers_qoq_growth, followers_yoy_growth, job_openings_<function>_qoq_pct, job_openings_<function>_six_months_growth_pct`, plus all firmographics in the Company Data Dictionary |

### 7.3 `POST /screener/company/search` — Realtime Company Search (filter-type DSL)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/screener/company/search` |
| Auth | Bearer (legacy blog) / Token |
| Body | `{ filters: [{filter_type, type, value, sub_filter?}], page: int }` |
| `filter_type` values | `COMPANY_HEADCOUNT, REGION, INDUSTRY, NUM_OF_FOLLOWERS, FORTUNE, ACCOUNT_ACTIVITIES, JOB_OPPORTUNITIES, COMPANY_HEADCOUNT_GROWTH, ANNUAL_REVENUE, DEPARTMENT_HEADCOUNT, DEPARTMENT_HEADCOUNT_GROWTH, KEYWORD, IN_THE_NEWS` |
| Freshness | Real-time — "checks the internet in real time" at request time |
| Pagination | 25 per page via `page` integer |
| Response | `{ companies: [...], total_display_count: int }` |

### 7.4 `POST /screener/person/search` — Realtime People Search (filter-type DSL)

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/screener/person/search` |
| Auth | Bearer / Token |
| Body | `{ filters: [{filter_type, type, value}], page: int }` |
| `filter_type` values | `CURRENT_COMPANY, CURRENT_TITLE, PAST_TITLE, PAST_COMPANY, COMPANY_HEADQUARTERS, COMPANY_HEADCOUNT, REGION, INDUSTRY, PROFILE_LANGUAGE, SENIORITY_LEVEL, YEARS_AT_CURRENT_COMPANY, YEARS_IN_CURRENT_POSITION, YEARS_OF_EXPERIENCE, FIRST_NAME, LAST_NAME, FUNCTION, COMPANY_TYPE, POSTED_ON_SOCIAL_MEDIA, RECENTLY_CHANGED_JOBS, IN_THE_NEWS, KEYWORD` |
| Freshness | Real-time (crawls on demand); job changes appear "within hours, not weeks" |
| Pagination | 25 per page |
| Response | `{ profiles: [...], total_display_count: string\|int }` |

### 7.5 `POST /screener/persondb/search/` — In-Database People Search

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/screener/persondb/search/` |
| Auth | Token |
| Body | `{ filters: {op,conditions}, limit (e.g. 50), post_processing: {exclude_profiles: string[] (up to 50,000 URLs), exclude_names: string[]} }` |
| Operators | Column-based (`=>, =, =<`), matches the persondb data dictionary |
| Freshness | **Refreshed every 30 days** (per Crustdata blog) |

### 7.6 `GET /screener/person/enrich` — Person Enrichment (legacy)

| | |
|---|---|
| Full URL | `GET https://api.crustdata.com/screener/person/enrich?linkedin_profile_url={url1},{url2}` |
| Auth | Token |
| Params | `linkedin_profile_url` (comma-separated, multi-profile), `business_email`, `fields` (comma-separated), `enrich_realtime: True|False` |
| Freshness | "Auto-enrichment for unfound profiles within 30-60 minutes"; retry ≥60 min after first miss |

### 7.7 `GET /screener/social_posts` — Social Posts by Person

| | |
|---|---|
| Full URL | `GET https://api.crustdata.com/screener/social_posts?person_linkedin_url={url}&page={n}` |
| Auth | Token |
| Params | `person_linkedin_url` or `company_linkedin_url`, `page` (starts at 1) |
| Limits | 20 results per page; pagination via `page` |
| Latency | 30–60 seconds per request (real-time fetch; depends on reaction counts) |
| Freshness | Live (real-time scrape) |

### 7.8 `POST /screener/web-search` — Legacy Web Search

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/screener/web-search` (also accepts `?fetch_content=true`) |
| Auth | Token |
| Body | `{ query, geolocation, sources: [news, web, scholar-articles, scholar-articles-enriched, scholar-author], site, startDate, endDate }` |
| Pricing (legacy doc) | 1 credit per search; Free tier = 5 total credits, Pro = 50/mo, Enterprise = unlimited |
| Rate limit | 15 req/min (standard credit-based limiting) |
| Pagination | Not supported in legacy (single page per search) |

### 7.9 `POST /screener/web-fetch` — Legacy Web Fetch

| | |
|---|---|
| Full URL | `POST https://api.crustdata.com/screener/web-fetch` |
| Auth | Token |
| Body | `{ urls: string[] }` (max 10 URLs, must include protocol) |
| Errors | 402 Payment Required on insufficient credits |

---

## CATEGORY 8 — Data Lab Timeseries Endpoints (`/data_lab/*`)

Exposed through the Crustdata / Composio MCP toolkit. Probed → 401 (exist, auth required). All support `count` + `offset` pagination, `sorts[]`, and a nested `filters.{op, conditions}` structure (same DSL as `/screener/screen/`).

### 8.1 `POST /data_lab/headcount_by_facet/` — Headcount by Facet Timeseries

- Full URL: `POST https://api.crustdata.com/data_lab/headcount_by_facet/`
- Composio tool: `CRUSTDATA_FETCH_HEADCOUNT_BY_FACET_TIMESERIES`
- Body: `{ count: int, offset: int, sorts: [...], filters: {op, conditions} }`
- Returns: headcount timeseries segmented by facets (role / region / seniority / etc.)
- Use-cases: HR analytics, workforce planning, organizational growth analysis

### 8.2 `POST /data_lab/headcount_timeseries/` — Headcount Timeseries

- Full URL: `POST https://api.crustdata.com/data_lab/headcount_timeseries/`
- Composio tool: `CRUSTDATA_POST_HEADCOUNT_TIMESERIES_DATA`
- Body: `{ count, offset, sorts, filters: {op, conditions} }`
- Returns: Historical total headcount over time, per company

### 8.3 `POST /data_lab/funding_milestone_timeseries/` — Funding Milestone Timeseries

- Full URL: `POST https://api.crustdata.com/data_lab/funding_milestone_timeseries/`
- Composio tool: `CRUSTDATA_POST_FUNDING_MILESTONE_TIME_SERIES_DATA`
- Body: `{ count, offset, sorts, filters: {op, conditions} }`
- Returns: Funding events over time per company; filter by stage, date range, company attributes

### 8.4 `POST /data_lab/job_listings/` — Job Listings Table

- Full URL: `POST https://api.crustdata.com/data_lab/job_listings/`
- Composio tool: `CRUSTDATA_POST_JOB_LISTINGS_TABLE_DATA`
- Body: `{ tickers: string[], dataset: {id?, name?}, count, offset, sorts, filters: {op, conditions} }`
- Returns: Filtered job listings per ticker; bulk retrieval for market research

### 8.5 `POST /data_lab/web_traffic/` — Web Traffic Data

- Full URL: `POST https://api.crustdata.com/data_lab/web_traffic/`
- Composio tool: `CRUSTDATA_POST_WEB_TRAFFIC_DATA`
- Body: `{ count, offset, sorts, filters: {op, conditions} }`
- Returns: Web traffic per domain over time (monthly_visitors, traffic sources)

### 8.6 `POST /data_lab/decision_makers/` — Decision Makers Filter

- Full URL: `POST https://api.crustdata.com/data_lab/decision_makers/`
- Composio tool: `CRUSTDATA_FILTER_DECISION_MAKERS_DATA`
- Body: `{ count, offset, sorts, filters: {op, conditions}, decision_maker_titles: string[] }`
- Returns: Decision maker profiles across organizations filtered by title + other criteria

### 8.7 `GET /data_lab/investor_portfolio/` — Investor Portfolio

- Full URL: `GET https://api.crustdata.com/data_lab/investor_portfolio/?investor_name={name}`
- Composio tool: `CRUSTDATA_FETCH_INVESTOR_PORTFOLIO_DATA`
- Params: `investor_name`
- Returns: Holdings, performance metrics for an investor
- Freshness: Not real-time — "frequency of updates should be verified in the API documentation" (Composio note)

### 8.8 `POST /data_lab/screen_data/` — Screen Metrics + Filters

- Full URL: `POST https://api.crustdata.com/data_lab/screen_data/`
- Composio tool: `CRUSTDATA_SCREEN_METRICS_AND_FILTER_CONDITIONS`
- Body: `{ metrics: [...], count, offset, sorts, filters: {op, conditions} }`
- Returns: Arbitrary metric screen with custom filter conditions

---

## CATEGORY 9 — Webhooks / Real-time streaming (Watcher API)

The **Watcher API** (`/apis/watcher` product page) is Crustdata's webhook-based push notification system. **Not documented with endpoint-level schemas on docs.crustdata.com; integration via sales.** No public request/response spec has been captured; Crustdata's comparison chart documents:

- Webhook support: "✅ Yes (for job changes & custom events)"
- Update latency: "Realtime" (vs. Coresignal's weekly / PDL's none)

**Watcher types documented**: Event Watchers (New funding announcement, Job posting with keyword & location, LinkedIn post with keywords, Someone starts a new job); Company Watchers (Company headcount increased, Company department headcount in range, First person hired in company department, First person hired internationally, Employee location in two countries, Company headcount growth over baseline); People Watchers.

Watcher trigger check cadence is not publicly specified. Setup and endpoint paths gated behind `Book a demo`.

---

## CATEGORY 10 — MCP / Third-party integrations

These are not additional endpoints — they are wrappers over the above — but they surface details not in the public docs:

- **Composio toolkit** (`composio.dev/toolkits/crustdata`, version `20260407_00`) exposes 14 MCP tools mapping to Categories 6, 7, 8 above. Confirmed tool list: `ENRICH_PERSON_SCREENER, FETCH_HEADCOUNT_BY_FACET_TIMESERIES, FETCH_INVESTOR_PORTFOLIO_DATA, FILTER_DECISION_MAKERS_DATA, POST_FUNDING_MILESTONE_TIME_SERIES_DATA, POST_HEADCOUNT_TIMESERIES_DATA, POST_JOB_LISTINGS_TABLE_DATA, POST_WEB_TRAFFIC_DATA, RETRIEVE_LINKED_IN_POSTS, SCREENER_COMPANY_INFORMATION, SCREEN_METRICS_AND_FILTER_CONDITIONS, SEARCH_COMPANIES_WITH_FILTERS, SEARCH_FOR_JOB_ID_IN_SCREENER, SEARCH_LINKED_IN_POSTS_BY_KEYWORD`.
- **Rube marketplace** (`rube.app/marketplace/crustdata`) redirects to Composio.
- **Native Crustdata MCP** is advertised in the site header ("Crustdata now works inside Claude — Give Claude real-time people and company data with MCP") — endpoint/config details not publicly documented.

---

## Summary — every endpoint at a glance

| # | Path | Method | Category | Pricing | Freshness | Access |
|---|---|---|---|---|---|---|
| 1 | `/company/search` | POST | Company (indexed) | 0.03/result | Indexed | Self-serve |
| 2 | `/company/identify` | POST | Company (indexed) | Free | Indexed | Self-serve |
| 3 | `/company/enrich` | POST | Company (indexed) | 2/record | Indexed | Self-serve |
| 4 | `/company/search/autocomplete` | POST | Company (indexed) | Free | Indexed | Self-serve |
| 5 | `/company/professional_network/search/live` | POST | Company (live) | 2/company | Live | 🔒 Enterprise |
| 6 | `/person/search` | POST | Person (indexed) | 0.03/result | Indexed | Self-serve |
| 7 | `/person/enrich` | POST | Person (indexed) | 1–7/record | Cached | Self-serve |
| 8 | `/person/professional_network/enrich/live` | POST | Person (live) | 7/profile | Live | 🔒 Enterprise |
| 9 | `/person/professional_network/search/live` | POST | Person (live) | 2/profile | Live | 🔒 Enterprise |
| 10 | `/person/search/autocomplete` | POST | Person (indexed) | Free | Indexed | Self-serve |
| 11 | `/web/search/live` | POST | Web (live) | 1/query | Live | Self-serve + Enterprise |
| 12 | `/web/enrich/live` | POST | Web (live) | 1/page | Live | Self-serve + Enterprise |
| 13 | `/job/search` | POST | Jobs (indexed) | 0.03/result | Indexed | Self-serve |
| 14 | `/job/professional_network/search/live` | POST | Jobs (live) | 2/result | Live | 🔒 Enterprise |
| 15 | `/professional_network/search/autocomplete` | POST | Shared | Free | — | 🔒 Enterprise |
| 16 | `/dev_platform/enrich` | POST | Dev data | — | — | Enterprise |
| 17 | `/employee_review/enrich` | POST | Reviews | — | — | Enterprise |
| 18 | `/social_post/professional_network/enrich/live` | POST | Social posts | — | Live | Enterprise |
| 19 | `/social_post/professional_network/search/live` | POST | Social posts | — | Live | Enterprise |
| 20 | `/screener/company` | GET | Company (legacy) | Credit-based | Cached or `enrich_realtime=True` | Legacy token |
| 21 | `/screener/screen/` | POST | Company discovery (legacy) | Credit-based | Indexed | Legacy token |
| 22 | `/screener/company/search` | POST | Company realtime (legacy) | Credit-based | Real-time SERP | Legacy token |
| 23 | `/screener/person/search` | POST | Person realtime (legacy) | Credit-based | Real-time | Legacy token |
| 24 | `/screener/persondb/search/` | POST | Person database (legacy) | Credit-based | Refreshed every 30 days | Legacy token |
| 25 | `/screener/person/enrich` | GET | Person enrich (legacy) | Credit-based | Auto-enrich 30-60 min | Legacy token |
| 26 | `/screener/social_posts` | GET | Social posts (legacy) | Credit-based | Real-time (30–60s latency) | Legacy token |
| 27 | `/screener/web-search` | POST | Web search (legacy) | 1 credit/search | Real-time | Legacy token |
| 28 | `/screener/web-fetch` | POST | Web fetch (legacy) | Credit-based | Real-time | Legacy token |
| 29 | `/data_lab/headcount_by_facet/` | POST | Data Lab | — | Timeseries | Enterprise |
| 30 | `/data_lab/headcount_timeseries/` | POST | Data Lab | — | Timeseries | Enterprise |
| 31 | `/data_lab/funding_milestone_timeseries/` | POST | Data Lab | — | Timeseries | Enterprise |
| 32 | `/data_lab/job_listings/` | POST | Data Lab | — | — | Enterprise |
| 33 | `/data_lab/web_traffic/` | POST | Data Lab | — | Timeseries | Enterprise |
| 34 | `/data_lab/decision_makers/` | POST | Data Lab | — | — | Enterprise |
| 35 | `/data_lab/investor_portfolio/` | GET | Data Lab | — | Not real-time | Enterprise |
| 36 | `/data_lab/screen_data/` | POST | Data Lab | — | — | Enterprise |
| — | Watcher webhook system | webhook | Real-time | — | Real-time push | 🔒 Book a demo |

**Totals**: 15 current (v2025-11-01) endpoints confirmed (10 publicly documented + 5 enterprise-only named on rate-limits / pricing / intro), 4 enterprise extension endpoints from rate-limits table, 9 legacy `/screener/*` endpoints, 8 `/data_lab/*` timeseries endpoints, 1 Watcher webhook system. **Grand total: 36 distinct HTTP endpoint paths + webhook push channel.**

---

## Key gaps / gated material

1. The `/openapi-specs/2025-11-01/introduction` page lists 12 public endpoints; my crawl adds `/job/search` (not counted in that page's Company/Person/Web totals) plus the enterprise-gated live endpoints for a total of 15 current-API endpoints.
2. `/docs/*` URLs (legacy docs) redirect to `/login`. Schemas recovered via `web.archive.org` captures from 2025-09 through 2026-01.
3. `/api` and `/openapi.json` on docs.crustdata.com redirect to `/login`. No public machine-readable spec exists.
4. `api.crustdata.com/openapi.json` (and `/swagger.json`, `/swagger.yaml`, `/v1/openapi.json`, `/api-docs`, `/redoc`) all return 404 — no self-hosted OpenAPI.
5. The **Watcher API** has no public endpoint-level schema; only the Watcher-type catalog (event / company / people) is published.
6. The legacy Company Search via Filters blog reveals an **in-database company search** alternative with cursor-based pagination (separate from the `filter_type` DSL's page-based pagination), but its distinct endpoint path is not explicitly named — it may be `/screener/screen/` used in a different mode.
7. Pricing for enterprise-only endpoints (dev_platform, employee_review, social_post enrich/search, data_lab) is quote-based; no public credit cost.
8. The `/screener/persondb/` refresh cadence ("every 30 days") is stated only on the Crustdata blog, not in the docs.

---

## Sources & Cache index

All pages cached to `/home/akash/PROJECTS/crustdata/research/cache/` (HTML files) and to `/home/akash/PROJECTS/crustdata/research/cache/endpoints/` (extracted endpoint specs):

- `crustdata_openapi-specs_2025-11-01_introduction.html` — master 12-endpoint table
- `crustdata_api-reference_company-apis_*.html` (4 files) — each company API reference page
- `crustdata_api-reference_person-apis_*.html` (3 files) — person API references
- `crustdata_api-reference_web-apis_*.html` (2 files) — web search + fetch
- `crustdata_api-reference_job-apis_search-the-indexed-job-dataset.html`
- `crustdata_company-docs_{quickstart,search,enrichment,identify,autocomplete,examples}.html`
- `crustdata_person-docs_quickstart.html`
- `crustdata_general_{introduction,pricing,rate-limits}.html`
- `endpoints/company_search.txt`, `company_identify.txt`, `company_enrich.txt`, `company_autocomplete.txt`, `company_quickstart.txt`
- `endpoints/person_search.txt`, `person_enrich.txt`, `person_autocomplete.txt`, `person_quickstart.txt`
- `endpoints/web_search.txt`, `web_fetch.txt`
- `endpoints/job_search.txt`
- `endpoints/pricing.txt`, `rate_limits.txt`
- `composio_crustdata.md` — full 14-tool Composio MCP reference

**Primary references**:
- `https://docs.crustdata.com/openapi-specs/2025-11-01/introduction`
- `https://docs.crustdata.com/general/{introduction,pricing,rate-limits}`
- `https://docs.crustdata.com/api-reference/{company,person,web,job}-apis/*`
- `https://docs.crustdata.com/{company,person,web}-docs/*`
- `https://web.archive.org/web/2025/https://docs.crustdata.com/docs/{intro,discover,dictionary}/*`
- `https://docs.composio.dev/toolkits/crustdata.md`
- `https://crustdata.com/apis/{watcher,posts,job-listing,company-enrichment,company-discovery,people-enrichment,people-discovery}`
- `https://crustdata.com/blog/{company-search-api,people-search-api,data-enrichment-api-use-cases,best-apis-for-job-posting-data}`
