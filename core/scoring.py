from datetime import datetime

def get_recency_weight(date_string: str) -> float:
    date = datetime.strptime(date_string, "%Y-%m-%d")
    now = datetime.now()
    months_ago = (now - date).days / 30
    return 1 / (1 + months_ago)

def detect_fake_reviews(reviews: list) -> list:
    flagged = []
    
    for i, review in enumerate(reviews):
        # Flag new accounts
        if review["account_age"] < 7:
            flagged.append(review["id"])
            continue
        
        # Flag identical reviews
        for j, other in enumerate(reviews):
            if i != j and review["text"].strip() == other["text"].strip():
                if review["id"] not in flagged:
                    flagged.append(review["id"])
    
    return flagged

def calculate_trust_score(agency: dict) -> dict:
    flagged_ids = detect_fake_reviews(agency["reviews"])
    
    # Remove fake reviews
    clean_reviews = [
        r for r in agency["reviews"] 
        if r["id"] not in flagged_ids
    ]
    
    # Time weighted review score
    review_score = 0
    total_weight = 0
    for review in clean_reviews:
        weight = get_recency_weight(review["date"])
        review_score += review["rating"] * weight
        total_weight += weight
    
    avg_review_score = (review_score / total_weight / 5 * 100) if total_weight > 0 else 0

    # Time weighted placement score
    placement_score = 0
    placement_weight = 0
    for p in agency["placements"]:
        weight = get_recency_weight(p["date"])
        placement_score += (1 if p["success"] else 0) * weight
        placement_weight += weight
    
    avg_placement_score = (placement_score / placement_weight * 100) if placement_weight > 0 else 0

    # Response time score
    response_score = max(0, 100 - agency["response_time"] * 5)

    # Verification score
    verification_score = 100 if agency["verified"] else 0

    # Final weighted score
    final_score = round(
        avg_review_score * 0.30 +
        avg_placement_score * 0.40 +
        response_score * 0.20 +
        verification_score * 0.10
    )

    # Confidence level
    if len(clean_reviews) >= 3:
        confidence = "high"
    elif len(clean_reviews) >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "score": final_score,
        "confidence": confidence,
        "flagged_reviews": len(flagged_ids),
        "clean_review_count": len(clean_reviews),
        "breakdown": {
            "review_score": round(avg_review_score),
            "placement_score": round(avg_placement_score),
            "response_score": round(response_score),
            "verification_score": verification_score
        }
    }
