# Crustdata

CrustData is an AI-powered data intelligence platform that provides real-time company and people data via APIs and webhooks, empowering B2B sales teams, AI SDRs, and investors to act on live signals

- **Category:** sales & crm
- **Auth:** API_KEY
- **Composio Managed App Available?** N/A
- **Tools:** 14
- **Triggers:** 0
- **Slug:** `CRUSTDATA`
- **Version:** 20260407_00

## Tools

### Enrich person screener

**Slug:** `CRUSTDATA_ENRICH_PERSON_SCREENER`

The screener_person_enrich endpoint enriches person data by providing additional information based on the given query. It allows users to retrieve detailed information about individuals, which can be useful for various purposes such as customer profiling, lead generation, or data verification. This endpoint should be used when you need to augment existing person data with additional details or verify information about a specific individual. The enrichment process draws from CrustData's extensive database and real-time data sources to provide up-to-date and comprehensive information. Users can customize the response by specifying the exact fields they need, optimizing data transfer and processing. Note that the availability and accuracy of enriched data may vary depending on the input provided and the information available in CrustData's systems.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | Yes | Comma-separated list of fields to be included in the response |
| `enrich_realtime` | boolean | Yes | Indicates whether the data should be enriched in real-time |
| `linkedin_profile_url` | string | Yes | The LinkedIn profile URL of the person to be enriched |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Fetch headcount by facet timeseries

**Slug:** `CRUSTDATA_FETCH_HEADCOUNT_BY_FACET_TIMESERIES`

Retrieves headcount data as a timeseries with faceted analysis capabilities. This endpoint allows users to fetch detailed headcount information over time, applying complex filters, pagination, and sorting. It's particularly useful for HR analytics, workforce planning, and organizational growth analysis. The endpoint supports nested logical operations in its filtering mechanism, enabling highly specific queries. Users can paginate through large datasets and sort results based on multiple criteria. While powerful, this endpoint requires careful construction of the filters parameter to ensure accurate data retrieval. It should be used when detailed, time-based headcount analysis is needed, but may not be suitable for simple, non-time-series headcount queries or for real-time data needs due to its complexity.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | The number of results to be returned |
| `sorts` | array | Yes | Specifies the sorting criteria |
| `offset` | integer | Yes | The offset for paginating the results |
| `filters__op` | string ("and" | "or") | No | The logical operator for combining conditions |
| `filters__conditions` | array | No | The conditions for filtering |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Fetch investor portfolio data

**Slug:** `CRUSTDATA_FETCH_INVESTOR_PORTFOLIO_DATA`

Retrieves comprehensive investor portfolio data from the Data Lab section of the CrustData API. This endpoint provides access to detailed information about investor portfolios, including investment holdings, performance metrics, and other relevant data points. It is designed to support investment analysis, portfolio management, and decision-making processes in a B2B context. The endpoint should be used when detailed investor portfolio information is required for tasks such as investment screening, performance tracking, or generating analytical reports. It's important to note that this endpoint may not provide real-time data and the frequency of updates should be verified in the API documentation. Additionally, users should be aware of any data privacy and usage restrictions that may apply to the retrieved investor information.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `investor_name` | string | Yes | The name of the investor |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Filter decision makers data

**Slug:** `CRUSTDATA_FILTER_DECISION_MAKERS_DATA`

Filters and retrieves decision maker data from the CrustData B2B SaaS integration platform based on complex criteria. This endpoint allows for advanced querying of decision maker information using a combination of filters, pagination, sorting, and title-based filtering. It's designed for scenarios where specific subsets of decision maker data need to be extracted or analyzed. The endpoint supports nested logical conditions in filters, enabling highly targeted data retrieval. Use this when you need to perform detailed analysis or reporting on decision makers across various organizations or industries. Note that the endpoint requires careful structuring of the request body to effectively utilize its advanced filtering capabilities.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | The number of results to be returned |
| `sorts` | array | Yes | Specifies the sorting criteria |
| `offset` | integer | Yes | The offset for paginating the results |
| `filters__op` | string ("and" | "or") | No | The logical operator for combining conditions |
| `filters__conditions` | array | No | The conditions for filtering |
| `decision_maker_titles` | array | Yes | Specifies the titles of the decision makers to filter by |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Post funding milestone timeseries data

**Slug:** `CRUSTDATA_POST_FUNDING_MILESTONE_TIME_SERIES_DATA`

The FundingMilestoneTimeseries endpoint retrieves time-series data related to funding milestones for companies. It allows for complex querying of funding events over time, with flexible filtering, pagination, and sorting options. This endpoint is particularly useful for analyzing funding trends, comparing company funding histories, or tracking specific funding events across multiple organizations. The data returned is based on the specified filters and can be tailored to focus on particular time ranges, funding stages, or company characteristics. While it provides comprehensive funding milestone data, it does not include detailed company information beyond what's directly related to funding events.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | The number of results to be returned |
| `sorts` | array | Yes | Specifies the sorting criteria |
| `offset` | integer | Yes | The offset for paginating the results |
| `filters__op` | string ("and" | "or") | No | The logical operator for combining conditions |
| `filters__conditions` | array | No | The conditions for filtering |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Post headcount timeseries data

**Slug:** `CRUSTDATA_POST_HEADCOUNT_TIMESERIES_DATA`

Retrieves filtered and sorted headcount timeseries data from the CrustData Data Lab. This endpoint allows for complex querying of historical headcount information, enabling users to analyze workforce trends over time. It supports advanced filtering with nested conditions, pagination for handling large datasets, and customizable sorting. Ideal for generating reports, conducting workforce analysis, or integrating headcount data into third-party business intelligence tools. Note that the specifics of the returned data structure are not provided in the given schema.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | The number of results to be returned |
| `sorts` | array | Yes | Specifies the sorting criteria |
| `offset` | integer | Yes | The offset for paginating the results |
| `filters__op` | string ("and" | "or") | No | The logical operator for combining conditions |
| `filters__conditions` | array | No | The conditions for filtering |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Post job listings table data

**Slug:** `CRUSTDATA_POST_JOB_LISTINGS_TABLE_DATA`

This endpoint retrieves filtered and sorted job listings data for specified company tickers from a chosen dataset in the CrustData platform. It allows for highly customizable queries with complex filtering conditions, pagination, and sorting options. The endpoint is designed for bulk data retrieval and analysis of job market trends across multiple companies. Use this endpoint when you need to fetch and analyze job listing data for specific companies, apply custom filters to narrow down the results, or when you want to paginate through large sets of job data. It's particularly useful for market research, competitive analysis, or tracking employment trends in specific industries or companies. Note that this endpoint requires careful construction of the request body, especially for the filters parameter, which can support nested logical conditions. The performance and response time may vary depending on the complexity of the filters and the amount of data requested.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | The number of results to be returned |
| `sorts` | array | Yes | Specifies the sorting criteria |
| `offset` | integer | Yes | The offset for paginating the results |
| `tickers` | array | Yes | An array of tickers |
| `dataset__id` | string | No | The id of the dataset |
| `filters__op` | string ("and" | "or") | No | The logical operator for combining conditions |
| `dataset__name` | string | No | The name of the dataset |
| `filters__conditions` | array | No | The conditions for filtering |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Post web traffic data

**Slug:** `CRUSTDATA_POST_WEB_TRAFFIC_DATA`

Retrieves filtered and sorted web traffic data from the CrustData platform. This endpoint allows for complex querying of web traffic information using nested conditions and logical operators. It supports pagination for handling large datasets and provides sorting capabilities for customized data presentation. Use this endpoint when you need to analyze web traffic patterns, filter data based on specific criteria, or extract insights from your web analytics. The endpoint is particularly useful for generating reports, identifying trends, or monitoring key performance indicators related to web traffic.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | The number of results to be returned |
| `sorts` | array | Yes | Specifies the sorting criteria |
| `offset` | integer | Yes | The offset for paginating the results |
| `filters__op` | string ("and" | "or") | No | The logical operator for combining conditions |
| `filters__conditions` | array | No | The conditions for filtering |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Retrieve linkedin posts

**Slug:** `CRUSTDATA_RETRIEVE_LINKED_IN_POSTS`

Retrieves LinkedIn posts for a specified company using CrustData's screener functionality. This endpoint allows users to gather social media data from LinkedIn, which can be used for analyzing company activity, engagement, and sentiment. It's particularly useful for B2B marketers, sales professionals, and analysts who need insights into a company's social media presence and content strategy. The endpoint supports filtering by date range and customizing the response fields, making it versatile for various use cases such as competitive analysis, lead generation, and market research. Note that the availability and completeness of data may depend on the company's LinkedIn activity and privacy settings.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_linkedin_url` | string | Yes | The LinkedIn URL of the company for which posts are to be retrieved |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Screener company information

**Slug:** `CRUSTDATA_SCREENER_COMPANY_INFORMATION`

The GetCompanyScreener endpoint allows users to search and filter companies based on various criteria such as headcount, growth rate, funding, and more. It provides a powerful way to identify specific companies that meet predefined conditions. This endpoint is particularly useful for tasks like lead generation, market research, and competitive analysis. The endpoint returns a list of companies matching the specified criteria, with each company entry containing key information such as name, industry, headcount, funding details, and growth metrics. Users can customize their search using multiple filters, sort the results, and paginate through large result sets. Note that the accuracy of the data depends on CrustData's real-time data collection and update frequency.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_domain` | string | Yes | The domain of the company for which information is requested |
| `enrich_realtime` | string ("False" | "True") | Yes | Indicates whether to enrich the data with real-time information |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Screen metrics and filter conditions

**Slug:** `CRUSTDATA_SCREEN_METRICS_AND_FILTER_CONDITIONS`

The ScreenData endpoint enables advanced data screening and filtering on the CrustData platform. It allows users to construct complex queries for retrieving specific datasets based on custom metrics, filtering conditions, and sorting criteria. Use this endpoint for targeted data extraction, custom reporting, or data analysis within the B2B SaaS integration ecosystem. Note that while powerful, complex queries may impact performance with large datasets.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | The number of results to be returned |
| `sorts` | array | Yes | Specifies the sorting criteria |
| `offset` | integer | Yes | The offset for paginating the results |
| `metrics` | array | Yes | Specifies the metrics to be used for screening |
| `filters__op` | string ("and" | "or") | No | The logical operator for combining conditions |
| `filters__conditions` | array | No | The conditions for filtering |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Search companies with filters

**Slug:** `CRUSTDATA_SEARCH_COMPANIES_WITH_FILTERS`

The CompanySearch endpoint enables users to search and filter companies using the CrustData API. It provides a powerful mechanism for querying company data based on multiple criteria, supporting complex filtering and pagination. This endpoint is ideal for applications that need to retrieve specific sets of company information, such as financial analysis tools, market research platforms, or business intelligence systems. The search functionality allows for precise data retrieval, enhancing the efficiency of data integration and analysis processes in B2B scenarios. Users should be aware that the endpoint requires careful construction of filter objects and proper use of pagination to ensure optimal performance and accurate results.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | Yes | Specifies the page number for paginated results |
| `filters` | array | Yes | Specifies the filters for the search |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Search for job id in screener

**Slug:** `CRUSTDATA_SEARCH_FOR_JOB_ID_IN_SCREENER`

The screener_person_search endpoint allows users to search for persons associated with a specific job ID within the CrustData B2B SaaS integration platform. This POST request accepts a JSON payload containing a job_id and returns relevant person data linked to that job. It's particularly useful for scenarios where you need to quickly retrieve all individuals connected to a particular job or project. The endpoint is part of the platform's screening functionality, enabling efficient filtering of person records based on job-related criteria. While it provides a focused search based on job ID, it may not offer advanced filtering options or return comprehensive job details.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number for paginating results (starts at 1) |
| `job_id` | string | Yes | The job ID to search for |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |

### Search linkedin posts by keyword

**Slug:** `CRUSTDATA_SEARCH_LINKED_IN_POSTS_BY_KEYWORD`

This endpoint enables searching for LinkedIn posts using a specific keyword. It allows users to retrieve relevant content from LinkedIn by specifying a search term, along with options for pagination, sorting, and filtering by post date. The function is particularly useful for conducting market research, competitor analysis, or tracking industry trends on the LinkedIn platform. Users can fine-tune their search results by choosing how to sort the posts (by relevance or date) and selecting a specific time frame for the content. The endpoint returns paginated results, allowing for efficient navigation through large sets of matching posts.

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | Yes | The page number of the search results |
| `keyword` | string | Yes | The keyword to search for in the LinkedIn posts |
| `sort_by` | string ("date" | "relevance") | Yes | The sorting criteria for the search results |
| `date_posted` | string ("all-time" | "past-day" | "past-month" | "past-quarter" | "past-week" | "past-year") | Yes | The time frame for the posted content |

#### Output

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | Yes | Data from the action execution |
| `error` | string | No | Error if any occurred during the execution of the action |
| `successful` | boolean | Yes | Whether or not the action execution was successful or not |
