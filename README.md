# SupplyLens — Supply Chain Discovery

Supply chain intelligence tool powered by **Crustdata API** + **Gemini AI** + **Sarvam STT**.

Search for suppliers by product/industry, verify their legitimacy, find key contacts, and generate personalized outreach emails — all from a single search bar. Supports Hindi and English voice input.

## Features

- **Natural language search** — type "GPU manufacturers" or "aerospace parts suppliers" and get matched companies
- **Voice search (Hindi + English)** — speak your query using Sarvam AI's speech-to-text
- **Legitimacy scoring** — 5-factor scoring (company age, employees, funding, type, web presence) with 0-100 score
- **Contact discovery** — find key decision-makers at each company via Crustdata's people search
- **Personalized outreach emails** — auto-generated emails using full company + contact intelligence
- **AI compliance analysis** — fit scoring, compliance flags, export control notes (Gemini-powered)

## Tech Stack

- **Backend**: Python, FastAPI, httpx
- **Frontend**: HTML, Tailwind CSS, vanilla JS
- **APIs**: Crustdata (company/people search), Gemini (AI analysis), Sarvam AI (voice STT)

## Quick Start

### 1. Clone and setup

```bash
git clone https://github.com/Akasxh/supplylens.git
cd supplylens
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the project root:

```env
CRUSTDATA_API_KEY=your_crustdata_api_key
GEMINI_API_KEY=your_gemini_api_key
SARVAM_API_KEY=your_sarvam_api_key
```

**Getting API keys:**
- **Crustdata**: Sign up at [crustdata.com](https://crustdata.com) — provides company and people search data
- **Gemini**: Get a key at [ai.google.dev](https://ai.google.dev) — powers AI query parsing, compliance analysis, and personalized emails
- **Sarvam AI**: Sign up at [sarvam.ai](https://sarvam.ai) — enables Hindi/English voice search

> Gemini and Sarvam are optional. The app works without them using local fallbacks.

### 3. Run

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Frontend UI |
| `POST` | `/api/search` | Search suppliers by query |
| `GET` | `/api/contacts?domain=X` | Get contacts at a company |
| `GET` | `/api/enrich?domain=X` | Enrich company details |
| `POST` | `/api/analyze` | AI compliance analysis |
| `POST` | `/api/outreach` | Generate personalized email |
| `POST` | `/api/voice` | Voice-to-text (Sarvam STT) |

## Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI server + routes
│   ├── crustdata.py     # Crustdata API client
│   ├── gemini.py        # Gemini AI + local fallbacks
│   └── scoring.py       # Legitimacy scoring engine
├── static/
│   └── index.html       # Single-page frontend (Tailwind)
├── requirements.txt
├── .env                 # API keys (not committed)
└── README.md
```

## How It Works

1. **Search**: User types or speaks a query (e.g., "semiconductor manufacturers in Taiwan")
2. **Parse**: Gemini extracts structured search terms, or local keyword mapper handles it
3. **Discover**: Crustdata's `/company/search` API finds matching companies by industry
4. **Score**: Each company gets a legitimacy score based on age, size, funding, type, and web presence
5. **Contacts**: Crustdata's `/person/search` API finds key people at each company
6. **Outreach**: Emails are generated using full company intelligence (employee count, funding, HQ, industry) and contact context (title, seniority, department)

## License

MIT
