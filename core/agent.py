import os
from dotenv import load_dotenv
from core.scoring import calculate_trust_score

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API KEY FOUND: {bool(api_key)}")

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def run_trust_agent(agency: dict) -> dict:
    # Step 1: Calculate scores
    score_data = calculate_trust_score(agency)

    # Step 2: Sentiment analysis
    clean_reviews = [
        r["text"] for r in agency["reviews"]
    ]
    reviews_text = "\n".join(clean_reviews) if clean_reviews else "No verified reviews."

    sentiment_prompt = f"""
You are analyzing reviews for a recruitment agency called "{agency['name']}".

Reviews:
{reviews_text}

In 2 sentences max, describe the overall sentiment of these reviews.
Be direct and factual.
"""
    sentiment = llm.invoke(sentiment_prompt).content

    # Step 3: Generate reasoning
    reasoning_prompt = f"""
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
"""
    reasoning = llm.invoke(reasoning_prompt).content

    # Step 4: Parse response
    def extract(label, text):
        import re
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
