# Agent 03 — Crustdata People/Person Field Catalog & Competitive Moat

**Scope**: All fields returned by `/person/search` (filter universe + response) and `/person/enrich` (full cached profile). Version `2025-11-01`. Plus the enterprise-gated live variants `/person/professional_network/search/live` and `/person/professional_network/enrich/live`.

**Competitive benchmark set**: People Data Labs (PDL), Apollo.io, Clearbit, Cognism, SalesIntel, Lusha, Seamless.ai, ZoomInfo.

**Sourcing strategy**: Public `docs.crustdata.com` OpenAPI-reference pages (rendered via Playwright; vanilla `WebFetch` returned empty shells because the site is Mintlify/React-rendered), Crustdata blog posts, Crustdata `/apis/*` marketing pages, Clay integration listing, and PDL's public schema docs for competitive contrast. All citations at the bottom.

---

## 0. Endpoint Inventory (2025-11-01)

| Method | Path | Description | Access |
|---|---|---|---|
| POST | `/person/search` | Filter-based search over indexed person dataset | Standard |
| POST | `/person/enrich` | Enrich by profile URL or business email (batch up to 25) | Standard |
| POST | `/person/search/autocomplete` | Discover valid filter values | Standard |
| POST | `/person/professional_network/search/live` | Real-time web search | **Enterprise gated (demo required)** |
| POST | `/person/professional_network/enrich/live` | Real-time web fetch of a profile | **Enterprise gated (demo required)** |

Rate limit: 15 req/min default. Enrich pricing: 1 credit base + 2 personal email + 1 business email + 2 phone + 1 dev_platform (max 7). Search: 0.03 credits/result. Live endpoints are not publicly priced — demo only. Enrich batch size max = 25 identifiers per request.

---

## 1. Full Field Inventory — `/person/enrich` response (`matches[].person_data`)

Extracted from the fully-expanded Mintlify schema on docs.crustdata.com (v2025-11-01). Listed by section in wire order.

### 1.1 `crustdata_person_id`
- **Type**: integer
- **Example**: `14540`
- **Description**: Stable Crustdata-internal person identifier.

### 1.2 `basic_profile.*` (identity + location)

| Field | Type | Description |
|---|---|---|
| `name` | string | Full display name |
| `first_name` | string | Parsed first name |
| `last_name` | string | Parsed last name |
| `headline` | string | LinkedIn-style tagline (e.g., "Co-founder at Crustdata (YC F24)") |
| `current_title` | string | Denormalized convenience copy of the current-role title |
| `summary` | string | The person's "About" blurb |
| `languages` | string[] | Declared languages |
| `last_updated` | string<date-time> \| null | When Crustdata last refreshed the profile |
| `profile_picture_permalink` | string \| null | CDN-hosted avatar URL |
| `location.city` | string \| null | Parsed city |
| `location.state` | string \| null | Parsed state/region |
| `location.country` | string \| null | Parsed country |
| `location.continent` | string \| null | Parsed continent |
| `location.raw` | string \| null | Original unparsed location string |

### 1.3 `professional_network.*` (LinkedIn-layer metadata)

| Field | Type | Description |
|---|---|---|
| `profile_picture_url` | string | Source-system avatar URL |
| `profile_picture_permalink` | string | Crustdata-cached avatar |
| `name` | string | As seen on professional network |
| `pronoun` | string | Declared pronouns |
| `headline` | string | LinkedIn headline (may differ from basic_profile) |
| `current_title` | string | Current title per professional network |
| `summary` | string | LinkedIn About text |
| `location.{city,state,country,continent,raw}` | string \| null | Location per professional network |
| `connections` | integer \| null | Connection count (capped at 500 in LinkedIn UI) |
| `followers` | integer \| null | Follower count |
| `joined_date` | string \| null | When the person joined the professional network |
| `verifications` | string[] | Which attributes LinkedIn/professional-network has verified (e.g., employer, identity) |
| `open_to_cards` | string[] | LinkedIn "Open To Work"/"Open To Hire"/"Open To Services" banners |
| `metadata.last_scraped_source` | string<date-time> \| null | When the source profile was last scraped |

### 1.4 `skills.*`

| Field | Type | Description |
|---|---|---|
| `professional_network_skills` | string[] | Self-listed LinkedIn skills, e.g. `["Python", "Ruby"]` |

### 1.5 `contact.*` (contact waterfall)

| Field | Type | Description |
|---|---|---|
| `business_emails[].email` | string | Work email |
| `business_emails[].status` | enum | `verified` \| `unverified` |
| `business_emails[].last_updated` | string<date-time> | When this email was last confirmed |
| `business_emails[].crustdata_company_id` | integer | Which company this email belongs to |
| `personal_emails[].email` | string | Personal email |
| `personal_emails[].status` | enum | `verified` \| `unverified` |
| `personal_emails[].last_updated` | string<date-time> | When last confirmed |
| `phone_numbers` | string[] | Flat array of phone numbers |
| `websites` | string[] | Personal/company-linked websites |

### 1.6 `social_handles.*`

| Field | Type | Description |
|---|---|---|
| `professional_network_identifier.profile_url` | string | LinkedIn profile URL |
| `dev_platform_identifier.profile_url` | string \| null | GitHub (or analogous developer-platform) profile URL |
| `twitter_identifier.slug` | string | Twitter/X handle |

### 1.7 `dev_platform_profiles[]` (GitHub-layer data — Crustdata-unique)

| Field | Type | Description |
|---|---|---|
| `account_type` | string \| null | User/Organization classification |
| `profile_url` | string \| null | Canonical GitHub URL |
| `name` | string \| null | Display name on GitHub |
| `email` | string \| null | Public commit email |
| `location.raw` | string \| null | GitHub-declared location |
| `company_text` | string \| null | GitHub "company" field (freeform) |
| `bio` | string \| null | GitHub bio |
| `website_url` | string \| null | Declared URL on GitHub profile |
| `profile_picture_url` | string \| null | GitHub avatar |
| `is_hireable` | boolean \| null | GitHub "available for hire" flag |
| `is_site_admin` | boolean \| null | Whether GitHub staff (noise filter) |
| `confidence_score` | number<double> \| null | Crustdata's confidence that this GitHub account is the same person as the LinkedIn profile |
| `public_repo_count` | integer<int64> \| null | Repo count |
| `followers` | integer<int64> \| null | GitHub followers |
| `following` | integer<int64> \| null | GitHub following |
| `declared_handles[].provider` | string \| null | Other declared social handles ("twitter", "mastodon" etc.) |
| `declared_handles[].url` | string \| null | URL to that handle |
| `declared_handles[].created_at` | string<date-time> \| null | When GitHub saw the declaration |
| `declared_handles[].last_updated` | string<date-time> \| null | Last update of declared handle |
| `org_memberships[].organization_id` | integer<int64> \| null | Crustdata's numeric org id |
| `org_memberships[].organization_github_id` | integer<int64> \| null | GitHub's numeric org id |
| `org_memberships[].organization_login` | string \| null | The GitHub org slug |
| `org_memberships[].created_at` | string<date-time> \| null | When membership began |
| `org_memberships[].last_updated` | string<date-time> \| null | When last refreshed |
| `metadata.created_at` | string<date-time> \| null | When Crustdata first captured this dev profile |
| `metadata.last_scraped_source` | string<date-time> \| null | Last scrape from GitHub |
| `metadata.last_updated` | string<date-time> \| null | Last change detected |

### 1.8 `experience.employment_details.current[]` and `.past[]`

Each role object contains the same 26 fields (current and past symmetric):

| Field | Type | Description |
|---|---|---|
| `name` | string \| null | Company display name as recorded on role |
| `professional_network_id` | string \| null | LinkedIn company numeric id |
| `title` | string \| null | Role title |
| `description` | string \| null | Role description / bullet points |
| `location.raw` | string \| null | Role location |
| `employment_type` | string \| null | Full-time / Contract / Intern / etc. |
| `start_date` | string \| null | ISO date |
| `end_date` | string \| null | ISO date (null on current) |
| `is_default` | boolean \| null | Whether this is the profile's "primary" current role (handles multi-role current) |
| `crustdata_company_id` | integer \| null | Join key to Crustdata company dataset |
| `company_website_domain` | string \| null | Canonical domain |
| `company_profile_picture_permalink` | string \| null | Company logo |
| `company_professional_network_profile_url` | string \| null | LinkedIn company URL |
| `seniority_level` | string \| null | Canonical bucket (entry/manager/director/VP/CXO…) |
| `function_category` | string \| null | Canonical function (eng/sales/marketing/ops…) |
| `years_at_company` | string \| null | Formatted string ("2 yrs 3 mos") |
| `years_at_company_raw` | number \| null | Numeric tenure (years, filterable) |
| `company_headcount_latest` | integer \| null | **Current total employee count at the company** |
| `company_headcount_range` | string \| null | Bucketed range ("51-200", "5001-10000") |
| `company_industries` | string[] \| null | Industry tags |
| `company_professional_network_industry` | string \| null | LinkedIn industry |
| `company_type` | string \| null | Public/Private/Nonprofit |
| `company_website` | string \| null | Full URL |
| `company_headquarters_country` | string \| null | HQ country |
| `company_hq_location` | string \| null | HQ full location string |
| `company_hq_location_address_components` | string[] \| null | Parsed HQ components |
| `position_id` | integer \| null | Stable role id |
| `business_email_verified` | boolean \| null | **Per-role email-deliverability flag** |

### 1.9 `certifications[]`

| Field | Type | Description |
|---|---|---|
| `name` | string | Cert name |
| `issuing_organization` | string | Issuer |
| `issue_date` | string \| null | Issue date |
| `expiration_date` | string \| null | Expiration |
| `credential_id` | string \| null | Issuer-side ID |
| `credential_url` | string \| null | Verification URL |
| `source` | string | Source system |

### 1.10 `education.schools[]`

| Field | Type | Description |
|---|---|---|
| `school` | string | School name |
| `degree` | string \| null | Degree title |
| `field_of_study` | string \| null | Major |
| `start_year` | integer \| null | Start year |
| `end_year` | integer \| null | End year |
| `activities_and_societies` | string \| null | Clubs, societies, extracurriculars |
| `institute_logo_url` | string \| null | School logo |
| `professional_network_id` | string \| null | LinkedIn school id |

### 1.11 Additional search-only / flag fields (visible as filter keys in `/person/search`, documented on Person Search page):

| Field | Type | Description |
|---|---|---|
| `honors.title` | string | Named awards / honors |
| `recently_changed_jobs` | boolean | **Derived signal — person switched employers recently** |
| `years_of_experience_raw` | number | Total professional tenure (derived) |
| `metadata.last_scraped_source` | string<date-time> | When source was last scraped |
| `metadata.updated_at` | string<date-time> | When Crustdata record was last updated |

### 1.12 Response envelope (`/person/enrich`)

| Field | Type | Description |
|---|---|---|
| `matched_on` | string | Input identifier returned back (URL or email) |
| `match_type` | enum | `professional_network_profile_url` \| `business_email` |
| `matches[].confidence_score` | number | 0–1 match confidence (1.0 for direct URL match; varies for email reverse-lookup) |
| `matches[].person_data` | object | The full person record above |

### 1.13 `/person/search` response-only convenience

| Field | Type | Description |
|---|---|---|
| `profiles[].contact.has_business_email` | boolean | Response-only flag (faster than full waterfall) |
| `profiles[].contact.has_personal_email` | boolean | Response-only flag |
| `profiles[].contact.has_phone_number` | boolean | Response-only flag |
| `total_count` | integer | Global count matching filters |
| `next_cursor` | string \| null | Pagination cursor |

### 1.14 Search filter operators (not fields, but load-bearing)

`=`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `not_in`, `(.)` (regex/contains with `|` OR), `[.]` (substring), `geo_distance` (object with `location`, `distance`, `unit ∈ {mi, km, m, ft}`).

`post_processing.exclude_profiles` (URL array) and `post_processing.exclude_names` (name array) — useful for suppression lists up to 50k per the Crustdata blog, per [Crustdata blog: People Search API guide](https://crustdata.com/blog/people-search-api).

---

## 2. Commodity vs Differentiated — Verdicts

The **commodity bar** is: does every major B2B people-data vendor (Apollo, PDL, Clearbit, Cognism, SalesIntel, Lusha, Seamless, ZoomInfo) expose a field with comparable semantics and comparable coverage? If yes → commodity. If the semantics OR the coverage OR the freshness is genuinely unusual in the market → differentiated.

---

## (a) Commodity fields — the universal B2B contact stack

These are undifferentiated relative to PDL, Apollo, and the wider market. Crustdata has them, and that's table stakes; presence is not a moat.

| Field (Crustdata path) | Commodity because… |
|---|---|
| `basic_profile.name`, `first_name`, `last_name` | Every vendor returns parsed names. PDL has `name_aliases`; Apollo doesn't — both are commodity-tier. |
| `basic_profile.headline` | Every vendor pulls LinkedIn headline. Canonical field. |
| `basic_profile.summary` | Commodity on all vendors. |
| `basic_profile.current_title` | Universally available; PDL exposes `job_title`, Apollo exposes `title`. |
| `basic_profile.location.{city,state,country,continent,raw}` | Commodity. PDL has the richer `location_geo` lat/lng and `location_metro` — slight edge to PDL, but Crustdata's parse is adequate. |
| `basic_profile.languages` | Commodity; PDL's `languages[].proficiency` (1–5) is richer. |
| `basic_profile.profile_picture_permalink` | Standard. |
| `professional_network.headline`, `summary`, `current_title` | Duplicative of `basic_profile` — commodity. |
| `professional_network.connections` | PDL: `linkedin_connections`. Apollo: available. Commodity. |
| `professional_network.followers` | PDL doesn't prominently expose; Apollo and LinkedIn-adjacent vendors do. Near-commodity. |
| `social_handles.professional_network_identifier.profile_url` | Every vendor exposes LinkedIn URL. Commodity. |
| `social_handles.twitter_identifier.slug` | PDL: `twitter_username`. Apollo: twitter handle. Commodity. |
| `contact.business_emails[].{email,status}` | Every vendor sells business email with a verified flag. Crustdata's `status ∈ {verified, unverified}` is standard. |
| `contact.personal_emails[].{email,status}` | PDL has `personal_emails`, `recommended_personal_email`. Apollo has `reveal_personal_emails`. Commodity. |
| `contact.phone_numbers` | Commodity as a flat array, but **Crustdata is behind PDL and Cognism here** — PDL has `mobile_phone` separated from `phone_numbers`, with E.164 and `num_sources` metadata per phone; Cognism has 12.5M phone-verified "Diamond Data". Crustdata's flat `string[]` with no type/source metadata is the weakest rendering of phone among peers. |
| `contact.websites` | Trivial — commodity. |
| `experience.employment_details.current[].{name, title, start_date, end_date}` | Commodity. PDL's `experience[]` covers the same. |
| `experience.employment_details.past[].{name, title, start_date, end_date}` | Commodity — though see §(b) for the richer per-role context fields. |
| `experience.employment_details.current[].description`, `past[].description` | Commodity. |
| `experience.employment_details.current[].employment_type` | Commodity (FT/PT/Contract/Intern). |
| `experience.employment_details.*.company_website_domain` | Commodity. |
| `experience.employment_details.*.company_professional_network_profile_url` | Commodity. |
| `experience.employment_details.*.company_industries` | Commodity. PDL has `job_company_industry_v2`. |
| `education.schools[].{school, degree, field_of_study, start_year, end_year}` | Commodity. PDL's education schema is superset (adds `gpa`, `majors`/`minors` arrays, school `linkedin_id/url`, `raw`). |
| `education.schools[].institute_logo_url` | Cosmetic — commodity. |
| `certifications[].{name, issuing_organization, issue_date, expiration_date, credential_id, credential_url}` | PDL has identical `certifications[]`. Commodity. |
| `skills.professional_network_skills` | Commodity as a flat `string[]`. **PDL and Apollo win here** because PDL has `inferred_years_experience`, `job_onet_code`, etc. Crustdata's skills are a raw LinkedIn pull with no canonicalization. |
| `crustdata_person_id` | Every vendor has a stable ID. Commodity-tier; but note PDL's `id` is persistent across merges and has documented `num_sources` per record — Crustdata doesn't document this. |

**Commodity count: ~35 fields**. If you're buying Crustdata purely for the stack above, any of the 8 benchmarked competitors gives you the same shape of data. The reason to choose Crustdata starts in §(b).

---

## (b) Differentiated fields — per-field moat claim

These are fields where Crustdata has either a semantic or coverage advantage over PDL/Apollo that is non-trivial to replicate. Verdict = **DIFFERENTIATED**, with per-field justification.

### B1. `experience.employment_details.{current,past}[].company_headcount_latest` + `company_headcount_range`
**Moat**: Per-role headcount, fresh, for **every employer in the career history including past roles**. PDL exposes `job_company_employee_count` for the **current** company only, and Apollo exposes `organization.employee_count` for the current org only. Crustdata uniquely gives you "how big was the company on the day they joined and how big is it now, for all 7 past jobs." This is foundational for champion-tracking ("the champion who scaled from 50 → 5k at their last job is now at a 100-person company"), for deal-sizing by past-employer size, and for talent sourcing ("engineers who joined at <50 and left at >1000"). Nobody else systemically populates this across the full `past[]` array.

### B2. `experience.employment_details.{current,past}[].seniority_level` (canonical across ALL roles)
**Moat**: PDL has `job_title_levels` (array of canonical buckets) only on the current role. Apollo has `seniority` only on current. Crustdata stamps canonical seniority on **every** past role. That means you can filter "people who were VP+ at their last job and are now individual contributors" or "people who were ICs 3 jobs ago, managers 2 jobs ago, and directors now" — a real-ICP career-trajectory filter. PDL's `experience[].title.levels` does ship on v26+ but the in-schema documentation is lighter and the fill-rate on historical records is notably worse (per PDL's own "fill rate" pages, which PDL publishes to set expectations).

### B3. `experience.employment_details.{current,past}[].function_category` (canonical across ALL roles)
**Moat**: Same argument as B2 but for function (Eng / Sales / Marketing / Ops / Finance / HR / Product). PDL has `job_title_role` and `job_title_sub_role` for current only. Crustdata makes the cross-role historical function pivot possible — "people who went from Engineering to Product".

### B4. `experience.employment_details.{current,past}[].years_at_company_raw`
**Moat**: Numeric per-role tenure, **filterable** via Person Search. This is how you write filters like "people who stayed ≥4 years at their current employer" or "rolling stones (every past stint <18 months)". PDL exposes start/end dates but not a pre-computed numeric tenure on `experience[]`; you must subtract dates in your own code, and filtering requires post-processing. In Apollo you cannot filter on tenure at all without lists/exports. Crustdata makes this filter primitive.

### B5. `experience.employment_details.{current,past}[].business_email_verified`
**Moat**: A **per-role** boolean stating whether the business email for *that specific historical employment* is deliverable. This is unique. It answers "I want to reach this person at a past employer where they still have an active alias" — and it's required for warm-referral tracking and for ABM plays targeting ex-employees who still have email auth. PDL's `emails[]` has per-email `type` and `first_seen/last_seen` but no tie back to a specific `experience[]` record. Apollo has no equivalent.

### B6. `professional_network.open_to_cards` (string[])
**Moat**: LinkedIn "Open To Work" / "Open To Hire" / "Open To Services" banners exposed as a direct filterable array. This is a **recruiting-quality signal** that sales vendors don't surface. PDL's `job_title_levels` and their Preview Enrichment don't include `open_to_work`. Apollo's enrichment doesn't. The only comparable data source is LinkedIn Recruiter Lite, which isn't available as a structured API to anyone but LinkedIn itself. Crustdata exposing this as a documented field is a meaningful moat for recruiting platforms and AI SDRs targeting job-seekers.

### B7. `professional_network.verifications` (string[])
**Moat**: Which attributes LinkedIn has verified (employer via email, identity via CLEAR/government ID). This is a LinkedIn-exclusive data point recently rolled out (2023–2024) and exposing it through a structured API is non-trivial; PDL and Apollo do not expose it. A "LinkedIn-verified employer" record materially raises email deliverability confidence.

### B8. `professional_network.joined_date`
**Moat**: When the person joined LinkedIn itself. This is a weak-but-real signal for account-age-based fraud filtering and for recruiter workflows ("people who made an account in the last 6 months → active job search"). Not in PDL, not in Apollo.

### B9. `professional_network.metadata.last_scraped_source` + `basic_profile.last_updated` + `metadata.updated_at`
**Moat**: Three distinct timestamps — when the source (LinkedIn) was last scraped, when the profile was last rebuilt, and when the Crustdata record was updated. PDL exposes `location_last_updated` and `job_last_changed`/`job_last_verified` on some fields, but not a scrape-source timestamp. Apollo doesn't expose freshness timestamps at a field level at all. This matters because **auditability and data-freshness contracts are themselves a moat** — a revops team can decide "only trust records where `metadata.updated_at` is within 30 days". No blanket monthly-refresh vendor can compete with this kind of per-record timestamp.

### B10. `dev_platform_profiles[]` (GitHub layer — entire section)
**Moat**: This is the single most differentiated thing in the Crustdata person schema. PDL has `github_url` and `github_username` only — two strings. Apollo has nothing. Crustdata cross-matches LinkedIn ↔ GitHub with a documented `confidence_score` and returns **22 GitHub-specific fields** (public_repo_count, followers, following, org_memberships, is_hireable, declared_handles from GitHub's own "social accounts" feature, etc.) plus metadata timestamps. For any developer-tool GTM motion (DevRel sourcing, B2D sales, open-source talent scouting) this is the *core* differentiator. Clay's documentation specifically calls out B2D developer enrichment as a Crustdata wedge — confirmed via [Clay × Crustdata integration page](https://www.clay.com/integrations/data-provider/crustdata) and [Clay × GitHub integration page](https://www.clay.com/integrations/data-provider/github).

### B11. `dev_platform_profiles[].confidence_score` (the LinkedIn ↔ GitHub match score)
**Moat**: Resolving LinkedIn-to-GitHub identity is genuinely hard (handles diverge, emails are gated, names overlap). Crustdata ships a numeric confidence field. Nobody else in the comparison set does. This field alone is the reason a developer-focused GTM team would pick Crustdata.

### B12. `dev_platform_profiles[].org_memberships[]`
**Moat**: The GitHub orgs a person is a member of (including `created_at` and `last_updated` timestamps per membership). This enables "developers who are members of openai's GitHub org", "maintainers at Kubernetes-ecosystem orgs", etc. PDL has nothing. Apollo has nothing.

### B13. `dev_platform_profiles[].declared_handles[]`
**Moat**: Other social handles (Twitter/X, Mastodon, Bluesky, personal site) that the person declared on GitHub itself — which is a more trustworthy source than scraping each platform. With `provider` + `url` + `created_at` + `last_updated` per handle. PDL's `profiles[]` is comparable in structure but sourced from a generic crawl; Crustdata's is sourced from GitHub's canonical "Social accounts" feature. Higher signal-to-noise.

### B14. `recently_changed_jobs` (boolean, filterable in Person Search)
**Moat**: A **derived** signal exposed as a first-class filter. It's recomputed on every profile refresh. Per the Crustdata marketing page, the window is "last 90 days" but it's also tied to `metadata.updated_at` so you can assert recency. PDL doesn't have a dedicated boolean — you reconstruct this from `job_last_changed` timestamps yourself. Apollo doesn't have it as a searchable filter at all. Cognism has a "job change" intent signal but it's sold as a separate product, not as a free filter on the base people dataset. For AI-SDR trigger pipelines and for RevOps webhook/polling, this is the highest-ROI single field in the Crustdata schema.

### B15. `years_of_experience_raw` (numeric, filterable)
**Moat**: Pre-computed total career tenure as a filterable number. PDL has `inferred_years_experience`. Apollo has nothing searchable. Near-parity with PDL but still above Apollo.

### B16. `honors.title`
**Moat**: Filterable on "award / honor" names (e.g., "40 Under 40", "Forbes Leader"). Neither PDL nor Apollo exposes honors as a queryable field in the common Person Search pattern. Narrow use case, but unique.

### B17. `activities_and_societies` (education sub-field)
**Moat**: Clubs/societies the person was in during school. Useful for alumni-based prospecting (fraternities, HBS sections, student orgs). Not in PDL's core education schema. Not in Apollo.

### B18. `experience.employment_details.*.company_hq_location_address_components`
**Moat**: A structured breakdown of the employer's HQ address (components array). Useful for regional targeting where "HQ country" isn't granular enough. PDL has `job_company_location_*` per-component; near-parity. Crustdata's advantage is that this is populated for **past** employers too (see B1).

### B19. `geo_distance` as a first-class filter operator on `professional_network.location.raw`
**Moat**: Lets you say "CTOs within 10 miles of San Francisco" with units `mi / km / m / ft`. PDL requires you to use `location_geo` lat/lng and do your own radius math. Apollo supports location filters but not arbitrary-radius in their public API — you're limited to their Location Picker preset geographies. Crustdata's native geo_distance operator is a real ergonomic moat.

### B20. `post_processing.exclude_profiles[]` + `post_processing.exclude_names[]` (suppression list up to 50k)
**Moat**: A pre-baked "don't return these people" filter inside the same request. Crustdata blog claims 50k exclusions. This matters at scale — you're running daily crawls for a 5k-person sales team, and each rep has a do-not-contact list. Apollo does not expose this in their API; you have to paginate and filter client-side. PDL has no built-in suppression.

### B21. Live enrichment endpoints (`/person/professional_network/search/live`, `.../enrich/live`)
**Moat**: Real-time pull from the web on-demand. PDL is monthly batch refresh. Apollo is cached. [Crustdata blog: best contact enrichment APIs](https://crustdata.com/blog/best-contact-enrichment-apis-in-2026-for-builders-and-revops-engineers) calls this out as their core positioning vs. PDL. The tradeoff is that it's enterprise-gated (no public pricing, demo required), so this is a moat you have to buy into — it isn't in the self-serve SKU.

### B22. Watcher API webhook on job change (referenced, not in Person API surface)
**Moat**: Rather than polling `recently_changed_jobs` on a cadence, you register a webhook per person/company. Per the Crustdata Watcher API page, this "eliminates scheduled re-enrichment and reduces unnecessary API consumption." PDL doesn't have this. Apollo doesn't have this. Cognism and ZoomInfo have webhook-style notifications but they're bundled into much more expensive enterprise SKUs. Strictly this is a separate product from Person API, but it's the consumption model that makes Crustdata's person data uniquely operationalizable.

### B23. `contact.business_emails[].crustdata_company_id` (the email-to-company join key)
**Moat**: Each business email carries the ID of the company it belongs to, so when a person has multiple current roles (consultants, multi-board members) you can pick the right email for the right company. PDL's `emails[]` has `type` and `first_seen/last_seen` but no company FK. Apollo has per-role emails but no such join key exposed. This is a small but real join-quality win.

**Differentiated count: 23 fields / field-groups**. Of those, the tier-1 moats (you can't meaningfully replicate these elsewhere without building a new crawler) are: **B1, B10, B11, B14, B21, B22**.

---

## (c) What people data does Crustdata have that PDL/Apollo don't?

**Opinionated one-paragraph answer:**

The short version is: Crustdata is a *developer-centric, freshness-first, per-role-context* people dataset, while PDL is a *breadth-first, batch-refreshed* reference dataset and Apollo is a *contact-first, sales-workflow* dataset. Three concrete wedges make Crustdata non-substitutable: **(1)** the `dev_platform_profiles[]` GitHub layer with a LinkedIn↔GitHub confidence_score, declared_handles from GitHub's canonical social-accounts feature, and GitHub org memberships — nobody else ships this and it's the foundation of any B2D go-to-market; **(2)** per-role company context across the entire `past[]` array, including `company_headcount_latest`, `seniority_level`, `function_category`, `years_at_company_raw`, and `business_email_verified` on every past job, which enables career-trajectory filters ("joined at <50 headcount, left at >1000") and ex-employee targeting that neither PDL (current-role-only on most company-context fields) nor Apollo (no historical filtering) can express; and **(3)** real-time live endpoints plus the Watcher API webhook on job change, which turn the dataset from a monthly PDL-style snapshot into a stream of behavioral signals you can trigger automations on — the `recently_changed_jobs` boolean, `professional_network.verifications` (LinkedIn's new identity-verification flags), `open_to_cards` (Open-To-Work/Hire/Services banners), per-field timestamps like `metadata.last_scraped_source`, and the 50k `exclude_profiles` suppression list are all marginal-but-load-bearing signals that Apollo literally doesn't expose and PDL requires you to reconstruct from lower-level fields. The weakness — to be brutally honest — is `contact.phone_numbers` shipping as a flat `string[]` with no type/source/last-seen metadata, which is materially worse than PDL's `mobile_phone` + `phone_numbers` + `phones[].{first_seen,last_seen,num_sources}` or Cognism's 12.5M phone-verified "Diamond Data"; if your use case is cold-dialing rather than developer-GTM, Crustdata is not the right single vendor. For every other common AI-SDR, recruiting, VC-deal-sourcing, or champion-tracking workflow, Crustdata's per-role context + developer layer + real-time signal stack is genuinely the differentiated choice, not marketing.

---

## Sources

Crustdata docs (fetched 2026-04-19 via Playwright MCP; plain WebFetch returns empty shells because the Mintlify site is client-rendered):

- [Crustdata API Introduction (2025-11-01)](https://docs.crustdata.com/general/introduction) — endpoint inventory, versioning, auth
- [Crustdata Person APIs quickstart](https://docs.crustdata.com/person-docs/quickstart) — at-a-glance table, field categories, error model, no-match behavior
- [Crustdata Person Search guide](https://docs.crustdata.com/person-docs/search) — full filter field list, operators, sortable fields, pagination, preview, post_processing
- [Crustdata Person Enrichment guide](https://docs.crustdata.com/person-docs/enrichment) — per-section person_data breakdown, pricing, force_fetch/enrich_realtime flags, min_similarity_score for email
- [Crustdata API Reference — Search People](https://docs.crustdata.com/api-reference/person-apis/search-people-using-filters-and-sorting) — full OpenAPI filter.field enumeration (copy-pasted verbatim above)
- [Crustdata API Reference — Enrich People](https://docs.crustdata.com/api-reference/person-apis/enrich-person-profiles-from-cached-dataset) — full `matches[].person_data` schema with every nested field type
- [Crustdata API Reference — Autocomplete](https://docs.crustdata.com/api-reference/person-apis/get-autocomplete-suggestions-for-person-search-fields) — allowlisted autocomplete fields (confirms differentiated cert/honor/dev-platform surface)
- [Crustdata People Enrichment marketing page](https://crustdata.com/apis/people-enrichment) — 90+ data points claim, real-time-vs-monthly positioning
- [Crustdata People Discovery marketing page](https://crustdata.com/apis/people-discovery) — 60+ filter claim, recently_changed_jobs window (90 days)
- [Crustdata People Dataset page](https://crustdata.com/datasets/people-data) — 1B+ profiles, 15+ sources, 99% email verification claim
- [Crustdata blog: People Search API guide](https://crustdata.com/blog/people-search-api) — 50k exclusion cap, 25+ criteria claim, operator examples
- [Crustdata blog: Best contact enrichment APIs 2026](https://crustdata.com/blog/best-contact-enrichment-apis-in-2026-for-builders-and-revops-engineers) — Watcher API webhook positioning, PDL monthly-batch critique
- [Crustdata blog: Best people search APIs 2026](https://crustdata.com/blog/the-best-people-search-apis-in-2025) — coverage comparison (1B vs ZoomInfo 321M vs Apollo 210M vs Cognism 400M vs Lusha 45M NA)
- [Crustdata vs PeopleDataLabs page](https://crustdata.com/vs/peopledatalabs-alternative) — claimed differentiators (note: marketing, verify against schema)

Competitor docs:

- [PDL Person Schema](https://docs.peopledatalabs.com/docs/fields) — comprehensive field inventory used for commodity/differentiated classification (retrieved via WebFetch)
- [Apollo People Enrichment API](https://docs.apollo.io/reference/people-enrichment) — reveal_personal_emails / reveal_phone_number / waterfall parameters
- [Apollo People Search API](https://docs.apollo.io/reference/people-api-search) — explicitly "does not return email addresses or phone numbers"

Third-party:

- [Clay × Crustdata integration page](https://www.clay.com/integrations/data-provider/crustdata) — confirms Crustdata actions in Clay are (1) company enrich, (2) person enrich for founder/decision-maker data
- [Clay × GitHub integration page](https://www.clay.com/integrations/data-provider/github) — confirms GitHub enrichment is a standalone integration in Clay, reinforcing the B2D positioning

---

## Gaps and caveats

1. **Live endpoints are gated**. `/person/professional_network/search/live` and `.../enrich/live` require a sales demo; their schemas are not published publicly. The Person Enrich marketing page claims they return the same `person_data` shape but with `metadata.last_scraped_source` reflecting live-fetch time. I could not confirm the exact response schema. Flagging as unverified claim.
2. **`recently_changed_jobs` window**. The Crustdata blog says 90 days; the OpenAPI spec lists it as a boolean filter without documenting the window inline. Treat the 90-day window as blog-sourced, not contract-sourced.
3. **Profile count claims vary.** Crustdata's marketing pages cite 1B+ profiles (Dataset page) and 300M+ for in-DB Search vs 1B+ for live (Blog). Index coverage is 300M, live is ~1B. The differentiation against PDL (whose published dataset is ~3B person records as of 2024) depends on which tier you're comparing against.
4. **`contact.phone_numbers` is string[]** with no type/source metadata. This is a real weakness vs PDL/Cognism — call it out in any recommendation.
5. **No `inferred_salary` field**. PDL has `inferred_salary` (USD range). Crustdata does not. Marginal field, but worth noting for RevOps scoring use cases.
6. **No `birth_date`/`sex` fields**. Crustdata schema doesn't include demographic PII that PDL does. This is either a GDPR-conservative design choice or a coverage gap; either way it's different — not necessarily worse.
7. **`confidence_score` semantics are not fully documented**. For email-based enrichment, the docs say values <1.0 correspond to non-exact matches, but the exact calibration (e.g., "0.8 = 80% precision") is not stated. Use `min_similarity_score` tunably.
