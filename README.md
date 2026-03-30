# JSO Trust Agent

An AI-powered recruitment agency reputation analyzer built for the JSO job search platform. It helps job seekers evaluate whether a recruitment agency is trustworthy before engaging with it.

## What It Does

1. User selects a recruitment agency
2. A deterministic scoring engine analyzes reviews, placements, response time, and verification status
3. An LLM (Llama 3.3 70B via Groq) generates a sentiment summary and reasoning
4. The result is returned as a trust score, badge, red flags, and score breakdown

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Validation | Pydantic v2 |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Deployment | Vercel (serverless Python) |

## Trust Score Breakdown

The score is calculated from four weighted components, all with **time decay** (recent data counts more):

| Component | Weight | How It's Calculated |
|---|---|---|
| Review Score | 30% | Average rating of non-flagged reviews, recency-weighted |
| Placement Score | 40% | Ratio of successful placements, recency-weighted |
| Response Score | 20% | `max(0, 100 - response_time_days * 5)` |
| Verification Score | 10% | 100 if verified, 0 if not |

### Fake Review Detection

Reviews are automatically flagged if:
- The reviewer's account is less than 7 days old
- The review text is identical to another review from a different user

Flagged reviews are excluded from the score calculation.

### Recommendation Labels

| Score | Label |
|---|---|
| High | TRUSTED |
| Medium | CAUTION |
| Low | AVOID |

## Project Structure

```
├── app.py                  # FastAPI entry point (local dev)
├── api/
│   └── index.py            # Vercel serverless entry point
├── core/
│   ├── agent.py            # LLM orchestration (2 sequential Groq calls)
│   ├── scoring.py          # Deterministic trust scoring engine
│   ├── mock_data.py        # Agency dataset
│   └── __init__.py
├── static/
│   └── index.html          # Single-page frontend UI
├── vercel.json             # Vercel deployment config
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.9+
- A [Groq API key](https://console.groq.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/heheDixo/JSO-trust-agent.git
cd JSO-trust-agent

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Running Locally

```bash
uvicorn app:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Deployment

This project is configured for [Vercel](https://vercel.com) deployment.

1. Push to GitHub
2. Import the repo in Vercel
3. Add `GROQ_API_KEY` under **Settings → Environment Variables**
4. Deploy

## API

### `POST /analyze`

Analyze an agency's trustworthiness.

**Request body:**
```json
{
  "agency_id": "1"
}
```

**Response:**
```json
{
  "agency_id": "1",
  "agency_name": "TalentBridge",
  "score": 82,
  "confidence": "high",
  "recommendation": "TRUSTED",
  "explanation": "...",
  "red_flags": [],
  "sentiment": "...",
  "breakdown": {
    "review_score": 90,
    "placement_score": 85,
    "response_score": 75,
    "verification_score": 100
  },
  "flagged_reviews": 0
}
```

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key — get one at [console.groq.com](https://console.groq.com) |
