import os
import re
from groq import Groq
from dotenv import load_dotenv
from core.scoring import calculate_trust_score

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

def run_trust_agent(agency: dict) -> dict:
    score_data = calculate_trust_score(agency)

    clean_reviews = [r["text"] for r in agency["reviews"]]
    reviews_text = "\n".join(clean_reviews) if clean_reviews else "No verified reviews."

    sentiment = call_llm(f"""
You are analyzing reviews for a recruitment agency called "{agency['name']}".
Reviews:
{reviews_text}
In 2 sentences max, describe the overall sentiment. Be direct and factual.
""")

    reasoning = call_llm(f"""
You are an AI trust analyst for JSO, a job search platform.

Agency: {agency['name']}
Trust Score: {score_data['score']}/100
Placement Rate: {agency['placement_rate']}%
Verified: {agency['verified']}
Flagged Fake Reviews: {score_data['flagged_reviews']}
Response Time: {agency['response_time']} days
Confidence: {score_data['confidence']}

Score Breakdown:
- Review Score: {score_data['breakdown']['review_score']}/100
- Placement Score: {score_data['breakdown']['placement_score']}/100
- Response Score: {score_data['breakdown']['response_score']}/100
- Verification Score: {score_data['breakdown']['verification_score']}/100

Sentiment: {sentiment}

Provide:
1. A 2 sentence explanation of why this agency got this score
2. Up to 3 red flags if any. If none write "No red flags"
3. One word recommendation: TRUSTED, CAUTION, or AVOID

Format exactly like this:
EXPLANATION: [your explanation]
RED_FLAGS: [flag1 | flag2 | flag3]
RECOMMENDATION: [TRUSTED/CAUTION/AVOID]
""")

    def extract(label, text):
        match = re.search(rf"{label}:(.*?)(?=\n[A-Z_]+:|$)", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    explanation = extract("EXPLANATION", reasoning)
    red_flags_raw = extract("RED_FLAGS", reasoning)
    recommendation = extract("RECOMMENDATION", reasoning).strip()

    red_flags = [] if red_flags_raw == "No red flags" else [
        f.strip() for f in red_flags_raw.split("|") if f.strip()
    ]

    return {
        "agency_id": agency["id"],
        "agency_name": agency["name"],
        "score": score_data["score"],
        "confidence": score_data["confidence"],
        "explanation": explanation,
        "red_flags": red_flags,
        "recommendation": recommendation,
        "breakdown": score_data["breakdown"],
        "flagged_reviews": score_data["flagged_reviews"],
        "sentiment": sentiment
    }